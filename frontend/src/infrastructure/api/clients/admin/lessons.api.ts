/**
 * Admin Lesson Management API
 */

import http from '@/infrastructure/api/http'
import type {
  AdminLesson,
  AdminLessonCreateRequest,
  AdminLessonUpdateRequest
} from './types'

export const adminGetChapterLessons = async (chapterId: string): Promise<AdminLesson[]> => {
  const response = await http.get<{
    success: boolean
    lessons: AdminLesson[]
  }>(`/admin/chapters/${chapterId}/lessons`)

  return response.data.lessons
}

export const adminCreateLesson = async (
  chapterId: string,
  data: AdminLessonCreateRequest
): Promise<AdminLesson> => {
  const response = await http.post<{
    success: boolean
    lesson: AdminLesson
  }>(`/admin/chapters/${chapterId}/lessons`, data)

  return response.data.lesson
}

export const adminUpdateLesson = async (
  lessonId: string,
  data: AdminLessonUpdateRequest
): Promise<AdminLesson> => {
  const response = await http.patch<{
    success: boolean
    lesson: AdminLesson
  }>(`/admin/lessons/${lessonId}`, data)

  return response.data.lesson
}

export const adminDeleteLesson = async (lessonId: string, reason?: string): Promise<void> => {
  await http.delete(`/admin/lessons/${lessonId}`, {
    data: { reason }
  })
}

export const adminReorderLessons = async (
  chapterId: string,
  lessonIds: string[]
): Promise<void> => {
  await http.post(`/admin/chapters/${chapterId}/lessons/reorder`, {
    lesson_ids: lessonIds
  })
}
