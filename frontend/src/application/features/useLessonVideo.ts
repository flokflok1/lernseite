/**
 * useLessonVideo - Composable for AI-generated lesson videos
 *
 * Uses Sora 2 / Sora 2 Pro for video generation.
 * Sora 2 generates VIDEO + AUDIO together (synced!) - no separate TTS needed!
 *
 * Videos are generated once per lesson and cached for repeated playback.
 *
 * Usage:
 * ```ts
 * const {
 *   generateVideo,
 *   getVideoStatus,
 *   videoUrl,
 *   isGenerating,
 *   progress,
 *   availableModels
 * } = useLessonVideo()
 *
 * // Generate video for a lesson with model selection
 * await generateVideo(lessonId, lessonTitle, teachingSteps, {
 *   model: 'sora-2-pro',  // or 'sora-2' (default)
 *   avatarStyle: 'professional_teacher'
 * })
 *
 * // Get cached video URL (includes audio!)
 * const url = await getVideoUrl(lessonId)
 * ```
 */

import { ref, computed } from 'vue'
import http from '@/infrastructure/api/http'

// Types
export interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear'
  content?: string
  position: { x: number; y: number }
  endPosition?: { x: number; y: number }
  duration: number
  color?: string
  fontSize?: number
}

export interface TeacherAnimation {
  type: 'idle' | 'talking' | 'pointing' | 'gesture' | 'thinking' | 'celebrating'
  target?: { x: number; y: number }
  duration?: number
}

export interface TeachingStep {
  speech: string
  whiteboard: WhiteboardAction[]
  animation: TeacherAnimation
  userInput?: {
    type: 'calculator' | 'answer' | 'confirm'
    prompt: string
    expectedValue?: number
    tolerance?: number
  }
}

export interface VideoGenerationResult {
  lesson_id: string
  video_id?: string
  video_url?: string           // Video includes synced audio!
  duration_ms?: number
  model: string                // 'sora-2' or 'sora-2-pro'
  model_info?: SoraModelInfo
  avatar_style?: string
  has_audio: boolean           // Always true for Sora 2
  status: 'generating' | 'ready' | 'fallback_mode' | 'api_error' | 'timeout' | 'failed'
  from_cache: boolean
  cost?: number
  message?: string
  error?: string
}

export interface SoraModelInfo {
  name: string
  description: string
  performance: 'higher' | 'highest'
  speed: 'slow' | 'slower'
  input: string[]
  output: string[]
  cost_per_second: number
  max_duration: number
}

export interface VideoStatus {
  status: 'pending' | 'generating' | 'ready' | 'failed'
  progress: number
  video_id?: string
  model?: string
  has_audio?: boolean
  error?: string
}

export interface VideoGenerationOptions {
  avatarStyle?: string
  model?: 'sora-2' | 'sora-2-pro'
  language?: string
  forceRegenerate?: boolean
}

export interface AvatarStyle {
  name: string
  description: string
  thumbnail: string
}

// State
const isGenerating = ref(false)
const progress = ref(0)
const currentVideoId = ref<string | null>(null)
const videoUrl = ref<string | null>(null)
const currentModel = ref<string>('sora-2')
const error = ref<string | null>(null)
const soraAvailable = ref(false)
const availableModels = ref<Record<string, SoraModelInfo>>({})
const hasAudio = ref(true) // Sora 2 always includes audio

// Check Sora API availability and load models
async function checkSoraStatus(): Promise<boolean> {
  try {
    const response = await http.get('/video/sora-status')
    if (response.data.success) {
      soraAvailable.value = response.data.data.sora_available
      availableModels.value = response.data.data.models || {}
      return soraAvailable.value
    }
    return false
  } catch (e) {
    console.warn('Could not check Sora status:', e)
    return false
  }
}

// Get available Sora models
async function getAvailableModels(): Promise<Record<string, SoraModelInfo>> {
  try {
    const response = await http.get('/video/models')
    if (response.data.success) {
      availableModels.value = response.data.data.models || {}
      return availableModels.value
    }
    return {}
  } catch (e) {
    console.warn('Could not get models:', e)
    return {}
  }
}

