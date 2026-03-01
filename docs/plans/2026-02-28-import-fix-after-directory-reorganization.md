# Import Fix Plan — Directory Reorganization

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all broken imports after ~370 files were moved into subdirectories (84 backend, 284 frontend)

**Architecture:** Two-phase approach — Backend uses Python barrel exports (`__init__.py`) so most external imports stay stable; Frontend uses TypeScript barrel exports (`index.ts`) + direct import path fixes.

**Tech Stack:** Python (Flask), Vue 3, TypeScript

**Key Insight:** Backend `__init__.py` barrel exports use **absolute imports** — updating these 12 files fixes ~95% of backend. Frontend needs barrel export updates + grep-based direct import fixes.

---

## Phase 1: Backend — Barrel Export Fixes (12 packages)

### Task 1: Create `__init__.py` in all 24 new subdirectories

**Files to create (empty Python packages):**

```bash
# All 24 new subdirectories need __init__.py
touch backend/app/application/services/ai/plan/__init__.py
touch backend/app/application/services/content/course_authoring/generation/__init__.py
touch backend/app/application/services/content/course_authoring/session/__init__.py
touch backend/app/application/services/content/course_authoring/validation/__init__.py
touch backend/app/application/services/content/lesson_video/pipeline/__init__.py
touch backend/app/application/services/content/lesson_video/runtime/__init__.py
touch backend/app/application/services/i18n/core/__init__.py
touch backend/app/application/services/i18n/generation/__init__.py
touch backend/app/application/services/system_features/math_toolkit/solving/__init__.py
touch backend/app/application/services/system_features/math_toolkit/tracking/__init__.py
touch backend/app/infrastructure/ai/plan/__init__.py
touch backend/app/infrastructure/persistence/repositories/ai/config/__init__.py
touch backend/app/infrastructure/persistence/repositories/ai/tracking/__init__.py
touch backend/app/infrastructure/persistence/repositories/authoring/sessions/__init__.py
touch backend/app/infrastructure/persistence/repositories/authoring/content/__init__.py
touch backend/app/infrastructure/persistence/repositories/courses/management/__init__.py
touch backend/app/infrastructure/persistence/repositories/courses/content/__init__.py
touch backend/app/infrastructure/persistence/repositories/courses/analytics/__init__.py
touch backend/app/infrastructure/persistence/repositories/i18n/admin/__init__.py
touch backend/app/infrastructure/persistence/repositories/i18n/sync/__init__.py
touch backend/app/infrastructure/persistence/repositories/i18n/translations/__init__.py
touch backend/app/infrastructure/persistence/repositories/learning_method/execution/__init__.py
touch backend/app/infrastructure/persistence/repositories/learning_method/config/__init__.py
touch backend/app/setup/diagnostics/verification/__init__.py
touch backend/app/setup/diagnostics/checks/__init__.py
```

**Step 1:** Run the touch commands above
**Step 2:** Verify: `find backend/app -name "__init__.py" -newer backend/app/__init__.py | wc -l` → should be 24+
**Step 3:** Commit: `git add backend/ && git commit -m "chore: add __init__.py to new backend subdirectories"`

---

### Task 2: Fix `repositories/courses/__init__.py`

**File:** `backend/app/infrastructure/persistence/repositories/courses/__init__.py`

**Old → New import paths:**
| Old path | New path |
|----------|----------|
| `.crud` | `.management.crud` |
| `.search` | `.analytics.search` |
| `.admin` | `.management.admin` |
| `.lifecycle` | `.management.lifecycle` |
| `.statistics` | `.analytics.statistics` |
| `.chapters` | `.content.chapters` |
| `.lessons` | `.content.lessons` |
| `.ai_settings` | `.analytics.ai_settings` |
| `.files` | `.content.files` |
| `.analytics` | `.analytics.analytics` |

**Step 1:** Update all import paths in `__init__.py`
**Step 2:** Verify: `python -c "from app.infrastructure.persistence.repositories.courses import CourseRepository"`

---

### Task 3: Fix `repositories/ai/__init__.py`

**File:** `backend/app/infrastructure/persistence/repositories/ai/__init__.py`

