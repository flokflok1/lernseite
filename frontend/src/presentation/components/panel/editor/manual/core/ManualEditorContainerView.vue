<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
import { useAutoSave, useEditorKeyboard, useConfirmDialog } from '@/presentation/components/panel/editor/manual/composables'
import type { AutoSaveStatus } from '@/presentation/components/panel/editor/manual/composables'
import type { EditorTab } from '@/presentation/components/panel/editor/manual/types'
import StructureTreePanel from '@/presentation/components/panel/editor/manual/panels/structure/StructureTreePanel.vue'
import ContentEditPanel from '@/presentation/components/panel/editor/manual/panels/ContentEditPanel.vue'
import CourseInfoPanel from '@/presentation/components/panel/editor/manual/panels/course/CourseInfoPanel.vue'
import MediaUploadPanel from '@/presentation/components/panel/editor/manual/panels/MediaUploadPanel.vue'
import LessonSettingsPanel from '@/presentation/components/panel/editor/manual/panels/lesson/LessonSettingsPanel.vue'
import PreviewPanel from '@/presentation/components/panel/editor/manual/panels/PreviewPanel.vue'
import LessonActivitiesSection from '@/presentation/components/panel/editor/manual/panels/lesson/LessonActivitiesSection.vue'
import CourseSelector from '@/presentation/components/panel/editor/manual/panels/course/CourseSelector.vue'
import InlineErrorBanner from '@/presentation/components/panel/editor/manual/panels/InlineErrorBanner.vue'
import ConfirmDialog from '@/presentation/components/panel/editor/manual/panels/ConfirmDialog.vue'
import TheorySheetsSection from '@/presentation/components/panel/editor/manual/panels/lesson/TheorySheetsSection.vue'

interface Props {
  projectId: string
  courseId?: string | null
}

const props = defineProps<Props>()

const { t } = useI18n()
const store = useCourseEditorStore()
const authStore = useAuthStore()
const { saveStatus, lastSaved, saveError, triggerSave, dismissError } = useAutoSave()
const { confirm: confirmDialog } = useConfirmDialog()

const isAdmin = computed(() => authStore.userHierarchyLevel >= 750)

const activeTab = ref<EditorTab>('lesson')
const isInitialized = ref(false)
const selectedCourseId = ref<number | null>(props.courseId ? Number(props.courseId) : null)

// Keyboard shortcuts
useEditorKeyboard({
  onSave: () => triggerSave(),
})

// All tabs always visible
const tabs = computed<Array<{ key: EditorTab; label: string }>>(() => [
  { key: 'lesson', label: t('panel.manualEditor.tabs.lesson') },
  { key: 'activities', label: t('panel.manualEditor.tabs.activities') },
  { key: 'course-info', label: t('panel.manualEditor.tabs.courseInfo') },
  { key: 'media', label: t('panel.manualEditor.tabs.media') },
  { key: 'preview', label: t('panel.manualEditor.tabs.preview') },
])

// Initialize: load course if ID provided, otherwise show selector
onMounted(async () => {
  if (selectedCourseId.value) {
    await store.loadCourseForEdit(selectedCourseId.value)
  }
  isInitialized.value = true
})

const loadError = ref<string | null>(null)

const handleSelectCourse = async (courseId: number) => {
  selectedCourseId.value = courseId
  loadError.value = null
  try {
    await store.loadCourseForEdit(courseId)
  } catch {
    loadError.value = t('panel.manualEditor.errors.loadFailed')
    selectedCourseId.value = null
  }
}

const handleCreateCourse = async () => {
  loadError.value = null
  try {
    await store.createNewCourse({ title: t('panel.manualEditor.courseSelector.defaultTitle') })
    if (store.currentCourse) {
      selectedCourseId.value = store.currentCourse.course_id
    }
  } catch {
    loadError.value = t('panel.manualEditor.errors.createFailed')
    selectedCourseId.value = null
  }
}

const handleBackToList = async () => {
  if (store.isDirty && !(await confirmDialog(t('panel.manualEditor.toolbar.confirmDiscard')))) return
  selectedCourseId.value = null
  store.clearEditor()
}

