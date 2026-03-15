/**
 * Admin Chapter & Category Management API
 *
 * Chapter routes map to backend: /api/v1/course-editor/manual/*
 */

import http from '@/infrastructure/api/http'
import type {
  AdminChapter,
  AdminChapterCreateRequest,
  AdminChapterUpdateRequest,
  Category,
  CategoryTree,
  CategoryTreeNode,
  CategoryFilterParams
} from '../types'

const PREFIX = '/course-editor/manual'

// Chapter Management

export const adminGetCourseChapters = async (courseId: string): Promise<AdminChapter[]> => {
  const response = await http.get<{
    success: boolean
    chapters: AdminChapter[]
  }>(`${PREFIX}/courses/${courseId}/chapters`)

  return response.data.chapters
}

export const adminCreateChapter = async (
  courseId: string,
  data: AdminChapterCreateRequest
): Promise<AdminChapter> => {
  const response = await http.post<{
    success: boolean
    chapter: AdminChapter
  }>(`${PREFIX}/courses/${courseId}/chapters`, data)

  return response.data.chapter
}

export const adminUpdateChapter = async (
  chapterId: string,
  data: AdminChapterUpdateRequest
): Promise<AdminChapter> => {
  const response = await http.patch<{
    success: boolean
    chapter: AdminChapter
  }>(`${PREFIX}/chapters/${chapterId}`, data)

  return response.data.chapter
}

export const adminDeleteChapter = async (chapterId: string, reason?: string): Promise<void> => {
  await http.delete(`${PREFIX}/chapters/${chapterId}`, {
    data: { reason }
  })
}

export const adminReorderChapters = async (
  courseId: string,
  chapterIds: string[]
): Promise<void> => {
  await http.post(`${PREFIX}/courses/${courseId}/chapters/reorder`, {
    chapter_ids: chapterIds
  })
}

// Category Management

export const adminGetCategoriesTree = async (activeOnly: boolean = true): Promise<CategoryTree> => {
  const response = await http.get<{
    success: boolean
    tree: CategoryTreeNode[]
  }>('/categories/tree', {
    params: { active_only: activeOnly }
  })

  return { tree: response.data.tree }
}

export const adminGetCategories = async (params?: CategoryFilterParams): Promise<Category[]> => {
  const response = await http.get<{
    success: boolean
    categories: Category[]
  }>('/categories', { params })

  return response.data.categories
}

export const adminCreateCategory = async (categoryData: Record<string, unknown>): Promise<Category> => {
  const response = await http.post<{
    success: boolean
    category: Category
  }>('/admin/categories', categoryData)

  return response.data.category
}

export const adminUpdateCategory = async (
  categoryId: number,
  categoryData: Record<string, unknown>
): Promise<Category> => {
  const response = await http.patch<{
    success: boolean
    category: Category
  }>(`/admin/categories/${categoryId}`, categoryData)

  return response.data.category
}

export const adminDeleteCategory = async (categoryId: number): Promise<void> => {
  await http.delete(`/admin/categories/${categoryId}`)
}