**Old → New import paths:**
| Old path | New path |
|----------|----------|
| `.jobs` | `.tracking.jobs` |
| `.profiles` | `.config.profiles` |
| `.providers` | `.config.providers` |
| `.editor` | `.config.editor` |
| `.usage` | `.tracking.usage` |
| `.generation_log` | `.tracking.generation_log` |

Note: `.exam_context` and `.content_plans` stayed in root — no change.

**Step 1:** Update import paths in `__init__.py`
**Step 2:** Verify: `python -c "from app.infrastructure.persistence.repositories.ai import AIJobRepository"`

---

### Task 4: Fix `repositories/i18n/__init__.py`

**File:** `backend/app/infrastructure/persistence/repositories/i18n/__init__.py`

**Old → New import paths:**
| Old path | New path |
|----------|----------|
| `.translation` | `.translations.translation` |
| `.translation_part2` | `.translations.translation_part2` |
| `.translations` | `.translations.translations` |
| `.service_queries` | `.translations.service_queries` |
| `.service_queries_part2` | `.translations.service_queries_part2` |
| `.admin_languages` | `.admin.admin_languages` |
| `.admin_queries` | `.admin.admin_queries` |
| `.bulk_seed` | `.admin.bulk_seed` |

Note: `import_repository` moved to `.admin.import_repository` — check if it's re-exported.
Note: `sync*` files moved to `.sync/` — check if any are re-exported.

**Step 1:** Update import paths in `__init__.py`
**Step 2:** Check for any direct imports to sync files: `grep -r "from.*repositories.i18n.sync" backend/app/`
**Step 3:** Fix any direct imports found
**Step 4:** Verify: `python -c "from app.infrastructure.persistence.repositories.i18n import TranslationRepository"`

---

### Task 5: Fix `repositories/authoring/__init__.py`

**File:** `backend/app/infrastructure/persistence/repositories/authoring/__init__.py`

**Old → New import paths:**
| Old path | New path |
|----------|----------|
| `.analysis` | `.content.analysis` |
| `.changes` | `.content.changes` |
| `.generations` | `.content.generations` |
| `.refinements` | `.content.refinements` |
| `.sessions` | `.sessions.sessions` |
| `.finalization` | `.sessions.finalization` |
| `.milestones` | `.sessions.milestones` |
| `.plan_versions` | `.sessions.plan_versions` |
| `.user_journey` | `.sessions.user_journey` |

Note: `.decision_explanations`, `.dialog_messages`, `.files` stayed in root — no change.

**Step 1:** Update import paths in `__init__.py`
**Step 2:** Verify: `python -c "from app.infrastructure.persistence.repositories.authoring import CourseAuthoringSessionRepository"`

---

### Task 6: Fix `repositories/learning_method/__init__.py`

**File:** `backend/app/infrastructure/persistence/repositories/learning_method/__init__.py`

**Old → New import paths:**
| Old path | New path |
|----------|----------|
| `.ai_execution` | `.execution.ai_execution` |
| `.ai_execution_part2` | `.execution.ai_execution_part2` |
| `.instances` | `.execution.instances` |
| `.instances_part2` | `.execution.instances_part2` |
| `.progress` | `.execution.progress` |
| `.catalog` | `.config.catalog` |
| `.types` | `.config.types` |
| `.groups` | `.config.groups` |

Note: `.base`, `.feedback`, `.statistics` stayed in root — no change.

**Step 1:** Update import paths in `__init__.py`
**Step 2:** Verify: `python -c "from app.infrastructure.persistence.repositories.learning_method import LearningMethodRepository"`

---

### Task 7: Fix `services/ai/__init__.py`

**File:** `backend/app/application/services/ai/__init__.py`

**Old → New import paths:**
| Old path | New path |
|----------|----------|
| `.plan_service` | `.plan.plan_service` |
| `.plan_service_part2` | `.plan.plan_service_part2` |

Note: `.adapter`, `.static`, `.context.detector`, `.job_service`, `.skill_service`, `.course_settings` stayed — no change.

**Step 1:** Update import paths in `__init__.py`
**Step 2:** Check direct imports: `grep -rn "from app.application.services.ai.plan_service" backend/app/ --include="*.py"` and `grep -rn "from app.application.services.ai.plan_execution" backend/app/ --include="*.py"`
**Step 3:** Fix any direct imports (add `.plan.` to path)
**Step 4:** Verify: `python -c "from app.application.services.ai import PlanService"`

