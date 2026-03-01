<!--
  CourseTab — Course metadata editor within the Unified AI Editor.
  Loads full course data on mount, auto-saves changes with debounce.
-->
<template>
  <div class="course-tab">
    <div v-if="!courseId" class="course-tab__empty">
      <p>{{ $t('aiEditor.course.selectFirst') }}</p>
    </div>

    <div v-else-if="isLoading" class="course-tab__loading">
      {{ $t('aiEditor.course.loading') }}
    </div>

    <div v-else-if="course" class="course-tab__form">
      <div class="course-tab__header">
        <h3>{{ $t('aiEditor.course.title') }}</h3>
        <span v-if="isSaving" class="save-badge saving">{{ $t('aiEditor.course.saving') }}</span>
        <span v-else-if="saveError" class="save-badge save-error">{{ saveError }}</span>
        <span v-else-if="lastSaved" class="save-badge saved">{{ $t('aiEditor.course.saved') }}</span>
        <div class="course-tab__actions">
          <button
            class="action-btn action-btn--warning"
            :title="$t('aiEditor.course.actions.archive')"
            @click="courseActions.requestAction('archive', course!.course_id as any)"
          >&#128451;</button>
          <button
            class="action-btn action-btn--danger"
            :title="$t('aiEditor.course.actions.trash')"
            @click="courseActions.requestAction('trash', course!.course_id as any)"
          >&times;</button>
        </div>
      </div>

      <ConfirmBanner
        v-if="courseActions.isConfirming.value"
        :message="getConfirmMessage()"
        :confirm-label="getConfirmLabel()"
        :variant="getConfirmVariant()"
        @confirm="handleConfirm"
        @cancel="courseActions.cancelAction()"
      />

      <!-- Title -->
      <div class="field">
        <label>{{ $t('aiEditor.course.fields.title') }}</label>
        <input v-model="course.title" type="text" @input="debouncedSave" />
      </div>

      <!-- Subtitle -->
      <div class="field">
        <label>{{ $t('aiEditor.course.fields.subtitle') }}</label>
        <input v-model="course.subtitle" type="text" @input="debouncedSave" />
      </div>

      <!-- Description -->
      <div class="field">
        <label>{{ $t('aiEditor.course.fields.description') }}</label>
        <textarea v-model="course.description" rows="4" @input="debouncedSave" />
      </div>

      <!-- Category + Subcategory -->
      <div class="field-row">
        <div class="field">
          <label>{{ $t('aiEditor.course.fields.category') }}</label>
          <select v-model="course.category_id" @change="handleCategoryChange">
            <option :value="undefined">—</option>
            <option v-for="cat in rootCategories" :key="cat.category_id" :value="cat.category_id">
              {{ cat.name }}
            </option>
          </select>
        </div>
        <div class="field">
          <label>{{ $t('aiEditor.course.fields.subcategory') }}</label>
          <select v-model="course.subcategory_id" @change="debouncedSave">
            <option :value="undefined">—</option>
            <option v-for="sub in subcategories" :key="sub.category_id" :value="sub.category_id">
              {{ sub.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Level + Language -->
      <div class="field-row">
        <div class="field">
          <label>{{ $t('aiEditor.course.fields.level') }}</label>
          <select v-model="course.level" @change="debouncedSave">
            <option value="beginner">{{ $t('aiEditor.course.levels.beginner') }}</option>
            <option value="intermediate">{{ $t('aiEditor.course.levels.intermediate') }}</option>
            <option value="advanced">{{ $t('aiEditor.course.levels.advanced') }}</option>
            <option value="expert">{{ $t('aiEditor.course.levels.expert') }}</option>
          </select>
        </div>
        <div class="field">
          <label>{{ $t('aiEditor.course.fields.language') }}</label>
          <select v-model="course.language" @change="debouncedSave">
            <option value="de">Deutsch</option>
            <option value="en">English</option>
            <option value="pl">Polski</option>
          </select>
        </div>
      </div>

      <!-- Target Group -->
      <div class="field">
        <label>{{ $t('aiEditor.course.fields.targetGroup') }}</label>
        <input v-model="course.target_group" type="text" @input="debouncedSave" />
      </div>

      <!-- Visibility + Price -->
      <div class="field-row">
        <div class="field">
          <label>{{ $t('aiEditor.course.fields.visibility') }}</label>
          <select v-model="course.visibility" @change="debouncedSave">
            <option value="private">{{ $t('aiEditor.course.visibility.private') }}</option>
            <option value="group_private">{{ $t('aiEditor.course.visibility.groupPrivate') }}</option>
            <option value="class_internal">{{ $t('aiEditor.course.visibility.classInternal') }}</option>
            <option value="company_internal">{{ $t('aiEditor.course.visibility.companyInternal') }}</option>
            <option value="community_public">{{ $t('aiEditor.course.visibility.communityPublic') }}</option>
            <option value="marketplace">{{ $t('aiEditor.course.visibility.marketplace') }}</option>
            <option value="academy">{{ $t('aiEditor.course.visibility.academy') }}</option>
          </select>
        </div>
        <div class="field">
          <label>{{ $t('aiEditor.course.fields.price') }}</label>
          <input v-model.number="course.price" type="number" min="0" step="0.01" @input="debouncedSave" />
        </div>
      </div>

      <!-- Tags -->
      <div class="field">
        <label>{{ $t('aiEditor.course.fields.tags') }}</label>
        <input
          :value="(course.tags || []).join(', ')"
          type="text"
          :placeholder="$t('aiEditor.course.tagsPlaceholder')"
          @change="handleTagsChange"
        />
      </div>

      <!-- Learning Goals -->
      <div class="field">
        <label>{{ $t('aiEditor.course.fields.learningGoals') }}</label>
        <textarea
          :value="(course.learning_goals || []).join('\n')"
          rows="3"
          :placeholder="$t('aiEditor.course.goalsPlaceholder')"
          @change="handleGoalsChange"
        />
      </div>

      <!-- Requirements -->
      <div class="field">
        <label>{{ $t('aiEditor.course.fields.requirements') }}</label>
        <textarea
          :value="(course.requirements || []).join('\n')"
          rows="3"
          :placeholder="$t('aiEditor.course.requirementsPlaceholder')"
          @change="handleRequirementsChange"
        />
      </div>

      <!-- Thumbnail URL -->
      <div class="field">
        <label>{{ $t('aiEditor.course.fields.thumbnail') }}</label>
        <input v-model="course.thumbnail_url" type="text" @input="debouncedSave" />
      </div>

      <!-- Status info (read-only) -->
      <div class="course-tab__status">
        <span>{{ $t('aiEditor.course.fields.published') }}: {{ course.is_published ? '✓' : '✗' }}</span>
        <span>{{ $t('aiEditor.course.fields.draft') }}: {{ course.draft_state ? '✓' : '✗' }}</span>
        <span v-if="course.created_at">{{ $t('aiEditor.course.fields.createdAt') }}: {{ formatDate(course.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, inject, onDeactivated, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { getCourseForEdit, updateCourse } from '@/infrastructure/api/clients/panel/editor'
import { getCategoryTree } from '@/infrastructure/api/clients/panel/editor/courses/categories.api'
import type { EditableCourse, CategoryTreeNode } from '@/infrastructure/api/clients/panel/editor'
import { useCourseActions } from '@/presentation/components/panel/editor/shared/composables'
import ConfirmBanner from '@/presentation/components/panel/editor/shared/ui/ConfirmBanner.vue'

const props = defineProps<{ courseId: string }>()
const emit = defineEmits<{ deleted: [courseId: string] }>()

const { t } = useI18n()
const courseActions = useCourseActions()

const course = ref<EditableCourse | null>(null)
const isLoading = ref(false)
const isSaving = ref(false)
const lastSaved = ref(false)
const saveError = ref<string | null>(null)
const categoryTree = ref<CategoryTreeNode[]>([])

let saveTimeout: ReturnType<typeof setTimeout> | null = null

function clearSaveTimeout() {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
    saveTimeout = null
  }
}

onDeactivated(clearSaveTimeout)
onUnmounted(clearSaveTimeout)

const rootCategories = computed(() => categoryTree.value)

const subcategories = computed(() => {
  if (!course.value?.category_id) return []
  const parent = categoryTree.value.find(c => c.category_id === course.value!.category_id)
  return parent?.children || []
})

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

async function loadCourse(id: string): Promise<void> {
  isLoading.value = true
  lastSaved.value = false
  try {
    course.value = await getCourseForEdit(id as any)
  } catch {
    course.value = null
  } finally {
    isLoading.value = false
  }
}

async function loadCategories(): Promise<void> {
  try {
    const tree = await getCategoryTree(true)
    categoryTree.value = tree.categories
  } catch {
    categoryTree.value = []
  }
}

async function save(): Promise<void> {
  if (!course.value) return
  isSaving.value = true
  lastSaved.value = false
  try {
    await updateCourse(course.value.course_id as any, {
      title: course.value.title,
      subtitle: course.value.subtitle,
      description: course.value.description,
      category_id: course.value.category_id,
      subcategory_id: course.value.subcategory_id,
      level: course.value.level,
      language: course.value.language,
      target_group: course.value.target_group,
      tags: course.value.tags,
      learning_goals: course.value.learning_goals,
      requirements: course.value.requirements,
      visibility: course.value.visibility as any,
      price: course.value.price ?? undefined,
      thumbnail_url: course.value.thumbnail_url,
    })
    saveError.value = null
    lastSaved.value = true
  } catch (e: unknown) {
    console.warn('[CourseTab] Failed to save course:', e)
    saveError.value = t('aiEditor.course.saveFailed')
  } finally {
    isSaving.value = false
  }
}

function getConfirmMessage(): string {
  const title = course.value?.title || ''
  if (courseActions.pendingAction.value === 'archive') {
    return t('aiEditor.course.actions.confirmArchive', { title })
  }
  return t('aiEditor.course.actions.confirmTrash', { title })
}

function getConfirmLabel(): string {
  if (courseActions.pendingAction.value === 'archive') {
    return t('aiEditor.course.actions.archive')
  }
  return t('aiEditor.course.actions.trash')
}

function getConfirmVariant(): 'danger' | 'warning' {
  return courseActions.pendingAction.value === 'archive' ? 'warning' : 'danger'
}

async function handleConfirm(): Promise<void> {
  const action = courseActions.pendingAction.value
  const success = await courseActions.confirmAction()
  if (success && (action === 'trash' || action === 'purge')) {
    emit('deleted', props.courseId)
  }
}

function debouncedSave(): void {
  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = setTimeout(() => save(), 800)
}

function handleCategoryChange(): void {
  if (course.value) course.value.subcategory_id = undefined
  debouncedSave()
}

function handleTagsChange(e: Event): void {
  const val = (e.target as HTMLInputElement).value
  if (course.value) {
    course.value.tags = val.split(',').map(t => t.trim()).filter(Boolean)
    debouncedSave()
  }
}

function handleGoalsChange(e: Event): void {
  const val = (e.target as HTMLTextAreaElement).value
  if (course.value) {
    course.value.learning_goals = val.split('\n').filter(Boolean)
    debouncedSave()
  }
}

function handleRequirementsChange(e: Event): void {
  const val = (e.target as HTMLTextAreaElement).value
  if (course.value) {
    course.value.requirements = val.split('\n').filter(Boolean)
    debouncedSave()
  }
}

// Load course when courseId changes
watch(() => props.courseId, (id) => {
  if (id) loadCourse(id)
  else course.value = null
}, { immediate: true })

// Load categories once
loadCategories()
</script>

<style scoped>
.course-tab {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
}

.course-tab__empty,
.course-tab__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-tertiary);
  font-size: 0.875rem;
}

.course-tab__header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.course-tab__header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  flex: 1;
}

.course-tab__actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.action-btn {
  width: 30px;
  height: 30px;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  transition: all 0.15s;
}

.action-btn--danger:hover {
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
  border-color: var(--color-error);
  color: var(--color-error);
}

.action-btn--warning:hover {
  background: color-mix(in srgb, var(--color-warning) 10%, transparent);
  border-color: var(--color-warning);
  color: var(--color-warning);
}

.save-badge {
  font-size: 0.6875rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 500;
}

.save-badge.saving {
  background: var(--color-warning-subtle, #fef3c7);
  color: var(--color-warning, #d97706);
}

.save-badge.saved {
  background: var(--color-success-subtle, #d1fae5);
  color: var(--color-success, #059669);
}

.save-badge.save-error {
  background: var(--color-danger-subtle, #fee2e2);
  color: var(--color-danger, #dc2626);
}

.field {
  margin-bottom: 0.75rem;
}

.field label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.field input,
.field textarea,
.field select {
  width: 100%;
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 0.8125rem;
  font-family: inherit;
}

.field textarea {
  resize: vertical;
}

.field input:focus,
.field textarea:focus,
.field select:focus {
  outline: none;
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
}

.field-row {
  display: flex;
  gap: 0.75rem;
}

.field-row .field {
  flex: 1;
}

.course-tab__status {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}
</style>
