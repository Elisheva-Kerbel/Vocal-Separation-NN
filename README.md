# VocalSplit - הפרדת שירים לווקאלים ורקע

פלטפורמה להפרדת שירים לשני ערוצים: **ווקאלים** (קול) ו**רקע** (מוזיקה).
המשתמש מעלה שיר, המערכת מפרידה אותו באמצעות רשת נוירונים, והתוצאה זמינה להאזנה ולהורדה.

## מה יש כאן

- העלאת קבצי אודיו (MP3 / WAV / M4A)
- הפרדה אוטומטית לווקאלים + רקע
- שתי רמות הפרדה: **Basic** (מודל מקומי) ו-**Professional** (Demucs של Meta)
- ספריה אישית לניהול השירים
- ספריה ציבורית עם דירוגים ודיווחים
- מנוי Free / Pro עם מכסות יומיות
- פאנל ניהול (admin)
- אימות: הרשמה + התחברות עם אימייל/סיסמה, או Google OAuth
- i18n: עברית ואנגלית

---

## ארכיטקטורה כללית

```
┌─────────────┐     HTTP      ┌─────────────┐     S3 API    ┌─────────┐
│  Frontend   │ ────────────> │   Backend   │ ────────────> │  MinIO  │
│  React+Vite │ <──────────── │   FastAPI   │ <──────────── │ Storage │
│  :5173      │               │   :8000     │               │  :9000  │
└─────────────┘               └──────┬──────┘               └─────────┘
                                     │
                              Redis (Broker)
                                     │
                              ┌──────┴──────┐
                              │   Worker    │
                              │   Celery    │     ┌────────────┐
                              │  separation │────>│ AI Models  │
                              │   queue     │     │ (PyTorch)  │
                              └─────────────┘     └────────────┘
                                     │
                              ┌──────┴──────┐
                              │ PostgreSQL  │
                              │   :5432     │
                              └─────────────┘
```

**7 קונטיינרים ב-Docker Compose:**

| שירות | תפקיד | פורט |
|---|---|---|
| `frontend` | React + Vite - ממשק משתמש | 5173 |
| `backend` | FastAPI - API ראשי | 8000 |
| `worker` | Celery - עיבוד הפרדות ברקע | - |
| `postgres` | PostgreSQL - מסד נתונים | 5432 |
| `redis` | Redis - broker ל-Celery | 6379 |
| `minio` | MinIO - אחסון קבצים (S3-compatible) | 9000 |
| `adminer` | ממשק ניהול DB | 8080 |

---

## Flow מלא: מה קורה כשמשתמש מעלה שיר

### שלב 1: המשתמש לוחץ "העלה והפרד" בממשק

**Frontend: `UploadPage.jsx`**

```
לחיצה על כפתור "העלה והפרד"
  └─> onUpload()
        └─> uploadSong(file, onProgress, { modelChoice, visibility })   [api/songs.js]
              └─> XMLHttpRequest POST /upload (עם FormData)
```

הפונקציה `uploadSong` שולחת את הקובץ כ-`FormData` עם `XMLHttpRequest` (לא `fetch`) כדי לתמוך ב-progress bar.

### שלב 2: הבקאנד מקבל את הקובץ

**Backend: `upload.py` → `upload_song()`**

```
POST /upload
  │
  ├─ 1. וולידציה:
  │     - סוג קובץ (MP3/WAV/M4A בלבד)
  │     - גודל קובץ (מקסימום לפי הגדרות)
  │     - model_choice ו-visibility תקינים
  │
  ├─ 2. בדיקת מכסה:
  │     └─> quotas.py → check_quota(db, user, model_tier)
  │           - בודק כמה הפרדות המשתמש עשה היום
  │           - אם עבר את המכסה → HTTP 429
  │
  ├─ 3. העלאה ל-MinIO:
  │     └─> storage.py → upload_bytes(data, storage_key, content_type)
  │           - storage_key = "{user_id}/{song_id}/original.mp3"
  │           - הקובץ נשמר ב-MinIO (S3-compatible storage)
  │
  ├─ 4. שמירה ב-DB:
  │     - Song (status="uploaded" → "processing")
  │     - AudioFile (purpose="original", storage_key=...)
  │     - SeparationJob (status="queued", model_tier=...)
  │
  └─ 5. שליחה לתור:
        └─> tasks.py → run_separation.delay(job_id, song_id, user_id, storage_key, model_tier)
              - Celery שולח את המשימה לתור "separation" ב-Redis
              - הבקאנד מחזיר תשובה מיד (HTTP 201) - לא מחכה לעיבוד
```

