# Lesson Video Service Package

Modular service for generating and caching lesson explanation videos using OpenAI Sora 2.

## Architecture Overview

### Module Structure

The service is organized into 7 focused modules, each with a single responsibility:

```
lesson_video/
├── __init__.py           # Package exports
├── exceptions.py         # Custom exceptions (8 LOC)
├── models.py             # Constants & config (73 LOC)
├── helpers.py            # Utility functions (178 LOC)
├── generation.py         # Sora API calls (161 LOC)
├── caching.py            # DB persistence (191 LOC)
├── status.py             # Status checking (71 LOC)
├── orchestration.py      # High-level coordination (295 LOC)
└── README.md             # This file
```

**Total: 1004 LOC** (vs 732 original) + documentation

### Module Responsibilities

| Module | Purpose | Exports |
|--------|---------|---------|
| **exceptions.py** | Custom exceptions | `VideoGenerationError` |
| **models.py** | Configuration constants | `SORA_MODELS`, `AVATAR_STYLES`, `SORA_API_URL` |
| **helpers.py** | Utility functions | `get_api_key()`, `generate_content_hash()`, `generate_video_prompt()`, `combine_teaching_steps()`, `estimate_video_duration()` |
| **generation.py** | Sora API interaction | `SoraVideoGenerator` class |
| **caching.py** | Database persistence | `VideoCache` class |
| **status.py** | Status tracking | `StatusChecker` class |
| **orchestration.py** | Main service facade | `LessonVideoService` class |

## Usage

### Basic Usage (Preferred)

```python
from app.services.lesson_video import LessonVideoService

# Generate lesson video
video = await LessonVideoService.generate_lesson_video(
    lesson_id="uuid-string",
    lesson_title="Bezugskalkulation",
    teaching_steps=[
        {
            "speech": "Today we learn about pricing...",
            "whiteboard": [
                {"type": "write", "content": "Price = Cost + Margin"}
            ]
        }
    ],
    avatar_style="professional_teacher",
    model="sora-2"
)

# Get cached video (no regeneration)
cached = LessonVideoService.get_cached_video(lesson_id)

# Get generation status
status = LessonVideoService.get_generation_status(lesson_id)

# Delete cached video
deleted = LessonVideoService.delete_cached_video(lesson_id)
```

### Legacy Usage (Deprecated)

```python
# Still works, but shows deprecation warning
from app.services.lesson_video_service import LessonVideoService
```

## API Reference

### LessonVideoService (orchestration.py)

Main facade providing all public methods.

#### `generate_lesson_video()`

```python
async def generate_lesson_video(
    lesson_id: str,
    lesson_title: str,
    teaching_steps: List[Dict[str, Any]],
    avatar_style: str = 'professional_teacher',
    model: str = 'sora-2',
    force_regenerate: bool = False,
    language: str = 'de'
) -> Dict[str, Any]
```

**Args:**
- `lesson_id`: UUID of the lesson
- `lesson_title`: Display title
- `teaching_steps`: List of steps with `speech` and `whiteboard` keys
- `avatar_style`: One of `professional_teacher`, `female_instructor`, `casual_tutor`, `animated_expert`
- `model`: `sora-2` (faster, cheaper) or `sora-2-pro` (higher quality)
- `force_regenerate`: Skip cache and regenerate
- `language`: Language code (default: `de` for German)

**Returns:**
```python
{
    'video_id': str,           # Unique video identifier
    'video_url': str,          # URL to video file (includes audio)
    'duration_ms': int,        # Duration in milliseconds
    'model': str,              # Sora model used
    'from_cache': bool,        # Whether from cache
    'cost': float,             # Token cost
    'status': str,             # 'ready', 'api_error', 'timeout', etc.
    'has_audio': True          # Sora 2 always includes audio
}
```

#### `get_cached_video()`

```python
@classmethod
def get_cached_video(cls, lesson_id: str, model: str = None) -> Dict[str, Any]
```

Returns cached video if available, updates access count.

#### `cache_video()`

```python
@classmethod
def cache_video(cls, lesson_id: str, video_path: str, metadata: Dict[str, Any]) -> str
```

Stores video in `agent_media_cache` and `agent_video_cache` tables.

#### `delete_cached_video()`

```python
@classmethod
def delete_cached_video(cls, lesson_id: str, model: str = None) -> bool
```

Removes cached video for lesson (optionally filtered by model).

#### `get_generation_status()`

```python
@classmethod
def get_generation_status(cls, lesson_id: str) -> Dict[str, Any]
```

Returns current status without regeneration.

#### `get_available_models()`

```python
@classmethod
def get_available_models(cls) -> Dict[str, Any]
```

Lists all available Sora models with specifications.

#### `compare_models()`

```python
@classmethod
def compare_models(cls) -> Dict[str, Any]
```

Provides comparison info for UI selection.

#### `generate_video_prompt()`

