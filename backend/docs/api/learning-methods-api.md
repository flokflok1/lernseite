# LernsystemX Learning Methods API Documentation

**Version:** 1.0.0
**Standard:** ISO/IEC/IEEE 26515:2018 - API Documentation
**Last Updated:** 2025-11-16

## Overview

The Learning Methods API provides AI-powered learning experiences with multi-provider support, token tracking, and feedback collection. This API enables 21 different learning methods across 3 subscription tiers.

### Key Features

- **AI Multi-Provider Support:** OpenAI, Anthropic, Google, Cohere, HuggingFace
- **Token Tracking:** Monitor and track AI token consumption and costs
- **Feedback Loop:** Collect and analyze user feedback (1-5 star ratings)
- **Tier-Based Access:** Basic, Premium, Pro subscription tiers
- **21 Learning Methods:** Flashcards, Quiz, KI-Tutor, Deep Praxis, and more

### Base URL

```
http://localhost:5000/api/v1
```

---

## Authentication

- **Public Endpoints:** GET requests for listing, details, examples, feedback
- **Authenticated Endpoints:** POST /execute, POST /feedback (requires JWT token)
- **Admin Endpoints:** POST, PUT, DELETE, stats (requires admin/superadmin role)

### Headers

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## Subscription Tiers

### Basic Tier (Free)
```
- Flashcards
- Quiz
- Lückentext
- Multiple Choice
- True/False
- Zuordnung
- Sortierung
- Mindmap
- Video
- Audio
- PDF
```

### Premium Tier
```
- All Basic methods
- KI-Tutor (AI-powered tutoring)
- KI-Glossar (AI terminology explanations)
- Braindump (Knowledge summaries)
- Zertifikatsprüfung (Certification exams)
- Lernpfad-KI (AI learning paths)
- Live-Raum (Live learning sessions)
```

### Pro Tier
```
- All Premium methods
- Deep Praxis (Advanced practical exercises)
- Deep Scenario (Complex scenario simulations)
- Projekt-Simulation (Project simulations)
- Echtzeit-Debugging (Real-time debugging)
```

---

## Endpoints

### 1. List All Learning Methods

Get a list of all available learning methods.

**Endpoint:** `GET /learning-methods`

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| active_only | boolean | No | true | Only return active methods |
| tier | string | No | - | Filter by tier (basic, premium, pro) |

**Example Request:**
```http
GET /api/v1/learning-methods?active_only=true&tier=premium
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "methods": [
    {
      "method_id": 5,
      "name": "KI-Tutor",
      "description": "AI-powered personalized tutoring",
      "tier": "premium",
      "config": {
        "ai_enabled": true,
        "ai_model": "gpt-4o-mini",
        "ai_provider": "openai",
        "context_memory": true,
        "adaptive_difficulty": true,
        "max_conversation_turns": 50
      },
      "active": true,
      "usage_count": 2847,
      "created_at": "2025-01-10T08:00:00Z",
      "updated_at": "2025-01-10T08:00:00Z"
    },
    {
      "method_id": 6,
      "name": "KI-Glossar",
      "description": "AI-powered terminology explanations",
      "tier": "premium",
      "config": {
        "ai_enabled": true,
        "ai_model": "gpt-4o-mini",
        "supports_images": true
      },
      "active": true,
      "usage_count": 1523,
      "created_at": "2025-01-10T08:05:00Z",
      "updated_at": "2025-01-10T08:05:00Z"
    }
  ],
  "total": 2
}
```

---

### 2. Get Learning Method Details

Get detailed information about a specific learning method.

**Endpoint:** `GET /learning-methods/:id`

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | Learning method ID |

