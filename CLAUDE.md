# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LernsystemX (LSX)** is an AI-powered learning platform with 33 learning methods, 9 user roles, and real-time collaboration. Flask backend (Python 3.12+) and Vue.js 3 frontend.

**Key Features:**
- 33 learning methods (LM00-LM32) in 4 groups (A-D)
- 9 roles: Free, Premium, Creator, Teacher, School, Company, Support, Moderator, Admin
- AI content generation (Anthropic Claude, OpenAI GPT-4)
- Token-based premium model (10,000 tokens/month)
- Multi-language support (20 languages via DeepL)
- LiveRoom with WebRTC video/audio and AI-powered whiteboard

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
python run.py                  # http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

### Required Services
```bash
# PostgreSQL must be running
# Redis: redis-server
# Celery (optional): celery -A app.extensions.celery worker --loglevel=info
```

### First Time Setup
Navigate to `http://localhost:5000/setup/status` - the Setup Wizard handles database initialization, admin user, and AI configuration.

## Commands

### Backend (from `backend/` with venv activated)
```bash
python run.py                           # Start dev server with SocketIO
flask routes                            # List all API routes
flask shell                             # Interactive Python shell
pytest                                  # Run all tests
pytest tests/test_auth.py               # Run specific test
pytest --cov=app --cov-report=html      # Coverage report
```

### Frontend (from `frontend/`)
```bash
npm run dev          # Development server (Vite)
npm run build        # Production build
npm run preview      # Preview production build
npm run check        # Verify setup
vue-tsc --noEmit     # Type check only
```

### Database
```bash
# Direct PostgreSQL access
psql -U lernsystem -d lernsystemx_dev -h 10.0.10.222

# Migrations (numbered SQL files in backend/database/)
python run_migration.py      # Run migration
python check_migrations.py   # Check status
python test_migration.py     # Test before applying
```

## Architecture

### Tech Stack
| Layer | Technology |
|-------|------------|
| Backend | Flask 3.0, Python 3.12+ |
| Database | PostgreSQL with psycopg (connection pooling, **NO ORM**) |
| Cache/Queue | Redis, Celery |
| Real-time | Flask-SocketIO |
| Auth | JWT (Flask-JWT-Extended) |
| Frontend | Vue.js 3 (Composition API), TypeScript, Vite |
| State | Pinia |
| Styling | TailwindCSS |

### Key Patterns

**1. No ORM - Direct SQL with psycopg**

This project **intentionally avoids ORM** (no SQLAlchemy). All database operations use direct SQL with psycopg connection pooling.

```python
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository):
    @staticmethod
    def find_by_id(user_id: str) -> Optional[dict]:
        query = "SELECT * FROM users WHERE user_id = %s"
        return UserRepository.fetch_one(query, (user_id,))
```

**2. Repository Pattern**
- `BaseRepository` handles connection pooling
- All repositories inherit from `BaseRepository`
- Use `fetch_one()` for single results, `fetch_all()` for multiple
- Always use parameterized queries (prevent SQL injection)

**3. Factory Pattern**
```python
from app import create_app
app = create_app('development')  # or 'production', 'testing'
```

**4. Blueprint-Based API Gateway**
All routes under `/api/v1`:
- `/api/v1/auth` - Authentication
- `/api/v1/users`, `/api/v1/profile` - User management
- `/api/v1/courses` - Course operations
- `/api/v1/learning-methods` - Learning method instances
- `/api/v1/subscriptions`, `/api/v1/tokens` - Premium features
- `/api/v1/organisations` - Organization management
- `/api/v1/dashboard`, `/api/v1/analytics` - Data endpoints
- `/api/v1/admin/*` - Admin endpoints
- `/health` - Health checks

### Dual-Mode Operation

**Setup Wizard Mode** (first run):
- Only `/setup/*` routes available
- Access: `http://localhost:5000/setup/status`

**Normal Mode** (after setup):
- Full API routes via API Gateway
- Frontend: `http://localhost:5173`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Factory pattern (create_app)
│   ├── config.py                # Environment configs
│   ├── extensions.py            # Flask extensions
│   ├── api/                     # API blueprints (routes)
│   ├── models/                  # Pydantic validation models
│   ├── repositories/            # Database access (direct SQL)
│   ├── services/                # Business logic
│   ├── middleware/              # Auth, security headers
│   ├── gateway/                 # API Gateway (routing, rate limiting)
│   ├── security/                # Rate limiting, permissions
│   ├── monitoring/              # Prometheus metrics
│   └── ki/                      # AI prompt system & learning method mapping
├── setup/                       # Setup Wizard
├── database/                    # SQL migration files (001-046+)
└── run.py                       # Entry point

