# Web Research System

**Version:** 1.0
**Stand:** März 2026
**Status:** Phase 1 in Entwicklung

---

## Überblick

Das **Web Research System** liefert echte, quellenbasierte Lerninhalte für Curriculum-Positionen ohne reale Prüfungsfragen (Gap-Positionen). Es nutzt **Google Search via Gemini Grounding** statt reiner KI-Halluzination und speichert alle Quellen transparent im Kurs.

### Kernziele

- **Echte Quellen** -- Google Search statt KI-Wissen, mit prüfbaren URLs
- **IHK-Qualität** -- Offizielle Quellen (ihk.de, IT-Handbuch) bevorzugt
- **Transparenz** -- Jedes Kapitel zeigt Grounding-Status und Quellen
- **Kosteneffizienz** -- Redis Cache + PDF Cache vermeiden wiederholte API-Calls
- **Fehler sichtbar** -- Kein stiller Fallback auf AI-Knowledge bei Grounding-Fehler

### Warum Web Research?

Der Prüfungskurs-Generator erstellt Kapitel aus echten IHK-Prüfungsfragen. Für Curriculum-Positionen **ohne** Prüfungsfragen (Gap-Positionen) muss Content KI-generiert werden. Ohne Web Research basiert dieser Content auf reinem KI-Wissen -- unzuverlässig und ohne Quellenangaben. Bei 1-2 EUR pro generiertem Kurs muss die Qualität stimmen.

---

## Architektur

### DDD-Layer-Zuordnung

```
app/
├── api/v1/panel/admin/exams/
│   └── course_generator.py              # API -- triggert Generierung
├── application/services/exams/
│   ├── course_generator_builder.py      # Orchestriert Gap Content Enrichment
│   └── gap_content_service.py           # Application Service -- koordiniert Research
├── domain/services/
│   └── (keine -- Web Research ist Infrastructure)
└── infrastructure/
    ├── web_research/
    │   ├── __init__.py
    │   ├── search_service.py            # Gemini Grounding Integration
    │   ├── pdf_scraper.py               # IHK PDF Extraktion
    │   └── source_scorer.py             # Quellen-Qualitätsbewertung
    ├── persistence/repositories/
    │   └── web_research/
    │       └── research_cache.py        # DB Cache Repository
    └── cache/
        └── service.py                   # Redis Cache (existiert)
```

### Datenfluss

```
Kurs-Generierung
  → _enrich_ai_plan_with_gap_content()           [Builder]
    → GapContentService.generate_gap_content()    [Application]
      → CurriculumFrameworkRepository             [Lernziele laden]
      → ResearchCacheRepository.find_cached()     [Cache prüfen]
      ┌─ Cache Hit → return cached_result
      └─ Cache Miss:
         → WebSearchService.search_with_grounding()  [Infrastructure]
           → Multi-Query Strategie (3 Queries)
           → Gemini API mit google_search Tool
           → Source Scoring (Quellen bewerten)
           → Quellen-URLs extrahieren
         → PDFScraperService.extract_ihk_content()   [Optional]
         → ResearchCacheRepository.save()             [Cache speichern]
      → return {summary, key_points, sources, grounding_status}
    → plan_data['gap_research_context'] = result
    → ai_metadata['grounding_status'] = 'success' | 'failed'
```

---

## Features

### Phase 1: Gemini Grounding + Qualität (aktuell)

#### 1. Google Search via Gemini Grounding

Statt reinem AI-Wissen nutzt der Service **Gemini mit google_search Tool**. Die API sucht in Echtzeit bei Google und fasst die Ergebnisse zusammen -- mit echten Quellen.

```python
# Infrastructure: search_service.py
class WebSearchService:
    @staticmethod
    def search_with_grounding(
        queries: List[str],
        context: str,
        language: str = 'de',
    ) -> Dict[str, Any]:
        """
        Gemini Grounding: Google Search + AI Summary.
        Returns summary with real source URLs.
        Raises WebResearchError on failure (NO silent fallback).
        """
```

