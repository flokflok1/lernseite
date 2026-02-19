/**
 * Admin Course Files Management API
 */

import http from '@/infrastructure/api/http'
import type {
  CourseFile,
  CourseFilesListResponse,
  CourseFileUploadData,
  CourseFileUploadResponse,
  CourseFileUpdateRequest,
  CourseFileCategory,
  CourseFileCategorySummary
} from '../types'

export const adminListCourseFiles = async (
  courseId: string,
  category?: CourseFileCategory,
  limit = 100,
  offset = 0
): Promise<CourseFilesListResponse> => {
  const params: Record<string, unknown> = { limit, offset }
  if (category) {
    params.category = category
  }

  const response = await http.get<{
    success: boolean
    files: CourseFile[]
    total: number
    categories_summary: CourseFileCategorySummary[]
  }>(`/admin/courses/${courseId}/files`, { params })

  return {
    files: response.data.files,
    total: response.data.total,
    categories_summary: response.data.categories_summary
  }
}

export const adminUploadCourseFile = async (
  courseId: string,
  file: File,
  data: CourseFileUploadData = {}
): Promise<CourseFileUploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)

  if (data.display_name) {
    formData.append('display_name', data.display_name)
  }
  if (data.description) {
    formData.append('description', data.description)
  }
  if (data.file_category) {
    formData.append('file_category', data.file_category)
  }
  if (data.is_public !== undefined) {
    formData.append('is_public', data.is_public ? 'true' : 'false')
  }

  const response = await http.post<{
    success: boolean
    file: CourseFile
    already_exists?: boolean
    message?: string
  }>(
    `/admin/courses/${courseId}/files`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  )

  return {
    file: response.data.file,
    already_exists: response.data.already_exists,
    message: response.data.message
  }
}

export const adminGetCourseFile = async (
  courseId: string,
  fileId: string
): Promise<CourseFile> => {
  const response = await http.get<{ success: boolean; file: CourseFile }>(
    `/admin/courses/${courseId}/files/${fileId}`
  )
  return response.data.file
}

export const adminUpdateCourseFile = async (
  courseId: string,
  fileId: string,
  data: CourseFileUpdateRequest
): Promise<CourseFile> => {
  const response = await http.patch<{ success: boolean; file: CourseFile }>(
    `/admin/courses/${courseId}/files/${fileId}`,
    data
  )
  return response.data.file
}

export const adminDeleteCourseFile = async (
  courseId: string,
  fileId: string
): Promise<void> => {
  await http.delete(`/admin/courses/${courseId}/files/${fileId}`)
}

export const adminReorderCourseFiles = async (
  courseId: string,
  fileIds: string[]
): Promise<void> => {
  await http.post(`/admin/courses/${courseId}/files/reorder`, {
    file_ids: fileIds
  })
}
