<!--
  AI Studio Content Area

  Renders the sidebar (session/chapter tree) and the active tab content.
  Extracted from AiStudioMain to keep each file under 500 LOC.
-->

<template>
  <div class="content-area">
    <!-- Sidebar (all tabs except Global) -->
    <template v-if="activeTab !== 'global'">
      <!-- Builder Tab: Session & Verlauf Sidebar -->
      <CourseAuthoringSidebar
        v-if="activeTab === 'builder'"
        :session-meta="kursBuilderRef?.sessionMeta"
        :activity-log="kursBuilderRef?.activityLog || []"
        :stats="kursBuilderRef?.draftStats"
      />

      <!-- Other Tabs: Chapter Tree Sidebar -->
      <CourseStructureSidebar
        v-else
        :course="selectedCourse"
        :chapters="chapters"
        :selected-chapter-id="selectedChapterId"
        :selected-lesson-id="selectedLessonId"
        :expanded-chapters="expandedChapters"
        :is-loading="isLoading"
        @select-chapter="$emit('select-chapter', $event)"
        @select-lesson="$emit('select-lesson', $event.lessonId, $event.chapterId)"
        @toggle-chapter="$emit('toggle-chapter', $event)"
        @create-chapter="$emit('create-chapter')"
      />
    </template>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Kurs-Builder Tab -->
      <KursBuilderTab
        v-if="activeTab === 'builder'"
        ref="kursBuilderRef"
        :course="selectedCourse"
      />

      <!-- Tutor Tab -->
      <TutorTab
        v-if="activeTab === 'tutor'"
        :lesson="selectedLesson"
        :chapter="selectedChapter"
        :course="selectedCourse"
        @back-to-chapter="$emit('clear-lesson')"
      />

      <!-- Lernmethoden Tab -->
      <LernmethodenTab
        v-if="activeTab === 'methods'"
        :course="selectedCourse"
        :chapter="selectedChapter"
        :lesson="selectedLesson"
        :chapters="chapters"
      />

      <!-- Prüfungen Tab -->
      <ExamsTab
        v-if="activeTab === 'exams'"
        :course="selectedCourse"
      />

      <!-- Features Tab -->
      <SystemFeaturesTab
        v-if="activeTab === 'features'"
        :course="selectedCourse"
      />

      <!-- Prompts Tab -->
      <PromptsTab
        v-if="activeTab === 'prompts'"
        :course="selectedCourse"
      />

      <!-- Analytics Tab -->
      <AnalyticsTab
        v-if="activeTab === 'analytics'"
        :course="selectedCourse"
      />

      <!-- Einstellungen Tab -->
      <SettingsTab
        v-if="activeTab === 'settings'"
        :course="selectedCourse"
      />

      <!-- Globale Einstellungen Tab -->
      <GlobalSettingsTab
        v-if="activeTab === 'global'"
      />

      <!-- Chat Panel (overlays content when expanded) -->
      <ChatPanel
        v-if="chatExpanded"
        :course="selectedCourse"
        @close="$emit('close-chat')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * AiStudioContentArea - Sidebar + tab content for AI Studio
 */
import { ref } from 'vue'

import { CourseStructureSidebar } from './views'
import KursBuilderTab from './tabs/KursBuilderTab.vue'
import TutorTab from './tabs/TutorTab.vue'
import LernmethodenTab from './tabs/LernmethodenTab.vue'
import ExamsTab from './tabs/ExamsTab.vue'
import SystemFeaturesTab from './tabs/SystemFeaturesTab.vue'
import PromptsTab from './tabs/PromptsTab.vue'
import AnalyticsTab from './tabs/AnalyticsTab.vue'
import SettingsTab from './tabs/SettingsTab.vue'
import GlobalSettingsTab from './tabs/GlobalSettingsTab.vue'
import ChatPanel from './tabs/ChatPanel.vue'
import CourseAuthoringSidebar from '../authoring/course-builder/CourseAuthoringSidebar.vue'

interface Props {
  activeTab: string
  chatExpanded: boolean
  selectedCourse: any | null
  selectedChapter: any | null
  selectedLesson: any | null
  selectedChapterId: string | null
  selectedLessonId: string | null
  chapters: any[]
  expandedChapters: Set<string>
  isLoading: boolean
}

defineProps<Props>()

defineEmits<{
  'select-chapter': [chapterId: string]
  'select-lesson': [payload: { lessonId: string; chapterId: string }]
  'toggle-chapter': [chapterId: string]
  'create-chapter': []
  'clear-lesson': []
  'close-chat': []
}>()

const kursBuilderRef = ref<InstanceType<typeof KursBuilderTab> | null>(null)

defineExpose({
  kursBuilderRef
})
</script>

<style scoped>
.content-area {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  position: relative;
}
</style>
