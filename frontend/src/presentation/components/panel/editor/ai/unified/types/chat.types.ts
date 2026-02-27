// chat.types.ts — Types for the persistent chat panel

export type MessageRole = 'user' | 'assistant' | 'system'

export interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  timestamp: string
  fileIds?: string[]
  operations?: ChatOperation[]
  confirmation?: ChatConfirmation
  isStreaming?: boolean
}

export interface ChatOperation {
  type: string
  target_type?: string
  target_id?: string
  label: string
}

export interface ChatConfirmation {
  action: string
  label: string
  skillCode?: string
  targetId?: string
  params?: Record<string, unknown>
}

export interface ChatSession {
  sessionId: string
  courseId: string
  status: 'active' | 'completed' | 'archived'
  metadata?: Record<string, unknown>
  createdAt: string
  updatedAt: string
}

export interface FileContext {
  fileId: string
  fileName: string
  fileType: string
  selected: boolean
}
