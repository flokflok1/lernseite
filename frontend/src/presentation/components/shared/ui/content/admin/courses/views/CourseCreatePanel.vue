<!--
  Admin Course Create Panel - Einfach

  Flow:
  1. Ohne Datei: Manuell alle Felder ausfüllen
  2. Mit Datei: KI füllt die Felder aus (Titel, Beschreibung, Kategorie, Level, Sprache)
  3. Keine Module-Generierung hier - das passiert auf der Detail-Seite

  Phase: C2.1 - Kurs-Erstellen
-->

<template>
  <div class="admin-course-create-panel h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
      <div>
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">Neuen Kurs erstellen</h3>
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ selectedFile ? 'KI kann die Felder ausfüllen' : 'Felder manuell ausfüllen' }}
        </p>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 p-6 overflow-y-auto">
      <div class="space-y-5 max-w-2xl">

        <!-- Datei Upload - Kompakt oben -->
        <div class="p-4 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-[var(--color-text-primary)]">
              Dokument hochladen
            </label>
            <span class="text-xs text-[var(--color-text-secondary)]">optional</span>
          </div>

          <!-- Kein File -->
          <div v-if="!selectedFile" class="flex items-center gap-3">
            <button
              type="button"
              @click="fileInput?.click()"
              :disabled="isProcessing"
              class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] hover:border-[var(--color-primary)] transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              <span>📄</span>
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

          <!-- File ausgewählt -->
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
                :disabled="isProcessing"
                class="p-1.5 text-[var(--color-text-secondary)] hover:text-[var(--color-error,#dc2626)] rounded transition-colors"
                :title="$t('admin.actions.removeFile')"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- KI Felder ausfüllen Button -->
            <button
              v-if="aiStatus === 'idle'"
              type="button"
              @click="fillFieldsWithAI"
              :disabled="isProcessing"
              class="mt-3 w-full px-4 py-2 text-sm bg-gradient-to-r from-[var(--color-magic-start,#8B5CF6)] to-[var(--color-magic-end,#EC4899)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              <span>✨</span>
              <span>Mit KI ausfüllen</span>
            </button>

            <!-- KI läuft -->
            <div v-else-if="aiStatus === 'processing'" class="mt-3 flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
              <span class="animate-pulse">✨</span>
              <span>KI analysiert Dokument...</span>
            </div>

            <!-- KI fertig -->
            <div v-else-if="aiStatus === 'completed'" class="mt-3 flex items-center gap-2 text-sm text-[var(--color-success,#22c55e)]">
              <span>✅</span>
              <span>Felder wurden ausgefüllt</span>
            </div>
          </div>

          <p v-if="fileError" class="mt-2 text-sm text-[var(--color-error,#dc2626)]">{{ fileError }}</p>
        </div>

        <!-- Kurstitel -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
            Kurstitel *
          </label>
          <input
            v-model="form.title"
            type="text"
            required
            :disabled="isProcessing"
            class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
            placeholder="z.B. Einführung in Python"
          />
        </div>

        <!-- Beschreibung -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
            Beschreibung
          </label>
          <textarea
            v-model="form.description"
            rows="3"
            :disabled="isProcessing"
            class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50 resize-none"
            :placeholder="$t('admin.courses.placeholders.descriptionInput')"
          ></textarea>
        </div>

        <!-- Kategorie & Level -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
              Kategorie
            </label>
            <select
              v-model="form.category_id"
              :disabled="isProcessing"
              class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
            >
              <option value="">Keine Kategorie</option>
              <option v-for="cat in categories" :key="cat.category_id" :value="cat.category_id">
                {{ cat.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
              Schwierigkeitsgrad
            </label>
            <select
              v-model="form.level"
              :disabled="isProcessing"
              class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
            >
              <option value="beginner">Anfänger</option>
              <option value="intermediate">Fortgeschritten</option>
              <option value="advanced">Experte</option>
            </select>
          </div>
        </div>

        <!-- Sprache -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
            Sprache
          </label>
          <select
            v-model="form.language"
            :disabled="isProcessing"
            class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent disabled:opacity-50"
          >
            <option value="de">Deutsch</option>
            <option value="en">Englisch</option>
            <option value="fr">Französisch</option>
            <option value="es">Spanisch</option>
          </select>
        </div>

        <!-- AI Model Override (Phase C3.3) -->
        <div class="p-4 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-[var(--color-text-primary)]">
              KI-Modell
            </label>
            <span class="text-xs text-[var(--color-text-secondary)]">optional</span>
          </div>
          <div class="flex items-center gap-3">
            <button
              type="button"
              @click="openModelSelector"
              :disabled="isProcessing"
              class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] hover:border-[var(--color-primary)] transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              <span>🤖</span>
              <span>{{ form.ai_model_override || 'Modell auswählen' }}</span>
            </button>
            <button
              v-if="form.ai_model_override"
              type="button"
              @click="form.ai_model_override = ''"
              :disabled="isProcessing"
              class="p-2 text-[var(--color-text-secondary)] hover:text-[var(--color-error,#dc2626)] transition-colors"
              title="Modell-Override entfernen"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p class="mt-2 text-xs text-[var(--color-text-secondary)]">
            {{ form.ai_model_override ? `Kurs verwendet: ${form.ai_model_override}` : 'Verwendet System-Default Modell' }}
          </p>
        </div>

      </div>
    </div>

    <!-- Footer Actions -->
    <div class="px-6 py-3 bg-[var(--color-surface)] border-t border-[var(--color-border)] flex justify-between">
      <button
        type="button"
        @click="$emit('close')"
        :disabled="isProcessing"
        class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg text-[var(--color-text-secondary)] hover:bg-[var(--color-bg)] transition-colors disabled:opacity-50"
      >
        Abbrechen
      </button>

      <button
        type="button"
        @click="createCourse"
        :disabled="!canCreate"
        class="px-5 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
      >
        {{ isCreating ? 'Erstelle...' : 'Kurs erstellen' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/application/stores/modules/admin'
import { useAuthStore } from '@/application/stores/modules/core'
import { usePanelStore } from '@/application/stores/modules/desktop'
import type { LsxPanel } from '@/application/stores/modules/desktop'

const { t } = useI18n()

interface Props {
  panel: LsxPanel
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const router = useRouter()
const adminStore = useAdminStore()
const authStore = useAuthStore()
const panelStore = usePanelStore()

// ============================================================================
// State
// ============================================================================

const form = ref({
  title: '',
  description: '',
  category_id: '',
  level: 'beginner',
  language: 'de',
  ai_model_override: ''
})

// Model selector callback ID for cross-panel communication
const modelSelectorCallbackId = ref<string | null>(null)

const categories = ref<Array<{ category_id: string; name: string }>>([])

const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const fileError = ref<string | null>(null)

const isCreating = ref(false)
const aiStatus = ref<'idle' | 'processing' | 'completed' | 'failed'>('idle')

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt']

// ============================================================================
// Computed
// ============================================================================

const isProcessing = computed(() => isCreating.value || aiStatus.value === 'processing')

const canCreate = computed(() =>
  form.value.title.length >= 3 &&
  !isProcessing.value &&
  authStore.user?.user_id
)

// ============================================================================
// Methods
// ============================================================================

const handleFileSelect = (event: Event): void => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    validateAndSetFile(target.files[0])
  }
}

const validateAndSetFile = (file: File): void => {
  fileError.value = null
  aiStatus.value = 'idle'

  const ext = file.name.split('.').pop()?.toLowerCase() || ''
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    fileError.value = 'Nur PDF, Word, PowerPoint und Text-Dateien sind erlaubt'
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
  aiStatus.value = 'idle'
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

const getFileIcon = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  const icons: Record<string, string> = {
    pdf: '📕',
    doc: '📘',
    docx: '📘',
    ppt: '📙',
    pptx: '📙',
    txt: '📄'
  }
  return icons[ext] || '📄'
}

const fillFieldsWithAI = async (): Promise<void> => {
  if (!selectedFile.value) return

  aiStatus.value = 'processing'

  try {
    // Start AI job to analyze document and extract course metadata
    const job = await adminStore.startAIJob(
      selectedFile.value,
      'Analysiere dieses Dokument und extrahiere: 1) Einen passenden Kurstitel, 2) Eine kurze Beschreibung, 3) Das Schwierigkeitslevel (beginner/intermediate/advanced), 4) Die Sprache (de/en/fr/es). Antworte im JSON-Format.'
    )

    // Poll for result - use longer interval to avoid rate limiting
    let pollCount = 0
    const maxPolls = 60 // Max 2 minutes (60 * 3 seconds)

    const pollResult = async (): Promise<void> => {
      pollCount++

      if (pollCount > maxPolls) {
        aiStatus.value = 'failed'
        fileError.value = 'Timeout: KI-Analyse dauert zu lange'
        return
      }

      try {
        // Use direct API call to avoid store's automatic polling
        const { adminGetAIJob } = await import('@/application/services/api/admin')
        const result = await adminGetAIJob(job.id)

        if (result.status === 'completed' && result.output_data) {
          // Fill form with AI results - data is nested under 'course' key
          const courseData = result.output_data.course || result.output_data
          console.log('[AI] Received output_data:', result.output_data)
          console.log('[AI] Course data to fill:', courseData)

          if (courseData.title) form.value.title = courseData.title
          if (courseData.description) form.value.description = courseData.description
          if (courseData.level) form.value.level = courseData.level
          if (courseData.language) form.value.language = courseData.language

          aiStatus.value = 'completed'
        } else if (result.status === 'failed') {
          aiStatus.value = 'failed'
          fileError.value = result.error_message || 'KI-Analyse fehlgeschlagen'
        } else if (result.status === 'queued' || result.status === 'processing') {
          // Still processing, poll again with 3 second interval
          setTimeout(pollResult, 3000)
        }
      } catch (pollError: any) {
        // On rate limit (429), wait longer and retry
        if (pollError.status === 429) {
          console.warn('[AI] Rate limited, waiting 5 seconds...')
          setTimeout(pollResult, 5000)
        } else {
          console.error('[AI] Poll error:', pollError)
          // On other errors, still try again but with longer delay
          setTimeout(pollResult, 4000)
        }
      }
    }

    // Start polling after 3 seconds
    setTimeout(pollResult, 3000)
  } catch (error: any) {
    aiStatus.value = 'failed'
    fileError.value = error.message || 'Fehler bei der KI-Analyse'
  }
}

const createCourse = async (): Promise<void> => {
  if (!canCreate.value) return

  isCreating.value = true

  try {
    const courseData: Record<string, any> = {
      title: form.value.title,
      description: form.value.description || '',
      category_id: form.value.category_id || null,
      creator_id: authStore.user?.user_id || '',
      level: form.value.level,
      language: form.value.language,
      price: 0,
      is_public: false
    }

    // Add AI model override if selected (Phase C3.3)
    if (form.value.ai_model_override) {
      courseData.ai_model_override = form.value.ai_model_override
    }

    const createdCourse = await adminStore.createCourse(courseData)
    const courseId = createdCourse.course_id

    // If file was selected, upload it as course file
    if (selectedFile.value && courseId) {
      try {
        const { adminUploadCourseFile } = await import('@/application/services/api/admin')
        await adminUploadCourseFile(courseId, selectedFile.value, {
          file_category: 'script',
          display_name: selectedFile.value.name
        })
      } catch (uploadErr) {
        console.warn('File upload after course creation failed:', uploadErr)
      }
    }

    emit('close')

    // Navigate to course detail page
    if (courseId) {
      router.push(`/admin/courses/${courseId}`)
    }
  } catch (error: any) {
    console.error('Failed to create course:', error)
    fileError.value = error.message || 'Error creating course'
  } finally {
    isCreating.value = false
  }
}

const loadCategories = async (): Promise<void> => {
  try {
    await adminStore.loadCategoryTree()
    const tree = adminStore.categoryTree

    // Check if tree is valid and iterable
    if (!tree || !Array.isArray(tree) || tree.length === 0) {
      categories.value = []
      return
    }

    const flatten = (nodes: any[]): Array<{ category_id: string; name: string }> => {
      const result: Array<{ category_id: string; name: string }> = []
      for (const node of nodes) {
        if (node && node.category_id) {
          result.push({ category_id: node.category_id, name: node.name || 'Unbenannt' })
          if (node.children && Array.isArray(node.children) && node.children.length > 0) {
            result.push(...flatten(node.children))
          }
        }
      }
      return result
    }
    categories.value = flatten(tree)
  } catch (error) {
    console.warn('Failed to load categories:', error)
    categories.value = []
  }
}

// Phase C3.3: Model Selector Panel
const openModelSelector = (): void => {
  // Generate unique callback ID
  modelSelectorCallbackId.value = `model-select-${Date.now()}`

  panelStore.openPanel({
    type: 'admin-model-selector',
    title: 'KI-Modell auswählen',
    icon: '🤖',
    payload: {
      scope: 'course',
      callbackId: modelSelectorCallbackId.value,
      onSelectModel: (modelName: string) => {
        form.value.ai_model_override = modelName
      }
    },
    size: { width: 600, height: 700 }
  })
}

// Handle model selection from cross-panel event
const handleModelSelected = (event: CustomEvent): void => {
  if (event.detail?.callbackId === modelSelectorCallbackId.value) {
    const model = event.detail.model
    if (model?.model_name) {
      form.value.ai_model_override = model.model_name
    }
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadCategories()
  // Listen for model selection events from Model Selector Panel
  window.addEventListener('model-selected', handleModelSelected as EventListener)
})

onUnmounted(() => {
  // Clean up event listener
  window.removeEventListener('model-selected', handleModelSelected as EventListener)
})
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>