const handleTogglePublish = async () => {
  if (!store.currentCourse) return
  try {
    if (store.currentCourse.is_published) {
      await store.unpublishCourse()
    } else {
      await store.publishCourse()
    }
  } catch {
    // Error already surfaced via store.error
  }
}

onBeforeUnmount(() => {
  store.clearEditor()
})

const handleSave = async (): Promise<void> => {
  dismissError()
  await triggerSave()
}

const formatSaveTime = (date: Date | null): string => {
  if (!date) return ''
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const saveStatusLabel = computed(() => {
  const labels: Record<AutoSaveStatus, string> = {
    saved: t('panel.manualEditor.toolbar.saved'),
    saving: t('panel.manualEditor.toolbar.saving'),
    unsaved: t('panel.manualEditor.toolbar.unsaved'),
    error: t('panel.manualEditor.toolbar.error'),
  }
  return labels[saveStatus.value]
})
</script>

<template>
  <div class="manual-editor-container">
    <!-- Loading state -->
    <div v-if="!isInitialized" class="loading-state">
      <p>{{ $t('common.loading') }}...</p>
    </div>

    <!-- Course selector (no course selected) -->
    <template v-else-if="!selectedCourseId">
      <InlineErrorBanner
        v-if="loadError"
        :message="loadError"
        class="selector-error"
        @dismiss="loadError = null"
      />
      <CourseSelector
        @select="handleSelectCourse"
        @create="handleCreateCourse"
      />
    </template>

    <!-- Editor layout (course selected) -->
    <template v-else>
      <!-- Top Bar -->
      <div class="editor-topbar">
        <div class="topbar-left">
          <button class="btn-back" @click="handleBackToList" :title="$t('panel.manualEditor.courseSelector.backToList')">
            &larr;
          </button>
          <div class="topbar-title">
            {{ store.currentCourse?.title || $t('panel.manualEditor.courseInfo.courseName') }}
          </div>
        </div>

        <!-- Publish status + action -->
        <div class="topbar-actions">
          <span
            v-if="store.currentCourse"
            class="publish-badge"
            :class="store.currentCourse.is_published ? 'badge-published' : 'badge-draft'"
          >
            {{ store.currentCourse.is_published
              ? $t('panel.manualEditor.publish.published')
              : $t('panel.manualEditor.publish.draft') }}
          </span>
          <button
            v-if="isAdmin && store.currentCourse"
            class="btn-publish"
            :class="store.currentCourse.is_published ? 'btn-unpublish' : ''"
            @click="handleTogglePublish"
            :disabled="store.saving || (!store.currentCourse.is_published && !store.canPublishCourse)"
          >
            {{ store.currentCourse.is_published
              ? $t('panel.manualEditor.publish.unpublish')
              : $t('panel.manualEditor.publish.publish') }}
          </button>

          <!-- Save status -->
          <span class="save-status" :class="saveStatus">
            {{ saveStatusLabel }}
            <span v-if="saveStatus === 'saved' && lastSaved" class="save-time">
              {{ formatSaveTime(lastSaved) }}
            </span>
          </span>
          <button class="save-btn" @click="handleSave" :disabled="store.saving">
            {{ store.saving ? $t('panel.manualEditor.toolbar.saving') : $t('panel.manualEditor.toolbar.save') }}
          </button>

          <!-- Error banner (appears below toolbar) -->
          <InlineErrorBanner
            :message="saveError"
            :hint="$t('panel.manualEditor.toolbar.retryHint')"
            class="save-error-dropdown"
            @dismiss="dismissError"
          />
        </div>
      </div>

      <!-- Main layout -->
      <div class="editor-body">
      <!-- Left sidebar: Structure tree -->
      <div class="sidebar">
        <StructureTreePanel />
      </div>

      <!-- Right area: Tabs + content -->
      <div class="main-area">
        <!-- Tab navigation -->
        <div class="tab-bar">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            :class="['tab-btn', { active: activeTab === tab.key }]"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab content -->
        <div class="tab-content">
          <!-- Lesson tab: Settings → Editor → Knowledge -->
          <div v-if="activeTab === 'lesson'" class="lesson-tab">
            <LessonSettingsPanel />
            <div class="content-editor-section">
              <ContentEditPanel />
            </div>
            <details class="knowledge-section">
              <summary>{{ $t('panel.manualEditor.knowledge.chapterTheory') }}</summary>
              <TheorySheetsSection
                :chapter-id="store.selectedChapterId ? String(store.selectedChapterId) : null"
              />
            </details>
            <details class="knowledge-section">
              <summary>{{ $t('panel.manualEditor.knowledge.lessonTheory') }}</summary>
              <TheorySheetsSection
                :lesson-id="store.currentLesson?.lesson_id ? String(store.currentLesson.lesson_id) : null"
              />
            </details>
          </div>

          <!-- Activities tab -->
          <LessonActivitiesSection
            v-else-if="activeTab === 'activities'"
            :lesson-id="store.currentLesson?.lesson_id ?? null"
          />

          <CourseInfoPanel v-else-if="activeTab === 'course-info'" />

          <MediaUploadPanel v-else-if="activeTab === 'media'" />

          <PreviewPanel v-else-if="activeTab === 'preview'" />
        </div>
      </div>
    </div>
    </template>

    <!-- Global confirm dialog (singleton, renders via Teleport) -->
    <ConfirmDialog />
  </div>
</template>

<style scoped>
.manual-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
  overflow: hidden;
}

