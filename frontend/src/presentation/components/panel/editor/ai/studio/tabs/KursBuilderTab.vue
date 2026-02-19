<!--
  KursBuilderTab.vue

  KI-Kurs-Builder Tab für chat-basiertes Authoring.
  Uses sub-components from ./kurs-builder/
  Business logic extracted to composables/useKursBuilderTab.ts

  Layout (2 Spalten):
  - Links (60%): Chat + Workflow Panel
  - Rechts (40%): Kursstruktur + Materialien
-->

<template>
  <div class="kurs-builder-tab">
    <!-- Header mit Session-Status -->
    <KursBuilderHeader
      :course="course"
      :session="session"
      :creating-session="creatingSession"
      :finalizing="finalizing"
      :has-changes="hasChanges"
      :draft-stats="draftStats"
      @create-session="createSession"
      @finalize-session="finalizeSession"
    />

    <!-- No Course Selected -->
    <div v-if="!course" class="empty-state">
      <span class="empty-icon">📚</span>
      <p class="empty-title">{{ $t('kursBuilder.noCourseSelected') }}</p>
      <p class="empty-hint">{{ $t('kursBuilder.selectCourseHint') }}</p>
    </div>

    <!-- Main Content (2 Spalten) -->
    <div v-else class="builder-content">
      <!-- Left: Chat Column (60%) -->
      <div class="chat-column">
        <WorkflowPanel
          v-if="selectedContext"
          :context="selectedContext"
          :selected-file-count="selectedFileIds.length"
          :is-analyzing="isAnalyzing"
          :is-loading-theories="isLoadingTheories"
          :is-generating-theory="isGeneratingTheory"
          :is-loading-l-m-suggestions="lmSuggestionsLoading"
          :is-loading-actions="contextActionsLoading"
          :theories="chapterTheories"
          :explanations="lessonExplanations"
          :lm-suggestions="lmSuggestions"
          :context-actions="contextActions"
          :selected-theory-id="selectedTheoryId"
          :disabled="chatLoading"
          @close="clearContext"
          @analyze="analyzeSelectedContext"
          @generate-theory="generateTheory"
          @open-theory="openTheoryInTutor"
          @open-explanation="openExplanationInTutor"
          @create-lm="createLMFromSuggestion"
          @action="sendContextAction"
        />

        <ConfirmationPanel
          v-if="pendingAction"
          :pending-action="pendingAction"
          :is-loading="confirmLoading"
          @confirm="confirmPendingAction"
          @modify="modifyPendingAction"
          @reject="rejectPendingAction"
        />

        <ChatPanel
          :messages="chatMessages"
          :is-loading="chatLoading"
          :quick-actions="quickActions"
          :actions-loading="actionsLoading"
          :selected-file-count="selectedFileIds.length"
          :has-context="!!selectedContext"
          :show-quick-actions="!pendingAction"
          v-model="inputMessage"
          v-model:mode="selectedMode"
          @send="sendMessage"
          @quick-action="sendQuickAction"
        />
      </div>

      <!-- Right: Structure + Materials (40%) -->
      <div class="right-column">
        <StructurePanel
          :chapters="draftStructure?.chapters || []"
          :analyzing-lesson-id="analyzingLessonId"
          :selected-file-count="selectedFileIds.length"
          @select-chapter="selectChapterForChat"
          @preview-chapter="openChapterPreview"
          @edit-chapter="editChapter"
          @delete-chapter="deleteChapter"
          @select-lesson="selectLessonForChat"
          @preview-lesson="openLessonPreview"
          @edit-lesson="editLesson"
          @delete-lesson="deleteLesson"
          @analyze-lesson="analyzeLessonWithFiles"
        />

        <MaterialsPanel
          :files="sessionFiles"
          v-model:selected-ids="selectedFileIds"
          @upload="triggerFileUpload"
          @preview="openFilePreview"
          @clear-selection="clearFileSelection"
        />
      </div>
    </div>

    <!-- Hidden file input -->
    <input
      ref="materialFileInput"
      type="file"
      multiple
      accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md"
      style="display: none"
      @change="handleMaterialUpload"
    />

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      <span>{{ error }}</span>
      <button @click="error = null">x</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, toRef } from 'vue'
import {
  ChatPanel,
  ConfirmationPanel,
  MaterialsPanel,
  StructurePanel,
  WorkflowPanel
} from '../../authoring/course-builder'
import KursBuilderHeader from './KursBuilderHeader.vue'
import { useKursBuilderTab } from './composables/useKursBuilderTab'
import type { Course } from './composables/useKursBuilderTab'

const props = defineProps<{ course: Course | null }>()

const builder = useKursBuilderTab(toRef(props, 'course'))

const {
  session, chatMessages, draftStructure, sessionFiles, selectedFileIds,
  materialFileInput, analyzingLessonId, isAnalyzing, isGeneratingTheory,
  inputMessage, selectedMode, creatingSession, chatLoading, finalizing, error,
  actionsLoading, selectedContext, contextActionsLoading, contextActions,
  lmSuggestions, lmSuggestionsLoading, pendingAction, confirmLoading,
  quickActions, selectedTheoryId,
  chapterTheories, lessonExplanations, isLoadingTheories, hasChanges, draftStats,
  createSession, finalizeSession, sendMessage, sendQuickAction,
  selectChapterForChat, selectLessonForChat, clearContext, sendContextAction,
  analyzeSelectedContext, analyzeLessonWithFiles, generateTheory, createLMFromSuggestion,
  confirmPendingAction, rejectPendingAction, modifyPendingAction,
  openChapterPreview, openLessonPreview, editChapter, editLesson, deleteChapter, deleteLesson,
  clearFileSelection, openFilePreview, triggerFileUpload, handleMaterialUpload,
  openTheoryInTutor, openExplanationInTutor
} = builder

defineExpose({
  sessionMeta: builder.sessionMeta,
  draftStats,
  createSession,
  hasSession: builder.hasSession
})
</script>

<style scoped>
.kurs-builder-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { font-size: 1.125rem; font-weight: 500; margin: 0; }
.empty-hint { font-size: 0.875rem; opacity: 0.7; margin: 0.25rem 0 0; }

.builder-content {
  flex: 1;
  display: flex;
  gap: 1rem;
  padding: 1rem;
  overflow: hidden;
}

.chat-column {
  flex: 6;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.right-column {
  flex: 4;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-width: 300px;
}

.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-top: 1px solid #ef4444;
  color: #ef4444;
  font-size: 0.875rem;
}

.error-banner button {
  background: none;
  border: none;
  color: currentColor;
  font-size: 1.25rem;
  cursor: pointer;
}
</style>
