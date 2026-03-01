<!--
  ConfirmBanner — Shared inline confirmation UI for course actions.
  Used by both AI Editor (CourseTab) and Manual Editor (CourseSelector).
  Renders a message with Confirm + Cancel buttons in a colored banner.
-->
<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Props {
  message: string
  confirmLabel: string
  variant?: 'danger' | 'warning'
}

withDefaults(defineProps<Props>(), {
  variant: 'danger'
})

defineEmits<{
  confirm: []
  cancel: []
}>()

const { t } = useI18n()
</script>

<template>
  <div class="confirm-banner" :class="`confirm-banner--${variant}`">
    <p class="confirm-banner__text">{{ message }}</p>
    <div class="confirm-banner__actions">
      <button
        class="confirm-banner__btn confirm-banner__btn--action"
        :class="`confirm-banner__btn--${variant}`"
        @click.stop="$emit('confirm')"
      >
        {{ confirmLabel }}
      </button>
      <button
        class="confirm-banner__btn confirm-banner__btn--cancel"
        @click.stop="$emit('cancel')"
      >
        {{ t('common.cancel') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.confirm-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
}

.confirm-banner--danger {
  background: color-mix(in srgb, var(--color-error) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-error) 30%, transparent);
}

.confirm-banner--warning {
  background: color-mix(in srgb, var(--color-warning) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-warning) 30%, transparent);
}

.confirm-banner__text {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.confirm-banner__actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.confirm-banner__btn {
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: filter 0.15s;
}

.confirm-banner__btn--action {
  color: white;
  border: none;
  font-weight: 600;
}

.confirm-banner__btn--danger {
  background: var(--color-error);
}

.confirm-banner__btn--warning {
  background: var(--color-warning);
}

.confirm-banner__btn--action:hover {
  filter: brightness(0.9);
}

.confirm-banner__btn--cancel {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  font-weight: 500;
}

.confirm-banner__btn--cancel:hover {
  border-color: var(--color-text-tertiary);
}
</style>
