# Design: PromptsTab CRUD + Route Restructuring

**Datum:** 2026-02-24
**Status:** APPROVED

## Route Restructuring

**Change:** `/panel/editor` → `/panel/admin/editor`

- Route path changes in `panelRoutes` (admin/routes.ts)
- Redirect `/panel/editor` → `/panel/admin/editor` for backward compat
- All old redirects (kurse, kurs-editor, courses) point to `/panel/admin/editor`
- Navigation link in PanelLayout updated
- Pages stay under `pages/panel/editor/` (shared, no duplication)
- Guard: `requiresSystemAdmin` inherited from `/panel` parent

## PromptsTab CRUD

**Replace** placeholder PromptsTab with full Prompt Template Library.

### API Client
- `GET /panel/prompts` — list (with ?category filter)
- `GET /panel/prompts/:id` — detail
- Backend CRUD already exists via PromptTemplateRepository

### PromptsTab UI
- Category chips (all, theory, lesson, quiz, flashcard, tutor, summary, exam)
- Search input
- Template card grid (title, category badge, style badge, description)
- Click card → detail/edit mode
- "New Template" button → create form

### Detail/Edit Mode
- System prompt + user prompt template (editable textareas)
- Variables list display
- Model / temperature / max_tokens config
- Save / Delete / Back buttons

### i18n
- Keys in de/en/pl for all labels