**API-Call Struktur:**
```python
# Gemini mit google_search Tool
response = genai.GenerativeModel('gemini-2.0-flash').generate_content(
    contents=prompt,
    tools=[{'google_search': {}}],
    generation_config={'temperature': 0.2},
)

# Grounding-Metadaten enthalten echte URLs
grounding_metadata = response.candidates[0].grounding_metadata
sources = grounding_metadata.grounding_chunks  # URLs + Titel
```

#### 2. Multi-Query Strategie

Pro Gap-Position werden **3 gezielte Queries** gesendet statt einer generischen:

| Query | Beispiel | Ziel |
|-------|----------|------|
| **Theorie** | `"IHK Fachinformatiker Netzwerktechnik Grundlagen"` | Theoretisches Wissen |
| **Praxis** | `"Netzwerktechnik praktische Aufgaben Beispiele IT-Ausbildung"` | Anwendungswissen |
| **Prüfung** | `"IHK Abschlussprüfung Netzwerktechnik Aufgabentypen"` | Prüfungsrelevanz |

```python
def _build_queries(position_title: str, objectives: List[str], language: str) -> List[str]:
    """3 gezielte Queries pro Position."""
    base = f"IHK Fachinformatiker {position_title}"
    return [
        f"{base} Grundlagen Theorie",
        f"{position_title} praktische Aufgaben Beispiele IT-Ausbildung",
        f"IHK Abschlussprüfung {position_title} Aufgabentypen",
    ]
```

#### 3. Quellen-Scoring

Nicht alle Quellen sind gleich. Offizielle IHK-Quellen wiegen schwerer als random Blogs:

| Domain | Score-Multiplikator | Grund |
|--------|-------------------|-------|
| `ihk.de`, `ihk-*.de` | 1.5x | Offizielle IHK-Quelle |
| `it-handbuch.de` | 1.4x | Referenzwerk IT-Berufe |
| `fachinformatiker.de` | 1.3x | Fach-Community |
| `bundesregierung.de`, `gesetze-im-internet.de` | 1.3x | Offizielle Rechtsquellen |
| `*.edu`, `*.ac.*` | 1.2x | Akademische Quellen |
| Wikipedia | 1.1x | Solide Basis, nicht spezialisiert |
| Andere | 1.0x | Standard |

```python
# Infrastructure: source_scorer.py
DOMAIN_SCORES = {
    'ihk.de': 1.5,
    'it-handbuch.de': 1.4,
    'fachinformatiker.de': 1.3,
    # ...
}

def score_source(url: str) -> float:
    """Score a source URL by domain authority."""
    domain = extract_domain(url)
    for pattern, score in DOMAIN_SCORES.items():
        if pattern in domain:
            return score
    return 1.0
```

#### 4. Quellen-URLs transparent speichern

Jedes Gap-Kapitel speichert seine Quellen in `ai_metadata`:

```json
{
  "coverage_source": "ai_generated",
  "grounding_status": "success",
  "intelligence_score": 0.72,
  "research_sources": [
    {
      "url": "https://www.ihk.de/fachinformatiker/netzwerktechnik",
      "title": "Netzwerktechnik - IHK",
      "domain_score": 1.5
    },
    {
      "url": "https://it-handbuch.de/netzwerke/osi-modell",
      "title": "OSI-Modell Grundlagen",
      "domain_score": 1.4
    }
  ],
  "research_cached": false,
  "research_generated_at": "2026-03-11T14:30:00Z"
}
```

#### 5. Redis Cache für Research-Ergebnisse

Gleiche Position = gleicher Content. Kein erneuter API-Call nötig.

```python
# Cache-Key Schema
CACHE_KEY = "CACHE:RESEARCH:POS:{position_id}:LANG:{language}"

# TTL: 7 Tage (Curriculum ändert sich selten)
TTL_SECONDS = 7 * 24 * 3600

# Invalidierung: Manuell via Admin oder bei Curriculum-Update
```

**Bestehende Infrastruktur:**
- `CacheService` (`app/infrastructure/cache/service.py`) -- Redis-Wrapper existiert
- `storage.pdf_cache` Tabelle -- PDF-Extraktion existiert (Migration 031)

