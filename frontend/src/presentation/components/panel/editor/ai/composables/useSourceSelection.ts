/**
 * useSourceSelection Composable
 *
 * Manages Phase 1a: PDF Upload & Source Selection
 * - File upload handling
 * - PDF analysis
 * - Session creation
 */

import { ref, computed, Ref } from 'vue'
import { uploadPDF, createSession, setSourceData } from '@/infrastructure/api/clients/panel/editor/ai-editor/editor.api'
import type { PDFUploadResponse, AIEditorSession, SourceType } from '@/infrastructure/api/clients/panel/editor/types/types'
import { useI18n } from 'vue-i18n'

export interface SourceSelectionState {
  sourceType: SourceType | null
  uploadedFile: File | null
  pdfAnalysis: PDFUploadResponse | null
  sessionData: AIEditorSession | null
  isLoading: boolean
  error: string | null
  currentStep: 'source-type' | 'upload' | 'summary' | 'complete'
}

export function useSourceSelection(courseId: Ref<string> | string) {
  const { t } = useI18n()

  // State
  const state = ref<SourceSelectionState>({
    sourceType: null,
    uploadedFile: null,
    pdfAnalysis: null,
    sessionData: null,
    isLoading: false,
    error: null,
    currentStep: 'source-type'
  })

  // Computed
  const canProceedToUpload = computed(() => {
    return state.value.sourceType !== null
  })

  const canProceedToSummary = computed(() => {
    return state.value.pdfAnalysis !== null
  })

  const canFinalize = computed(() => {
    return state.value.pdfAnalysis !== null && state.value.sessionData !== null
  })

  // Methods

  /**
   * Select source type (pdf, manual, template, etc.)
   */
  function selectSourceType(type: SourceType) {
    state.value.sourceType = type
    state.value.error = null

    if (type === 'pdf') {
      state.value.currentStep = 'upload'
    } else if (type === 'manual') {
      state.value.currentStep = 'summary'
    } else if (type === 'template') {
      state.value.currentStep = 'summary'
    }
  }

  /**
   * Handle document file upload and analysis
   * Supports: PDF, Word (DOC, DOCX), PowerPoint (PPT, PPTX), OpenDocument (ODT, ODP)
   */
  async function uploadPDFFile(file: File): Promise<void> {
    state.value.isLoading = true
    state.value.error = null

    try {
      // Validate file type - accept PDF and common document formats
      const validMimeTypes = [
        'application/pdf',
        'application/msword', // .doc
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
        'application/vnd.ms-powerpoint', // .ppt
        'application/vnd.openxmlformats-officedocument.presentationml.presentation', // .pptx
        'application/vnd.oasis.opendocument.presentation', // .odp
        'application/vnd.oasis.opendocument.text' // .odt
      ]

      if (!validMimeTypes.includes(file.type)) {
        throw new Error(t('courses.editor.invalidFileType'))
      }

      if (file.size > 50 * 1024 * 1024) { // 50MB limit
        throw new Error(t('courses.editor.fileTooLarge'))
      }

      // Upload to backend
      const analysis = await uploadPDF(file)

      // Store results
      state.value.uploadedFile = file
      state.value.pdfAnalysis = analysis
      state.value.currentStep = 'summary'

      // Auto-create session with PDF source data
      const courseIdValue = typeof courseId === 'string' ? courseId : courseId.value
      const session = await createSession({
        course_id: courseIdValue,
        source_type: 'pdf'
      })

      // Set source data on session
      await setSourceData(session.session_id, {
        source_type: 'pdf',
        source_data: {
          file_name: file.name,
          file_hash: analysis.file_hash,
          page_count: analysis.page_count,
          word_count: analysis.word_count
        }
      })

      state.value.sessionData = session
    } catch (err) {
      state.value.error = err instanceof Error ? err.message : t('common.unknownError')
      console.error('PDF Upload Error:', err)
    } finally {
      state.value.isLoading = false
    }
  }

  /**
   * Create new session for manual source
   */
  async function createManualSession(): Promise<void> {
    state.value.isLoading = true
    state.value.error = null

    try {
      const courseIdValue = typeof courseId === 'string' ? courseId : courseId.value
      const session = await createSession({
        course_id: courseIdValue,
        source_type: 'manual'
      })

      state.value.sessionData = session
      state.value.currentStep = 'complete'
    } catch (err) {
      state.value.error = err instanceof Error ? err.message : t('common.unknownError')
      console.error('Session Creation Error:', err)
    } finally {
      state.value.isLoading = false
    }
  }

  /**
   * Go to previous step
   */
  function goToPreviousStep() {
    if (state.value.currentStep === 'upload') {
      state.value.currentStep = 'source-type'
      state.value.uploadedFile = null
      state.value.pdfAnalysis = null
    } else if (state.value.currentStep === 'summary') {
      if (state.value.sourceType === 'pdf') {
        state.value.currentStep = 'upload'
      } else {
        state.value.currentStep = 'source-type'
      }
    }
    state.value.error = null
  }

  /**
   * Reset selection
   */
  function reset() {
    state.value = {
      sourceType: null,
      uploadedFile: null,
      pdfAnalysis: null,
      sessionData: null,
      isLoading: false,
      error: null,
      currentStep: 'source-type'
    }
  }

  return {
    // State
    state: computed(() => state.value),
    sourceType: computed(() => state.value.sourceType),
    uploadedFile: computed(() => state.value.uploadedFile),
    pdfAnalysis: computed(() => state.value.pdfAnalysis),
    sessionData: computed(() => state.value.sessionData),
    isLoading: computed(() => state.value.isLoading),
    error: computed(() => state.value.error),
    currentStep: computed(() => state.value.currentStep),

    // Computed
    canProceedToUpload,
    canProceedToSummary,
    canFinalize,

    // Methods
    selectSourceType,
    uploadPDFFile,
    createManualSession,
    goToPreviousStep,
    reset
  }
}