---

### Task 8: Fix `infrastructure/ai/__init__.py`

**File:** `backend/app/infrastructure/ai/__init__.py`

**Old → New import path:**
| Old path | New path |
|----------|----------|
| `.plan_generator` | `.plan.plan_generator` |

Also check: `plan_prompts.py` and `plan_prompts_part2.py` moved to `plan/` — find any direct imports.

**Step 1:** Update `__init__.py`
**Step 2:** Check: `grep -rn "from app.infrastructure.ai.plan_prompts" backend/app/ --include="*.py"`
**Step 3:** Check: `grep -rn "from app.infrastructure.ai.plan_generator" backend/app/ --include="*.py"`
**Step 4:** Fix any direct imports found
**Step 5:** Verify: `python -c "from app.infrastructure.ai import PlanGeneratorAdapter"`

---

### Task 9: Fix `services/content/course_authoring/__init__.py`

**File:** `backend/app/application/services/content/course_authoring/__init__.py`

**Old → New import paths:**
| Old path | New path |
|----------|----------|
| `.session` | `.session.session` |
| `.scope_guard` | `.validation.scope_guard` |
| `.content_validator` | `.validation.content_validator` |
| `.token_budget` | `.session.token_budget` |
| `.pipeline` | `.generation.pipeline` |

Note: `.tool_processor` and `.quality_profile` stayed in root — verify. Also `.prompts` moved to `.generation.prompts`, `.ai_generator` moved to `.generation.ai_generator`.

**Step 1:** Update `__init__.py`
**Step 2:** Check: `grep -rn "from app.application.services.content.course_authoring.prompts" backend/app/ --include="*.py"`
**Step 3:** Check: `grep -rn "from app.application.services.content.course_authoring.session" backend/app/ --include="*.py"`
**Step 4:** Fix any direct imports
**Step 5:** Verify: `python -c "from app.application.services.content.course_authoring import CourseAuthoringService"`

---

### Task 10: Fix remaining backend barrel exports

Fix the remaining 3 `__init__.py` files:

**A) `services/content/lesson_video/__init__.py`**
| Old path | New path |
|----------|----------|
| `.orchestration` | `.pipeline.orchestration` |
| (check `.generation`, `.helpers`, `.caching`, `.status`, `.models`) | (`.pipeline.*` or `.runtime.*`) |

**B) `services/i18n/__init__.py`**
| Old path | New path |
|----------|----------|
| `.translations` | `.core.translations` |
| `.languages` | `.core.languages` |
| `.keys` | `.core.keys` |
| `.suggestions` | `.generation.suggestions` |
| `.ai_generation` | `.generation.ai_generation` |
| `.config` | `.core.config` |

**C) `services/system_features/math_toolkit/__init__.py`**
| Old path | New path |
|----------|----------|
| `.parser` | `.solving.parser` |
| `.solver` | `.solving.solver` |
| `.patterns` | `.solving.patterns` |
| `.calculator` | `.solving.calculator` |
| `.steps` | `.solving.steps` |
| `.sessions` | `.tracking.sessions` |
| `.progress` | `.tracking.progress` |
| `.hints` | `.tracking.hints` |
| `.tasks` | `.tracking.tasks` |

**D) `setup/diagnostics/__init__.py`**
| Old path | New path |
|----------|----------|
| `.checks` | `.checks.checks` |
| `.checks_part2` | `.checks.checks_part2` |

Also check: `grep -rn "from app.setup.diagnostics.verify" backend/app/ --include="*.py"` and `grep -rn "from app.setup.diagnostics.system_check" backend/app/ --include="*.py"` — those moved to `verification/` and `checks/`.

**Step 1:** Update all 4 `__init__.py` files
**Step 2:** Check and fix any direct imports
**Step 3:** Verify: `python -c "from app import create_app; create_app()"`

---

### Task 11: Full backend import scan

**Step 1:** Run comprehensive scan for any remaining broken imports:
```bash
# Find all imports referencing old paths of moved files
cd backend
python -c "from app import create_app; create_app()"
```

