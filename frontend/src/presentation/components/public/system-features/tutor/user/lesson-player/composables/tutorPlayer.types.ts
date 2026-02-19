/**
 * Types for useTutorPlayer composable
 */

export interface SchemaRow {
  name: string
  operator: string
  value: string
  highlight?: boolean
}

export interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear' | 'schema'
  content?: string
  position?: { x: number; y: number }
  endPosition?: { x: number; y: number }
  duration?: number
  color?: string
  fontSize?: number
  schema?: SchemaRow[]
}

export interface TutorialStep {
  title: string
  speech: string
  calculator?: string
  result?: string
  schema?: SchemaRow[]
  whiteboardActions?: WhiteboardAction[]
}

export interface ExplanationListItem {
  explanationId: string
  title: string
  style: string
  hasAudio: boolean
  tokensUsed: number
  createdAt: string
  updatedAt: string
}
