/**
 * LessonActivitiesSection.vue
 *
 * Manages learning method activities assigned to a specific lesson.
 * Shows list of activities with add/delete, grouped LM type selector.
 */

<script setup lang="ts">
import { ref, computed, toRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLessonActivities } from '../composables'
import type { LessonActivity } from '../composables'
import ActivityEditorAccordion from '../activity-editors/ActivityEditorAccordion.vue'

const props = defineProps<{
  lessonId: string | null
}>()

const { t } = useI18n()

const { activities, loading, addActivity: apiAddActivity, removeActivity: apiRemoveActivity, updateActivityLocal } = useLessonActivities(toRef(props, 'lessonId'))
const expandedActivityId = ref<string | null>(null)

const toggleExpand = (id: string) => {
  expandedActivityId.value = expandedActivityId.value === id ? null : id
}

const onActivitySaved = (updated: LessonActivity) => {
  updateActivityLocal(updated)
}
const showAddForm = ref(false)
const newActivityType = ref<number>(0)
const newActivityTitle = ref('')

// LM groups for the selector (12 methods in 3 groups)
const lmGroups = computed(() => [
  {
    label: t('panel.manualEditor.activities.groupA'),
    methods: [
      { type: 0, name: t('learningMethods.lm00.name') },
      { type: 1, name: t('learningMethods.lm01.name') },
      { type: 2, name: t('learningMethods.lm02.name') },
      { type: 3, name: t('learningMethods.lm03.name') },
      { type: 4, name: t('learningMethods.lm04.name') },
    ]
  },
  {
    label: t('panel.manualEditor.activities.groupB'),
    methods: [
      { type: 5, name: t('learningMethods.lm05.name') },
      { type: 6, name: t('learningMethods.lm06.name') },
      { type: 7, name: t('learningMethods.lm07.name') },
      { type: 8, name: t('learningMethods.lm08.name') },
    ]
  },
  {
    label: t('panel.manualEditor.activities.groupC'),
    methods: [
      { type: 9, name: t('learningMethods.lm09.name') },
      { type: 10, name: t('learningMethods.lm10.name') },
      { type: 11, name: t('learningMethods.lm11.name') },
    ]
  }
])

const addActivity = async () => {
  if (!props.lessonId || !newActivityTitle.value.trim()) return
  try {
    await apiAddActivity(newActivityType.value, newActivityTitle.value.trim())
    newActivityTitle.value = ''
    showAddForm.value = false
  } catch (e) {
    console.error('Failed to create activity:', e)
  }
}

const removeActivity = async (activityId: string, title: string) => {
  if (!confirm(t('panel.manualEditor.activities.confirmDelete', { title }))) return
  try {
    await apiRemoveActivity(activityId)
  } catch (e) {
    console.error('Failed to delete activity:', e)
  }
}

const getMethodName = (methodType: number): string => {
  return t(`learningMethods.lm${String(methodType).padStart(2, '0')}.name`)
}
</script>

<template>
  <div class="activities-section">
    <label class="section-label">{{ $t('panel.manualEditor.activities.title') }}</label>

    <!-- Loading -->
    <div v-if="loading" class="activities-loading">...</div>

    <!-- Activity list -->
    <div v-else-if="activities.length > 0" class="activities-list">
      <div
        v-for="activity in activities"
        :key="activity.method_id"
        class="activity-wrapper"
      >
        <div
          class="activity-item"
          :class="{ 'activity-item--expanded': expandedActivityId === activity.method_id }"
          @click="toggleExpand(activity.method_id)"
        >
          <div class="activity-info">
            <span class="activity-chevron" :class="{ 'activity-chevron--open': expandedActivityId === activity.method_id }">&#x25B6;</span>
            <span class="activity-type-badge">LM{{ String(activity.method_type).padStart(2, '0') }}</span>
            <span class="activity-title">{{ activity.title }}</span>
            <span class="activity-method-name">{{ getMethodName(activity.method_type) }}</span>
          </div>
          <button
            class="activity-delete-btn"
            @click.stop="removeActivity(activity.method_id, activity.title)"
          >&times;</button>
        </div>
        <ActivityEditorAccordion
          v-if="expandedActivityId === activity.method_id"
          :activity="activity"
          @saved="onActivitySaved"
        />
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="activities-empty">
      <p>{{ $t('panel.manualEditor.activities.empty') }}</p>
      <p class="activities-empty-hint">{{ $t('panel.manualEditor.activities.emptyHint') }}</p>
    </div>

    <!-- Add activity form -->
    <div v-if="showAddForm" class="add-activity-form">
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
      v-else
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

.activity-wrapper {
  display: flex;
  flex-direction: column;
}

.activity-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  cursor: pointer;
  transition: background-color 0.15s;
}

.activity-item:hover {
  background: color-mix(in srgb, var(--color-accent) 5%, var(--color-surface));
}

.activity-item--expanded {
  border-radius: 4px 4px 0 0;
  border-bottom-color: transparent;
  background: color-mix(in srgb, var(--color-accent) 8%, var(--color-surface));
}

.activity-chevron {
  font-size: 8px;
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
}

.activity-chevron--open {
  transform: rotate(90deg);
}

.activity-info {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
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
