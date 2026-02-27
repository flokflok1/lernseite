# AI Editor: Chat-First Split-View Design

**Goal:** Rebuild the Unified AI Editor into a split-view interface where a persistent AI chat (left) drives course creation, and a context-dependent panel (right) shows the live course structure, generation progress, or results.

**Architecture:** The chat is always visible. Users create courses from scratch by chatting with the AI, optionally uploading materials. The AI builds the course structure, generates content (theory, flashcards, quizzes), and asks for confirmation before executing. The right panel switches automatically based on workflow phase.

**Tech Stack:** Vue 3 Composition API, TypeScript, existing Flask backend (CourseAuthoringService), psycopg3, AIAdapter (Claude)

---

## Layout

```
+----------------------------+--------------------------------+
|                            |                                |
|  Chat (always visible)     |  Right Panel (context-dependent)|
|  40-50% width              |  50-60% width                  |
|                            |                                |
|  - Message list            |  Default: Course Structure     |
|  - Input + file attach     |  During gen: Progress          |
|  - Context badge           |  After gen: Result preview     |
|  - Inline confirmations    |  On demand: History            |
|                            |                                |
+----------------------------+--------------------------------+
```

## Workflow Phases

The right panel content changes based on the current phase. The chat stays constant.

### Plan Phase (default)
- User chats freely: "Create a Python course for beginners"
- AI responds with structure suggestions
- Right panel: Live course tree (chapters, lessons, content indicators)
- User clicks elements in tree to set chat context
- User uploads materials for AI context

### Generate Phase (AI working)
- AI asks confirmation: "Generate flashcards for Lesson 2?"
- User confirms via inline button or chat message
- Right panel: Progress indicator (current task, tokens, %)
- Chat shows status messages but user can still type

### Accept Phase (review results)
- Right panel: Generated content preview (theory text, flashcard list, etc.)
- User can:
  - Accept -> content saved to draft
  - Chat to refine -> "Make it simpler, add more examples" -> back to Generate
  - Reject -> content discarded, back to Plan
- After accept, returns to Plan phase

## Component Architecture

```
unified/
  UnifiedAIEditor.vue              # Split-view orchestrator (replaces tab-based layout)
  UnifiedAIEditorWindow.vue        # Window wrapper (unchanged)

  chat/
    ChatPanel.vue                  # Left side: persistent chat
    ChatMessageList.vue            # Scrollable message list
    ChatMessage.vue                # Single message (markdown, inline buttons)
    ChatInput.vue                  # Input bar + file attach + context badge
    ChatWelcome.vue                # Empty state: "Start a new course or load existing"
    index.ts

  right-panel/
    RightPanel.vue                 # Container: switches between views
    StructureView.vue              # Course tree + materials + finalize
    StructureTree.vue              # Interactive tree (chapters/lessons/content)
    StructureNode.vue              # Single tree node (chapter or lesson)
    MaterialsSection.vue           # File upload area + file list
    ProgressView.vue               # Generation progress display
    ResultView.vue                 # Generated content preview + accept/reject
    index.ts

  composables/
    useChatSession.ts              # Session lifecycle, messages, AI communication,
                                   # token tracking, file context
    useStructureView.ts            # Course tree state, context selection, finalize
    useWorkflowPhase.ts            # Phase tracking (plan/generate/accept),
                                   # progress, accept/reject actions
    useGenerationHistory.ts        # History loading + filtering (kept for History view)
    index.ts

  types/
    chat.types.ts                  # ChatMessage, ChatSession, FileContext
    structure.types.ts             # DraftStructure, Chapter, Lesson, ContentIndicator
    workflow.types.ts              # WorkflowPhase, GenerateProgress, GenerateResult
    index.ts
```

## Composable Responsibilities

### useChatSession.ts
Merges: useEditorState + usePlanMode + usePromptBuilder + useTokenBudget

- `createSession(courseId?)` - Create new or load existing authoring session
- `sendMessage(content, fileIds?)` - Send chat message, receive AI response
- `messages` - Reactive message list
- `session` - Current session (id, status, metadata)
- `tokensUsed / tokenBudget` - Token tracking
- `selectedFileIds` - Files selected for AI context
- `isLoading` - AI is processing

### useStructureView.ts
New composable for the right panel structure view.

- `draftStructure` - Reactive course tree
- `selectedContext` - Currently selected chapter/lesson (set by click)
- `setContext(type, id)` - Set chat context to a specific element
- `clearContext()` - Clear context
- `expandedNodes` - UI state for tree expand/collapse
- `finalize()` - Convert draft to real DB entities

