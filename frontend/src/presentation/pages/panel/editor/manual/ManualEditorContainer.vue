/**
 * ManualEditorContainer.vue
 *
 * Main orchestrator for the manual course editor.
 * Left sidebar: always-visible structure tree.
 * Right area: tab-based panels (content, course info, AI theory/explanation).
 * Top bar: editor mode selector, auto-save status, save button.
 */

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'
import { useEditorMode, useAutoSave, useEditorKeyboard } from '@/presentation/components/panel/editor/manual/composables'
import type { EditorTab } from '@/presentation/components/panel/editor/manual/types'
import StructureTreePanel from '@/presentation/components/panel/editor/manual/panels/StructureTreePanel.vue'
import ContentEditPanel from '@/presentation/components/panel/editor/manual/panels/ContentEditPanel.vue'
import CourseInfoPanel from '@/presentation/components/panel/editor/manual/panels/CourseInfoPanel.vue'
import MediaUploadPanel from '@/presentation/components/panel/editor/manual/panels/MediaUploadPanel.vue'
import LessonSettingsPanel from '@/presentation/components/panel/editor/manual/panels/LessonSettingsPanel.vue'
import PreviewPanel from '@/presentation/components/panel/editor/manual/panels/PreviewPanel.vue'
import { TheoryGenerationContainer } from '@/presentation/components/panel/editor/content-generation'
import { ExplanationGenerationContainer } from '@/presentation/components/panel/editor/explanation-generation'

interface Props {
  projectId: string
  courseId?: string | null
}

const props = defineProps<Props>()

const { t } = useI18n()
const store = useCourseEditorStore()
const { currentMode, modeConfig, setMode } = useEditorMode()
const { saveStatus, lastSaved, triggerSave } = useAutoSave()

const activeTab = ref<EditorTab>('content')
const isInitialized = ref(false)

// Keyboard shortcuts
useEditorKeyboard({
  onSave: () => triggerSave(),
})

// Available tabs based on editor mode
const tabs = computed(() => {
  const base: Array<{ key: EditorTab; label: string }> = [
    { key: 'content', label: t('panel.manualEditor.tabs.content') },
    { key: 'course-info', label: t('panel.manualEditor.tabs.courseInfo') },
  ]

  if (modeConfig.value.showMediaUpload) {
    base.push({ key: 'media', label: t('panel.manualEditor.tabs.media') })
  }
  if (modeConfig.value.showPreview) {
    base.push({ key: 'preview', label: t('panel.manualEditor.tabs.preview') })
  }
  if (modeConfig.value.showLessonSettings) {
    base.push({ key: 'lesson-settings', label: t('panel.manualEditor.tabs.lessonSettings') })
  }

  // AI tabs always available
  base.push(
    { key: 'theory', label: t('course-editor.theory.container.title') },
    { key: 'explanation', label: t('course-editor.explanation.container.title') },
  )

  return base
})

// Reset active tab when switching to a mode that hides current tab
watch(tabs, (newTabs) => {
  const tabKeys = newTabs.map(t => t.key)
  if (!tabKeys.includes(activeTab.value)) {
    activeTab.value = 'content'
  }
})

// Initialize store with course data
onMounted(async () => {
  if (props.courseId) {
    const numericId = Number(props.courseId)
    if (!isNaN(numericId)) {
      await store.loadCourseForEdit(numericId)
    }
  } else {
    await store.createNewCourse()
  }
  isInitialized.value = true
})

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
    <!-- Top Bar -->
    <div class="editor-topbar">
      <!-- Mode selector -->
      <div class="mode-selector">
        <span class="mode-label">{{ $t('panel.manualEditor.mode.label') }}:</span>
        <button
          v-for="mode in (['beginner', 'advanced', 'expert'] as const)"
          :key="mode"
          :class="['mode-btn', { active: currentMode === mode }]"
          @click="setMode(mode)"
        >
          {{ $t(`panel.manualEditor.mode.${mode}`) }}
        </button>
      </div>

      <!-- Save status -->
      <div class="save-area">
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

    <!-- Loading state -->
    <div v-if="!isInitialized" class="loading-state">
      <p>{{ $t('common.loading') }}...</p>
    </div>

    <!-- Main layout -->
    <div v-else class="editor-body">
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
          <!-- Content editor -->
          <ContentEditPanel
            v-if="activeTab === 'content'"
            :mode-config="modeConfig"
          />

          <!-- Course info -->
          <CourseInfoPanel
            v-else-if="activeTab === 'course-info'"
            :mode-config="modeConfig"
          />

          <!-- Media upload (advanced/expert) -->
          <MediaUploadPanel
            v-else-if="activeTab === 'media'"
          />

          <!-- Preview (advanced/expert) -->
          <PreviewPanel
            v-else-if="activeTab === 'preview'"
          />

          <!-- Lesson settings (advanced/expert) -->
          <LessonSettingsPanel
            v-else-if="activeTab === 'lesson-settings'"
          />

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
  </div>
</template>

<style scoped>
.manual-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8f9fa;
  overflow: hidden;
}

/* Top Bar */
.editor-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.mode-selector {
  display: flex;
  align-items: center;
  gap: 6px;
}

.mode-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.mode-btn {
  padding: 4px 10px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s;
}

.mode-btn:hover {
  background: #f0f0f0;
}

.mode-btn.active {
  background: #2196f3;
  color: white;
  border-color: #1976d2;
}

.save-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.save-status {
  font-size: 12px;
  color: #999;
}

.save-status.saved {
  color: #4caf50;
}

.save-status.saving {
  color: #ff9800;
}

.save-status.unsaved {
  color: #f44336;
}

.save-time {
  margin-left: 4px;
  color: #bbb;
}

.save-btn {
  padding: 6px 14px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
}

.save-btn:hover {
  background: #1976d2;
}

.save-btn:disabled {
  background: #90caf9;
  cursor: not-allowed;
}

/* Loading */
.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

/* Main layout */
.editor-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  gap: 1px;
  background: #e0e0e0;
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: white;
  overflow: hidden;
  position: relative;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: white;
}

/* Tab bar */
.tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 1px solid #e0e0e0;
  background: #fafafa;
  flex-shrink: 0;
}

.tab-btn {
  padding: 10px 16px;
  border: none;
  border-bottom: 2px solid transparent;
  background: none;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  transition: all 0.15s;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #333;
  background: #f0f0f0;
}

.tab-btn.active {
  color: #2196f3;
  border-bottom-color: #2196f3;
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

  .mode-selector {
    display: none;
  }
}
</style>
