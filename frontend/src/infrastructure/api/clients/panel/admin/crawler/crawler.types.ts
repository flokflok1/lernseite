/**
 * Crawler Admin API Types
 */

export interface CrawlDomain {
  domain_id: string
  domain_name: string
  base_url: string
  display_name: string
  url_patterns: string[]
  crawl_schedule: 'daily' | 'weekly' | 'monthly'
  rate_limit_seconds: number
  max_pages_per_crawl: number
  max_depth: number
  is_active: boolean
  last_crawled_at: string | null
  total_pdfs_found: number
  config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface CrawlJob {
  job_id: string
  domain_id: string | null
  domain_name?: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  started_at: string | null
  completed_at: string | null
  pages_crawled: number
  pdfs_discovered: number
  pdfs_downloaded: number
  pdfs_new: number
  pdfs_updated: number
  errors_count: number
  error_log: Array<Record<string, unknown>>
  celery_task_id: string | null
  progress_pct: number
  created_at: string
  live_progress?: CrawlJobProgress
}

export interface CrawlJobProgress {
  status: string
  domain_name?: string
  pages_crawled?: number
  pdfs_discovered?: number
  pdfs_downloaded?: number
  progress_pct?: number
  error?: string
}

export interface CrawlPdf {
  url_id: string
  url: string
  domain_name: string
  domain_id: string
  relevance_score: number
  relevance_reason: string | null
  has_extractable_text: boolean | null
  page_count: number | null
  file_size_bytes: number | null
  status: string
  last_checked_at: string | null
  created_at: string
}

export interface CrawlDashboardStats {
  total_pdfs: number
  total_domains: number
  active_domains: number
  active_jobs: number
  cache_size_mb: number
  last_crawl_at: string | null
  domain_status: CrawlDomainStatus[]
}

export interface CrawlDomainStatus {
  domain_id: string
  display_name: string
  is_active: boolean
  last_crawled_at: string | null
  total_pdfs_found: number
  health: 'good' | 'stale' | 'error' | 'never'
}

export interface CrawlTrendPoint {
  date: string
  pdfs_found: number
  total_urls: number
}

export interface PaginatedCrawlResponse<T> {
  items: T[]
  total: number
  page?: number
  per_page?: number
}

export interface CreateDomainPayload {
  domain_name: string
  base_url: string
  display_name: string
  url_patterns?: string[]
  crawl_schedule?: 'daily' | 'weekly' | 'monthly'
  rate_limit_seconds?: number
  max_pages_per_crawl?: number
  max_depth?: number
  is_active?: boolean
}

export interface UpdateDomainPayload {
  display_name?: string
  base_url?: string
  url_patterns?: string[]
  crawl_schedule?: 'daily' | 'weekly' | 'monthly'
  rate_limit_seconds?: number
  max_pages_per_crawl?: number
  max_depth?: number
  is_active?: boolean
}
