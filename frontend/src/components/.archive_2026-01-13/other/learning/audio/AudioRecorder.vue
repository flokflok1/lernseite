<script setup lang="ts">
/**
 * AudioRecorder - Reusable audio recording component
 *
 * Features:
 * - Record audio from microphone
 * - Visual waveform display
 * - Playback recorded audio
 * - Download or submit recording
 * - Configurable max duration
 */

import { ref, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Props
const props = withDefaults(defineProps<{
  maxDuration?: number  // Max recording duration in seconds (0 = unlimited)
  autoStop?: boolean    // Auto-stop when max duration reached
  showPlayback?: boolean // Show playback controls
  showDownload?: boolean // Show download button
}>(), {
  maxDuration: 120,     // 2 minutes default
  autoStop: true,
  showPlayback: true,
  showDownload: false
})

// Emits
const emit = defineEmits<{
  (e: 'recorded', blob: Blob, duration: number): void
  (e: 'started'): void
  (e: 'stopped'): void
  (e: 'error', error: string): void
}>()

// State
const isRecording = ref(false)
const isPaused = ref(false)
const isPlaying = ref(false)
const recordingTime = ref(0)
const audioUrl = ref<string | null>(null)
const audioBlob = ref<Blob | null>(null)
const hasPermission = ref<boolean | null>(null)
const errorMessage = ref<string | null>(null)
const audioLevel = ref(0)

// Refs
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let timerInterval: number | null = null
let audioContext: AudioContext | null = null
let analyser: AnalyserNode | null = null
let animationFrame: number | null = null
let audioElement: HTMLAudioElement | null = null
const canvasRef = ref<HTMLCanvasElement | null>(null)

// Computed
const formattedTime = computed(() => {
  const minutes = Math.floor(recordingTime.value / 60)
  const seconds = recordingTime.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const maxFormattedTime = computed(() => {
  if (!props.maxDuration) return ''
  const minutes = Math.floor(props.maxDuration / 60)
  const seconds = props.maxDuration % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const progressPercent = computed(() => {
  if (!props.maxDuration) return 0
  return (recordingTime.value / props.maxDuration) * 100
})

// Check microphone permission
const checkPermission = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    stream.getTracks().forEach(track => track.stop())
    hasPermission.value = true
    return true
  } catch (err) {
    hasPermission.value = false
    errorMessage.value = t('common.audio.microphoneAccessDenied')
    emit('error', errorMessage.value)
    return false
  }
}

// Start recording
const startRecording = async () => {
  errorMessage.value = null

  // Check permission first
  if (hasPermission.value === null) {
    const permitted = await checkPermission()
    if (!permitted) return
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        sampleRate: 44100
      }
    })

    // Set up audio analysis for visualization
    audioContext = new AudioContext()
    analyser = audioContext.createAnalyser()
    const source = audioContext.createMediaStreamSource(stream)
    source.connect(analyser)
    analyser.fftSize = 256

    // Start visualization
    visualize()

    // Set up media recorder
    // Try different formats for browser compatibility
    const mimeTypes = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/ogg;codecs=opus',
      'audio/mp4',
      'audio/mpeg'
    ]

    let selectedMimeType = ''
    for (const mimeType of mimeTypes) {
      if (MediaRecorder.isTypeSupported(mimeType)) {
        selectedMimeType = mimeType
        break
      }
    }

    if (!selectedMimeType) {
      throw new Error(t('common.audio.noSupportedFormat'))
    }

    mediaRecorder = new MediaRecorder(stream, {
      mimeType: selectedMimeType
    })

    audioChunks = []

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        audioChunks.push(event.data)
      }
    }

    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks, { type: selectedMimeType })
      audioBlob.value = blob
      audioUrl.value = URL.createObjectURL(blob)
      emit('recorded', blob, recordingTime.value)

      // Stop all tracks
      stream.getTracks().forEach(track => track.stop())

      // Clean up audio context
      if (audioContext) {
        audioContext.close()
        audioContext = null
      }
    }

    mediaRecorder.start(100) // Collect data every 100ms
    isRecording.value = true
    isPaused.value = false
    recordingTime.value = 0

    // Start timer
    timerInterval = window.setInterval(() => {
      if (!isPaused.value) {
        recordingTime.value++

        // Auto-stop if max duration reached
        if (props.autoStop && props.maxDuration && recordingTime.value >= props.maxDuration) {
          stopRecording()
        }
      }
    }, 1000)

    emit('started')

  } catch (err: any) {
    console.error('Recording error:', err)
    errorMessage.value = err.message || t('common.audio.recordingStartFailed')
    emit('error', errorMessage.value || t('common.unknownError'))
  }
}

