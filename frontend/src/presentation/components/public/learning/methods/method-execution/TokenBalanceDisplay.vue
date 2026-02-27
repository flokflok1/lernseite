<template>
  <div class="token-balance-section">
    <div class="token-header">
      <div class="token-icon-wrap">
        <svg class="token-svg" viewBox="0 0 24 24" fill="none">
          <path d="M12 2L2 7l10 5 10-5-10-5z" fill="currentColor" opacity="0.3" />
          <path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
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
interface Props {
  balance: number
  colorClass: string
  percentage: number
}

defineProps<Props>()
</script>

<style scoped>
.token-balance-section {
  padding: 0.625rem 0.75rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.06) 0%, rgba(139, 92, 246, 0.06) 100%);
  border-bottom: 1px solid var(--color-border, #e5e7eb);
}

.token-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.375rem;
}

.token-icon-wrap {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  flex-shrink: 0;
}

.token-svg {
  width: 1.125rem;
  height: 1.125rem;
}

.token-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.token-label {
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.token-value {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.2;
  transition: color 0.3s;
}

.token-value.color-green { color: #10b981; }
.token-value.color-yellow { color: #f59e0b; }
.token-value.color-red { color: #ef4444; }

/* Token Bar */
.token-bar {
  height: 5px;
  background-color: var(--color-surface-secondary, #f3f4f6);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

:root.dark .token-bar {
  background-color: rgba(255, 255, 255, 0.1);
}

.token-fill {
  height: 100%;
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 9999px;
}

.token-fill.color-green { background: linear-gradient(90deg, #10b981, #059669); }
.token-fill.color-yellow { background: linear-gradient(90deg, #f59e0b, #d97706); }
.token-fill.color-red { background: linear-gradient(90deg, #ef4444, #dc2626); }

/* Hint */
.token-hint {
  text-align: center;
}

.token-hint span {
  font-size: 0.6875rem;
  font-weight: 500;
}

.hint-warning { color: #ef4444; }
.hint-info { color: #f59e0b; }
.hint-success { color: #10b981; }
</style>
