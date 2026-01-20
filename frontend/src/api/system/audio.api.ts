/**
 * Audio API - Speech-to-Text, TTS, and Audio Processing
 *
 * Provides functions for:
 * - Whisper transcription (STT)
 * - Oral explanation analysis (LM24)
 * - Audio format support
 */

import http from '../http'

// Types
export interface TranscriptionResult {
  text: string
  language?: string
  duration?: number
  segments?: Array<{
    id: number
    start: number
    end: number
    text: string
  }>
}

export interface OralAnalysisResult {
  transcription: string
  duration?: number
  analysis: {
    score: number
    feedback: string
    covered_points: string[]
    missing_points: string[]
    suggestions: string[]
  }
}

export interface AudioFormatsResponse {
  formats: string[]
  max_size_mb: number
}

/**
 * Transcribe audio file to text using Whisper
 */
export const transcribeAudio = async (
  audioBlob: Blob,
  options?: {
    language?: string
    prompt?: string
  }
): Promise<TranscriptionResult> => {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')

  if (options?.language) {
    formData.append('language', options.language)
  }
  if (options?.prompt) {
    formData.append('prompt', options.prompt)
  }

  const response = await http.post<{
    success: boolean
    data: TranscriptionResult
  }>('/audio/transcribe', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 120000 // 2 minutes for long audio
  })

  return response.data.data
}

/**
 * Transcribe audio from base64-encoded data
 */
export const transcribeAudioBase64 = async (
  audioBase64: string,
  format: string = 'webm',
  options?: {
    language?: string
    prompt?: string
  }
): Promise<TranscriptionResult> => {
  const response = await http.post<{
    success: boolean
    data: TranscriptionResult
  }>('/audio/transcribe-base64', {
    audio: audioBase64,
    format,
    language: options?.language,
    prompt: options?.prompt
  }, {
    timeout: 120000
  })

  return response.data.data
}

/**
 * Analyze oral explanation for LM24 (Mündliche Erklärung)
 */
export const analyzeOralExplanation = async (
  audioBlob: Blob,
  options: {
    topic: string
    expectedPoints?: string[]
    language?: string
  }
): Promise<OralAnalysisResult> => {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')
  formData.append('topic', options.topic)

  if (options.expectedPoints && options.expectedPoints.length > 0) {
    formData.append('expected_points', JSON.stringify(options.expectedPoints))
  }
  if (options.language) {
    formData.append('language', options.language)
  }

  const response = await http.post<{
    success: boolean
    data: OralAnalysisResult
  }>('/audio/analyze-oral', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 180000 // 3 minutes for transcription + analysis
  })

  return response.data.data
}

/**
 * Get supported audio formats
 */
export const getSupportedAudioFormats = async (): Promise<AudioFormatsResponse> => {
  const response = await http.get<{
    success: boolean
    data: AudioFormatsResponse
  }>('/audio/supported-formats')

  return response.data.data
}
