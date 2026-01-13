# Media API Package

**Domain:** Audio Processing & Text-to-Speech
**Status:** ✅ DDD-Compliant - Reference Implementation
**Last Updated:** 2026-01-08

---

## Overview

The media package provides audio processing and text-to-speech functionality for the LSX platform. This package is organized by **functional domains** (audio, tts) and serves as a **reference implementation** for DDD-compliant API structure.

---

## Package Structure

```
media/
├── __init__.py                    # Blueprint registration
├── README.md                      # This file
├── REFACTORING_SUMMARY.md         # DDD analysis (detailed)
│
├── audio/                         [Speech-to-Text Domain]
│   ├── __init__.py                # Package exports
│   ├── processing.py              # File/base64 upload → Whisper STT
│   └── streaming.py               # Real-time analysis (LM24 oral explanation)
│
└── tts/                           [Text-to-Speech Domain]
    ├── __init__.py                # Package exports + config
    ├── config.py                  # Voice definitions, constants
    ├── helpers.py                 # Text preprocessing utilities
    ├── synthesis.py               # Audio generation (OpenAI TTS)
    ├── voices.py                  # Voice/model management
    ├── scripts.py                 # Multi-step tutor scripts
    ├── tutor.py                   # Tutor knowledge integration
    └── pronunciation.py           # Pronunciation rules (CRUD + AI)
```

---

## Endpoints

### Audio (Speech-to-Text)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| `POST` | `/api/v1/audio/transcribe` | User | Upload audio file for STT |
| `POST` | `/api/v1/audio/transcribe-base64` | User | Base64-encoded audio for STT |
| `POST` | `/api/v1/audio/analyze-oral` | User | Analyze oral explanation (LM24) |
| `GET` | `/api/v1/audio/supported-formats` | Public | List supported audio formats |

**Supported Formats:** mp3, mp4, mpeg, mpga, m4a, wav, webm, ogg, flac
**Max File Size:** 25 MB (OpenAI Whisper limit)

### TTS (Text-to-Speech)

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| `POST` | `/api/v1/tts/speak` | User | Generate TTS audio (cached) |
| `GET` | `/api/v1/tts/audio/<id>` | User | Retrieve cached TTS audio |
| `POST` | `/api/v1/tts/speak-stream` | User | Streaming TTS audio |
| `GET` | `/api/v1/tts/voices` | Public | List available voices/models |
| `POST` | `/api/v1/tts/tutor-script` | User | Generate multi-step tutor script |
| `POST` | `/api/v1/tutor/knowledge` | User | Load tutor knowledge (course/chapter) |
| `GET` | `/api/v1/tutor/course/<id>/context` | User | Get course context for tutor |
| `GET` | `/api/v1/tutor/chapter/<id>/context` | User | Get chapter context for tutor |
| `GET` | `/api/v1/tts/pronunciations` | Public | Get pronunciation rules |
| `POST` | `/api/v1/tts/pronunciations` | User | Add pronunciation rule |
| `POST` | `/api/v1/tts/pronunciations/ai` | User | AI-generate pronunciation |

**Available Voices (OpenAI):** alloy, echo, fable, onyx, nova, shimmer
**Default Voice:** nova
**TTS Models:** tts-1 (fast), tts-1-hd (high quality)

---

## Services

### TTSService (`app.services.tts_service`)

Business logic for Text-to-Speech with intelligent pronunciation:

```python
from app.services.tts_service import TTSService

# Load pronunciations from database
pronunciations = TTSService.load_pronunciations(language='de')

# Preprocess text for better TTS quality
processed_text = TTSService.preprocess_text(
    text="Der Listeneinkaufspreis beträgt 35,67€",
    language='de'
)
# → "Der Listen Einkaufs Preis beträgt 35 Komma 67 Euro"

# Add custom pronunciation
TTSService.add_pronunciation(
    word="Skonto",
    phonetic="Skonnto",
    language='de'
)

# AI-generate pronunciation for unknown word
phonetic = await TTSService.generate_pronunciation_with_ai(
    word="Listeneinkaufspreis",
    language='de'
)
```

**Features:**
- ✅ Pronunciation corrections from database
- ✅ AI-generated pronunciations for unknown words
- ✅ Pattern replacements (numbers, decimals, symbols)
- ✅ In-memory caching for performance
- ✅ Async AI processing queue

### MediaCacheService (`app.services.media_cache`)

