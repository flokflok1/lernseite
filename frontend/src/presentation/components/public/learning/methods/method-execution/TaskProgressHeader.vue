<template>
  <div class="task-progress-header">
    <div class="progress-info">
      <h3 class="progress-title">{{ $t('lesson.methodExecution.practiceTitle') }}</h3>
      <span class="progress-count">
        {{ $t('lesson.methodExecution.progressLabel', { completed, total }) }}
      </span>
    </div>
    <div class="progress-bar-track">
      <div
        class="progress-bar-fill"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  completed: number
  total: number
  percentage: number
}

defineProps<Props>()
</script>

<style scoped>
.task-progress-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.progress-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.progress-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

:root.dark .progress-title {
  color: #e2e8f0;
}

.progress-count {
  font-size: 0.6875rem;
  color: #64748b;
  font-variant-numeric: tabular-nums;
}

.progress-bar-track {
  height: 4px;
  background-color: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 0;
}
</style>
