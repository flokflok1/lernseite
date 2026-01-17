/**
 * useFileManagement - Course File Management
 *
 * Manages course files: upload, delete, selection, and preview.
 *
 * @module kurs-builder/composables/useFileManagement
 */

import { ref, computed, type Ref } from 'vue'
import http from '@/api/http'
import type { CourseFile } from '../types'

/**
 * File Management Composable
 *
 * Provides reactive file management for course authoring with
 * upload, selection, and preview capabilities.
 *
 * @param courseId - Reactive course ID reference
 * @param onOpenPreview - Optional callback to open file preview window
 * @returns File management state and methods
 *
 * @example
 * ```typescript
 * const fileMgr = useFileManagement(
 *   computed(() => props.courseId),
 *   (file) => windowStore.openPanel({ type: 'file-preview', payload: { file } })
 * )
 *
 * // Load files
 * await fileMgr.loadFiles()
 *
 * // Upload file
 * await fileMgr.uploadFile(myFile)
 *
 * // Select files for AI context
 * fileMgr.toggleSelection('file-123')
 * ```
 */
export function useFileManagement(
  courseId: Ref<string | undefined>,
  onOpenPreview?: (file: CourseFile) => void
) {
  // State
  const files = ref<CourseFile[]>([])
  const selectedIds = ref<string[]>([])
  const uploading = ref(false)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const hasFiles = computed(() => files.value.length > 0)
  const hasSelection = computed(() => selectedIds.value.length > 0)
  const selectedCount = computed(() => selectedIds.value.length)
  const allSelected = computed(() =>
    files.value.length > 0 && selectedIds.value.length === files.value.length
  )

  /**
   * Load course files from API
   *
   * Fetches all files associated with the current course.
   *
   * @throws {Error} If course ID is not set or API call fails
   */
  async function loadFiles(): Promise<void> {
    if (!courseId.value) {
      error.value = 'Keine Kurs-ID verfügbar'
      return
    }

    loading.value = true
    error.value = null

    try {
      const res = await http.get(`/admin/courses/${courseId.value}/files`)

      if (res.data.success) {
        const apiFiles = res.data.files || []

        // Map API response to CourseFile type
        files.value = apiFiles.map((f: any) => ({
          id: f.course_file_id || f.file_id,
          name: f.display_name || f.file_name || 'Unbekannt',
          type: f.file_type || 'pdf',
          size: f.file_size_bytes || 0,
          parsed: f.is_parsed || false,
          url: f.public_url || f.cdn_url || null
        }))
      } else {
        error.value = res.data.error || 'Fehler beim Laden der Dateien'
      }
    } catch (err: any) {
      error.value = 'Fehler beim Laden: ' + (err.message || 'Unbekannt')
      console.error('Failed to load files:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * Upload a new file
   *
   * Uploads a file to the current course and reloads the file list.
   *
   * @param file - File object to upload
   * @returns True if upload succeeded, false otherwise
   */
  async function uploadFile(file: File): Promise<boolean> {
    if (!courseId.value) {
      error.value = 'Keine Kurs-ID verfügbar'
      return false
    }

    uploading.value = true
    error.value = null

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_category', 'material')

      const res = await http.post(
        `/admin/courses/${courseId.value}/files`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      )

      if (res.data.success) {
        // Reload files list
        await loadFiles()
        return true
      } else {
        error.value = res.data.error || 'Upload fehlgeschlagen'
        return false
      }
    } catch (err: any) {
      error.value = 'Upload-Fehler: ' + (err.message || 'Unbekannt')
      console.error('File upload failed:', err)
      return false
    } finally {
      uploading.value = false
    }
  }

  /**
   * Upload multiple files
   *
   * Uploads multiple files sequentially and reloads the file list.
   *
   * @param fileList - Array of File objects or FileList
   * @returns Number of successfully uploaded files
   */
  async function uploadFiles(fileList: File[] | FileList): Promise<number> {
    const filesArray = Array.from(fileList)
    let successCount = 0

    uploading.value = true
    error.value = null

    try {
      for (const file of filesArray) {
        const success = await uploadFile(file)
        if (success) successCount++
      }

      return successCount
    } finally {
      uploading.value = false
    }
  }

  /**
   * Delete a file
   *
   * Deletes a file from the course and updates the file list.
   *
   * @param fileId - File ID to delete
   * @returns True if deletion succeeded, false otherwise
   */
  async function deleteFile(fileId: string): Promise<boolean> {
    if (!courseId.value) {
      error.value = 'Keine Kurs-ID verfügbar'
      return false
    }

    try {
      const res = await http.delete(
        `/admin/courses/${courseId.value}/files/${fileId}`
      )

      if (res.data.success) {
        // Remove from local state
        files.value = files.value.filter(f => f.id !== fileId)

        // Remove from selection if selected
        const idx = selectedIds.value.indexOf(fileId)
        if (idx !== -1) {
          selectedIds.value.splice(idx, 1)
        }

        return true
      } else {
        error.value = res.data.error || 'Löschen fehlgeschlagen'
        return false
      }
    } catch (err: any) {
      error.value = 'Lösch-Fehler: ' + (err.message || 'Unbekannt')
      console.error('File delete failed:', err)
      return false
    }
  }

  /**
   * Toggle file selection
   *
   * Adds or removes a file from the selection list.
   * Selected files are used as context for AI operations.
   *
   * @param fileId - File ID to toggle
   */
  function toggleSelection(fileId: string): void {
    const idx = selectedIds.value.indexOf(fileId)
    if (idx === -1) {
      selectedIds.value.push(fileId)
    } else {
      selectedIds.value.splice(idx, 1)
    }
  }

  /**
   * Toggle all files selection
   *
   * If all files are selected, deselects all.
   * If some or none are selected, selects all.
   */
  function toggleSelectAll(): void {
    if (allSelected.value) {
      selectedIds.value = []
    } else {
      selectedIds.value = files.value.map(f => f.id)
    }
  }

  /**
   * Clear all selections
   *
   * Deselects all files.
   */
  function clearSelection(): void {
    selectedIds.value = []
  }

  /**
   * Open file preview
   *
   * Triggers the preview callback if provided.
   *
   * @param file - File to preview
   */
  function openPreview(file: CourseFile): void {
    if (onOpenPreview) {
      onOpenPreview(file)
    } else {
      console.warn('No preview handler configured')
    }
  }

  /**
   * Reset all state
   *
   * Clears files, selections, and error state.
   * Used when switching courses or closing component.
   */
  function reset(): void {
    files.value = []
    selectedIds.value = []
    error.value = null
    uploading.value = false
    loading.value = false
  }

  return {
    // State
    files,
    selectedIds,
    uploading,
    loading,
    error,

    // Computed
    hasFiles,
    hasSelection,
    selectedCount,
    allSelected,

    // Methods
    loadFiles,
    uploadFile,
    uploadFiles,
    deleteFile,
    toggleSelection,
    toggleSelectAll,
    clearSelection,
    openPreview,
    reset
  }
}