Media caching services:
- `MediaCacheService` - Base cache service
- `TTSCacheService` - TTS audio caching
- `TranscriptCacheService` - Transcription caching
- `SessionCacheService` - Session caching

---

## Repositories

### TTSRepository (`app.repositories.tts.core`)

Database access for TTS-related data:

```python
from app.repositories.tts.core import TTSRepository

# Pronunciations
pronunciations = TTSRepository.get_all_pronunciations(language='de')
TTSRepository.add_pronunciation(
    original_word='Skonto',
    phonetic_spelling='Skonnto',
    language='de',
    source='manual'
)

# AI Requests
TTSRepository.add_ai_request(word='Listeneinkaufspreis', language='de')
pending = TTSRepository.get_pending_ai_requests(limit=10)

# Search
results = TTSRepository.search_pronunciations(query='preis', language='de', limit=50)
```

**Pattern:** Direct SQL via `BaseRepository` (no ORM)

---

## Usage Examples

### 1. Transcribe Audio (Frontend)

```typescript
import { mediaApi } from '@/api/media.api'

// Upload audio file
const formData = new FormData()
formData.append('audio', audioFile)
formData.append('language', 'de')

const result = await mediaApi.transcribeAudio(formData)
console.log(result.data.text) // Transcribed text
```

### 2. Generate TTS Audio (Frontend)

```typescript
import { ttsApi } from '@/api/tts.api'

// Generate TTS
const result = await ttsApi.speak({
  text: "Willkommen beim LSX!",
  voice: "nova",
  speed: 1.0,
  language: "de"
})

// Audio URL
const audioUrl = result.data.audio_url // /api/v1/tts/audio/abc123
```

### 3. Analyze Oral Explanation (LM24)

```typescript
import { mediaApi } from '@/api/media.api'

const formData = new FormData()
formData.append('audio', audioFile)
formData.append('topic', 'Photosynthese')
formData.append('expected_points', JSON.stringify([
  'Chlorophyll',
  'Lichtenergie',
  'Sauerstoff'
]))

const result = await mediaApi.analyzeOralExplanation(formData)

console.log(result.data.transcription) // Transcribed text
console.log(result.data.analysis.score) // 85 (0-100)
console.log(result.data.analysis.feedback) // "Gute Erklärung..."
console.log(result.data.analysis.covered_points) // ["Chlorophyll", ...]
console.log(result.data.analysis.missing_points) // ["Sauerstoff"]
```

### 4. Preprocessing Text for TTS (Backend)

```python
from app.services.tts_service import TTSService

# Automatically load pronunciations and preprocess
text = "Der Listeneinkaufspreis beträgt 35,67€"
processed = TTSService.preprocess_text(text, language='de')
# → "Der Listen Einkaufs Preis beträgt 35 Komma 67 Euro"

# Generate TTS with AIAdapter
from app.services.ai_adapter import AIAdapter

audio_bytes = AIAdapter.text_to_speech(
    text=processed,
    voice='nova',
    model='tts-1',
    speed=1.0
)
```

---

## Dependencies

### External Services

| Service | Purpose | Endpoint |
|---------|---------|----------|
| OpenAI Whisper | Speech-to-Text | `AIAdapter.transcribe_audio()` |
| OpenAI TTS | Text-to-Speech | `AIAdapter.text_to_speech()` |
| OpenAI GPT-4 | Oral explanation analysis | `AIAdapter.chat_completion()` |
| OpenAI GPT-4o-mini | Pronunciation generation | `AIAdapter.generate_content_async()` |

### Database Tables

```sql
-- Pronunciations
tts.pronunciations (
    pronunciation_id,
    original_word,
    phonetic_spelling,
    language,
    category,
    word_type,
    source,
    ai_model,
    confidence,
    is_verified
)

-- AI Pronunciation Requests
tts.ai_pronunciation_requests (
    request_id,
    word,
    language,
    context,
    status,
    suggested_spelling,
    pronunciation_id
)
```

---

## Configuration

### Environment Variables

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Media Cache Path
MEDIA_CACHE_PATH=/path/to/backend/storage/media_cache

