<!--
  TutorPlayerNavigation - Navigation buttons and quick actions for the tutor player
-->

<template>
  <div class="tutor-navigation">
    <!-- Navigation -->
    <div class="nav-buttons">
      <button @click="$emit('prev')" class="nav-btn nav-prev" :disabled="currentStep === 0">
        {{ $t('lesson.tutorPlayer.back') }}
      </button>
      <button v-if="currentStep < totalSteps - 1" @click="$emit('next')" class="nav-btn nav-next">
        {{ $t('lesson.tutorPlayer.next') }}
      </button>
      <button v-else @click="$emit('finish')" class="nav-btn nav-finish">
        {{ $t('lesson.tutorPlayer.done') }}
      </button>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <button @click="$emit('back-to-theory')" class="action-btn">
        {{ $t('lesson.tutorPlayer.backToTheory') }}
      </button>
      <button @click="$emit('restart')" class="action-btn">
        {{ $t('lesson.tutorPlayer.restart') }}
      </button>
      <button @click="$emit('practice')" class="action-btn primary">
        {{ $t('lesson.tutorPlayer.practiceNow') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * TutorPlayerNavigation
 *
 * Renders prev/next/finish navigation and quick action buttons
 * for the tutor step player.
 */

interface Props {
  currentStep: number
  totalSteps: number
}

defineProps<Props>()

defineEmits<{
  prev: []
  next: []
  finish: []
  restart: []
  'back-to-theory': []
  practice: []
}>()
</script>

<style scoped>
/* Navigation */
.nav-buttons {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
}

.nav-btn {
  flex: 1;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-prev {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  color: var(--color-text-secondary, #94a3b8);
}

.nav-prev:hover:not(:disabled) {
  background: var(--color-surface-secondary, #0f172a);
  color: var(--color-text-primary, #f1f5f9);
}

.nav-prev:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.nav-next {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
}

.nav-next:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.nav-finish {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.nav-finish:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Quick Actions */
.quick-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
  padding-top: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border, #334155);
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-text-secondary, #94a3b8);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--color-surface-secondary, #0f172a);
  color: var(--color-text-primary, #f1f5f9);
  border-color: var(--color-primary, #6366f1);
}

.action-btn.primary {
  background: var(--color-primary, #6366f1);
  border-color: var(--color-primary, #6366f1);
  color: white;
}

.action-btn.primary:hover {
  filter: brightness(1.1);
}
</style>
