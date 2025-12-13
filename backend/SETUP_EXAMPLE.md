# LernsystemX Setup Wizard - API Verwendung

Der Setup Wizard ist jetzt vollständig implementiert! Du kannst das gesamte Setup über die API durchführen.

## Verfügbare Endpunkte

### 1. Status prüfen
```bash
curl http://localhost:5000/api/setup/status
```

Antwort:
```json
{
  "success": true,
  "installed": false,
  "requires_setup": true
}
```

### 2. Datenbank-Verbindung testen
```bash
curl -X POST http://localhost:5000/api/setup/test-database \
  -H "Content-Type: application/json" \
  -d '{
    "host": "10.0.10.10",
    "port": "5432",
    "dbname": "lernsystemx_dev",
    "user": "lernsystem",
    "password": "your_secure_password"
  }'
```

### 3. Komplettes Setup in einem Schritt
```bash
curl -X POST http://localhost:5000/api/setup/complete \
  -H "Content-Type: application/json" \
  -d '{
    "database": {
      "host": "10.0.10.10",
      "port": "5432",
      "dbname": "lernsystemx_dev",
      "user": "lernsystem",
      "password": "your_secure_password"
    },
    "admin": {
      "email": "admin@lernsystemx.de",
      "username": "admin",
      "password": "secure_admin_password_123",
      "first_name": "System",
      "last_name": "Administrator"
    }
  }'
```

Diese Anfrage wird:
1. ✅ Datenbank-Verbindung testen
2. ✅ Alle Tabellen erstellen
3. ✅ Admin-User anlegen
4. ✅ Installation finalisieren

Antwort bei Erfolg:
```json
{
  "success": true,
  "message": "Setup completed successfully! System is now installed.",
  "steps_completed": [
    "database_connection_test",
    "database_initialization",
    "admin_user_creation",
    "installation_finalized"
  ],
  "admin_email": "admin@lernsystemx.de"
}
```

## Schritt-für-Schritt (falls gewünscht)

### Schritt 1: Datenbank initialisieren
```bash
curl -X POST http://localhost:5000/api/setup/initialize-database \
  -H "Content-Type: application/json" \
  -d '{
    "host": "10.0.10.10",
    "port": "5432",
    "dbname": "lernsystemx_dev",
    "user": "lernsystem",
    "password": "your_secure_password"
  }'
```

### Schritt 2: Admin-User erstellen
```bash
curl -X POST http://localhost:5000/api/setup/create-admin \
  -H "Content-Type: application/json" \
  -d '{
    "database": {
      "host": "10.0.10.10",
      "port": "5432",
      "dbname": "lernsystemx_dev",
      "user": "lernsystem",
      "password": "your_secure_password"
    },
    "admin": {
      "email": "admin@lernsystemx.de",
      "username": "admin",
      "password": "secure_admin_password_123",
      "first_name": "System",
      "last_name": "Administrator"
    }
  }'
```

### Schritt 3: Installation finalisieren
```bash
curl -X POST http://localhost:5000/api/setup/finalize \
  -H "Content-Type: application/json" \
  -d '{
    "admin_email": "admin@lernsystemx.de",
    "version": "1.0.0"
  }'
```

## PostgreSQL auf VM einrichten

Auf deiner VM (10.0.10.10):

```bash
docker run -d --name postgres \
  -e POSTGRES_USER=lernsystem \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e POSTGRES_DB=lernsystemx_dev \
  -p 5432:5432 \
  postgres:15
```

## Nach dem Setup

Nach erfolgreichem Setup:
1. Backend neu starten
2. `.env` wird automatisch aktualisiert (optional - für zukünftige Starts)
3. System ist einsatzbereit!

## Troubleshooting

### Fehler: "System already installed"
```bash
# Install-Datei löschen für Neuinstallation
rm instance/.install
```

### Fehler: "Connection failed"
- PostgreSQL auf VM prüfen: `docker ps`
- Firewall-Regel auf VM prüfen
- Von Windows aus testen: `telnet 10.0.10.10 5432`

### Fehler: "Admin user already exists"
- Datenbank zurücksetzen:
```bash
# Auf VM:
docker exec -it postgres psql -U lernsystem -d lernsystemx_dev
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
\q
```
