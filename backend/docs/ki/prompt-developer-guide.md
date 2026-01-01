# LernsystemX - Prompt Developer Guide

**Phase 24 - KI Prompt System**
**Version:** 1.0
**Last Updated:** 2025-11-17

## Übersicht

Das zentrale Prompt-System von LernsystemX ermöglicht die strukturierte Verwaltung aller KI-Prompts für Lernmethoden. Statt verstreuter, hartcodierter Prompts bietet das System:

- **Zentrale Prompt-Registry** mit Versionierung
- **Pydantic-basierte Type-Safety** für Prompts
- **Template-Rendering** mit Variablen
- **Multi-Provider-Support** (OpenAI, Anthropic, Google, Cohere, HuggingFace)
- **Internationalisierung** (Language Modes)
- **RBAC-Integration** (Role-based Access Control)

---

## Architektur

### Module

```
backend/app/ki/
├── __init__.py                      # Public API exports
├── prompt_models.py                 # Pydantic models (PromptTemplate, PromptMessage, etc.)
├── prompt_registry.py               # Central registry + init_default_prompts()
└── learning_method_mapping.py       # Mapping: learning_method → prompt_template
```

### Datenmodelle

#### `PromptMessage`
Einzelne Nachricht in einem Prompt (System/User/Assistant).

```python
from app.ki import PromptMessage

msg = PromptMessage(
    role="system",  # "system" | "user" | "assistant"
    content="Du bist ein KI-Tutor für {{course_title}}."
)
```

#### `PromptVariable`
Variablendefinition für Template-Rendering.

```python
from app.ki import PromptVariable

var = PromptVariable(
    name="course_title",
    description="Titel des Kurses",
    required=True,
    default=None  # Nur für optional variables
)
```

#### `PromptTemplate`
Vollständiges Prompt-Template mit Metadaten.

```python
from app.ki import PromptTemplate, PromptMessage, PromptVariable

template = PromptTemplate(
    code="explain_concept",
    title="Konzept Erklärung",
    description="Erklärt ein Konzept schrittweise mit Beispielen",
    version=1,
    tags=["learning", "explanation"],
    messages=[
        PromptMessage(role="system", content="Du bist ein KI-Tutor für {{course_title}}."),
        PromptMessage(role="user", content="Erkläre: {{concept_text}}")
    ],
    variables=[
        PromptVariable(name="course_title", description="Kurstitel", required=True),
        PromptVariable(name="concept_text", description="Konzepttext", required=True)
    ],
    model="claude-3-sonnet-20240229",
    max_tokens=2000,
    temperature=0.7,
    language_mode="target",
    allowed_roles=["student", "teacher", "admin"]
)
```

---

## Verwendung

### 1. Template aus Registry laden

```python
from app.ki import get_prompt_template

template = get_prompt_template("explain_concept")
```

### 2. Template rendern

```python
messages = template.render({
    "course_title": "Python Basics",
    "lesson_title": "Functions",
    "concept_text": "What is a decorator?",
    "user_level": "intermediate"  # Optional variable
})

# messages = [
#     {"role": "system", "content": "Du bist ein KI-Tutor für Python Basics..."},
#     {"role": "user", "content": "Erkläre: What is a decorator?"}
# ]
```

### 3. An KI-Provider senden

```python
from app.services.ai_adapter import AIAdapter

adapter = AIAdapter(provider='openai', model='gpt-4o-mini')
response = adapter.send_messages(messages, temperature=0.7, max_tokens=2000)

print(response['output_text'])
print(f"Tokens: {response['total_tokens']}, Cost: {response['cost_eur']} EUR")
```

### 4. Komplett-Beispiel

```python
from app.ki import get_prompt_template
from app.services.ai_adapter import AIAdapter

# 1. Template laden
template = get_prompt_template("explain_concept")

# 2. Context definieren
context = {
    "course_title": "Python Basics",
    "lesson_title": "Decorators",
    "concept_text": "Erkläre @property Decorators",
    "user_level": "advanced"
}

# 3. Messages rendern
messages = template.render(context)

# 4. AI Request
adapter = AIAdapter(
    provider=template.model.split('-')[0] if template.model else 'openai',
    model=template.model or 'gpt-4o-mini'
)

response = adapter.send_messages(
    messages=messages,
    temperature=template.temperature or 0.7,
    max_tokens=template.max_tokens or 2000
)

# 5. Response verarbeiten
print(f"Output: {response['output_text']}")
print(f"Cost: {response['cost_eur']} EUR")
print(f"Latency: {response['latency_ms']} ms")
```

