# Agents Domain - Import Guide

**Quick reference for importing agents/ modules**

---

## Blueprints (API Routes)

### Import all blueprints at once
```python
from app.api import agents  # Auto-registers all blueprints on api_v1
```

### Import specific blueprints
```python
from app.api.agents import agents_core_bp, agents_admin_bp
from app.api.agents.core import agents_core_bp
from app.api.agents.knowledge import agents_knowledge_bp
from app.api.agents.admin import agents_admin_bp
from app.api.agents.audio import agents_audio_bp
from app.api.agents.media import agents_media_bp, media_bp
```

---

## Helpers

```python
from app.api.agents._helpers import (
    validate_course_exists,
    check_course_authorization,
    error_response,
    success_response,
    UPLOAD_TEMP_PATH,
    ALLOWED_AUDIO_EXTENSIONS
)
```

---

## Factory (Optional - Reference Implementation)

**Note:** Factory is not yet integrated. To use it:

1. Uncomment in `app/api/agents/core/__init__.py`:
   ```python
   from .factory import AgentFactory
   ```

2. Import in your code:
   ```python
   from app.api.agents.core import AgentFactory

   # Create default agent
   agent = AgentFactory.create_default_agent('course-123', 'premium')

   # Create custom agent
   agent = AgentFactory.create_custom_agent(
       course_id='course-123',
       name='Math Tutor',
       persona='socratic'
   )

   # Validate agent
   AgentFactory.validate_agent_config(agent)
   ```

---

## Service Layer

```python
from app.services.agent_service import AgentService

# Ask agent
result = AgentService.ask(
    course_id='course-123',
    user_id='user-456',
    question='Was ist Python?'
)

# Get status
status = AgentService.get_status('course-123')

# Add knowledge
knowledge = AgentService.add_knowledge(
    course_id='course-123',
    question='Was ist OOP?',
    answer='OOP steht fuer...'
)
```

---

## Repository Layer

```python
from app.repositories.agent import AgentRepository

# Get agent by course
agent = AgentRepository.get_agent_by_course('course-123')

# Get or create agent
agent = AgentRepository.get_or_create_agent('course-123')

# Update agent
updated = AgentRepository.update_agent(
    agent_id='agent-789',
    name='New Name',
    temperature=0.9
)

# Get agent stats
stats = AgentRepository.get_agent_stats('agent-789')
```

---

## Models (Pydantic)

```python
from app.models.agent import (
    # Request models
    AgentAskRequest,
    AgentFeedbackRequest,
    AgentConfigUpdate,
    KnowledgeCreateRequest,
    AgentWarmRequest,

    # Response models
    AgentAskResponse,
    AgentStatusResponse,
    AgentConfigResponse,
    KnowledgeEntryResponse,
    AgentWarmResponse,

    # Enums
    AgentPersona,
    KnowledgeStatus,
    KnowledgeType,
    ScopeType,
    ResponseSource
)

# Example usage
request = AgentAskRequest(
    question='Was ist Polymorphismus?',
    context={'lesson_id': 'lesson-123'},
    language='de'
)
```

---

## Middleware (Authentication)

```python
from app.middleware.auth import (
    token_required,
    role_required,
    get_current_user
)

# Usage in routes
@agents_core_bp.route('/<course_id>/ask', methods=['POST'])
@token_required
def agent_ask(course_id: str):
    user = get_current_user()
    # ...

@agents_admin_bp.route('', methods=['GET'])
@role_required('admin', 'superadmin')
def list_all_agents():
    # ...
```

---

## Testing (When implemented)

```python
# Unit tests
from app.api.agents.core import agents_core_bp
from app.api.agents.core.factory import AgentFactory

def test_agent_ask(client, auth_headers):
    response = client.post(
        '/api/v1/agents/course-123/ask',
        json={'question': 'Was ist Python?'},
        headers=auth_headers
    )
    assert response.status_code == 200

def test_factory_creates_valid_agent():
    agent = AgentFactory.create_default_agent('course-123', 'premium')
    assert agent['primary_provider'] == 'anthropic'
    assert AgentFactory.validate_agent_config(agent) == True
```

---

## Common Import Patterns

### Backend API Endpoint
```python
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.agent import AgentAskRequest, AgentAskResponse
from app.services.agent_service import AgentService
from app.repositories.agent import AgentRepository
from app.middleware.auth import token_required, get_current_user
from app.api.agents._helpers import validate_course_exists, error_response

@agents_core_bp.route('/<course_id>/ask', methods=['POST'])
@token_required
def agent_ask(course_id: str):
    # Implementation...
```

### Service Implementation
```python
from typing import Dict, Optional
from app.repositories.agent import AgentRepository
from app.extensions import redis_client

class AgentService:
    @staticmethod
    def ask(course_id: str, user_id: str, question: str) -> Dict:
        # Implementation...
```

### Repository Implementation
```python
from app.repositories.base_repository import BaseRepository
from typing import Optional, Dict, List

class AgentCRUDRepository(BaseRepository):
    @staticmethod
    def get_agent_by_course(course_id: str) -> Optional[Dict]:
        query = "SELECT * FROM course_agents WHERE course_id = %s"
        return AgentCRUDRepository.fetch_one(query, (course_id,))
```

---

## Troubleshooting

### Import Error: "No module named 'app.api.agents'"
**Solution:** Ensure you're running from `backend/` directory with venv activated

### Import Error: "cannot import name 'AgentFactory'"
**Solution:** Factory is optional. Uncomment the import in `core/__init__.py` first

### Import Error: "No module named 'app.services.agent_service'"
**Solution:** Use correct import path:
```python
# Deprecated (but works for backward compatibility)
from app.services.agent_service import AgentService

# New (preferred)
from app.services.agent import AgentService
```

### Circular Import Error
**Solution:** Agents domain has no circular imports. If you encounter one:
1. Check if you're importing from API layer in service/repository layer (forbidden!)
2. Use TYPE_CHECKING for type hints only:
   ```python
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from app.api.agents import agents_core_bp
   ```

---

## Import Hierarchy (Top to Bottom)

```
API Layer (app/api/agents/)
    ↓ imports
Service Layer (app/services/agent/)
    ↓ imports
Repository Layer (app/repositories/agent/)
    ↓ imports
Models (app/models/agent.py)
    ↓ imports
Extensions (app/extensions.py - db, redis, etc.)
```

**RULE:** Never import upward in this hierarchy!

---

**Last Updated:** 2026-01-08
**Maintainer:** Backend Team
