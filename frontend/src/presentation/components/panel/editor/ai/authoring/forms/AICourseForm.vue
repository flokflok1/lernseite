<template>
  <div class="space-y-4">
    <!-- Initial State: PDF Upload -->
    <div v-if="jobState.status === 'idle'">
      <div class="mb-4">
        <h4 class="text-md font-semibold text-[var(--color-text-primary)] mb-2">
          PDF hochladen
        </h4>
        <p class="text-sm text-[var(--color-text-secondary)]">
          Laden Sie ein PDF-Dokument hoch, und die KI erstellt automatisch einen strukturierten Kurs mit Modulen und Lektionen.
        </p>
      </div>

      <!-- PDF Upload Zone -->
      <div
        class="border-2 border-dashed rounded-lg p-6 text-center transition-colors"
        :class="dragActive ? 'border-[var(--color-primary)] bg-[var(--color-background)]' : 'border-[var(--color-border)]'"
        @dragover.prevent="dragActive = true"
        @dragleave.prevent="dragActive = false"
        @drop.prevent="handleFileDrop"
      >
        <input
          ref="fileInput"
          type="file"
          accept=".pdf"
          @change="handleFileSelect"
          class="hidden"
        />

        <div v-if="!selectedFile">
          <svg class="mx-auto h-12 w-12 text-[var(--color-text-secondary)]" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <p class="mt-2 text-sm text-[var(--color-text-primary)]">
            PDF hierher ziehen oder
            <button
              type="button"
              @click="fileInput?.click()"
              class="text-[var(--color-primary)] hover:underline"
            >
              durchsuchen
            </button>
          </p>
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">
            Max. 50 MB
          </p>
        </div>

        <div v-else class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <svg class="h-8 w-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
            </svg>
            <div class="text-left">
              <p class="text-sm font-medium text-[var(--color-text-primary)]">
                {{ selectedFile.name }}
              </p>
              <p class="text-xs text-[var(--color-text-secondary)]">
                {{ formatFileSize(selectedFile.size) }}
              </p>
            </div>
          </div>
          <button
            type="button"
            @click="clearFile"
            class="text-red-500 hover:text-red-700"
          >
            <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      <p v-if="fileError" class="mt-2 text-sm text-red-500">
        {{ fileError }}
      </p>

      <!-- Optional Prompt -->
      <div class="mt-4">
        <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
          Anweisungen für die KI (optional)
        </label>
        <textarea
          v-model="prompt"
          rows="3"
          class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent resize-none"
          placeholder="z.B.: Erstelle einen Anfängerkurs mit praktischen Beispielen..."
        ></textarea>
        <p class="mt-1 text-xs text-[var(--color-text-secondary)]">
          Geben Sie spezifische Anweisungen, um die KI-Generierung anzupassen
        </p>
      </div>

      <!-- Start Button -->
      <button
        type="button"
        @click="startJob"
        :disabled="!selectedFile || isSubmitting"
        class="w-full mt-4 px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity flex items-center justify-center gap-2"
      >
        <svg v-if="isSubmitting" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isSubmitting ? 'Wird hochgeladen...' : 'KI-Analyse starten' }}
      </button>
    </div>

    <!-- Processing State: Progress -->
    <div v-else-if="jobState.status === 'pending' || jobState.status === 'processing'">
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-md font-semibold text-[var(--color-text-primary)]">KI analysiert das PDF...</h4>
          <span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
            {{ jobState.status === 'pending' ? 'Wartend' : 'In Bearbeitung' }}
          </span>
        </div>
        <p class="text-sm text-[var(--color-text-secondary)]">
          Die KI erstellt automatisch Titel, Beschreibung, Module und Lektionen aus dem PDF-Inhalt.
        </p>
      </div>

      <!-- Progress Bar -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-[var(--color-text-primary)]">Fortschritt</span>
          <span class="text-sm font-medium text-[var(--color-text-primary)]">{{ jobState.progress }}%</span>
        </div>
        <div class="w-full h-2 bg-[var(--color-surface)] rounded-full overflow-hidden border border-[var(--color-border)]">
          <div
            class="h-full bg-[var(--color-primary)] transition-all duration-300 ease-out"
            :style="{ width: `${jobState.progress}%` }"
          ></div>
        </div>
      </div>

      <!-- Cancel Button -->
      <button
        type="button"
        @click="$emit('cancelJob')"
        class="w-full px-4 py-2 text-red-600 border border-red-600 rounded-lg hover:bg-red-50 transition-colors"
      >
        Job abbrechen
      </button>
    </div>

    <!-- Completed State: Preview -->
    <div v-else-if="jobState.status === 'completed' && jobState.draft">
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-md font-semibold text-[var(--color-text-primary)]">Kurs erfolgreich generiert!</h4>
          <span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
            Abgeschlossen
          </span>
        </div>
        <p class="text-sm text-[var(--color-text-secondary)]">
          Überprüfen Sie die generierte Kursstruktur und erstellen Sie den Kurs mit einem Klick.
        </p>
      </div>

      <!-- Course Info -->
      <div class="p-4 bg-[var(--color-background)] rounded-lg border border-[var(--color-border)] mb-4">
        <h5 class="font-semibold text-[var(--color-text-primary)] mb-2">{{ jobState.draft.course.title }}</h5>
        <p class="text-sm text-[var(--color-text-secondary)] mb-2">{{ jobState.draft.course.description }}</p>
        <div class="flex flex-wrap gap-2 text-xs">
          <span class="px-2 py-1 bg-[var(--color-surface)] rounded border border-[var(--color-border)]">
            {{ getCategoryLabel(jobState.draft.course.category) }}
          </span>
          <span class="px-2 py-1 bg-[var(--color-surface)] rounded border border-[var(--color-border)]">
            Level: {{ getLevelLabel(jobState.draft.course.level) }}
          </span>
          <span class="px-2 py-1 bg-[var(--color-surface)] rounded border border-[var(--color-border)]">
            {{ jobState.draft.course.language.toUpperCase() }}
          </span>
        </div>
      </div>

      <!-- Chapters Preview -->
      <div class="mb-4">
        <h5 class="font-semibold text-[var(--color-text-primary)] mb-2">Kapitel ({{ jobState.draft.chapters?.length || 0 }})</h5>
        <div class="space-y-2 max-h-64 overflow-y-auto">
          <div v-for="(chapter, index) in jobState.draft.chapters" :key="index" class="p-3 bg-[var(--color-background)] rounded border border-[var(--color-border)]">
            <div class="flex items-start justify-between mb-1">
              <span class="text-sm font-medium text-[var(--color-text-primary)]">{{ chapter.title }}</span>
              <span class="text-xs text-[var(--color-text-secondary)]">{{ chapter.duration_minutes }} Min</span>
            </div>
            <p class="text-xs text-[var(--color-text-secondary)] mb-2">{{ chapter.description }}</p>
            <p class="text-xs text-[var(--color-text-secondary)]">{{ chapter.lessons?.length || 0 }} Lektionen</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Failed State -->
    <div v-else-if="jobState.status === 'failed'">
      <div class="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center gap-2 mb-2">
          <span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
            Fehlgeschlagen
          </span>
          <h4 class="text-md font-semibold text-red-800">KI-Analyse fehlgeschlagen</h4>
        </div>
        <p v-if="jobState.error" class="text-sm text-red-600">{{ jobState.error }}</p>
        <button
          type="button"
          @click="resetJob"
          class="mt-4 w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Erneut versuchen
        </button>
      </div>
    </div>

    <!-- Cancelled State -->
    <div v-else-if="jobState.status === 'cancelled'">
      <div class="p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <h4 class="text-md font-semibold text-gray-800 mb-2">Job wurde abgebrochen</h4>
        <button
          type="button"
          @click="resetJob"
          class="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          Neuen Job starten
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { AIJob, AICourseDraft } from '@/infrastructure/api/clients/panel/admin'

