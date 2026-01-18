# LernsystemX Backend

Enterprise-grade Flask application with Domain-Driven Design architecture.

## Quick Start

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
python run.py

# Application runs on http://localhost:5000
```

### Production

```bash
# Using Gunicorn with config
gunicorn -c config/gunicorn.conf.py wsgi:app

# With WebSocket support (eventlet)
gunicorn -c config/gunicorn.conf.py -k eventlet wsgi:app
```

### Docker

```bash
# Build and run
docker-compose up -d backend-api-1 backend-api-2

# View logs
docker-compose logs -f backend-api-1
```

## Project Structure

```
backend/
├── app/                    # Main application (DDD architecture)
│   ├── api/               # HTTP Layer (endpoints)
│   ├── application/       # Application Services
│   ├── domain/            # Business Logic
│   ├── infrastructure/    # Technical Services
│   └── core/              # Core Configuration
├── config/                # Configuration files
│   ├── gunicorn.conf.py  # Production web server
│   └── logging.conf      # Logging setup
├── migrations/            # Database migrations (SQL)
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── run.py                 # Development entry point
├── wsgi.py                # Production entry point
└── requirements.txt       # Dependencies
```

## Documentation

- **Architecture**: See `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md`
- **Database**: See `LernsystemX-Doku/05_Technical/01_DB-Struktur.md`
- **API**: See `LernsystemX-Doku/05_Technical/02_API-Spezifikation.md`
- **Development Guide**: See `LernsystemX-Doku/07_Setup-Dev/03_Developer-Guide-KI.md`

## Database

Initialize database:
```bash
python run.py
# Navigate to http://localhost:5000/setup/status
```

Run migrations:
```bash
python scripts/migrations/run_all_migrations.py
```

## Testing

Run all tests:
```bash
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key

## API Endpoints

Health checks:
- `GET /health` - Application health
- `GET /health/ready` - Readiness check
- `GET /health/live` - Liveness check

Admin:
- `GET /api/v1/admin/system/version` - System version info
- `GET /api/v1/admin/system/health/detailed` - Detailed health

API Documentation (when running):
- `GET /api/docs` - Swagger/OpenAPI docs

## Security

- SQL Injection protection via parameterized queries
- JWT authentication (15min access + 7d refresh tokens)
- Rate limiting (100 req/min per user)
- CSRF protection
- OWASP Top 10 compliance

## Production

See [Production Checklist](../../.claude/PRODUCTION_READINESS_UPDATED.md)

## Support

Issues? Check:
1. Logs: `tail -f logs/lernsystemx.log`
2. Health: `curl http://localhost:5000/health`
3. Database: `psql service=devdb`

---

**Version**: 2.0 | **Framework**: Flask 3.x + psycopg3 | **Architecture**: DDD
