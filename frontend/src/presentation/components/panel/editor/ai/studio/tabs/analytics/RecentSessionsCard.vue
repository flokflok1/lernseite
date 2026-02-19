<!--
  RecentSessionsCard.vue

  Displays a list of recent AI authoring sessions with status indicators.
  Used as a sub-component of AnalyticsTab.

  Phase: KI-Studio Pro - Analytics Tab
-->

<template>
  <div class="stats-card lg:col-span-2">
    <div class="card-header">
      <span class="card-icon">📋</span>
      <span class="card-title">{{ $t('aiEditorAnalytics.recentSessions') }}</span>
    </div>
    <div class="sessions-list">
      <div
        v-for="session in sessions"
        :key="session.session_id"
        class="session-item"
      >
        <div class="session-status" :class="session.status"></div>
        <div class="session-info">
          <span class="session-id">{{ session.session_id.slice(0, 8) }}...</span>
          <span class="session-meta">{{ session.model_profile }} &bull; {{ formatTokens(session.tokens_used) }} {{ $t('aiEditorAnalytics.tokens') }}</span>
        </div>
        <div class="session-time">
          {{ formatDate(session.updated_at) }}
        </div>
      </div>
      <div v-if="!sessions.length" class="text-sm text-[var(--color-text-tertiary)] text-center py-4">
        {{ $t('aiEditorAnalytics.noSessions') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatTokens, formatDate } from '../composables/useAnalyticsData'
import type { RecentSession } from '../composables/useAnalyticsData'

defineProps<{
  sessions: RecentSession[]
}>()
</script>

<style scoped>
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
</style>
