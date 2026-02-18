<!--
  CourseFileUpload - File upload with AI field filling

  Handles document upload, validation, and AI-powered
  metadata extraction for course creation.
-->

<template>
  <div class="p-4 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
    <div class="flex items-center justify-between mb-2">
      <label class="text-sm font-medium text-[var(--color-text-primary)]">
        Dokument hochladen
      </label>
      <span class="text-xs text-[var(--color-text-secondary)]">optional</span>
    </div>

    <!-- No File Selected -->
    <div v-if="!selectedFile" class="flex items-center gap-3">
      <button
        type="button"
        @click="fileInput?.click()"
        :disabled="disabled"
        class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] hover:border-[var(--color-primary)] transition-colors disabled:opacity-50 flex items-center gap-2"
      >
        <span>{{ fileIcon }}</span>
        <span>Datei auswählen</span>
      </button>
      <span class="text-xs text-[var(--color-text-secondary)]">
        PDF, Word, PowerPoint, Text (max. 50 MB)
      </span>
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.doc,.docx,.ppt,.pptx,.txt"
        @change="handleFileSelect"
        class="hidden"
      />
    </div>

    <!-- File Selected -->
    <div v-else>
      <div class="flex items-center gap-3 p-3 bg-[var(--color-bg)] border border-[var(--color-success,#22c55e)]/30 rounded-lg">
        <span class="text-2xl">{{ getFileIcon(selectedFile.name) }}</span>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-[var(--color-text-primary)] truncate">{{ selectedFile.name }}</p>
          <p class="text-xs text-[var(--color-text-secondary)]">{{ formatFileSize(selectedFile.size) }}</p>
        </div>
        <button
          type="button"
          @click="clearFile"
          :disabled="disabled"
          class="p-1.5 text-[var(--color-text-secondary)] hover:text-[var(--color-error,#dc2626)] rounded transition-colors"
          :title="$t('panel.actions.removeFile')"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- AI Fill Button -->
      <button
        v-if="aiStatus === 'idle'"
        type="button"
        @click="$emit('fill-with-ai')"
        :disabled="disabled"
        class="mt-3 w-full px-4 py-2 text-sm bg-gradient-to-r from-[var(--color-magic-start,#8B5CF6)] to-[var(--color-magic-end,#EC4899)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
      >
        <span>{{ sparkleIcon }}</span>
        <span>Mit KI ausfüllen</span>
      </button>

      <!-- AI Processing -->
      <div v-else-if="aiStatus === 'processing'" class="mt-3 flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
        <span class="animate-pulse">{{ sparkleIcon }}</span>
        <span>KI analysiert Dokument...</span>
      </div>

      <!-- AI Completed -->
      <div v-else-if="aiStatus === 'completed'" class="mt-3 flex items-center gap-2 text-sm text-[var(--color-success,#22c55e)]">
        <span>{{ checkIcon }}</span>
        <span>Felder wurden ausgefüllt</span>
      </div>
    </div>

    <p v-if="error" class="mt-2 text-sm text-[var(--color-error,#dc2626)]">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  selectedFile: File | null
  aiStatus: 'idle' | 'processing' | 'completed' | 'failed'
  error: string | null
  disabled?: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'select-file', file: File): void
  (e: 'clear-file'): void
  (e: 'fill-with-ai'): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)

const fileIcon = '\uD83D\uDCC4'
const sparkleIcon = '\u2728'
const checkIcon = '\u2705'

const MAX_FILE_SIZE = 50 * 1024 * 1024
const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt']

function handleFileSelect(event: Event): void {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    emit('select-file', target.files[0])
  }
}

function clearFile(): void {
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('clear-file')
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function getFileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  const icons: Record<string, string> = {
    pdf: '\uD83D\uDCD5',
    doc: '\uD83D\uDCD8',
    docx: '\uD83D\uDCD8',
    ppt: '\uD83D\uDCD9',
    pptx: '\uD83D\uDCD9',
    txt: '\uD83D\uDCC4'
  }
  return icons[ext] || '\uD83D\uDCC4'
}

// Expose validation constants for parent to use
defineExpose({ MAX_FILE_SIZE, ALLOWED_EXTENSIONS })
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