**Step 2:** If import errors occur, fix them one by one
**Step 3:** Final verify: `python -c "from app import create_app; app = create_app(); print('OK')"`
**Step 4:** Commit: `git add backend/ && git commit -m "fix(backend): update all imports after directory reorganization"`

---

## Phase 2: Frontend — Barrel Export + Direct Import Fixes

### Task 12: Fix `editor/ai/index.ts` barrel export

**File:** `frontend/src/presentation/components/panel/editor/ai/index.ts`

**Old → New paths:**
```typescript
// OLD → NEW
'./AIEditorContainer.vue'          → './core/AIEditorContainer.vue'
'./AIEditorWindow.vue'             → './core/AIEditorWindow.vue'
'./AIPreview.vue'                  → './settings/AIPreview.vue'
'./AISettings.vue'                 → './settings/AISettings.vue'
'./ChatInterface.vue'              → './chat-source/ChatInterface.vue'
'./ContentGenerator.vue'           → './generation/ContentGenerator.vue'
'./GenerationHistory.vue'          → './generation/GenerationHistory.vue'
'./PromptBuilder.vue'              → './generation/PromptBuilder.vue'
'./SourceSelectionContainer.vue'   → './chat-source/SourceSelectionContainer.vue'
'./TemplateLibrary.vue'            → './settings/TemplateLibrary.vue'
'./VariantSelector.vue'            → './settings/VariantSelector.vue'
```

**Step 1:** Update `index.ts`
**Step 2:** Check: `grep -rn "from.*panel/editor/ai/AIEditor" frontend/src/ --include="*.ts" --include="*.vue"` — fix any direct imports bypassing barrel
**Step 3:** Check: `grep -rn "from.*panel/editor/ai/AI" frontend/src/ --include="*.ts" --include="*.vue"` — same for other moved files

---

### Task 13: Fix `unified/composables/index.ts` barrel export

**File:** `frontend/src/presentation/components/panel/editor/ai/unified/composables/index.ts`

**Old → New paths:**
```typescript
'./useEditorState'        → './editor/useEditorState'
'./usePlanMode'           → './plan/usePlanMode'
'./useSkillExecution'     → './generation/useSkillExecution'
'./usePromptBuilder'      → './generation/usePromptBuilder'
'./useTokenBudget'        → './plan/useTokenBudget'
'./useGenerationHistory'  → './generation/useGenerationHistory'
'./useChatSession'        → './generation/useChatSession'
'./useStructureView'      → './editor/useStructureView'
'./useWorkflowPhase'      → './plan/useWorkflowPhase'
'./useFileUpload'         → './editor/useFileUpload'
'./useModelSelector'      → './editor/useModelSelector'
'./useQualityLevel'       → (stayed in root — no change)
```

**Step 1:** Update `index.ts`
**Step 2:** Check for direct imports: `grep -rn "from.*unified/composables/use" frontend/src/ --include="*.ts" --include="*.vue"` — any that bypass the barrel
**Step 3:** Fix direct imports found

---

### Task 14: Fix `unified/panels/index.ts` barrel export

**File:** `frontend/src/presentation/components/panel/editor/ai/unified/panels/index.ts`

**Old → New paths:**
```typescript
'./PlanModePanel.vue'         → './plan/PlanModePanel.vue'
'./SkillCatalogPanel.vue'     → './skill/SkillCatalogPanel.vue'
'./SkillExecutionPanel.vue'   → './skill/SkillExecutionPanel.vue'
'./PromptBuilderPanel.vue'    → './shared/PromptBuilderPanel.vue'
'./GenerationResultPanel.vue' → './shared/GenerationResultPanel.vue'
'./BatchProgressPanel.vue'    → './shared/BatchProgressPanel.vue'
'./PlanPhaseWizard.vue'       → './plan/PlanPhaseWizard.vue'
'./PlanCourseCard.vue'        → './plan/PlanCourseCard.vue'
'./PlanChapterList.vue'       → './plan/PlanChapterList.vue'
'./PlanChat.vue'              → './plan/PlanChat.vue'
```

Also add exports for new files: `PlanEmptyState`, `StepDetailPanel`.

