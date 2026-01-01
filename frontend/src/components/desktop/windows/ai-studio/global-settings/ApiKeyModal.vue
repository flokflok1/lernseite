<!--
  ApiKeyModal - Modal for entering and testing API keys

  Provides input field for API key with show/hide,
  test and save functionality.
-->

<template>
  <div v-if="provider" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ provider.display_name }} - API-Key</h3>
        <button @click="$emit('close')" class="modal-close">×</button>
      </div>

      <div class="modal-body">
        <div class="form-row">
          <label>API-Key</label>
          <div class="input-group">
            <input
              :value="modelValue"
              @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
              :type="showKey ? 'text' : 'password'"
              :placeholder="provider.has_api_key ? '••••••••••••••••' : 'API Key eingeben...'"
              class="form-input mono"
            />
            <button @click="showKey = !showKey" class="btn-icon">
              {{ showKey ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div v-if="result" class="result-message" :class="result.success ? 'success' : 'error'">
          {{ result.message }}
        </div>
      </div>

      <div class="modal-footer">
        <button
          @click="$emit('test')"
          :disabled="isTesting"
          class="btn-secondary"
        >
          {{ isTesting ? 'Teste...' : 'Testen' }}
        </button>
        <button
          @click="$emit('save')"
          :disabled="!modelValue || isSaving"
          class="btn-primary"
        >
          {{ isSaving ? 'Speichern...' : 'Speichern' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Types
interface Provider {
  provider_id: number
  name: string
  display_name: string
  active: boolean
  has_api_key: boolean
}

interface Result {
  success: boolean
  message: string
}

// Props
defineProps<{
  provider: Provider | null
  modelValue: string
  isTesting?: boolean
  isSaving?: boolean
  result?: Result | null
}>()

// Emits
defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'test'): void
  (e: 'save'): void
  (e: 'close'): void
}>()

// Local state
const showKey = ref(false)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 100%;
  max-width: 480px;
  background: var(--color-surface);
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--color-text-tertiary);
  border-radius: 0.25rem;
}

.modal-close:hover {
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
}

.modal-body {
  padding: 1.25rem;
}

.form-row {
  margin-bottom: 1rem;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-row label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 0.375rem;
}

.input-group {
  display: flex;
  gap: 0.5rem;
}

.form-input {
  flex: 1;
  padding: 0.625rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: var(--color-bg);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.mono {
  font-family: monospace;
}

.btn-icon {
  width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  cursor: pointer;
}

.btn-icon:hover {
  background: var(--color-surface);
}

.result-message {
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  margin-top: 0.75rem;
}

.result-message.success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #22c55e;
}

.result-message.error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #ef4444;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.btn-primary,
.btn-secondary {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  border: none;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--color-primary);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