### שלב 3: ה-Worker מעבד את ההפרדה

**Worker: `tasks.py` → `run_separation()`**

ה-Worker הוא קונטיינר נפרד שמריץ Celery ומאזין לתור `separation` ב-Redis.

```
run_separation() [רץ ב-Worker, לא ב-Backend]
  │
  ├─ 1. מעדכן סטטוס: job.status = "running"
  │
  ├─ 2. מוריד את הקובץ מ-MinIO לתיקייה זמנית:
  │     └─> storage.download_to_file(storage_key, input_path)
  │
  ├─ 3. מריץ הפרדה - לפי רמת המודל:
  │     │
  │     ├─ model_tier == "professional":
  │     │     └─> demucs_inference.py → run_demucs_separation()
  │     │           - טוען את htdemucs_ft של Meta (מ-HuggingFace)
  │     │           - מריץ את המודל → 4 stems (vocals, drums, bass, other)
  │     │           - מערבב drums+bass+other → background
  │     │           - שומר vocals.wav + background.wav
  │     │
  │     └─ model_tier == "basic":
  │           └─> local_inference.py → run_local_separation()
  │                 - local_checkpoint.py → מוצא את checkpoint file
  │                 - local_model.py → בונה את הרשת (UNet)
  │                 - טוען weights מהקובץ
  │                 - audio_io.py → STFT על הקובץ
  │                 - מריץ mask prediction
  │                 - vocals = mask × spectrogram
  │                 - background = (1-mask) × spectrogram
  │                 - ISTFT בחזרה ל-waveform
  │                 - שומר vocals.wav + background.wav
  │
  ├─ 4. מעלה תוצאות ל-MinIO:
  │     - storage.upload_from_file("vocals.wav", "{user}/{song}/vocals.wav")
  │     - storage.upload_from_file("background.wav", "{user}/{song}/background.wav")
  │     - יוצר AudioFile record לכל stem ב-DB
  │
  ├─ 5. מעדכן סטטוס:
  │     - job.status = "succeeded"
  │     - song.status = "ready"
  │
  └─ 6. עדכון צריכה:
        └─> _finalize_usage() → יוצר UsageEvent + מעדכן DailyUsage
```

### שלב 4: הממשק מציג את התוצאה

**Frontend: `SongPage.jsx`**

```
SongPage נטען (hash = #/song/{songId})
  │
  ├─ 1. loadSong():
  │     └─> getSong(songId) → GET /songs/{songId}
  │           - מחזיר: title, status, visibility, stems[], job{}
  │
  ├─ 2. אם status == "processing":
  │     - מציג ספינר + טיימר
  │     - כל 3 שניות: polling עם getSong() שוב
  │     - כשהסטטוס משתנה ל-"ready" → עובר לשלב 3
  │
  ├─ 3. אם status == "ready":
  │     - מבקש signed URL לכל stem:
  │     │   └─> getListenUrl(songId, "original") → GET /songs/{songId}/listen-url/original
  │     │   └─> getListenUrl(songId, "vocals")   → GET /songs/{songId}/listen-url/vocals
  │     │   └─> getListenUrl(songId, "background")→ GET /songs/{songId}/listen-url/background
  │     │
  │     │   הבקאנד (songs.py → get_listen_url):
  │     │     └─> storage.generate_signed_url(storage_key, ttl)
  │     │           - MinIO מייצר URL זמני (חתום) שתקף למספר דקות
  │     │           - ה-URL הזה מאפשר גישה ישירה לקובץ מהדפדפן
  │     │
  │     - מציג 3 כפתורי ערוץ: מקור / ווקאלים / רקע
  │     - לחיצה על ערוץ → <audio> element טוען את ה-signed URL
  │     - מעבר בין ערוצים שומר על אותו timestamp
  │
  └─ 4. הורדה:
        └─> onDownload(purpose):
              └─> getDownloadUrl(songId, purpose) → GET /songs/{songId}/download-url/{purpose}
                    - מחזיר signed URL עם Content-Disposition: attachment
                    - הדפדפן מוריד את הקובץ
```