#### 6. Parallel Execution

15+ Gap-Positionen sequentiell = langsam. Mit ThreadPoolExecutor parallel:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def research_all_gaps(gaps: List[Dict], language: str) -> List[Dict]:
    """Research all gap positions in parallel."""
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(_research_single_gap, gap, language): gap
            for gap in gaps
        }
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return results
```

#### 7. Sprach-Split (DE/EN)

IHK-Recht und BWL → Deutsch suchen (beste Quellen auf Deutsch).
Tech-Topics (Docker, Kubernetes, Python) → Englisch suchen (beste Quellen auf Englisch).

```python
# Heuristik: Tech-Keywords → englische Suche
TECH_KEYWORDS = {
    'docker', 'kubernetes', 'python', 'java', 'linux', 'git',
    'sql', 'html', 'css', 'javascript', 'api', 'rest', 'tcp',
    'http', 'dns', 'dhcp', 'cloud', 'devops', 'agile', 'scrum',
}

def detect_search_language(position_title: str) -> str:
    """Detect optimal search language based on topic."""
    title_lower = position_title.lower()
    tech_matches = sum(1 for kw in TECH_KEYWORDS if kw in title_lower)
    return 'en' if tech_matches >= 2 else 'de'
```

#### 8. Grounding-Status + Failure-Transparenz

**Kein stiller Fallback.** Wenn Grounding fehlschlägt:

```python
class WebResearchError(Exception):
    """Raised when Gemini Grounding fails. NOT silently caught."""
    pass

# Im Builder:
try:
    result = GapContentService.generate_gap_content(...)
    ai_metadata['grounding_status'] = 'success'
    ai_metadata['research_sources'] = result.get('sources', [])
except WebResearchError:
    ai_metadata['grounding_status'] = 'failed'
    ai_metadata['grounding_error'] = str(e)
    logger.error("Grounding FAILED for position %s", position_id)
    # Chapter wird trotzdem erstellt, aber als "failed" markiert
    # Admin sieht im Dashboard welche Kapitel keine Quellen haben
```

**Frontend/Admin sieht:**
- `grounding_status: "success"` → Grünes Badge
- `grounding_status: "failed"` → Rotes Badge mit Warnung

---

### Phase 2: IHK PDF-Scraping + Crawler (geplant)

#### PDF-Scraping

IHK veröffentlicht die wertvollsten Dokumente als PDFs:
- Rahmenlehrpläne
- Prüfungsordnungen
- Musteraufgaben
- Handreichungen

Diese PDFs werden heruntergeladen, extrahiert und in `storage.pdf_cache` gespeichert.

```python
# Infrastructure: pdf_scraper.py
class PDFScraperService:
    """Download and extract IHK PDFs into pdf_cache."""

    KNOWN_SOURCES = [
        'https://www.bibb.de/dienst/berufesuche/',
        'https://www.ihk.de/fachinformatiker/',
    ]

    @staticmethod
    def scrape_and_cache(url: str) -> Dict[str, Any]:
        """Download PDF, extract text, store in pdf_cache."""
        # 1. Download
        # 2. Hash für Dedup (file_hash in pdf_cache)
        # 3. Extraktion mit pdfplumber
        # 4. Struktur-Analyse (Kapitel, Überschriften)
        # 5. Speichern in storage.pdf_cache