**Example Request:**
```http
GET /api/v1/learning-methods/5
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "method": {
    "method_id": 5,
    "name": "KI-Tutor",
    "description": "AI-powered personalized tutoring with adaptive difficulty",
    "tier": "premium",
    "config": {
      "ai_enabled": true,
      "ai_model": "gpt-4o-mini",
      "ai_provider": "openai",
      "context_memory": true,
      "adaptive_difficulty": true,
      "max_conversation_turns": 50,
      "temperature": 0.7,
      "max_tokens": 2000
    },
    "active": true,
    "usage_count": 2847,
    "feedback_stats": {
      "total_feedback": 342,
      "average_rating": 4.6,
      "helpful_count": 318,
      "not_helpful_count": 24,
      "rating_distribution": {
        "1": 3,
        "2": 8,
        "3": 13,
        "4": 98,
        "5": 220
      }
    },
    "created_at": "2025-01-10T08:00:00Z",
    "updated_at": "2025-01-10T08:00:00Z"
  }
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Learning method not found"
}
```

---

### 3. Execute AI Learning Method (Premium+)

Execute an AI-powered learning method. Requires authentication and appropriate subscription tier.

**Endpoint:** `POST /learning-methods/:id/execute`

**Authentication:** Required (JWT token)

**Tier Requirement:** Varies by method (Premium or Pro)

**Rate Limit:** 100 requests per hour per user