---

## מבנה ה-Backend (קבצים עיקריים)

```
backend/
├── app/
│   ├── main.py              # FastAPI app - רישום כל ה-routers
│   ├── config.py            # הגדרות מ-.env (DB, Redis, MinIO, SMTP...)
│   ├── constants.py         # כל הערכים הקבועים (Enums) - מקור אמת יחיד
│   ├── helpers.py           # פונקציות עזר משותפות (api_error, get_audio_file_or_404...)
│   ├── storage.py           # מתאם MinIO/S3 - upload, download, signed URLs
│   ├── celery_app.py        # הגדרת Celery (broker=Redis)
│   ├── tasks.py             # Celery tasks - run_separation, send_new_song_emails
│   │
│   ├── upload.py            # POST /upload - העלאת קובץ + שליחה לתור
│   ├── songs.py             # GET /songs/{id} - פרטי שיר, listen/download URLs
│   ├── library.py           # GET /library - ספריה אישית
│   ├── public.py            # GET /public/songs - ספריה ציבורית, דירוגים, דיווחים
│   ├── quotas.py            # בדיקת מכסות יומיות
│   ├── admin.py             # פאנל ניהול - משתמשים, שירים, סטטיסטיקות
│   ├── settings_routes.py   # הגדרות משתמש, מחיקת חשבון, שינוי סיסמה
│   ├── subscriptions.py     # מנויים Free/Pro
│   ├── coupons.py           # קופונים
│   │
│   ├── auth/                # אימות
│   │   ├── routes.py        # /auth/signup, /auth/login, /auth/google, /auth/logout
│   │   ├── session.py       # ניהול session (httpOnly cookie)
│   │   ├── password.py      # hash + verify סיסמאות (bcrypt)
│   │   └── schemas.py       # Pydantic models לבקשות/תגובות auth
│   │
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models: User, Song, AudioFile, SeparationJob...
│   │   └── session.py       # DB session factory
│   │
│   └── email_service.py     # שליחת מיילים (SMTP)
│
└── ai/                      # מודולי AI - הפרדת אודיו
    ├── model.py             # Stem enum (vocals/background), ModelTier enum
    ├── local_model.py       # ארכיטקטורת הרשת (UNet) - Basic tier
    ├── local_inference.py   # הרצת המודל המקומי: load → STFT → predict → ISTFT
    ├── local_checkpoint.py  # מציאת קובץ ה-checkpoint
    ├── demucs_inference.py  # הרצת Demucs (htdemucs_ft) - Professional tier
    └── audio_io.py          # עזרי אודיו: load, STFT, ISTFT, save WAV
```

## מבנה ה-Frontend (קבצים עיקריים)

