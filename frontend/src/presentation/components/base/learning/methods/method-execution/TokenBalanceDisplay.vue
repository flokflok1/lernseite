<template>
  <div class="token-balance-section">
    <div class="token-header">
      <div class="token-icon">💎</div>
      <div class="token-info">
        <span class="token-label">{{ $t('lesson.methodExecution.tokenBalance') }}</span>
        <span class="token-value" :class="colorClass">
          {{ balance.toLocaleString() }} {{ $t('lesson.methodExecution.tokens') }}
        </span>
      </div>
    </div>

    <div class="token-bar">
      <div class="token-fill" :class="colorClass" :style="{ width: `${percentage}%` }"></div>
    </div>

    <div class="token-hint">
      <span v-if="balance < 500" class="hint-warning">
        {{ $t('lesson.methodExecution.lowBalanceWarning') }}
      </span>
      <span v-else-if="balance < 2000" class="hint-info">
        {{ $t('lesson.methodExecution.mediumBalanceInfo') }}
      </span>
      <span v-else class="hint-success">
        {{ $t('lesson.methodExecution.goodBalanceInfo') }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TokenBalanceDisplay Component
 * ==============================
 * Displays user token balance with color-coded status bar
 */

interface Props {
  balance: number
  colorClass: string
  percentage: number
}

defineProps<Props>()
</script>

<style scoped>
/* Token Balance Section */
.token-balance-section {
  padding: 1rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  margin-bottom: 1rem;
}

.token-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.token-icon {
  font-size: 2rem;
  line-height: 1;
}

.token-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.token-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.token-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.2;
  transition: color 0.3s;
}

.token-value.color-green {
  color: #10b981;
}

.token-value.color-yellow {
  color: #f59e0b;
}

.token-value.color-red {
  color: #ef4444;
}

/* Token Bar */
.token-bar {
  height: 8px;
  background-color: var(--color-surface-secondary, #f9fafb);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.token-fill {
  height: 100%;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 9999px;
}

.token-fill.color-green {
  background: linear-gradient(90deg, #10b981, #059669);
}

.token-fill.color-yellow {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.token-fill.color-red {
  background: linear-gradient(90deg, #ef4444, #dc2626);
}

/* Token Hint */
.token-hint {
  text-align: center;
}

.token-hint span {
  font-size: 0.75rem;
  font-weight: 500;
}

.hint-warning {
  color: #ef4444;
}

.hint-info {
  color: #f59e0b;
}

.hint-success {
  color: #10b981;
}
</style>
