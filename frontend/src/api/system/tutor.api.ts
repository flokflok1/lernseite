/**
 * Tutor API - API functions for the 3D AI Tutor Companion
 *
 * Supports context-aware tutoring with course/chapter/lesson knowledge.
 */

import http from '../http'

// Types
export interface TutorChatRequest {
  message: string
  context?: string
  systemPrompt?: string
  history?: Array<{
    role: 'user' | 'assistant'
    content: string
  }>
  // Context IDs for knowledge-aware responses
  courseId?: string
  chapterId?: string
  lessonId?: number | string
  methodId?: string
}

export interface TutorChatResponse {
  message: string
  tokens_used?: number
  context_used?: boolean  // True if course/chapter context was loaded
}

export interface TutorTTSRequest {
  text: string
  voice?: string  // alloy, echo, fable, onyx, nova, shimmer
}

/**
 * Send a chat message to the tutor
 */
export const tutorChat = async (request: TutorChatRequest): Promise<TutorChatResponse> => {
  const response = await http.post<{
    success: boolean
    data: TutorChatResponse
  }>('/tutor/chat', request, {
    timeout: 60000  // 60 seconds for AI response
  })
  return response.data.data
}

/**
 * Get TTS audio for text
 * Returns a blob URL that can be played with Audio()
 */
export const tutorTTS = async (request: TutorTTSRequest): Promise<string> => {
  const response = await http.post('/tutor/tts', request, {
    responseType: 'blob',
    timeout: 30000
  })

  // Create blob URL for audio playback
  const blob = new Blob([response.data], { type: 'audio/mpeg' })
  return URL.createObjectURL(blob)
}

/**
 * Get available TTS voices
 */
export const getTTSVoices = async (): Promise<string[]> => {
  const response = await http.get<{
    success: boolean
    data: { voices: string[] }
  }>('/tutor/voices')
  return response.data.data.voices
}