// Generate video for a lesson
async function generateVideo(
  lessonId: string,
  lessonTitle: string,
  teachingSteps: TeachingStep[],
  options: VideoGenerationOptions = {}
): Promise<VideoGenerationResult> {
  const {
    avatarStyle = 'professional_teacher',
    model = 'sora-2',
    language = 'de',
    forceRegenerate = false
  } = options

  isGenerating.value = true
  progress.value = 0
  error.value = null
  currentModel.value = model

  try {
    const response = await http.post(`/lessons/${lessonId}/video`, {
      lesson_title: lessonTitle,
      teaching_steps: teachingSteps,
      avatar_style: avatarStyle,
      model: model,          // 'sora-2' or 'sora-2-pro'
      language: language,
      force_regenerate: forceRegenerate
    })

    if (response.data.success) {
      const result = response.data.data as VideoGenerationResult

      currentVideoId.value = result.video_id || null
      videoUrl.value = result.video_url || null
      currentModel.value = result.model || model
      hasAudio.value = result.has_audio ?? true

      // Update progress based on status
      if (result.status === 'ready') {
        progress.value = 100
      } else if (result.status === 'generating') {
        // Poll for status
        await pollVideoStatus(lessonId)
      } else if (result.status === 'fallback_mode') {
        progress.value = 100
        // Fallback mode - use current animated teacher
      }

      return result
    }

    throw new Error(response.data.error?.message || 'Video generation failed')
  } catch (e: any) {
    error.value = e.message || 'Video generation failed'
    throw e
  } finally {
    isGenerating.value = false
  }
}

// Poll video generation status
async function pollVideoStatus(lessonId: string, maxAttempts: number = 60): Promise<VideoStatus> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    const status = await getVideoStatus(lessonId)

    if (status.status === 'ready') {
      progress.value = 100
      return status
    }

    if (status.status === 'failed') {
      error.value = status.error || 'Video generation failed'
      throw new Error(status.error || 'Video generation failed')
    }

    // Update progress
    progress.value = status.progress

    // Wait before next poll (5 seconds)
    await new Promise(resolve => setTimeout(resolve, 5000))
  }

  throw new Error('Video generation timed out')
}

// Get video generation status
async function getVideoStatus(lessonId: string): Promise<VideoStatus> {
  try {
    const response = await http.get(`/lessons/${lessonId}/video/status`)

    if (response.data.success) {
      return response.data.data as VideoStatus
    }

    return {
      status: 'failed',
      progress: 0,
      error: response.data.error?.message
    }
  } catch (e: any) {
    return {
      status: 'failed',
      progress: 0,
      error: e.message
    }
  }
}

// Get video URL for a lesson (checks cache first)
async function getVideoUrl(lessonId: string): Promise<string | null> {
  try {
    const response = await http.get(`/lessons/${lessonId}/video`)

    if (response.data.success && response.data.data?.has_video) {
      return `/api/v1/lessons/${lessonId}/video`
    }

    return null
  } catch (e) {
    console.warn('Could not get video URL:', e)
    return null
  }
}

// Get audio URL for a lesson
async function getAudioUrl(lessonId: string): Promise<string | null> {
  try {
    return `/api/v1/lessons/${lessonId}/audio`
  } catch (e) {
    console.warn('Could not get audio URL:', e)
    return null
  }
}

// Delete cached video
async function deleteVideo(lessonId: string): Promise<boolean> {
  try {
    const response = await http.delete(`/lessons/${lessonId}/video`)
    return response.data.success
  } catch (e) {
    console.warn('Could not delete video:', e)
    return false
  }
}

// Get available avatar styles
async function getAvatarStyles(): Promise<Record<string, AvatarStyle>> {
  try {
    const response = await http.get('/video/avatar-styles')

    if (response.data.success) {
      return response.data.data.styles
    }

    return {}
  } catch (e) {
    console.warn('Could not get avatar styles:', e)
    return {}
  }
}

// Composable export
export function useLessonVideo() {
  return {
    // State
    isGenerating: computed(() => isGenerating.value),
    progress: computed(() => progress.value),
    currentVideoId: computed(() => currentVideoId.value),
    videoUrl: computed(() => videoUrl.value),
    currentModel: computed(() => currentModel.value),
    hasAudio: computed(() => hasAudio.value),
    error: computed(() => error.value),
    soraAvailable: computed(() => soraAvailable.value),
    availableModels: computed(() => availableModels.value),

    // Actions
    checkSoraStatus,
    getAvailableModels,
    generateVideo,
    getVideoStatus,
    getVideoUrl,
    getAudioUrl,
    deleteVideo,
    getAvatarStyles,

    // Reset state
    reset: () => {
      isGenerating.value = false
      progress.value = 0
      currentVideoId.value = null
      videoUrl.value = null
      currentModel.value = 'sora-2'
      hasAudio.value = true
      error.value = null
    }
  }
}

// Default export for convenience
export default useLessonVideo
