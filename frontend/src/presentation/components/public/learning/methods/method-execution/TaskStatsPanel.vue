<template>
  <div class="stats-section">
    <!-- Inline stats row -->
    <div class="stats-row">
      <div class="stat-item stat-generated">
        <span class="stat-value">{{ countGenerated }}</span>
        <span class="stat-label">{{ $t('lesson.methodExecution.stats.generated') }}</span>
      </div>
      <div class="stat-divider"></div>
      <div class="stat-item stat-solved">
        <span class="stat-value">{{ countSolved }}</span>
        <span class="stat-label">{{ $t('lesson.methodExecution.stats.solved') }}</span>
      </div>
    </div>

    <!-- Actions -->
    <div v-if="countGenerated > 0" class="stats-actions">
      <button @click="$emit('show-all')" class="action-btn action-primary">
        <span>{{ $t('lesson.methodExecution.stats.viewAll') }}</span>
        <span class="badge">{{ countGenerated }}</span>
      </button>

      <button @click="$emit('delete-all')" class="action-btn action-danger">
        {{ $t('lesson.methodExecution.stats.deleteAll') }}
      </button>
    </div>

    <!-- Calculator Button (Optional) -->
    <button
      v-if="showCalculator"
      @click="$emit('open-calculator')"
      class="calc-btn"
      :title="$t('lesson.methodExecution.calculator.tooltip')"
    >
      <span class="calc-icon">
        <svg class="calc-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="4" y="2" width="16" height="20" rx="2" />
          <line x1="8" y1="6" x2="16" y2="6" />
          <line x1="8" y1="14" x2="16" y2="14" />
          <line x1="12" y1="10" x2="12" y2="18" />
        </svg>
      </span>
      <div class="calc-text">
        <strong>{{ $t('lesson.methodExecution.calculator.title') }}</strong>
        <small>{{ $t('lesson.methodExecution.calculator.subtitle') }}</small>
      </div>
      <span class="calc-badge">{{ $t('lesson.methodExecution.calculator.badge') }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  countGenerated: number
  countSolved: number
  showCalculator?: boolean
}

withDefaults(defineProps<Props>(), {
  showCalculator: false
})

defineEmits<{
  'show-all': []
  'delete-all': []
  'open-calculator': []
}>()
</script>

<style scoped>
.stats-section {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.stats-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.stat-value {
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1;
}

.stat-generated .stat-value { color: #3b82f6; }
.stat-solved .stat-value { color: #10b981; }

.stat-label {
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  text-transform: uppercase;
}

.stat-divider {
  width: 1px;
  height: 1.25rem;
  background-color: var(--color-border, #e5e7eb);
}

/* Actions */
.stats-actions {
  display: flex;
  gap: 0.375rem;
}

.action-btn {
  flex: 1;
  padding: 0.375rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 0.375rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
}

.action-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.action-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.action-danger {
  background-color: rgba(239, 68, 68, 0.08);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.action-danger:hover {
  background-color: #ef4444;
  color: white;
}

.badge {
  padding: 0.0625rem 0.375rem;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
}

/* Calculator Button */
.calc-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  margin-top: 0.5rem;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.08) 100%);
  border: 1px dashed rgba(16, 185, 129, 0.3);
  border-radius: 0.5rem;
  color: #059669;
  font-weight: 600;
  transition: all 0.2s;
}

.calc-btn:hover {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
  transform: translateY(-1px);
}

.calc-svg {
  width: 1.25rem;
  height: 1.25rem;
}

.calc-text {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.calc-text strong {
  font-size: 0.75rem;
  color: #059669;
}

.calc-text small {
  font-size: 0.625rem;
  color: var(--color-text-secondary, #6b7280);
}

.calc-badge {
  font-size: 0.5625rem;
  font-weight: 600;
  padding: 0.125rem 0.375rem;
  background-color: #10b981;
  color: white;
  border-radius: 9999px;
  text-transform: uppercase;
}
</style>