**Step 1:** Update `index.ts`
**Step 2:** Check for direct panel imports: `grep -rn "from.*unified/panels/" frontend/src/ --include="*.ts" --include="*.vue"` — fix any bypassing barrel

---

### Task 15: Fix `manual/` barrel exports

**Files:**
- `manual/index.ts` — update paths from `./panels/X.vue` to `./panels/lesson/X.vue` etc.
- `manual/composables/index.ts` — update paths to `./editor/X` and `./content/X`
- `manual/panels/index.ts` — update paths to `./course/X`, `./lesson/X`, `./structure/X`

**Old → New for `manual/composables/index.ts`:**
```typescript
'./useAutoSave'           → './editor/useAutoSave'
'./useActivityEditor'     → './content/useActivityEditor'
'./useContentEditor'      → './editor/useContentEditor'
'./useEditorKeyboard'     → './editor/useEditorKeyboard'
'./useLessonActivities'   → './content/useLessonActivities'
'./useConfirmDialog'      → (stayed — no change)
'./useFocusTrap'          → './editor/useFocusTrap'
'./useTheorySheets'       → './content/useTheorySheets'
```

**Old → New for `manual/panels/index.ts`:**
```typescript
'./CourseInfoPanel.vue'          → './course/CourseInfoPanel.vue'
'./CourseSelector.vue'           → './course/CourseSelector.vue'
'./CourseMetaForm.vue'           → './course/CourseMetaForm.vue'
'./LessonActivitiesSection.vue'  → './lesson/LessonActivitiesSection.vue'
'./LessonSettingsPanel.vue'      → './lesson/LessonSettingsPanel.vue'
'./LessonContentEditor.vue'     → './lesson/LessonContentEditor.vue'
'./TheorySheetsSection.vue'     → './lesson/TheorySheetsSection.vue'
'./StructureTreePanel.vue'      → './structure/StructureTreePanel.vue'
'./ChapterLessonTree.vue'       → './structure/ChapterLessonTree.vue'
```

Note: `ContentEditPanel.vue`, `MediaUploadPanel.vue`, `PreviewPanel.vue` stayed in root — no change.

**Step 1:** Update all 3 `index.ts` files
**Step 2:** Update `manual/index.ts` to use new subpaths

---

### Task 16: Fix `editor/shared/index.ts` barrel export

**File:** `frontend/src/presentation/components/panel/editor/shared/index.ts`

**Old → New paths:**
```typescript
'./ContentEditor.vue'      → './panels/ContentEditor.vue'
'./MediaUpload.vue'        → './ui/MediaUpload.vue'
'./PreviewPanel.vue'       → './panels/PreviewPanel.vue'
'./StructurePanel.vue'     → './panels/StructurePanel.vue'
'./ToolbarActions.vue'     → './ui/ToolbarActions.vue'
'./CreatorCoursesView.vue' → './views/CreatorCoursesView.vue'
'./CourseEditorView.vue'   → './views/CourseEditorView.vue'
'./ConfirmBanner.vue'      → './ui/ConfirmBanner.vue'
```

**Step 1:** Update `index.ts`
**Step 2:** Check for direct imports: `grep -rn "from.*editor/shared/Content\|from.*editor/shared/Media\|from.*editor/shared/Preview\|from.*editor/shared/Structure\|from.*editor/shared/Toolbar\|from.*editor/shared/Creator\|from.*editor/shared/Course\|from.*editor/shared/Confirm" frontend/src/ --include="*.ts" --include="*.vue"`

---

### Task 17: Fix all `panel/admin/*` direct imports

For each admin module that was reorganized, find and fix direct imports.

**Scan commands:**
```bash
# For each moved component, find imports
grep -rn "from.*panel/admin/courses/Course" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/categories/Categor" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/i18n/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/security/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/prompts/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/users/User" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/groups/Group" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/system/System" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/dashboard/Dash" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/learning-methods/LM\|from.*panel/admin/learning-methods/Method" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/analytics/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/admin/ai/AI" frontend/src/ --include="*.ts" --include="*.vue"
```

