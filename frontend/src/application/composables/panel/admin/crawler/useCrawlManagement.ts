/**
 * Crawler Management Store (Pinia)
 *
 * Singleton store for crawler admin state: dashboard stats, jobs, PDFs,
 * domains, and trends. Shared across all tab components.
 * Includes polling support for active crawl jobs.
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import {
  getCrawlDashboard,
  getCrawlJobs,
  getCrawlPdfs,
  getCrawlDomains,
  startCrawl,
  deleteCrawlPdf,
  createCrawlDomain,
  updateCrawlDomain,
  deleteCrawlDomain,
  getCrawlTrends,
} from '@/infrastructure/api/clients/panel/admin/crawler'
import type {
  CrawlDashboardStats,
  CrawlJob,
  CrawlPdf,
  CrawlDomain,
  CrawlTrendPoint,
  CreateDomainPayload,
  UpdateDomainPayload,
} from '@/infrastructure/api/clients/panel/admin/crawler'

export const useCrawlManagement = defineStore('crawlManagement', () => {
  // ==========================================================================
  // STATE
  // ==========================================================================

  const dashboard = ref<CrawlDashboardStats | null>(null)
  const jobs = ref<CrawlJob[]>([])
  const pdfs = ref<CrawlPdf[]>([])
  const domains = ref<CrawlDomain[]>([])
  const trends = ref<CrawlTrendPoint[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalPdfs = ref(0)
  const totalJobs = ref(0)

  // Polling
  let pollIntervalId: ReturnType<typeof setInterval> | null = null
  const isPolling = computed(() => pollIntervalId !== null)

  // ==========================================================================
  // DASHBOARD
  // ==========================================================================

  async function refreshDashboard(): Promise<void> {
    try {
      dashboard.value = await getCrawlDashboard()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load dashboard'
    }
  }

  // ==========================================================================
  // JOBS
  // ==========================================================================

  async function loadJobs(params?: {
    page?: number
    per_page?: number
    status?: string
    domain_id?: string
  }): Promise<void> {
    loading.value = true
    try {
      const result = await getCrawlJobs(params)
      jobs.value = result.items
      totalJobs.value = result.total
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load jobs'
    } finally {
      loading.value = false
    }
  }

  // ==========================================================================
  // PDFS
  // ==========================================================================

  async function loadPdfs(params?: {
    page?: number
    per_page?: number
    search?: string
    domain_id?: string
  }): Promise<void> {
    loading.value = true
    try {
      const result = await getCrawlPdfs(params)
      pdfs.value = result.items
      totalPdfs.value = result.total
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load PDFs'
    } finally {
      loading.value = false
    }
  }

  async function removePdf(urlId: string): Promise<void> {
    try {
      await deleteCrawlPdf(urlId)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to delete PDF'
    }
  }

  // ==========================================================================
  // DOMAINS
  // ==========================================================================

  async function loadDomains(): Promise<void> {
    try {
      const result = await getCrawlDomains()
      domains.value = result.items
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load domains'
    }
  }

  async function addDomain(data: CreateDomainPayload): Promise<void> {
    try {
      await createCrawlDomain(data)
      await loadDomains()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to create domain'
    }
  }

  async function editDomain(
    domainId: string,
    data: UpdateDomainPayload,
  ): Promise<void> {
    try {
      await updateCrawlDomain(domainId, data)
      await loadDomains()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to update domain'
    }
  }

  async function removeDomain(domainId: string): Promise<void> {
    try {
      await deleteCrawlDomain(domainId)
      await loadDomains()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to delete domain'
    }
  }

  // ==========================================================================
  // CRAWL CONTROL
  // ==========================================================================

  async function triggerCrawl(domainId?: string): Promise<void> {
    try {
      await startCrawl(domainId)
      startPolling()
      await refreshDashboard()
      await loadJobs()
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to start crawl'
    }
  }

  // ==========================================================================
  // POLLING — merge updates instead of replacing job list
  // ==========================================================================

  function startPolling(): void {
    if (pollIntervalId) return
    pollIntervalId = setInterval(async () => {
      try {
        const result = await getCrawlJobs({ status: 'running' })
        const runningJobs = result.items

        // Merge running job updates into existing list
        const jobMap = new Map(jobs.value.map((j) => [j.job_id, j]))
        for (const rj of runningJobs) {
          jobMap.set(rj.job_id, rj)
        }
        jobs.value = Array.from(jobMap.values()).sort(
          (a, b) => (b.created_at ?? '').localeCompare(a.created_at ?? ''),
        )

        const hasActive = runningJobs.length > 0
        if (!hasActive) {
          stopPolling()
          await refreshDashboard()
          await loadJobs()
        }
      } catch {
        // Non-critical polling failure — skip this cycle
      }
    }, 2000)
  }

  function stopPolling(): void {
    if (pollIntervalId) {
      clearInterval(pollIntervalId)
      pollIntervalId = null
    }
  }

  // ==========================================================================
  // TRENDS
  // ==========================================================================

  async function loadTrends(days?: number): Promise<void> {
    try {
      const result = await getCrawlTrends(days)
      trends.value = result.items
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to load trends'
    }
  }

  // ==========================================================================
  // PUBLIC API
  // ==========================================================================

  return {
    // State
    dashboard,
    jobs,
    pdfs,
    domains,
    trends,
    loading,
    error,
    totalPdfs,
    totalJobs,
    isPolling,
    // Actions
    refreshDashboard,
    loadJobs,
    loadPdfs,
    loadDomains,
    triggerCrawl,
    startPolling,
    stopPolling,
    loadTrends,
    addDomain,
    editDomain,
    removeDomain,
    removePdf,
  }
})
