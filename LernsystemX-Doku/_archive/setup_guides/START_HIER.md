# 🎯 START HIER - LernsystemX Setup

**Letzte Aktualisierung:** 2025-01-17

---

## ⚡ Schnellstart (3 Schritte)

### Schritt 1: Setup Helper ausführen

Öffne PowerShell und führe aus:

```powershell
cd C:\Users\Pascal\Desktop\Lernsystem\backend
.\.venv\Scripts\activate
python setup_helper.py
```

**Der Setup Helper wird:**
1. Nach deinem PostgreSQL-Passwort fragen
2. Die Verbindung testen
3. Das Passwort in `.env` speichern
4. Die Datenbank zurücksetzen
5. PostgreSQL-Extensions aktivieren

**Du wirst gefragt:**
- PostgreSQL-Passwort für User `postgres`
- Bestätigung für Datenbank-Reset

**Erwartete Ausgabe:**
```
======================================================================
🚀 LernsystemX Setup Helper
======================================================================

Step 1: PostgreSQL Configuration
----------------------------------------------------------------------

Current settings:
  Host: localhost
  Port: 5432
  User: postgres
  Database: lernsystemx_dev

Please enter your PostgreSQL password for user 'postgres':
(This is the password you set during PostgreSQL installation)

Password (attempt 1/3): ********
Testing connection... ✓ SUCCESS!

✓ Configuration saved to .env

Step 2: Database Reset
----------------------------------------------------------------------

This will:
  1. Drop database 'lernsystemx_dev' (if exists)
  2. Create fresh database 'lernsystemx_dev'
  3. Enable PostgreSQL extensions

Continue? (yes/no): yes

Connecting to PostgreSQL...
Terminating existing connections to 'lernsystemx_dev'...
Dropping database 'lernsystemx_dev'...
Creating database 'lernsystemx_dev'...
Enabling PostgreSQL extensions...
  ✓ uuid-ossp
  ✓ pgcrypto

✓ Database reset complete!

======================================================================
✓ Setup Helper Complete!
======================================================================

Next steps:
  1. Start the backend:
     python run.py

  2. Open browser and navigate to:
     http://localhost:5000/setup/status

  3. Click 'Initialize Database' to run all 40 migrations

The Setup Wizard will guide you through the rest!
```

---

### Schritt 2: Backend starten

```powershell
python run.py
```

**Erwartete Ausgabe:**
```
[INFO] System not installed - Setup Wizard mode active
[INFO] Please navigate to http://localhost:5000/setup/status
 * Running on http://127.0.0.1:5000
```

**Wichtig:** Jetzt sollten KEINE PostgreSQL-Verbindungsfehler mehr erscheinen!

---

### Schritt 3: Setup Wizard öffnen

Öffne Browser:

```
http://localhost:5000/setup/status
```

**Der Setup Wizard führt dich durch:**

1. ✅ **System Check** - Prüft Voraussetzungen
2. 🔄 **Database Initialize** - Führt alle 40 Migrationen aus
   - Dauer: ~15-20 Sekunden
   - Erstellt 112 Tabellen
   - Erstellt ~300 Indexes
   - Erstellt ~120 Foreign Keys
3. 👤 **Admin User** - Erstellt Admin-Benutzer
4. 🏢 **Organization** - Optional: Schule/Firma
5. 🤖 **AI Providers** - Optional: API-Keys
6. ✅ **Complete** - Fertig!

---

## 🐛 Troubleshooting

### Problem: "PostgreSQL password incorrect"

**Lösung 1:** Passwort herausfinden
```powershell
# Öffne pgAdmin
# Oder SQL Shell (psql)
# Das Passwort wurde bei der PostgreSQL-Installation gesetzt
```

**Lösung 2:** Passwort zurücksetzen
1. Öffne `C:\Program Files\PostgreSQL\17\data\pg_hba.conf`
2. Ändere `md5` zu `trust` für localhost
3. Starte PostgreSQL neu
4. Ändere Passwort:
   ```sql
   ALTER USER postgres WITH PASSWORD 'neues-passwort';
   ```
