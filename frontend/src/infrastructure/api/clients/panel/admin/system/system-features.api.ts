/**
 * LernsystemX Admin API - System Features
 *
 * API client for system feature configuration (activate/deactivate).
 */

import http from '@/infrastructure/api/http'

// ============================================================================
// Types
// ============================================================================

export interface SystemFeature {
  feature_id: number
  feature_code: string
  feature_name: string
  description: string | null
  category: string
  active: boolean
  icon: string | null
  requires_infrastructure: boolean
  requires_external_service: boolean
  config: Record<string, unknown> | null
}

export interface SystemFeaturesResponse {
  success: boolean
  data: SystemFeature[]
  meta: {
    total: number
    categories: string[]
  }
}

// ============================================================================
// API Functions
// ============================================================================

export async function getSystemFeatures(params?: {
  category?: string
  include_inactive?: boolean
}): Promise<{ features: SystemFeature[]; total: number; categories: string[] }> {
  const response = await http.get<SystemFeaturesResponse>(
    '/panel/system-features',
    { params }
  )
  return {
    features: response.data.data,
    total: response.data.meta.total,
    categories: response.data.meta.categories
  }
}

export async function updateSystemFeature(
  featureId: number,
  data: Partial<Pick<SystemFeature, 'active' | 'config' | 'feature_name' | 'description' | 'icon'>>
): Promise<SystemFeature> {
  const response = await http.patch<{ success: boolean; data: SystemFeature }>(
    `/panel/system-features/${featureId}`,
    data
  )
  return response.data.data
}
