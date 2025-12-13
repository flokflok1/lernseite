# 🚀 LernsystemX - Komplette Setup-Anleitung

**Version:** 1.0.0
**Datum:** 2025-01-17
**Status:** Produktionsbereit mit 40 Migrationen

---

## 📋 Voraussetzungen

Stelle sicher, dass folgende Software installiert ist:

- ✅ **Python 3.12+** - [Download](https://www.python.org/downloads/)
- ✅ **PostgreSQL 14+** - Installiert in `C:\Program Files\PostgreSQL\17`
- ✅ **Redis Server** - Läuft auf `10.0.10.10:6379` (VM)
- ✅ **Node.js 18+** - Für Frontend (optional)

---

## 🔧 Schritt 1: PostgreSQL konfigurieren

### 1.1 PostgreSQL-Passwort setzen

Das Standard-Passwort für den `postgres`-Benutzer sollte bekannt sein.
Falls nicht, setze es neu:

```powershell
# Öffne pgAdmin oder SQL Shell
# Setze Passwort für postgres-Benutzer
ALTER USER postgres WITH PASSWORD 'postgres';
```

### 1.2 PostgreSQL-Dienst prüfen

```powershell
# Prüfe ob PostgreSQL läuft
Get-Service -Name "postgresql-x64-17"

# Falls nicht gestartet:
Start-Service -Name "postgresql-x64-17"
```

---

## 🔧 Schritt 2: Backend einrichten

### 2.1 Repository klonen / öffnen

```powershell
cd C:\Users\Pascal\Desktop\Lernsystem
```

### 2.2 Virtual Environment aktivieren

```powershell
cd backend
.\.venv\Scripts\activate
```

### 2.3 Abhängigkeiten installieren (falls noch nicht geschehen)

```powershell
pip install -r requirements.txt
```

### 2.4 Umgebungsvariablen konfigurieren

Die `.env` Datei ist bereits vorhanden. **Wichtig:** Prüfe die PostgreSQL-Credentials:

```env
# In backend/.env
DB_USER=postgres
DB_PASSWORD=postgres  # <-- Dein tatsächliches Passwort
```

**Weitere wichtige Einstellungen:**
```env
# Redis (läuft auf VM)
REDIS_URL=redis://10.0.10.10:6379/0

# Entwicklungsmodus
FLASK_ENV=development
DEBUG=True
```

---

## 🗄️ Schritt 3: Datenbank zurücksetzen (Neustart)

### Option A: Python-Skript (Empfohlen)

```powershell
# Stelle sicher, dass .venv aktiviert ist
python reset_database.py
```

**Das Skript:**
1. Löscht die alte `lernsystemx_dev` Datenbank
2. Erstellt eine neue leere Datenbank
3. Aktiviert PostgreSQL-Extensions (`uuid-ossp`, `pgcrypto`)

**Erwartete Ausgabe:**
```
============================================================
LernsystemX Database Reset
============================================================

Database Host: localhost:5432
Database User: postgres
Database Name: lernsystemx_dev

WARNING: This will delete ALL existing data!

Continue? (yes/no): yes

Connecting to PostgreSQL...
Terminating existing connections to 'lernsystemx_dev'...
Dropping database 'lernsystemx_dev'...
Creating fresh database 'lernsystemx_dev'...
Enabling PostgreSQL extensions...
  ✓ uuid-ossp extension enabled
  ✓ pgcrypto extension enabled

============================================================
✓ Database reset complete!
============================================================
```

### Option B: Batch-Skript

```powershell
.\reset_database.bat
```

### Option C: Manuell via psql

```powershell
# PostgreSQL bin-Verzeichnis zum PATH hinzufügen oder direkt aufrufen
$env:PGPASSWORD="postgres"

& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "DROP DATABASE IF EXISTS lernsystemx_dev;"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "CREATE DATABASE lernsystemx_dev OWNER postgres;"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d lernsystemx_dev -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d lernsystemx_dev -c "CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";"
```

---

## 🚀 Schritt 4: Backend starten

```powershell
# Virtual Environment muss aktiviert sein
python run.py
```

**Erwartete Ausgabe:**
```
[2025-11-17 22:46:29] INFO in __init__: System not installed - Setup Wizard mode active
[2025-11-17 22:46:29] INFO in __init__: Please navigate to http://localhost:5000/setup/status to begin installation
...
 * Running on http://127.0.0.1:5000
 * Running on http://10.0.20.111:5000
```

**Wichtig:** Die Fehlermeldungen bzgl. Datenbankverbindung sind normal beim ersten Start, da die Tabellen noch nicht existieren!

---

## 🧙 Schritt 5: Setup Wizard durchlaufen

### 5.1 Setup Wizard öffnen

Öffne deinen Browser und navigiere zu:

```
http://localhost:5000/setup/status
```

### 5.2 Setup-Schritte

Der Setup Wizard führt dich durch folgende Schritte:

#### **Schritt 1: System-Check**
- Prüft Python-Version
- Prüft PostgreSQL-Verbindung
- Prüft Redis-Verbindung
- Prüft erforderliche Pakete

**Erwartetes Ergebnis:**
```
✓ Python 3.12+
✓ PostgreSQL 17 erreichbar
✓ Redis erreichbar (10.0.10.10:6379)
✓ Alle Abhängigkeiten installiert
```

#### **Schritt 2: Datenbank initialisieren**

Klicke auf **"Initialize Database"**

**Das passiert:**
1. Verbindung zur Datenbank wird hergestellt
2. PostgreSQL-Extensions werden aktiviert (uuid-ossp, pgcrypto)
3. `migration_history` Tabelle wird erstellt
4. **Alle 40 SQL-Migrationen werden ausgeführt** (001-040)
5. 112 Tabellen werden erstellt
6. ~300 Indexes werden erstellt
7. ~120 Foreign Keys werden erstellt
8. Row Level Security (RLS) wird aktiviert
9. System-Seeds werden eingefügt (Rollen, AI-Provider, Sprachen, etc.)

**Dauer:** ~15-20 Sekunden

**Erwartete Ausgabe:**
```json
{
  "success": true,
  "migrations_executed": 40,
  "tables_created": 112,
  "database_created": true
}
```

#### **Schritt 3: Admin-Benutzer erstellen**

Fülle das Formular aus:

- **E-Mail:** `admin@lernsystemx.local`
- **Vorname:** `Admin`
- **Nachname:** `User`
- **Passwort:** `admin123` (mindestens 8 Zeichen)
- **Passwort bestätigen:** `admin123`

**Das passiert:**
- Admin-Benutzer wird mit Rolle `admin` erstellt
- Passwort wird mit bcrypt gehashed (cost factor 12)
- Token-Wallet wird erstellt
- Dashboard-Layout wird initialisiert

#### **Schritt 4: Organisation einrichten** (Optional)

Falls du eine Schule/Firma einrichten möchtest:

- **Name:** `Meine Schule`
- **Typ:** `school` oder `company`
- **Domain:** `meineschule.local` (optional)

**Das passiert:**
- Organisation wird erstellt
- Admin wird als Organization Admin hinzugefügt
- Organisation-Settings werden initialisiert

#### **Schritt 5: AI-Provider konfigurieren** (Optional)

Füge API-Keys für AI-Services hinzu:

- **Anthropic API Key:** `sk-ant-...` (Claude)
- **OpenAI API Key:** `sk-...` (GPT-4)
- **DeepL API Key:** `...` (Übersetzungen)

**Das passiert:**
- API-Keys werden verschlüsselt gespeichert
- AI-Provider werden als "aktiv" markiert
- Verbindungstests werden durchgeführt

#### **Schritt 6: Abschluss & Verifizierung**

Der Setup Wizard führt finale Checks durch:

```
✓ Alle Migrationen erfolgreich ausgeführt
✓ Admin-Benutzer erstellt
✓ System bereit
```

**Klicke auf:** "Complete Setup"

---

## ✅ Schritt 6: Verifizierung

### 6.1 Datenbank-Schema prüfen

```powershell
# PostgreSQL-Verifizierungsskript ausführen
$env:PGPASSWORD="postgres"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -d lernsystemx_dev -f backend\migrations\verify_schema.sql
```

**Erwartete Ausgabe:**
```
========================================
LernsystemX Schema Verification
========================================

1. TABLE COUNT
---
 metric         | value
----------------+-------
 Total Tables:  | 112
 Expected:      | 102

2. TABLES WITHOUT PRIMARY KEYS
---
(0 rows)

3. INDEX STATISTICS
---
 metric               | value
---------------------+-------
 Total Indexes:       | 300+
 Tables with Indexes: | 112

4. FOREIGN KEY STATISTICS
---
 metric               | value
---------------------+-------
 Total Foreign Keys:  | 120+

...

========================================
SCHEMA VERIFICATION COMPLETE
========================================
```

### 6.2 Migration History prüfen

```sql
-- In psql oder pgAdmin
SELECT COUNT(*) FROM migration_history WHERE status = 'success';
-- Erwartet: 40
```

### 6.3 Backend-Neustart

Stoppe den Server (CTRL+C) und starte ihn neu:

```powershell
python run.py
```

**Jetzt sollten KEINE Datenbankfehler mehr erscheinen!**

**Erwartete Ausgabe:**
```
[2025-11-17 23:00:00] INFO in __init__: LernsystemX Backend started successfully
[2025-11-17 23:00:00] INFO in __init__: Database connected: lernsystemx_dev
[2025-11-17 23:00:00] INFO in __init__: 112 tables loaded
...
 * Running on http://127.0.0.1:5000
```

### 6.4 Login testen

Öffne Browser:

```
http://localhost:5000/api/v1/auth/login
```

POST-Request (mit Postman oder cURL):
```json
{
  "email": "admin@lernsystemx.local",
  "password": "admin123"
}
```

**Erwartete Antwort:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "user_id": "...",
      "email": "admin@lernsystemx.local",
      "role": "admin"
    }
  }
}
```

---

## 🎯 Nächste Schritte

Nach erfolgreichem Setup:

### 1. Frontend einrichten (optional)

```powershell
cd ../frontend
npm install
npm run dev
```

**Frontend URL:** `http://localhost:5173`

