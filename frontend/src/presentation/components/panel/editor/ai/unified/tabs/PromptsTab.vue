<!--
  PromptsTab — Prompt Library with browse, detail & edit modes.
  Browse: category filter + search + card grid
  Detail: read-only view of template
  Edit: inline editing of editable fields
-->
<template>
  <div class="prompts-tab">
    <!-- Detail / Edit View -->
    <div v-if="selectedTemplate" class="detail-view">
      <div class="detail-header">
        <button class="back-btn" @click="closeDetail">
          ← {{ t('aiEditor.prompts.library.back') }}
        </button>
        <div class="detail-actions">
          <button
            v-if="!isEditing && !selectedTemplate.is_system"
            class="edit-btn"
            @click="startEditing"
          >
            {{ t('aiEditor.prompts.library.edit') }}
          </button>
          <button
            v-if="!isEditing && !selectedTemplate.is_system"
            class="delete-btn"
            @click="confirmingDelete = true"
          >
            {{ t('aiEditor.prompts.library.delete') }}
          </button>
        </div>
      </div>

      <!-- Delete confirmation -->
      <div v-if="confirmingDelete" class="confirm-banner">
        <p>{{ t('aiEditor.prompts.library.confirmDelete', { title: selectedTemplate.title }) }}</p>
        <div class="confirm-actions">
          <button class="btn-danger" @click="handleDelete">{{ t('aiEditor.prompts.library.delete') }}</button>
          <button class="btn-cancel" @click="confirmingDelete = false">{{ t('common.cancel') }}</button>
        </div>
      </div>

      <!-- Template detail content -->
      <div class="detail-body">
        <div class="detail-meta">
          <h3 v-if="!isEditing" class="detail-title">{{ selectedTemplate.title }}</h3>
          <input
            v-else
            v-model="editForm.title"
            class="edit-input edit-title"
          />

          <div class="meta-row">
            <span class="badge badge-category">
              {{ t('aiEditor.prompts.library.categories.' + selectedTemplate.category) }}
            </span>
            <span class="badge badge-style">
              {{ t('aiEditor.prompts.library.styles.' + selectedTemplate.style) }}
            </span>
            <span v-if="selectedTemplate.is_default" class="badge badge-default">
              {{ t('aiEditor.prompts.library.default') }}
            </span>
            <span v-if="selectedTemplate.is_system" class="badge badge-system">
              {{ t('aiEditor.prompts.library.system') }}
            </span>
          </div>

          <p v-if="!isEditing" class="detail-desc">{{ selectedTemplate.description }}</p>
          <textarea
            v-else
            v-model="editForm.description"
            class="edit-input edit-desc"
            rows="2"
          />
        </div>

        <!-- Config info -->
        <div class="detail-config">
          <div v-if="selectedTemplate.model" class="config-item">
            <span class="config-label">{{ t('aiEditor.prompts.library.model') }}</span>
            <span class="config-value">{{ selectedTemplate.model }}</span>
          </div>
          <div v-if="selectedTemplate.temperature != null" class="config-item">
            <span class="config-label">{{ t('aiEditor.prompts.library.temperature') }}</span>
            <span v-if="!isEditing" class="config-value">{{ selectedTemplate.temperature }}</span>
            <input v-else v-model.number="editForm.temperature" type="number" step="0.1" min="0" max="2" class="edit-input edit-small" />
          </div>
          <div v-if="selectedTemplate.max_tokens != null" class="config-item">
            <span class="config-label">{{ t('aiEditor.prompts.library.maxTokens') }}</span>
            <span v-if="!isEditing" class="config-value">{{ selectedTemplate.max_tokens }}</span>
            <input v-else v-model.number="editForm.max_tokens" type="number" min="100" class="edit-input edit-small" />
          </div>
          <div class="config-item">
            <span class="config-label">{{ t('aiEditor.prompts.library.version') }}</span>
            <span class="config-value">v{{ selectedTemplate.version }}</span>
          </div>
        </div>

        <!-- System Prompt -->
        <div class="prompt-section">
          <h4 class="section-label">{{ t('aiEditor.prompts.library.systemPrompt') }}</h4>
          <pre v-if="!isEditing" class="prompt-block">{{ selectedTemplate.system_prompt }}</pre>
          <textarea
            v-else
            v-model="editForm.system_prompt"
            class="edit-input edit-prompt"
            rows="8"
          />
        </div>

        <!-- User Prompt Template -->
        <div class="prompt-section">
          <h4 class="section-label">{{ t('aiEditor.prompts.library.userPrompt') }}</h4>
          <pre v-if="!isEditing" class="prompt-block">{{ selectedTemplate.user_prompt_template }}</pre>
          <textarea
            v-else
            v-model="editForm.user_prompt_template"
            class="edit-input edit-prompt"
            rows="6"
          />
        </div>

        <!-- Variables -->
        <div v-if="selectedTemplate.variables?.length" class="prompt-section">
          <h4 class="section-label">{{ t('aiEditor.prompts.library.variables') }}</h4>
          <div class="variables-table">
            <div v-for="v in selectedTemplate.variables" :key="v.name" class="var-row">
              <span class="var-name">{{ v.name }}</span>
              <span class="var-desc">{{ v.description }}</span>
              <span class="var-required" :class="{ required: v.required }">
                {{ v.required ? t('aiEditor.prompts.library.variableRequired') : t('aiEditor.prompts.library.variableOptional') }}
              </span>
            </div>
          </div>
        </div>

        <!-- Edit actions -->
        <div v-if="isEditing" class="edit-actions">
          <button class="btn-save" :disabled="isSaving" @click="handleSave">
            {{ isSaving ? t('aiEditor.prompts.library.saving') : t('aiEditor.prompts.library.save') }}
          </button>
          <button class="btn-cancel" @click="cancelEditing">{{ t('common.cancel') }}</button>
        </div>
      </div>
    </div>

    <!-- Browse View -->
    <template v-else>
      <div class="catalog-header">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('aiEditor.prompts.library.searchPlaceholder')"
          class="search-input"
        />
        <div class="category-filters">
          <button
            v-for="cat in categories"
            :key="cat"
            class="category-btn"
            :class="{ active: activeCategory === cat }"
            @click="activeCategory = cat"
          >
            {{ cat === 'all' ? t('aiEditor.prompts.library.allCategories') : t('aiEditor.prompts.library.categories.' + cat) }}
          </button>
        </div>
      </div>

      <div class="catalog-body">
        <div v-if="isLoading" class="state-message">{{ t('common.loading') }}</div>
        <div v-else-if="loadError" class="state-message error">{{ t('aiEditor.prompts.library.loadError') }}</div>
        <div v-else-if="filteredTemplates.length === 0" class="state-message">
          {{ templates.length === 0 ? t('aiEditor.prompts.library.empty') : t('aiEditor.prompts.library.noResults') }}
        </div>
        <div v-else class="templates-grid">
          <button
            v-for="tpl in filteredTemplates"
            :key="tpl.template_id"
            class="template-card"
            @click="openDetail(tpl.template_id)"
          >
            <div class="card-top">
              <span class="card-icon">{{ CATEGORY_ICON[tpl.category] || '📝' }}</span>
              <div class="card-badges">
                <span v-if="tpl.is_default" class="badge badge-default">{{ t('aiEditor.prompts.library.default') }}</span>
                <span v-if="tpl.is_system" class="badge badge-system">{{ t('aiEditor.prompts.library.system') }}</span>
              </div>
            </div>
            <div class="card-title">{{ tpl.title }}</div>
            <div class="card-desc">{{ tpl.description }}</div>
            <div class="card-meta">
              <span class="badge badge-category">
                {{ t('aiEditor.prompts.library.categories.' + tpl.category) }}
              </span>
              <span class="badge badge-style">
                {{ t('aiEditor.prompts.library.styles.' + tpl.style) }}
              </span>
            </div>
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  listPromptTemplates,
  getPromptTemplate,
  updatePromptTemplate,
  deletePromptTemplate,
  type PromptTemplateListItem,
  type PromptTemplateDetail,
} from '@/infrastructure/api/clients/panel/admin/ai/prompts-library.api'

