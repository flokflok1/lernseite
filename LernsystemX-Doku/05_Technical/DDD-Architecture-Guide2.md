# 🎯 DDD Architecture Guide - Backend + Frontend
**Comprehensive Reference Document for LernSystemX**

**Version:** 1.0  
**Stand:** 20.01.2026  
**Autor:** Development Team  
**Sprache:** Deutsch + English Code Examples

---

## 📖 Inhaltsverzeichnis

1. [Quick Reference](#quick-reference)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Architecture](#frontend-architecture)
4. [Backend ↔ Frontend Flow](#backend--frontend-flow)
5. [Real Examples](#real-examples)
6. [Decision Trees](#decision-trees)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

# 🚀 Quick Reference

## Backend & Frontend Side by Side

```
BACKEND:                        FRONTEND:
─────────────────────────────────────────────────────────

🔴 api/                         🔴 presentation/
   Routes (HTTP)                   Components, Views, Router
   Blueprints                       What user SEES
   
🟡 application/                 🟡 application/
   Services (Orchestration)        Services, Stores, Composables
   Business Logic Delegation       What HAPPENS

🟢 domain/                      🟢 domain/
   Models (ai/, social/, etc)      Models, Value Objects, Factories
   Value Objects                   What IS that?
   Factories                        
   Repository Interfaces           
   
🔵 infrastructure/              🔵 infrastructure/
   Persistence (DB)                API Clients, WebSocket
   Cache (Redis)                   Cache, i18n, Utils
   i18n, Security, Logging         
   
⚙️ core/ + setup/               ⚪ shared/
   Feature Flags                   Types, Constants, Utils
   App Initialization              Shared across all layers
```

---

## 📊 Layer Responsibilities (1 Minute Version)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  🔴 PRESENTATION (UI Layer)                                     │
│  ├─ What user SEES (Components, Views, Forms)                  │
│  ├─ User interactions (clicks, inputs)                          │
│  ├─ UI state management (open/close modals, sorting)            │
│  └─ ❌ NEVER: Business logic, API calls, data persistence       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🟡 APPLICATION (Orchestration Layer)                           │
│  ├─ What HAPPENS (Services, Stores, Composables)               │
│  ├─ Workflow coordination (1. fetch, 2. validate, 3. save)     │
│  ├─ State management (reactive data)                            │
│  └─ Uses: Domain Logic + Infrastructure Services               │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🟢 DOMAIN (Business Logic Layer)                               │
│  ├─ What IS that? (Models, Value Objects, Rules)               │
│  ├─ Business rules (validation, calculations)                   │
│  ├─ Pure logic (no framework dependencies)                      │
│  └─ ❌ NEVER: Database access, HTTP requests, UI imports        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔵 INFRASTRUCTURE (Technical Services)                         │
│  ├─ HOW we communicate (API clients, WebSocket, Cache)          │
│  ├─ External services (Database, Redis, Auth)                   │
│  ├─ Technical details (Axios config, encryption)                │
│  └─ Returns: Raw data (JSON, no business logic)                 │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⚪ SHARED (Cross-Cutting Concerns)                             │
│  ├─ Code used by ALL layers (Types, Constants, Utils)           │
│  ├─ Single source of truth                                      │
│  └─ DRY principle (Don't Repeat Yourself)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

# 🔧 Backend Architecture

## Directory Structure

```
app/
├── api/                        🔴 HTTP LAYER
│   ├── __init__.py
│   ├── routes.py               # Route registration
│   ├── auth_bp.py              # Auth routes
│   ├── content_bp.py           # Content routes (courses, lessons)
│   ├── learning_bp.py          # Learning routes (progress, quizzes)
│   ├── social_bp.py            # Social routes (posts, feeds, likes)
│   ├── user_bp.py              # User routes (profile, settings)
│   ├── admin_bp.py             # Admin routes (users, moderation)
│   ├── compliance_bp.py        # Compliance routes (reports, exports)
│   ├── moderation_bp.py        # Moderation routes (content review)
│   ├── security_bp.py          # Security routes (2FA, API keys)
│   └── course_editor_bp.py     # Course Editor routes (manual + AI)
│
├── application/                🟡 APPLICATION SERVICES
│   ├── __init__.py
│   ├── services/               # Business workflow services
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── AuthService.py  # Login, register, logout
│   │   │   └── JWTService.py   # Token generation & validation
│   │   │
│   │   ├── content/
│   │   │   ├── __init__.py
│   │   │   ├── CourseService.py        # Course CRUD, publishing
│   │   │   ├── LessonService.py        # Lesson CRUD
│   │   │   ├── ContentService.py       # Content blocks
│   │   │   └── CourseEnrollmentService.py # Enrollment logic
│   │   │
│   │   ├── learning/
│   │   │   ├── __init__.py
│   │   │   ├── ProgressService.py      # Track user progress
│   │   │   ├── QuizService.py          # Quiz logic
│   │   │   └── CertificateService.py   # Certificate generation
│   │   │
│   │   ├── social/
│   │   │   ├── __init__.py
│   │   │   ├── PostService.py          # Create, like, delete posts
│   │   │   ├── FeedService.py          # Generate personalized feeds
│   │   │   └── FollowService.py        # Follow/unfollow logic
│   │   │
│   │   ├── user/
│   │   │   ├── __init__.py
│   │   │   ├── UserProfileService.py   # Profile management
│   │   │   └── NotificationService.py  # Send notifications
│   │   │
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── UserManagementService.py
│   │   │   └── SystemHealthService.py
│   │   │
│   │   ├── course_editor/
│   │   │   ├── __init__.py
│   │   │   ├── ManualEditorService.py  # Manual editing
│   │   │   └── AIEditorService.py      # AI-powered editing
│   │   │
│   │   └── shared/
│   │       ├── __init__.py
│   │       ├── TransactionService.py   # Handle transactions
│   │       └── ValidationService.py    # Input validation
│   │
│   └── dto/                    # Data Transfer Objects (API Input/Output)
│       ├── __init__.py
│       ├── CourseDTO.py
│       ├── UserDTO.py
│       └── ...
│
├── domain/                     🟢 BUSINESS LOGIC
│   ├── __init__.py
│   │
│   ├── models/                 # Domain Models (Entities)
│   │   ├── __init__.py
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── AIModel.py      # AI model entity
│   │   │   ├── AIPrompt.py     # Prompt template
│   │   │   └── AIResponse.py   # Response structure
│   │   │
│   │   ├── content/
│   │   │   ├── __init__.py
│   │   │   ├── Course.py       # Course entity
│   │   │   ├── Lesson.py       # Lesson entity
│   │   │   ├── ContentBlock.py # Content block entity
│   │   │   └── CourseStatus.py # Status enum
│   │   │
│   │   ├── learning/
│   │   │   ├── __init__.py
│   │   │   ├── Progress.py
│   │   │   ├── Quiz.py
│   │   │   └── Certificate.py
│   │   │
│   │   ├── social/
│   │   │   ├── __init__.py
│   │   │   ├── Post.py
│   │   │   ├── Comment.py
│   │   │   └── Like.py
│   │   │
│   │   ├── user/
│   │   │   ├── __init__.py
│   │   │   ├── User.py         # User entity
│   │   │   ├── UserRole.py     # Role enum
│   │   │   └── UserPermission.py
│   │   │
│   │   └── security/
│   │       ├── __init__.py
│   │       ├── ApiKey.py
│   │       └── SecurityLog.py
│   │
│   ├── value-objects/          # Value Objects (Immutable)
│   │   ├── __init__.py
│   │   ├── UserId.py           # User ID value object
│   │   ├── CourseId.py         # Course ID value object
│   │   ├── Email.py            # Email validation
│   │   ├── Password.py         # Password validation
│   │   └── PhoneNumber.py      # Phone validation
│   │
│   ├── factories/              # Factories (Object Creation)
│   │   ├── __init__.py
│   │   ├── UserFactory.py      # Create users
│   │   ├── CourseFactory.py    # Create courses
│   │   └── PostFactory.py      # Create posts
│   │
│   ├── repositories/           # Repository Interfaces
│   │   ├── __init__.py
│   │   ├── IUserRepository.py
│   │   ├── ICourseRepository.py
│   │   ├── IPostRepository.py
│   │   └── IProgressRepository.py
│   │
│   ├── events/                 # Domain Events
│   │   ├── __init__.py
│   │   ├── UserRegisteredEvent.py
│   │   ├── CoursePublishedEvent.py
│   │   └── PostCreatedEvent.py
│   │
│   └── exceptions/             # Custom Domain Exceptions
│       ├── __init__.py
│       ├── CourseNotFoundException.py
│       ├── UnauthorizedAccessException.py
│       └── InvalidCourseStatusException.py
│
├── infrastructure/             🔵 TECHNICAL SERVICES
│   ├── __init__.py
│   │
│   ├── persistence/            # Database Layer
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy config
│   │   ├── models/             # SQLAlchemy Models (ORM)
│   │   │   ├── UserModel.py
│   │   │   ├── CourseModel.py
│   │   │   ├── PostModel.py
│   │   │   └── ...
│   │   │
│   │   └── repositories/       # Repository Implementations
│   │       ├── __init__.py
│   │       ├── UserRepository.py
│   │       ├── CourseRepository.py
│   │       ├── PostRepository.py
│   │       └── ...
│   │
│   ├── cache/                  # Redis Cache
│   │   ├── __init__.py
│   │   ├── redis_client.py     # Redis connection
│   │   └── cache_manager.py    # Caching logic
│   │
│   ├── external/               # External APIs
│   │   ├── __init__.py
│   │   ├── openai_client.py    # OpenAI API integration
│   │   ├── email_client.py     # Email sending (SMTP)
│   │   └── payment_client.py   # Payment provider (Stripe)
│   │
│   ├── i18n/                   # Internationalization
│   │   ├── __init__.py
│   │   ├── translator.py       # Translation service
│   │   └── locales/
│   │       ├── de.json
│   │       └── en.json
│   │
│   ├── security/               # Security Services
│   │   ├── __init__.py
│   │   ├── encryption.py       # Encrypt/decrypt sensitive data
│   │   ├── password_hasher.py  # Password hashing (bcrypt)
│   │   ├── 2fa_service.py      # 2-factor authentication
│   │   └── audit_logger.py     # Security audit logging
│   │
│   ├── websocket/              # WebSocket Support
│   │   ├── __init__.py
│   │   ├── socket_manager.py   # Socket.IO handling
│   │   └── events.py           # WebSocket event handlers
│   │
│   └── logging/                # Logging Configuration
│       ├── __init__.py
│       ├── logger.py           # Logger setup
│       └── formatters.py       # Log formatters
│
├── core/                       ⚙️ CORE SERVICES
│   ├── __init__.py
│   ├── config.py               # Environment configuration
│   ├── feature_flags.py        # Feature toggle system
│   ├── constants.py            # Global constants
│   └── exceptions.py           # Global exceptions
│
├── setup/                      🔧 INITIALIZATION
│   ├── __init__.py
│   ├── app_factory.py          # Flask app creation
│   ├── db_init.py              # Database initialization
│   └── seed.py                 # Initial data seeding
│
├── shared/                     ⚪ UTILITIES
│   ├── __init__.py
│   ├── utils.py                # Utility functions
│   ├── validators.py           # Input validators
│   ├── decorators.py           # Custom decorators
│   └── types.py                # Shared types
│
└── tests/                      ✅ TEST SUITE
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## Backend Example: Course Creation Flow

```python
# 1️⃣ API LAYER - HTTP Request comes in
# api/content_bp.py

@content_bp.route('/courses', methods=['POST'])
@require_auth
def create_course():
    data = request.get_json()
    
    # ✅ Calls Application Service
    course = course_service.create_course(data)
    
    return jsonify(course.to_dict()), 201
```

```python
# 2️⃣ APPLICATION LAYER - Orchestration
# application/services/content/CourseService.py

class CourseService:
    def __init__(self):
        self.course_repo = CourseRepository()
        self.factory = CourseFactory()
    
    def create_course(self, data):
        # ✅ Calls Domain Factory
        course = self.factory.create_from_input(data)
        
        # ✅ Calls Domain logic (validation)
        if not course.is_valid():
            raise InvalidCourseException()
        
        # ✅ Calls Infrastructure (save to DB)
        saved_course = self.course_repo.save(course)
        
        # ✅ Calls Domain Event
        DomainEventPublisher.publish(CourseCreatedEvent(saved_course))
        
        return saved_course
```

```python
# 3️⃣ DOMAIN LAYER - Business Logic
# domain/models/content/Course.py

class Course:
    def __init__(self, title, description, instructor_id):
        if not title or len(title) < 3:
            raise InvalidCourseException("Title must be >= 3 chars")
        
        self.title = title
        self.description = description
        self.instructor_id = instructor_id
        self.status = CourseStatus.DRAFT
        self.created_at = datetime.now()
    
    def is_valid(self):
        """Business rule validation"""
        return (
            self.title and 
            self.description and 
            self.instructor_id is not None
        )
    
    def publish(self):
        """Business logic: can only publish if complete"""
        if not self.is_complete():
            raise InvalidStateException("Course must be complete")
        self.status = CourseStatus.PUBLISHED
```

```python
# 🎏 DOMAIN LAYER - Factory
# domain/factories/CourseFactory.py

class CourseFactory:
    @staticmethod
    def create_from_input(data):
        """Create from API input"""
        return Course(
            title=data['title'],
            description=data['description'],
            instructor_id=data['instructor_id']
        )
    
    @staticmethod
    def create_from_db_row(row):
        """Create from database row"""
        course = Course(
            title=row.title,
            description=row.description,
            instructor_id=row.instructor_id
        )
        course.id = row.id
        return course
```

```python
# 4️⃣ INFRASTRUCTURE LAYER - Data Access
# infrastructure/persistence/repositories/CourseRepository.py

class CourseRepository:
    def save(self, course: Course) -> Course:
        """Save course to database"""
        db_model = CourseModel(
            title=course.title,
            description=course.description,
            instructor_id=course.instructor_id,
            status=course.status.value
        )
        db.session.add(db_model)
        db.session.commit()
        
        course.id = db_model.id
        return course
    
    def find_by_id(self, course_id) -> Course:
        """Fetch from database"""
        db_model = CourseModel.query.get(course_id)
        if not db_model:
            raise CourseNotFoundException()
        
        return CourseFactory.create_from_db_row(db_model)
```

---

# 🎨 Frontend Architecture

## Directory Structure

```
/src
├── /presentation                       🔴 UI LAYER
│   ├── /components
│   │   ├── /shared                     # Reusable UI components
│   │   │   ├── /ui                     # Button, Input, Modal
│   │   │   │   ├── Button.vue
│   │   │   │   ├── Input.vue
│   │   │   │   ├── Modal.vue
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── /layout                 # Layout components
│   │   │   │   ├── Header.vue
│   │   │   │   ├── Sidebar.vue
│   │   │   │   ├── Footer.vue
│   │   │   │   └── MainLayout.vue
│   │   │   │
│   │   │   └── /forms                  # Form components
│   │   │       ├── FormInput.vue
│   │   │       ├── FormSelect.vue
│   │   │       └── FormSubmit.vue
│   │   │
│   │   ├── /content                    # Content domain components
│   │   │   ├── CourseCard.vue
│   │   │   ├── CourseList.vue
│   │   │   ├── LessonView.vue
│   │   │   ├── ContentBlock.vue
│   │   │   └── CourseEnrollButton.vue
│   │   │
│   │   ├── /learning                   # Learning domain components
│   │   │   ├── ProgressBar.vue
│   │   │   ├── QuizView.vue
│   │   │   ├── CertificateView.vue
│   │   │   └── StudentDashboard.vue
│   │   │
│   │   ├── /social                     # Social domain components
│   │   │   ├── PostCard.vue
│   │   │   ├── PostComposer.vue
│   │   │   ├── FeedView.vue
│   │   │   ├── UserProfile.vue
│   │   │   └── FollowButton.vue
│   │   │
│   │   ├── /user                       # User domain components
│   │   │   ├── LoginForm.vue
│   │   │   ├── RegisterForm.vue
│   │   │   ├── UserSettings.vue
│   │   │   └── NotificationCenter.vue
│   │   │
│   │   ├── /admin                      # Admin domain components
│   │   │   ├── UserManagement.vue
│   │   │   ├── CourseApproval.vue
│   │   │   └── SystemStats.vue
│   │   │
│   │   ├── /moderation                 # Moderation domain components
│   │   │   ├── ContentReview.vue
│   │   │   ├── ReportList.vue
│   │   │   └── ActionTaker.vue
│   │   │
│   │   └── /course-editor              # Course editor domain
│   │       ├── /manual-editor
│   │       │   ├── ManualEditorView.vue
│   │       │   ├── CourseStructure.vue
│   │       │   ├── LessonEditor.vue
│   │       │   ├── ContentBlockEditor.vue
│   │       │   └── MediaUploader.vue
│   │       │
│   │       └── /ai-editor
│   │           ├── AIEditorView.vue
│   │           ├── PromptComposer.vue
│   │           ├── AIPreview.vue
│   │           ├── AIChat.vue
│   │           └── GenerationStatus.vue
│   │
│   ├── /views                          # Page-level views (routes)
│   │   ├── /auth
│   │   │   ├── LoginView.vue
│   │   │   ├── RegisterView.vue
│   │   │   └── ResetPasswordView.vue
│   │   │
│   │   ├── /content
│   │   │   ├── CoursesView.vue         # List courses
│   │   │   ├── CourseDetailView.vue    # Single course
│   │   │   ├── LessonView.vue          # Single lesson
│   │   │   └── CourseEnrollView.vue    # Enrollment flow
│   │   │
│   │   ├── /learning
│   │   │   ├── DashboardView.vue       # Student dashboard
│   │   │   ├── ProgressView.vue        # Progress tracking
│   │   │   └── CertificatesView.vue    # My certificates
│   │   │
│   │   ├── /social
│   │   │   ├── FeedView.vue            # Social feed
│   │   │   ├── ProfileView.vue         # User profile
│   │   │   └── FollowingView.vue       # My following
│   │   │
│   │   ├── /course-editor
│   │   │   ├── CourseEditorView.vue    # Editor wrapper
│   │   │   ├── ManualEditorView.vue    # Manual editing
│   │   │   └── AIEditorView.vue        # AI editing
│   │   │
│   │   ├── /admin
│   │   │   ├── AdminDashboard.vue
│   │   │   ├── UserManagementView.vue
│   │   │   └── ModerationView.vue
│   │   │
│   │   └── 404.vue, 500.vue            # Error pages
│   │
│   └── /layouts                        # Layout wrappers
│       ├── DefaultLayout.vue           # Standard layout (header + sidebar + content)
│       ├── AdminLayout.vue             # Admin layout
│       ├── AuthLayout.vue              # Auth page layout (centered)
│       └── EditorLayout.vue            # Editor layout (full width)
│
├── /application                        🟡 APPLICATION SERVICES
│   ├── /services                       # Business services
│   │   ├── /content
│   │   │   ├── CourseService.ts
│   │   │   ├── LessonService.ts
│   │   │   └── EnrollmentService.ts
│   │   │
│   │   ├── /learning
│   │   │   ├── ProgressService.ts
│   │   │   ├── QuizService.ts
│   │   │   └── CertificateService.ts
│   │   │
│   │   ├── /social
│   │   │   ├── PostService.ts
│   │   │   ├── FeedService.ts
│   │   │   └── FollowService.ts
│   │   │
│   │   ├── /user
│   │   │   ├── AuthService.ts
│   │   │   ├── ProfileService.ts
│   │   │   └── NotificationService.ts
│   │   │
│   │   └── /course-editor
│   │       ├── ManualEditorService.ts
│   │       ├── AIEditorService.ts
│   │       └── EditorValidationService.ts
│   │
│   ├── /stores                         # Pinia stores (state management)
│   │   ├── index.ts                    # Store registration
│   │   │
│   │   ├── /modules
│   │   │   ├── /auth
│   │   │   │   └── auth.store.ts       # Auth state (user, token)
│   │   │   │
│   │   │   ├── /content
│   │   │   │   ├── course.store.ts     # Courses state
│   │   │   │   ├── lesson.store.ts     # Lessons state
│   │   │   │   └── enrollment.store.ts # Enrollments state
│   │   │   │
│   │   │   ├── /learning
│   │   │   │   ├── progress.store.ts
│   │   │   │   └── quiz.store.ts
│   │   │   │
│   │   │   ├── /social
│   │   │   │   ├── post.store.ts
│   │   │   │   ├── feed.store.ts
│   │   │   │   └── follow.store.ts
│   │   │   │
│   │   │   ├── /user
│   │   │   │   ├── user.store.ts
│   │   │   │   └── notification.store.ts
│   │   │   │
│   │   │   └── /course-editor
│   │   │       └── editor.store.ts
│   │   │
│   │   └── /ui                         # UI state stores
│   │       ├── ui.store.ts             # Theme, language, sidebar state
│   │       └── loading.store.ts        # Global loading state
│   │
│   ├── /composables                    # Reusable composition functions
│   │   ├── useAuth.ts                  # Auth composable
│   │   ├── useFetch.ts                 # Fetch wrapper with error handling
│   │   ├── usePagination.ts            # Pagination logic
│   │   ├── useForm.ts                  # Form validation & submission
│   │   ├── useLocalStorage.ts          # LocalStorage persistence
│   │   └── useWebSocket.ts             # WebSocket connection
│   │
│   └── /use-cases                      # Complex business workflows
│       ├── /course-editor
│       │   ├── useManualCourseCreation.ts
│       │   └── useAICourseGeneration.ts
│       │
│       └── /social
│           └── useCreateAndSharePost.ts
│
├── /domain                             🟢 BUSINESS LOGIC
│   ├── /models                         # Domain entities
│   │   ├── /content
│   │   │   ├── Course.model.ts
│   │   │   ├── Lesson.model.ts
│   │   │   └── ContentBlock.model.ts
│   │   │
│   │   ├── /social
│   │   │   ├── Post.model.ts
│   │   │   ├── Comment.model.ts
│   │   │   └── Like.model.ts
│   │   │
│   │   ├── /user
│   │   │   ├── User.model.ts
│   │   │   └── UserProfile.model.ts
│   │   │
│   │   └── /learning
│   │       ├── Progress.model.ts
│   │       └── Certificate.model.ts
│   │
│   ├── /value-objects                 # Immutable value objects
│   │   ├── CourseId.vo.ts
│   │   ├── UserId.vo.ts
│   │   ├── Email.vo.ts
│   │   ├── Password.vo.ts
│   │   └── Rating.vo.ts
│   │
│   ├── /factories                      # Factory functions
│   │   ├── Course.factory.ts
│   │   ├── Post.factory.ts
│   │   ├── User.factory.ts
│   │   └── Progress.factory.ts
│   │
│   ├── /events                         # Domain events
│   │   ├── PostCreatedEvent.ts
│   │   ├── CoursePublishedEvent.ts
│   │   └── UserFollowedEvent.ts
│   │
│   └── /repositories                   # Repository interfaces (optional)
│       ├── IPostRepository.ts
│       ├── ICourseRepository.ts
│       └── IUserRepository.ts
│
├── /infrastructure                     🔵 TECHNICAL SERVICES
│   ├── /api                            # HTTP API clients
│   │   ├── http.ts                     # Axios instance
│   │   └── /clients
│   │       ├── auth.client.ts
│   │       ├── content.client.ts
│   │       ├── learning.client.ts
│   │       ├── social.client.ts
│   │       ├── user.client.ts
│   │       └── course-editor.client.ts
│   │
│   ├── /websocket                      # WebSocket clients
│   │   ├── socket.ts                   # Socket.IO instance
│   │   ├── handlers/
│   │   │   ├── postEventHandlers.ts
│   │   │   ├── courseEventHandlers.ts
│   │   │   └── notificationHandlers.ts
│   │   └── emitters/
│   │       └── eventEmitters.ts
│   │
│   ├── /cache                          # Client-side caching
│   │   ├── storage.ts                  # LocalStorage wrapper
│   │   └── cache-manager.ts            # Cache management
│   │
│   ├── /i18n                           # Internationalization
│   │   ├── i18n.ts                     # Vue i18n setup
│   │   └── locales/
│   │       ├── de.json
│   │       └── en.json
│   │
│   └── /security                       # Security utilities
│       ├── crypto.ts                   # Encryption/decryption
│       └── validators.ts               # Input validation
│
├── /shared                             ⚪ CROSS-CUTTING CONCERNS
│   ├── /types                          # Shared TypeScript types
│   │   ├── api.types.ts                # API response types
│   │   ├── common.types.ts             # Common types (ID, Timestamps)
│   │   ├── domain.types.ts             # Domain types
│   │   └── dto.types.ts                # Data transfer objects
│   │
│   ├── /constants                      # Shared constants
│   │   ├── api.constants.ts            # API endpoints
│   │   ├── errors.constants.ts         # Error codes
│   │   ├── events.constants.ts         # WebSocket events
│   │   └── validation.constants.ts     # Validation rules
│   │
│   ├── /utils                          # Utility functions
│   │   ├── date.utils.ts               # Date formatting
│   │   ├── format.utils.ts             # Number, currency, text formatting
│   │   ├── validation.utils.ts         # Email, URL, phone validation
│   │   └── string.utils.ts             # String manipulation
│   │
│   ├── /guards                         # TypeScript guards
│   │   ├── type.guards.ts              # isDefined, isString, isArray
│   │   ├── user.guards.ts              # isAdmin, hasPermission
│   │   └── domain.guards.ts            # Domain-specific guards
│   │
│   └── /decorators                     # Decorator functions
│       ├── cache.decorator.ts
│       └── timing.decorator.ts
│
├── /assets                             # Static assets
│   ├── /images
│   ├── /icons
│   ├── /styles
│   │   ├── global.css
│   │   ├── variables.css
│   │   └── utilities.css
│   └── /fonts
│
├── /plugins                            # Vue plugins
│   ├── index.ts
│   ├── vuetify.ts (if using Vuetify)
│   └── custom-plugins.ts
│
├── router.ts                           # Vue Router setup
├── main.ts                             # Vue app entry point
├── vite-env.d.ts                       # Vite env types
├── env.d.ts                            # Custom types
│
├── package.json
├── vite.config.ts
├── tsconfig.json
└── .env.example
```

---

## Frontend Example: Course Creation Flow

```vue
<!-- 1️⃣ PRESENTATION - CourseCard.vue -->
<template>
  <div class="course-card">
    <img :src="course.thumbnail" />
    <h3>{{ course.title }}</h3>
    
    <button @click="handleEnroll" :disabled="isEnrolling">
      {{ isEnrolling ? 'Enrolling...' : 'Enroll Now' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useCourseStore } from '@/application/stores/modules/content/course.store'

const props = defineProps<{
  course: { id: string; title: string; thumbnail: string }
}>()

const courseStore = useCourseStore()
const isEnrolling = ref(false)

async function handleEnroll() {
  isEnrolling.value = true
  try {
    // ✅ Calls application store
    await courseStore.enrollInCourse(props.course.id)
  } finally {
    isEnrolling.value = false
  }
}
</script>
```

```typescript
// 2️⃣ APPLICATION - course.store.ts
import { defineStore } from 'pinia'
import { CourseService } from '@/application/services/content/CourseService'
import type { Course } from '@/domain/models/content/Course.model'

export const useCourseStore = defineStore('course', {
  state: () => ({
    courses: [] as Course[],
    currentCourse: null as Course | null,
    loading: false,
    error: null as string | null
  }),

  actions: {
    async enrollInCourse(courseId: string) {
      this.loading = true
      this.error = null
      
      try {
        // ✅ Calls application service
        const service = new CourseService()
        const course = await service.enrollCourse(courseId)
        
        // ✅ Updates state
        this.currentCourse = course
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})
```

```typescript
// 🟡 APPLICATION - CourseService.ts
import { enrollmentClient } from '@/infrastructure/api/clients/enrollment.client'
import { CourseFactory } from '@/domain/factories/content/Course.factory'

export class CourseService {
  async enrollCourse(courseId: string): Promise<Course> {
    // ✅ Calls infrastructure API client
    const response = await enrollmentClient.enroll(courseId)
    
    // ✅ Calls domain factory
    const course = CourseFactory.fromApiResponse(response.data)
    
    // ✅ Validation (domain logic)
    if (!course.canBeEnrolled()) {
      throw new Error('Cannot enroll in this course')
    }
    
    return course
  }
}
```

```typescript
// 🟢 DOMAIN - Course.model.ts
export class Course {
  constructor(
    public readonly id: string,
    public readonly title: string,
    public readonly thumbnail: string,
    public readonly isPublished: boolean,
    public readonly enrolledCount: number
  ) {}
  
  canBeEnrolled(): boolean {
    return this.isPublished && this.enrolledCount < 1000
  }
}
```

```typescript
// 🟡 DOMAIN - Course.factory.ts
export class CourseFactory {
  static fromApiResponse(data: any): Course {
    return new Course(
      data.id,
      data.title,
      data.thumbnail,
      data.is_published,
      data.enrolled_count
    )
  }
}
```

```typescript
// 🔵 INFRASTRUCTURE - enrollment.client.ts
import { http } from '@/infrastructure/api/http'
import { API_ENDPOINTS } from '@/shared/constants/api.constants'

class EnrollmentClient {
  async enroll(courseId: string) {
    // ✅ Makes HTTP request
    return http.post(`${API_ENDPOINTS.COURSES.ENROLL}/${courseId}`)
  }
}

export const enrollmentClient = new EnrollmentClient()
```

---

# 🔄 Backend ↔ Frontend Flow

## Complete User Journey: "Create & Publish Course"

### Phase 1: Course Creation (Manual or AI)

```
FRONTEND:
─────────────────────────────────

1. 🔴 User opens CourseEditorView.vue
   ↓ clicks "Create Course"
   ↓
2. 🟡 useCourseStore().createCourse()
   ↓ calls CourseService.createCourse()
   ↓
3. 🟡 CourseService calls infrastructure
   ↓
4. 🔵 courseEditorClient.POST /api/v1/courses
   ↓
   
BACKEND:
─────────────────────────────────

5. 🔴 api/course_editor_bp.py
   ↓ receives HTTP POST /api/v1/courses
   ↓
6. 🟡 application/services/CourseEditorService.create_course()
   ↓ orchestrates creation
   ↓
7. 🟢 domain/factories/CourseFactory.create_from_input()
   ↓ validates & creates Course model
   ↓
8. 🔵 infrastructure/persistence/CourseRepository.save()
   ↓ saves to PostgreSQL database
   ↓
9. 🟢 domain/events/CourseCreatedEvent published
   ↓ (triggers notifications, webhooks, etc.)
   ↓
10. 🔴 Returns: { id: 123, title: "...", status: "DRAFT" }

FRONTEND:
─────────────────────────────────

11. 🔵 courseEditorClient receives response
    ↓
12. 🟡 CourseService calls CourseFactory.fromApiResponse()
    ↓
13. 🟢 Course model created (validation occurs)
    ↓
14. 🟡 Store updated: currentCourse = course
    ↓
15. 🔴 CourseEditorView shows "Course created! ID: 123"
```

### Phase 2: AI Content Generation

```
FRONTEND:
─────────────────────────────────

1. 🔴 User writes prompt in AIEditorView.vue
   ↓ clicks "Generate Content"
   ↓
2. 🟡 useCourseStore().generateWithAI(prompt)
   ↓
3. 🟡 AIEditorService.generateContent(prompt)
   ↓
4. 🔵 courseEditorClient.POST /api/v1/courses/123/ai-generate
   ↓ sends prompt + course ID
   ↓

BACKEND:
─────────────────────────────────

5. 🔴 api/course_editor_bp.py
   ↓ receives POST /api/v1/courses/123/ai-generate
   ↓
6. 🟡 application/services/AIEditorService.generate()
   ↓
7. 🔵 infrastructure/external/openai_client.py
   ↓ calls OpenAI API (streaming or batched)
   ↓
   → "Generate lesson about Python Basics..."
   ← "## Python Basics\n\n### What is Python?..."
   ↓
8. 🟡 AIEditorService processes response
   ↓
9. 🟢 ContentBlockFactory.create_from_ai_response()
   ↓ creates ContentBlock models with validation
   ↓
10. 🔵 CourseRepository.update() saves blocks
    ↓
11. 🟢 AIContentGeneratedEvent published
    ↓
12. 🔴 Returns: { status: "SUCCESS", blocks: [...] }

FRONTEND:
─────────────────────────────────

13. 🔵 courseEditorClient receives response
    ↓
14. 🟡 ContentBlockFactory creates models from response
    ↓
15. 🟡 Store updated: currentCourse.contentBlocks = blocks
    ↓
16. 🔴 AIEditorView shows generated content
    ↓ User can edit/refine
```

### Phase 3: Publishing

```
Flow: Same as Phase 1, but calls:
  Backend: ApplicationService.publish_course(course_id)
  Domain: Course.publish() (validates state)
  Event: CoursePublishedEvent (emails students, updates social feed)
```

---

# 🎯 Real Examples

## Example 1: User Registration Flow

### Backend Flow

```python
# 1. API receives POST /auth/register
# api/auth_bp.py
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = auth_service.register(data)
    return jsonify(user.to_dict()), 201

# 2. Application Service orchestrates
# application/services/AuthService.py
def register(self, data):
    # Validate input
    if not self.validation_service.is_valid_email(data['email']):
        raise ValidationException("Invalid email")
    
    # Create domain model
    user = UserFactory.create_from_input(data)
    
    # Check business rules
    if self.user_repo.exists_by_email(user.email):
        raise DuplicateUserException()
    
    # Save to database
    saved_user = self.user_repo.save(user)
    
    # Publish event
    DomainEventPublisher.publish(
        UserRegisteredEvent(saved_user)
    )
    
    return saved_user

# 3. Domain Model validates
# domain/models/User.py
class User:
    def __init__(self, email, password, name):
        if not email or '@' not in email:
            raise InvalidEmailException()
        
        self.email = email
        self.password_hash = bcrypt.hash(password)
        self.name = name
        self.role = UserRole.STUDENT

# 4. Repository saves to database
# infrastructure/persistence/UserRepository.py
def save(self, user: User) -> User:
    db_user = UserModel(
        email=user.email,
        password_hash=user.password_hash,
        name=user.name,
        role=user.role.value
    )
    db.session.add(db_user)
    db.session.commit()
    return user
```

### Frontend Flow

```typescript
// 1. Component handles user input
// presentation/views/auth/RegisterView.vue
const form = reactive({
  email: '',
  password: '',
  name: ''
})

async function handleSubmit() {
  try {
    // 2. Application service orchestrates
    const user = await authService.register(form)
    
    // 3. Store updated
    authStore.setUser(user)
    
    // 4. Navigation
    router.push('/dashboard')
  } catch (err) {
    error.value = err.message
  }
}

// 2. Application Service calls API
// application/services/AuthService.ts
async register(data: RegisterDTO): Promise<User> {
  // Infrastructure: make API call
  const response = await authClient.register(data)
  
  // Domain: create model from response
  const user = UserFactory.fromApiResponse(response.data)
  
  // Application: store token
  this.tokenService.setToken(response.token)
  
  return user
}

// 3. Infrastructure: API Client
// infrastructure/api/clients/auth.client.ts
async register(data: RegisterDTO) {
  return http.post('/auth/register', data)
}
```

---

## Example 2: Create Social Post with AI Enhancement

### Backend

```python
# 1. API receives POST /social/posts
@social_bp.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    post = post_service.create_post(data)
    return jsonify(post.to_dict()), 201

# 2. Application Service
class PostService:
    def create_post(self, data):
        # Create post
        post = PostFactory.create_from_input(data)
        
        # If AI enhancement requested
        if data.get('enhance_with_ai'):
            enhanced_content = self.ai_client.enhance_text(post.content)
            post.content = enhanced_content
        
        # Save
        saved_post = self.post_repo.save(post)
        
        # Publish event
        DomainEventPublisher.publish(PostCreatedEvent(saved_post))
        
        return saved_post

# 3. Domain Model
class Post:
    def __init__(self, content, author_id, created_at=None):
        if not content or len(content) < 1:
            raise InvalidPostException()
        
        self.content = content
        self.author_id = author_id
        self.likes_count = 0
        self.created_at = created_at or datetime.now()

# 4. Repository
def save(self, post: Post):
    db_post = PostModel(
        content=post.content,
        author_id=post.author_id
    )
    db.session.add(db_post)
    db.session.commit()
    return post
```

### Frontend

```typescript
// 1. Component
// presentation/components/social/PostComposer.vue
const form = reactive({
  content: '',
  enhanceWithAI: false
})

async function submitPost() {
  try {
    await postStore.createPost(form)
    form.content = ''
    // Post appears in feed
  } catch (err) {
    // Show error
  }
}

// 2. Application Store + Service
class PostService {
  async createPost(data: CreatePostDTO): Promise<Post> {
    // Infrastructure: API call
    const response = await socialClient.createPost(data)
    
    // Domain: create model
    const post = PostFactory.fromApiResponse(response.data)
    
    return post
  }
}

// 3. Infrastructure: API Client
async createPost(data: CreatePostDTO) {
  return http.post('/social/posts', data)
}
```

---

# 🎲 Decision Trees

## When you're unsure where code belongs...

### "Where does this validation go?"

```
Is it about USER INPUT FORMAT?
├─ Email format, phone number format?
├─ Yes → shared/utils/validation.utils.ts ✅
└─ No → Continue

Is it about BUSINESS RULES?
├─ "User can only enroll if course is published"?
├─ "Post must have at least 1 character"?
├─ Yes → domain/models/YourModel.ts ✅
└─ No → Continue

Is it about FORM SUBMISSION?
├─ Email & password are present?
├─ Yes → presentation/components/YourForm.vue ✅
└─ Invalid
```

### "Where does this API call go?"

```
Is it EXTERNAL communication?
├─ HTTP request, WebSocket, Database?
├─ Yes → infrastructure/api/clients/ ✅
└─ No → Invalid

Does it transform response?
├─ Maps API JSON to domain model?
├─ Yes → application/services/ ✅
└─ No → Just return raw response from infrastructure

Does it affect STATE?
├─ Updates Pinia store?
├─ Yes → application/stores/ ✅
└─ No → Just use service directly
```

### "Where does this component go?"

```
Is it REUSABLE across domains?
├─ Button, Input, Modal, Layout?
├─ Yes → presentation/components/shared/ ✅
└─ No → Continue

Is it domain-SPECIFIC?
├─ CourseCard (content domain)?
├─ PostComposer (social domain)?
├─ Yes → presentation/components/[domain-name]/ ✅
└─ No → Continue

Is it a full PAGE / ROUTE?
├─ CoursesView.vue (shows list of courses)?
├─ Yes → presentation/views/[domain-name]/ ✅
└─ Invalid
```

---

# ⚙️ Common Patterns

## Pattern 1: Service → Store → Component

**The standard flow for any data operation:**

```typescript
// Service (Business Logic)
export class CourseService {
  async getCourses(): Promise<Course[]> {
    const response = await courseClient.list()
    return response.data.map(dto => CourseFactory.fromAPI(dto))
  }
}

// Store (State Management)
export const useCourseStore = defineStore('course', {
  state: () => ({ courses: [] as Course[] }),
  
  actions: {
    async loadCourses() {
      const service = new CourseService()
      this.courses = await service.getCourses()
    }
  }
})

// Component (UI)
<script setup>
const store = useCourseStore()

onMounted(() => {
  store.loadCourses()
})
</script>

<template>
  <div v-for="course in store.courses">
    {{ course.title }}
  </div>
</template>
```

## Pattern 2: Factory → Model → Repository

**The standard flow for creating domain objects:**

```typescript
// Factory (Creates Objects)
export class CourseFactory {
  static fromApiResponse(data: any): Course {
    return new Course(
      data.id,
      data.title,
      data.description
    )
  }
}

// Model (Defines Object)
export class Course {
  constructor(
    public id: string,
    public title: string,
    public description: string
  ) {}
}

// Repository (Persists Object)
export class CourseRepository {
  save(course: Course): Promise<void> {
    return courseClient.save(course)
  }
}
```

## Pattern 3: Use-Case Composable

**For complex workflows:**

```typescript
// application/use-cases/useCourseEnrollment.ts
export function useCourseEnrollment() {
  const courseStore = useCourseStore()
  const userStore = useUserStore()
  const notifications = useNotifications()
  
  return {
    async enrollCourse(courseId: string) {
      try {
        // 1. Check if already enrolled
        if (userStore.isEnrolledIn(courseId)) {
          throw new Error('Already enrolled')
        }
        
        // 2. Enroll
        await courseStore.enrollInCourse(courseId)
        
        // 3. Show success
        notifications.success('Enrolled successfully!')
        
      } catch (err) {
        notifications.error(err.message)
        throw err
      }
    }
  }
}

// In component:
<script setup>
const { enrollCourse } = useCourseEnrollment()

async function handleEnroll() {
  await enrollCourse(courseId)
}
</script>
```

---

# 🔧 Troubleshooting

## Common Mistakes & Solutions

### ❌ Mistake 1: Business Logic in Component

```typescript
// ❌ WRONG
<script setup>
async function handleSubmit() {
  // Validation in component
  if (form.email.includes('@')) {
    // API call in component
    const res = await fetch('/api/users')
    // Parsing response in component
    const user = { email: res.email, id: res.id }
  }
}
</script>

// ✅ CORRECT
<script setup>
const service = new UserService()

async function handleSubmit() {
  const user = await service.createUser(form)
}
</script>

// Services handle validation, API, parsing
```

### ❌ Mistake 2: Duplicate Code Across Stores

```typescript
// ❌ WRONG - formatDate copied in each store
export const useCourseStore = defineStore('course', {
  actions: {
    someAction() {
      const formatted = new Date().toLocaleDateString('de-DE')
    }
  }
})

export const useSocialStore = defineStore('social', {
  actions: {
    anotherAction() {
      const formatted = new Date().toLocaleDateString('de-DE')
    }
  }
})

// ✅ CORRECT - use shared utility
import { formatDate } from '@/shared/utils/date.utils'

export const useCourseStore = defineStore('course', {
  actions: {
    someAction() {
      const formatted = formatDate(new Date())
    }
  }
})
```

### ❌ Mistake 3: Domain Model depends on Framework

```typescript
// ❌ WRONG - Domain imports Vue!
import { ref } from 'vue'

export class Course {
  title = ref('')  // Vue dependency!
}

// ✅ CORRECT - Pure TypeScript
export class Course {
  constructor(public title: string) {}
}

// Make it reactive in store
export const useCourseStore = defineStore('course', {
  state: () => ({
    course: new Course('Title')  // Wrapped by Pinia
  })
})
```

### ❌ Mistake 4: API Client doing Business Logic

```typescript
// ❌ WRONG - API client has logic
async getCourse(id: string) {
  const response = await http.get(`/courses/${id}`)
  
  // Business logic in infrastructure!
  if (!response.data.isPublished) {
    throw new Error('Not published')
  }
  
  return response.data
}

// ✅ CORRECT - API client just fetches
async getCourse(id: string) {
  return http.get(`/courses/${id}`)
}

// Service handles business logic
async getCourse(id: string) {
  const response = await client.getCourse(id)
  const course = CourseFactory.fromAPI(response.data)
  
  if (!course.isPublished) {
    throw new Error('Not published')
  }
  
  return course
}
```

---

## Debugging Checklist

When something doesn't work:

```
□ Component not updating?
  → Check: Is store.action() being called?
  → Check: Is state actually being modified?
  → Check: Component watching the correct state?

□ API returns wrong data?
  → Check: Is client calling correct endpoint?
  → Check: Is Factory transforming data correctly?
  → Check: Are DTOs matching API response?

□ Business logic not working?
  → Check: Is Model validating correctly?
  → Check: Is Service calling Model methods?
  → Check: Are pre-conditions being checked?

□ Data not persisting?
  → Check: Is Repository.save() being called?
  → Check: Is Database transaction committed?
  → Check: Are required fields present?
```

---

# 📚 Quick Cheat Sheet

## Which Layer?

```
PRESENTATION:
✅ Vue components, templates, event handlers
✅ User interactions (click, input, submit)
❌ API calls, business logic, data manipulation

APPLICATION:
✅ Services (coordinate business workflows)
✅ Stores (Pinia state management)
✅ Use-cases (complex user journeys)
❌ Vue components, database queries

DOMAIN:
✅ Models (entities), factories, value objects
✅ Business rules, validation
✅ Pure TypeScript (no framework)
❌ API calls, UI, database operations

INFRASTRUCTURE:
✅ API clients (HTTP, WebSocket)
✅ Database access, caching
✅ External services
❌ Business logic, UI

SHARED:
✅ Types, constants, utilities
✅ Code used by multiple layers
❌ Layer-specific code
```

## Naming Conventions

```
Components:          ✅ UserProfile.vue, PostCard.vue
Stores:              ✅ user.store.ts, post.store.ts
Services:            ✅ UserService.ts, PostService.ts
Models:              ✅ User.model.ts, Post.model.ts
Factories:           ✅ User.factory.ts, Post.factory.ts
Clients:             ✅ user.client.ts, post.client.ts
Utils:               ✅ formatDate.ts, isValidEmail.ts
Types:               ✅ user.types.ts, post.types.ts
```

## Data Flow Direction (MUST BE DOWNWARD!)

```
❌ WRONG DIRECTIONS:
Infrastructure ← Domain (NO!)
Domain ← Presentation (NO!)
Presentation → Domain (NO!)

✅ CORRECT DIRECTIONS:
Presentation → Application (store/service)
Application → Domain (models, factories)
Application → Infrastructure (API client)
Infrastructure → (returns data)
Domain → shared (types, utils)
All → Shared (single source of truth)
```

---

# 📖 Weitere Ressourcen

- **Feature-Sliced Design**: https://feature-sliced.design
- **Clean Architecture**: Uncle Bob's blog
- **Domain-Driven Design**: Eric Evans book
- **Vue.js Best Practices**: https://vuejs.org/guide/best-practices

---

**Dieses Dokument regelmäßig updaten!** 
Last Updated: 20.01.2026
Version: 1.0

---

## Quick Links für schnelle Referenzen:

1. **Backend Flow** → Siehe: [Backend Example: Course Creation](#backend-example-course-creation-flow)
2. **Frontend Flow** → Siehe: [Frontend Example: Course Creation Flow](#frontend-example-course-creation-flow)
3. **Complete Journey** → Siehe: [Complete User Journey](#complete-user-journey-create--publish-course)
4. **Entscheidungen treffen** → Siehe: [Decision Trees](#-decision-trees)
5. **Fehler beheben** → Siehe: [Troubleshooting](#-troubleshooting)