### useWorkflowPhase.ts
Merges: useSkillExecution + plan execution logic

- `phase` - Current phase: 'plan' | 'generate' | 'accept'
- `generateProgress` - { current, total, label, percent }
- `generateResult` - Generated content for review
- `startGenerate(skillCode, targetId, params)` - Begin generation
- `acceptResult()` - Save result to draft
- `rejectResult()` - Discard, back to plan
- `requestRevision(feedback)` - Send chat message to refine

## API URL Fix (Critical)

Frontend composables currently call wrong paths:

| Frontend (broken) | Backend (correct) |
|---|---|
| `/admin/course-authoring/sessions` | `/panel/course-editor/ai/sessions` |
| `/admin/course-authoring/sessions/:id/chat` | `/panel/course-editor/ai/sessions/:id/chat` |
| `/admin/courses/:id/files` | `/panel/course-editor/manual/courses/:id/files` |

Fix: Update `authoring.api.ts` base paths to match backend.

## Backend Changes

### No new endpoints needed.
Existing endpoints cover everything:
- `POST /sessions` - Create session
- `GET /sessions/:id` - Load session (with chat history + draft)
- `POST /sessions/:id/chat` - Send message (AI responds + applies operations)
- `POST /sessions/:id/finalize` - Finalize draft to real entities
- `GET /courses/:id/sessions` - List sessions
- `DELETE /sessions/:id` - Archive session
- `GET /method-types` - Available LM types

### System prompt enhancement
Extend the CourseAuthoringService system prompt to:
- Use uploaded material as primary source
- Generate content (theory, flashcards, etc.) not just structure
- Ask for confirmation before heavy generation
- Be thorough in research and accuracy

## i18n Keys (de/en/pl)

New keys needed in `panel/aiEditor/unified.json`:

```
aiEditor.chat.welcome
aiEditor.chat.placeholder
aiEditor.chat.attachFile
aiEditor.chat.newCourse
aiEditor.chat.loadCourse
aiEditor.chat.contextLabel
aiEditor.chat.clearContext
aiEditor.structure.title
aiEditor.structure.empty
aiEditor.structure.materials
aiEditor.structure.uploadMaterial
aiEditor.structure.finalize
aiEditor.structure.finalizeConfirm
aiEditor.progress.generating
aiEditor.progress.tokens
aiEditor.result.title
aiEditor.result.accept
aiEditor.result.reject
aiEditor.result.revise
aiEditor.phase.plan
aiEditor.phase.generate
aiEditor.phase.accept
```

## What Gets Removed

- Tab-based navigation in UnifiedAIEditor.vue (Plan|Skills|Content|Prompts|History tabs)
- `usePlanMode.ts` (merged into useChatSession + useWorkflowPhase)
- `usePromptBuilder.ts` (chat replaces prompt builder)
- `useTokenBudget.ts` (merged into useChatSession)
- `useEditorState.ts` (merged into useChatSession)
- `useSkillExecution.ts` (merged into useWorkflowPhase)
- PlanModePanel.vue, PromptBuilderPanel.vue, PlanTab.vue
- SkillsTab content moves into right panel as optional view

## What Gets Kept

- HistoryTab.vue (as right panel view option)
- SkillCatalogPanel.vue (optional: accessible from chat or right panel)
- GenerationResultPanel.vue patterns (reused in ResultView.vue)
- All authoring types (Session, ChatMessage, DraftStructure, CourseFile)
- Backend completely unchanged (except system prompt improvement)

## Verification

1. `npm run build` passes
2. AI Editor opens in split-view (chat left, structure right)
3. User can chat to create course structure
4. Structure appears live in right panel
5. Click on structure element sets chat context
6. Material upload works and AI uses it as context
7. AI asks confirmation before generating content
8. Progress shown during generation
9. Result preview with accept/reject/revise
10. Finalize creates real DB entities
11. i18n complete (de/en/pl)
12. Dark mode correct
13. Pop-out window works with new layout

## Estimated Scope

| Area | New Files | Changed Files | LOC (new) |
|---|---|---|---|
| Chat components | 6 | 0 | ~800 |
| Right panel components | 7 | 0 | ~900 |
| Composables | 4 | 0 | ~600 |
| Types | 3 | 0 | ~150 |
| Orchestrator rewrite | 0 | 1 | ~200 |
| API URL fix | 0 | 1 | ~20 |
| i18n | 0 | 3 | ~100 |
| Backend prompt | 0 | 1 | ~50 |
| **Total** | **20** | **6** | **~2,820** |
