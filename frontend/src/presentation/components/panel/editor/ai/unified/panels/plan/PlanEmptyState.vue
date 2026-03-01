<script setup lang="ts">
/**
 * PlanEmptyState — Empty state with scope selector and create buttons.
 * Shown when no active plan exists.
 */
import { ref, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PlanScope } from '../../types'
import type { useEditorState } from '../../composables/editor/useEditorState'

interface Props {
  isCreating: boolean
  hasFiles?: boolean
}

withDefaults(defineProps<Props>(), {
  hasFiles: false,
})

const emit = defineEmits<{
  createPlan: [scope: PlanScope, scopeId?: string]
}>()

const editorState = inject<ReturnType<typeof useEditorState>>('editorState')
const { t } = useI18n()

const selectedScope = ref<PlanScope>('course')
</script>

<template>
  <div class="empty-state">
    <div class="empty-icon">&#x1f5fa;&#xfe0f;</div>
    <h3 class="empty-title">{{ t('aiEditor.plan.emptyTitle') }}</h3>
    <p class="empty-desc">{{ t('aiEditor.plan.emptyDescription') }}</p>

    <!-- Scope Selector -->
    <div class="scope-selector">
      <label class="scope-label">{{ t('aiEditor.plan.scope.label') }}</label>
      <div class="scope-options">
        <button
          v-for="s in (['course', 'chapter', 'lesson'] as PlanScope[])"
          :key="s"
          class="scope-btn"
          :class="{ 'scope-btn-active': selectedScope === s }"
          @click="selectedScope = s"
        >
          {{ t(`aiEditor.plan.scope.${s}`) }}
        </button>
      </div>
    </div>

    <button
      class="create-btn"
      :disabled="isCreating"
      @click="emit('createPlan', selectedScope)"
    >
      <span v-if="isCreating" class="pulse">{{ t('aiEditor.plan.creating') }}</span>
      <template v-else>
        <span v-if="hasFiles">{{ t('aiEditor.plan.createFromFile') }}</span>
        <span v-else>{{ t('aiEditor.plan.createManual') }}</span>
      </template>
    </button>

    <button
      v-if="!hasFiles"
      class="secondary-btn"
      :disabled="isCreating"
      @click="editorState?.setTab('files')"
    >
      {{ t('aiEditor.plan.uploadFile') }}
    </button>
  </div>
</template>

<style scoped>
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
}
.empty-icon { font-size: 2.5rem; }
.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary, #fff);
}
.empty-desc {
  font-size: 0.8125rem;
  color: var(--color-text-tertiary, #9ca3af);
  max-width: 22rem;
  text-align: center;
  line-height: 1.5;
}

/* Scope Selector */
.scope-selector {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  margin: 0.5rem 0;
}
.scope-label {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.scope-options {
  display: flex;
  gap: 0.25rem;
  background: var(--color-surface, #111827);
  border-radius: 0.375rem;
  padding: 0.125rem;
  border: 1px solid var(--color-border, #374151);
}
.scope-btn {
  padding: 0.375rem 0.75rem;
  background: transparent;
  color: var(--color-text-secondary, #9ca3af);
  border: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.15s;
}
.scope-btn:hover { color: var(--color-text-primary, #fff); }
.scope-btn-active {
  background: var(--color-primary, #6366f1);
  color: #fff;
}

.create-btn {
  margin-top: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: var(--color-primary, #6366f1);
  color: #fff;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
}
.create-btn:hover:not(:disabled) { background: var(--color-primary-hover, #4f46e5); }
.create-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.secondary-btn {
  padding: 0.5rem 1rem;
  background: var(--color-surface-secondary, #374151);
  color: var(--color-text-secondary, #d1d5db);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  border: none;
  cursor: pointer;
  transition: background 0.15s;
}
.secondary-btn:hover:not(:disabled) { background: var(--color-surface-tertiary, #4b5563); }

.pulse { animation: pulse-anim 1.5s ease-in-out infinite; }
@keyframes pulse-anim {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
