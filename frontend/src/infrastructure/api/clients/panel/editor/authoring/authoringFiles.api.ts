/**
 * Authoring Files API
 *
 * File upload, listing, deletion, and text extraction for AI authoring sessions.
 */

import http from '@/infrastructure/api/http'

export interface FileRecord {
  file_id: string
  filename: string
  file_type: string
  file_size_bytes: number
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed'
  has_extracted_text?: boolean
  uploaded_at?: string
}

/**
 * Upload a file to an authoring session
 */
export async function uploadSessionFile(
  sessionId: string,
  file: File
): Promise<FileRecord> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await http.post(
    `/course-editor/ai/authoring/sessions/${sessionId}/files`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data?.data
}

/**
 * List all files for a session
 */
export async function listSessionFiles(
  sessionId: string
): Promise<FileRecord[]> {
  const response = await http.get(
    `/course-editor/ai/authoring/sessions/${sessionId}/files`
  )
  return response.data?.data?.files ?? []
}

/**
 * Delete a file from a session
 */
export async function deleteSessionFile(
  sessionId: string,
  fileId: string
): Promise<void> {
  await http.delete(
    `/course-editor/ai/authoring/sessions/${sessionId}/files/${fileId}`
  )
}

/**
 * Get extracted text content for a file
 */
export async function getFileContent(
  sessionId: string,
  fileId: string
): Promise<{ extracted_text: string }> {
  const response = await http.get(
    `/course-editor/ai/authoring/sessions/${sessionId}/files/${fileId}/content`
  )
  return response.data?.data
}