---

## Standard-Prompts

Das System registriert automatisch folgende Standard-Templates:

| Code                   | Beschreibung                                    | Model               |
|------------------------|-------------------------------------------------|---------------------|
| `explain_concept`      | Erklärt Konzepte verständlich                   | claude-3-sonnet     |
| `flashcards`           | Generiert Flashcard Q&A-Paare                   | gpt-4-turbo         |
| `quiz_generator`       | Erstellt Multiple-Choice-Quizze                 | gpt-4-turbo         |
| `socratic_tutor`       | Führt sokratischen Dialog                       | claude-3-sonnet     |
| `summarize_lesson`     | Erstellt strukturierte Zusammenfassungen        | gpt-4-turbo         |
| `translation_assistant`| Übersetzt Lerninhalte                           | gpt-4-turbo         |

---

## Eigene Prompt-Templates erstellen

### Schritt 1: Template definieren

```python
from app.ki import PromptTemplate, PromptMessage, PromptVariable

custom_template = PromptTemplate(
    code="custom_method",
    title="Meine Custom Lernmethode",
    description="Beschreibung der Methode",
    version=1,
    tags=["custom", "learning"],
    messages=[
        PromptMessage(
            role="system",
            content="System-Anweisung mit {{variable}}"
        ),
        PromptMessage(
            role="user",
            content="User-Input: {{user_input}}"
        )
    ],
    variables=[
        PromptVariable(
            name="variable",
            description="Beschreibung",
            required=True
        ),
        PromptVariable(
            name="user_input",
            description="User Input",
            required=True
        )
    ],
    model="gpt-4o-mini",
    max_tokens=1500,
    temperature=0.8,
    language_mode="target",
    allowed_roles=["teacher", "admin"]
)
```

### Schritt 2: Template registrieren

```python
from app.ki import register_prompt

register_prompt(custom_template)
```

### Schritt 3: Template verwenden

```python
from app.ki import get_prompt_template

template = get_prompt_template("custom_method")
messages = template.render({"variable": "Wert", "user_input": "Text"})
```

---

## Template-Variablen

### Standard-Variablen

Folgende Variablen sind in den meisten Templates verfügbar:

| Variable           | Typ    | Beschreibung                       |
|--------------------|--------|-------------------------------------|
| `course_title`     | str    | Kurstitel                           |
| `lesson_title`     | str    | Lektionstitel                       |
| `lesson_content`   | str    | Lektionsinhalt (vollständig)        |
| `concept_text`     | str    | Zu erklärender Konzepttext          |
| `user_level`       | str    | Wissenslevel (beginner/inter/adv)   |
| `language`         | str    | Zielsprache (de, en, es, ...)       |
| `organisation_name`| str    | Name der Organisation               |

### Methodenspezifische Variablen

**Flashcards:**
- `num_flashcards` (int): Anzahl zu erstellender Flashcards

**Quiz:**
- `num_questions` (int): Anzahl Multiple-Choice-Fragen

**Translation:**
- `source_language` (str): Quellsprache
- `target_language` (str): Zielsprache
- `content_to_translate` (str): Zu übersetzender Inhalt

**Summary:**
- `summary_length` (str): Länge (kurz/mittel/ausführlich)

---

## Language Modes

Templates unterstützen drei Language Modes:

### 1. `source` (Quellsprache)
Prompt verwendet die Sprache des Lerninhalts.

**Beispiel:** Deutsches Lehrmaterial → Prompt auf Deutsch

```python
PromptTemplate(
    ...,
    language_mode="source"
)
```

### 2. `target` (Zielsprache)
Prompt verwendet die Sprache des Users (Standard).

**Beispiel:** User mit UI-Sprache Englisch → Prompt auf Englisch

