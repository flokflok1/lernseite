/**
 * useFileUpload — Manages file uploads for AI authoring sessions.
 *
 * Provides upload, delete, list, and text extraction for session files.
 * Watches the active session and auto-loads files when it changes.
 */
import { ref, watch, type Ref } from 'vue'
import {
  uploadSessionFile,
  listSessionFiles,
  deleteSessionFile,
  getFileContent,
  type FileRecord,
} from '@/infrastructure/api/clients/panel/editor/authoring/authoringFiles.api'

const ALLOWED_EXTENSIONS = [
  'pdf', 'doc', 'docx', 'ppt', 'pptx',
  'xls', 'xlsx', 'txt', 'png', 'jpg', 'jpeg',
]

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50 MB

export function useFileUpload(sessionIdRef: Ref<string | null>) {
  const files = ref<FileRecord[]>([])
  const isUploading = ref(false)
  const error = ref<string | null>(null)
  const previewFileId = ref<string | null>(null)
  const previewText = ref<string | null>(null)
  const isLoadingPreview = ref(false)

  // ── Load files when session changes ─────────────────────────────
  watch(sessionIdRef, async (id) => {
    if (id) {
      await loadFiles()
    } else {
      files.value = []
    }
  }, { immediate: true })

  // ── Actions ─────────────────────────────────────────────────────

  async function loadFiles(): Promise<void> {
    const sid = sessionIdRef.value
    if (!sid) return
    try {
      const result = await listSessionFiles(sid)
      if (sessionIdRef.value !== sid) return
      files.value = result
    } catch (e: unknown) {
      if (sessionIdRef.value !== sid) return
      console.warn('[FileUpload] Failed to load files:', e)
      files.value = []
    }
  }

  function validateFile(file: File): string | null {
    const ext = file.name.split('.').pop()?.toLowerCase() ?? ''
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `File type .${ext} is not allowed. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File is too large (max ${MAX_FILE_SIZE / 1024 / 1024} MB)`
    }
    return null
  }

  async function uploadFile(file: File): Promise<boolean> {
    const sid = sessionIdRef.value
    if (!sid) {
      error.value = 'No active session'
      return false
    }

    const validationError = validateFile(file)
    if (validationError) {
      error.value = validationError
      return false
    }

    isUploading.value = true
    error.value = null
    try {
      const record = await uploadSessionFile(sid, file)
      files.value.push(record)
      return true
    } catch (e: any) {
      error.value = e.message || 'Upload failed'
      return false
    } finally {
      isUploading.value = false
    }
  }

  async function removeFile(fileId: string): Promise<void> {
    const sid = sessionIdRef.value
    if (!sid) return
    try {
      await deleteSessionFile(sid, fileId)
      files.value = files.value.filter((f) => f.file_id !== fileId)
      if (previewFileId.value === fileId) {
        previewFileId.value = null
        previewText.value = null
      }
    } catch (e: any) {
      error.value = e.message || 'Delete failed'
    }
  }

  async function loadPreview(fileId: string): Promise<void> {
    const sid = sessionIdRef.value
    if (!sid) return

    if (previewFileId.value === fileId) {
      previewFileId.value = null
      previewText.value = null
      return
    }

    isLoadingPreview.value = true
    try {
      const result = await getFileContent(sid, fileId)
      previewFileId.value = fileId
      previewText.value = result.extracted_text || null
    } catch (e: unknown) {
      console.warn('[FileUpload] Failed to load preview:', e)
      previewText.value = null
    } finally {
      isLoadingPreview.value = false
    }
  }

  function clearPreview(): void {
    previewFileId.value = null
    previewText.value = null
  }

  function clearError(): void {
    error.value = null
  }

  return {
    files,
    isUploading,
    error,
    previewFileId,
    previewText,
    isLoadingPreview,
    loadFiles,
    uploadFile,
    removeFile,
    loadPreview,
    clearPreview,
    clearError,
  }
}
