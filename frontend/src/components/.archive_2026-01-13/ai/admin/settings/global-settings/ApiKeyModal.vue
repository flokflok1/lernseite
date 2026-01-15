<!--
  ApiKeyModal - API Key Management Modal
  Sub-component of GlobalSettingsTab
-->

<template>
  <div v-if="provider" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ provider.display_name }} - {{ $t('windows.aiEditorGlobalSettings.apiKeyTitle') }}</h3>
        <button @click="$emit('close')" class="modal-close">×</button>
      </div>
      <div class="modal-body">
        <div class="form-row">
          <label>{{ $t('windows.aiEditorGlobalSettings.apiKeyTitle') }}</label>
          <div class="input-group">
            <input
              :value="apiKey"
              @input="$emit('update:apiKey', ($event.target as HTMLInputElement).value)"
              :type="showKey ? 'text' : 'password'"
              :placeholder="provider.has_api_key ? $t('windows.aiEditorGlobalSettings.apiKeyMasked') : $t('windows.aiEditorGlobalSettings.apiKeyPlaceholder')"
              class="form-input mono"
            />
            <button @click="$emit('toggleShow')" class="btn-icon">{{ showKey ? '🙈' : '👁️' }}</button>
          </div>
        </div>
        <div v-if="result" class="api-key-result" :class="result.success ? 'success' : 'error'">{{ result.message }}</div>
      </div>
      <div class="modal-footer">
        <button @click="$emit('test')" :disabled="testing" class="btn-secondary">{{ testing ? $t('windows.aiEditorGlobalSettings.testingApiKey') : $t('windows.aiEditorGlobalSettings.testApiKey') }}</button>
        <button @click="$emit('save')" :disabled="!apiKey || saving" class="btn-primary">{{ saving ? $t('windows.aiEditorGlobalSettings.savingApiKey') : $t('windows.aiEditorGlobalSettings.saveApiKey') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Provider { provider_id: number; name: string; display_name: string; has_api_key: boolean }

defineProps<{
  provider: Provider | null
  apiKey: string
  showKey: boolean
  testing: boolean
  saving: boolean
  result: { success: boolean; message: string } | null
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'update:apiKey', value: string): void
  (e: 'toggleShow'): void
  (e: 'test'): void
  (e: 'save'): void
}>()
</script>

<style scoped>
.modal-overlay { position: fixed; inset: 0; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: var(--color-surface); border-radius: 0.75rem; width: 100%; max-width: 450px; overflow: hidden; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 1px solid var(--color-border); }
.modal-header h3 { font-size: 1rem; font-weight: 600; color: var(--color-text-primary); margin: 0; }
.modal-close { font-size: 1.5rem; line-height: 1; color: var(--color-text-tertiary); }
.modal-body { padding: 1.25rem; }
.form-row { display: flex; flex-direction: column; gap: 0.25rem; }
.form-row label { font-size: 0.6875rem; font-weight: 500; color: var(--color-text-secondary); }
.input-group { display: flex; gap: 0.5rem; }
.input-group .form-input { flex: 1; }
.form-input { padding: 0.5rem 0.75rem; background: var(--color-surface-secondary); border: 1px solid var(--color-border); border-radius: 0.375rem; color: var(--color-text-primary); font-size: 0.875rem; }
.form-input:focus { outline: none; border-color: var(--color-primary); }
.form-input.mono { font-family: ui-monospace, monospace; }
.btn-icon { padding: 0.5rem; background: var(--color-surface-secondary); border: 1px solid var(--color-border); border-radius: 0.375rem; }
.api-key-result { margin-top: 0.75rem; padding: 0.5rem 0.75rem; border-radius: 0.375rem; font-size: 0.8125rem; }
.api-key-result.success { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
.api-key-result.error { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.5rem; padding: 1rem 1.25rem; border-top: 1px solid var(--color-border); background: var(--color-surface-secondary); }
.btn-primary { padding: 0.5rem 1rem; background: var(--color-primary); color: white; border-radius: 0.375rem; font-size: 0.875rem; font-weight: 500; }
.btn-primary:disabled { opacity: 0.5; }
.btn-secondary { padding: 0.5rem 1rem; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 0.375rem; color: var(--color-text-primary); font-size: 0.875rem; }
</style>