**Request Body:**
```json
{
  "user_input": "Erkläre mir Polymorphismus in Python",
  "context": "Wir sind bei Lektion 3: OOP Konzepte",
  "language": "de",
  "difficulty": "intermediate",
  "course_id": 10,
  "module_id": 25,
  "lesson_id": 42,
  "conversation_history": [
    {
      "role": "user",
      "content": "Was ist Vererbung?"
    },
    {
      "role": "assistant",
      "content": "Vererbung ist ein grundlegendes Konzept..."
    }
  ]
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| user_input | string | Yes | User's question/input (1-5000 chars) |
| context | string | No | Additional context (max 10000 chars) |
| language | string | No | Response language (de, en, pl, es, fr, it) - default: de |
| difficulty | string | No | Difficulty level (beginner, intermediate, advanced) |
| course_id | integer | No | Course ID for context tracking |
| module_id | integer | No | Module ID for context tracking |
| lesson_id | integer | No | Lesson ID for context tracking |
| conversation_history | array | No | Previous conversation turns (max 20 turns) |

**Example Response (200 OK):**
```json
{
  "success": true,
  "execution": {
    "execution_id": 12345,
    "method_id": 5,
    "method_name": "KI-Tutor",
    "output_text": "Polymorphismus in Python ermöglicht es, dass Objekte verschiedener Klassen über eine gemeinsame Schnittstelle angesprochen werden können. Es gibt zwei Hauptarten:\n\n1. **Duck Typing**: Python nutzt Duck Typing - wenn ein Objekt eine Methode hat, kann sie aufgerufen werden, unabhängig vom Klassentyp.\n\n2. **Vererbung**: Unterklassen können Methoden der Oberklasse überschreiben.\n\nBeispiel:\n```python\nclass Tier:\n    def sprechen(self):\n        pass\n\nclass Hund(Tier):\n    def sprechen(self):\n        return \"Wuff!\"\n\nclass Katze(Tier):\n    def sprechen(self):\n        return \"Miau!\"\n\n# Polymorphismus in Aktion:\ntiere = [Hund(), Katze()]\nfor tier in tiere:\n    print(tier.sprechen())  # Ruft die richtige Methode auf\n```",
    "input_tokens": 150,
    "output_tokens": 320,
    "total_tokens": 470,
    "model": "gpt-4o-mini",
    "provider": "openai",
    "latency_ms": 1234,
    "confidence": 0.92,
    "cost_eur": 0.000235,
    "executed_at": "2025-01-16T14:23:45Z"
  }
}
```

**Error Response (403 Forbidden - Tier Insufficient):**
```json
{
  "success": false,
  "error": "Insufficient subscription tier",
  "message": "This method requires premium tier. Your tier: basic",
  "required_tier": "premium",
  "user_tier": "basic",
  "upgrade_url": "/api/v1/subscriptions/upgrade"
}
```

**Error Response (500 AI Provider Error):**
```json
{
  "success": false,
  "error": "AI execution failed",
  "message": "AI request timed out. Please try again."
}
```

---

### 4. Get Method Usage Examples

Get example prompts and use cases for a learning method.

**Endpoint:** `GET /learning-methods/:id/examples`

**Example Request:**
```http
GET /api/v1/learning-methods/5/examples
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "method_id": 5,
  "method_name": "KI-Tutor",
  "examples": [
    {
      "prompt": "Erkläre mir Polymorphismus in Python",
      "context": "Wir sind bei Lektion 3: OOP Konzepte",
      "difficulty": "intermediate"
    },
    {
      "prompt": "Was sind Decorators und wann verwende ich sie?",
      "context": "Python Advanced Concepts",
      "difficulty": "advanced"
    }
  ]
}
```

---

### 5. Get Method Feedback

Get user feedback for a learning method.

**Endpoint:** `GET /learning-methods/:id/feedback`

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 50 | Maximum results (max: 200) |

**Example Request:**
```http
GET /api/v1/learning-methods/5/feedback?limit=10
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "feedback": [
    {
      "feedback_id": 789,
      "user_id": 42,
      "username": "max.mustermann",
      "first_name": "Max",
      "last_name": "Mustermann",
      "execution_id": 12345,
      "method_id": 5,
      "rating": 5,
      "feedback_text": "Sehr hilfreiche Erklärung mit praktischen Beispielen!",
      "is_helpful": true,
      "created_at": "2025-01-16T14:25:00Z"
    }
  ],
  "stats": {
    "total_feedback": 342,
    "average_rating": 4.6,
    "helpful_count": 318,
    "not_helpful_count": 24,
    "rating_distribution": {
      "1": 3,
      "2": 8,
      "3": 13,
      "4": 98,
      "5": 220
    }
  },
  "total": 10
}
```

---

### 6. Submit Feedback (Authenticated)

Submit feedback for an AI execution.

**Endpoint:** `POST /learning-methods/:id/feedback`

**Authentication:** Required

**Request Body:**
```json
{
  "execution_id": 12345,
  "rating": 5,
  "feedback_text": "Sehr hilfreiche Erklärung mit praktischen Beispielen!",
  "is_helpful": true,
  "course_id": 10,
  "module_id": 25
}
```

**Field Descriptions:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| execution_id | integer | Yes | Execution record ID |
| rating | integer | Yes | Rating (1-5 stars) |
| feedback_text | string | No | Feedback text (max 2000 chars) |
| is_helpful | boolean | No | Was response helpful? (default: true) |
| course_id | integer | No | Course ID for context |
| module_id | integer | No | Module ID for context |
| lesson_id | integer | No | Lesson ID for context |

**Example Response (201 Created):**
```json
{
  "success": true,
  "message": "Feedback submitted successfully",
  "feedback": {
    "feedback_id": 790,
    "user_id": 42,
    "execution_id": 12345,
    "method_id": 5,
    "rating": 5,
    "feedback_text": "Sehr hilfreiche Erklärung!",
    "is_helpful": true,
    "created_at": "2025-01-16T14:30:00Z"
  }
}
```

---

### 7. Get My Token Usage (Authenticated)

Get current user's AI token usage statistics.

**Endpoint:** `GET /learning-methods/my-usage`

**Authentication:** Required

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| period_days | integer | No | 30 | Period in days (max: 365) |

**Example Request:**
```http
GET /api/v1/learning-methods/my-usage?period_days=30
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "usage": {
    "user_id": 42,
    "total_tokens": 125000,
    "total_cost_eur": 12.50,
    "total_requests": 267,
    "by_method": {
      "KI-Tutor": 85000,
      "KI-Glossar": 25000,
      "Braindump": 15000
    },
    "by_provider": {
      "openai": 100000,
      "anthropic": 25000
    },
    "by_model": {
      "gpt-4o-mini": 75000,
      "gpt-4o": 25000,
      "claude-3-5-haiku-20241022": 25000
    },
    "period_start": "2024-12-17T00:00:00Z",
    "period_end": "2025-01-16T14:30:00Z"
  }
}
```

---

### 8. Create Learning Method (Admin Only)

Create a new learning method.

**Endpoint:** `POST /learning-methods`

**Authentication:** Required (Admin/Superadmin)

**Request Body:**
```json
{
  "name": "Advanced Quiz",
  "description": "Quiz with adaptive difficulty and AI-generated questions",
  "tier": "premium",
  "config": {
    "ai_enabled": true,
    "adaptive_difficulty": true,
    "max_questions": 100,
    "ai_model": "gpt-4o-mini",
    "ai_provider": "openai",
    "question_types": ["multiple_choice", "true_false", "fill_in_blank"]
  },
  "active": true
}
```

**Example Response (201 Created):**
```json
{
  "success": true,
  "message": "Learning method created successfully",
  "method": {
    "method_id": 22,
    "name": "Advanced Quiz",
    "tier": "premium",
    "created_at": "2025-01-16T14:35:00Z"
  }
}
```

---

### 9. Update Learning Method (Admin Only)

Update an existing learning method.

**Endpoint:** `PUT /learning-methods/:id`

**Authentication:** Required (Admin/Superadmin)

**Request Body (Partial Update):**
```json
{
  "description": "Updated description",
  "config": {
    "ai_model": "gpt-4o",
    "max_tokens": 3000
  },
  "active": true
}
```

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Learning method updated successfully",
  "method": {
    "method_id": 5,
    "name": "KI-Tutor",
    "updated_at": "2025-01-16T14:40:00Z"
  }
}
```

