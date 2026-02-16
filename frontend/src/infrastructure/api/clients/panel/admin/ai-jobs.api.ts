/**
 * Admin AI Job Management API
 */

import http from '@/infrastructure/api/http'
import type {
  AIJob,
  AIJobResponse,
  AIJobFinalizeRequest,
  AIJobFinalizeResponse
} from './types'

export const adminStartAIJob = async (data: FormData): Promise<AIJob> => {
  const response = await http.post<AIJobResponse>('/admin/ai/jobs', data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })

  return response.data.job
}

export const adminGetAIJob = async (jobId: string): Promise<AIJob> => {
  const response = await http.get<AIJobResponse>(`/admin/ai/jobs/${jobId}`)

  return response.data.job
}

export const adminCancelAIJob = async (jobId: string): Promise<void> => {
  await http.post(`/admin/ai/jobs/${jobId}/cancel`)
}

export const adminFinalizeAIJob = async (
  jobId: string,
  options?: AIJobFinalizeRequest
): Promise<AIJobFinalizeResponse> => {
  const response = await http.post<AIJobFinalizeResponse>(
    `/admin/ai/jobs/${jobId}/finalize`,
    options || {}
  )

  return response.data
}
