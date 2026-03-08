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
  importPdfConfirm,
  autoMapQuestions,
  fetchCoverageStats,
  linkFrameworkToExamType,
  type CurriculumFramework,
  type CurriculumTree,
  type CoverageStats,
  type AutoMapStats,
} from '@/infrastructure/api/clients/panel/admin/exams/curriculum.api'

export function useCurriculum() {
  const frameworks = ref<CurriculumFramework[]>([])
  const activeTree = ref<CurriculumTree | null>(null)
  const coverage = ref<CoverageStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const importPreview = ref<Record<string, any> | null>(null)

  const hasFrameworks = computed(() => frameworks.value.length > 0)

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
    loading.value = true
    error.value = null
    try {
      activeTree.value = await fetchFrameworkTree(frameworkId)
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'Failed to load framework tree'
    } finally {
      loading.value = false
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

  async function parsePdf(pdfText: string) {
    loading.value = true
    error.value = null
    try {
      importPreview.value = await importPdfPreview(pdfText)
      return importPreview.value
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'AI PDF parse failed'
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
    loading.value = true
    error.value = null
    try {
      coverage.value = await fetchCoverageStats(frameworkId)
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'Failed to load coverage'
    } finally {
      loading.value = false
    }
  }

  async function linkToExamType(frameworkId: number, examTypeKey: string) {
    loading.value = true
    error.value = null
    try {
      await linkFrameworkToExamType(frameworkId, examTypeKey)
    } catch (e: any) {
      error.value = e?.response?.data?.error || 'Failed to link framework'
    } finally {
      loading.value = false
    }
  }

  return {
    frameworks,
    activeTree,
    coverage,
    loading,
    error,
    importPreview,
    hasFrameworks,
    loadFrameworks,
    loadTree,
    addFramework,
    removeFramework,
    parsePdf,
    confirmImport,
    runAutoMap,
    loadCoverage,
    linkToExamType,
  }
}