const { t } = useI18n()

// ============================================================================
// State — Browse
// ============================================================================

const templates = ref<PromptTemplateListItem[]>([])
const isLoading = ref(false)
const loadError = ref(false)
const searchQuery = ref('')
const activeCategory = ref<string>('all')

const CATEGORY_ICON: Record<string, string> = {
  theory: '📖',
  lesson: '📝',
  quiz: '❓',
  flashcard: '🃏',
  tutor: '🧑‍🏫',
  summary: '📋',
  exam: '🎓',
}

const ALL_CATEGORIES = ['all', 'theory', 'lesson', 'quiz', 'flashcard', 'tutor', 'summary', 'exam']

const categories = computed(() => {
  const present = new Set(templates.value.map(t => t.category))
  return ALL_CATEGORIES.filter(c => c === 'all' || present.has(c))
})

const filteredTemplates = computed(() => {
  let result = templates.value
  if (activeCategory.value !== 'all') {
    result = result.filter(t => t.category === activeCategory.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(t =>
      t.title.toLowerCase().includes(q) ||
      t.description.toLowerCase().includes(q) ||
      t.code.toLowerCase().includes(q)
    )
  }
  return result
})

// ============================================================================
// State — Detail / Edit
// ============================================================================

const selectedTemplate = ref<PromptTemplateDetail | null>(null)
const isEditing = ref(false)
const isSaving = ref(false)
const confirmingDelete = ref(false)

const editForm = reactive({
  title: '',
  description: '',
  system_prompt: '',
  user_prompt_template: '',
  temperature: null as number | null,
  max_tokens: null as number | null,
})

// ============================================================================
// Actions
// ============================================================================

async function loadTemplates() {
  isLoading.value = true
  loadError.value = false
  try {
    templates.value = await listPromptTemplates()
  } catch {
    loadError.value = true
  } finally {
    isLoading.value = false
  }
}

async function openDetail(templateId: string) {
  try {
    selectedTemplate.value = await getPromptTemplate(templateId)
  } catch {
    // stay on browse view
  }
}

function closeDetail() {
  selectedTemplate.value = null
  isEditing.value = false
  confirmingDelete.value = false
}

function startEditing() {
  if (!selectedTemplate.value) return
  editForm.title = selectedTemplate.value.title
  editForm.description = selectedTemplate.value.description
  editForm.system_prompt = selectedTemplate.value.system_prompt
  editForm.user_prompt_template = selectedTemplate.value.user_prompt_template
  editForm.temperature = selectedTemplate.value.temperature
  editForm.max_tokens = selectedTemplate.value.max_tokens
  isEditing.value = true
}

function cancelEditing() {
  isEditing.value = false
}

async function handleSave() {
  if (!selectedTemplate.value) return
  isSaving.value = true
  try {
    const updated = await updatePromptTemplate(selectedTemplate.value.template_id, {
      title: editForm.title,
      description: editForm.description,
      system_prompt: editForm.system_prompt,
      user_prompt_template: editForm.user_prompt_template,
      temperature: editForm.temperature ?? undefined,
      max_tokens: editForm.max_tokens ?? undefined,
    })
    selectedTemplate.value = updated
    isEditing.value = false
    // Refresh list in background
    loadTemplates()
  } catch {
    // keep editing open on failure
  } finally {
    isSaving.value = false
  }
}

async function handleDelete() {
  if (!selectedTemplate.value) return
  try {
    await deletePromptTemplate(selectedTemplate.value.template_id)
    closeDetail()
    loadTemplates()
  } catch {
    confirmingDelete.value = false
  }
}

onMounted(loadTemplates)
</script>

<style scoped>
.prompts-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* ========== Browse: Header ========== */
.catalog-header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.search-input::placeholder { color: var(--color-text-tertiary); }
.search-input:focus { outline: none; border-color: var(--color-primary); }

.category-filters {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.category-btn {
  padding: 0.25rem 0.625rem;
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  background: var(--color-surface-secondary, var(--color-surface));
  color: var(--color-text-secondary);
}

.category-btn:hover { color: var(--color-text-primary); }
.category-btn.active { background: var(--color-primary); color: white; }

/* ========== Browse: Body ========== */
.catalog-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}

.state-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 8rem;
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
}

