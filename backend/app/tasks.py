"""Celery tasks — async separation (Phase 5)."""

from __future__ import annotations

import datetime
import os
import shutil
import tempfile
import uuid

from app.celery_app import celery
from app.config import load_settings


@celery.task(bind=True, max_retries=2, default_retry_delay=30)
def run_separation(self, job_id: str, song_id: str, user_id: str, storage_key: str, model_tier: str) -> dict:
    from sqlalchemy import select

    from ai import local_checkpoint, local_inference
    from app import storage
    from app.db.models import AudioFile, SeparationJob, Song
    from app.db.session import get_sessionmaker

    db = get_sessionmaker()()
    try:
        job = db.get(SeparationJob, uuid.UUID(job_id))
        if job is None:
            return {"status": "error", "message": "Job not found"}

        job.status = "running"
        job.started_at = datetime.datetime.now(datetime.timezone.utc)
        db.commit()

        work_dir = tempfile.mkdtemp(prefix="stemspace_")
        try:
            input_path = os.path.join(work_dir, "input")
            storage.download_to_file(storage_key, input_path)

            if model_tier == "professional":
                from ai.demucs_inference import run_demucs_separation
                outputs = run_demucs_separation(input_path, work_dir)
            else:
                outputs = local_inference.run_local_separation(
                    input_path, work_dir,
                    use_best_model=local_checkpoint.use_best_model_from_env(False),
                )

            song = db.get(Song, uuid.UUID(song_id))
            for stem, local_path in outputs.items():
                ext = os.path.splitext(local_path)[1] or ".wav"
                out_key = storage.generate_storage_key(
                    uuid.UUID(user_id), uuid.UUID(song_id), stem.value, ext,
                )
                file_size = os.path.getsize(local_path)
                storage.upload_from_file(local_path, out_key, "audio/wav")

                existing = db.scalars(
                    select(AudioFile).where(
                        AudioFile.song_id == uuid.UUID(song_id),
                        AudioFile.purpose == stem.value,
                    )
                ).first()
                if existing:
                    existing.storage_key = out_key
                    existing.byte_size = file_size
                else:
                    audio_file = AudioFile(
                        song_id=uuid.UUID(song_id),
                        purpose=stem.value,
                        storage_key=out_key,
                        content_type="audio/wav",
                        byte_size=file_size,
                    )
                    db.add(audio_file)

            job.status = "succeeded"
            job.finished_at = datetime.datetime.now(datetime.timezone.utc)
            if song:
                song.status = "ready"
            db.commit()

            _finalize_usage(db, uuid.UUID(user_id), uuid.UUID(song_id), uuid.UUID(job_id), model_tier)

            return {"status": "succeeded", "job_id": job_id}

        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)[:1000]
            job.finished_at = datetime.datetime.now(datetime.timezone.utc)

            song = db.get(Song, uuid.UUID(song_id))
            if song:
                song.status = "failed"
            db.commit()

            if self.request.retries < self.max_retries:
                raise self.retry(exc=exc)
            return {"status": "failed", "message": "Separation failed"}
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)
    finally:
        db.close()


@celery.task(bind=True, max_retries=2, default_retry_delay=60)
def send_new_song_emails(self, song_title: str, owner_name: str) -> dict:
    from sqlalchemy import select

    from app.db.models import User
    from app.db.session import get_sessionmaker
    from app.email_service import send_email

    db = get_sessionmaker()()
    try:
        users = db.scalars(
            select(User).where(
                User.email_opt_in.is_(True),
                User.status == "active",
            )
        ).all()

        sent = 0
        for user in users:
            subject = f"🎵 שיר חדש בספריה: {song_title}"
            html = f"""
            <div dir="rtl" style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto;">
                <h2 style="color: #7c3aed;">🎵 שיר חדש בספריה!</h2>
                <p>שלום {user.email.split('@')[0]},</p>
                <p>השיר <strong>{song_title}</strong> מאת <strong>{owner_name}</strong>
                   עלה לספריה הציבורית של VocalSplit.</p>
                <p>היכנס/י לאפליקציה כדי להאזין, להוריד ולדרג!</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb;">
                <p style="font-size: 12px; color: #6b7280;">
                    קיבלת מייל זה כי הפעלת קבלת עדכונים. ניתן לבטל בהגדרות.</p>
            </div>
            """
            if send_email(user.email, subject, html):
                sent += 1
        return {"status": "done", "sent": sent, "total_users": len(users)}
    except Exception as exc:
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        return {"status": "failed", "message": str(exc)[:500]}
    finally:
        db.close()


def _finalize_usage(db, user_id: uuid.UUID, song_id: uuid.UUID, job_id: uuid.UUID, model_tier: str = "basic") -> None:
    from sqlalchemy import select

    from app.db.models import DailyUsage, UsageEvent

    existing = db.scalars(
        select(UsageEvent).where(
            UsageEvent.song_id == song_id,
            UsageEvent.event_type == "separation_succeeded",
        )
    ).first()
    if existing:
        return

    event = UsageEvent(
        user_id=user_id,
        song_id=song_id,
        separation_job_id=job_id,
        event_type="separation_succeeded",
    )
    db.add(event)

    today = datetime.date.today()
    daily = db.scalars(
        select(DailyUsage).where(
            DailyUsage.user_id == user_id,
            DailyUsage.usage_date == today,
        )
    ).first()
    if daily:
        daily.successful_count += 1
        if model_tier == "professional":
            daily.professional_count += 1
        else:
            daily.basic_count += 1
    else:
        db.add(DailyUsage(
            user_id=user_id,
            usage_date=today,
            successful_count=1,
            basic_count=0 if model_tier == "professional" else 1,
            professional_count=1 if model_tier == "professional" else 0,
        ))
    db.commit()
