<template>
  <div class="progress-widget">
    <h4 class="widget-title">
      <span class="widget-icon">\uD83D\uDCCA</span>
      {{ $t('dashboard.learning_progress') }}
    </h4>
    <div class="progress-stats">
      <div class="progress-stat">
        <span class="stat-value">{{ totalProgress }}%</span>
        <span class="stat-label">{{ $t('dashboard.total') }}</span>
      </div>
      <div class="progress-stat">
        <span class="stat-value">{{ completedLessons }}</span>
        <span class="stat-label">{{ $t('dashboard.lessons') }}</span>
      </div>
    </div>
    <div class="overall-progress-bar">
      <div
        class="overall-progress-fill"
        :style="{ width: `${totalProgress}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  totalProgress: number
  completedLessons: number
}

defineProps<Props>()
</script>

<style scoped>
.progress-widget {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 16px;
}

.widget-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 12px 0;
}

.widget-icon {
  font-size: 16px;
}

.progress-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.progress-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 11px;
  color: var(--color-text-muted);
}

.overall-progress-bar {
  height: 8px;
  background: var(--color-background);
  border-radius: 4px;
  overflow: hidden;
}

.overall-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}
</style>
