# Media API - Quick Reference

**Last Updated:** 2026-01-08

---

## Quick Facts

- ✅ **DDD-Compliant** - Reference implementation
- ✅ **14 User Endpoints** - All authenticated with `@token_required`
- ✅ **2 Public Endpoints** - Info-only (no auth)
- ✅ **0 Admin Endpoints** - All functionality is user-facing
- ✅ **File Sizes OK** - Largest: 328 LOC (66% of limit)
- ✅ **Services Exist** - `TTSService`, `MediaCacheService`
- ✅ **Repository Pattern** - `TTSRepository` (direct SQL)

---

## Structure

```
media/
├── audio/          [STT Domain]
│   ├── processing.py   (261 LOC) - Upload → Whisper STT
│   └── streaming.py    (239 LOC) - Real-time analysis (LM24)
└── tts/            [TTS Domain]
    ├── synthesis.py    (328 LOC) - Audio generation
    ├── pronunciation.py (206 LOC) - Pronunciation CRUD + AI
    ├── tutor.py        (188 LOC) - Tutor integration
    ├── scripts.py      (157 LOC) - Multi-step scripts
    ├── helpers.py      (137 LOC) - Preprocessing
    ├── voices.py       (114 LOC) - Voice management
    └── config.py        (45 LOC) - Constants
```

---

## Endpoints at a Glance

### Audio (4 endpoints)

| URL | Method | Auth | Purpose |
|-----|--------|------|---------|
| `/audio/transcribe` | POST | User | Upload audio → STT |
| `/audio/transcribe-base64` | POST | User | Base64 audio → STT |
| `/audio/analyze-oral` | POST | User | LM24 oral analysis |
| `/audio/supported-formats` | GET | Public | List formats |

### TTS (11 endpoints)

| URL | Method | Auth | Purpose |
|-----|--------|------|---------|
| `/tts/speak` | POST | User | Generate TTS |
| `/tts/audio/<id>` | GET | User | Get cached audio |
| `/tts/speak-stream` | POST | User | Streaming TTS |
| `/tts/voices` | GET | Public | List voices |
| `/tts/tutor-script` | POST | User | Multi-step script |
| `/tutor/knowledge` | POST | User | Load tutor data |
| `/tutor/course/<id>/context` | GET | User | Course context |
| `/tutor/chapter/<id>/context` | GET | User | Chapter context |
| `/tts/pronunciations` | GET | Public | Get pronunciations |
| `/tts/pronunciations` | POST | User | Add pronunciation |
| `/tts/pronunciations/ai` | POST | User | AI pronunciation |

---

## Services

### TTSService

```python
from app.services.tts_service import TTSService

# Preprocess text for TTS
processed = TTSService.preprocess_text("35,67€", language='de')
# → "35 Komma 67 Euro"

# Add pronunciation
TTSService.add_pronunciation(word="Skonto", phonetic="Skonnto", language='de')

# AI-generate pronunciation
phonetic = await TTSService.generate_pronunciation_with_ai("Listeneinkaufspreis", "de")
```

### MediaCacheService

```python
from app.services.media_cache import TTSCacheService

# Cache TTS audio
TTSCacheService.cache_audio(audio_id, audio_bytes)

# Retrieve cached audio
audio = TTSCacheService.get_cached_audio(audio_id)
```

---

## Repository

### TTSRepository

```python
from app.repositories.tts.core import TTSRepository

# Get pronunciations
pronunciations = TTSRepository.get_all_pronunciations(language='de')

# Add pronunciation
TTSRepository.add_pronunciation(
    original_word='Skonto',
    phonetic_spelling='Skonnto',
    language='de',
    source='manual'
)

# Search
results = TTSRepository.search_pronunciations(query='preis', language='de')
```

---

## Configuration

### Voices (OpenAI)

| Voice | Gender | Style |
|-------|--------|-------|
| `nova` | Female | Natural (default) |
| `alloy` | Neutral | Balanced |
| `onyx` | Male | Deep |
| `echo` | Male | Clear |
| `fable` | Female | Expressive |
| `shimmer` | Female | Warm |

### Models

