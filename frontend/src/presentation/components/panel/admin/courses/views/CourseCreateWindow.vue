<!--
  Admin Course Create Window - Einfach

  Flow:
  1. Ohne Datei: Manuell alle Felder ausfuellen
  2. Mit Datei: KI fuellt die Felder aus (Titel, Beschreibung, Kategorie, Level, Sprache)
  3. Keine Module-Generierung hier - das passiert auf der Detail-Seite

  File upload/AI logic extracted to composables/useCourseFileUpload.ts

  Phase: C2.1 - Kurs-Erstellen
-->

<template>
  <div class="admin-course-create-window h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
      <div>
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">Neuen Kurs erstellen</h3>
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ selectedFile ? 'KI kann die Felder ausfuellen' : 'Felder manuell ausfuellen' }}
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
              <span>Datei auswaehlen</span>
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

          <!-- File ausgewaehlt -->
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
                title="Datei entfernen"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <!-- KI Felder ausfuellen Button -->
            <button
              v-if="aiStatus === 'idle'"
              type="button"
              @click="fillFieldsWithAI"
              :disabled="isProcessing"
              class="mt-3 w-full px-4 py-2 text-sm bg-gradient-to-r from-[var(--color-magic-start,#8B5CF6)] to-[var(--color-magic-end,#EC4899)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
            >
              <span>✨</span>
              <span>Mit KI ausfuellen</span>
            </button>

            <!-- KI laeuft -->
            <div v-else-if="aiStatus === 'processing'" class="mt-3 flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
              <span class="animate-pulse">✨</span>
              <span>KI analysiert Dokument...</span>
            </div>

            <!-- KI fertig -->
            <div v-else-if="aiStatus === 'completed'" class="mt-3 flex items-center gap-2 text-sm text-[var(--color-success,#22c55e)]">
              <span>✅</span>
              <span>Felder wurden ausgefuellt</span>
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
            placeholder="z.B. Einfuehrung in Python"
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
            placeholder="Kursbeschreibung..."
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
              <option value="beginner">Anfaenger</option>
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
            <option value="fr">Franzoesisch</option>
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
              <span>{{ form.ai_model_override || 'Modell auswaehlen' }}</span>
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
import { useRouter } from 'vue-router'
import { usePanelStore } from '@/application/stores/modules/admin/panel.store'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import { useCourseFileUpload } from './composables/useCourseFileUpload'

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const router = useRouter()
const panelStore = usePanelStore()
const authStore = useAuthStore()
const windowStore = useWindowStore()

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

const modelSelectorCallbackId = ref<string | null>(null)
const categories = ref<Array<{ category_id: string; name: string }>>([])
const isCreating = ref(false)

// File upload composable
const {
  selectedFile,
  fileInput,
  fileError,
  aiStatus,
  handleFileSelect,
  clearFile,
  formatFileSize,
  getFileIcon,
  fillFieldsWithAI
} = useCourseFileUpload(form)

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

    if (form.value.ai_model_override) {
      courseData.ai_model_override = form.value.ai_model_override
    }

    const createdCourse = await panelStore.createCourse(courseData)
    const courseId = createdCourse.course_id

    // If file was selected, upload it as course file
    if (selectedFile.value && courseId) {
      try {
        const { adminUploadCourseFile } = await import('@/application/services/api/panel-admin')
        await adminUploadCourseFile(courseId, selectedFile.value, {
          file_category: 'script',
          display_name: selectedFile.value.name
        })
      } catch (uploadErr) {
        console.warn('File upload after course creation failed:', uploadErr)
      }
    }

    emit('close')

    if (courseId) {
      router.push(`/panel/courses/${courseId}`)
    }
  } catch (error: any) {
    console.error('Failed to create course:', error)
    alert('Fehler beim Erstellen des Kurses: ' + (error.message || 'Unbekannter Fehler'))
  } finally {
    isCreating.value = false
  }
}

const loadCategories = async (): Promise<void> => {
  try {
    await panelStore.loadCategoryTree()
    const tree = panelStore.categoryTree

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

// Phase C3.3: Model Selector Window
const openModelSelector = (): void => {
  modelSelectorCallbackId.value = `model-select-${Date.now()}`

  windowStore.openWindow({
    type: 'admin-model-selector',
    title: 'KI-Modell auswaehlen',
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
  window.addEventListener('model-selected', handleModelSelected as EventListener)
})

onUnmounted(() => {
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