```python
PromptTemplate(
    ...,
    language_mode="target"  # Default
)
```

### 3. `mixed` (Gemischt)
Kombination aus Quell- und Zielsprache.

**Beispiel:** Übersetzung von DE → EN → Prompt erwähnt beide Sprachen

```python
PromptTemplate(
    ...,
    language_mode="mixed"
)
```

---

## RBAC (Role-Based Access Control)

Templates können auf bestimmte Rollen beschränkt werden:

```python
PromptTemplate(
    ...,
    allowed_roles=["teacher", "admin"]  # Nur für Teacher & Admin
)
```

**Leeres Array = alle Rollen:**
```python
PromptTemplate(
    ...,
    allowed_roles=[]  # Alle Rollen können verwenden
)
```

---

## Versionierung

Templates sind versioniert. Bei Änderungen:

1. **Version erhöhen:**
   ```python
   PromptTemplate(
       code="explain_concept",
       version=2,  # Erhöht von 1
       ...
   )
   ```

2. **Registrieren mit Overwrite:**
   ```python
   register_prompt(updated_template, overwrite=True)
   ```

---

## Integration in Learning Methods

### Mapping: Learning Method → Prompt Template

```python
from app.ki.learning_method_mapping import get_prompt_template_for_method

# Learning Method Name → Prompt Template Code
template_code = get_prompt_template_for_method("KI-Tutor")
# Returns: "explain_concept"
```

### Verwendung in Repository

```python
from app.ki import get_prompt_template
from app.ki.learning_method_mapping import get_prompt_template_for_method
from app.services.ai_adapter import AIAdapter

def execute_ai_method(method_name, user_input, context):
    # 1. Get prompt template code
    template_code = get_prompt_template_for_method(method_name)

    # 2. Load template
    template = get_prompt_template(template_code)

    # 3. Prepare context
    prompt_context = {
        "course_title": context.get("course_title"),
        "lesson_title": context.get("lesson_title"),
        "concept_text": user_input,
        "user_level": context.get("difficulty", "intermediate")
    }

    # 4. Render messages
    messages = template.render(prompt_context)

    # 5. Send to AI
    adapter = AIAdapter(
        provider=template.model.split('-')[0] if template.model else 'openai',
        model=template.model or 'gpt-4o-mini'
    )

    response = adapter.send_messages(
        messages=messages,
        temperature=template.temperature or 0.7,
        max_tokens=template.max_tokens or 2000
    )

    return response
```

---

## Best Practices

### 1. Descriptive Template Codes
```python
# Good
code="explain_concept_with_examples"

# Bad
code="ec1"
```

### 2. Required vs. Optional Variables
```python
# Required für kritische Daten
PromptVariable(name="lesson_content", required=True)

# Optional mit Default für Nice-to-Have
PromptVariable(name="user_level", required=False, default="intermediate")
```

### 3. Model Selection
```python
# Komplexe Aufgaben: GPT-4 Turbo, Claude 3.5 Sonnet
model="gpt-4-turbo"

# Einfache Aufgaben: GPT-4o-mini, Claude 3.5 Haiku
model="gpt-4o-mini"
```

### 4. Temperature Settings
```python
# Faktisch, präzise Antworten
temperature=0.3

# Kreative, vielfältige Antworten
temperature=0.9

# Standard
temperature=0.7
```

### 5. Security & Privacy
```python
# NIEMALS vollständige Prompts oder Userdaten loggen
# NUR: template_code, model, tokens, cost

logger.info(f"AI request: template={template.code}, tokens={total_tokens}")
```

---

## Debugging

### Template anzeigen
```python
template = get_prompt_template("explain_concept")
print(template.to_dict())
```

### Alle Templates auflisten
```python
from app.ki import list_all_prompts

templates = list_all_prompts()
for t in templates:
    print(f"{t.code} (v{t.version}): {t.title}")
```

### Templates filtern
```python
learning_templates = list_all_prompts(tags=["learning"])
```

### Rendering testen
```python
template = get_prompt_template("explain_concept")

try:
    messages = template.render({
        "course_title": "Test Course",
        "lesson_title": "Test Lesson",
        "concept_text": "Test Concept"
    })
    print("✓ Rendering successful")
    print(messages)
except ValueError as e:
    print(f"✗ Missing variables: {e}")
```

