/**
 * TTS API - Text-to-Speech Service
 *
 * Handles:
 * - TTS audio generation with caching
 * - Voice selection
 * - Tutor script generation
 */

import http from './http'

// ============================================================================
// Types
// ============================================================================

export interface TTSSpeakRequest {
  text: string
  voice?: string
  speed?: number
  provider?: 'edge' | 'openai'
}

export interface TTSSpeakResponse {
  audio_url: string
  audio_path: string
  from_cache: boolean
  duration_ms: number
  text_length: number
  voice: string
  voice_name?: string
  provider: string
  is_free: boolean
  cost_saved?: number
}

export interface VoiceInfo {
  name: string
  gender: string
  style: string
  provider?: string
  is_free?: boolean
}

export interface VoicesResponse {
  edge: Record<string, VoiceInfo>
  openai: Record<string, VoiceInfo>
  all_voices: Record<string, VoiceInfo>
  default: string
  default_provider: string
  edge_available: boolean
  recommended: Array<{ voice: string; name: string; description: string }>
}

// Default tutor voice (Piper TTS - free, offline, high quality!)
export const DEFAULT_TUTOR_VOICE = 'thorsten'

export interface TutorScriptStep {
  id: string
  text: string
}

export interface TutorScriptRequest {
  steps: TutorScriptStep[]
  voice?: string
  speed?: number
}

export interface TutorScriptResultStep {
  id: string
  audio_url: string
  audio_path: string
  duration_ms: number
  from_cache: boolean
}

export interface TutorScriptResponse {
  script: TutorScriptResultStep[]
  total_duration_ms: number
  from_cache_count: number
  generated_count: number
  voice: string
  voice_name?: string
  speed: number
  provider: string
  is_free: boolean
}

// ============================================================================
// API Functions
// ============================================================================

export const ttsApi = {
  /**
   * Generate TTS audio from text (with caching)
   * Uses Edge TTS by default (FREE, premium quality!)
   */
  async speak(request: TTSSpeakRequest): Promise<{ success: boolean; data?: TTSSpeakResponse; error?: any }> {
    try {
      const response = await http.post('/tts/speak', {
        text: request.text,
        voice: request.voice || DEFAULT_TUTOR_VOICE,
        speed: request.speed || 1.0,
        provider: request.provider || 'edge'
      })
      return response.data
    } catch (error: any) {
      console.error('TTS speak error:', error)
      return {
        success: false,
        error: error.response?.data?.error || { message: error.message }
      }
    }
  },

  /**
   * Get available TTS voices
   */
  async getVoices(): Promise<{ success: boolean; data?: VoicesResponse; error?: any }> {
    try {
      const response = await http.get('/tts/voices')
      return response.data
    } catch (error: any) {
      console.error('TTS voices error:', error)
      return {
        success: false,
        error: error.response?.data?.error || { message: error.message }
      }
    }
  },

  /**
   * Generate a complete tutor script with pre-cached audio
   * Uses Edge TTS by default (FREE!)
   */
  async generateTutorScript(request: TutorScriptRequest): Promise<{ success: boolean; data?: TutorScriptResponse; error?: any }> {
    try {
      const response = await http.post('/tts/tutor-script', {
        steps: request.steps,
        voice: request.voice || DEFAULT_TUTOR_VOICE,
        speed: request.speed || 1.0
      })
      return response.data
    } catch (error: any) {
      console.error('Tutor script error:', error)
      return {
        success: false,
        error: error.response?.data?.error || { message: error.message }
      }
    }
  },

  /**
   * Get direct audio URL for playback
   */
  getAudioUrl(audioId: string): string {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'
    return `${baseUrl}/api/v1/tts/audio/${audioId}`
  },

  /**
   * Stream TTS audio directly (no caching)
   */
  async speakStream(request: TTSSpeakRequest): Promise<Blob | null> {
    try {
      const response = await http.post('/tts/speak-stream', {
        text: request.text,
        voice: request.voice || DEFAULT_TUTOR_VOICE,
        speed: request.speed || 1.0
      }, {
        responseType: 'blob'
      })
      return response.data
    } catch (error: any) {
      console.error('TTS stream error:', error)
      return null
    }
  }
}

// ============================================================================
// Helper: Piper TTS Voice List (High-quality, offline, free!)
// ============================================================================

export const PIPER_VOICES = {
  // German (Deutschland) - Premium Neural Voice
  'thorsten': { name: 'Thorsten', gender: 'male', style: 'natural' },
} as const

