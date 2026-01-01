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
      <h3>Kein Kurs ausgewählt</h3>
      <p>Wähle einen Kurs aus, um Analytics anzuzeigen.</p>
    </div>

    <!-- Analytics Content -->
    <template v-else>
      <!-- Header -->
      <div class="mb-6">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
          📊 Analytics: {{ course.title }}
        </h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          Statistiken und KI-Nutzung für diesen Kurs
        </p>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Lade Analytics...</p>
      </div>

      <!-- Stats Grid -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Content Stats Card -->
        <div class="stats-card">
          <div class="card-header">
            <span class="card-icon">📚</span>
            <span class="card-title">Inhalte</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ analytics.content?.chapter_count || 0 }}</span>
              <span class="stat-label">Kapitel</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.content?.lesson_count || 0 }}</span>
              <span class="stat-label">Lektionen</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.content?.method_count || 0 }}</span>
              <span class="stat-label">Lernmethoden</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.content?.unique_methods || 0 }}</span>
              <span class="stat-label">Methoden-Typen</span>
            </div>
          </div>
          <div class="card-footer">
            <span class="text-xs text-[var(--color-text-tertiary)]">
              {{ analytics.content?.published_chapters || 0 }}/{{ analytics.content?.chapter_count || 0 }} Kapitel veröffentlicht
            </span>
          </div>
        </div>

        <!-- AI Usage Card -->
        <div class="stats-card">
          <div class="card-header">
            <span class="card-icon">🤖</span>
            <span class="card-title">KI-Nutzung ({{ analytics.ai_usage?.period_days || 30 }} Tage)</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ analytics.ai_usage?.total_requests || 0 }}</span>
              <span class="stat-label">Anfragen</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ formatTokens(analytics.ai_usage?.total_tokens || 0) }}</span>
              <span class="stat-label">Tokens</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">${{ (analytics.ai_usage?.total_cost_usd || 0).toFixed(2) }}</span>
              <span class="stat-label">Kosten</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.ai_usage?.unique_users || 0 }}</span>
              <span class="stat-label">Nutzer</span>
            </div>
          </div>
          <div class="card-footer">
            <span class="text-xs text-[var(--color-text-tertiary)]">
              {{ analytics.ai_usage?.request_types || 0 }} verschiedene Anfrage-Typen
            </span>
          </div>
        </div>

        <!-- Engagement Stats Card -->
        <div class="stats-card">
          <div class="card-header">
            <span class="card-icon">👥</span>
            <span class="card-title">Engagement</span>
          </div>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ analytics.enrollments?.total_enrollments || 0 }}</span>
              <span class="stat-label">Einschreibungen</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.enrollments?.active_enrollments || 0 }}</span>
              <span class="stat-label">Aktiv</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ analytics.enrollments?.completed_enrollments || 0 }}</span>
              <span class="stat-label">Abgeschlossen</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ Math.round(analytics.enrollments?.avg_progress || 0) }}%</span>
              <span class="stat-label">Ø Fortschritt</span>
            </div>
          </div>
        </div>

        <!-- Method Distribution Card -->
        <div class="stats-card">
          <div class="card-header">
            <span class="card-icon">🧩</span>
            <span class="card-title">Lernmethoden-Verteilung</span>
          </div>
          <div class="method-list">
            <div
              v-for="method in (analytics.method_distribution || []).slice(0, 8)"
              :key="method.method_type"
              class="method-item"
            >
              <div class="method-info">
                <span class="method-badge">LM{{ String(method.method_type).padStart(2, '0') }}</span>
                <span class="method-name">{{ method.method_name }}</span>
              </div>
              <div class="method-bar-container">
                <div
                  class="method-bar"
                  :style="{ width: getMethodBarWidth(method.count) }"
                ></div>
                <span class="method-count">{{ method.count }}</span>
              </div>
            </div>
            <div v-if="!analytics.method_distribution?.length" class="text-sm text-[var(--color-text-tertiary)] text-center py-4">
              Keine Lernmethoden vorhanden
            </div>
          </div>
        </div>

        <!-- Recent Sessions Card -->
        <div class="stats-card lg:col-span-2">
          <div class="card-header">
            <span class="card-icon">📋</span>
            <span class="card-title">Letzte Authoring-Sessions</span>
          </div>
          <div class="sessions-list">
            <div
              v-for="session in analytics.recent_sessions || []"
              :key="session.session_id"
              class="session-item"
            >
              <div class="session-status" :class="session.status"></div>
              <div class="session-info">
                <span class="session-id">{{ session.session_id.slice(0, 8) }}...</span>
                <span class="session-meta">{{ session.model_profile }} • {{ formatTokens(session.tokens_used) }} Tokens</span>
              </div>
              <div class="session-time">
                {{ formatDate(session.updated_at) }}
              </div>
            </div>
            <div v-if="!analytics.recent_sessions?.length" class="text-sm text-[var(--color-text-tertiary)] text-center py-4">
              Keine Sessions vorhanden
            </div>
          </div>
        </div>

        <!-- AI Request Types Breakdown -->
        <div v-if="analytics.ai_usage?.by_type?.length" class="stats-card lg:col-span-2">
          <div class="card-header">
            <span class="card-icon">📈</span>
            <span class="card-title">KI-Anfragen nach Typ</span>
          </div>
          <div class="request-types-grid">
            <div
              v-for="typeInfo in analytics.ai_usage.by_type"
              :key="typeInfo.type"
              class="request-type-item"
            >
              <span class="type-name">{{ formatRequestType(typeInfo.type) }}</span>
              <span class="type-count">{{ typeInfo.count }} Anfragen</span>
              <span class="type-tokens">{{ formatTokens(typeInfo.tokens) }} Tokens</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Last Updated -->
      <div v-if="analytics.generated_at" class="mt-6 text-xs text-[var(--color-text-tertiary)] text-right">
        Zuletzt aktualisiert: {{ formatDate(analytics.generated_at) }}
        <button @click="loadAnalytics" class="ml-2 text-[var(--color-primary)] hover:underline">
          Aktualisieren
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import http from '@/api/http'

