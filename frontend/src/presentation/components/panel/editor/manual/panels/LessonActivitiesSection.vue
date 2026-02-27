/**
 * LessonActivitiesSection.vue
 *
 * Manages learning method activities assigned to a specific lesson.
 * Shows list of activities with add/delete, grouped LM type selector.
 * Each activity opens in a FloatingWindow for editing.
 */

<script setup lang="ts">
import { ref, computed, toRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLessonActivities, useConfirmDialog } from '../composables'
import type { LessonActivity } from '../composables'
import { useWindowStore, type LsxWindow } from '@/application/stores/modules/ui/window.store'
import { useActivitySyncStore } from '@/application/stores/modules/content/activitySync.store'
import InlineErrorBanner from './InlineErrorBanner.vue'

const props = defineProps<{
  lessonId: string | number | null
}>()

const { t } = useI18n()
const { confirm: confirmDialog } = useConfirmDialog()
const windowStore = useWindowStore()
const activitySyncStore = useActivitySyncStore()

const { activities, loading, error: activitiesError, clearError: clearActivitiesError, addActivity: apiAddActivity, removeActivity: apiRemoveActivity, updateActivityLocal } = useLessonActivities(toRef(props, 'lessonId'))

const errorMessage = ref<string | null>(null)

const clearAllErrors = () => {
  clearActivitiesError()
  errorMessage.value = null
}

// Sync saves from floating windows back to the list
watch(() => activitySyncStore.lastSaved, (saved) => {
  if (saved && Number(saved.lesson_id) === props.lessonId) {
    updateActivityLocal(saved)
  }
})

const openActivityWindow = (activity: LessonActivity) => {
  // Check if a window for this activity is already open -> focus it
  const existing = windowStore.panels.find(
    (p: LsxWindow) => p.type === 'activity-editor' && ((p.payload as { activity?: LessonActivity })?.activity?.method_id === activity.method_id)
  )
  if (existing) {
    windowStore.focusWindow(existing.id)
    return
  }

  windowStore.openWindow({
    type: 'activity-editor',
    title: `${lmName(activity.method_type)}: ${activity.title}`,
    payload: { activity },
    size: { width: 700, height: 560 },
  })
}

const showAddForm = ref(false)
const newActivityType = ref<number>(0)
const newActivityTitle = ref('')

/**
 * Resolve localized LM name. Depends on keys from content.json:
 * `lesson.methodExecution.methods.lm00` ... `lm11`
 * (not from manual-editor.json — cross-locale bundle dependency)
 */
const lmName = (id: number): string => {
  return t(`lesson.methodExecution.methods.lm${String(id).padStart(2, '0')}`)
}

const lmGroups = computed(() => [
  {
    label: t('panel.manualEditor.activities.groupA'),
    methods: [0, 1, 2, 3, 4].map(id => ({ type: id, name: lmName(id) }))
  },
  {
    label: t('panel.manualEditor.activities.groupB'),
    methods: [5, 6, 7, 8].map(id => ({ type: id, name: lmName(id) }))
  },
  {
    label: t('panel.manualEditor.activities.groupC'),
    methods: [9, 10, 11].map(id => ({ type: id, name: lmName(id) }))
  }
])

const addActivity = async () => {
  if (!props.lessonId || !newActivityTitle.value.trim()) return
  errorMessage.value = null
  try {
    await apiAddActivity(newActivityType.value, newActivityTitle.value.trim())
    newActivityTitle.value = ''
    showAddForm.value = false
  } catch (e) {
    errorMessage.value = e instanceof Error ? e.message : t('panel.manualEditor.activities.addFailed')
  }
}

const removeActivity = async (activityId: string, title: string) => {
  if (!(await confirmDialog(t('panel.manualEditor.activities.confirmDelete', { title })))) return
  errorMessage.value = null
  try {
    await apiRemoveActivity(activityId)
  } catch (e) {
    errorMessage.value = e instanceof Error ? e.message : t('panel.manualEditor.activities.deleteFailed')
  }
}

</script>

