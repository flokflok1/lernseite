# 32_API-Gateway.md (Final)  
Version: 1.0  
Stand: Final

Dieses Dokument beschreibt das gesamte **API-Gateway-System** des LSX Lernsystems.  
Das API-Gateway ist die zentrale Schicht, die **alle Anfragen** reguliert, steuert, validiert und weiterleitet.  
Es bildet die erste technische Sicherheitsbarriere und orchestriert sämtliche Microservices.

---

# 1. Ziele des API-Gateways

Das API-Gateway soll:

- als zentraler Einstiegspunkt für alle Clients dienen  
- Routing zu Backend-Services übernehmen  
- Authentifizierung & Autorisierung prüfen  
- Rate Limits durchsetzen  
- API-Versionierung ermöglichen  
- Monitoring & Logging bündeln  
- Caching an der richtigen Stelle aktivieren  
- WebSockets (LiveRoom) verwalten  
- statische Assets ausliefern (nur wo sinnvoll)  

Es ersetzt einzelne, unkontrollierte API-Endpunkte durch einen einheitlichen Kontrollpunkt.

---

# 2. Architekturübersicht

Das Gateway sitzt VOR allen Services:

[User Browser / Mobile App]
↓
[API Gateway (Traefik / Nginx / Kong / Envoy)]
↓
[Backend API Services]
↓
[Worker / KI-Pipeline / Datenbanken]

yaml
Code kopieren

---

# 3. Verantwortlichkeiten

Das Gateway übernimmt folgende Aufgaben:

- Authentifizierung / JWT-Validierung  
- Header-Validierung  
- Rate Limiting  
- IP-Filtering (Firewall Layer 7)  
- Routing zu Microservices  
- Domain- und Tenant-Routing (Organisationen)  
- Logging & Request Tracking  
- CORS-Handling  
- WebSocket Proxy  
- Request Size Limits  
- Throttling für KI-Requests  

---

# 4. Routing-Struktur

LSX verwendet das folgende Routenlayout:

/api/v1/auth/* → Auth-Service
/api/v1/users/* → User-Service
/api/v1/courses/* → Course-Service
/api/v1/modules/* → Module-Service
/api/v1/methods/* → Learning-Methods-Service
/api/v1/community/* → Community-Service
/api/v1/creator/* → Creator-Service
/api/v1/organisation/* → Org-Service
/api/v1/exams/* → Exam-Service
/api/v1/liveroom/* → LiveRoom WebSocket Gateway
/api/v1/ki/* → KI-Pipeline-Service
/api/v1/payments/* → Payment-Service
/api/v1/analytics/* → Analytics-Service
/api/v1/admin/* → Admin-Service

yaml
Code kopieren

**Alle Routes laufen über das API-Gateway und werden dort validiert.**

---

# 5. Versionierung (API Versioning)

LSX verwendet **URL-basierte Versionierung**:

- `/api/v1/…` = stabile Version  
- `/api/v2/…` = neue Versionen, Beta, Breaking Changes  

Regeln:

- v1 bleibt kompatibel  
- v2 wird parallel eingeführt  
- Migration erfolgt schrittweise  
- Deprecation-Hinweise werden über den Header gesendet  

Header:

X-LSX-API-Version: 1
X-LSX-API-Deprecated: false

yaml
Code kopieren

---

# 6. Authentifizierung im Gateway

Jeder Request durchläuft:

1. **JWT Access Token Check**  
2. **Refresh Token Logik (falls expired)**  
3. **Rollenprüfung**  
4. **Organisation Routing** (Mandantenerkennung)  

### 6.1 Header Anforderungen

```
Authorization: Bearer <jwt>
X-LSX-Client: web|mobile|admin
X-LSX-Org-ID: optional (automatisch erkannt)
```

yaml
Code kopieren

### 6.2 Token Parsing

Das Gateway validiert:

- Signatur  
- Ablaufzeit  
- Rollen  
- Organisation  

Wenn ungültig → `401 Unauthorized`

---

# 7. Rate Limits

Beispiele:

### 7.1 Standardlimits

| Route | Limit |
|-------|--------|
| Auth | 5 Requests / Minute / IP |
| KI | 30 Requests / Minute / User |
| Analytics | 60 / Minute |
| LiveRoom | 100 / Minute |
| Public API | 10 / Minute |

### 7.2 Organisationen können erweiterte Limits kaufen

- Schulen: +200 %  
- Unternehmen: +500 %  
- Premium-User: +50 %  

---

# 8. Multi-Tenant Routing (Schulen/Unternehmen)

Das Gateway erkennt anhand der Domain:

schule123.de → Org 51
training-firma.com → Org 88
academy.lsx.com → LSX Default

makefile
Code kopieren

Intern:

X-LSX-Org-ID

yaml
Code kopieren

wird automatisch gesetzt.

Multi-Tenant Regeln:

- Keine Cross-Tenant Zugriffe  
- Jede Organisation hat eigene Ressourcen  
- LiveRoom Instanzen separat  
- Tokenpools separat  

---

# 9. CORS-Konfiguration

Nur definierte Domains werden akzeptiert:

*.lsx.com
*.schule-domain.de
*.firma-domain.com
localhost:3000

makefile
Code kopieren

Methoden:

GET, POST, PATCH, DELETE, OPTIONS

css
Code kopieren

Sichere Header:

Authorization, Content-Type, X-LSX-*

yaml
Code kopieren

---

# 10. WebSocket Routing – LiveRoom

Das Gateway leitet WebSockets weiter:

/api/v1/liveroom/ws

yaml
Code kopieren

Features:

- Token-Authentifizierung  
- Room-Validation  
- Anti-Flood Protection  
- Heartbeat Messages  
- Auto-Reconnect  

---

# 11. Request-Validation

Jeder Request wird geprüft:

- Header  
- Body Size (max. 20MB)  
- JSON-Format  
- Rate Limits  
- Rolle  
- Organisation  
- Content-Type  

Ungültig → `400 / 403`

---

# 12. Gateway-Logging

Jeder Request erhält eine Tracking-ID:

X-LSX-Request-ID

yaml
Code kopieren

Logs enthalten:

- Pfad  
- Nutzer-ID  
- Organisation  
- Dauer  
- Statuscode  
- IP  
- KI-Tokens (falls KI-Service)  
- User-Agent  

---

# 13. Fehlerbehandlung

Gateway erzeugt:

### 13.1 Standardfehler

- 400 → Bad Request  
- 401 → Unauthorized  
- 403 → Forbidden  
- 404 → Not Found  
- 429 → Too Many Requests  
- 502 → Bad Gateway (Backend down)  

### 13.2 Einheitliche Fehlerstruktur

```json
{
  "success": false,
  "error_code": "API-403",
  "message": "Access denied",
  "request_id": "abc-123-xyz"
}
14. Sicherheitsmechanismen
WAF (Web Application Firewall)

DDoS Schutz

Geo Blocking

Bot Filter

SQL Injection Blocker

Header Whitelisting

Payload Inspection

15. API-Gateway Deployment
Empfehlung:
Traefik oder Kong

Features:

automatische Zertifikate (Let’s Encrypt)

Load Balancing

Canary Releases

Rate Limiting

Header Injection

Rewrites & Redirects

Multi-Tenant Domain Routing

16. Zusammenfassung
Das LSX API-Gateway ist:

sicher

skalierbar

zentralisiert

modular

mandantenfähig

KI-optimiert

professionell

zukunftssicher

Es bildet den Kern aller Verbindungen zwischen Frontend, Backend, KI, Organisationen und Workern.

Dokument abgeschlossen.