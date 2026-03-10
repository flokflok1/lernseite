/**
 * Composable for managing live-log entries and elapsed timer
 * during curriculum import.
 *
 * Collects timestamped log messages from SSE progress events
 * and provides auto-scrolling for the log container.
 */

import { ref, computed, nextTick, onUnmounted } from 'vue'

export interface LogEntry {
  time: string
  message: string
  isError: boolean
  isSuccess: boolean
}

export function useImportLog() {
  const logEntries = ref<LogEntry[]>([])
  const logContainerRef = ref<HTMLElement | null>(null)

  function addLogEntry(message: string, isError = false, isSuccess = false) {
    const now = new Date()
    const time = [
      String(now.getHours()).padStart(2, '0'),
      String(now.getMinutes()).padStart(2, '0'),
      String(now.getSeconds()).padStart(2, '0'),
    ].join(':')

    logEntries.value.push({ time, message, isError, isSuccess })

    nextTick(() => {
      if (logContainerRef.value) {
        logContainerRef.value.scrollTop = logContainerRef.value.scrollHeight
      }
    })
  }

  function clearLog() {
    logEntries.value = []
  }

  // --- Elapsed timer ---
  const startTime = ref(0)
  const elapsed = ref(0)
  let timerInterval: ReturnType<typeof setInterval> | null = null

  const elapsedFormatted = computed(() => {
    const secs = elapsed.value
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return m > 0 ? `${m}:${String(s).padStart(2, '0')}` : `${s}s`
  })

  function startTimer() {
    startTime.value = Date.now()
    elapsed.value = 0
    timerInterval = setInterval(() => {
      elapsed.value = Math.floor((Date.now() - startTime.value) / 1000)
    }, 1000)
  }

  function stopTimer() {
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }

  onUnmounted(stopTimer)

  return {
    logEntries,
    logContainerRef,
    addLogEntry,
    clearLog,
    elapsed,
    elapsedFormatted,
    startTimer,
    stopTimer,
  }
}
