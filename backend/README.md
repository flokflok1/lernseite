# LernsystemX Backend

**AI-Powered Learning Platform - Backend API**

Version: 1.0.0
Python: 3.12+
Framework: Flask 3.0

Documentation compliant with ISO/IEC/IEEE 26515:2018 (Developer Documentation)

---

## Table of Contents

- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

LernsystemX Backend provides the REST API and WebSocket infrastructure for the AI-powered learning platform. Key features:

- **21 Learning Methods**: From flashcards to AI-powered exam simulation
- **9 Role Model**: Free, Premium, Creator, Teacher, School, Company, Support, Moderator, Admin
- **AI Integration**: Anthropic Claude & OpenAI GPT-4
- **Token-Based Premium**: 10,000 tokens/month for €14.99
- **Real-time Features**: LiveRoom with WebRTC support
- **Multi-language**: 20 languages via DeepL translation

---

## Technology Stack

### Core Framework
- **Flask 3.0** - Web framework with Blueprint architecture
- **Python 3.12** - Programming language
- **Gunicorn** - Production WSGI server

### Database & Caching
- **PostgreSQL** - Primary database (psycopg with connection pooling, no ORM)
- **Redis** - Caching, sessions, rate limiting, message queue

### Background Processing
- **Celery** - Asynchronous task queue for AI processing
- **Eventlet** - WebSocket async support

### Authentication & Security
- **Flask-JWT-Extended** - JWT token authentication
- **bcrypt** - Password hashing
- **Flask-Limiter** - Rate limiting

### AI Integration
- **Anthropic Claude API** - Content generation, validation
- **OpenAI GPT-4** - Module generation, quizzes
- **DeepL** - Translation engine

### Payment Processing
- **Stripe** - Subscription and token package payments

### Real-time Communication
- **Flask-SocketIO** - WebSocket support
- **WebRTC** - Video/audio for LiveRoom

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py           # Application factory (create_app)
│   ├── config.py             # Configuration classes
│   ├── extensions.py         # Flask extensions initialization
│   ├── models/               # Pydantic validation models
│   ├── api/                  # API blueprints
│   ├── repositories/         # Database access layer (Repository pattern)
│   ├── services/             # Business logic
│   ├── middleware/           # Custom middleware
│   ├── gateway/              # API Gateway layer
│   ├── security/             # Security features (rate limiting, permissions)
│   ├── monitoring/           # Prometheus metrics
│   └── ki/                   # AI prompt system
├── tests/                    # Unit and integration tests
├── logs/                     # Application logs (gitignored)
├── uploads/                  # User-uploaded files (gitignored)
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Local environment (gitignored)
└── README.md                 # This file
```

---

## Prerequisites

### Required Software
- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Redis 7+** - [Download](https://redis.io/download/)

### Optional
- **Git** - Version control
- **Docker** - Container deployment (optional)

---

## Installation

### 1. Clone Repository

```bash
cd C:\Users\Pascal\Desktop\Lernsystem\backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE lernsystemx_dev;

-- Create user (optional)
CREATE USER lsx_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lernsystemx_dev TO lsx_user;
```

---

## Configuration

### 1. Environment Variables

Copy `.env.example` to `.env`:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

### 2. Configure `.env`

**Minimum Required Configuration:**

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-random-secret-key-generate-this

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/lernsystemx_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-jwt-secret-generate-this
```

**For AI Features (Optional in Development):**

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
OPENAI_API_KEY=sk-...

# DeepL
DEEPL_API_KEY=...
```

### 3. Generate Secret Keys

```python
# Run in Python shell
import secrets
print("SECRET_KEY:", secrets.token_urlsafe(32))
print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))
```

---

## Running the Application

### Development Server (with WebSocket support)

```bash
python run.py
```

Application runs at: `http://localhost:5000`

### Production Server (Gunicorn)

```bash
gunicorn -w 1 -b 0.0.0.0:5000 --worker-class eventlet run:app
```

### Start Redis (Required)

