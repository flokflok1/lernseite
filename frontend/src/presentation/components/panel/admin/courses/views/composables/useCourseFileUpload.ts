/**
 * useCourseFileUpload - Composable for file upload and AI analysis
 *
 * Handles file validation, selection, AI-powered field filling,
 * and file utility functions for the course creation window.
 *
 * Extracted from CourseCreateWindow.vue for Quality Gate G01 compliance.
 */

import { ref } from 'vue'
import { usePanelStore } from '@/application/stores/modules/admin/panel.store'

interface CourseFormData {
  title: string
  description: string
  category_id: string
  level: string
  language: string
  ai_model_override: string
}

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
const ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt']

export function useCourseFileUpload(form: { value: CourseFormData }) {
  const panelStore = usePanelStore()

  const selectedFile = ref<File | null>(null)
  const fileInput = ref<HTMLInputElement | null>(null)
  const fileError = ref<string | null>(null)
  const aiStatus = ref<'idle' | 'processing' | 'completed' | 'failed'>('idle')

  /**
   * Handle file input change event
   */
  function handleFileSelect(event: Event): void {
    const target = event.target as HTMLInputElement
    if (target.files && target.files.length > 0) {
      validateAndSetFile(target.files[0])
    }
  }

  /**
   * Validate file type and size, then set as selected
   */
  function validateAndSetFile(file: File): void {
    fileError.value = null
    aiStatus.value = 'idle'

    const ext = file.name.split('.').pop()?.toLowerCase() || ''
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      fileError.value = 'Nur PDF, Word, PowerPoint und Text-Dateien sind erlaubt'
      return
    }

    if (file.size > MAX_FILE_SIZE) {
      fileError.value = 'Datei ist zu gross (max. 50 MB)'
      return
    }

    selectedFile.value = file
  }

  /**
   * Clear selected file and reset state
   */
  function clearFile(): void {
    selectedFile.value = null
    fileError.value = null
    aiStatus.value = 'idle'
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }

  /**
   * Format file size in human-readable format
   */
  function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  /**
   * Get emoji icon for a file type
   */
  function getFileIcon(filename: string): string {
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

  /**
   * Use AI to analyze the uploaded document and fill form fields
   */
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
          fileError.value = 'Timeout: KI-Analyse dauert zu lange'
          return
        }

        try {
          const { adminGetAIJob } = await import('@/infrastructure/api/clients/panel/admin')
          const result = await adminGetAIJob(job.id)

          if (result.status === 'completed' && result.output_data) {
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
      fileError.value = error.message || 'Fehler bei der KI-Analyse'
    }
  }

  return {
    selectedFile,
    fileInput,
    fileError,
    aiStatus,
    handleFileSelect,
    clearFile,
    formatFileSize,
    getFileIcon,
    fillFieldsWithAI
  }
}
