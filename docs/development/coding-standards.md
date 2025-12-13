# LernsystemX - Coding Standards & Development Guidelines

**Quality Management System conforming to ISO 9001:2015 Principles**

---

## Document Control

| Property | Value |
|----------|-------|
| **Document ID** | LSX-DEV-001 |
| **Version** | 1.0.0 |
| **Date** | 2025-11-15 |
| **Status** | Active |
| **Owner** | Development Team |
| **Review Cycle** | Quarterly |
| **Next Review** | 2026-02-15 |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [General Principles](#2-general-principles)
3. [Python Coding Standards](#3-python-coding-standards)
4. [JavaScript/Vue.js Standards](#4-javascriptvuejs-standards)
5. [Database Standards](#5-database-standards)
6. [API Design Standards](#6-api-design-standards)
7. [Testing Standards](#7-testing-standards)
8. [Documentation Standards](#8-documentation-standards)
9. [Version Control Standards](#9-version-control-standards)
10. [Code Review Process](#10-code-review-process)
11. [Security Standards](#11-security-standards)
12. [Performance Standards](#12-performance-standards)

---

## 1. Introduction

### 1.1 Purpose

This document defines the coding standards and development guidelines for LernsystemX (LSX) to ensure:

- **Code Quality**: Maintainable, readable, and consistent code
- **Collaboration**: Seamless teamwork through shared conventions
- **Reliability**: Reduced bugs through testing and reviews
- **Scalability**: Architecture that grows with the platform

### 1.2 Scope

These standards apply to:
- Backend development (Python/Flask)
- Frontend development (JavaScript/Vue.js)
- Database design (PostgreSQL)
- API design (REST/WebSocket)
- Documentation

### 1.3 ISO 9001 Alignment

This document aligns with ISO 9001:2015 quality management principles:
- **Process Approach**: Structured development workflow
- **Continuous Improvement**: Code reviews, refactoring
- **Evidence-Based Decision Making**: Metrics, test coverage
- **Customer Focus**: User experience and reliability

---

## 2. General Principles

### 2.1 Code Quality Principles

1. **KISS (Keep It Simple, Stupid)**: Prefer simple solutions over complex ones
2. **DRY (Don't Repeat Yourself)**: Avoid code duplication
3. **YAGNI (You Aren't Gonna Need It)**: Don't build features you don't need yet
4. **SOLID Principles**: Object-oriented design best practices
5. **Separation of Concerns**: Models, Services, Routes clearly separated

### 2.2 Readability Over Cleverness

```python
# ❌ BAD - Clever but unreadable
result = [x for x in range(100) if x % 2 and x % 3]

# ✅ GOOD - Clear and readable
def is_not_divisible_by_2_or_3(number):
    return number % 2 != 0 and number % 3 != 0

result = [x for x in range(100) if is_not_divisible_by_2_or_3(x)]
```

### 2.3 Fail Fast Principle

Validate inputs early and throw errors immediately:

```python
def create_course(user_id, title, description):
    # ✅ GOOD - Validate immediately
    if not user_id:
        raise ValueError("user_id is required")
    if not title or len(title) < 3:
        raise ValueError("title must be at least 3 characters")

    # Continue with business logic
    ...
```

---

## 3. Python Coding Standards

### 3.1 PEP 8 Compliance

**All Python code MUST conform to PEP 8.**

- **Line Length**: Maximum 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped (stdlib, third-party, local)
- **Naming**: See section 3.2

**Enforcement**: Use `black` for auto-formatting, `flake8` for linting.

```bash
# Format code
black app/

# Lint code
flake8 app/ --max-line-length=100
```

### 3.2 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| **Module/Package** | lowercase_with_underscores | `auth_service.py` |
| **Class** | PascalCase | `UserService`, `CourseModel` |
| **Function/Method** | lowercase_with_underscores | `get_user_by_id()` |
| **Variable** | lowercase_with_underscores | `user_count`, `is_active` |
| **Constant** | UPPERCASE_WITH_UNDERSCORES | `MAX_TOKEN_LIMIT`, `API_VERSION` |
| **Private** | _leading_underscore | `_validate_token()` |

### 3.3 Type Hints (Required)

Use Python type hints for all functions:

```python
from typing import Optional, List, Dict
from datetime import datetime

def get_user_courses(
    user_id: int,
    include_archived: bool = False,
    limit: Optional[int] = None
) -> List[Dict[str, any]]:
    """
    Retrieve courses for a specific user

    Args:
        user_id: ID of the user
        include_archived: Whether to include archived courses
        limit: Maximum number of courses to return

    Returns:
        List of course dictionaries

    Raises:
        ValueError: If user_id is invalid
    """
    pass
```

### 3.4 Docstrings (Required)

Use Google-style docstrings for all public functions/classes:

```python
def calculate_token_cost(method_type: str, content_length: int) -> int:
    """
    Calculate AI token cost for a learning method.

    Args:
        method_type: Type of learning method (e.g., 'quiz', 'exam')
        content_length: Length of input content in characters

    Returns:
        Estimated token cost

    Raises:
        ValueError: If method_type is not supported

    Example:
        >>> calculate_token_cost('quiz', 5000)
        1500
    """
    pass
```

### 3.5 Error Handling

**Always use specific exceptions:**

```python
# ❌ BAD - Generic exception
try:
    user = User.query.get(user_id)
except Exception as e:
    print(e)

# ✅ GOOD - Specific exceptions
from sqlalchemy.exc import SQLAlchemyError

try:
    user = User.query.get(user_id)
except SQLAlchemyError as e:
    logger.error(f"Database error fetching user {user_id}: {e}")
    raise DatabaseError("Failed to retrieve user") from e
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise
```

### 3.6 Import Order

```python
# 1. Standard library imports
import os
import sys
from datetime import datetime

# 2. Third-party imports
from flask import Flask, jsonify
from sqlalchemy import Column, Integer

# 3. Local application imports
from app.models import User
from app.services import AuthService
```

---

## 4. JavaScript/Vue.js Standards

### 4.1 ESLint + Prettier

Use ESLint with Airbnb style guide + Prettier for auto-formatting.

```json
// .eslintrc.js
module.exports = {
  extends: [
    'plugin:vue/vue3-recommended',
    'airbnb-base',
    'prettier'
  ],
  rules: {
    'max-len': ['error', { code: 100 }],
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn'
  }
}
```

### 4.2 Vue 3 Composition API

**Always use Composition API (not Options API):**

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCourseStore } from '@/stores/course'

// ✅ GOOD - Composition API
const courseStore = useCourseStore()
const isLoading = ref(false)

const totalCourses = computed(() => courseStore.courses.length)

onMounted(async () => {
  await courseStore.fetchCourses()
})
</script>
```

### 4.3 Component Naming

- **PascalCase** for component files: `CourseCard.vue`, `UserProfile.vue`
- **kebab-case** in templates: `<course-card />`, `<user-profile />`

---

## 5. Database Standards

### 5.1 Model Design

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.extensions import db

class Course(db.Model):
    """
    Course model representing a learning course

    Relationships:
        - creator: User who created the course (many-to-one)
        - modules: List of modules in the course (one-to-many)
        - enrollments: List of user enrollments (one-to-many)
    """
    __tablename__ = 'courses'

    # Primary Key
    id = Column(Integer, primary_key=True)

    # Foreign Keys
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Attributes
    title = Column(String(200), nullable=False, index=True)
    description = Column(String(1000))
    language = Column(String(2), default='de')  # ISO 639-1
    is_published = Column(Boolean, default=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship('User', back_populates='created_courses')
    modules = relationship('Module', back_populates='course', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.id}: {self.title}>'
```

### 5.2 Migration Standards

**Always create migrations for schema changes:**

```bash
# Create migration
flask db migrate -m "Add language column to courses table"

# Review migration file before applying
# Edit if necessary

# Apply migration
flask db upgrade
```

### 5.3 Query Optimization

```python
# ❌ BAD - N+1 query problem
courses = Course.query.all()
for course in courses:
    print(course.creator.name)  # Triggers additional query

# ✅ GOOD - Eager loading
from sqlalchemy.orm import joinedload

courses = Course.query.options(joinedload(Course.creator)).all()
for course in courses:
    print(course.creator.name)  # No additional query
```

---

## 6. API Design Standards

### 6.1 RESTful Conventions

| HTTP Method | Endpoint | Action |
|-------------|----------|--------|
| `GET` | `/api/v1/courses` | List all courses |
| `GET` | `/api/v1/courses/:id` | Get single course |
| `POST` | `/api/v1/courses` | Create new course |
| `PUT` | `/api/v1/courses/:id` | Replace course (full update) |
| `PATCH` | `/api/v1/courses/:id` | Update course (partial) |
| `DELETE` | `/api/v1/courses/:id` | Delete course |

### 6.2 Response Format

**All API responses MUST use this structure:**

```json
// Success Response
{
  "status": "success",
  "data": {
    "id": 123,
    "title": "Python Programming"
  },
  "meta": {
    "timestamp": "2025-11-15T10:30:00Z"
  }
}

// Error Response
{
  "status": "error",
  "error": {
    "code": "INVALID_INPUT",
    "message": "Title must be at least 3 characters",
    "field": "title"
  },
  "meta": {
    "timestamp": "2025-11-15T10:30:00Z"
  }
}

// List Response (with pagination)
{
  "status": "success",
  "data": [...],
  "meta": {
    "total": 150,
    "page": 1,
    "per_page": 20,
    "total_pages": 8
  }
}
```

### 6.3 HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET, PATCH, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid JWT |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

---

## 7. Testing Standards

### 7.1 Test Coverage Requirements

- **Minimum Coverage**: 80% for new code
- **Critical Paths**: 100% (auth, payments, AI token deduction)
- **Models**: 100% (simple to test)

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Coverage report should show:
# TOTAL: 85%+ coverage
```

### 7.2 Test Structure

```python
# tests/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.models import User

class TestAuthService:
    """Test suite for AuthService"""

    def test_register_user_success(self, db_session):
        """Test successful user registration"""
        # Arrange
        email = "test@example.com"
        password = "SecurePass123!"

        # Act
        user = AuthService.register(email, password)

        # Assert
        assert user.id is not None
        assert user.email == email
        assert user.password_hash != password  # Hashed

    def test_register_duplicate_email_fails(self, db_session, existing_user):
        """Test that duplicate email registration fails"""
        # Arrange
        email = existing_user.email

        # Act & Assert
        with pytest.raises(ValueError, match="Email already exists"):
            AuthService.register(email, "password")
```

### 7.3 Test Categories

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test multiple components together
3. **E2E Tests**: Test full user workflows (frontend + backend)
4. **Performance Tests**: Load testing with Locust

---

## 8. Documentation Standards

### 8.1 Code Documentation

**Every module must have a module-level docstring:**

```python
"""
User authentication service

This module provides functions for user registration, login, and JWT token management.
It implements role-based access control (RBAC) for the 9 user roles in LernsystemX.

Example:
    from app.services.auth_service import AuthService

    user = AuthService.register('user@example.com', 'password')
    token = AuthService.login('user@example.com', 'password')

Dependencies:
    - Flask-JWT-Extended for token management
    - bcrypt for password hashing
    - Redis for token blacklist
"""
```

### 8.2 API Documentation

Use **OpenAPI 3.0** (Swagger) for API documentation:

```python
from flask import Blueprint
from flasgger import swag_from

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Register a new user',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string', 'minLength': 8}
            }
        }
    }],
    'responses': {
        201: {'description': 'User created successfully'},
        400: {'description': 'Invalid input'},
        409: {'description': 'Email already exists'}
    }
})
def register():
    pass
```

---

## 9. Version Control Standards

### 9.1 Git Commit Messages

**Format: `<type>(<scope>): <subject>`**

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build, dependencies, tooling

Examples:
```
feat(auth): add JWT token refresh endpoint
fix(payments): correct Stripe webhook signature validation
docs(api): update course creation endpoint documentation
refactor(models): simplify User model relationships
test(ai): add tests for quiz generation service
```

### 9.2 Branch Naming

- `main` - Production-ready code
- `develop` - Development branch
- `feature/<name>` - New features
- `fix/<name>` - Bug fixes
- `hotfix/<name>` - Urgent production fixes

### 9.3 Pull Request Requirements

**All PRs must have:**
1. Descriptive title and description
2. Linked issue (e.g., "Closes #123")
3. Tests for new functionality
4. Documentation updates
5. No merge conflicts
6. Passing CI/CD checks
7. At least 1 approval from code review

---

## 10. Code Review Process

### 10.1 Review Checklist

**Functionality**
- [ ] Code works as intended
- [ ] Edge cases handled
- [ ] Error handling present

**Code Quality**
- [ ] Follows coding standards (PEP 8, ESLint)
- [ ] No code duplication
- [ ] Meaningful variable/function names

**Testing**
- [ ] Tests added for new features
- [ ] All tests pass
- [ ] Coverage >= 80%

**Documentation**
- [ ] Docstrings for public functions
- [ ] README updated if needed
- [ ] API docs updated

**Security**
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] SQL injection prevented (parameterized queries)

### 10.2 Review Response Time

- **Critical Fixes**: 2 hours
- **Regular PRs**: 24 hours
- **Large Features**: 48 hours

---

## 11. Security Standards

### 11.1 Input Validation

**Always validate and sanitize user input:**

```python
from marshmallow import Schema, fields, validate

class CourseCreateSchema(Schema):
    title = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=200)
    )
    description = fields.Str(
        validate=validate.Length(max=1000)
    )
    language = fields.Str(
        validate=validate.OneOf(['de', 'en', 'es', 'fr'])
    )

# In route
@courses_bp.route('/', methods=['POST'])
def create_course():
    schema = CourseCreateSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify({'error': errors}), 400

    data = schema.load(request.json)
    # Continue...
```

### 11.2 Secrets Management

**NEVER commit secrets to Git:**

- Use `.env` files (gitignored)
- Use environment variables
- Use secret management tools (AWS Secrets Manager, Azure Key Vault)

```python
# ❌ BAD
STRIPE_API_KEY = "sk_test_abc123"

# ✅ GOOD
import os
STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')
if not STRIPE_API_KEY:
    raise ValueError("STRIPE_SECRET_KEY environment variable not set")
```

---

## 12. Performance Standards

### 12.1 Database Queries

- Use pagination for large result sets (max 100 items per page)
- Use database indexes for frequently queried columns
- Avoid N+1 queries (use `joinedload`)

### 12.2 Caching Strategy

```python
from app.extensions import redis_client

def get_course_with_cache(course_id: int):
    # Check cache first
    cache_key = f'course:{course_id}'
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Query database
    course = Course.query.get(course_id)

    # Store in cache (TTL: 5 minutes)
    redis_client.setex(
        cache_key,
        300,
        json.dumps(course.to_dict())
    )

    return course
```

---

## Compliance Checklist

Before merging any code, verify:

- [ ] Code follows PEP 8 (Python) or ESLint (JavaScript)
- [ ] All functions have type hints (Python) or TypeScript types (JS)
- [ ] All public functions have docstrings
- [ ] Tests written and passing (coverage >= 80%)
- [ ] No security vulnerabilities (secrets, SQL injection, XSS)
- [ ] Error handling present
- [ ] Code reviewed and approved
- [ ] Documentation updated

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-15 | Development Team | Initial coding standards document |

---

**Document Classification**: Internal Use

**Compliance**: ISO 9001:2015 Quality Management - Process Approach & Continuous Improvement