**For each hit:** Add the new subdirectory to the path:
- `admin/courses/CourseEditor.vue` → `admin/courses/editor/CourseEditor.vue`
- `admin/courses/CoursesListView.vue` → `admin/courses/list/CoursesListView.vue`
- `admin/courses/CourseDetailView.vue` → `admin/courses/core/CourseDetailView.vue`
- `admin/i18n/TranslationsView.vue` → `admin/i18n/views/TranslationsView.vue`
- `admin/i18n/panels/ComparisonPanel.vue` → `admin/i18n/panels/comparison/ComparisonPanel.vue`
- `admin/security/SessionManager.vue` → `admin/security/features/SessionManager.vue`
- etc.

**Step 1:** Run all grep commands, collect hits
**Step 2:** Fix each import path
**Step 3:** Also check route files: `frontend/src/presentation/pages/panel/admin/routes.ts`

---

### Task 18: Fix all `panel/user/*` direct imports

**Scan commands:**
```bash
grep -rn "from.*panel/user/courses/Course\|from.*panel/user/courses/Enrolled\|from.*panel/user/courses/User" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/user/dashboard/Dashboard\|from.*panel/user/dashboard/User\|from.*panel/user/dashboard/Widget" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/user/settings/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/user/learning/Lesson\|from.*panel/user/learning/Exam" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/user/gamification/Rpg\|from.*panel/user/gamification/Skill\|from.*panel/user/gamification/Inventory" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*panel/user/social/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*chapters/detail/Theory\|from.*chapters/detail/Lesson\|from.*chapters/detail/Progress" frontend/src/ --include="*.ts" --include="*.vue"
```

**Step 1:** Run grep, collect hits
**Step 2:** Fix import paths (add subdirectory)
**Step 3:** Check route files: `frontend/src/presentation/pages/panel/user/routes.ts` (if exists)

---

### Task 19: Fix all `public/*` direct imports

**Scan commands:**
```bash
# Learning methods
grep -rn "from.*public/learning/methods/AiLesson\|from.*public/learning/methods/CaseStudy\|from.*public/learning/methods/DetailedSteps\|from.*public/learning/methods/TextLesson\|from.*public/learning/methods/VideoLesson\|from.*public/learning/methods/Simulation" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*public/learning/methods/Flashcards\|from.*public/learning/methods/Lueckentext\|from.*public/learning/methods/MultipleChoice\|from.*public/learning/methods/TrueFalse\|from.*public/learning/methods/MathTask" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*public/learning/methods/Freitext\|from.*public/learning/methods/Objective\|from.*public/learning/methods/TaskManager\|from.*public/learning/methods/TaskRow" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*public/learning/methods/MethodExecution" frontend/src/ --include="*.ts" --include="*.vue"

# System features
grep -rn "from.*system-features/collaboration/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*system-features/exam/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*system-features/interactive/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*system-features/it-environments/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*system-features/math/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*system-features/gamification/" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*system-features/tutor/" frontend/src/ --include="*.ts" --include="*.vue"
```

**Step 1:** Run grep, collect hits
**Step 2:** Fix import paths
**Step 3:** Also check: `frontend/src/presentation/pages/public/routes.ts`

---

### Task 20: Fix `course-builder/` and `assessment/exams/` imports

**Scan commands:**
```bash
grep -rn "from.*course-builder/ChatPanel\|from.*course-builder/CourseChatPanel\|from.*course-builder/CourseChatMessage\|from.*course-builder/CourseAuthoringSidebar\|from.*course-builder/CourseStructurePreview\|from.*course-builder/StructurePanel" frontend/src/ --include="*.ts" --include="*.vue"

# Assessment exams - many files moved to panels/, modals/, config/, features/
grep -rn "from.*assessment/settings/exams/" frontend/src/ --include="*.ts" --include="*.vue"
```

**Step 1:** Fix course-builder imports (add `chat/` or `structure/`)
**Step 2:** Fix assessment/exams imports (add `panels/`, `modals/`, `config/`, `features/`)

---

### Task 21: Fix `shared/utils/` (API clients) imports

**Scan commands:**
```bash
grep -rn "from.*shared/utils/time\|from.*shared/utils/adapter\|from.*shared/utils/response\|from.*shared/utils/collection" frontend/src/ --include="*.ts" --include="*.vue"
```

