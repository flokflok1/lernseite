/**
 * TheorySheetsSection.vue
 *
 * Manages theory sheets for a chapter or lesson.
 * Accordion-style inline CRUD: list, add, expand-to-edit, delete with confirmation.
 */

<script setup lang="ts">
import { ref, computed, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTheorySheets } from '../composables/useTheorySheets'
import { useConfirmDialog } from '../composables'
import InlineErrorBanner from './InlineErrorBanner.vue'

interface Props {
  chapterId?: string | null
  lessonId?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  chapterId: null,
  lessonId: null,
})

const { t } = useI18n()
const { confirm: confirmDialog } = useConfirmDialog()

const parentType = computed<'chapter' | 'lesson'>(() => props.chapterId ? 'chapter' : 'lesson')
const parentId = computed(() => props.chapterId ?? props.lessonId ?? null)

const {
  theories,
  loading,
  error,
  clearError,
  addTheory,
  updateTheory,
  removeTheory,
} = useTheorySheets(parentId, parentType)

// Accordion: which theory is expanded for editing
const expandedId = ref<string | null>(null)

const toggleExpand = (theoryId: string) => {
  expandedId.value = expandedId.value === theoryId ? null : theoryId
}

// Inline edit state (per expanded item)
const editTitle = ref('')
const editContent = ref('')
const saving = ref(false)

const startEdit = (theory: { theory_id: string; title: string; content: string }) => {
  editTitle.value = theory.title
  editContent.value = theory.content
  expandedId.value = theory.theory_id
}

const saveEdit = async (theoryId: string) => {
  if (!editTitle.value.trim() || !editContent.value.trim()) return
  saving.value = true
  await updateTheory(theoryId, {
    title: editTitle.value.trim(),
    content: editContent.value.trim(),
  })
  saving.value = false
}

const handleDelete = async (theoryId: string, title: string) => {
  if (!(await confirmDialog(t('panel.manualEditor.knowledge.confirmDelete', { title })))) return
  await removeTheory(theoryId)
  if (expandedId.value === theoryId) expandedId.value = null
}

// Add new sheet
const showAddForm = ref(false)
const newTitle = ref('')
const newContent = ref('')
const adding = ref(false)

const handleAdd = async () => {
  if (!newTitle.value.trim() || !newContent.value.trim()) return
  adding.value = true
  const result = await addTheory(newTitle.value.trim(), newContent.value.trim())
  adding.value = false
  if (result) {
    newTitle.value = ''
    newContent.value = ''
    showAddForm.value = false
  }
}
</script>