---

## API Reference

### `get_prompt_template(code: str) -> PromptTemplate`
Lädt Template aus Registry.

**Raises:** `PromptRegistryError` wenn nicht gefunden

### `register_prompt(template: PromptTemplate, overwrite: bool = False) -> None`
Registriert Template in Registry.

**Raises:** `PromptRegistryError` wenn code bereits existiert und overwrite=False

### `list_all_prompts(tags: Optional[List[str]] = None) -> List[PromptTemplate]`
Listet alle registrierten Templates (optional nach Tags gefiltert).

### `template.render(context: Dict[str, Any]) -> List[Dict[str, str]]`
Rendert Template mit Context-Variablen.

**Returns:** Liste von Messages: `[{"role": "system", "content": "..."}, ...]`

**Raises:** `ValueError` wenn required variables fehlen

### `adapter.send_messages(messages: list, temperature: float, max_tokens: int) -> Dict`
Sendet pre-rendered messages an AI provider.

**Returns:**
```python
{
    'output_text': str,
    'input_tokens': int,
    'output_tokens': int,
    'total_tokens': int,
    'cost_eur': float,
    'latency_ms': int,
    'model': str,
    'provider': str
}
```

---

## Testing

### Unit Tests für Templates
```python
import pytest
from app.ki import PromptTemplate, PromptMessage, PromptVariable

def test_template_rendering():
    template = PromptTemplate(
        code="test_template",
        title="Test",
        description="Test template",
        messages=[
            PromptMessage(role="system", content="Hello {{name}}")
        ],
        variables=[
            PromptVariable(name="name", description="Name", required=True)
        ]
    )

    messages = template.render({"name": "World"})

    assert len(messages) == 1
    assert messages[0]['content'] == "Hello World"

def test_missing_required_variable():
    template = PromptTemplate(
        code="test_template",
        title="Test",
        description="Test",
        messages=[PromptMessage(role="system", content="{{required_var}}")],
        variables=[PromptVariable(name="required_var", required=True)]
    )

    with pytest.raises(ValueError, match="Missing required variables"):
        template.render({})
```

---

## Migration von Alt-Code

### Vorher (Hartcodiert)
```python
def execute_ai_method(user_input, context):
    prompt = f"Du bist ein KI-Tutor. {context}. {user_input}"

    adapter = AIAdapter()
    response = adapter.send_request(prompt=prompt, context=context)
    return response
```

### Nachher (Mit Templates)
```python
def execute_ai_method(user_input, context):
    template = get_prompt_template("explain_concept")

    messages = template.render({
        "course_title": context["course"],
        "concept_text": user_input,
        "user_level": context.get("level", "intermediate")
    })

    adapter = AIAdapter(model=template.model)
    response = adapter.send_messages(
        messages=messages,
        temperature=template.temperature,
        max_tokens=template.max_tokens
    )
    return response
```

---

## Troubleshooting

### `PromptRegistryError: Prompt template 'xxx' not found`
**Lösung:** Template nicht registriert. Prüfe `init_default_prompts()` oder registriere manuell.

### `ValueError: Missing required variables: course_title`
**Lösung:** Alle required variables im render() call übergeben.

### `AIProviderError: Invalid API key`
**Lösung:** Environment Variable für Provider setzen (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)

### Templates werden nicht initialisiert
**Lösung:** Prüfe `app/__init__.py` → `setup_prompt_system(app)` wird aufgerufen.

---

## Weiterführende Dokumentation

- **User-Dokumentation:** `LernsystemX-Doku/35_Developer-Guide-KI-Prompts.md`
- **KI-Pipeline:** `LernsystemX-Doku/22_KI-Pipeline-Deep.md`
- **Lernmethoden:** `LernsystemX-Doku/02_Lernmethoden.md`
- **AI Adapter:** `backend/app/services/ai_adapter.py`
- **Prompt Models:** `backend/app/ki/prompt_models.py`
- **Prompt Registry:** `backend/app/ki/prompt_registry.py`

---

**Version History:**
- v1.0 (2025-11-17): Initial documentation