/* Top Bar */
.editor-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.btn-back {
  padding: 4px 8px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
  transition: all 0.15s;
}

.btn-back:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.topbar-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  flex-wrap: wrap;
}

.publish-badge {
  padding: 3px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.badge-draft {
  background: color-mix(in srgb, var(--color-text-tertiary) 15%, transparent);
  color: var(--color-text-secondary);
}

.badge-published {
  background: color-mix(in srgb, var(--color-success) 15%, transparent);
  color: var(--color-success);
}

.btn-publish {
  padding: 5px 12px;
  background: var(--color-success);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: filter 0.15s;
}

.btn-publish:hover { filter: brightness(0.9); }
.btn-publish:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-unpublish { background: var(--color-warning); }

.save-status { font-size: 12px; color: var(--color-text-tertiary); }
.save-status.saved { color: var(--color-success); }
.save-status.saving { color: var(--color-warning); }
.save-status.unsaved { color: var(--color-error); }

.save-status.error {
  color: var(--color-error);
  font-weight: 600;
}

/* Positioning override: dropdown below toolbar */
.save-error-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 10;
  white-space: nowrap;
  border-radius: 0 0 6px 6px;
}

.save-time { margin-left: 4px; color: var(--color-text-tertiary); }

.save-btn {
  padding: 6px 14px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.save-btn:hover { background: var(--color-accent-hover, var(--color-accent)); filter: brightness(0.9); }
.save-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

.editor-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  gap: 1px;
  background: var(--color-border);
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: var(--color-surface);
  overflow: hidden;
  position: relative;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--color-surface);
}

.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
  flex-shrink: 0;
  overflow-x: auto;
}

.tab-btn {
  padding: 10px 16px;
  border: none;
  border-bottom: 2px solid transparent;
  background: none;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-secondary);
  transition: all 0.15s;
  white-space: nowrap;
}

.tab-btn:hover { color: var(--color-text-primary); background: var(--color-surface-secondary); filter: brightness(0.95); }
.tab-btn.active { color: var(--color-accent); border-bottom-color: var(--color-accent); font-weight: 500; }

.tab-content { flex: 1; overflow: hidden; }

/* Lesson tab (combined content + settings + knowledge) */
.lesson-tab {
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.content-editor-section {
  flex: 1 0 400px;
  display: flex;
  flex-direction: column;
  min-height: 400px;
}

.knowledge-section {
  flex-shrink: 0;
  border-top: 1px solid var(--color-border);
  margin: 0;
}

.knowledge-section summary {
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  background: var(--color-surface-secondary);
  user-select: none;
}

.knowledge-section summary:hover { color: var(--color-text-primary); }
.knowledge-section[open] summary { border-bottom: 1px solid var(--color-border); }

.selector-error { margin: 8px 16px 0; }
@media (max-width: 900px) { .sidebar { width: 180px; } }
</style>
