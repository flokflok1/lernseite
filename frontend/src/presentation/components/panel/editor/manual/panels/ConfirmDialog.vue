/**
 * ConfirmDialog.vue
 *
 * Styled replacement for native window.confirm() and window.prompt().
 * Works with useConfirmDialog composable (singleton state).
 * Mount once in ManualEditorContainerView via Teleport.
 */

<script setup lang="ts">
import { ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useConfirmDialog } from '../composables/useConfirmDialog'
import { useFocusTrap } from '../composables/useFocusTrap'

const { t } = useI18n()
const {
  visible,
  dialogMode,
  message,
  inputValue,
  inputPlaceholder,
  handleConfirm,
  handleCancel,
} = useConfirmDialog()

const { trapRef } = useFocusTrap(visible)
const promptInputRef = ref<HTMLInputElement | null>(null)

// Auto-focus input when prompt mode opens
watch(visible, (open) => {
  if (open && dialogMode.value === 'prompt') {
    nextTick(() => promptInputRef.value?.focus())
  }
})

// Resolve pending promise on unmount to prevent caller from hanging
onBeforeUnmount(() => {
  if (visible.value) handleCancel()
})
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="confirm-overlay" @click.self="handleCancel">
      <div ref="trapRef" class="confirm-dialog" role="dialog" aria-modal="true" :aria-label="message">
        <p class="confirm-message">{{ message }}</p>

        <!-- Prompt mode: text input -->
        <input
          v-if="dialogMode === 'prompt'"
          ref="promptInputRef"
          v-model="inputValue"
          type="text"
          class="prompt-input"
          :placeholder="inputPlaceholder"
          @keydown.enter="handleConfirm"
          @keydown.escape="handleCancel"
        />

        <div class="confirm-actions">
          <button class="confirm-cancel" @click="handleCancel">
            {{ t('panel.manualEditor.content.cancel') }}
          </button>
          <button class="confirm-ok" @click="handleConfirm">
            {{ t('panel.manualEditor.content.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.confirm-dialog {
  background: var(--color-surface);
  border-radius: 8px;
  padding: 20px;
  width: 380px;
  max-width: 90vw;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.confirm-message {
  margin: 0 0 16px;
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text-primary);
}

.prompt-input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 13px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  box-sizing: border-box;
  margin-bottom: 12px;
}

.prompt-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.confirm-cancel {
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 12px;
}

.confirm-cancel:hover {
  background: color-mix(in srgb, var(--color-border) 30%, var(--color-surface));
}

.confirm-ok {
  padding: 6px 14px;
  border: none;
  border-radius: 4px;
  background: var(--color-accent);
  color: white;
  cursor: pointer;
  font-size: 12px;
}

.confirm-ok:hover {
  filter: brightness(0.9);
}
</style>