**Old → New:**
- `shared/utils/time*` → `shared/utils/time/time*`
- `shared/utils/adapter*` → `shared/utils/adapters/adapter*`
- `shared/utils/response-adapters` → `shared/utils/adapters/response-adapters`
- `shared/utils/collection-transforms` → `shared/utils/adapters/collection-transforms`
- `shared/utils/adapter-caching` → `shared/utils/adapters/adapter-caching`

Check if there's a barrel `index.ts` to update too.

---

### Task 22: Fix `tutor/user/` component and composable imports

**Scan commands:**
```bash
# Tutor user components moved to avatars/, chat/, tools/
grep -rn "from.*tutor/user/Animated\|from.*tutor/user/Avatar\|from.*tutor/user/Realistic\|from.*tutor/user/Teacher\|from.*tutor/user/Tutor" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*tutor/user/AvatarChat\|from.*tutor/user/TutorChat\|from.*tutor/user/TutorSpeech\|from.*tutor/user/Feedback" frontend/src/ --include="*.ts" --include="*.vue"
grep -rn "from.*tutor/user/OnScreen\|from.*tutor/user/Calculator\|from.*tutor/user/Interactive" frontend/src/ --include="*.ts" --include="*.vue"

# Tutor user composables moved to avatar/, scene/, interaction/
grep -rn "from.*tutor/user/composables/use" frontend/src/ --include="*.ts" --include="*.vue"
```

---

### Task 23: Frontend build verification

**Step 1:** Run: `cd frontend && npm run build`
**Step 2:** If build errors, fix remaining broken imports from error output
**Step 3:** Iterate until build succeeds
**Step 4:** Commit: `git add frontend/ && git commit -m "fix(frontend): update all imports after directory reorganization"`

---

## Phase 3: Final Verification

### Task 24: Full system verification

**Step 1:** Backend: `cd backend && python -c "from app import create_app; app = create_app(); print('Backend OK')"`
**Step 2:** Frontend: `cd frontend && npm run build && echo 'Frontend OK'`
**Step 3:** TypeCheck: `cd frontend && npm run typecheck`
**Step 4:** Final commit with all remaining fixes

---

## File Move Reference (Quick Lookup)

### Backend Moves (84 files, 12 packages)

| Package | Subdirectory | Files Moved |
|---------|-------------|-------------|
| `repositories/courses/` | `management/` | admin, lifecycle, crud |
| | `content/` | chapters, lessons, files |
| | `analytics/` | analytics, statistics, search, ai_settings |
| `repositories/ai/` | `config/` | profiles, providers, editor |
| | `tracking/` | generation_log, usage, jobs |
| `repositories/i18n/` | `admin/` | admin_languages, admin_queries, bulk_seed, import_repository |
| | `sync/` | sync, sync_ops, sync_changes, sync_repository, sync_repository_part2, sync_resolutions |
| | `translations/` | translation, translation_part2, translations, service_queries, service_queries_part2 |
| `repositories/authoring/` | `sessions/` | sessions, finalization, milestones, plan_versions, user_journey |
| | `content/` | analysis, changes, generations, refinements |
| `repositories/learning_method/` | `execution/` | ai_execution, ai_execution_part2, instances, instances_part2, progress |
| | `config/` | catalog, groups, types |
| `services/ai/` | `plan/` | plan_service, plan_service_part2, plan_execution |
| `infrastructure/ai/` | `plan/` | plan_generator, plan_prompts, plan_prompts_part2 |
| `services/course_authoring/` | `generation/` | ai_generator, prompts, pipeline, tool_processor |
| | `session/` | session, session_finalize, token_budget |
| | `validation/` | content_validator, validation, scope_guard |
| `services/lesson_video/` | `pipeline/` | generation, orchestration, helpers |
| | `runtime/` | caching, status, models |
| `services/i18n/` | `core/` | config, keys, languages, translations |
| | `generation/` | ai_generation, suggestions |
| `math_toolkit/` | `solving/` | solver, steps, patterns, parser, calculator |
| | `tracking/` | sessions, progress, tasks, hints |
| `setup/diagnostics/` | `verification/` | verify, verify_part2, verify_final |
| | `checks/` | checks, checks_part2, system_check |

### Frontend Moves (284 files) — See Tasks 12-22 for details