---

### 10. Delete Learning Method (Admin Only)

Delete a learning method (hard delete).

**Endpoint:** `DELETE /learning-methods/:id`

**Authentication:** Required (Admin/Superadmin)

**WARNING:** Hard delete. Use deactivate for methods in active use.

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Learning method deleted successfully"
}
```

---

### 11. Get Statistics (Admin Only)

Get overall learning method statistics.

**Endpoint:** `GET /learning-methods/stats`

**Authentication:** Required (Admin/Superadmin)

**Example Response (200 OK):**
```json
{
  "success": true,
  "stats": {
    "total_methods": 21,
    "active_methods": 21,
    "by_tier": {
      "basic": 11,
      "premium": 6,
      "pro": 4
    },
    "ai_powered_count": 10,
    "most_used": "Flashcards",
    "total_executions": 125678,
    "total_tokens": 25000000,
    "total_cost_eur": 2587.50
  }
}
```

---

### 12. Activate Learning Method (Admin Only)

Activate a deactivated learning method.

**Endpoint:** `POST /learning-methods/:id/activate`

**Authentication:** Required (Admin/Superadmin)

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Learning method activated successfully",
  "method": {
    "method_id": 5,
    "active": true
  }
}
```

---

### 13. Deactivate Learning Method (Admin Only)

Deactivate a learning method (soft delete).

**Endpoint:** `POST /learning-methods/:id/deactivate`

**Authentication:** Required (Admin/Superadmin)

**Example Response (200 OK):**
```json
{
  "success": true,
  "message": "Learning method deactivated successfully",
  "method": {
    "method_id": 5,
    "active": false
  }
}
```

---

## AI Provider Configuration

### Supported Providers

| Provider | Models | Input Price (per 1K tokens, EUR) | Output Price (per 1K tokens, EUR) |
|----------|--------|----------------------------------|-----------------------------------|
| **OpenAI** | gpt-4o | 0.0025 | 0.010 |
| | gpt-4o-mini | 0.00015 | 0.0006 |
| | gpt-4-turbo | 0.010 | 0.030 |
| | gpt-3.5-turbo | 0.0005 | 0.0015 |
| **Anthropic** | claude-3-5-sonnet-20241022 | 0.003 | 0.015 |
| | claude-3-5-haiku-20241022 | 0.001 | 0.005 |
| | claude-3-opus-20240229 | 0.015 | 0.075 |
| **Google** | gemini-1.5-pro | 0.00125 | 0.005 |
| | gemini-1.5-flash | 0.000075 | 0.0003 |
| **Cohere** | command | 0.0015 | 0.002 |
| | command-light | 0.0003 | 0.0006 |
| **HuggingFace** | meta-llama/Llama-3.2-3B-Instruct | 0.0001 | 0.0002 |
| | mistralai/Mistral-7B-Instruct-v0.3 | 0.0001 | 0.0002 |