### 2. Test-Daten erstellen

- Erstelle Test-Kurse über die API
- Füge Test-Benutzer hinzu
- Teste Learning Methods

### 3. LiveRoom testen

- Erstelle einen Raum
- Teste WebRTC Video/Audio
- Teste AI-Whiteboard

### 4. API-Dokumentation

Alle verfügbaren Endpunkte:

```
http://localhost:5000/api/v1/docs
```

---

## 🐛 Troubleshooting

### Problem: PostgreSQL-Verbindung schlägt fehl

**Fehlermeldung:**
```
connection to server at "127.0.0.1", port 5432 failed:
FATAL: password authentication failed for user "postgres"
```

**Lösung:**
1. Prüfe `.env` Datei:
   ```env
   DB_USER=postgres
   DB_PASSWORD=dein-tatsächliches-passwort
   ```

2. Setze PostgreSQL-Passwort neu:
   ```sql
   ALTER USER postgres WITH PASSWORD 'neues-passwort';
   ```

3. Starte PostgreSQL-Dienst:
   ```powershell
   Restart-Service -Name "postgresql-x64-17"
   ```

### Problem: Redis-Verbindung schlägt fehl

**Fehlermeldung:**
```
Error connecting to Redis at 10.0.10.10:6379
```

**Lösung:**
1. Prüfe ob Redis auf VM läuft:
   ```bash
   ssh vm-user@10.0.10.10
   sudo systemctl status redis
   ```

