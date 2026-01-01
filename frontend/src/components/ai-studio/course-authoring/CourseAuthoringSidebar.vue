<!--
  CourseAuthoringSidebar.vue

  Sidebar für den KI-Kurs-Builder Tab.
  Zeigt aktive Session-Infos und Aktivitäts-Verlauf.
  Ersetzt die Kapitel-Liste wenn der Builder-Tab aktiv ist.

  Phase D4 - KI-Kurs-Builder
-->

<template>
  <div class="course-authoring-sidebar">
    <!-- Sektion 1: Aktive Session -->
    <div class="sidebar-section session-info">
      <div class="section-header">
        <span class="section-icon">⭐</span>
        <span class="section-title">Aktive Session</span>
      </div>

      <!-- Keine Session -->
      <div v-if="!sessionMeta" class="empty-session">
        <p>Keine aktive Session</p>
        <p class="hint">Klicke auf "Neue Session" um zu starten.</p>
      </div>

      <!-- Session Details -->
      <div v-else class="session-details">
        <div class="detail-row">
          <span class="detail-label">Kurs</span>
          <span class="detail-value">{{ sessionMeta.courseTitle || 'Unbekannt' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Session-ID</span>
          <span class="detail-value mono">{{ shortSessionId }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Status</span>
          <span class="detail-value">
            <span class="status-badge" :class="sessionMeta.status">
              {{ statusLabel }}
            </span>
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Modell</span>
          <span class="detail-value mono">{{ shortModelProfile }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Letzte Änderung</span>
          <span class="detail-value">{{ formattedLastUpdate }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Tokens</span>
          <span class="detail-value">{{ formatTokens(sessionMeta.totalTokensUsed || 0) }}</span>
        </div>
      </div>

      <!-- Finalized Warning -->
      <div v-if="sessionMeta?.status === 'finalized'" class="finalized-notice">
        <span class="notice-icon">ℹ️</span>
        <span>Diese Session ist schreibgeschützt. Erstelle eine neue Session, um weiterzuarbeiten.</span>
      </div>
    </div>

    <!-- Sektion 2: Verlauf -->
    <div class="sidebar-section activity-log">
      <div class="section-header">
        <span class="section-icon">📋</span>
        <span class="section-title">Letzte Aktionen</span>
        <span v-if="activityLog.length" class="activity-count">{{ activityLog.length }}</span>
      </div>

      <!-- Keine Aktionen -->
      <div v-if="!activityLog.length" class="empty-activity">
        <p>Noch keine Aktionen</p>
        <p class="hint">Starte mit einer Quick-Action oder schreibe eine Nachricht.</p>
      </div>

      <!-- Aktivitäts-Liste -->
      <div v-else class="activity-list">
        <div
          v-for="(activity, index) in displayedActivities"
          :key="index"
          class="activity-item"
        >
          <span class="activity-icon">{{ getActivityIcon(activity) }}</span>
          <div class="activity-content">
            <span class="activity-summary">{{ activity.summary }}</span>
            <span class="activity-time">{{ formatActivityTime(activity.timestamp) }}</span>
          </div>
        </div>
      </div>

      <!-- Mehr anzeigen -->
      <button
        v-if="activityLog.length > maxDisplayed"
        @click="showAll = !showAll"
        class="show-more-btn"
      >
        {{ showAll ? 'Weniger anzeigen' : `+${activityLog.length - maxDisplayed} weitere` }}
      </button>
    </div>

    <!-- Quick Stats -->
    <div v-if="sessionMeta" class="sidebar-section quick-stats">
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-value">{{ stats.chapters }}</span>
          <span class="stat-label">Kapitel</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.lessons }}</span>
          <span class="stat-label">Lektionen</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ stats.methods }}</span>
          <span class="stat-label">Methoden</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface SessionMeta {
  sessionId: string
  courseId: string
  courseTitle?: string
  status: 'active' | 'finalized' | 'archived'
  modelProfile: string
  totalTokensUsed: number
  totalOperations: number
  updatedAt?: string
  createdAt?: string
}

interface ActivityLogItem {
  timestamp: string
  summary: string
  operations?: string[]
  type?: string
}

interface DraftStats {
  chapters: number
  lessons: number
  methods: number
}

const props = withDefaults(defineProps<{
  sessionMeta?: SessionMeta | null
  activityLog?: ActivityLogItem[]
  stats?: DraftStats
}>(), {
  sessionMeta: null,
  activityLog: () => [],
  stats: undefined
})

const showAll = ref(false)
const maxDisplayed = 10

// Computed
const shortSessionId = computed(() => {
  if (!props.sessionMeta?.sessionId) return '-'
  return props.sessionMeta.sessionId.slice(0, 8) + '...'
})

const shortModelProfile = computed(() => {
  if (!props.sessionMeta?.modelProfile) return '-'
  const profile = props.sessionMeta.modelProfile
  // Kürze lange Profile-Namen
  if (profile.length > 20) {
    return profile.replace('anthropic-', '').replace('openai-', '')
  }
  return profile
})

const statusLabel = computed(() => {
  const labels: Record<string, string> = {
    'active': 'Aktiv',
    'finalized': 'Finalisiert',
    'archived': 'Archiviert'
  }
  return labels[props.sessionMeta?.status || ''] || props.sessionMeta?.status
})

const formattedLastUpdate = computed(() => {
  if (!props.sessionMeta?.updatedAt) return '-'
  try {
    const date = new Date(props.sessionMeta.updatedAt)
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '-'
  }
})

const displayedActivities = computed(() => {
  if (showAll.value) return props.activityLog
  return props.activityLog.slice(0, maxDisplayed)
})

const stats = computed(() => {
  return props.stats || { chapters: 0, lessons: 0, methods: 0 }
})

// Functions
function formatTokens(tokens: number): string {
  if (tokens >= 1000000) return (tokens / 1000000).toFixed(1) + 'M'
  if (tokens >= 1000) return (tokens / 1000).toFixed(1) + 'K'
  return tokens.toString()
}

function getActivityIcon(activity: ActivityLogItem): string {
  const summary = activity.summary.toLowerCase()
  if (summary.includes('kapitel') && summary.includes('erstellt')) return '📖'
  if (summary.includes('kapitel') && summary.includes('aktualisiert')) return '✏️'
  if (summary.includes('lektion') && summary.includes('erstellt')) return '📄'
  if (summary.includes('lektion') && summary.includes('aktualisiert')) return '✏️'
  if (summary.includes('taschenrechner')) return '🧮'
  if (summary.includes('prüfung') || summary.includes('exam')) return '🎓'
  if (summary.includes('quiz')) return '❓'
  if (summary.includes('flashcard') || summary.includes('karteikarte')) return '🗂️'
  if (summary.includes('struktur')) return '📋'
  if (summary.includes('methode')) return '🎯'
  if (summary.includes('gelöscht') || summary.includes('entfernt')) return '🗑️'
  return '✅'
}

function formatActivityTime(timestamp: string): string {
  if (!timestamp) return ''
  try {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)

    if (minutes < 1) return 'gerade eben'
    if (minutes < 60) return `vor ${minutes} Min.`
    if (hours < 24) return `vor ${hours} Std.`
    return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })
  } catch {
    return ''
  }
}
</script>