```
frontend/src/
├── App.jsx              # ניתוב (hash-based), sidebar, auth modal
├── i18n.js              # מערכת תרגום עברית/אנגלית - כל הטקסטים כאן
├── helpers.jsx          # אייקונים, פונקציות עזר
│
├── api/
│   ├── auth.js          # פונקציות auth: signUp, signIn, googleLogin, signOut
│   └── songs.js         # כל קריאות ה-API: upload, getSong, getListenUrl, library...
│
├── components/
│   ├── AuthModal.jsx    # מודל הרשמה/התחברות (+ Google OAuth)
│   ├── NeedAuth.jsx     # הודעת "צריך להתחבר"
│   ├── LibrarySongCard.jsx   # כרטיס שיר בספריה האישית
│   └── PublicSongCard.jsx    # כרטיס שיר בספריה הציבורית (+ נגן + דירוג)
│
└── pages/
    ├── HomePage.jsx     # דף נחיתה + תמחור
    ├── UploadPage.jsx   # העלאת שיר (בחירת מודל, נראות, progress bar)
    ├── SongPage.jsx     # דף שיר - ספינר בזמן עיבוד, 3 נגנים כשמוכן
    ├── LibraryPage.jsx  # ספריה אישית
    ├── ExplorePage.jsx  # ספריה ציבורית
    ├── SettingsPage.jsx # הגדרות + שינוי סיסמה + מחיקת חשבון
    ├── UpgradePage.jsx  # שדרוג ל-Pro
    └── AdminPage.jsx    # פאנל ניהול (super_admin בלבד)
```

---

## מודלי ה-AI

### Basic tier (מודל מקומי)

- רשת **UNet** שאומנה על הפרדת מוזיקה
- קובץ ה-checkpoint נמצא מחוץ לריפו (LOCAL_MODEL_ROOT)
- עובד על **ספקטרוגרמה**: STFT → mask prediction → ISTFT
- מהיר אבל פחות מדויק

**Flow טכני:**
```
audio_io.load_mono(input) → waveform
audio_io.stft(waveform) → spectrogram (complex)
np.abs(spectrogram) → magnitude
model(magnitude) → mask (0..1)
vocals = mask × spectrogram
background = (1-mask) × spectrogram
audio_io.istft(vocals) → vocals.wav
audio_io.istft(background) → background.wav
```

### Professional tier (Demucs)

- **htdemucs_ft** של Meta - state-of-the-art בהפרדת מוזיקה
- נטען אוטומטית מ-HuggingFace Hub (פעם ראשונה)
- מפריד ל-4 stems (vocals, drums, bass, other)
- אנחנו מערבבים drums+bass+other → background
- איטי יותר אבל הרבה יותר מדויק

---

## איך ה-Auth עובד

```
Frontend                          Backend (/auth/...)
────────                          ───────────────────
signUp(email, pw) ─────────────> POST /auth/signup
                                   ├─ hash password (bcrypt)
                                   ├─ create User in DB
                                   ├─ create session (UUID)
                                   └─ Set-Cookie: session={uuid}; HttpOnly; SameSite=Lax

signIn(email, pw) ─────────────> POST /auth/login
                                   ├─ find user by email
                                   ├─ verify password
                                   └─ Set-Cookie: session={uuid}

googleLogin(credential) ───────> POST /auth/google
                                   ├─ verify Google ID token
                                   ├─ find or create user
                                   └─ Set-Cookie: session={uuid}

currentUser() ─────────────────> GET /auth/me
                                   ├─ read cookie → find session
                                   └─ return user data (or 401)

כל בקשה אחרי login:
  הדפדפן שולח את ה-cookie אוטומטית
  → Backend: current_user() dependency → מחלץ user מה-session
```

ה-session הוא **httpOnly cookie** - ה-JavaScript לא יכול לגשת אליו, רק הדפדפן שולח אותו אוטומטית.

---

## Signed URLs - גישה לקבצים

הקבצים ב-MinIO הם **פרטיים** תמיד. אין public URLs.

כדי להאזין או להוריד, הבקאנד מייצר **Signed URL** - כתובת זמנית עם חתימה קריפטוגרפית:

