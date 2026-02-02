<!--
  ProfileEditor - Profile Form Editor
  Sub-component of GlobalSettingsTab
-->

<template>
  <div class="profile-editor">
    <div v-if="!profile && !isCreating" class="editor-empty">
      <p>{{ $t('windows.aiEditorGlobalSettings.selectProfileHint') }}</p>
    </div>

    <template v-else>
      <div class="editor-header">
        <h4>{{ isCreating ? $t('windows.aiEditorGlobalSettings.newProfileTitle') : $t('windows.aiEditorGlobalSettings.editProfileTitle') }}</h4>
      </div>

      <div class="editor-form">
        <div class="form-row">
          <label>{{ $t('windows.aiEditorGlobalSettings.key') }}</label>
          <input v-if="isCreating" :value="formData.key" @input="updateField('key', $event)" type="text" :placeholder="$t('windows.aiEditorGlobalSettings.keyPlaceholder')" class="form-input" />
          <span v-else class="form-value mono">{{ formData.key }}</span>
        </div>
        <div class="form-row">
          <label>{{ $t('windows.aiEditorGlobalSettings.name') }}</label>
          <input :value="formData.name" @input="updateField('name', $event)" type="text" :placeholder="$t('windows.aiEditorGlobalSettings.namePlaceholder')" class="form-input" />
        </div>
        <div class="form-row">
          <label>{{ $t('windows.aiEditorGlobalSettings.description') }}</label>
          <input :value="formData.description" @input="updateField('description', $event)" type="text" :placeholder="$t('windows.aiEditorGlobalSettings.descriptionPlaceholder')" class="form-input" />
        </div>

        <div class="categories-section">
          <h5>{{ $t('windows.aiEditorGlobalSettings.modelsPerCategory') }}</h5>
          <div class="category-grid">
            <div v-for="category in categories" :key="category" class="category-item">
              <label class="category-label">
                <span class="category-icon">{{ getCategoryIcon(category) }}</span>
                <span class="category-name">{{ category }}</span>
              </label>
              <select :value="formData.models[category]" @change="updateModel(category, $event)" class="category-select">
                <option value="">{{ $t('windows.aiEditorGlobalSettings.notSet') }}</option>
                <option v-for="model in getModelsForCategory(category)" :key="model.model_id" :value="model.model_id || model.model_name">
                  {{ model.display_name || model.model_name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="editor-actions">
          <button v-if="!isCreating && !profile?.is_default" @click="$emit('delete')" class="btn-danger">{{ $t('windows.aiEditorGlobalSettings.delete') }}</button>
          <div class="action-spacer"></div>
          <button v-if="!isCreating && !profile?.is_default" @click="$emit('setDefault')" class="btn-secondary">{{ $t('windows.aiEditorGlobalSettings.setAsDefault') }}</button>
          <button @click="$emit('cancel')" class="btn-secondary">{{ $t('windows.aiEditorGlobalSettings.cancel') }}</button>
          <button @click="$emit('save')" :disabled="saving" class="btn-primary">{{ saving ? $t('windows.aiEditorGlobalSettings.saving') : $t('windows.aiEditorGlobalSettings.save') }}</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
interface Profile { key: string; name: string; description?: string; is_default: boolean }
interface AIModel { model_id: number; model_name: string; display_name?: string; category: string; active: boolean }
interface FormData { key: string; name: string; description: string; models: Record<string, string> }

const props = defineProps<{
  profile?: Profile | null
  isCreating: boolean
  formData: FormData
  categories: string[]
  models: AIModel[]
  saving: boolean
}>()

const emit = defineEmits<{
  (e: 'update:formData', data: FormData): void
  (e: 'save'): void
  (e: 'cancel'): void
  (e: 'delete'): void
  (e: 'setDefault'): void
}>()

const categoryIcons: Record<string, string> = { chat: '💬', audio: '🔊', video: '🎬', embedding: '📊', image: '🖼️', reasoning: '🧠', realtime: '⚡', moderation: '🛡️', vision: '👁️', transcription: '📝', translation: '🌍', legacy: '⚙️' }

function getCategoryIcon(category: string): string { return categoryIcons[category] || '📦' }
function getModelsForCategory(category: string): AIModel[] { return props.models.filter(m => m.category === category && m.active) }
function updateField(field: string, event: Event) { emit('update:formData', { ...props.formData, [field]: (event.target as HTMLInputElement).value }) }
function updateModel(category: string, event: Event) { emit('update:formData', { ...props.formData, models: { ...props.formData.models, [category]: (event.target as HTMLSelectElement).value } }) }
</script>

<style scoped>
.profile-editor { padding: 1rem; overflow-y: auto; max-height: 320px; }
.editor-empty { display: flex; align-items: center; justify-content: center; height: 100%; color: var(--color-text-tertiary); }
.editor-header { margin-bottom: 0.75rem; }
.editor-header h4 { font-size: 0.875rem; font-weight: 600; color: var(--color-text-primary); margin: 0; }
.editor-form { display: flex; flex-direction: column; gap: 0.5rem; }
.form-row { display: flex; flex-direction: column; gap: 0.25rem; }
.form-row label { font-size: 0.6875rem; font-weight: 500; color: var(--color-text-secondary); }
.form-input { padding: 0.375rem 0.5rem; background: var(--color-surface-secondary); border: 1px solid var(--color-border); border-radius: 0.25rem; color: var(--color-text-primary); font-size: 0.8125rem; }
.form-input:focus { outline: none; border-color: var(--color-primary); }
.form-value { padding: 0.5rem 0; color: var(--color-text-primary); font-size: 0.875rem; }
.form-value.mono, .form-input.mono { font-family: ui-monospace, monospace; }
.categories-section { margin-top: 0.5rem; padding-top: 0.75rem; border-top: 1px solid var(--color-border); }
.categories-section h5 { font-size: 0.75rem; font-weight: 600; color: var(--color-text-primary); margin: 0 0 0.5rem 0; }
.category-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; }
.category-item { display: flex; flex-direction: column; gap: 0.25rem; }
.category-label { display: flex; align-items: center; gap: 0.25rem; font-size: 0.6875rem; color: var(--color-text-secondary); }
.category-icon { font-size: 0.75rem; }
.category-name { text-transform: capitalize; }
.category-select { padding: 0.35rem 0.5rem; background: var(--color-surface-secondary); border: 1px solid var(--color-border); border-radius: 0.25rem; color: var(--color-text-primary); font-size: 0.6875rem; }
.category-select:focus { outline: none; border-color: var(--color-primary); }
.editor-actions { display: flex; align-items: center; gap: 0.375rem; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--color-border); }
.action-spacer { flex: 1; }
.btn-primary { padding: 0.375rem 0.75rem; background: var(--color-primary); color: white; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 500; }
.btn-primary:disabled { opacity: 0.5; }
.btn-secondary { padding: 0.375rem 0.75rem; background: var(--color-surface-secondary); border: 1px solid var(--color-border); border-radius: 0.25rem; color: var(--color-text-primary); font-size: 0.75rem; }
.btn-danger { padding: 0.375rem 0.75rem; background: #ef4444; color: white; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 500; }
</style>
