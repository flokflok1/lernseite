<!--
  ExamClusterSuggestion — AI-powered cluster suggestion with multi-perspective review.
  Shows existing clusters, lets admin request AI suggestions, review and apply them.
-->
<template>
  <div class="space-y-4">
    <!-- Section Header -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ t('aiEditor.exam.clusterSection') }}
        </h3>
        <p class="text-xs text-[var(--color-text-secondary)] mt-0.5">
          {{ t('aiEditor.exam.clusterDescription') }}
        </p>
      </div>
      <button
        @click="$emit('suggest')"
        :disabled="suggesting"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white rounded-md transition-colors disabled:opacity-50"
        style="background-color: var(--color-primary, #7c3aed);"
      >
        <span v-if="suggesting" class="animate-spin">⟳</span>
        <span v-else>✦</span>
        {{ suggesting ? t('aiEditor.exam.suggesting') : t('aiEditor.exam.suggestClusters') }}
      </button>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      class="rounded-md px-3 py-2 text-xs border"
      style="background: var(--color-error-bg, #fee2e2); border-color: var(--color-error-text, #dc2626); color: var(--color-error-text, #dc2626);"
    >
      {{ error }}
    </div>

    <!-- Existing Clusters -->
    <div v-if="clusters.length > 0">
      <h4 class="text-xs font-medium text-[var(--color-text-secondary)] mb-2">
        {{ t('aiEditor.exam.currentClusters') }} ({{ clusters.length }})
      </h4>
      <div class="grid grid-cols-2 gap-2">
        <div
          v-for="cluster in clusters"
          :key="cluster.cluster_key"
          class="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2"
        >
          <p class="text-xs font-medium text-[var(--color-text-primary)]">
            {{ cluster.label?.de || cluster.cluster_key }}
          </p>
          <p class="text-[10px] text-[var(--color-text-tertiary)] mt-0.5">
            {{ t('aiEditor.exam.topics', { count: cluster.topics?.length || 0 }) }}
          </p>
        </div>
      </div>
    </div>

    <!-- No Clusters State -->
    <div
      v-else-if="!suggestion && !suggesting"
      class="text-center py-6 text-xs text-[var(--color-text-secondary)]"
    >
      {{ t('aiEditor.exam.noClusters') }}
    </div>

    <!-- AI Suggestion -->
    <div v-if="suggestion" class="space-y-3">
      <div class="flex items-center justify-between">
        <h4 class="text-xs font-medium text-[var(--color-text-primary)]">
          {{ t('aiEditor.exam.suggestedClusters') }} ({{ suggestion.clusters.length }})
        </h4>
        <button
          @click="$emit('apply')"
          :disabled="applying"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white rounded-md transition-colors disabled:opacity-50"
          style="background-color: var(--color-success-text, #16a34a);"
        >
          {{ applying ? t('aiEditor.exam.applying') : t('aiEditor.exam.applyClusters') }}
        </button>
      </div>

      <!-- Suggested Cluster Cards -->
      <div class="space-y-2">
        <div
          v-for="cluster in suggestion.clusters"
          :key="cluster.cluster_key"
          class="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2.5"
        >
          <div class="flex items-center justify-between">
            <p class="text-xs font-semibold text-[var(--color-text-primary)]">
              {{ cluster.label?.de || cluster.cluster_key }}
            </p>
            <div class="flex items-center gap-2 text-[10px] text-[var(--color-text-tertiary)]">
              <span>{{ t('aiEditor.exam.questions', { count: cluster.question_count }) }}</span>
              <span>{{ t('aiEditor.exam.points', { pct: cluster.point_share_pct?.toFixed(1) }) }}</span>
            </div>
          </div>
          <p class="text-[10px] text-[var(--color-text-secondary)] mt-1">
            {{ cluster.reasoning }}
          </p>
          <div class="flex flex-wrap gap-1 mt-1.5">
            <span
              v-for="topic in cluster.topics.slice(0, 5)"
              :key="topic"
              class="inline-block px-1.5 py-0.5 text-[9px] rounded bg-[var(--color-surface-secondary)] text-[var(--color-text-tertiary)]"
            >
              {{ topic }}
            </span>
            <span
              v-if="cluster.topics.length > 5"
              class="inline-block px-1.5 py-0.5 text-[9px] rounded bg-[var(--color-surface-secondary)] text-[var(--color-text-tertiary)]"
            >
              +{{ cluster.topics.length - 5 }}
            </span>
          </div>
        </div>
      </div>

      <!-- Multi-Perspective Reviews -->
      <div v-if="suggestion.reviews" class="rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] p-3 space-y-2">
        <h4 class="text-xs font-medium text-[var(--color-text-primary)]">
          {{ t('aiEditor.exam.reviews') }}
        </h4>
        <div v-for="(text, key) in reviewEntries" :key="key" class="text-[10px]">
          <span class="font-medium text-[var(--color-text-primary)]">{{ key }}:</span>
          <span class="text-[var(--color-text-secondary)] ml-1">{{ text }}</span>
        </div>
      </div>

      <!-- Warnings -->
      <div v-if="suggestion.warnings?.length" class="space-y-1">
        <h4 class="text-xs font-medium text-[var(--color-text-primary)]">
          {{ t('aiEditor.exam.warnings') }}
        </h4>
        <div
          v-for="(warning, idx) in suggestion.warnings"
          :key="idx"
          class="text-[10px] text-amber-600 bg-amber-50 rounded px-2 py-1 border border-amber-200"
        >
          {{ warning }}
        </div>
      </div>

      <!-- Overall Assessment -->
      <div v-if="suggestion.overall_assessment" class="text-xs text-[var(--color-text-secondary)] italic">
        {{ suggestion.overall_assessment }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  ClusterSuggestionResult,
  ExistingCluster,
} from '@/infrastructure/api/clients/panel/admin/exams/exam-clusters.api'

const { t } = useI18n()

const props = defineProps<{
  clusters: ExistingCluster[]
  suggestion: ClusterSuggestionResult | null
  suggesting: boolean
  applying: boolean
  error: string | null
}>()

defineEmits<{
  suggest: []
  apply: []
}>()

const reviewEntries = computed(() => {
  if (!props.suggestion?.reviews) return {}
  const r = props.suggestion.reviews
  return {
    [t('aiEditor.exam.studentPerspective')]: r.student_perspective,
    [t('aiEditor.exam.instructorPerspective')]: r.instructor_perspective,
    [t('aiEditor.exam.examinerPerspective')]: r.examiner_perspective,
  }
})
</script>