# Max Audio File Size (bytes)
MAX_AUDIO_SIZE=26214400  # 25 MB
```

### Constants (`tts/config.py`)

```python
# Available TTS voices
AVAILABLE_VOICES = {
    'openai': {
        'alloy': {'name': 'Alloy', 'gender': 'neutral', ...},
        'echo': {'name': 'Echo', 'gender': 'male', ...},
        'fable': {'name': 'Fable', 'gender': 'female', ...},
        'onyx': {'name': 'Onyx', 'gender': 'male', ...},
        'nova': {'name': 'Nova', 'gender': 'female', ...},
        'shimmer': {'name': 'Shimmer', 'gender': 'female', ...},
    }
}

# Defaults
DEFAULT_TUTOR_VOICE = 'nova'
DEFAULT_PROVIDER = 'openai'
DEFAULT_MODEL = 'tts-1'

# Limits
MAX_TEXT_LENGTH = 4096
MIN_SPEED = 0.5
MAX_SPEED = 2.0
```

---

## File Size Statistics

```
Line Count by File:
─────────────────────────────────────
synthesis.py              328 LOC  ← Largest (66% of limit)
processing.py             261 LOC
streaming.py              239 LOC
pronunciation.py          206 LOC
tutor.py                  188 LOC
scripts.py                157 LOC
helpers.py                137 LOC
voices.py                 114 LOC
tts/__init__.py            62 LOC
config.py                  45 LOC
media/__init__.py          47 LOC
audio/__init__.py          23 LOC
─────────────────────────────────────
Total:                  1,807 LOC

Average File Size: 151 LOC
Largest File: 328 LOC (well under 500 LOC limit)
```

---

## Quality Gates

| Gate | Rule | Status |
|------|------|--------|
| **G01** | No duplicates (.old, .bak, _v2) | ✅ PASS |
| **G02** | LSX architecture followed | ✅ PASS |
| **G04** | Complete files (no fragments) | ✅ PASS |
| **G05** | Docstrings + Type hints | ✅ PASS |
| **G07** | OWASP-compliant, no secrets | ✅ PASS |
| **G09** | Performance (caching implemented) | ✅ PASS |

---

## DDD Compliance

✅ **Domain Separation:** `audio/` (STT) and `tts/` (TTS) are clear functional sub-domains
✅ **Role-Based:** User endpoints authenticated, public endpoints info-only
✅ **Service Layer:** `TTSService` handles business logic
✅ **Repository Pattern:** `TTSRepository` for database access
✅ **File Size Limits:** All files < 500 LOC
✅ **Type Safety:** Type hints everywhere
✅ **Documentation:** All endpoints documented

**This package serves as a reference implementation for DDD-compliant API structure.**

---

## Migration Notes

**Refactored:** 2026-01-07 (TTS), 2026-01-08 (Audio + Analysis)

**Before:**
```
api/audio.py              (460 LOC) → audio/processing.py + audio/streaming.py
api/tts.py                (993 LOC) → tts/ package (7 modules)
```

**After:**
```
api/media/
├── audio/                (2 modules, 500 LOC)
└── tts/                  (7 modules, 1,307 LOC)
```

**Breaking Changes:** NONE - All URLs remain unchanged

---

## Future Considerations (Low Priority)

### Optional: AudioService

If audio processing grows beyond STT:

```python
# services/media/audio.py
class AudioService:
    def validate_audio_file(file) -> bool
    def convert_audio_format(path, target) -> str
    def extract_metadata(path) -> dict
```

**Benefit:** Centralize audio validation and processing logic.
**Priority:** LOW - Current duplication is minimal.

### Optional: Public Sub-Package

If many public endpoints are added:

```python
# media/public/__init__.py
@public_bp.route('/formats', methods=['GET'])
def get_all_supported_formats():
    """Combined audio + TTS format info"""
    pass
```

**Priority:** VERY LOW - Only 2 public endpoints currently.

---

## Related Documentation

- `.claude/MEDIA_DOMAIN_ANALYSIS.md` - Full DDD analysis
- `REFACTORING_SUMMARY.md` - Detailed refactoring summary
- `LernsystemX-Doku/05_Technical/05_Backend-Struktur.md` - Backend architecture
- `LernsystemX-Doku/07_Setup-Dev/03_Developer-Guide-KI.md` - Quality Gates

---

## Support

For issues or questions:
1. Check `REFACTORING_SUMMARY.md` for detailed analysis
2. Review service/repository implementations
3. Consult `.claude/MEDIA_DOMAIN_ANALYSIS.md` for DDD rationale

---

**Version:** 1.0
**Status:** ✅ Production Ready - Reference Implementation
**Maintainer:** LSX Backend Team
