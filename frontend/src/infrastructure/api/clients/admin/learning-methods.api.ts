/**
 * Admin Learning Methods Management API
 */

import http from '@/infrastructure/api/http'
import type {
  LearningMethodTypesResponse,
  AdminLearningMethod,
  AdminLearningMethodsResponse,
  AdminLearningMethodCreateRequest,
  AdminLearningMethodUpdateRequest
} from './types'

export const adminGetLearningMethodTypes = async (): Promise<LearningMethodTypesResponse> => {
  const response = await http.get<LearningMethodTypesResponse>(
    '/admin/learning-method-types'
  )
  return response.data
}

export const adminGetChapterLearningMethods = async (
  chapterId: string,
  publishedOnly = false
): Promise<AdminLearningMethodsResponse> => {
  const response = await http.get<AdminLearningMethodsResponse>(
    `/admin/chapters/${chapterId}/learning-methods`,
    { params: { published_only: publishedOnly } }
  )
  return response.data
}

export const adminGetLearningMethod = async (
  methodId: string
): Promise<AdminLearningMethod> => {
  const response = await http.get<{
    success: boolean
    learning_method: AdminLearningMethod
  }>(`/admin/learning-methods/${methodId}`)
  return response.data.learning_method
}

export const adminCreateLearningMethod = async (
  chapterId: string,
  data: AdminLearningMethodCreateRequest
): Promise<AdminLearningMethod> => {
  const response = await http.post<{
    success: boolean
    learning_method: AdminLearningMethod
    message: string
  }>(`/admin/chapters/${chapterId}/learning-methods`, data)
  return response.data.learning_method
}

export const adminUpdateLearningMethod = async (
  methodId: string,
  data: AdminLearningMethodUpdateRequest
): Promise<AdminLearningMethod> => {
  const response = await http.patch<{
    success: boolean
    learning_method: AdminLearningMethod
    message: string
  }>(`/admin/learning-methods/${methodId}`, data)
  return response.data.learning_method
}

export const adminDeleteLearningMethod = async (
  methodId: string
): Promise<void> => {
  await http.delete(`/admin/learning-methods/${methodId}`)
}

export const adminReorderLearningMethods = async (
  chapterId: string,
  methodIds: string[]
): Promise<void> => {
  await http.post(`/admin/chapters/${chapterId}/learning-methods/reorder`, {
    method_ids: methodIds
  })
}

export const adminPublishLearningMethod = async (
  methodId: string
): Promise<AdminLearningMethod> => {
  const response = await http.post<{
    success: boolean
    learning_method: AdminLearningMethod
    message: string
  }>(`/admin/learning-methods/${methodId}/publish`)
  return response.data.learning_method
}

export const adminUnpublishLearningMethod = async (
  methodId: string
): Promise<AdminLearningMethod> => {
  const response = await http.post<{
    success: boolean
    learning_method: AdminLearningMethod
    message: string
  }>(`/admin/learning-methods/${methodId}/unpublish`)
  return response.data.learning_method
}