frontend/
├── src/
│   ├── api/                     # API services (Axios)
│   │   └── http.ts              # Base instance with JWT interceptor
│   ├── store/                   # Pinia stores
│   ├── components/              # Vue components
│   ├── pages/                   # Route pages
│   ├── layouts/                 # Layout components
│   ├── router/                  # Vue Router config
│   └── main.ts                  # Entry point
├── vite.config.ts
└── tailwind.config.js
```

## Database

**Numbered SQL migrations** in `backend/database/`. After full migration:
- **114 tables**, ~560 indexes, 71+ migration files
- PostgreSQL with JSONB for flexible data (learning method content, whiteboard data, etc.)

### Key Tables
- `users`, `roles`, `permissions`, `role_permissions` - User accounts & RBAC (10 roles, hierarchy level 1-9)
- `courses`, `chapters`, `lessons` - Course hierarchy (Course → Chapters → Lessons → Learning Methods)
- `learning_method_instances`, `learning_method_types` - 33 method types (LM00-LM32, JSONB data)
- `enrollments`, `course_access` - User-course relationships (access types: purchased, assigned, free, premium)
- `subscriptions`, `token_wallets`, `token_transactions` - Premium/billing
- `organisations`, `organisation_members` - Schools/Companies with token pools
- `ki_requests`, `ki_raw_inputs` - AI operation tracking (types: module_gen, method_gen, exam_gen, translation, summary)
- `rooms`, `room_participants`, `room_whiteboards`, `room_transcripts`, `room_recordings`, `room_ai_stats` - LiveRoom system
- `translations` - Multi-language content cache (unique index on content_type, content_id, language)
- `dashboards`, `dashboard_widgets`, `widget_registry` - Dashboard system (15+ widgets)
- `exams`, `exam_questions`, `exam_results` - Examination system
- `groups`, `group_members`, `group_resources` - Community groups
- `course_categories` - 5-level hierarchical category system (8 main categories)

## Learning Methods (33 Methods, LM00-LM32)

> **Master Document**: See `LernsystemX-Doku/02_Lernmethoden.md` for complete specifications.

### Group A - Explanatory Methods (LM00-LM07) - 8 methods
| ID | Name | KI Usage |
|----|------|----------|
| LM00 | Deep Explanation | Intensive |
| LM01 | Step-by-Step Explanation | Medium |
| LM02 | Interactive Theory | Medium |
| LM03 | Diagram/Visualization | Medium |
| LM04 | Glossary Auto-Generator | Medium |
| LM05 | Mindmap Generator | Medium |
| LM06 | Scenario Examples | Medium |
| LM07 | NPC Tutor Lecture | Intensive |

### Group B - Practice (LM08-LM17) - 10 methods
| ID | Name | KI Usage |
|----|------|----------|
| LM08 | Whiteboard Tasks | Intensive |
| LM09 | Code/IT-Config Sandbox | Medium |
| LM10 | Network Simulation | Medium |
| LM11 | IT Scenario Solving | Intensive |
| LM12 | Math Interactive | Medium |
| LM13 | Flashcards | Optional |
| LM14 | Drag & Drop | Optional |
| LM15 | Fill-in-the-Blanks | Optional |
| LM16 | Error Analysis | Medium |
| LM17 | Hands-on Lab | Intensive |

### Group C - Exam-Oriented (LM18-LM25) - 8 methods
| ID | Name | KI Usage |
|----|------|----------|
| LM18 | Free Text Long Answer | Medium |
| LM19 | IHK-Style Tasks | Intensive |
| LM20 | Multi-Step Practical Exam | Intensive |
| LM21 | Time Limit Training | Optional |
| LM22 | Exam Quiz (MC, Matching) | Optional |
| LM23 | Comprehension Checks | Optional |
| LM24 | Oral Explanation | Intensive |
| LM25 | Chapter Final Exam | Medium |

### Group D - Pro/Gamification (LM26-LM32) - 7 methods
| ID | Name | KI Usage |
|----|------|----------|
| LM26 | Adaptive Difficulty | Intensive |
| LM27 | Learning Path Generator | Intensive |
| LM28 | Persona Tutor | Intensive |
| LM29 | Socratic Dialog | Intensive |
| LM30 | Daily Recall / Spaced Repetition | Medium |
| LM31 | Quest/XP System | Optional |
| LM32 | Vocabulary Trainer (Vokabel Trainer) | Medium |

**Code Reference**: `backend/app/ki/learning_method_mapping.py`
**DB Constraint**: `method_type BETWEEN 0 AND 32`

## Coding Standards

### Python
- PEP 8, line length 100 chars
- Type hints required for all functions
- Google-style docstrings

### SQL
```python
# Good - parameterized query
query = "SELECT * FROM users WHERE email = %s"
result = UserRepository.fetch_one(query, (email,))

