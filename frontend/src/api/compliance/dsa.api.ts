/**
 * DSA Compliance API (Digital Services Act)
 *
 * Handles content moderation reporting, appeal processes, and user complaint
 * management for compliance with EU Digital Services Act (DSA) requirements.
 *
 * The DSA requires platforms to:
 * - Allow users to report illegal or harmful content
 * - Provide moderation decisions with reasoning
 * - Enable appeals of moderation decisions
 * - Track and report on moderation actions
 *
 * Endpoints:
 * - POST /compliance/dsa/report - Report content to moderators
 * - GET /compliance/dsa/reports - List user's reports
 * - GET /compliance/dsa/reports/:reportId - Get report details
 * - POST /compliance/dsa/appeals - Appeal moderation decision
 * - GET /compliance/dsa/appeals - List user's appeals
 * - GET /compliance/dsa/appeals/:appealId - Get appeal details
 */

import http from '../http'
import type {
  DSAReportRequest,
  DSAReportResponse,
  DSAReport,
  DSAReportList,
  DSAAppealRequest,
  DSAAppealResponse,
  DSAAppeal,
  DSAAppealList,
} from './types'

/**
 * Report content violation to moderators (DSA Transparency).
 *
 * Users can report content they believe violates policies or laws.
 * Reports are tracked and moderators respond with decisions.
 *
 * @param request - Report details including content reference and violation type
 * @returns Report confirmation with tracking ID
 *
 * @example
 * const report = await reportContent({
 *   content_id: 'post-12345',
 *   content_type: 'post',
 *   violation_type: 'harassment',
 *   description: 'This post contains hateful language targeting a group'
 * })
 * console.log('Report submitted:', report.report_id)
 */
export const reportContent = async (request: DSAReportRequest): Promise<DSAReportResponse> => {
  const response = await http.post<{ success: boolean; data: DSAReportResponse }>(
    '/compliance/dsa/report',
    request
  )
  return response.data.data
}

/**
 * Get list of all user's content reports.
 *
 * Retrieve paginated list of reports submitted by the current user.
 * Includes report status and moderator decisions.
 *
 * @param params - Pagination and filter parameters
 * @returns Paginated list of user's reports
 *
 * @example
 * const reports = await getMyReports({ limit: 20, offset: 0 })
 * reports.data.forEach(report => {
 *   console.log(`Report #${report.report_id}: ${report.status}`)
 * })
 */
export const getMyReports = async (params?: {
  limit?: number
  offset?: number
  status?: 'pending' | 'under_review' | 'resolved' | 'dismissed'
}): Promise<DSAReportList> => {
  const response = await http.get<{ success: boolean; data: DSAReportList }>(
    '/compliance/dsa/reports',
    { params }
  )
  return response.data.data
}

/**
 * Get detailed information about a specific report.
 *
 * Retrieve full details of a report including moderator's decision,
 * reasoning, and any actions taken.
 *
 * @param reportId - ID of the report to retrieve
 * @returns Full report details with moderation outcome
 *
 * @example
 * const report = await getReportDetails('report-67890')
 * if (report.status === 'resolved') {
 *   console.log('Decision:', report.moderator_decision)
 *   console.log('Reason:', report.moderator_reasoning)
 * }
 */
export const getReportDetails = async (reportId: string): Promise<DSAReport> => {
  const response = await http.get<{ success: boolean; data: DSAReport }>(
    `/compliance/dsa/reports/${reportId}`
  )
  return response.data.data
}

/**
 * Appeal a moderation decision (DSA Right to Remedy).
 *
 * Users can appeal moderation decisions they believe are incorrect.
 * Appeals are reviewed by a different moderator for fairness.
 *
 * @param request - Appeal request with original moderation decision reference
 * @returns Appeal confirmation with tracking ID
 *
 * @example
 * const appeal = await appealModerationDecision({
 *   moderation_decision_id: 'mod-12345',
 *   content_id: 'post-12345',
 *   reason: 'This post does not violate any policy. It is legitimate criticism.',
 *   additional_evidence: 'Here is context showing the post is acceptable...'
 * })
 */
export const appealModerationDecision = async (request: DSAAppealRequest): Promise<DSAAppealResponse> => {
  const response = await http.post<{ success: boolean; data: DSAAppealResponse }>(
    '/compliance/dsa/appeals',
    request
  )
  return response.data.data
}

/**
 * Get list of all user's moderation appeals.
 *
 * Retrieve paginated list of appeals submitted by the current user.
 * Includes appeal status and outcome.
 *
 * @param params - Pagination and filter parameters
 * @returns Paginated list of user's appeals
 *
 * @example
 * const appeals = await getMyAppeals({ limit: 10, offset: 0 })
 * appeals.data.forEach(appeal => {
 *   console.log(`Appeal status: ${appeal.status}`)
 * })
 */
export const getMyAppeals = async (params?: {
  limit?: number
  offset?: number
  status?: 'pending' | 'under_review' | 'upheld' | 'overturned'
}): Promise<DSAAppealList> => {
  const response = await http.get<{ success: boolean; data: DSAAppealList }>(
    '/compliance/dsa/appeals',
    { params }
  )
  return response.data.data
}

/**
 * Get detailed information about a specific appeal.
 *
 * Retrieve full details of an appeal including appeal board decision,
 * reasoning, and any corrective actions.
 *
 * @param appealId - ID of the appeal to retrieve
 * @returns Full appeal details with outcome
 *
 * @example
 * const appeal = await getAppealDetails('appeal-11111')
 * console.log('Appeal decision:', appeal.decision_outcome)
 * console.log('Appeal reasoning:', appeal.decision_reasoning)
 */
export const getAppealDetails = async (appealId: string): Promise<DSAAppeal> => {
  const response = await http.get<{ success: boolean; data: DSAAppeal }>(
    `/compliance/dsa/appeals/${appealId}`
  )
  return response.data.data
}

/**
 * Get DSA transparency report for user.
 *
 * Retrieve aggregate statistics about moderation actions, content restrictions,
 * and account limitations applied to the current user.
 *
 * @returns Transparency report with moderation statistics
 *
 * @example
 * const report = await getDSATransparencyReport()
 * console.log('Content removed:', report.total_content_removed)
 * console.log('Appeals won:', report.appeals_overturned)
 */
export const getDSATransparencyReport = async () => {
  const response = await http.get<{
    success: boolean
    data: {
      total_reports_filed: number
      total_reports_upheld: number
      total_appeals_filed: number
      total_appeals_overturned: number
      total_content_removed: number
      account_restrictions: string[]
    }
  }>('/compliance/dsa/transparency-report')
  return response.data.data
}
