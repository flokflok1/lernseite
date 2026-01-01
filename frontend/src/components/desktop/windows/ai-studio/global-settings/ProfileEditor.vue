<!--
  ProfileEditor - Edit or create AI model profiles

  Displays form for editing profile metadata and
  selecting models for each category.
-->

<template>
  <div class="profile-editor">
    <div v-if="!profile && !isCreating" class="editor-empty">
      <p>Wähle ein Profil aus der Liste</p>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="editor-header">
        <h4>{{ isCreating ? 'Neues Profil' : 'Profil bearbeiten' }}</h4>
      </div>

      <div class="editor-form">
        <!-- Key -->
        <div class="form-row">
          <label>Schlüssel</label>
          <input
            v-if="isCreating"
            :value="formData.key"
            @input="$emit('update:key', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="z.B. premium"
            class="form-input"
          />
          <span v-else class="form-value mono">{{ formData.key }}</span>
        </div>

        <!-- Name -->
        <div class="form-row">
          <label>Name</label>
          <input
            :value="formData.name"
            @input="$emit('update:name', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="Anzeigename"
            class="form-input"
          />
        </div>

        <!-- Description -->
        <div class="form-row">
          <label>Beschreibung</label>
          <input
            :value="formData.description"
            @input="$emit('update:description', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="Optional"
            class="form-input"
          />
        </div>

        <!-- Categories -->
        <div class="categories-section">
          <h5>Modelle pro Kategorie</h5>
          <div class="category-grid">
            <div
              v-for="category in categories"
              :key="category"
              class="category-item"
            >
              <label class="category-label">
                <span class="category-icon">{{ getCategoryIcon(category) }}</span>
                <span class="category-name">{{ category }}</span>
              </label>
              <select
                :value="formData.models[category]"
                @change="handleModelChange(category, ($event.target as HTMLSelectElement).value)"
                class="category-select"
              >
                <option value="">Nicht gesetzt</option>
                <option
                  v-for="model in getModelsForCategory(category)"
                  :key="model.model_id"
                  :value="model.model_id || model.model_name"
                >
                  {{ model.display_name || model.model_name }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="editor-actions">
          <button
            v-if="!isCreating && !profile?.is_default"
            @click="$emit('delete')"
            class="btn-danger"
          >
            Löschen
          </button>
          <div class="action-spacer"></div>
          <button
            v-if="!isCreating && !profile?.is_default"
            @click="$emit('set-default')"
            class="btn-secondary"
          >
            Als Default
          </button>
          <button @click="$emit('cancel')" class="btn-secondary">
            Abbrechen
          </button>
          <button @click="$emit('save')" :disabled="isSaving" class="btn-primary">
            {{ isSaving ? 'Speichern...' : 'Speichern' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
// Types
interface Profile {
  key: string
  name: string
  description?: string
  is_default: boolean
  [key: string]: any
}

interface AIModel {
  model_id: number
  model_name: string
  display_name?: string
  provider_name: string
  category: string
  active: boolean
}

interface FormData {
  key: string
  name: string
  description: string
  models: Record<string, string>
}

// Props
const props = defineProps<{
  profile?: Profile | null
  isCreating?: boolean
  isSaving?: boolean
  formData: FormData
  categories: string[]
  models: AIModel[]
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:key', value: string): void
  (e: 'update:name', value: string): void
  (e: 'update:description', value: string): void
  (e: 'update:model', category: string, modelId: string): void
  (e: 'save'): void
  (e: 'cancel'): void
  (e: 'delete'): void
  (e: 'set-default'): void
}>()

// Category Icons
const categoryIcons: Record<string, string> = {
  chat: '💬',
  audio: '🔊',
  video: '🎬',
  embedding: '📊',
  image: '🖼️',
  reasoning: '🧠',
  realtime: '⚡',
  moderation: '🛡️',
  vision: '👁️',
  transcription: '📝',
  translation: '🌍',
  legacy: '⚙️'
}

// Methods
function getCategoryIcon(category: string): string {
  return categoryIcons[category] || '📦'
}

function getModelsForCategory(category: string): AIModel[] {
  return props.models.filter(m => m.category === category && m.active)
}

function handleModelChange(category: string, modelId: string) {
  emit('update:model', category, modelId)
}
</script>

<style scoped>
.profile-editor {
  flex: 1;
  background: var(--color-surface);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.editor-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  color: var(--color-text-tertiary);
}

.editor-header {
  padding: 0.75rem 1rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.editor-header h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.editor-form {
  padding: 1rem;
}

.form-row {
  margin-bottom: 1rem;
}

.form-row label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 0.375rem;
}

.form-input {
  width: 100%;
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

.form-value {
  display: block;
  padding: 0.625rem 0.75rem;
  background: var(--color-surface-secondary);
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.mono {
  font-family: monospace;
}

/* Categories */
.categories-section {
  margin-top: 1.5rem;
}

.categories-section h5 {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.category-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.category-icon {
  font-size: 0.875rem;
}

.category-select {
  width: 100%;
  padding: 0.5rem 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  background: var(--color-bg);
}

.category-select:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Actions */
.editor-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.action-spacer {
  flex: 1;
}

.btn-primary,
.btn-secondary,
.btn-danger {
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
  background: var(--color-surface-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}
</style>
