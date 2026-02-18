/**
 * useAudioRecorder - Composable for microphone recording, playback, and download.
 *
 * Handles MediaRecorder lifecycle, audio context visualization,
 * permission checks, timer management, and cleanup.
 */

import { ref, computed, onUnmounted, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'

interface UseAudioRecorderOptions {
  maxDuration: number
  autoStop: boolean
}

interface UseAudioRecorderEmits {
  onRecorded: (blob: Blob, duration: number) => void
  onStarted: () => void
  onStopped: () => void
  onError: (error: string) => void
}

export function useAudioRecorder(
  options: UseAudioRecorderOptions,
  emits: UseAudioRecorderEmits,
  canvasRef: Ref<HTMLCanvasElement | null>,
) {
  const { t } = useI18n()

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

  // Internal references (not reactive)
  let mediaRecorder: MediaRecorder | null = null
  let audioChunks: Blob[] = []
  let timerInterval: number | null = null
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let animationFrame: number | null = null
  let audioElement: HTMLAudioElement | null = null

  // Computed
  const formattedTime = computed((): string => {
    const minutes = Math.floor(recordingTime.value / 60)
    const seconds = recordingTime.value % 60
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  })

  const maxFormattedTime = computed((): string => {
    if (!options.maxDuration) return ''
    const minutes = Math.floor(options.maxDuration / 60)
    const seconds = options.maxDuration % 60
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  })

  const progressPercent = computed((): number => {
    if (!options.maxDuration) return 0
    return (recordingTime.value / options.maxDuration) * 100
  })

  async function checkPermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach(track => track.stop())
      hasPermission.value = true
      return true
    } catch {
      hasPermission.value = false
      errorMessage.value = t('common.audio.microphoneAccessDenied')
      emits.onError(errorMessage.value)
      return false
    }
  }

  function visualize(): void {
    if (!analyser || !canvasRef.value) return

    const canvas = canvasRef.value
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)

    const currentAnalyser = analyser
    function draw(): void {
      if (!isRecording.value || !currentAnalyser) return
      animationFrame = requestAnimationFrame(draw)

      currentAnalyser.getByteFrequencyData(dataArray)

      const average = dataArray.reduce((a, b) => a + b, 0) / bufferLength
      audioLevel.value = average / 255

      ctx.fillStyle = 'rgb(31, 41, 55)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      const barWidth = (canvas.width / bufferLength) * 2.5
      let x = 0

      for (let i = 0; i < bufferLength; i++) {
        const dataValue = dataArray[i] ?? 0
        const barHeight = (dataValue / 255) * canvas.height

        const hue = 250 + (dataValue / 255) * 30
        ctx.fillStyle = `hsl(${hue}, 80%, 60%)`

        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight)
        x += barWidth + 1
      }
    }

    draw()
  }

  async function startRecording(): Promise<void> {
    errorMessage.value = null

    if (hasPermission.value === null) {
      const permitted = await checkPermission()
      if (!permitted) return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      })

      audioContext = new AudioContext()
      analyser = audioContext.createAnalyser()
      const source = audioContext.createMediaStreamSource(stream)
      source.connect(analyser)
      analyser.fftSize = 256

      visualize()

      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/mp4',
        'audio/mpeg',
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
        mimeType: selectedMimeType,
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
        emits.onRecorded(blob, recordingTime.value)

        stream.getTracks().forEach(track => track.stop())

        if (audioContext) {
          audioContext.close()
          audioContext = null
        }
      }

      mediaRecorder.start(100)
      isRecording.value = true
      isPaused.value = false
      recordingTime.value = 0

      timerInterval = window.setInterval(() => {
        if (!isPaused.value) {
          recordingTime.value++

          if (options.autoStop && options.maxDuration && recordingTime.value >= options.maxDuration) {
            stopRecording()
          }
        }
      }, 1000)

      emits.onStarted()
    } catch (err: any) {
      console.error('Recording error:', err)
      errorMessage.value = err.message || t('common.audio.recordingStartFailed')
      emits.onError(errorMessage.value || t('common.unknownError'))
    }
  }

  function togglePause(): void {
    if (!mediaRecorder) return

    if (isPaused.value) {
      mediaRecorder.resume()
      isPaused.value = false
    } else {
      mediaRecorder.pause()
      isPaused.value = true
    }
  }

  function stopRecording(): void {
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

      emits.onStopped()
    }
  }

  function playRecording(): void {
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

  function stopPlayback(): void {
    if (audioElement) {
      audioElement.pause()
      audioElement.currentTime = 0
      isPlaying.value = false
    }
  }

  function downloadRecording(): void {
    if (!audioUrl.value || !audioBlob.value) return

    const link = document.createElement('a')
    link.href = audioUrl.value
    link.download = `recording-${new Date().toISOString()}.webm`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  function reset(): void {
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value)
    }
    audioUrl.value = null
    audioBlob.value = null
    recordingTime.value = 0
    isPlaying.value = false
    errorMessage.value = null
  }

  function getBlob(): Blob | null {
    return audioBlob.value
  }

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

  return {
    isRecording,
    isPaused,
    isPlaying,
    recordingTime,
    audioUrl,
    audioBlob,
    errorMessage,
    audioLevel,
    formattedTime,
    maxFormattedTime,
    progressPercent,
    startRecording,
    togglePause,
    stopRecording,
    playRecording,
    stopPlayback,
    downloadRecording,
    reset,
    getBlob,
  }
}