### API Keys Required

Set these environment variables:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
COHERE_API_KEY=...
HUGGINGFACE_API_KEY=hf_...
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions or tier) |
| 404 | Not Found |
| 429 | Too Many Requests (rate limit exceeded) |
| 500 | Internal Server Error (AI provider error) |

---

## Rate Limits

| Tier | Executions per Hour | Daily Token Limit |
|------|---------------------|-------------------|
| Basic | - | - (No AI access) |
| Premium | 100 | 100,000 tokens |
| Pro | 500 | 500,000 tokens |

---

## Example Use Cases

### 1. KI-Tutor Conversation

```javascript
// Initial question
const response1 = await fetch('/api/v1/learning-methods/5/execute', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_input: 'Was ist Vererbung in Python?',
    context: 'OOP Grundlagen',
    language: 'de',
    difficulty: 'beginner'
  })
});

const data1 = await response1.json();
console.log(data1.execution.output_text);

// Follow-up question with conversation history
const response2 = await fetch('/api/v1/learning-methods/5/execute', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_input: 'Kannst du mir ein Beispiel zeigen?',
    context: 'OOP Grundlagen',
    language: 'de',
    difficulty: 'beginner',
    conversation_history: [
      {
        role: 'user',
        content: 'Was ist Vererbung in Python?'
      },
      {
        role: 'assistant',
        content: data1.execution.output_text
      }
    ]
  })
});

const data2 = await response2.json();
console.log(data2.execution.output_text);
```

### 2. Token Usage Monitoring

```javascript
// Get user's token usage
const response = await fetch('/api/v1/learning-methods/my-usage?period_days=7', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const { usage } = await response.json();

console.log(`Tokens used this week: ${usage.total_tokens}`);
console.log(`Cost: €${usage.total_cost_eur.toFixed(4)}`);
console.log(`Requests: ${usage.total_requests}`);

// Display usage by method
Object.entries(usage.by_method).forEach(([method, tokens]) => {
  console.log(`${method}: ${tokens} tokens`);
});
```

### 3. Feedback Collection

```javascript
// Submit feedback after execution
const feedbackResponse = await fetch('/api/v1/learning-methods/5/feedback', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    execution_id: 12345,
    rating: 5,
    feedback_text: 'Excellent explanation with clear examples!',
    is_helpful: true,
    course_id: 10,
    module_id: 25
  })
});

const feedbackData = await feedbackResponse.json();
console.log('Feedback submitted:', feedbackData.feedback.feedback_id);
```

---

## Security Best Practices

1. **API Key Management**
   - Never expose API keys in client-side code
   - Rotate API keys regularly
   - Use environment variables for key storage

2. **Input Validation**
   - All user inputs are sanitized
   - Max input length: 5,000 characters
   - Max context length: 10,000 characters

3. **Token Limits**
   - Premium: 100,000 tokens/day
   - Pro: 500,000 tokens/day
   - Automatic tracking and enforcement

4. **Rate Limiting**
   - 100 requests/hour for Premium
   - 500 requests/hour for Pro
   - 429 status code on limit exceeded

5. **Timeout Protection**
   - AI requests timeout after 55 seconds
   - Prevents hung connections

---

## Compliance

This API documentation complies with:
- **ISO/IEC/IEEE 26515:2018** - Developing user documentation
- **ISO 9001:2015** - Quality management systems
- **ISO 27001:2013** - Information security management
- **RESTful API Design** best practices

---

## Support

For API support or questions:
- Documentation: https://lernsystemx.de/docs
- Email: api-support@lernsystemx.de
- GitHub Issues: https://github.com/lernsystemx/backend/issues

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-16
**Maintained by:** LernsystemX Development Team