interface JobState {
  status: 'idle' | 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  progress: number
  jobId: string | null
  job: AIJob | null
  draft: AICourseDraft | null
  error: string | null
  isEditing: boolean
}

interface Props {
  jobState: JobState
}

interface Emits {
  (e: 'startJob', file: File, prompt?: string): void
  (e: 'cancelJob'): void
  (e: 'finalizeJob'): void
  (e: 'editDraft'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const prompt = ref('')
const dragActive = ref(false)
const fileError = ref<string | null>(null)
const isSubmitting = ref(false)

const MAX_FILE_SIZE = 50 * 1024 * 1024

const handleFileSelect = (event: Event): void => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const handleFileDrop = (event: DragEvent): void => {
  dragActive.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) {
    validateAndSetFile(file)
  }
}

const validateAndSetFile = (file: File): void => {
  fileError.value = null

  if (file.type !== 'application/pdf') {
    fileError.value = 'Nur PDF-Dateien sind erlaubt'
    return
  }

  if (file.size > MAX_FILE_SIZE) {
    fileError.value = 'Datei ist zu groß (max. 50 MB)'
    return
  }

  selectedFile.value = file
}

const clearFile = (): void => {
  selectedFile.value = null
  fileError.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const startJob = async (): Promise<void> => {
  const file = selectedFile.value
  if (!file || isSubmitting.value) return

  isSubmitting.value = true
  try {
    emit('startJob', file, prompt.value || undefined)
  } finally {
    isSubmitting.value = false
  }
}

const resetJob = (): void => {
  clearFile()
  prompt.value = ''
}

const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    programming: 'Programmierung',
    business: 'Business',
    design: 'Design',
    marketing: 'Marketing',
    languages: 'Sprachen',
    science: 'Wissenschaft',
    mathematics: 'Mathematik',
    health: 'Gesundheit',
    'personal-development': 'Persönliche Entwicklung',
    other: 'Sonstiges'
  }
  return labels[category] || category
}

const getLevelLabel = (level: string): string => {
  const labels: Record<string, string> = {
    beginner: 'Anfänger',
    intermediate: 'Fortgeschritten',
    advanced: 'Experte'
  }
  return labels[level] || level
}
</script>