5. Ändere `trust` zurück zu `md5` in pg_hba.conf
6. Starte PostgreSQL neu

**Lösung 3:** Andere Standard-Passwörter probieren
- `admin`
- `password`
- `root`
- Leer (einfach Enter drücken)

---

### Problem: "PostgreSQL service not found"

```powershell
# Prüfe Service
Get-Service -Name "postgresql*"

# Starte Service
Start-Service -Name "postgresql-x64-17"
```

---

### Problem: "Port 5000 already in use"

```powershell
# Finde Prozess auf Port 5000
netstat -ano | findstr :5000

# Beende Prozess (ersetze PID)
taskkill /PID <PID> /F

# Oder ändere Port in run.py
```

---

## 📁 Wichtige Dateien

### Für Setup
- **`setup_helper.py`** - Interaktiver Setup-Assistent (NEU!)
- **`reset_database.py`** - Datenbank zurücksetzen
- **`.env`** - Umgebungsvariablen (wird automatisch aktualisiert)

### Dokumentation
- **`START_HIER.md`** - Diese Datei
- **`SETUP_ANLEITUNG.md`** - Detaillierte Anleitung
- **`FEHLER_BEHOBEN.md`** - Was wurde behoben
- **`backend/migrations/README.md`** - Migrations-Dokumentation

---

## ✅ Nach erfolgreichem Setup

Du hast dann:

- ✅ PostgreSQL korrekt konfiguriert
- ✅ Datenbank `lernsystemx_dev` erstellt
- ✅ 112 Tabellen mit kompletten Schema
- ✅ Admin-Benutzer angelegt
- ✅ System betriebsbereit

**Teste das System:**
```powershell
# Backend läuft auf
http://localhost:5000

# API-Endpunkte
http://localhost:5000/api/v1/docs

# Admin-Login (nach Setup Wizard)
POST http://localhost:5000/api/v1/auth/login
{
  "email": "admin@lernsystemx.local",
  "password": "dein-admin-passwort"
}
```

---

## 🎯 Was als Nächstes?

Nach dem Setup kannst du:

1. **Frontend starten** (optional)
   ```powershell
   cd ../frontend
   npm install
   npm run dev
   ```

2. **Test-Kurse erstellen**
   - Über API oder Frontend
   - Learning Methods hinzufügen

3. **LiveRoom testen**
   - WebRTC Video/Audio
   - AI-Whiteboard

4. **Dokumentation lesen**
   - `CLAUDE.md` - Projekt-Übersicht
   - `LernsystemX-Doku/` - Komplette Spezifikation

---

## 💡 Tipps

**Tipp 1:** Setup Helper speichert dein Passwort automatisch in `.env`

**Tipp 2:** Falls du die Datenbank nochmal zurücksetzen willst:
```powershell
python reset_database.py
# Oder
python setup_helper.py
```

**Tipp 3:** Alle Migrationen sind idempotent - du kannst sie mehrfach ausführen

**Tipp 4:** Backup vor Änderungen:
```powershell
& "C:\Program Files\PostgreSQL\17\bin\pg_dump.exe" -U postgres lernsystemx_dev > backup.sql
```

---

## 🆘 Hilfe

**Bei Problemen:**
1. Siehe `SETUP_ANLEITUNG.md` - Abschnitt "Troubleshooting"
2. Prüfe Logs in `backend/logs/`
3. PostgreSQL-Logs in `C:\Program Files\PostgreSQL\17\data\log\`

**Dokumentation:**
- Migrations: `backend/migrations/README.md`
- Backend: `backend/README.md`
- Datenbank: `LernsystemX-Doku/14_DB-Struktur.md`

---

## 🎉 Los geht's!

Führe einfach aus:

```powershell
cd C:\Users\Pascal\Desktop\Lernsystem\backend
.\.venv\Scripts\activate
python setup_helper.py
```

**Viel Erfolg! 🚀**
