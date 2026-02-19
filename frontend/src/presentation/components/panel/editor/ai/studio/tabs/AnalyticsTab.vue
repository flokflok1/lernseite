<!--
  AnalyticsTab.vue

  KI-Studio Pro Analytics Tab
  Zeigt Kurs-Statistiken, KI-Nutzung, Content-Metriken und Engagement.

  Features:
  - Übersicht: Kapitel, Lektionen, Lernmethoden
  - KI-Nutzung: Tokens, Requests, Kosten
  - Engagement: Einschreibungen, Fortschritt, Abschlussrate
  - Methoden-Verteilung: Chart der verwendeten Lernmethoden

  Phase: KI-Studio Pro - Analytics Tab
-->

<template>
  <div class="analytics-tab p-6">
    <!-- Kein Kurs gewählt -->
    <div v-if="!course" class="empty-state">
      <div class="icon">📊</div>
      <h3>{{ $t('aiEditorAnalytics.noCourse') }}</h3>
      <p>{{ $t('aiEditorAnalytics.selectCourse') }}</p>
    </div>

    <!-- Analytics Content -->
    <template v-else>
      <!-- Header -->
      <div class="mb-6">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
          📊 {{ $t('aiEditorAnalytics.title', { title: course.title }) }}
        </h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          {{ $t('aiEditorAnalytics.subtitle') }}
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>{{ $t('aiEditorAnalytics.loading') }}</p>
      </div>

      <!-- Stats Grid -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Content Stats Card -->
        <StatsCard icon="📚" :title="$t('aiEditorAnalytics.content')">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ analytics.content?.chapter_count || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.chapters') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.content?.lesson_count || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.lessons') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.content?.method_count || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.methods') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.content?.unique_methods || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.methodTypes') }}</span>
            </div>
          </div>
          <template #footer>
            <span class="text-xs text-[var(--color-text-tertiary)]">
              {{ $t('aiEditorAnalytics.chaptersPublished', { published: analytics.content?.published_chapters || 0, total: analytics.content?.chapter_count || 0 }) }}
            </span>
          </template>
        </StatsCard>

        <!-- AI Usage Card -->
        <StatsCard icon="🤖" :title="$t('aiEditorAnalytics.aiUsage', { days: analytics.ai_usage?.period_days || 30 })">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ analytics.ai_usage?.total_requests || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.requests') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ formatTokens(analytics.ai_usage?.total_tokens || 0) }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.tokens') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">${{ (analytics.ai_usage?.total_cost_usd || 0).toFixed(2) }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.cost') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.ai_usage?.unique_users || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.users') }}</span>
            </div>
          </div>
          <template #footer>
            <span class="text-xs text-[var(--color-text-tertiary)]">
              {{ $t('aiEditorAnalytics.requestTypes', { count: analytics.ai_usage?.request_types || 0 }) }}
            </span>
          </template>
        </StatsCard>

        <!-- Engagement Stats Card -->
        <StatsCard icon="👥" :title="$t('aiEditorAnalytics.engagement')">
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ analytics.enrollments?.total_enrollments || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.enrollments') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.enrollments?.active_enrollments || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.active') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.enrollments?.completed_enrollments || 0 }}</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.completed') }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ Math.round(analytics.enrollments?.avg_progress || 0) }}%</span>
              <span class="stat-label">{{ $t('aiEditorAnalytics.avgProgress') }}</span>
            </div>
          </div>
        </StatsCard>

        <!-- Method Distribution Card -->
        <MethodDistributionCard :methods="analytics.method_distribution || []" />

        <!-- Recent Sessions Card -->
        <RecentSessionsCard :sessions="analytics.recent_sessions || []" />

        <!-- AI Request Types Breakdown -->
        <AiRequestTypesCard :request-types="analytics.ai_usage?.by_type || []" />
      </div>

      <!-- Last Updated -->
      <div v-if="analytics.generated_at" class="mt-6 text-xs text-[var(--color-text-tertiary)] text-right">
        {{ $t('aiEditorAnalytics.lastUpdated', { date: formatDate(analytics.generated_at) }) }}
        <button @click="loadAnalytics" class="ml-2 text-[var(--color-primary)] hover:underline">
          {{ $t('aiEditorAnalytics.refresh') }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { watch, onMounted } from 'vue'
import { StatsCard } from '@/presentation/components/panel/admin/assessment/settings/exams'
import MethodDistributionCard from './analytics/MethodDistributionCard.vue'
import RecentSessionsCard from './analytics/RecentSessionsCard.vue'
import AiRequestTypesCard from './analytics/AiRequestTypesCard.vue'
import { useAnalyticsData, formatTokens, formatDate } from './composables/useAnalyticsData'

interface Course {
  course_id: string
  title: string
}

interface Stats {
  videosGenerated: number
  totalLessons: number
  tokensUsed: number
  costToday: number
}

const props = defineProps<{
  course?: Course | null
  stats?: Stats
}>()

const { loading, analytics, loadAnalytics, resetAnalytics } = useAnalyticsData(
  () => props.course?.course_id
)

watch(() => props.course?.course_id, (newId) => {
  if (newId) {
    loadAnalytics()
  } else {
    resetAnalytics()
  }
}, { immediate: true })

onMounted(() => {
  if (props.course?.course_id) {
    loadAnalytics()
  }
})
</script>

<style scoped>
.analytics-tab {
  max-width: 1400px;
  margin: 0 auto;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-state .icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--color-text-secondary);
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin-top: 0.25rem;
}
</style>
