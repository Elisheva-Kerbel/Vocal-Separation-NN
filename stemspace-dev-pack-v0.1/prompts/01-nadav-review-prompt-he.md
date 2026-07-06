# Nadav Review Prompt — Hebrew

Artifact Type: Review Prompt
Artifact ID: STEMSPACE-NADAV-PROMPT-001
Version: v0.1
Status: DRAFT — FOR NADAV REVIEW — NOT APPROVED FOR AI CODE AGENT
Project: Vocal Removing Platform / StemSpace
Source Baseline: User-provided technical handoff + generated development pack
Prepared by: Eitan
Required approval: Nadav
Execution allowed: No

## Prompt to send to Nadav

נדב שלום,

מצורפת חבילת הפיתוח `STEMSPACE-DEV-PACK-001 v0.1` עבור פרויקט Vocal Removing Platform / StemSpace.

המטרה של הבדיקה שלך היא לאשר האם החבילה מוכנה להפוך לשלב ראשון מבוקר לעבודה עם Claude Code / Cursor / כלי AI, או האם נדרש תיקון לפני שמתחילים.

נא לבדוק במיוחד:

1. האם ה־phases מחולקים נכון לפי תלויות ותוצאות ניתנות לבדיקה.
2. האם Phase 0 מוגדר מספיק טוב כ־Docker Compose-first, כולל:
   - `docker-compose.yml`
   - `backend/Dockerfile`
   - `frontend/Dockerfile`
   - PostgreSQL
   - Redis
   - MinIO
   - backend
   - worker
   - frontend
   - `.env.example`
   - `docs/` עם קבצי MD ברורים לפי משימות
   - קבצי Git בסיסיים: `.gitignore`, `.gitattributes`, `.editorconfig`
3. האם עקרון `Minimal Code / No Over-Engineering` ברור ומספיק אכיף.
4. האם Phase 1 מבודד נכון כ־AI Benchmark Harness לפני חיבור ל־Upload API / Queue / DB.
5. האם Phase 2 מגדיר נכון DB/domain skeleton בלי חשיפת `storage_key` ובלי שמירת audio bytes ב־DB.
6. האם ה־Do Not Build מונע פתיחה מוקדמת של Public Library, Admin, Billing, extra stems, resumable upload או public storage.
7. האם ה־acceptance criteria, tests, evidence ו־Stop Gates מספיקים כדי להעביר בהמשך משימות בודדות לסוכן קוד.
8. האם חסרה החלטה Product / Architecture / Security / UX לפני שמותר לפתוח את Phase 0 בפועל.

נא להחזיר אחת מהתשובות הבאות בלבד:

- `PASS` — החבילה מאושרת עבור scope ו־version אלה בלבד, ומותר להכין העברה מבוקרת ל־AI code agent לשלב Phase 0 בלבד.
- `PASS WITH FIXES` — יש תיקונים נדרשים; אין אישור להעברה עד תיקון ובדיקה חוזרת.
- `BLOCKED` — יש חסם מהותי שמונע התחלת עבודה.

אם יש תיקונים, נא לציין לכל תיקון:
- מזהה קובץ / Phase / Task;
- חומרה: Blocker / Major / Minor;
- מה חסר או שגוי;
- מה נדרש לתקן;
- האם התיקון חוסם את Phase 0 או רק downstream.

חשוב: גם אם אתה נותן PASS, נא לציין במפורש שזה חל רק על:
`STEMSPACE-DEV-PACK-001 v0.1`
ורק על scope שאישרת.