<style scoped>
.course-authoring-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface-secondary);
  overflow-y: auto;
}

.sidebar-section {
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.section-icon {
  font-size: 1rem;
}

.section-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.activity-count {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

/* Session Info */
.empty-session,
.empty-activity {
  padding: 1rem;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
}

.empty-session .hint,
.empty-activity .hint {
  font-size: 0.75rem;
  opacity: 0.7;
  margin-top: 0.25rem;
}

.session-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
}

.detail-label {
  color: var(--color-text-secondary);
}

.detail-value {
  color: var(--color-text-primary);
  font-weight: 500;
  text-align: right;
  max-width: 60%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-value.mono {
  font-family: ui-monospace, monospace;
  font-size: 0.6875rem;
}

.status-badge {
  display: inline-flex;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

.status-badge.active {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.status-badge.finalized {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.status-badge.archived {
  background: rgba(156, 163, 175, 0.1);
  color: #9ca3af;
}

.finalized-notice {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 0.625rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 0.375rem;
  font-size: 0.6875rem;
  color: #3b82f6;
  line-height: 1.4;
}

.notice-icon {
  flex-shrink: 0;
}

/* Activity Log */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--color-surface);
  border-radius: 0.375rem;
  transition: background 0.15s;
}

.activity-item:hover {
  background: var(--color-surface-hover, var(--color-surface));
}

.activity-icon {
  font-size: 0.875rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-summary {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.activity-time {
  display: block;
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
  margin-top: 0.125rem;
}

.show-more-btn {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.375rem;
  background: transparent;
  border: 1px dashed var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.show-more-btn:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* Quick Stats */
.quick-stats {
  margin-top: auto;
  background: var(--color-surface);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  background: var(--color-surface-secondary);
  border-radius: 0.375rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 0.625rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>
