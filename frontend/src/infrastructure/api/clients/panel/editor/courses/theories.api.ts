import http from '@/infrastructure/api/http'

import { EDITOR_PREFIX } from './constants'

// ============================================================================
// Theory Sheets (Chapter & Lesson Theory Management)
// ============================================================================

export interface TheorySheet {
  theory_id: string
  parent_id: string
  parent_type: 'chapter' | 'lesson'
  title: string
  content: string
  order_index: number | null
  is_summary: boolean | null
  created_at: string
  updated_at: string
}

export const getChapterTheories = async (chapterId: string): Promise<TheorySheet[]> => {
  const response = await http.get<{
    success: boolean
    data: TheorySheet[]
    total: number
  }>(`${EDITOR_PREFIX}/chapters/${chapterId}/theory`)

  return response.data.data || []
}

export const getLessonTheories = async (lessonId: string): Promise<TheorySheet[]> => {
  const response = await http.get<{
    success: boolean
    data: TheorySheet[]
    total: number
  }>(`${EDITOR_PREFIX}/lessons/${lessonId}/theory`)

  return response.data.data || []
}

export const createChapterTheory = async (
  chapterId: string,
  title: string,
  content: string,
  isSummary = false
): Promise<TheorySheet> => {
  const response = await http.post<{
    success: boolean
    data: TheorySheet
  }>(`${EDITOR_PREFIX}/chapters/${chapterId}/theory`, {
    title,
    content,
    is_summary: isSummary
  })

  return response.data.data
}

export const createLessonTheory = async (
  lessonId: string,
  title: string,
  content: string
): Promise<TheorySheet> => {
  const response = await http.post<{
    success: boolean
    data: TheorySheet
  }>(`${EDITOR_PREFIX}/lessons/${lessonId}/theory`, {
    title,
    content
  })

  return response.data.data
}

export const updateTheory = async (
  theoryId: string,
  payload: Partial<Pick<TheorySheet, 'title' | 'content' | 'order_index'>>
): Promise<TheorySheet> => {
  const response = await http.patch<{
    success: boolean
    data: TheorySheet
  }>(`${EDITOR_PREFIX}/theory-sheets/${theoryId}`, payload)

  return response.data.data
}

export const deleteTheory = async (theoryId: string): Promise<void> => {
  await http.delete(`${EDITOR_PREFIX}/theory-sheets/${theoryId}`)
}