```

**Bestehende DB-Tabelle** (`storage.pdf_cache`):
```sql
CREATE TABLE storage.pdf_cache (
    cache_id UUID PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 Dedup
    original_filename VARCHAR(255),
    extracted_text TEXT,
    extracted_metadata JSONB,
    structure_analysis JSONB,               -- KI-analysierte Struktur
    extraction_method VARCHAR(50),          -- pdfplumber
    access_count INTEGER DEFAULT 0,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### Targeted Crawler

Kein generischer Crawler, sondern gezielt für 3-5 Domains:

| Domain | Content-Typ | Crawl-Frequenz |
|--------|------------|----------------|
| `ihk.de` | Prüfungsinfos, Rahmenlehrpläne | Monatlich |
| `it-handbuch.de` | IT-Grundlagen, Referenz | Monatlich |
| `fachinformatiker.de` | Forum, Erfahrungsberichte | Wöchentlich |
| `bibb.de` | Ausbildungsordnungen | Quartalsweise |

**Kostenvorteil:**
- Ohne Crawler: ~$0.05-0.10 pro Position pro Grounding-Call
- Mit Crawler + lokalem Index: $0.00 für bekannte Inhalte
- Bei 20 Positionen x 1000 Kurse = $1000-2000 gespart

**Crawl-Job:** Celery Periodic Task, läuft nachts.

---

### Phase 3: ML Source Ranking (Zukunft)

Wenn genügend Nutzerdaten vorhanden sind (welche Quellen führen zu besseren Lernergebnissen):

- Feedback-Loop: Nutzer bewertet generierte Kapitel
- Korrelation: Welche Quellen-Domains → bessere Bewertungen?
- Modell: Einfache logistische Regression, kein Deep Learning nötig
- Input: Domain, Content-Länge, Aktualität, Thema
- Output: Quality Score 0.0-1.0

**Voraussetzung:** Genügend Kurs-Generierungen mit Feedback (>500).

---

## Datenmodell

### Neue Tabelle: web_research_cache

```sql
CREATE TABLE IF NOT EXISTS ai_pipeline.web_research_cache (
    cache_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identifikation
    position_id INTEGER NOT NULL,
    language VARCHAR(5) NOT NULL DEFAULT 'de',
    cache_key VARCHAR(255) NOT NULL UNIQUE,

    -- Research-Ergebnis
    summary TEXT NOT NULL,
    key_points JSONB DEFAULT '[]',
    difficulty_level VARCHAR(20),
    recommended_study_time_minutes INTEGER,

    -- Quellen
    sources JSONB DEFAULT '[]',
    -- Format: [{"url": "...", "title": "...", "domain_score": 1.5}, ...]
    grounding_status VARCHAR(20) NOT NULL DEFAULT 'success',
    -- "success" | "partial" | "failed"

    -- Queries
    queries_used JSONB DEFAULT '[]',
    search_language VARCHAR(5),

    -- Cache-Management
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT chk_grounding_status CHECK (
        grounding_status IN ('success', 'partial', 'failed')
    )
);

CREATE INDEX idx_research_cache_position
    ON ai_pipeline.web_research_cache(position_id, language);
CREATE INDEX idx_research_cache_expires
    ON ai_pipeline.web_research_cache(expires_at)
    WHERE expires_at IS NOT NULL;
```

### Bestehende Tabelle: pdf_cache (Migration 031)

Bereits vorhanden in `storage` Schema. Wird für PDF-Scraping genutzt.

### ai_metadata Erweiterung (chapters Tabelle)

Kein Schema-Change nötig -- `ai_metadata` ist JSONB:

```json
{
  "coverage_source": "ai_generated",
  "intelligence_score": 0.72,
  "relevance_score": 0.85,
  "prognosis_probability": 0.60,
  "grounding_status": "success",
  "research_sources": [...],
  "research_cached": true,
  "research_generated_at": "2026-03-11T14:30:00Z"
}
```

---

## Kosten

### API-Kosten pro Kursgeneration

| Komponente | Kosten (ohne Cache) | Kosten (mit Cache) |
|-----------|---------------------|---------------------|
| Gemini Grounding (pro Query) | ~$0.01-0.02 | $0.00 (cached) |
| 3 Queries x 15 Gap-Positionen | ~$0.45-0.90 | $0.00-0.10 |
| PDF-Scraping (einmalig) | ~$0.00 | $0.00 |
| **Gesamt pro Kurs** | **~$0.50-1.00** | **~$0.00-0.10** |

### Cache Hit Rate (erwartet)

- Woche 1: ~0% (Cold Start)
- Woche 2-4: ~60-70% (gleiche Positionen, verschiedene User)
- Monat 2+: ~85-95% (Curriculum ändert sich selten)

---

## Fehlerbehandlung

### Kein stiller Fallback

| Fehler | Aktion | Sichtbarkeit |
|--------|--------|-------------|
| Gemini API down | `WebResearchError` → Chapter als `grounding_status: "failed"` markiert | Admin Dashboard |
| Google Search liefert 0 Ergebnisse | `grounding_status: "partial"` + AI-Only Fallback **mit Warnung** | Admin Dashboard |
| PDF Download fehlschlägt | Log + Skip (nicht blockierend für Kurs) | Log |
| Redis Cache nicht erreichbar | Direkt Grounding aufrufen (kein Cache) | Log |
| Rate Limit Google API | Retry mit Backoff, nach 3 Versuchen `WebResearchError` | Admin Dashboard |

### Monitoring

```python
# Structured Logging für alle Research-Operationen
logger.info(
    "Web research completed",
    extra={
        'position_id': pid,
        'grounding_status': 'success',
        'sources_count': len(sources),
        'cache_hit': False,
        'query_count': 3,
        'duration_ms': 1200,
    }
)
```

---

## Konfiguration

### Umgebungsvariablen

| Variable | Beschreibung | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Gemini API Key (existiert) | -- |
| `WEB_RESEARCH_CACHE_TTL` | Cache TTL in Sekunden | `604800` (7 Tage) |
| `WEB_RESEARCH_MAX_WORKERS` | Parallel Threads | `5` |
| `WEB_RESEARCH_MAX_QUERIES` | Queries pro Position | `3` |

### Feature Flag

```python
# Aktivierung via Feature Flag
WEB_RESEARCH_GROUNDING_ENABLED = True   # Gemini Grounding an/aus
WEB_RESEARCH_PDF_SCRAPING_ENABLED = False  # Phase 2
WEB_RESEARCH_CRAWLER_ENABLED = False       # Phase 2
```

---

## Implementierungs-Phasen

### Phase 1: Gemini Grounding + Qualität

- [ ] `WebSearchService` umbauen auf Gemini Grounding
- [ ] Multi-Query Strategie (3 Queries pro Position)
- [ ] Quellen-Scoring (`source_scorer.py`)
- [ ] Quellen-URLs in `ai_metadata` speichern
- [ ] Redis Cache für Research-Ergebnisse
- [ ] Parallel Execution (ThreadPoolExecutor)
- [ ] Sprach-Split (DE/EN je nach Topic)
- [ ] `grounding_status` in Chapter-Metadaten
- [ ] `WebResearchError` statt stiller Fallback
- [ ] Migration: `web_research_cache` Tabelle
- [ ] i18n: Hardcoded Deutsch entfernen

### Phase 2: PDF-Scraping + Crawler

- [ ] `PDFScraperService` implementieren
- [ ] IHK PDF-Quellen konfigurieren
- [ ] Celery Periodic Task für Crawling
- [ ] Integration mit `storage.pdf_cache`
- [ ] Admin UI: Crawl-Status + manuelle Trigger

### Phase 3: ML Source Ranking

- [ ] Feedback-Collection (Kapitel-Bewertungen)
- [ ] Korrelations-Analyse (Quelle → Bewertung)
- [ ] Einfaches Ranking-Modell trainieren
- [ ] Integration in Source Scoring

---

## Zusammenfassung

| Feature | Phase | Status |
|---------|-------|--------|
| Gemini Grounding (Google Search) | 1 | Geplant |
| Multi-Query (Theorie + Praxis + Prüfung) | 1 | Geplant |
| Quellen-Scoring (Domain-Whitelist) | 1 | Geplant |
| Quellen-URLs transparent | 1 | Geplant |
| Redis Cache (7 Tage TTL) | 1 | Geplant |
| Parallel Execution | 1 | Geplant |
| Sprach-Split (DE/EN) | 1 | Geplant |
| Grounding-Status transparent | 1 | Geplant |
| IHK PDF-Scraping | 2 | Geplant |
| Targeted Crawler | 2 | Geplant |
| ML Source Ranking | 3 | Zukunft |

---

**Version:** 1.0
**Letzte Aktualisierung:** März 2026
