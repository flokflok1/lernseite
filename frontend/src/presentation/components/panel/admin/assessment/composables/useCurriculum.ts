/**
 * Composable for curriculum framework management.
 *
 * Provides state management and API operations for:
 * - Framework CRUD and tree loading
 * - AI PDF import (parse preview + confirm)
 * - Auto-mapping questions to objectives
 * - Coverage statistics
 */

import { ref, computed } from 'vue'
import {
  fetchFrameworks,
  fetchFrameworkTree,
  createFramework,
  deleteFramework,
  importPdfPreview,
  importPdfFileStreaming,
  importPdfConfirm,
  autoMapQuestions,
  fetchCoverageStats,
  fetchRelevanceWeights,
  linkFrameworkToExamType,
  type CurriculumFramework,
  type CurriculumTree,
  type CoverageStats,
  type AutoMapStats,
  type RelevanceEntry,
  type ImportProgressEvent,
} from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'

export function useCurriculum() {
  const frameworks = ref<CurriculumFramework[]>([])
  const activeTree = ref<CurriculumTree | null>(null)
  const coverage = ref<CoverageStats | null>(null)
  const relevance = ref<RelevanceEntry[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const importPreview = ref<Record<string, any> | null>(null)
  const importProgress = ref<ImportProgressEvent | null>(null)

  const hasFrameworks = computed(() => frameworks.value.length > 0)

  // Stale-response guard: each read increments the counter.
  // After await, if counter moved, a newer read superseded us — skip write.
  let _readSeq = 0

  async function loadFrameworks() {
    loading.value = true
    error.value = null
    try {
      frameworks.value = await fetchFrameworks()
    } catch (e: any) {
      // 404 means no frameworks exist yet — treat as empty, not error
      const status = e?.response?.status ?? e?.status
      if (status === 404) {
        frameworks.value = []
      } else {
        error.value = e?.response?.data?.error || e?.message || 'Failed to load frameworks'
      }
    } finally {
      loading.value = false
    }
  }

  async function loadTree(frameworkId: number) {
    const seq = ++_readSeq
    loading.value = true
    error.value = null
    try {
      const result = await fetchFrameworkTree(frameworkId)
      if (seq !== _readSeq) return
      activeTree.value = result
    } catch (e: any) {
      if (seq !== _readSeq) return
      error.value = e?.response?.data?.error || 'Failed to load framework tree'
    } finally {
      if (seq === _readSeq) loading.value = false
    }
  }

  async function addFramework(payload: Partial<CurriculumFramework>) {
    loading.value = true
    error.value = null
    try {
      const created = await createFramework(payload)
      frameworks.value.unshift(created)
      return created
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'Failed to create framework'
      return null
    } finally {
      loading.value = false
    }
  }

  async function removeFramework(frameworkId: number) {
    loading.value = true
    error.value = null
    try {
      await deleteFramework(frameworkId)
      frameworks.value = frameworks.value.filter(
        (f) => f.framework_id !== frameworkId
      )
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'Failed to delete framework'
    } finally {
      loading.value = false
    }
  }

  async function parsePdf(pdfText: string, provider?: string, model?: string) {
    loading.value = true
    error.value = null
    try {
      importPreview.value = await importPdfPreview(pdfText, provider, model)
      return importPreview.value
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'AI PDF parse failed'
      return null
    } finally {
      loading.value = false
    }
  }

  async function parsePdfFile(file: File, provider?: string, model?: string) {
    loading.value = true
    error.value = null
    importProgress.value = null
    try {
      const preview = await importPdfFileStreaming(
        file, provider, model,
        (evt) => { importProgress.value = { ...evt } },
      )
      importPreview.value = preview
      return preview
    } catch (e: any) {
      error.value = e?.message || 'AI PDF parse failed'
      return null
    } finally {
      loading.value = false
    }
  }

  async function confirmImport(sourceDocument?: string) {
    if (!importPreview.value) {
      error.value = 'No preview to confirm'
      return null
    }
    loading.value = true
    error.value = null
    try {
      const framework = await importPdfConfirm(
        importPreview.value,
        sourceDocument
      )
      frameworks.value.unshift(framework)
      importPreview.value = null
      return framework
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'Import failed'
      return null
    } finally {
      loading.value = false
    }
  }

  async function runAutoMap(examTypeKey: string): Promise<AutoMapStats | null> {
    loading.value = true
    error.value = null
    try {
      return await autoMapQuestions(examTypeKey)
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'Auto-mapping failed'
      return null
    } finally {
      loading.value = false
    }
  }

  async function loadCoverage(frameworkId: number) {
    const seq = ++_readSeq
    loading.value = true
    error.value = null
    try {
      const result = await fetchCoverageStats(frameworkId)
      if (seq !== _readSeq) return
      coverage.value = result
    } catch (e: any) {
      if (seq !== _readSeq) return
      error.value = e?.response?.data?.error || 'Failed to load coverage'
    } finally {
      if (seq === _readSeq) loading.value = false
    }
  }

  async function loadRelevance(frameworkId: number) {
    const seq = ++_readSeq
    loading.value = true
    error.value = null
    try {
      const result = await fetchRelevanceWeights(frameworkId)
      if (seq !== _readSeq) return
      relevance.value = result
    } catch (e: any) {
      if (seq !== _readSeq) return
      error.value = e?.response?.data?.error || 'Failed to load relevance'
    } finally {
      if (seq === _readSeq) loading.value = false
    }
  }

  async function loadStructureData(frameworkId: number) {
    const seq = ++_readSeq
    loading.value = true
    error.value = null
    try {
      const [treeResult, coverageResult] = await Promise.allSettled([
        fetchFrameworkTree(frameworkId),
        fetchCoverageStats(frameworkId),
      ])
      if (seq !== _readSeq) return
      if (treeResult.status === 'fulfilled') {
        activeTree.value = treeResult.value
      }
      if (coverageResult.status === 'fulfilled') {
        coverage.value = coverageResult.value
      }
      const failed = [treeResult, coverageResult].filter(
        (r) => r.status === 'rejected',
      )
      if (failed.length) {
        error.value = 'Failed to load framework data'
      }
    } finally {
      if (seq === _readSeq) loading.value = false
    }
  }

  async function loadMappingData(frameworkId: number) {
    const seq = ++_readSeq
    loading.value = true
    error.value = null
    try {
      const [coverageResult, relevanceResult] = await Promise.allSettled([
        fetchCoverageStats(frameworkId),
        fetchRelevanceWeights(frameworkId),
      ])
      if (seq !== _readSeq) return
      if (coverageResult.status === 'fulfilled') {
        coverage.value = coverageResult.value
      }
      if (relevanceResult.status === 'fulfilled') {
        relevance.value = relevanceResult.value
      }
      const failed = [coverageResult, relevanceResult].filter(
        (r) => r.status === 'rejected',
      )
      if (failed.length) {
        error.value = 'Failed to load mapping data'
      }
    } finally {
      if (seq === _readSeq) loading.value = false
    }
  }

  async function linkToExamType(frameworkId: number, examTypeKey: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      await linkFrameworkToExamType(frameworkId, examTypeKey)
      return true
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'Failed to link framework'
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    frameworks,
    activeTree,
    coverage,
    relevance,
    loading,
    error,
    importPreview,
    importProgress,
    hasFrameworks,
    loadFrameworks,
    loadTree,
    addFramework,
    removeFramework,
    parsePdf,
    parsePdfFile,
    confirmImport,
    runAutoMap,
    loadCoverage,
    loadRelevance,
    loadStructureData,
    loadMappingData,
    linkToExamType,
  }
}