```
GET /songs/{id}/listen-url/vocals
  → Backend:
      1. בודק שהמשתמש מורשה
      2. מוצא את ה-storage_key של הקובץ ב-DB
      3. storage.generate_signed_url(key, ttl=600) → MinIO מייצר URL חתום
      4. שומר SignedUrlGrant ב-DB (audit)
      5. מחזיר: { url: "http://minio:9000/bucket/...?X-Amz-Signature=...", expires_in: 600 }
  → Frontend:
      <audio src={url} /> → הדפדפן ניגש ישירות ל-MinIO עם ה-URL החתום
```

---

## הרצה מקומית

```bash
# 1. העתק את קובץ ההגדרות
cp .env.example .env
# ערוך את .env עם הערכים שלך

# 2. בנה והרם
docker compose build
docker compose up -d

# 3. בדוק
curl http://localhost:8000/health   # Backend
open http://localhost:5173          # Frontend
open http://localhost:8080          # Adminer (DB)
open http://localhost:9001          # MinIO Console
```

### משתני סביבה חשובים (.env)

| משתנה | תיאור |
|---|---|
| `DATABASE_URL` | חיבור ל-PostgreSQL |
| `CELERY_BROKER_URL` | חיבור ל-Redis |
| `S3_ENDPOINT_URL` | כתובת MinIO |
| `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | הרשאות MinIO |
| `LOCAL_MODEL_HOST_ROOT` | נתיב למודל ה-Basic על המחשב |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `SMTP_HOST` / `SMTP_USER` / `SMTP_PASSWORD` | שליחת מיילים |

---

## ה-DB Models העיקריים

| טבלה | תיאור |
|---|---|
| `User` | משתמש - email, password_hash, role, tier, status |
| `Song` | שיר - title, status (uploaded/processing/ready/failed), visibility, user_id |
| `AudioFile` | קובץ אודיו - song_id, purpose (original/vocals/background), storage_key |
| `SeparationJob` | משימת הפרדה - song_id, status, model_tier, error_message |
| `DailyUsage` | שימוש יומי - basic_count, professional_count |
| `SignedUrlGrant` | audit - מי ביקש URL ומתי |
| `SongRating` | דירוג שיר ציבורי |
| `SongReport` | דיווח על שיר ציבורי |

---

## סיכום ה-Flow בתמונה אחת

```
[משתמש]                [Frontend]              [Backend]              [Worker]            [MinIO]
   │                       │                       │                     │                   │
   │── לוחץ "העלה" ──────>│                       │                     │                   │
   │                       │── POST /upload ──────>│                     │                   │
   │                       │                       │── upload_bytes ────────────────────────>│
   │                       │                       │── INSERT Song, Job │                   │
   │                       │                       │── run_separation.delay ──> Redis        │
   │                       │<── 201 {song_id} ─────│                     │                   │
   │                       │                       │                     │                   │
   │── רואה ספינר ────────│── GET /songs/{id} ───>│                     │                   │
   │   (polling כל 3s)     │<── {status:processing}│                     │                   │
   │                       │                       │                     │                   │
   │                       │                       │   Worker picks job from Redis           │
   │                       │                       │                     │── download ──────>│
   │                       │                       │                     │<── audio file ────│
   │                       │                       │                     │                   │
   │                       │                       │                     │── AI model ──┐    │
   │                       │                       │                     │   (UNet or   │    │
   │                       │                       │                     │    Demucs)   │    │
   │                       │                       │                     │<─────────────┘    │
   │                       │                       │                     │                   │
   │                       │                       │                     │── upload vocals ─>│
   │                       │                       │                     │── upload bg ─────>│
   │                       │                       │                     │── UPDATE Song     │
   │                       │                       │                     │   status="ready"  │
   │                       │                       │                     │                   │
   │── רואה נגנים ────────│── GET /songs/{id} ───>│                     │                   │
   │                       │<── {status:ready} ────│                     │                   │
   │                       │── GET listen-url ────>│                     │                   │
   │                       │<── signed URL ────────│                     │                   │
   │── מנגן ──────────────│── <audio src=URL> ──────────────────────────────────────────────>│
   │                       │<── audio stream ───────────────────────────────────────────────<│
```
