/**
 * useCourseCreate Composable
 * ==========================
 * Shared business logic for the course creation flow (panel, window, and base variants).
 *
 * Handles:
 * - Form state management
 * - File upload with validation
 * - AI-powered field extraction (document analysis polling)
 * - Course creation with optional file attachment
 * - Category tree loading
 * - Model selector callback coordination
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { usePanelStore } from '@/application/stores/modules/admin/panel.store'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'

export interface CourseCreateForm {
  title: string
  description: string
  category_id: string
  level: string
  language: string
  ai_model_override: string
}

export type AiStatus = 'idle' | 'processing' | 'completed' | 'failed'

export interface CategoryOption {
  category_id: string
  name: string
}

const MAX_FILE_SIZE = 50 * 1024 * 1024
const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt']

const FILE_ICONS: Record<string, string> = {
  pdf: '\uD83D\uDCD5',
  doc: '\uD83D\uDCD8',
  docx: '\uD83D\uDCD8',
  ppt: '\uD83D\uDCD9',
  pptx: '\uD83D\uDCD9',
  txt: '\uD83D\uDCC4'
}

export function useCourseCreate(emitClose: () => void) {
  const { t } = useI18n()
  const router = useRouter()
  const panelStore = usePanelStore()
  const authStore = useAuthStore()

  // ==========================================================================
  // State
  // ==========================================================================

  const form = ref<CourseCreateForm>({
    title: '',
    description: '',
    category_id: '',
    level: 'beginner',
    language: 'de',
    ai_model_override: ''
  })

  const modelSelectorCallbackId = ref<string | null>(null)
  const categories = ref<CategoryOption[]>([])
  const selectedFile = ref<File | null>(null)
  const fileInput = ref<HTMLInputElement | null>(null)
  const fileError = ref<string | null>(null)
  const isCreating = ref(false)
  const aiStatus = ref<AiStatus>('idle')

  // ==========================================================================
  // Computed
  // ==========================================================================

  const isProcessing = computed((): boolean =>
    isCreating.value || aiStatus.value === 'processing'
  )

  const canCreate = computed((): boolean =>
    form.value.title.length >= 3 &&
    !isProcessing.value &&
    !!authStore.user?.user_id
  )

  // ==========================================================================
  // File handling
  // ==========================================================================

  function handleFileSelect(event: Event): void {
    const target = event.target as HTMLInputElement
    if (target.files && target.files.length > 0) {
      validateAndSetFile(target.files[0])
    }
  }

  function validateAndSetFile(file: File): void {
    fileError.value = null
    aiStatus.value = 'idle'

    const ext = file.name.split('.').pop()?.toLowerCase() || ''
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      fileError.value = t('courseCreate.file.onlyAllowed')
      return
    }

    if (file.size > MAX_FILE_SIZE) {
      fileError.value = t('courseCreate.file.tooLarge')
      return
    }

    selectedFile.value = file
  }

  function clearFile(): void {
    selectedFile.value = null
    fileError.value = null
    aiStatus.value = 'idle'
    if (fileInput.value) {
      fileInput.value.value = ''
    }
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
    return FILE_ICONS[ext] || '\uD83D\uDCC4'
  }

  // ==========================================================================
  // AI-powered field extraction
  // ==========================================================================

  async function fillFieldsWithAI(): Promise<void> {
    if (!selectedFile.value) return

    aiStatus.value = 'processing'

    try {
      const job = await panelStore.startAIJob(
        selectedFile.value,
        'Analysiere dieses Dokument und extrahiere: 1) Einen passenden Kurstitel, 2) Eine kurze Beschreibung, 3) Das Schwierigkeitslevel (beginner/intermediate/advanced), 4) Die Sprache (de/en/fr/es). Antworte im JSON-Format.'
      )

      let pollCount = 0
      const maxPolls = 60

      const pollResult = async (): Promise<void> => {
        pollCount++

        if (pollCount > maxPolls) {
          aiStatus.value = 'failed'
          fileError.value = t('courseCreate.errors.timeout')
          return
        }

        try {
          const { adminGetAIJob } = await import('@/infrastructure/api/clients/panel/admin')
          const result = await adminGetAIJob(job.id)

          if (result.status === 'completed' && result.output_data) {
            const courseData = result.output_data.course || result.output_data

            if (courseData.title) form.value.title = courseData.title
            if (courseData.description) form.value.description = courseData.description
            if (courseData.level) form.value.level = courseData.level
            if (courseData.language) form.value.language = courseData.language

            aiStatus.value = 'completed'
          } else if (result.status === 'failed') {
            aiStatus.value = 'failed'
            fileError.value = result.error_message || t('courseCreate.errors.aiFailed')
          } else if (result.status === 'queued' || result.status === 'processing') {
            setTimeout(pollResult, 3000)
          }
        } catch (pollError: any) {
          if (pollError.status === 429) {
            console.warn('[AI] Rate limited, waiting 5 seconds...')
            setTimeout(pollResult, 5000)
          } else {
            console.error('[AI] Poll error:', pollError)
            setTimeout(pollResult, 4000)
          }
        }
      }

      setTimeout(pollResult, 3000)
    } catch (error: any) {
      aiStatus.value = 'failed'
      fileError.value = error.message || t('courseCreate.errors.aiError')
    }
  }

  // ==========================================================================
  // Course creation
  // ==========================================================================

  async function createCourse(): Promise<void> {
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

      if (selectedFile.value && courseId) {
        try {
          const { adminUploadCourseFile } = await import('@/infrastructure/api/clients/panel/admin')
          await adminUploadCourseFile(courseId, selectedFile.value, {
            file_category: 'script',
            display_name: selectedFile.value.name
          })
        } catch (uploadErr) {
          console.warn('File upload after course creation failed:', uploadErr)
        }
      }

      emitClose()

      if (courseId) {
        router.push(`/panel/courses/${courseId}`)
      }
    } catch (error: any) {
      console.error('Failed to create course:', error)
      fileError.value = error.message || t('courseCreate.errors.createError')
    } finally {
      isCreating.value = false
    }
  }

  // ==========================================================================
  // Categories
  // ==========================================================================

  async function loadCategories(): Promise<void> {
    try {
      await panelStore.loadCategoryTree()
      const tree = panelStore.categoryTree

      if (!tree || !Array.isArray(tree) || tree.length === 0) {
        categories.value = []
        return
      }

      function flatten(nodes: any[]): CategoryOption[] {
        const result: CategoryOption[] = []
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

  // ==========================================================================
  // Model selector cross-component communication
  // ==========================================================================

  function handleModelSelected(event: CustomEvent): void {
    if (event.detail?.callbackId === modelSelectorCallbackId.value) {
      const model = event.detail.model
      if (model?.model_name) {
        form.value.ai_model_override = model.model_name
      }
    }
  }

  function clearModelOverride(): void {
    form.value.ai_model_override = ''
  }

  function generateCallbackId(): string {
    const id = `model-select-${Date.now()}`
    modelSelectorCallbackId.value = id
    return id
  }

  // ==========================================================================
  // Lifecycle
  // ==========================================================================

  onMounted(() => {
    loadCategories()
    window.addEventListener('model-selected', handleModelSelected as EventListener)
  })

  onUnmounted(() => {
    window.removeEventListener('model-selected', handleModelSelected as EventListener)
  })

  return {
    form,
    categories,
    selectedFile,
    fileInput,
    fileError,
    isCreating,
    aiStatus,
    isProcessing,
    canCreate,
    handleFileSelect,
    clearFile,
    formatFileSize,
    getFileIcon,
    fillFieldsWithAI,
    createCourse,
    clearModelOverride,
    generateCallbackId
  }
}
