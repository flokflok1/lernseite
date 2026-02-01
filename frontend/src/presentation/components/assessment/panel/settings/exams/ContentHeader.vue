<!--
  ContentHeader - Header with lesson info and stats
  Sub-component of ContentTab
-->

<template>
  <div class="content-header">
    <div class="header-icon">📝</div>
    <div class="header-info">
      <h2>{{ $t('windows.aiStudioContent.lessonEditor') }}</h2>
      <p>{{ lessonTitle }} • {{ chapterTitle }}</p>
    </div>
    <div class="header-stats">
      <div class="stat">
        <span class="stat-value">{{ wordCount }}</span>
        <span class="stat-label">{{ $t('windows.aiStudioContent.words') }}</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ stepsCount }}</span>
        <span class="stat-label">{{ $t('windows.aiStudioContent.steps') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  lessonTitle: string
  chapterTitle: string
  wordCount: number
  stepsCount: number
}>()
</script>

<style scoped>
.content-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  margin-bottom: 1rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #06b6d4);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.header-info { flex: 1; }

.header-info h2 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.header-info p {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin: 0.25rem 0 0;
}

.header-stats {
  display: flex;
  gap: 1.5rem;
}

.stat { text-align: center; }

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>