```bash
# Windows (if installed via WSL or native)
redis-server

# macOS
brew services start redis

# Linux
sudo systemctl start redis
```

### Start Celery Worker (For AI Tasks)

```bash
celery -A app.extensions.celery worker --loglevel=info
```

---

## Development Workflow

### 1. Database Management

**Note:** This project uses **raw SQL migrations** (no ORM). Database schema is managed via:
- Setup Wizard at `http://localhost:5000/setup/status` (first-time installation)
- SQL migration scripts in `backend/database/migrations/`
- Migration system in `setup/migrations.py`

```bash
# First-time setup: Use the Setup Wizard
# Navigate to: http://localhost:5000/setup/status
```

### 2. Flask CLI Commands

```bash
# Initialize database
flask init-db

# Seed database with test data
flask seed-db

# Create admin user
flask create-admin

# View all routes
flask routes

# Run tests
flask test

# Flask shell (interactive)
flask shell
```

### 3. Code Quality

```bash
# Format code (install black)
pip install black
black app/

# Lint code (install flake8)
pip install flake8
flake8 app/

# Type checking (install mypy)
pip install mypy
mypy app/
```

---

## API Documentation

### Base URL
```
http://localhost:5000/api/v1
```

### Authentication
All protected endpoints require JWT token in header:
```
Authorization: Bearer <access_token>
```

### Endpoints (Will be implemented in Phase 4)

```
POST   /api/v1/auth/register        # User registration
POST   /api/v1/auth/login           # User login
POST   /api/v1/auth/refresh         # Refresh token
POST   /api/v1/auth/logout          # Logout

GET    /api/v1/users/me             # Get current user
PATCH  /api/v1/users/me             # Update profile

GET    /api/v1/courses              # List courses
POST   /api/v1/courses              # Create course
GET    /api/v1/courses/:id          # Get course
PATCH  /api/v1/courses/:id          # Update course
DELETE /api/v1/courses/:id          # Delete course

POST   /api/v1/ai/generate-quiz     # Generate quiz
POST   /api/v1/ai/generate-exam     # Generate exam
POST   /api/v1/ai/translate         # Translate content

POST   /api/v1/payments/subscribe   # Create subscription
POST   /api/v1/payments/tokens      # Buy token package
```

### Health Check
```bash
GET /health
```

---

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Generate Coverage Report

```bash
pytest --cov=app --cov-report=html
```

---

## Deployment

### Docker (Recommended for Production)

```bash
# Build image (Docker file will be created in Phase 10)
docker build -t lernsystemx-backend .

# Run container
docker run -p 5000:5000 --env-file .env lernsystemx-backend
```

### Manual Deployment

1. Install dependencies on server
2. Configure environment variables
3. Setup PostgreSQL and Redis
4. Run Gunicorn with systemd/supervisor

---

## Troubleshooting

### Database Connection Error

```
Error: could not connect to server
```

**Solution:**
- Check PostgreSQL is running: `pg_isready`
- Verify `DATABASE_URL` in `.env`
- Check firewall settings

### Redis Connection Error

```
Error: Error 111 connecting to localhost:6379. Connection refused.
```

**Solution:**
- Start Redis: `redis-server`
- Verify `REDIS_URL` in `.env`

### Import Errors

```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
- Activate virtual environment
- Install dependencies: `pip install -r requirements.txt`

### Port Already in Use

```
OSError: [Errno 48] Address already in use
```

**Solution:**
- Kill process on port 5000: `lsof -ti:5000 | xargs kill -9` (macOS/Linux)
- Or change port in `.env`: `PORT=5001`

---

## Documentation References

- **API Specification**: `docs/api/` (Phase 9)
- **Architecture**: `docs/architecture/system-architecture.md`
- **Coding Standards**: `docs/development/coding-standards.md`
- **Database Schema**: `docs/database/schema.md` (Phase 3)

---

## Support

For issues and questions:
- **Issues**: Create GitHub issue
- **Documentation**: See `docs/` directory
- **Architecture**: Review `docs/architecture/`

---

**LernsystemX Backend** - Built with systematic development practices following ISO standards.