<template>
  <div class="theory-section">
    <!-- Error banner -->
    <InlineErrorBanner :message="error" @dismiss="clearError" />

    <!-- No parent selected -->
    <div v-if="!parentId" class="theory-empty">
      <p>{{ $t('panel.manualEditor.knowledge.noParentSelected') }}</p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="theory-loading">...</div>

    <template v-else>
      <!-- Theory list (accordion) -->
      <div v-if="theories.length > 0" class="theory-list">
        <div
          v-for="theory in theories"
          :key="theory.theory_id"
          class="theory-item"
          :class="{ expanded: expandedId === theory.theory_id }"
        >
          <!-- Collapsed header -->
          <div class="theory-header" @click="startEdit(theory)">
            <span class="theory-expand-icon">{{ expandedId === theory.theory_id ? '\u25BE' : '\u25B8' }}</span>
            <span class="theory-title">{{ theory.title }}</span>
            <button
              class="theory-delete-btn"
              :aria-label="$t('panel.manualEditor.knowledge.deleteSheet')"
              @click.stop="handleDelete(theory.theory_id, theory.title)"
            >&times;</button>
          </div>

          <!-- Expanded editor -->
          <div v-if="expandedId === theory.theory_id" class="theory-editor">
            <label class="field-label">{{ $t('panel.manualEditor.knowledge.sheetTitle') }}</label>
            <input
              v-model="editTitle"
              type="text"
              class="form-input"
              :placeholder="$t('panel.manualEditor.knowledge.sheetTitlePlaceholder')"
            />

            <label class="field-label">{{ $t('panel.manualEditor.knowledge.sheetContent') }}</label>
            <textarea
              v-model="editContent"
              class="form-textarea"
              :placeholder="$t('panel.manualEditor.knowledge.sheetContentPlaceholder')"
              rows="8"
            />

            <div class="theory-editor-actions">
              <button
                class="btn-save"
                :disabled="saving || !editTitle.trim() || !editContent.trim()"
                @click="saveEdit(theory.theory_id)"
              >
                {{ saving ? $t('panel.manualEditor.toolbar.saving') : $t('panel.manualEditor.knowledge.save') }}
              </button>
              <button class="btn-collapse" @click="expandedId = null">
                {{ $t('panel.manualEditor.content.cancel') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-else class="theory-empty">
        <p>{{ $t('panel.manualEditor.knowledge.empty') }}</p>
      </div>

      <!-- Add form -->
      <div v-if="showAddForm" class="theory-add-form">
        <label class="field-label">{{ $t('panel.manualEditor.knowledge.sheetTitle') }}</label>
        <input
          v-model="newTitle"
          type="text"
          class="form-input"
          :placeholder="$t('panel.manualEditor.knowledge.sheetTitlePlaceholder')"
        />

        <label class="field-label">{{ $t('panel.manualEditor.knowledge.sheetContent') }}</label>
        <textarea
          v-model="newContent"
          class="form-textarea"
          :placeholder="$t('panel.manualEditor.knowledge.sheetContentPlaceholder')"
          rows="6"
        />

        <div class="theory-editor-actions">
          <button
            class="btn-save"
            :disabled="adding || !newTitle.trim() || !newContent.trim()"
            @click="handleAdd"
          >
            {{ adding ? $t('panel.manualEditor.toolbar.saving') : $t('panel.manualEditor.knowledge.addSheet') }}
          </button>
          <button class="btn-collapse" @click="showAddForm = false; newTitle = ''; newContent = ''">
            {{ $t('panel.manualEditor.content.cancel') }}
          </button>
        </div>
      </div>

      <!-- Add button -->
      <button
        v-else-if="parentId"
        class="btn-add-theory"
        @click="showAddForm = true"
      >
        + {{ $t('panel.manualEditor.knowledge.addSheet') }}
      </button>
    </template>
  </div>
</template>

<style scoped>
.theory-section {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.theory-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.theory-item {
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  overflow: hidden;
}

.theory-item.expanded {
  border-color: var(--color-accent);
}

.theory-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.theory-header:hover {
  background: color-mix(in srgb, var(--color-accent) 5%, var(--color-surface));
}

.theory-expand-icon {
  font-size: 12px;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
  width: 12px;
}

.theory-title {
  font-size: 13px;
  color: var(--color-text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.theory-delete-btn {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  flex-shrink: 0;
}

.theory-delete-btn:hover {
  color: var(--color-error);
}

.theory-editor {
  padding: 10px 12px;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.form-input,
.form-textarea {
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 13px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color 0.15s;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 10%, transparent);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.theory-editor-actions {
  display: flex;
  gap: 6px;
}

.btn-save {
  padding: 6px 14px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.btn-save:hover { filter: brightness(0.9); }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-collapse {
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 12px;
}

.btn-collapse:hover {
  border-color: var(--color-text-tertiary);
  color: var(--color-text-primary);
}

.theory-empty {
  text-align: center;
  padding: 12px 0;
}

.theory-empty p {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.theory-loading {
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 12px;
  padding: 8px 0;
}

.theory-add-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
  padding: 12px;
  border: 1px dashed var(--color-border);
  border-radius: 4px;
}

.btn-add-theory {
  width: 100%;
  padding: 6px;
  border: 1px dashed var(--color-border);
  border-radius: 4px;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 12px;
  cursor: pointer;
  margin-top: 6px;
}

.btn-add-theory:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}
</style>