```python
@classmethod
def generate_video_prompt(
    cls,
    lesson_title: str,
    speech_text: str,
    whiteboard_content: str,
    avatar_style: str = 'professional_teacher',
    language: str = 'de'
) -> str
```

Generates structured prompt for Sora 2 API.

#### `generate_sora_video()` (async)

```python
@classmethod
async def generate_sora_video(
    cls,
    prompt: str,
    duration_seconds: int = 15,
    resolution: str = None,
    model: str = 'sora-2'
) -> Dict[str, Any]
```

Low-level API call to Sora 2 service.

## Helper Functions

### helpers.py

**`get_api_key() -> str`**
- Retrieves OpenAI API key from env or database

**`generate_content_hash(lesson_id, teaching_steps, avatar_style, model) -> str`**
- Creates SHA256 hash for cache deduplication

**`generate_video_prompt(...) -> str`**
- Creates Sora 2 prompt with avatar styling and speech instructions

**`combine_teaching_steps(teaching_steps) -> (str, str)`**
- Merges all steps into unified speech and whiteboard content

**`estimate_video_duration(speech_text, model) -> int`**
- Calculates duration based on word count (~150 words/min)

## Data Models

### SORA_MODELS (models.py)

```python
{
    'sora-2': {
        'name': 'Sora 2',
        'performance': 'higher',
        'speed': 'slow',
        'cost_per_second': 0.10,
        'max_duration': 60
    },
    'sora-2-pro': {
        'name': 'Sora 2 Pro',
        'performance': 'highest',
        'speed': 'slower',
        'cost_per_second': 0.20,
        'max_duration': 120
    }
}
```

### AVATAR_STYLES (models.py)

Four preset avatars:
- `professional_teacher`: Male teacher in classroom
- `female_instructor`: Female instructor with modern setup
- `casual_tutor`: Young peer-style tutor
- `animated_expert`: Pixar-style animated character

Each includes:
- `name`: Display name
- `description`: Visual scene description
- `voice_style`: Speech characteristics
- `gestures`: Typical movements
- `expression`: Facial expression style

## Database Integration

### Tables Used

**agent_media_cache**
- Stores media files with metadata
- Fields: media_id, content_hash, source_id, storage_path, generation_model, status, etc.

**agent_video_cache**
- Video-specific metadata
- Fields: video_id, media_id, avatar_id, resolution, framerate, etc.

## Error Handling

### VideoGenerationError

Raised when video caching fails. Network errors and API timeouts return status fields instead.

### Status Codes

- `'ready'`: Successfully generated
- `'api_error'`: API returned error
- `'timeout'`: Generation exceeded 10-minute timeout
- `'api_not_available'`: API endpoint not reachable (fallback mode)

## Migration Guide

### From Monolithic to Package

Old code:
```python
from app.services.lesson_video_service import LessonVideoService
video = await LessonVideoService.generate_lesson_video(...)
```

No changes needed! Bridge module ensures backward compatibility with deprecation warning.

### Recommended Migration

Update imports for clarity:
```python
from app.services.lesson_video import LessonVideoService
video = await LessonVideoService.generate_lesson_video(...)
```

## Performance Notes

- **Caching**: Queries `agent_media_cache` first, avoids regeneration
- **Access tracking**: Updates `access_count` and `last_accessed_at` on cache hits
- **Duration estimation**: ~150 words per minute (adjustable in helpers.py)
- **Model limits**: sora-2 (max 60s), sora-2-pro (max 120s)

## Testing

### Unit Tests

Test modules independently:
```bash
pytest tests/test_lesson_video_generation.py
pytest tests/test_lesson_video_caching.py
pytest tests/test_lesson_video_status.py
```

### Integration Tests

Test full orchestration:
```bash
pytest tests/test_lesson_video_service.py
```

### Mock API Testing

When Sora API unavailable:
- Status returns `'api_not_available'`
- No exception thrown
- Fallback rendering suggested

## Quality Gates (G01-G10)

✓ **G01 - No Duplicates**: Single source of truth (orchestration.py as facade)
✓ **G02 - Consistency**: Repository pattern for DB access, async for API
✓ **G03 - Versioning**: All changes tied to deployment
✓ **G04 - Completeness**: No code fragments, full file exports
✓ **G05 - Documentation**: Full docstrings, type hints throughout
✓ **G06 - Quality**: Error handling, validation in place
✓ **G07 - Security**: No hardcoded secrets, parameterized queries
✓ **G08 - Transparency**: Each module single-responsibility
✓ **G09 - Performance**: Caching, efficient queries
✓ **G10 - Accessibility**: N/A (backend service)

## Future Enhancements

1. **Async Caching**: Use Redis for status polling
2. **Batch Generation**: Queue multiple videos
3. **Streaming**: Return chunks as generation completes
4. **Model Auto-Selection**: Based on lesson complexity
5. **Alternative Providers**: Support additional video APIs

## Related Documentation

- `CLAUDE.md` - LessonVideo service overview
- `17_Backend-Struktur.md` - Backend service patterns
- `02_Lernmethoden.md` - Learning method system