export type PiperVoiceKey = keyof typeof PIPER_VOICES

// OpenAI Voices (paid fallback)
export const OPENAI_VOICES = {
  'alloy': { name: 'Alloy', gender: 'neutral', style: 'balanced' },
  'echo': { name: 'Echo', gender: 'male', style: 'warm' },
  'fable': { name: 'Fable', gender: 'neutral', style: 'expressive' },
  'onyx': { name: 'Onyx', gender: 'male', style: 'deep' },
  'nova': { name: 'Nova', gender: 'female', style: 'friendly' },
  'shimmer': { name: 'Shimmer', gender: 'female', style: 'soft' },
} as const

export type OpenAIVoiceKey = keyof typeof OPENAI_VOICES

// ============================================================================
// Helper: Browser TTS Fallback
// ============================================================================

export const browserTTS = {
  /**
   * Check if browser TTS is available
   */
  isAvailable(): boolean {
    return 'speechSynthesis' in window
  },

  /**
   * Speak text using browser TTS
   */
  speak(text: string, options?: { lang?: string; rate?: number; pitch?: number }): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.isAvailable()) {
        reject(new Error('Browser TTS not available'))
        return
      }

      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = options?.lang || 'de-DE'
      utterance.rate = options?.rate || 1.0
      utterance.pitch = options?.pitch || 1.0

      utterance.onend = () => resolve()
      utterance.onerror = (e) => reject(e)

      window.speechSynthesis.speak(utterance)
    })
  },

  /**
   * Stop all browser TTS
   */
  stop(): void {
    if (this.isAvailable()) {
      window.speechSynthesis.cancel()
    }
  },

  /**
   * Get available browser voices
   */
  getVoices(): SpeechSynthesisVoice[] {
    if (!this.isAvailable()) return []
    return window.speechSynthesis.getVoices()
  }
}

export default ttsApi

// ============================================================================
// Tutor Knowledge API
// ============================================================================

export interface TutorKnowledgeRequest {
  course_id?: string
  chapter_id?: string
  lesson_id?: number
  method_id?: string
  include_files?: boolean
  include_progress?: boolean
}

export interface CourseContext {
  course: {
    id: string
    title: string
    subtitle?: string
    description?: string
    learning_objectives?: string[]
    target_audience?: string
    prerequisites?: string
    difficulty: string
    language: string
    duration_hours?: number
    category?: string
  }
  chapters: Array<{
    id: string
    title: string
    description?: string
    order: number
    lesson_count: number
    method_count: number
  }>
  total_chapters: number
  total_lessons: number
}

export interface ChapterContext {
  chapter: {
    id: string
    title: string
    description?: string
    order: number
    course_id: string
    course_title: string
  }
  lessons: Array<{
    id: string
    title: string
    type: string
    content_preview?: string
    order: number
    duration_minutes?: number
  }>
  learning_methods: Array<{
    id: string
    type: number
    title: string
    instructions?: string
    difficulty?: string
    order: number
  }>
}

export interface TutorKnowledgeResponse {
  context_prompt: string
  course?: CourseContext
  chapter?: ChapterContext
  lesson?: any
  method?: any
}

export const tutorApi = {
  /**
   * Load tutor knowledge from DB/course content
   */
  async getKnowledge(request: TutorKnowledgeRequest): Promise<{ success: boolean; data?: TutorKnowledgeResponse; error?: any }> {
    try {
      const response = await http.post('/tutor/knowledge', request)
      return response.data
    } catch (error: any) {
      console.error('Tutor knowledge error:', error)
      return {
        success: false,
        error: error.response?.data?.error || { message: error.message }
      }
    }
  },

  /**
   * Get course context for tutor
   */
  async getCourseContext(courseId: string): Promise<{ success: boolean; data?: CourseContext; error?: any }> {
    try {
      const response = await http.get(`/tutor/course/${courseId}/context`)
      return response.data
    } catch (error: any) {
      console.error('Course context error:', error)
      return {
        success: false,
        error: error.response?.data?.error || { message: error.message }
      }
    }
  },

  /**
   * Get chapter context for tutor
   */
  async getChapterContext(chapterId: string): Promise<{ success: boolean; data?: ChapterContext; error?: any }> {
    try {
      const response = await http.get(`/tutor/chapter/${chapterId}/context`)
      return response.data
    } catch (error: any) {
      console.error('Chapter context error:', error)
      return {
        success: false,
        error: error.response?.data?.error || { message: error.message }
      }
    }
  }
}
