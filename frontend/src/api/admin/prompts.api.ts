/**
 * Admin Course Prompts API
 */

import http from '../http'
import type {
  CoursePrompt,
  CoursePromptUpdateRequest,
  CoursePromptResolveResponse,
  PromptScope
} from './types'

export const adminListCoursePrompts = async (
  courseId: string,
  includeInactive = false
): Promise<CoursePrompt[]> => {
  const response = await http.get<{ success: boolean; prompts: CoursePrompt[] }>(
    `/admin/courses/${courseId}/prompts`,
    { params: { include_inactive: includeInactive } }
  )
  return response.data.prompts
}

export const adminGetCoursePrompt = async (
  courseId: string,
  scope: PromptScope,
  language?: string | null
): Promise<{
  prompt: CoursePrompt | null
  resolved: CoursePromptResolveResponse
  source: string
}> => {
  const response = await http.get<{
    success: boolean
    prompt: CoursePrompt | null
    resolved?: CoursePromptResolveResponse
    source: string
  }>(`/admin/courses/${courseId}/prompts/${scope}`, {
    params: language ? { language } : {}
  })

  return {
    prompt: response.data.prompt,
    resolved: response.data.resolved!,
    source: response.data.source
  }
}

export const adminUpsertCoursePrompt = async (
  courseId: string,
  scope: PromptScope,
  data: CoursePromptUpdateRequest
): Promise<{ prompt: CoursePrompt; created: boolean }> => {
  const response = await http.put<{
    success: boolean
    prompt: CoursePrompt
    created: boolean
  }>(`/admin/courses/${courseId}/prompts/${scope}`, data)

  return {
    prompt: response.data.prompt,
    created: response.data.created
  }
}

export const adminDeleteCoursePrompt = async (
  courseId: string,
  scope: PromptScope,
  language?: string | null
): Promise<void> => {
  await http.delete(`/admin/courses/${courseId}/prompts/${scope}`, {
    params: language ? { language } : {}
  })
}

export const adminBulkResetCoursePrompts = async (
  courseId: string,
  scopes?: PromptScope[]
): Promise<{ message: string }> => {
  const response = await http.post<{
    success: boolean
    message: string
  }>(`/admin/courses/${courseId}/prompts/reset`, {
    scopes: scopes || null,
    confirm: true
  })

  return {
    message: response.data.message
  }
}

export const adminResolveCoursePrompt = async (
  courseId: string,
  scope: PromptScope,
  language?: string | null
): Promise<CoursePromptResolveResponse> => {
  const response = await http.post<{
    success: boolean
    resolved: CoursePromptResolveResponse
  }>(`/admin/courses/${courseId}/prompts/resolve`, {
    scope,
    language: language || null
  })

  return response.data.resolved
}
