# LernsystemX - System Architecture Documentation

**Architecture Description conforming to ISO/IEC/IEEE 42010:2011**

---

## Document Control

| Property | Value |
|----------|-------|
| **Document ID** | LSX-ARCH-001 |
| **Version** | 1.0.0 |
| **Date** | 2025-11-15 |
| **Status** | Active Development |
| **Author** | Development Team |
| **Reviewed By** | - |
| **Approved By** | - |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Stakeholders and Concerns](#2-stakeholders-and-concerns)
3. [Architecture Viewpoints](#3-architecture-viewpoints)
4. [System Context View](#4-system-context-view)
5. [Logical View](#5-logical-view)
6. [Process View](#6-process-view)
7. [Development View](#7-development-view)
8. [Physical View](#8-physical-view)
9. [Data View](#9-data-view)
10. [Architecture Decisions](#10-architecture-decisions)
11. [Quality Attributes](#11-quality-attributes)
12. [Constraints and Assumptions](#12-constraints-and-assumptions)

---

## 1. Introduction

### 1.1 Purpose

This document provides a comprehensive architectural description of **LernsystemX (LSX)**, an AI-powered learning platform that enables users to create, learn, and publish educational content with 21 different learning methods.

### 1.2 Scope

The architecture covers:
- Backend API (Flask/Python)
- Frontend Application (Vue.js) - *separate document*
- AI Processing Pipeline (13 specialized modules)
- Real-time Communication (WebSockets, WebRTC)
- Payment Processing (Stripe integration)
- Multi-language Support (20 languages)

### 1.3 System Overview

**LernsystemX** is a microservices-oriented platform supporting:

- **9 User Roles**: Free, Premium, Creator, Teacher, School, Company, Support, Moderator, Admin
- **21 Learning Methods**: From basic flashcards to advanced AI-powered exam simulation
- **AI Integration**: Anthropic Claude & OpenAI GPT-4
- **Token Economy**: Usage-based pricing (10,000 tokens/month for Premium)
- **Global Publishing**: Content in 20 languages
- **Real-time Collaboration**: LiveRoom with video/whiteboard

---

## 2. Stakeholders and Concerns

### 2.1 Stakeholder Table

| Stakeholder | Concerns |
|-------------|----------|
| **End Users (Learners)** | Usability, learning effectiveness, mobile support, cost |
| **Content Creators** | Authoring tools, revenue sharing (75%), content protection |
| **Teachers/Schools** | Student management, progress tracking, curriculum alignment |
| **Companies** | Training ROI, compliance tracking, integration with HR systems |
| **Developers** | Code maintainability, API documentation, scalability |
| **System Administrators** | Deployment, monitoring, security, backup/recovery |
| **Business Owners** | Revenue generation, cost control, market scalability |
| **Compliance Officers** | GDPR compliance, data privacy, audit trails |

### 2.2 Key Concerns

- **Performance**: Support 10,000+ concurrent users
- **Security**: Protect user data and payment information (PCI-DSS)
- **Scalability**: Handle AI processing workload efficiently
- **Availability**: 99.9% uptime SLA
- **Maintainability**: Modular architecture for easy updates
- **Compliance**: GDPR, PCI-DSS, ISO 27001

---

## 3. Architecture Viewpoints

Following the **4+1 Architectural View Model** (Philippe Kruchten):

1. **Logical View** - System functionality and components
2. **Process View** - System runtime behavior and concurrency
3. **Development View** - Code organization and modules
4. **Physical View** - Deployment topology
5. **+1 Scenarios (Use Cases)** - Tie all views together

Additionally:
- **Data View** - Database schema and data flow

---

## 4. System Context View

### 4.1 Context Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LernsystemX Platform                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Frontend   │  │   Backend    │  │  AI Pipeline │      │
│  │   (Vue.js)   │◄─┤   (Flask)    │◄─┤  (Celery)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                    │             │
└─────────┼─────────────────┼────────────────────┼─────────────┘
          │                 │                    │
          ▼                 ▼                    ▼
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │   End Users  │  │  PostgreSQL  │  │  Anthropic   │
  │  (Browsers)  │  │     Redis    │  │   OpenAI     │
  └──────────────┘  └──────────────┘  └──────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │    Stripe    │
                  │   (Payment)  │
                  └──────────────┘
```

### 4.2 External Systems

| System | Purpose | Protocol | Criticality |
|--------|---------|----------|-------------|
| **Anthropic Claude API** | AI content generation, validation | HTTPS/REST | High |
| **OpenAI GPT-4 API** | Module generation, quizzes | HTTPS/REST | High |
| **DeepL API** | Translation to 20 languages | HTTPS/REST | Medium |
| **Stripe API** | Payment processing | HTTPS/REST | Critical |
| **TURN Server** | WebRTC relay for LiveRoom | UDP/TCP | Medium |
| **Email SMTP** | Transactional emails | SMTP | Low |

---

## 5. Logical View

### 5.1 High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Backend (Flask)                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Service │  │Course Service│  │  AI Service  │      │
│  │              │  │              │  │              │      │
│  │ - Register   │  │ - CRUD       │  │ - Generate   │      │
│  │ - Login      │  │ - Modules    │  │ - Translate  │      │
│  │ - JWT        │  │ - Methods    │  │ - Validate   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │User Service  │  │Payment Svc   │  │LiveRoom Svc  │      │
│  │              │  │              │  │              │      │
│  │ - Profile    │  │ - Subscribe  │  │ - WebRTC     │      │
│  │ - Roles      │  │ - Tokens     │  │ - Whiteboard │      │
│  │ - Progress   │  │ - Stripe     │  │ - SocketIO   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Component Descriptions

#### Authentication Service
- **Responsibility**: User authentication and authorization
- **Key Functions**: Register, Login, JWT token management, Role-based access control (RBAC)
- **Dependencies**: User model, Redis (token blacklist), bcrypt

#### Course Service
- **Responsibility**: Course and module management
- **Key Functions**: CRUD operations, module creation, learning method assignment
- **Dependencies**: Course model, Module model, AI service

#### AI Service
- **Responsibility**: AI-powered content generation
- **Key Functions**: Quiz generation, exam simulation, content validation, translation
- **Dependencies**: Anthropic API, OpenAI API, DeepL API, Token wallet

#### Payment Service
- **Responsibility**: Subscription and token package processing
- **Key Functions**: Stripe integration, webhook handling, subscription lifecycle
- **Dependencies**: Stripe API, Subscription model, Payment history

#### LiveRoom Service
- **Responsibility**: Real-time collaboration
- **Key Functions**: WebRTC signaling, whiteboard sync, video/audio streaming
- **Dependencies**: Flask-SocketIO, TURN server

---

## 6. Process View

### 6.1 AI Content Generation Flow

```
User Request → API Gateway → JWT Validation → Token Check
                                                    │
                                                    ▼
                                            Token Sufficient?
                                               /        \
                                             Yes        No
                                              │          │
                                              ▼          ▼
                                        Celery Task   Reject
                                              │
                                              ▼
                                        AI API Call
                                        (Claude/GPT-4)
                                              │
                                              ▼
                                        Deduct Tokens
                                              │
                                              ▼
                                        Store Result
                                              │
                                              ▼
                                        Return to User
```

### 6.2 User Authentication Flow

```
1. User submits credentials (email, password)
2. Backend validates input format
3. Query User from database
4. Verify password with bcrypt
5. Generate JWT access + refresh tokens
6. Return tokens to client
7. Client stores tokens (localStorage/cookie)
8. Subsequent requests include JWT in Authorization header
9. Backend validates JWT signature and expiration
10. Extract user_id and role from JWT payload
11. Process request based on role permissions
```

### 6.3 Payment Processing Flow

```
User → Subscribe/Buy Tokens → Stripe Checkout Session
                                        │
                                        ▼
                                  User Completes Payment
                                        │
                                        ▼
                                Stripe Webhook → Backend
                                        │
                                        ▼
                                Verify Webhook Signature
                                        │
                                        ▼
                        Update Subscription/Token Wallet
                                        │
                                        ▼
                                Send Confirmation Email
```

---

## 7. Development View

### 7.1 Backend Structure (Flask)

```
backend/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration classes
│   ├── extensions.py            # Flask extensions
│   │
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py              # User, Role
│   │   ├── course.py            # Course, Module, Enrollment
│   │   ├── learning_method.py   # MethodInstance, Progress
│   │   ├── token.py             # TokenWallet, TokenTransaction
│   │   ├── subscription.py      # Subscription, PaymentHistory
│   │   ├── ai_request.py        # AIRequest, AIResponse
│   │   └── liveroom.py          # LiveRoom, Participant
│   │
│   ├── routes/                  # API Blueprints
│   │   ├── auth.py              # /api/v1/auth
│   │   ├── users.py             # /api/v1/users
│   │   ├── courses.py           # /api/v1/courses
│   │   ├── ai.py                # /api/v1/ai
│   │   ├── payments.py          # /api/v1/payments
│   │   ├── community.py         # /api/v1/community
│   │   └── liveroom.py          # /api/v1/liveroom
│   │
│   ├── services/                # Business logic
│   │   ├── auth_service.py
│   │   ├── course_service.py
│   │   ├── ai_service.py
│   │   ├── payment_service.py
│   │   └── liveroom_service.py
│   │
│   ├── tasks/                   # Celery background tasks
│   │   ├── ai_tasks.py          # AI generation tasks
│   │   ├── email_tasks.py       # Email sending
│   │   └── export_tasks.py      # PDF/Export generation
│   │
│   ├── middleware/              # Custom middleware
│   │   ├── auth_middleware.py   # JWT verification
│   │   └── role_middleware.py   # RBAC enforcement
│   │
│   └── schemas/                 # Marshmallow schemas
│       ├── user_schema.py
│       ├── course_schema.py
│       └── ai_schema.py
│
├── tests/                       # Unit & integration tests
├── run.py                       # Application entry point
└── requirements.txt             # Python dependencies
```

### 7.2 Module Dependencies

- **Models** → No dependencies (pure data layer)
- **Services** → Depend on Models
- **Routes** → Depend on Services and Schemas
- **Tasks** → Depend on Services
- **Middleware** → Depend on Models (User, Role)

---

## 8. Physical View

### 8.1 Deployment Architecture (Production)

```
┌─────────────────────────────────────────────────────────────┐
│                       Load Balancer                         │
│                        (Nginx)                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Backend     │ │  Backend     │ │  Backend     │
│  Instance 1  │ │  Instance 2  │ │  Instance 3  │
│  (Gunicorn)  │ │  (Gunicorn)  │ │  (Gunicorn)  │
└──────────────┘ └──────────────┘ └──────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  PostgreSQL  │ │    Redis     │ │   Celery     │
│   Primary    │ │   Cluster    │ │   Workers    │
└──────────────┘ └──────────────┘ └──────────────┘
        │
        ▼
┌──────────────┐
│  PostgreSQL  │
│   Replica    │
└──────────────┘
```

### 8.2 Infrastructure Components

| Component | Technology | Purpose | Scalability |
|-----------|-----------|---------|-------------|
| **Load Balancer** | Nginx | Distribute traffic | Horizontal |
| **Backend API** | Flask + Gunicorn | REST API, WebSocket | Horizontal (3-10 instances) |
| **Database** | PostgreSQL 15 | Primary data store | Vertical + Read replicas |
| **Cache** | Redis Cluster | Session, cache, rate limiting | Horizontal |
| **Task Queue** | Celery + Redis | Async AI processing | Horizontal (workers) |
| **File Storage** | S3/MinIO | User uploads, generated content | Horizontal |
| **Monitoring** | Prometheus + Grafana | Metrics, alerting | - |

---

## 9. Data View

### 9.1 Core Entity-Relationship Model

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│   User   │──1:N──│Enrollment│──N:1──│  Course  │
└──────────┘       └──────────┘       └──────────┘
     │                                       │
     │ 1:1                                 1:N
     ▼                                       ▼
┌──────────┐                         ┌──────────┐
│TokenWalet│                         │  Module  │
└──────────┘                         └──────────┘
     │                                       │
     │ 1:N                                 1:N
     ▼                                       ▼
┌──────────┐                         ┌──────────┐
│TokenTrans│                         │  Method  │
└──────────┘                         └──────────┘

┌──────────┐       ┌──────────┐
│   User   │──1:N──│AIRequest │
└──────────┘       └──────────┘

┌──────────┐       ┌──────────┐
│   User   │──1:1──│Subscript.│
└──────────┘       └──────────┘
```

### 9.2 Key Database Tables

| Table | Purpose | Estimated Rows |
|-------|---------|----------------|
| `users` | User accounts | 100K - 1M |
| `roles` | User roles (9 types) | 9 (fixed) |
| `courses` | Course content | 10K - 100K |
| `modules` | Course modules | 100K - 1M |
| `learning_methods` | Method instances | 1M - 10M |
| `enrollments` | User-course relationships | 1M - 10M |
| `token_wallets` | User token balances | 100K - 1M |
| `token_transactions` | Token usage history | 10M - 100M |
| `ai_requests` | AI processing queue | 1M - 10M |
| `subscriptions` | Premium subscriptions | 10K - 100K |

---

## 10. Architecture Decisions

### 10.1 ADR-001: Flask over Django

**Status**: Accepted

**Context**: Need lightweight, flexible framework for API development

**Decision**: Use Flask with Blueprint pattern instead of Django

**Rationale**:
- Microservices-friendly (no monolithic ORM)
- Better WebSocket support (Flask-SocketIO)
- Smaller learning curve for team
- More control over architecture

**Consequences**:
- Manual setup of extensions
- No built-in admin panel (will build custom)

---

### 10.2 ADR-002: PostgreSQL over MongoDB

**Status**: Accepted

**Context**: Need reliable, ACID-compliant database

**Decision**: Use PostgreSQL for primary data store

**Rationale**:
- Strong relational data (users, courses, enrollments)
- ACID transactions critical for payments
- Better query performance for complex joins
- Mature ecosystem and tooling

**Consequences**:
- Schema migrations required (Alembic)
- Less flexible for unstructured data

---

### 10.3 ADR-003: Celery for AI Processing

**Status**: Accepted

**Context**: AI API calls can take 5-30 seconds

**Decision**: Use Celery with Redis as message broker

**Rationale**:
- Prevents blocking HTTP requests
- Retry mechanism for failed AI calls
- Rate limiting across workers
- Scalable worker pool

**Consequences**:
- Additional Redis dependency
- More complex error handling

---

### 10.4 ADR-004: JWT for Authentication

**Status**: Accepted

**Context**: Need stateless authentication for API

**Decision**: Use JWT tokens (Flask-JWT-Extended)

**Rationale**:
- Stateless (no server-side session storage)
- Scalable across multiple backend instances
- Include user role in token payload
- Industry standard

**Consequences**:
- Token revocation requires Redis blacklist
- Larger payload size than session cookies

---

### 10.5 ADR-005: Token-Based Premium Model

**Status**: Accepted

**Context**: Need fair pricing for AI features

**Decision**: Implement token-based usage system (10K tokens/month for Premium)

**Rationale**:
- Transparent cost control for users
- Prevents abuse of expensive AI calls
- Flexible pricing tiers
- Aligns with AI API billing models

**Consequences**:
- Complex wallet/transaction tracking
- Need real-time token deduction

---

## 11. Quality Attributes

### 11.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | < 200ms | Prometheus |
| AI Generation (Quiz) | < 10s | Application logs |
| Database Query Time | < 50ms | PostgreSQL slow query log |
| WebSocket Latency | < 100ms | Client-side monitoring |
| Concurrent Users | 10,000+ | Load testing (Locust) |

### 11.2 Scalability

- **Horizontal Scaling**: Backend instances (3-10)
- **Database**: Read replicas for heavy queries
- **Celery Workers**: Auto-scaling based on queue length
- **Redis**: Cluster mode for high availability

### 11.3 Security

- **Authentication**: JWT with RS256 signing
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: TLS 1.3 in transit, AES-256 at rest
- **Password Hashing**: bcrypt (cost factor 12)
- **Rate Limiting**: 200 requests/hour per user
- **Input Validation**: Marshmallow schemas
- **SQL Injection**: Parameterized queries (SQLAlchemy)
- **XSS Protection**: Content Security Policy headers

### 11.4 Availability

- **Target SLA**: 99.9% uptime (< 8.76 hours downtime/year)
- **Load Balancer**: Nginx with health checks
- **Database**: Primary + replica with automatic failover
- **Monitoring**: Prometheus + Grafana alerts
- **Backup**: Daily automated backups (7-day retention)

---

## 12. Constraints and Assumptions

### 12.1 Technical Constraints

- **Python Version**: 3.12+ (for latest type hints)
- **Database**: PostgreSQL 15+ (for JSONB performance)
- **Redis**: 7+ (for ACL support)
- **Browser Support**: Chrome 90+, Firefox 88+, Safari 14+

### 12.2 Business Constraints

- **Budget**: Cost-effective infrastructure (prefer managed services)
- **Timeline**: Phased rollout (MVP in 3 months)
- **Team Size**: 2-3 developers
- **Compliance**: GDPR, PCI-DSS

### 12.3 Assumptions

- Users have stable internet connection (>= 5 Mbps for LiveRoom)
- AI API availability >= 99.5%
- Stripe uptime >= 99.9%
- Average AI token usage: 3,000 tokens/user/month

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-15 | Development Team | Initial architecture documentation |

---

**Document Classification**: Internal Use

**Compliance**: ISO/IEC/IEEE 42010:2011 - Systems and software engineering — Architecture description
