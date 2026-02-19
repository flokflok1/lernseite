/**
 * API client for LM Plugins (Admin)
 *
 * 8 endpoints for plugin discovery, approval, and management.
 */
import http from '@/infrastructure/api/http'
import type {
  LMPluginMetadata,
  ScanPluginsResponse,
  APIResponse
} from '@/domain/models/learning/plugins.types'

/**
 * Admin LM Plugins API
 */
export const lmPluginsApi = {
  /**
   * Trigger plugin discovery scan
   * POST /api/v1/admin/plugins/learning-methods/scan
   */
  async scan(): Promise<APIResponse<ScanPluginsResponse>> {
    const response = await http.post('/admin/plugins/learning-methods/scan')
    return response.data
  },

  /**
   * Get all plugins pending review
   * GET /api/v1/admin/plugins/learning-methods/pending
   */
  async getPending(): Promise<APIResponse<LMPluginMetadata[]>> {
    const response = await http.get('/admin/plugins/learning-methods/pending')
    return response.data
  },

  /**
   * Get all active plugins
   * GET /api/v1/admin/plugins/learning-methods/active
   */
  async getActive(): Promise<APIResponse<LMPluginMetadata[]>> {
    const response = await http.get('/admin/plugins/learning-methods/active')
    return response.data
  },

  /**
   * Get plugin detail by ID
   * GET /api/v1/admin/plugins/learning-methods/:pluginId
   */
  async getDetail(pluginId: string): Promise<APIResponse<LMPluginMetadata>> {
    const response = await http.get(`/admin/plugins/learning-methods/${pluginId}`)
    return response.data
  },

  /**
   * Approve a pending plugin
   * POST /api/v1/admin/plugins/learning-methods/:pluginId/approve
   */
  async approve(pluginId: string): Promise<APIResponse<{ plugin_id: string; status: string }>> {
    const response = await http.post(`/admin/plugins/learning-methods/${pluginId}/approve`)
    return response.data
  },

  /**
   * Reject a pending plugin
   * POST /api/v1/admin/plugins/learning-methods/:pluginId/reject
   */
  async reject(pluginId: string, reason: string): Promise<APIResponse<{ plugin_id: string; status: string }>> {
    const response = await http.post(`/admin/plugins/learning-methods/${pluginId}/reject`, { reason })
    return response.data
  },

  /**
   * Activate an approved plugin
   * POST /api/v1/admin/plugins/learning-methods/:pluginId/activate
   */
  async activate(pluginId: string): Promise<APIResponse<{ plugin_id: string; status: string }>> {
    const response = await http.post(`/admin/plugins/learning-methods/${pluginId}/activate`)
    return response.data
  },

  /**
   * Deactivate an active plugin
   * POST /api/v1/admin/plugins/learning-methods/:pluginId/deactivate
   */
  async deactivate(pluginId: string): Promise<APIResponse<{ plugin_id: string; status: string }>> {
    const response = await http.post(`/admin/plugins/learning-methods/${pluginId}/deactivate`)
    return response.data
  }
}