# Bad - SQL injection risk
query = f"SELECT * FROM users WHERE email = '{email}'"
```

### API Response Format
```json
{
  "success": true,
  "data": { ... },
  "meta": { "timestamp": "2025-01-15T10:30:00Z" }
}
```

Error:
```json
{
  "success": false,
  "error": { "code": "INVALID_INPUT", "message": "...", "field": "email" }
}
```

### Vue.js
Always use Composition API with `<script setup>`:
```vue
<script setup>
import { ref, computed } from 'vue'
const count = ref(0)
</script>
```

## Common Tasks

### Adding a New API Endpoint
1. Create route in `app/api/` blueprint
2. Add Pydantic model in `app/models/`
3. Add repository methods in `app/repositories/`
4. Add service logic if complex

### Adding a New Database Table
1. Create SQL migration: `backend/database/047_new_table.sql`
2. Run: `python run_migration.py`
3. Create repository (inherit `BaseRepository`)
4. Create Pydantic model

### Adding a New Learning Method
1. Add method definition to `app/ki/learning_method_mapping.py`
2. Update `learning_method_types` table if needed
3. Create frontend editor component in `components/editor/`
4. Add AI generation logic in `app/ki/` if applicable

## Common Pitfalls

1. **Don't use SQLAlchemy/ORM** - This project uses direct SQL with psycopg only
2. **Always use repository methods** - They handle connection pooling
3. **Setup Wizard first** - Most routes won't work until installation complete
4. **Redis required** - For JWT blacklist, rate limiting, Celery, caching
5. **Use `python run.py`** - Not `flask run` (SocketIO needs eventlet)
6. **method_type validation** - Must be between 0 and 32 (LM00-LM32)

## AI Integration (13 KI Modules)

### KI Pipeline Modules
| Category | Modules |
|----------|---------|
| **Content Input** | PDF/Doc Parser, Slide Parser, Math Parser, Whiteboard Analysis |
| **Content Generation** | Module Generator, Theory Sheet Generator, Learning Method Generator, Quiz Generator, Exam Simulation |
| **Content Enhancement** | Summarizer/Explain-KI, Multi-Language Engine (20 languages), Content Validator, KI Optimizer |

### Providers
- **Anthropic Claude**: Content generation, validation
- **OpenAI GPT-4**: Module generation, quizzes
- **DeepL**: Translation (20 languages)

Token costs: 500-6000 tokens per AI operation. Tracked in `token_transactions` and `ki_requests`.

```python
from app.services.ai_adapter import AIAdapter

result = AIAdapter.generate_content(
    prompt="Generate quiz...",
    provider="anthropic",
    user_id=user_id
)
```

### KI Request Types
`module_gen`, `method_gen`, `exam_gen`, `translation`, `summary`, `math_analysis`, `whiteboard_analysis`

## LiveRoom System

Real-time learning rooms with:
- WebRTC video/audio (mediasoup/Jitsi)
- AI-powered whiteboard with recognition (formulas, network diagrams, keywords)
- Live transcription & AI summaries (Whisper/Deepgram → GPT/Claude)
- Recording storage (hot: 30d S3 Standard, warm: 30-90d S3 IA, cold: >90d Glacier)

### Room Types
| Type | Description | AI | Recording | Max Participants |
|------|-------------|-----|-----------|------------------|
| `classroom` | Standard teaching | Optional | Yes | 50 |
| `seminar` | Workshops | Optional | Yes | 30 |
| `study` | Study groups | No | Optional | 10 |
| `exam` | Exam simulation (proctoring) | No | Yes | 100 |
| `ai` | KI-Tutor Room (1:1) | Yes | Yes | 5 |

### Participant Roles
`host` (full control), `teacher` (moderation), `student` (participant), `guest` (limited)

## Security

- JWT tokens (15min access, 7d refresh), blacklist in Redis
- Role-based access control (RBAC)
- Rate limiting: 100 req/min per user, 10 req/min for AI
- Passwords: bcrypt (cost factor 12)
- Pydantic validation for all inputs
- Row-Level Security for organization isolation

## Documentation

### German Technical Docs (`/LernsystemX-Doku/`)
Comprehensive system specifications (50+ documents). Key files:

| File | Content |
|------|---------|
| `00_System-Übersicht.md` | System architecture, C4 diagrams, full overview |
| `01_Rollenmodell.md` | 9 roles with permissions |
| `02_Lernmethoden.md` | **Master document** - All 33 learning methods (LM00-LM32) |
| `03_Zugriffssystem.md` | Access control & permissions |
| `04_Kurs-Architektur.md` | Course → Chapters → Lessons → Learning Methods |
| `09_KI-Pipeline.md` | 13 KI modules & workflows |
| `14_DB-Struktur.md` | Complete database schema (114 tables) |
| `16_Frontend-Struktur.md` | Vue.js frontend architecture |
| `17_Backend-Struktur.md` | Flask backend with Repository Pattern |
| `21_LiveRoom-System.md` | WebRTC, Whiteboard, Recordings |
| `35_Developer-Guide-KI-Prompts.md` | KI prompts for each learning method |

### API Docs
- `/backend/docs/api/` - REST API documentation
- Code documentation in English