<template>
  <div class="activities-section">
    <label class="section-label">{{ $t('panel.manualEditor.activities.title') }}</label>

    <!-- Error banner -->
    <InlineErrorBanner
      :message="activitiesError || errorMessage"
      @dismiss="clearAllErrors"
    />

    <!-- No lesson selected -->
    <div v-if="!lessonId" class="activities-empty">
      <p>{{ $t('panel.manualEditor.activities.noLessonSelected') }}</p>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="activities-loading">...</div>

    <!-- Activity list -->
    <div v-else-if="activities.length > 0" class="activities-list">
      <div
        v-for="activity in activities"
        :key="activity.method_id"
        class="activity-item"
      >
        <div class="activity-info" @click="openActivityWindow(activity)">
          <span class="activity-type-badge">{{ lmName(activity.method_type) }}</span>
          <span class="activity-title">{{ activity.title }}</span>
          <span class="activity-method-name">{{ lmName(activity.method_type) }}</span>
        </div>
        <div class="activity-actions">
          <button
            class="activity-edit-btn"
            :title="$t('panel.manualEditor.activityEditor.openEditor')"
            :aria-label="$t('panel.manualEditor.activityEditor.openEditor')"
            @click="openActivityWindow(activity)"
          >&#x270E;</button>
          <button
            class="activity-delete-btn"
            :aria-label="$t('panel.manualEditor.activities.deleteActivity')"
            @click="removeActivity(activity.method_id, activity.title)"
          >&times;</button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="activities-empty">
      <p>{{ $t('panel.manualEditor.activities.empty') }}</p>
      <p class="activities-empty-hint">{{ $t('panel.manualEditor.activities.emptyHint') }}</p>
    </div>

    <!-- Add activity form -->
    <div v-if="lessonId && showAddForm" class="add-activity-form">
      <select v-model="newActivityType" class="form-select">
        <optgroup v-for="group in lmGroups" :key="group.label" :label="group.label">
          <option v-for="m in group.methods" :key="m.type" :value="m.type">
            {{ m.name }}
          </option>
        </optgroup>
      </select>
      <input
        v-model="newActivityTitle"
        type="text"
        class="form-input"
        :placeholder="$t('panel.manualEditor.activities.activityTitle')"
        @keydown.enter="addActivity"
      />
      <div class="add-activity-actions">
        <button class="btn-confirm" @click="addActivity">+</button>
        <button class="btn-cancel" @click="showAddForm = false">&times;</button>
      </div>
    </div>

    <button
      v-else-if="lessonId"
      class="btn-add-activity"
      @click="showAddForm = true"
    >
      + {{ $t('panel.manualEditor.activities.add') }}
    </button>
  </div>
</template>

<style scoped>
.activities-section {
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.activity-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  transition: background-color 0.15s;
}

.activity-item:hover {
  background: color-mix(in srgb, var(--color-accent) 5%, var(--color-surface));
}

.activity-info {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  cursor: pointer;
  flex: 1;
}

.activity-type-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  background: color-mix(in srgb, var(--color-accent) 15%, transparent);
  color: var(--color-accent);
  white-space: nowrap;
}

.activity-title {
  font-size: 13px;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-method-name {
  font-size: 11px;
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

.activity-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  flex-shrink: 0;
}

.activity-edit-btn {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  font-size: 14px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.activity-edit-btn:hover {
  color: var(--color-accent);
}

.activity-delete-btn {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  font-size: 16px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
}

.activity-delete-btn:hover {
  color: var(--color-error);
}

.activities-empty {
  text-align: center;
  padding: 8px 0;
}

.activities-empty p {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.activities-empty-hint {
  font-size: 11px;
}

.add-activity-form {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 6px;
}

.form-select,
.form-input {
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.15s;
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent) 10%, transparent);
}

.add-activity-actions {
  display: flex;
  gap: 4px;
}

.btn-confirm,
.btn-cancel {
  padding: 4px 12px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.btn-confirm:hover {
  background: color-mix(in srgb, var(--color-success) 15%, transparent);
  border-color: var(--color-success);
  color: var(--color-success);
}

.btn-cancel:hover {
  background: color-mix(in srgb, var(--color-error) 15%, transparent);
  border-color: var(--color-error);
  color: var(--color-error);
}

.btn-add-activity {
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

.btn-add-activity:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.activities-loading {
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 12px;
  padding: 8px 0;
}

</style>