// Pause/Resume recording
const togglePause = () => {
  if (!mediaRecorder) return

  if (isPaused.value) {
    mediaRecorder.resume()
    isPaused.value = false
  } else {
    mediaRecorder.pause()
    isPaused.value = true
  }
}

// Stop recording
const stopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
    isPaused.value = false

    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }

    if (animationFrame) {
      cancelAnimationFrame(animationFrame)
      animationFrame = null
    }

    emit('stopped')
  }
}

// Visualize audio levels
const visualize = () => {
  if (!analyser || !canvasRef.value) return

  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const bufferLength = analyser.frequencyBinCount
  const dataArray = new Uint8Array(bufferLength)

  const currentAnalyser = analyser
  const draw = () => {
    if (!isRecording.value || !currentAnalyser) return
    animationFrame = requestAnimationFrame(draw)

    currentAnalyser.getByteFrequencyData(dataArray)

    // Calculate average level
    const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength
    audioLevel.value = average / 255

    // Draw waveform
    ctx.fillStyle = 'rgb(31, 41, 55)' // gray-800
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    const barWidth = (canvas.width / bufferLength) * 2.5
    let x = 0

    for (let i = 0; i < bufferLength; i++) {
      const dataValue = dataArray[i] ?? 0
      const barHeight = (dataValue / 255) * canvas.height

      // Gradient from indigo to purple based on height
      const hue = 250 + (dataValue / 255) * 30
      ctx.fillStyle = `hsl(${hue}, 80%, 60%)`

      ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight)
      x += barWidth + 1
    }
  }

  draw()
}

// Play recorded audio
const playRecording = () => {
  if (!audioUrl.value) return

  if (audioElement) {
    audioElement.pause()
    audioElement = null
  }

  audioElement = new Audio(audioUrl.value)
  audioElement.onended = () => {
    isPlaying.value = false
  }
  audioElement.onpause = () => {
    isPlaying.value = false
  }

  audioElement.play()
  isPlaying.value = true
}

// Stop playback
const stopPlayback = () => {
  if (audioElement) {
    audioElement.pause()
    audioElement.currentTime = 0
    isPlaying.value = false
  }
}

// Download recording
const downloadRecording = () => {
  if (!audioUrl.value || !audioBlob.value) return

  const link = document.createElement('a')
  link.href = audioUrl.value
  link.download = `recording-${new Date().toISOString()}.webm`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Reset for new recording
const reset = () => {
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
  audioUrl.value = null
  audioBlob.value = null
  recordingTime.value = 0
  isPlaying.value = false
  errorMessage.value = null
}

// Get the recorded blob
const getBlob = () => audioBlob.value

// Expose methods
defineExpose({
  startRecording,
  stopRecording,
  reset,
  getBlob
})

// Cleanup
onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }
  if (audioContext) {
    audioContext.close()
  }
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
  if (audioElement) {
    audioElement.pause()
  }
})
</script>

