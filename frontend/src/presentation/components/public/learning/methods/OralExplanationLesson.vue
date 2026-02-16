<script setup lang="ts">
/**
 * OralExplanationLesson - LM24 Mündliche Erklärung
 *
 * Interactive oral examination simulation where learners explain
 * concepts verbally and receive AI-powered feedback.
 *
 * Features:
 * - Audio recording with Speech-to-Text
 * - AI examiner simulation
 * - Real-time transcription
 * - Detailed feedback on oral explanations
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { AudioRecorder } from '@/presentation/components/public/learning/audio'
// import { analyzeOralExplanation, transcribeAudio } from '@/application/services/api/panel-user'
// import { tutorChat, tutorTTS } from '@/application/services/api/panel-user'
// TODO: Implement analyzeOralExplanation, transcribeAudio, tutorChat, tutorTTS APIs in @/application/services/api/learning domain

const { t } = useI18n()

// Props
const props = defineProps<{
  lesson: {
    lesson_id: string
    title: string
    content?: {
      data?: {
        topic: string
        format: string
        examiner_persona: string
        difficulty: string
        topic_blocks?: Array<{
          topic: string
          key_points: string
        }>
        duration_minutes: number
        allow_thinking_time: boolean
        allow_retry: boolean
        use_audio: boolean
        show_transcript: boolean
        criteria: {
          content: boolean
          structure: boolean
          clarity: boolean
          reactions: boolean
        }
      }
    }
  }
  courseId: string
  chapterId: string
}>()

// Emits
const emit = defineEmits<{
  (e: 'completed'): void
  (e: 'continue'): void
}>()

// State
const phase = ref<'intro' | 'question' | 'answer' | 'feedback' | 'complete'>('intro')
const currentBlockIndex = ref(0)
const isLoading = ref(false)
const isPlayingAudio = ref(false)
const error = ref<string | null>(null)

// Chat/Exam state
const examinerMessages = ref<Array<{
  role: 'examiner' | 'user'
  content: string
  timestamp: Date
  audioUrl?: string
}>>([])
const currentQuestion = ref('')
const userAnswer = ref('')
const transcription = ref('')
const feedbackResult = ref<{
  score: number
  feedback: string
  covered_points: string[]
  missing_points: string[]
  suggestions: string[]
} | null>(null)

// Refs
const audioRecorderRef = ref<InstanceType<typeof AudioRecorder> | null>(null)

// Computed
const methodData = computed(() => props.lesson.content?.data || {
  topic: t('lesson.oral.defaultTopic'),
  format: 'interview',
  examiner_persona: 'formal',
  difficulty: 'medium',
  topic_blocks: [],
  duration_minutes: 15,
  allow_thinking_time: true,
  allow_retry: false,
  use_audio: true,
  show_transcript: true,
  criteria: {
    content: true,
    structure: true,
    clarity: true,
    reactions: true
  }
})

const currentBlock = computed(() => {
  return methodData.value.topic_blocks?.[currentBlockIndex.value]
})

const totalBlocks = computed(() => {
  return methodData.value.topic_blocks?.length || 1
})

const progressPercent = computed(() => {
  return ((currentBlockIndex.value + 1) / totalBlocks.value) * 100
})

const examinerPersonaLabel = computed(() => {
  const persona = methodData.value.examiner_persona
  return t(`lesson.oral.personas.${persona}`)
})

// System prompt for the examiner
const _examinerSystemPrompt = computed(() => {
  const persona = methodData.value.examiner_persona
  const personaPrompt = t(`lesson.oral.systemPrompts.${persona}`)

  return `${personaPrompt}

${t('lesson.oral.systemPrompts.examContext', {
  topic: methodData.value.topic,
  difficulty: methodData.value.difficulty,
  format: methodData.value.format
})}

${t('lesson.oral.systemPrompts.rules')}`
})

// Methods
const startExam = async () => {
  phase.value = 'question'
  isLoading.value = true
  error.value = null

  try {
    // Generate first question
    const questionTopic = currentBlock.value?.topic || methodData.value.topic

    // TODO: Implement tutorChat API call
    // Stub response for now
    const response = {
      message: t('lesson.oral.stubQuestion', { topic: questionTopic }) || `Please explain the concept of ${questionTopic}. Take your time and provide a comprehensive explanation.`
    }

    currentQuestion.value = response.message
    examinerMessages.value.push({
      role: 'examiner',
      content: response.message,
      timestamp: new Date()
    })

    // TTS for the question using Web Speech API
    if (methodData.value.use_audio) {
      try {
        // TODO: Implement tutorTTS API call
        // Using Web Speech API as fallback for now
        const utterance = new SpeechSynthesisUtterance(response.message)
        utterance.lang = 'de-DE'
        utterance.rate = 0.95
        window.speechSynthesis.speak(utterance)
        // Store stub audioUrl
        examinerMessages.value[examinerMessages.value.length - 1].audioUrl = 'web-speech-api://stub'
      } catch (e) {
        console.warn('TTS failed:', e)
      }
    }

  } catch (e: any) {
    error.value = e.message || t('lesson.oral.errors.startFailed')
  } finally {
    isLoading.value = false
  }
}

const handleRecording = async (_blob: Blob, _duration: number) => {
  phase.value = 'answer'
  isLoading.value = true
  error.value = null

  try {
    // Get expected points from current block
    const expectedPoints = currentBlock.value?.key_points
      ? currentBlock.value.key_points.split('\n').filter(p => p.trim())
      : []

    // TODO: Implement analyzeOralExplanation API call
    // Stub response for now - in production, would use actual speech-to-text and AI analysis
    const result = {
      transcription: `[Stub transcription: User provided an oral explanation on topic]`,
      analysis: {
        score: 75,
        feedback: t('lesson.oral.stubAnalysisFeedback') || 'Your explanation covers the main points well.',
        covered_points: expectedPoints.slice(0, Math.min(2, expectedPoints.length)),
        missing_points: expectedPoints.slice(2),
        suggestions: [
          'Try to provide more specific examples',
          'Use clearer transitions between ideas'
        ]
      }
    }

    transcription.value = result.transcription
    userAnswer.value = result.transcription

    // Add user message
    examinerMessages.value.push({
      role: 'user',
      content: result.transcription,
      timestamp: new Date()
    })

    // Generate examiner response
    // TODO: Implement tutorChat API call
    // Stub response for now
    const examinerResponse = {
      message: t('lesson.oral.stubAnalysis') || `Good attempt! You covered ${result.analysis.covered_points.length} key points. Continue with the next part of the explanation.`
    }

    currentQuestion.value = examinerResponse.message
    examinerMessages.value.push({
      role: 'examiner',
      content: examinerResponse.message,
      timestamp: new Date()
    })

    // TTS for examiner response using Web Speech API
    if (methodData.value.use_audio) {
      try {
        // TODO: Implement tutorTTS API call
        // Using Web Speech API as fallback for now
        const utterance = new SpeechSynthesisUtterance(examinerResponse.message)
        utterance.lang = 'de-DE'
        utterance.rate = 0.95
        window.speechSynthesis.speak(utterance)
        // Store stub audioUrl
        examinerMessages.value[examinerMessages.value.length - 1].audioUrl = 'web-speech-api://stub'
      } catch (e) {
        console.warn('TTS failed:', e)
      }
    }

    feedbackResult.value = result.analysis
    phase.value = 'feedback'

  } catch (e: any) {
    error.value = e.message || t('lesson.oral.errors.analysisFailed')
    phase.value = 'question'
  } finally {
    isLoading.value = false
  }
}

const handleTextAnswer = async () => {
  if (!userAnswer.value.trim()) return

  phase.value = 'answer'
  isLoading.value = true
  error.value = null

  try {
    // Add user message
    examinerMessages.value.push({
      role: 'user',
      content: userAnswer.value,
      timestamp: new Date()
    })

    // Generate examiner response with feedback
    // TODO: Implement tutorChat API call
    // Stub response for now
    const examinerResponse = {
      message: t('lesson.oral.stubEvaluation') || 'Thank you for your answer. Let me ask you a follow-up question...'
    }

    currentQuestion.value = examinerResponse.message
    examinerMessages.value.push({
      role: 'examiner',
      content: examinerResponse.message,
      timestamp: new Date()
    })

    // TTS for examiner response using Web Speech API
    if (methodData.value.use_audio) {
      try {
        // TODO: Implement tutorTTS API call
        // Using Web Speech API as fallback for now
        const utterance = new SpeechSynthesisUtterance(examinerResponse.message)
        utterance.lang = 'de-DE'
        utterance.rate = 0.95
        window.speechSynthesis.speak(utterance)
        // Store stub audioUrl
        examinerMessages.value[examinerMessages.value.length - 1].audioUrl = 'web-speech-api://stub'
      } catch (e) {
        console.warn('TTS failed:', e)
      }
    }

    userAnswer.value = ''
    phase.value = 'question'

  } catch (e: any) {
    error.value = e.message || t('lesson.oral.errors.processingFailed')
    phase.value = 'question'
  } finally {
    isLoading.value = false
  }
}

const nextBlock = () => {
  if (currentBlockIndex.value < totalBlocks.value - 1) {
    currentBlockIndex.value++
    feedbackResult.value = null
    phase.value = 'question'
    startExam()
  } else {
    completeExam()
  }
}

const completeExam = async () => {
  phase.value = 'complete'

  // Generate final summary
  isLoading.value = true
  try {
    // TODO: Implement tutorChat API call
    // Stub response for now
    const summaryResponse = {
      message: t('lesson.oral.stubSummary') || 'Excellent oral examination! You have demonstrated good understanding of the topic. Well done!'
    }

    examinerMessages.value.push({
      role: 'examiner',
      content: summaryResponse.message,
      timestamp: new Date()
    })

    if (methodData.value.use_audio) {
      try {
        // TODO: Implement tutorTTS API call
        // Using Web Speech API as fallback for now
        const utterance = new SpeechSynthesisUtterance(summaryResponse.message)
        utterance.lang = 'de-DE'
        utterance.rate = 0.95
        window.speechSynthesis.speak(utterance)
        // Store stub audioUrl
        examinerMessages.value[examinerMessages.value.length - 1].audioUrl = 'web-speech-api://stub'
      } catch (e) {
        console.warn('TTS failed:', e)
      }
    }

  } catch (e) {
    console.error('Failed to generate summary:', e)
  } finally {
    isLoading.value = false
  }

  emit('completed')
}

const playAudio = (url: string) => {
  if (isPlayingAudio.value) return

  const audio = new Audio(url)
  isPlayingAudio.value = true

  audio.onended = () => {
    isPlayingAudio.value = false
  }
  audio.onerror = () => {
    isPlayingAudio.value = false
  }

  audio.play()
}

const retryAnswer = () => {
  feedbackResult.value = null
  phase.value = 'question'
  audioRecorderRef.value?.reset()
}
</script>

<template>
  <div class="oral-explanation-lesson">
    <!-- Intro Phase -->
    <div v-if="phase === 'intro'" class="text-center py-8">
      <div class="max-w-2xl mx-auto">
        <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
          <svg class="w-10 h-10 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </div>

        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('lesson.oral.title') }}
        </h2>

        <p class="text-gray-600 dark:text-gray-300 mb-6">
          {{ methodData.topic }}
        </p>

        <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 mb-6 text-left">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ $t('lesson.oral.examDetails') }}:</h3>
          <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-300">
            <li class="flex items-center gap-2">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              {{ $t('lesson.oral.examiner') }}: {{ examinerPersonaLabel }}
            </li>
            <li class="flex items-center gap-2">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              {{ $t('lesson.oral.topicBlocks') }}: {{ totalBlocks }}
            </li>
            <li class="flex items-center gap-2">
              <span class="w-2 h-2 bg-purple-500 rounded-full"></span>
              {{ $t('lesson.oral.duration') }}: {{ $t('lesson.oral.durationValue', { minutes: methodData.duration_minutes }) }}
            </li>
            <li v-if="methodData.use_audio" class="flex items-center gap-2">
              <span class="w-2 h-2 bg-green-500 rounded-full"></span>
              {{ $t('lesson.oral.audioEnabled') }}
            </li>
          </ul>
        </div>

        <button
          @click="startExam"
          :disabled="isLoading"
          class="px-8 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 disabled:opacity-50 transition-colors"
        >
          {{ $t('lesson.oral.startExam') }}
        </button>
      </div>
    </div>

    <!-- Question/Answer Phase -->
    <div v-else-if="phase === 'question' || phase === 'answer'" class="space-y-6">
      <!-- Progress Bar -->
      <div class="bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-6">
        <div
          class="bg-purple-600 h-2 rounded-full transition-all duration-300"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>

      <!-- Chat History -->
      <div class="space-y-4 max-h-[400px] overflow-y-auto p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
        <div
          v-for="(message, index) in examinerMessages"
          :key="index"
          class="flex"
          :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[80%] rounded-2xl px-4 py-3"
            :class="message.role === 'user'
              ? 'bg-purple-600 text-white rounded-br-none'
              : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-none shadow-sm'"
          >
            <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
            <div class="flex items-center justify-between mt-2">
              <span class="text-xs opacity-60">
                {{ new Date(message.timestamp).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) }}
              </span>
              <button
                v-if="message.audioUrl"
                @click="playAudio(message.audioUrl)"
                class="text-xs opacity-60 hover:opacity-100 flex items-center gap-1"
              >
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
                </svg>
                {{ $t('lesson.oral.play') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Typing indicator -->
        <div v-if="isLoading" class="flex justify-start">
          <div class="bg-white dark:bg-gray-700 rounded-2xl rounded-bl-none px-4 py-3">
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-xl">
        {{ error }}
      </div>

      <!-- Answer Input -->
      <div v-if="!isLoading" class="space-y-4">
        <!-- Audio Recording -->
        <div v-if="methodData.use_audio">
          <AudioRecorder
            ref="audioRecorderRef"
            :max-duration="120"
            @recorded="handleRecording"
          />
        </div>

        <!-- Or Text Input -->
        <div class="relative">
          <span v-if="methodData.use_audio" class="absolute -top-3 left-4 px-2 bg-white dark:bg-gray-900 text-xs text-gray-500">
            {{ $t('lesson.oral.orWriteAnswer') }}
          </span>
          <textarea
            v-model="userAnswer"
            rows="3"
            :placeholder="$t('lesson.oral.answerPlaceholder')"
            class="w-full px-4 py-3 border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
            @keydown.enter.ctrl="handleTextAnswer"
          ></textarea>
          <button
            v-if="!methodData.use_audio || userAnswer.trim()"
            @click="handleTextAnswer"
            :disabled="!userAnswer.trim() || isLoading"
            class="absolute bottom-3 right-3 p-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Feedback Phase -->
    <div v-else-if="phase === 'feedback'" class="space-y-6">
      <!-- Transcription -->
      <div v-if="methodData.show_transcript && transcription" class="bg-gray-50 dark:bg-gray-800 rounded-xl p-4">
        <h3 class="font-semibold text-gray-900 dark:text-white mb-2">{{ $t('lesson.oral.yourAnswerTranscript') }}:</h3>
        <p class="text-gray-600 dark:text-gray-300 text-sm">{{ transcription }}</p>
      </div>

      <!-- Feedback Result -->
      <div v-if="feedbackResult" class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold text-gray-900 dark:text-white">{{ $t('lesson.oral.evaluation') }}</h3>
          <div class="flex items-center gap-2">
            <div
              class="w-16 h-16 rounded-full flex items-center justify-center font-bold text-xl"
              :class="feedbackResult.score >= 70 ? 'bg-green-100 text-green-700' : feedbackResult.score >= 50 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'"
            >
              {{ feedbackResult.score }}%
            </div>
          </div>
        </div>

        <p class="text-gray-600 dark:text-gray-300 mb-4">{{ feedbackResult.feedback }}</p>

        <!-- Covered Points -->
        <div v-if="feedbackResult.covered_points.length > 0" class="mb-4">
          <h4 class="text-sm font-medium text-green-700 dark:text-green-400 mb-2">{{ $t('lesson.oral.coveredPoints') }}:</h4>
          <ul class="space-y-1">
            <li v-for="point in feedbackResult.covered_points" :key="point" class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
              <svg class="w-4 h-4 text-green-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
              {{ point }}
            </li>
          </ul>
        </div>

        <!-- Missing Points -->
        <div v-if="feedbackResult.missing_points.length > 0" class="mb-4">
          <h4 class="text-sm font-medium text-red-700 dark:text-red-400 mb-2">{{ $t('lesson.oral.missingPoints') }}:</h4>
          <ul class="space-y-1">
            <li v-for="point in feedbackResult.missing_points" :key="point" class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
              <svg class="w-4 h-4 text-red-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
              </svg>
              {{ point }}
            </li>
          </ul>
        </div>

        <!-- Suggestions -->
        <div v-if="feedbackResult.suggestions.length > 0">
          <h4 class="text-sm font-medium text-blue-700 dark:text-blue-400 mb-2">{{ $t('lesson.oral.suggestions') }}:</h4>
          <ul class="space-y-1">
            <li v-for="suggestion in feedbackResult.suggestions" :key="suggestion" class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-300">
              <svg class="w-4 h-4 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
              </svg>
              {{ suggestion }}
            </li>
          </ul>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-center gap-4">
        <button
          v-if="methodData.allow_retry"
          @click="retryAnswer"
          class="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          {{ $t('lesson.oral.retryAnswer') }}
        </button>
        <button
          @click="nextBlock"
          class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          {{ currentBlockIndex < totalBlocks - 1 ? $t('lesson.oral.nextBlock') : $t('lesson.oral.completeExam') }}
        </button>
      </div>
    </div>

    <!-- Complete Phase -->
    <div v-else-if="phase === 'complete'" class="text-center py-8">
      <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
        <svg class="w-10 h-10 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        {{ $t('lesson.oral.examCompleted') }}
      </h2>

      <!-- Final Summary -->
      <div v-if="examinerMessages.length > 0" class="max-w-2xl mx-auto mb-6">
        <div class="bg-gray-50 dark:bg-gray-800 rounded-xl p-6 text-left">
          <h3 class="font-semibold text-gray-900 dark:text-white mb-3">{{ $t('lesson.oral.finalEvaluation') }}:</h3>
          <p class="text-gray-600 dark:text-gray-300">
            {{ examinerMessages[examinerMessages.length - 1].content }}
          </p>
        </div>
      </div>

      <button
        @click="emit('continue')"
        class="px-8 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700 transition-colors"
      >
        {{ $t('common.continue') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.oral-explanation-lesson {
  min-height: 400px;
}
</style>