.state-message.error { color: var(--color-error, #e53e3e); }

.templates-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.625rem;
}

.template-card {
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.template-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.375rem;
}

.card-icon { font-size: 1.125rem; }

.card-badges {
  display: flex;
  gap: 0.25rem;
}

.card-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-desc {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-top: 0.125rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  gap: 0.375rem;
  margin-top: 0.5rem;
}

/* ========== Badges ========== */
.badge {
  font-size: 0.5625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-category {
  background: var(--color-surface-secondary, var(--color-surface));
  color: var(--color-primary);
}

.badge-style {
  background: var(--color-surface-secondary, var(--color-surface));
  color: var(--color-text-secondary);
}

.badge-default {
  background: #ebf8ff;
  color: #2b6cb0;
}

.badge-system {
  background: #fefcbf;
  color: #975a16;
}

/* ========== Detail View ========== */
.detail-view {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.back-btn {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
}

.back-btn:hover { color: var(--color-text-primary); background: var(--color-surface-secondary, var(--color-surface)); }

.detail-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn,
.delete-btn {
  font-size: 0.75rem;
  padding: 0.25rem 0.625rem;
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
  cursor: pointer;
  background: var(--color-surface);
  color: var(--color-text-secondary);
}

.edit-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.delete-btn:hover { border-color: var(--color-error, #e53e3e); color: var(--color-error, #e53e3e); }

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}

.detail-meta { margin-bottom: 1rem; }

.detail-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 0.5rem;
}

.meta-row {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}

.detail-desc {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.4;
}

/* ========== Config ========== */
.detail-config {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 0.625rem 0.75rem;
  background: var(--color-surface-secondary, var(--color-surface));
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.config-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.config-value {
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  font-weight: 500;
}

/* ========== Prompt Sections ========== */
.prompt-section { margin-bottom: 1rem; }

.section-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  margin: 0 0 0.375rem;
}

.prompt-block {
  padding: 0.75rem;
  background: var(--color-surface-secondary, var(--color-surface));
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--color-text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 16rem;
  overflow-y: auto;
  margin: 0;
}

/* ========== Variables Table ========== */
.variables-table {
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  overflow: hidden;
}

.var-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.var-row:last-child { border-bottom: none; }

.var-name {
  font-weight: 600;
  color: var(--color-primary);
  font-family: monospace;
  min-width: 6rem;
}

.var-desc {
  flex: 1;
  color: var(--color-text-secondary);
}

.var-required {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--color-text-tertiary);
}

.var-required.required { color: var(--color-error, #e53e3e); }

/* ========== Edit Mode ========== */
.edit-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  font-family: inherit;
}

.edit-input:focus { outline: none; border-color: var(--color-primary); }

.edit-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.edit-desc { margin-bottom: 0.5rem; resize: vertical; }

.edit-prompt {
  font-family: monospace;
  font-size: 0.75rem;
  line-height: 1.5;
  resize: vertical;
}

.edit-small {
  width: 6rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.edit-actions {
  display: flex;
  gap: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.btn-save {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  background: var(--color-primary);
  color: white;
  font-weight: 600;
  font-size: 0.8125rem;
  cursor: pointer;
}

.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-save:hover:not(:disabled) { opacity: 0.9; }

/* ========== Confirm Banner ========== */
.confirm-banner {
  padding: 0.75rem;
  background: #fff5f5;
  border-bottom: 1px solid var(--color-error, #e53e3e);
}

.confirm-banner p {
  font-size: 0.8125rem;
  color: var(--color-error, #e53e3e);
  margin: 0 0 0.5rem;
}

.confirm-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-danger {
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  border: none;
  background: var(--color-error, #e53e3e);
  color: white;
  font-weight: 600;
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-cancel {
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: 0.75rem;
  cursor: pointer;
}
</style>
