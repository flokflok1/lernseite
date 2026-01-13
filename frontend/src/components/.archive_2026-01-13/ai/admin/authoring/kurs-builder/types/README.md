# KursBuilder Types Package

TypeScript type definitions for the KI-Kurs-Builder component.

## 📦 Package Structure

```
types/
├── index.ts                  # Barrel export (import from here)
├── session.types.ts          # Session & Chat types
├── course.types.ts           # Course structure (Course → Chapter → Lesson)
├── file.types.ts             # File management & uploads
├── action.types.ts           # Actions & workflows
├── theory.types.ts           # Theory content & explanations
├── lm.types.ts               # Learning method suggestions
└── README.md                 # This file
```

## 🎯 Usage

### Recommended Import (Barrel Export)

```typescript
import type {
  Session,
  ChatMessage,
  Course,
  Chapter,
  QuickAction,
  LMSuggestion
} from '@/components/admin/ai-operations/authoring/kurs-builder/types'
```

### Direct Import (If Needed)

```typescript
import type { Session } from '@/components/admin/ai-operations/authoring/kurs-builder/types/session.types'
import type { Course } from '@/components/admin/ai-operations/authoring/kurs-builder/types/course.types'
```

## 📋 Type Categories

### 1. Session Types (`session.types.ts`)

Core session management and chat functionality.

- **Session** - Authoring session
- **ChatMessage** - User/AI messages
- **SessionStats** - Session statistics

### 2. Course Types (`course.types.ts`)

Hierarchical course structure.

- **Course** - Top-level course
- **Chapter** - Course chapter
- **Lesson** - Chapter lesson
- **LearningMethodInstance** - LM instance
- **DraftStructure** - Draft state
- **DraftStats** - Draft statistics

### 3. File Types (`file.types.ts`)

File management for course materials.

- **CourseFile** - Uploaded file
- **FileUploadProgress** - Upload tracking
- **FileSelectionState** - Selection state

### 4. Action Types (`action.types.ts`)

AI-assisted authoring actions.

- **QuickAction** - Quick action buttons
- **ContextAction** - Context-sensitive actions
- **PendingAction** - Actions awaiting confirmation
- **SelectedContext** - Current selection (chapter/lesson)
- **WorkflowState** - Workflow process state

### 5. Theory Types (`theory.types.ts`)

Theory content generation.

- **Theory** - Chapter theory/summary
- **Explanation** - Lesson step-by-step explanation
- **ExplanationStep** - Single explanation step
- **TheoryGenerationRequest** - Theory gen params
- **ExplanationGenerationRequest** - Explanation gen params

### 6. Learning Method Types (`lm.types.ts`)

Learning method suggestions and configuration.

- **LearningMethodType** - LM metadata (0-11)
- **LMSuggestion** - AI-suggested LM
- **LMConfiguration** - LM instance config
- **LMSuggestionRequest** - Request params
- **LMCreationRequest** - Creation params

## 🔄 Migration Guide

### Before (Duplicated Types)

```typescript
// ChatPanel.vue
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  // ...
}

// WorkflowPanel.vue
interface ChatMessage {  // ❌ DUPLICATE
  role: 'user' | 'assistant'
  content: string
  // ...
}
```

### After (Centralized)

```typescript
// ChatPanel.vue
import type { ChatMessage } from '../types'

// WorkflowPanel.vue
import type { ChatMessage } from '../types'  // ✅ SINGLE SOURCE
```

## ✅ Benefits

1. **Single Source of Truth** - No type duplication
2. **Type Safety** - Consistent types across components
3. **Maintainability** - Update once, applies everywhere
4. **Documentation** - TSDoc comments on all types
5. **IDE Support** - Better autocomplete & IntelliSense

## 📊 Metrics

| Metric | Before | After |
|--------|--------|-------|
| Type Duplication | 5x | 0x |
| Files with Types | 5 components | 1 package |
| Total Type LOC | ~350 (duplicated) | ~280 (deduplicated) |
| Maintainability | Low | High |

## 🔧 Maintenance

When adding new types:

1. Choose appropriate file (or create new one)
2. Add TSDoc comments
3. Export from `index.ts`
4. Update this README

## 📚 Related Documentation

- [REFACTORING_ANALYSIS_KURSBUILDER.md](../../../../../../../REFACTORING_ANALYSIS_KURSBUILDER.md) - Full analysis
- [REFACTORING_ARCHITECTURE_PREVIEW.md](../../../../../../../REFACTORING_ARCHITECTURE_PREVIEW.md) - Architecture plan

---

**Created:** 2025-01-07
**Version:** 1.0.0
**Status:** ✅ Production Ready
