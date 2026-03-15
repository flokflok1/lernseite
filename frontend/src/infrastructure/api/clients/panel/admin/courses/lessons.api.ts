/**
 * Admin Lesson Management API
 *
 * Routes map to backend: /api/v1/course-editor/manual/*
 */

import http from '@/infrastructure/api/http'
import type {
  AdminLesson,
  AdminLessonCreateRequest,
  AdminLessonUpdateRequest
} from '../types'

const PREFIX = '/course-editor/manual'

export const adminGetChapterLessons = async (chapterId: string): Promise<AdminLesson[]> => {
  const response = await http.get<{
    success: boolean
    lessons: AdminLesson[]
  }>(`${PREFIX}/chapters/${chapterId}/lessons`)

  return response.data.lessons
}

export const adminCreateLesson = async (
  chapterId: string,
  data: AdminLessonCreateRequest
): Promise<AdminLesson> => {
  const response = await http.post<{
    success: boolean
    lesson: AdminLesson
  }>(`${PREFIX}/chapters/${chapterId}/lessons`, data)

  return response.data.lesson
}

export const adminUpdateLesson = async (
  lessonId: string,
  data: AdminLessonUpdateRequest
): Promise<AdminLesson> => {
  const response = await http.patch<{
    success: boolean
    lesson: AdminLesson
  }>(`${PREFIX}/lessons/${lessonId}`, data)

  return response.data.lesson
}

export const adminDeleteLesson = async (lessonId: string, reason?: string): Promise<void> => {
  await http.delete(`${PREFIX}/lessons/${lessonId}`, {
    data: { reason }
  })
}

export const adminReorderLessons = async (
  chapterId: string,
  lessonIds: string[]
): Promise<void> => {
  await http.post(`${PREFIX}/chapters/${chapterId}/lessons/reorder`, {
    lesson_ids: lessonIds
  })
}
