/**
 * Theory Generation Types
 *
 * TypeScript interfaces for theory content generation system.
 * Used in course-editor for chapter theory creation and management.
 */

export type TheoryStyle = 'standard' | 'compact' | 'detailed' | 'visual' | 'exam'

export interface ChapterTheory {
  theoryId: string
  chapterId: string
  title: string
  style: TheoryStyle
  overview?: string
  learningGoals?: string[]
  concepts?: Concept[]
  terms?: Term[]
  examRelevance?: string
  examTips?: string[]
  audioUrl?: string
  createdAt: Date
  updatedAt?: Date
}

export interface Concept {
  name: string
  description: string
}

export interface Term {
  term: string
  definition: string
}

export interface GenerateTheoryRequest {
  chapter_id: string
  style: TheoryStyle
  title?: string
  generate_tts: boolean
}

export interface Chapter {
  chapter_id: string
  title: string
}

export interface Course {
  course_id: string
  title: string
}

export interface TheoryGenerationState {
  chapterTheories: ChapterTheory[]
  selectedTheoryId: string | null
  selectedTheory: ChapterTheory | null
  isLoading: boolean
  isGenerating: boolean
  error: string | null
}