interface Course {
  course_id: string
  title: string
}

interface Analytics {
  content?: {
    chapter_count: number
    published_chapters: number
    lesson_count: number
    published_lessons: number
    method_count: number
    unique_methods: number
  }
  ai_usage?: {
    total_requests: number
    total_tokens: number
    total_cost_usd: number
    request_types: number
    unique_users: number
    period_days: number
    by_type: Array<{ type: string; count: number; tokens: number }>
  }
  enrollments?: {
    total_enrollments: number
    active_enrollments: number
    completed_enrollments: number
    avg_progress: number
  }
  method_distribution?: Array<{
    method_type: number
    method_name: string
    count: number
  }>
  recent_sessions?: Array<{
    session_id: string
    status: string
    model_profile: string
    tokens_used: number
    operations: number
    created_at: string
    updated_at: string
  }>
  generated_at?: string
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

const loading = ref(false)
const analytics = ref<Analytics>({})

// Methods
async function loadAnalytics() {
  if (!props.course?.course_id) return

  loading.value = true
  try {
    const response = await http.get(`/admin/course-analytics/${props.course.course_id}`)
    analytics.value = response.data.data || {}
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    loading.value = false
  }
}

function formatTokens(tokens: number): string {
  if (tokens >= 1000000) return (tokens / 1000000).toFixed(1) + 'M'
  if (tokens >= 1000) return (tokens / 1000).toFixed(1) + 'K'
  return tokens.toString()
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '-'
  }
}

function formatRequestType(type: string): string {
  const labels: Record<string, string> = {
    'module_gen': 'Modul-Generierung',
    'method_gen': 'Lernmethoden',
    'exam_gen': 'Prüfungen',
    'translation': 'Übersetzung',
    'summary': 'Zusammenfassung',
    'theory_gen': 'Theorie-Generierung',
    'tutor_steps': 'Tutor-Schritte'
  }
  return labels[type] || type
}

function getMethodBarWidth(count: number): string {
  const max = Math.max(...(analytics.value.method_distribution?.map(m => m.count) || [1]))
  return `${(count / max) * 100}%`
}

// Watch for course changes
watch(() => props.course?.course_id, (newId) => {
  if (newId) {
    loadAnalytics()
  } else {
    analytics.value = {}
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

.stats-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.card-icon {
  font-size: 1.25rem;
}

.card-title {
  font-weight: 600;
  color: var(--color-text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  padding: 1rem;
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

.card-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

/* Method Distribution */
.method-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.method-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.method-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 150px;
}

.method-badge {
  padding: 0.125rem 0.375rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 600;
  font-family: ui-monospace, monospace;
}

.method-name {
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.method-bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.method-bar {
  height: 0.5rem;
  background: var(--color-primary);
  border-radius: 0.25rem;
  min-width: 4px;
}

.method-count {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  min-width: 2rem;
  text-align: right;
}

/* Sessions List */
.sessions-list {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
}

.session-status {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  flex-shrink: 0;
}

.session-status.active { background: #22c55e; }
.session-status.finalized { background: #3b82f6; }
.session-status.archived { background: #9ca3af; }

.session-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.session-id {
  font-family: ui-monospace, monospace;
  font-size: 0.8125rem;
  color: var(--color-text-primary);
}

.session-meta {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.session-time {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

/* Request Types Grid */
.request-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
}

.request-type-item {
  display: flex;
  flex-direction: column;
  padding: 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.5rem;
}

.type-name {
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.type-count,
.type-tokens {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
</style>