<template>
  <div class="audio-recorder bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
    <!-- Error Message -->
    <div
      v-if="errorMessage"
      class="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg text-sm flex items-center gap-2"
    >
      <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <span>{{ errorMessage }}</span>
    </div>

    <!-- Waveform Visualization -->
    <div class="relative mb-4">
      <canvas
        ref="canvasRef"
        width="400"
        height="80"
        class="w-full h-20 rounded-lg bg-gray-800"
        :class="{ 'opacity-50': !isRecording }"
      ></canvas>

      <!-- Recording indicator -->
      <div
        v-if="isRecording"
        class="absolute top-2 left-2 flex items-center gap-2"
      >
        <span
          class="w-3 h-3 rounded-full"
          :class="isPaused ? 'bg-yellow-500' : 'bg-red-500 animate-pulse'"
        ></span>
        <span class="text-white text-sm font-medium">
          {{ isPaused ? $t('common.audio.paused') : $t('common.audio.recording') }}
        </span>
      </div>
    </div>

    <!-- Time Display -->
    <div class="flex items-center justify-center gap-2 mb-4">
      <span class="text-2xl font-mono font-bold text-gray-900 dark:text-white">
        {{ formattedTime }}
      </span>
      <span v-if="maxDuration" class="text-gray-500 dark:text-gray-400">
        / {{ maxFormattedTime }}
      </span>
    </div>

    <!-- Progress Bar -->
    <div v-if="maxDuration && isRecording" class="mb-4">
      <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          class="h-full transition-all duration-300"
          :class="progressPercent > 90 ? 'bg-red-500' : 'bg-indigo-600'"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
    </div>

    <!-- Controls -->
    <div class="flex items-center justify-center gap-4">
      <!-- Record/Stop Button -->
      <button
        v-if="!isRecording && !audioUrl"
        @click="startRecording"
        class="w-16 h-16 rounded-full bg-red-600 hover:bg-red-700 text-white flex items-center justify-center transition-colors shadow-lg hover:shadow-xl"
        :title="$t('common.audio.startRecording')"
      >
        <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="8" />
        </svg>
      </button>

      <!-- Pause Button -->
      <button
        v-if="isRecording"
        @click="togglePause"
        class="w-12 h-12 rounded-full bg-yellow-500 hover:bg-yellow-600 text-white flex items-center justify-center transition-colors"
        :title="isPaused ? $t('common.audio.resume') : $t('common.audio.pause')"
      >
        <svg v-if="isPaused" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M8 5v14l11-7z" />
        </svg>
        <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
        </svg>
      </button>

      <!-- Stop Button -->
      <button
        v-if="isRecording"
        @click="stopRecording"
        class="w-16 h-16 rounded-full bg-gray-700 hover:bg-gray-800 text-white flex items-center justify-center transition-colors shadow-lg"
        :title="$t('common.audio.stopRecording')"
      >
        <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      </button>

      <!-- Playback Controls (after recording) -->
      <template v-if="audioUrl && showPlayback">
        <button
          @click="isPlaying ? stopPlayback() : playRecording()"
          class="w-12 h-12 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center transition-colors"
          :title="isPlaying ? $t('common.audio.stop') : $t('common.audio.play')"
        >
          <svg v-if="isPlaying" class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <rect x="6" y="4" width="4" height="16" rx="1" />
            <rect x="14" y="4" width="4" height="16" rx="1" />
          </svg>
          <svg v-else class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </button>

        <!-- Download Button -->
        <button
          v-if="showDownload"
          @click="downloadRecording"
          class="w-12 h-12 rounded-full bg-green-600 hover:bg-green-700 text-white flex items-center justify-center transition-colors"
          :title="$t('common.audio.download')"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </button>

        <!-- Reset Button -->
        <button
          @click="reset"
          class="w-12 h-12 rounded-full bg-gray-500 hover:bg-gray-600 text-white flex items-center justify-center transition-colors"
          :title="$t('common.audio.newRecording')"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </template>
    </div>

    <!-- Instructions -->
    <p class="text-center text-sm text-gray-500 dark:text-gray-400 mt-4">
      <template v-if="!isRecording && !audioUrl">
        {{ $t('common.audio.clickToStart') }}
      </template>
      <template v-else-if="isRecording">
        {{ isPaused ? $t('common.audio.recordingPaused') : $t('common.audio.recordingInProgress') }}
      </template>
      <template v-else>
        {{ $t('common.audio.recordingComplete', { duration: formattedTime }) }}
      </template>
    </p>
  </div>
</template>

<style scoped>
.audio-recorder {
  min-width: 300px;
}
</style>