2. Teste Verbindung:
   ```powershell
   Test-NetConnection -ComputerName 10.0.10.10 -Port 6379
   ```

3. Firewall prüfen (auf VM):
   ```bash
   sudo ufw allow 6379/tcp
   ```

### Problem: Migrationen schlagen fehl

**Fehlermeldung:**
```
Migration failed: 017_ai_providers.sql
```

**Lösung:**
1. Prüfe Migration History:
   ```sql
   SELECT * FROM migration_history WHERE status = 'failed';
   ```

2. Fehler analysieren:
   ```sql
   SELECT error_message FROM migration_history WHERE status = 'failed';
   ```

3. Datenbank zurücksetzen und neu versuchen:
   ```powershell
   python reset_database.py
   python run.py
   # -> Setup Wizard neu durchlaufen
   ```

### Problem: Extension uuid-ossp fehlt

**Fehlermeldung:**
```
ERROR: extension "uuid-ossp" does not exist
```

**Lösung:**
```sql
-- Als PostgreSQL Superuser
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### Problem: Setup Wizard nicht erreichbar

**Fehlermeldung:**
```
404 Not Found - /setup/status
```

**Lösung:**
1. Prüfe ob Backend im Setup-Modus ist:
   ```
   [INFO] System not installed - Setup Wizard mode active
   ```

2. Falls nicht, lösche `.installed` Datei:
   ```powershell
   Remove-Item -Path "backend\.installed" -Force
   ```

3. Backend neu starten

---

## 📊 Datenbank-Statistiken

Nach erfolgreichem Setup:

| Metric | Wert |
|--------|------|
| **Migrationen** | 40 |
| **Tabellen** | 112 |
| **Indexes** | ~300+ |
| **Foreign Keys** | ~120+ |
| **Triggers** | ~30+ |
| **Functions** | 3 |
| **Views** | 2 |
| **RLS Policies** | 3 |
| **System Seeds** | 9 Rollen, 3 AI-Provider, 7 AI-Modelle, 20 Sprachen |

---

## 📚 Dokumentation

**Migration System:**
- `backend/migrations/README.md` - Vollständige Migrations-Liste
- `backend/migrations/INTEGRATION_GUIDE.md` - Detaillierte Integration
- `MIGRATION_REPORT.md` - Komplette Analyse
- `QUICK_START_MIGRATIONS.md` - Schnellstart

**Backend:**
- `backend/README.md` - Backend-Dokumentation
- `CLAUDE.md` - Projekt-Übersicht für AI

**Datenbank:**
- `LernsystemX-Doku/14_DB-Struktur.md` - Vollständiges Schema
- `backend/migrations/verify_schema.sql` - Verifizierungsskript

---

## 🔐 Sicherheit

**Wichtig für Produktion:**

1. **Ändere alle Secrets:**
   ```env
   SECRET_KEY=generiere-einen-starken-zufälligen-schlüssel
   JWT_SECRET_KEY=anderer-starker-zufälliger-schlüssel
   ```

2. **Verwende starke Passwörter:**
   - Mindestens 16 Zeichen
   - Buchstaben, Zahlen, Sonderzeichen

3. **HTTPS aktivieren:**
   - Nginx als Reverse Proxy
   - SSL-Zertifikate (Let's Encrypt)

4. **Debug-Modus deaktivieren:**
   ```env
   FLASK_ENV=production
   DEBUG=False
   ```

5. **Rate Limiting aktivieren:**
   - Bereits konfiguriert in `backend/middleware/rate_limit.py`

---

## 🎉 Fertig!

Das LernsystemX-System ist jetzt vollständig eingerichtet und betriebsbereit!

**Teste die wichtigsten Features:**
- ✅ Login als Admin
- ✅ Kurs erstellen
- ✅ Learning Method hinzufügen
- ✅ LiveRoom erstellen
- ✅ AI-Features testen

**Bei Fragen:**
- Dokumentation lesen
- GitHub Issues erstellen
- Support kontaktieren

---

**Version:** 1.0.0
**Erstellt:** 2025-01-17
**LernsystemX Development Team**