| Model | Quality | Speed | Use Case |
|-------|---------|-------|----------|
| `tts-1` | Standard | Fast | Real-time, development |
| `tts-1-hd` | High | Slower | Production, high quality |

### Limits

| Limit | Value | Notes |
|-------|-------|-------|
| Max Audio Size | 25 MB | OpenAI Whisper limit |
| Max Text Length | 4096 chars | TTS input limit |
| TTS Speed Range | 0.5 - 2.0 | Speed multiplier |

---

## Common Use Cases

### 1. Transcribe Audio (User)

```bash
curl -X POST https://api.lsx.de/api/v1/audio/transcribe \
  -H "Authorization: Bearer <token>" \
  -F "audio=@audio.mp3" \
  -F "language=de"
```

### 2. Generate TTS (User)

```bash
curl -X POST https://api.lsx.de/api/v1/tts/speak \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Willkommen beim LSX!",
    "voice": "nova",
    "speed": 1.0
  }'
```

### 3. Analyze Oral Explanation (LM24)

```bash
curl -X POST https://api.lsx.de/api/v1/audio/analyze-oral \
  -H "Authorization: Bearer <token>" \
  -F "audio=@explanation.mp3" \
  -F "topic=Photosynthese" \
  -F 'expected_points=["Chlorophyll", "Lichtenergie"]'
```

### 4. Get Available Voices (Public)

```bash
curl https://api.lsx.de/api/v1/tts/voices
```

---

## Response Format

### Success

```json
{
  "success": true,
  "data": {
    "text": "Transcribed text...",
    "language": "de",
    "duration": 5.2
  }
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "INVALID_FORMAT",
    "message": "Invalid audio format. Allowed: mp3, wav, webm, ..."
  }
}
```

---

## Error Codes

| Code | Meaning | HTTP Status |
|------|---------|-------------|
| `NO_AUDIO_FILE` | No audio file in request | 400 |
| `INVALID_FORMAT` | Unsupported audio format | 400 |
| `FILE_TOO_LARGE` | File exceeds 25 MB | 400 |
| `INVALID_BASE64` | Invalid base64 data | 400 |
| `TRANSCRIPTION_ERROR` | Whisper STT failed | 500 |
| `ANALYSIS_ERROR` | LM24 analysis failed | 500 |
| `NO_AUDIO_DATA` | No audio data provided | 400 |

---

## Dependencies

| Component | Type | Purpose |
|-----------|------|---------|
| OpenAI Whisper | External | Speech-to-Text |
| OpenAI TTS | External | Text-to-Speech |
| OpenAI GPT-4o-mini | External | Pronunciation AI |
| PostgreSQL | Database | Pronunciation storage |
| Redis | Cache | Media cache |

---

## Files by Size

| File | LOC | % of Limit |
|------|-----|------------|
| `synthesis.py` | 328 | 66% |
| `processing.py` | 261 | 52% |
| `streaming.py` | 239 | 48% |
| `pronunciation.py` | 206 | 41% |
| `tutor.py` | 188 | 38% |
| `scripts.py` | 157 | 31% |
| `helpers.py` | 137 | 27% |
| `voices.py` | 114 | 23% |

**All files well under 500 LOC limit.**

---

## Quality Gates

| Gate | Status |
|------|--------|
| G01 - No duplicates | ✅ PASS |
| G02 - Architecture | ✅ PASS |
| G04 - Complete files | ✅ PASS |
| G05 - Docstrings | ✅ PASS |
| G07 - Security | ✅ PASS |
| G09 - Performance | ✅ PASS |

---

## Next Steps

**If you need to:**
- Add new audio format → Update `ALLOWED_AUDIO_FORMATS` in `audio/processing.py`
- Add new TTS voice → Update `AVAILABLE_VOICES` in `tts/config.py`
- Add pronunciation → Use `POST /tts/pronunciations`
- Debug TTS issues → Check `services/tts_service.py` logging
- Optimize performance → Review `services/media_cache/`

---

## Documentation

- `README.md` - Full package documentation
- `REFACTORING_SUMMARY.md` - DDD analysis (detailed)
- `.claude/MEDIA_DOMAIN_ANALYSIS.md` - Complete analysis + rationale

---

**Version:** 1.0
**Status:** ✅ Production Ready
