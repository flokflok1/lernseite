// structure.types.ts — Types for the right-panel structure view

export interface DraftStructure {
  courseId: string
  courseTitle: string
  chapters: DraftChapter[]
}

export interface DraftChapter {
  id: string
  title: string
  order: number
  lessons: DraftLesson[]
}

export interface DraftLesson {
  id: string
  title: string
  order: number
  contentIndicators: ContentIndicator[]
}

export interface ContentIndicator {
  type: 'theory' | 'flashcards' | 'quiz' | 'exercise' | 'method'
  label: string
  count?: number
  status: 'empty' | 'draft' | 'generated' | 'accepted'
}

export interface SelectedContext {
  type: 'chapter' | 'lesson'
  id: string
  title: string
}
