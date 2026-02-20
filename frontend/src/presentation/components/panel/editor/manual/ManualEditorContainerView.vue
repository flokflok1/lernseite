/**
 * ManualEditorContainerView.vue
 *
 * Main orchestrator for the manual course editor.
 * Left sidebar: always-visible structure tree.
 * Right area: tab-based panels (content, course info, media, preview, settings, AI).
 * Top bar: auto-save status, save button.
 */

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
import { useAutoSave, useEditorKeyboard } from '@/presentation/components/panel/editor/manual/composables'
import type { EditorTab } from '@/presentation/components/panel/editor/manual/types'
import StructureTreePanel from '@/presentation/components/panel/editor/manual/panels/StructureTreePanel.vue'
import ContentEditPanel from '@/presentation/components/panel/editor/manual/panels/ContentEditPanel.vue'
import CourseInfoPanel from '@/presentation/components/panel/editor/manual/panels/CourseInfoPanel.vue'
import MediaUploadPanel from '@/presentation/components/panel/editor/manual/panels/MediaUploadPanel.vue'
import LessonSettingsPanel from '@/presentation/components/panel/editor/manual/panels/LessonSettingsPanel.vue'
import PreviewPanel from '@/presentation/components/panel/editor/manual/panels/PreviewPanel.vue'
import CourseSelector from '@/presentation/components/panel/editor/manual/panels/CourseSelector.vue'
import { TheoryGenerationContainer } from '@/presentation/components/panel/editor/ai/content-generation'
import { ExplanationGenerationContainer } from '@/presentation/components/panel/editor/ai/explanation-generation'

interface Props {
  projectId: string
  courseId?: string | null
}

const props = defineProps<Props>()

const { t } = useI18n()
const store = useCourseEditorStore()
const authStore = useAuthStore()
const { saveStatus, lastSaved, triggerSave } = useAutoSave()

const isAdmin = computed(() => authStore.userHierarchyLevel >= 750)

const activeTab = ref<EditorTab>('content')
const isInitialized = ref(false)
const selectedCourseId = ref<number | null>(props.courseId ? Number(props.courseId) : null)

// Keyboard shortcuts
useEditorKeyboard({
  onSave: () => triggerSave(),
})

// All tabs always visible
const tabs = computed<Array<{ key: EditorTab; label: string }>>(() => [
  { key: 'content', label: t('panel.manualEditor.tabs.content') },
  { key: 'course-info', label: t('panel.manualEditor.tabs.courseInfo') },
  { key: 'media', label: t('panel.manualEditor.tabs.media') },
  { key: 'preview', label: t('panel.manualEditor.tabs.preview') },
  { key: 'lesson-settings', label: t('panel.manualEditor.tabs.lessonSettings') },
  { key: 'theory', label: t('course-editor.theory.container.title') },
  { key: 'explanation', label: t('course-editor.explanation.container.title') },
])

// Initialize: load course if ID provided, otherwise show selector
onMounted(async () => {
  if (selectedCourseId.value) {
    await store.loadCourseForEdit(selectedCourseId.value)
  }
  isInitialized.value = true
})

const handleSelectCourse = async (courseId: number) => {
  selectedCourseId.value = courseId
  await store.loadCourseForEdit(courseId)
}

const handleCreateCourse = async () => {
  await store.createNewCourse()
  if (store.currentCourse) {
    selectedCourseId.value = store.currentCourse.course_id
  }
}

const handleBackToList = () => {
  selectedCourseId.value = null
  store.clearEditor()
}

const handleTogglePublish = async () => {
  if (!store.currentCourse) return
  if (store.currentCourse.is_published) {
    await store.unpublishCourse()
  } else {
    await store.publishCourse()
  }
}

onBeforeUnmount(() => {
  store.clearEditor()
})

const handleSave = async (): Promise<void> => {
  await store.saveAllChanges()
}

const formatSaveTime = (date: Date | null): string => {
  if (!date) return ''
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="manual-editor-container">
    <!-- Loading state -->
    <div v-if="!isInitialized" class="loading-state">
      <p>{{ $t('common.loading') }}...</p>
    </div>

    <!-- Course selector (no course selected) -->
    <CourseSelector
      v-else-if="!selectedCourseId"
      @select="handleSelectCourse"
      @create="handleCreateCourse"
    />

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
            {{ $t(`panel.manualEditor.toolbar.${saveStatus}`) }}
            <span v-if="lastSaved" class="save-time">
              {{ formatSaveTime(lastSaved) }}
            </span>
          </span>
          <button class="save-btn" @click="handleSave" :disabled="store.saving">
            {{ store.saving ? $t('panel.manualEditor.toolbar.saving') : $t('panel.manualEditor.toolbar.save') }}
          </button>
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
          <ContentEditPanel v-if="activeTab === 'content'" />

          <CourseInfoPanel v-else-if="activeTab === 'course-info'" />

          <MediaUploadPanel v-else-if="activeTab === 'media'" />

          <PreviewPanel v-else-if="activeTab === 'preview'" />

          <LessonSettingsPanel v-else-if="activeTab === 'lesson-settings'" />

          <!-- Theory generation (AI) -->
          <div v-else-if="activeTab === 'theory'" class="ai-tab-content">
            <TheoryGenerationContainer
              :chapter="store.selectedChapterId ? { chapter_id: store.selectedChapterId } : null"
              :course="store.currentCourse ? { course_id: String(store.currentCourse.course_id) } : null"
              @generated="store.markDirty()"
              @deleted="store.markDirty()"
            />
          </div>

          <!-- Explanation generation (AI) -->
          <div v-else-if="activeTab === 'explanation'" class="ai-tab-content">
            <ExplanationGenerationContainer
              :lesson="store.currentLesson ? { lesson_id: store.currentLesson.lesson_id, title: store.currentLesson.title } : null"
              :course="store.currentCourse ? { course_id: String(store.currentCourse.course_id), title: store.currentCourse.title } : null"
              @generated="store.markDirty()"
              @deleted="store.markDirty()"
            />
          </div>
        </div>
      </div>
    </div>
    </template>
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

.btn-publish:hover {
  filter: brightness(0.9);
}

.btn-publish:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-unpublish {
  background: var(--color-warning);
}

.save-status {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.save-status.saved {
  color: var(--color-success);
}

.save-status.saving {
  color: var(--color-warning);
}

.save-status.unsaved {
  color: var(--color-error);
}

.save-time {
  margin-left: 4px;
  color: var(--color-text-tertiary);
}

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

.save-btn:hover {
  background: var(--color-accent-hover, var(--color-accent));
  filter: brightness(0.9);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading */
.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

/* Main layout */
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

/* Tab bar */
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

.tab-btn:hover {
  color: var(--color-text-primary);
  background: var(--color-surface-secondary);
  filter: brightness(0.95);
}

.tab-btn.active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
  font-weight: 500;
}

/* Tab content */
.tab-content {
  flex: 1;
  overflow: hidden;
}

.ai-tab-content {
  height: 100%;
  overflow: auto;
}

/* Responsive */
@media (max-width: 900px) {
  .sidebar {
    width: 180px;
  }
}
</style>
