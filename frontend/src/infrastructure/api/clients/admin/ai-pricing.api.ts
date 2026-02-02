/**
 * Admin AI Pricing API
 *
 * Price management for AI models:
 * - List all models with pricing
 * - Update single model pricing
 * - Bulk update prices
 * - Apply margin to selection
 */
import http from '@/infrastructure/api/http'
import type {
  AIModelPricing,
  AIModelPricingResponse,
  AIModelPricingUpdateRequest,
  AIModelBulkPricingRequest,
  AIModelApplyMarginRequest,
  AIModelBulkPricingResponse
} from './types'

export interface PricingFilterParams {
  include_inactive?: boolean
  provider?: string
  category?: string
}

/**
 * Get all AI models with pricing information
 */
export const adminGetAIPricing = async (
  params: PricingFilterParams = {}
): Promise<AIModelPricingResponse> => {
  const response = await http.get<AIModelPricingResponse>('/admin/ai/pricing', {
    params: {
      include_inactive: params.include_inactive ? 'true' : 'false',
      provider: params.provider || undefined,
      category: params.category || undefined
    }
  })
  return response.data
}

/**
 * Update pricing for a single AI model
 */
export const adminUpdateAIPricing = async (
  modelId: number,
  data: AIModelPricingUpdateRequest
): Promise<AIModelPricing> => {
  const response = await http.put<{
    success: boolean
    data: AIModelPricing
    message: string
  }>(`/admin/ai/pricing/${modelId}`, data)
  return response.data.data
}

/**
 * Bulk update pricing for multiple models
 */
export const adminBulkUpdateAIPricing = async (
  data: AIModelBulkPricingRequest
): Promise<AIModelBulkPricingResponse> => {
  const response = await http.post<AIModelBulkPricingResponse>(
    '/admin/ai/pricing/bulk',
    data
  )
  return response.data
}

/**
 * Apply margin percentage to selected models
 * Calculates: price = cost * (1 + margin_percent/100)
 */
export const adminApplyPricingMargin = async (
  data: AIModelApplyMarginRequest
): Promise<AIModelBulkPricingResponse> => {
  const response = await http.post<AIModelBulkPricingResponse>(
    '/admin/ai/pricing/apply-margin',
    data
  )
  return response.data
}
