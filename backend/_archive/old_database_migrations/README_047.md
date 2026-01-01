# Migration 047 - Course-Specific Prompts (Phase C1.4)

## Beschreibung

Diese Migration fügt Unterstützung für kurs-spezifische AI-Prompts hinzu.
Administratoren können damit AI-Generierungs-Prompts pro Kurs anpassen.

## Ausführung

### Manuelle Ausführung (PostgreSQL)

```bash
# 1. In Datenbank einloggen
psql -h localhost -U lernsystemx_user -d lernsystemx_db

# 2. Migration ausführen
\i backend/migrations/047_course_prompts.sql

# 3. Erfolg prüfen
\d course_prompts
SELECT COUNT(*) FROM course_prompts;
```

### Python-basierte Ausführung

```python
from app.database.connection import get_connection

def run_migration():
    with open('backend/migrations/047_course_prompts.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("✓ Migration 047 erfolgreich ausgeführt")

if __name__ == '__main__':
    run_migration()
```

## Rollback

Falls die Migration rückgängig gemacht werden muss:

```sql
DROP TRIGGER IF EXISTS trigger_course_prompts_updated_at ON course_prompts;
DROP FUNCTION IF EXISTS update_course_prompts_updated_at();
DROP TABLE IF EXISTS course_prompts CASCADE;
```

## Abhängigkeiten

- ✅ Migration 008 (courses table)
- ✅ Migration 001 (users table)
- ✅ Migration 019 (global AI prompts)

## Neue Tabellen

- `course_prompts` - Kurs-spezifische Prompt-Overrides

## Neue Indexes

- `idx_course_prompts_course_scope` - Performance-Index
- `idx_course_prompts_scope` - Analytics-Index
- `idx_course_prompts_audit` - Audit-Trail-Index

## Testing nach Migration

```sql
-- Test 1: Tabelle existiert
SELECT table_name FROM information_schema.tables
WHERE table_name = 'course_prompts';

-- Test 2: Indexes existieren
SELECT indexname FROM pg_indexes
WHERE tablename = 'course_prompts';

-- Test 3: Trigger existiert
SELECT trigger_name FROM information_schema.triggers
WHERE event_object_table = 'course_prompts';

-- Test 4: Testdaten einfügen (optional)
INSERT INTO course_prompts (
    course_id,
    scope,
    language,
    prompt_system,
    prompt_user_template,
    created_by
) VALUES (
    (SELECT course_id FROM courses LIMIT 1),
    'exam_generation',
    'de',
    'Du bist ein Experte...',
    'Erstelle eine Prüfung...',
    (SELECT user_id FROM users WHERE role = 'admin' LIMIT 1)
);

-- Test 5: Unique Constraint testen
-- Dies sollte FEHLSCHLAGEN (Unique Constraint Violation)
INSERT INTO course_prompts (
    course_id,
    scope,
    language,
    prompt_system,
    created_by
) VALUES (
    (SELECT course_id FROM courses LIMIT 1),
    'exam_generation',
    'de',
    'Duplicate test',
    (SELECT user_id FROM users WHERE role = 'admin' LIMIT 1)
);
```

## API-Endpoints nach Migration

Nach erfolgreicher Migration stehen folgende Endpoints zur Verfügung:

- `GET /api/v1/admin/courses/{course_id}/prompts`
- `GET /api/v1/admin/courses/{course_id}/prompts/{scope}`
- `PUT /api/v1/admin/courses/{course_id}/prompts/{scope}`
- `DELETE /api/v1/admin/courses/{course_id}/prompts/{scope}`
- `POST /api/v1/admin/courses/{course_id}/prompts/reset`
- `POST /api/v1/admin/courses/{course_id}/prompts/resolve`

## Hinweise

- Diese Migration ist **non-breaking** (keine bestehenden Daten werden geändert)
- Die Migration ist **backward-compatible** (System funktioniert weiterhin ohne course_prompts)
- Die Migration erfordert **PostgreSQL 12+** (wegen `gen_random_uuid()`)

## Support

Bei Problemen:
1. Logs prüfen: `tail -f backend/logs/app.log`
2. Datenbank-Verbindung prüfen: `psql -h localhost -U lernsystemx_user -d lernsystemx_db`
3. Migration-Status: `SELECT * FROM course_prompts LIMIT 1;`

Phase: C1.4 - Course-Specific Prompt System
Datum: 2025-01-23
