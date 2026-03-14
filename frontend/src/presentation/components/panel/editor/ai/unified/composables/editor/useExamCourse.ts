/**
 * useExamCourse — Composable for exam course generation within the AI Editor.
 *
 * Manages: cluster suggestion/apply, course preview/generate, progress polling.
 */
import { ref, computed, onUnmounted } from 'vue'
import type {
  ClusterSuggestionResult,
  ExistingCluster,
} from '@/infrastructure/api/clients/panel/admin/exams/exam-clusters.api'
import {
  suggestClusters,
  applyClusters,
  getClusters,
} from '@/infrastructure/api/clients/panel/admin/exams/exam-clusters.api'
import type {
  CoursePlan,
  GenerateResult,
  GenerationProgress,
} from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'
import {
  previewExamCourse,
  generateExamCourse,
  getGenerationProgress,
} from '@/infrastructure/api/clients/panel/admin/exams/course-generator.api'

export function useExamCourse() {
  // ── Cluster State ─────────────────────────────────────────────
  const existingClusters = ref<ExistingCluster[]>([])
  const suggestion = ref<ClusterSuggestionResult | null>(null)
  const loadingClusters = ref(false)
  const suggestingClusters = ref(false)
  const applyingClusters = ref(false)
  const clusterError = ref<string | null>(null)

  // ── Course Generation State ───────────────────────────────────
  const plan = ref<CoursePlan | null>(null)
  const result = ref<GenerateResult | null>(null)
  const progress = ref<GenerationProgress | null>(null)
  const previewing = ref(false)
  const generating = ref(false)
  const courseError = ref<string | null>(null)

  let progressInterval: ReturnType<typeof setInterval> | null = null

  // ── Cluster Actions ───────────────────────────────────────────

  async function loadClusters(examTypeKey: string) {
    loadingClusters.value = true
    clusterError.value = null
    try {
      existingClusters.value = await getClusters(examTypeKey)
    } catch (e: any) {
      clusterError.value = e?.message || 'Failed to load clusters'
    } finally {
      loadingClusters.value = false
    }
  }

  async function requestSuggestion(
    examTypeKey: string,
    region: string = 'alle',
    options?: { provider?: string; model?: string },
  ) {
    suggestingClusters.value = true
    clusterError.value = null
    suggestion.value = null
    try {
      suggestion.value = await suggestClusters(examTypeKey, region, options)
    } catch (e: any) {
      clusterError.value = e?.message || 'Cluster suggestion failed'
    } finally {
      suggestingClusters.value = false
    }
  }

  async function applyClusterSuggestion(examTypeKey: string) {
    if (!suggestion.value?.clusters?.length) return
    applyingClusters.value = true
    clusterError.value = null
    try {
      await applyClusters(examTypeKey, suggestion.value.clusters)
      await loadClusters(examTypeKey)
      suggestion.value = null
    } catch (e: any) {
      clusterError.value = e?.message || 'Failed to apply clusters'
    } finally {
      applyingClusters.value = false
    }
  }

  // ── Course Generation Actions ─────────────────────────────────

  async function previewCourse(
    examType: string,
    region: string = 'alle',
    frameworkId?: number,
    sortMode?: string,
  ) {
    previewing.value = true
    courseError.value = null
    result.value = null
    progress.value = null
    try {
      plan.value = await previewExamCourse(examType, region, frameworkId, sortMode)
    } catch (e: any) {
      courseError.value = e?.response?.data?.error || e?.message || 'Preview failed'
    } finally {
      previewing.value = false
    }
  }

  async function generateCourse(
    examType: string,
    region: string = 'alle',
    options?: { provider?: string; model?: string },
    frameworkId?: number,
    sortMode?: string,
  ) {
    generating.value = true
    courseError.value = null
    progress.value = null
    try {
      result.value = await generateExamCourse(examType, region, options, frameworkId, sortMode)
      if (result.value.status === 'generating' && result.value.course_id) {
        startPolling(result.value.course_id)
      } else {
        generating.value = false
      }
    } catch (e: any) {
      courseError.value = e?.response?.data?.error || e?.message || 'Generation failed'
      generating.value = false
    }
  }

  // ── Progress Polling ──────────────────────────────────────────

  function startPolling(courseId: string) {
    stopPolling()
    progressInterval = setInterval(() => pollProgress(courseId), 3000)
    pollProgress(courseId)
  }

  function stopPolling() {
    if (progressInterval) {
      clearInterval(progressInterval)
      progressInterval = null
    }
  }

  async function pollProgress(courseId: string) {
    try {
      progress.value = await getGenerationProgress(courseId)
      const done = new Set(['ready', 'partial', 'failed'])
      if (done.has(progress.value.status)) {
        stopPolling()
        generating.value = false
      }
    } catch {
      /* polling errors are non-critical */
    }
  }

  onUnmounted(stopPolling)

  // ── Computed ──────────────────────────────────────────────────

  const hasClusters = computed(() => existingClusters.value.length > 0)
  const hasSuggestion = computed(() => !!suggestion.value?.clusters?.length)

  const progressPercent = computed(() => {
    if (!progress.value) return 0
    return Math.round((progress.value.completed / Math.max(progress.value.total, 1)) * 100)
  })

  return {
    // Cluster state
    existingClusters,
    suggestion,
    loadingClusters,
    suggestingClusters,
    applyingClusters,
    clusterError,
    hasClusters,
    hasSuggestion,
    // Cluster actions
    loadClusters,
    requestSuggestion,
    applyClusterSuggestion,
    // Course state
    plan,
    result,
    progress,
    previewing,
    generating,
    courseError,
    progressPercent,
    // Course actions
    previewCourse,
    generateCourse,
  }
}
