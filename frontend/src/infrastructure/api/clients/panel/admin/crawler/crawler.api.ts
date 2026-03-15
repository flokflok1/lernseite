/**
 * Crawler Admin API Client
 *
 * Endpoints for managing IHK exam PDF crawling domains, jobs, and results.
 */

import http from '@/infrastructure/api/http'
import type {
  CrawlDashboardStats,
  CrawlJob,
  CrawlPdf,
  CrawlDomain,
  CrawlTrendPoint,
  PaginatedCrawlResponse,
  CreateDomainPayload,
  UpdateDomainPayload,
} from './crawler.types'

const BASE = '/admin/crawler'

// --- Dashboard ---

export const getCrawlDashboard = async (): Promise<CrawlDashboardStats> => {
  const response = await http.get<CrawlDashboardStats>(
    `${BASE}/status`
  )
  return response.data
}

// --- Crawl Control ---

export const startCrawl = async (
  domainId?: string
): Promise<{ job_ids: string[]; domain_count: number }> => {
  const response = await http.post<{
    success: boolean
    job_ids: string[]
    domain_count: number
  }>(`${BASE}/start`, domainId ? { domain_id: domainId } : {})
  return { job_ids: response.data.job_ids, domain_count: response.data.domain_count }
}

// --- Jobs ---

export const getCrawlJobs = async (params?: {
  page?: number
  per_page?: number
  status?: string
  domain_id?: string
}): Promise<PaginatedCrawlResponse<CrawlJob>> => {
  const response = await http.get<{
    success: boolean
    items: CrawlJob[]
    total: number
    page: number
    per_page: number
  }>(`${BASE}/jobs`, { params })
  return {
    items: response.data.items,
    total: response.data.total,
    page: response.data.page,
    per_page: response.data.per_page,
  }
}

export const getCrawlJob = async (jobId: string): Promise<CrawlJob> => {
  const response = await http.get<CrawlJob>(
    `${BASE}/jobs/${jobId}`
  )
  return response.data
}

export const cancelCrawlJob = async (jobId: string): Promise<void> => {
  await http.post(`${BASE}/jobs/${jobId}/cancel`)
}

// --- PDFs ---

export const getCrawlPdfs = async (params?: {
  page?: number
  per_page?: number
  search?: string
  domain_id?: string
}): Promise<PaginatedCrawlResponse<CrawlPdf>> => {
  const response = await http.get<{
    success: boolean
    items: CrawlPdf[]
    total: number
    page: number
    per_page: number
  }>(`${BASE}/pdfs`, { params })
  return {
    items: response.data.items,
    total: response.data.total,
    page: response.data.page,
    per_page: response.data.per_page,
  }
}

export const deleteCrawlPdf = async (urlId: string): Promise<void> => {
  await http.delete(`${BASE}/pdfs/${urlId}`)
}

// --- Domains ---

export const getCrawlDomains = async (): Promise<PaginatedCrawlResponse<CrawlDomain>> => {
  const response = await http.get<{
    items: CrawlDomain[]
  }>(`${BASE}/domains`)
  const items = response.data.items
  return { items, total: items.length }
}

export const createCrawlDomain = async (
  data: CreateDomainPayload
): Promise<{ domain_id: string }> => {
  const response = await http.post<{ success: boolean; domain_id: string }>(
    `${BASE}/domains`,
    data
  )
  return { domain_id: response.data.domain_id }
}

export const updateCrawlDomain = async (
  domainId: string,
  data: UpdateDomainPayload
): Promise<void> => {
  await http.put(`${BASE}/domains/${domainId}`, data)
}

export const deleteCrawlDomain = async (domainId: string): Promise<void> => {
  await http.delete(`${BASE}/domains/${domainId}`)
}

// --- Trends / Stats ---

export const getCrawlTrends = async (
  days?: number
): Promise<{ items: CrawlTrendPoint[]; days: number }> => {
  const response = await http.get<{
    success: boolean
    items: CrawlTrendPoint[]
    days: number
  }>(`${BASE}/stats/trends`, { params: days ? { days } : undefined })
  return { items: response.data.items, days: response.data.days }
}
