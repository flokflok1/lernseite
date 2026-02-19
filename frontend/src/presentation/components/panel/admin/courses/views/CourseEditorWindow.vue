<!--
  Admin Course Editor Window Content

  Window content for editing course details, chapters, and settings.
  Features:
  - Course metadata editing (title, description, category, level, etc.)
  - Chapter management overview
  - Quick actions (publish, archive, delete)
  Phase: B24-06 - Admin Desktop OS
  Refactored: modules -> chapters (2025-11-27)
  Refactored: extracted tabs into sub-components (2026-02-18)
-->

<template>
  <div class="admin-course-editor-window h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)] mx-auto mb-3"></div>
        <p class="text-sm text-[var(--color-text-secondary)]">Lade Kursdaten...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 p-6">
      <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fef2f2); border-color: var(--color-error-border, #fecaca);">
        <p style="color: var(--color-error-text, #b91c1c);">{{ error }}</p>
        <button
          @click="loadCourse"
          class="mt-3 px-3 py-1.5 bg-red-600 text-white text-sm rounded hover:bg-red-700"
        >
          Erneut versuchen
        </button>
      </div>
    </div>

    <!-- Course Editor Content -->
    <div v-else-if="course" class="flex-1 flex flex-col overflow-hidden">
      <!-- Tabs -->
      <div class="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div class="flex px-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            ]"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-y-auto">
        <CourseMetadataTab
          v-if="activeTab === 'metadata'"
          :form="form"
          :tags-input="tagsInput"
          :flat-categories="flatCategories"
          :loading-categories="loadingCategories"
          :saving="saving"
          @save="saveCourse"
          @reset="resetForm"
          @update:form="form = $event"
          @update:tags-input="tagsInput = $event"
        />

        <CourseChaptersTab
          v-else-if="activeTab === 'chapters'"
          :chapters="chapters"
          :loading="loadingChapters"
          @create-chapter="openChapterEditor(null)"
          @edit-chapter="openChapterEditor"
          @delete-chapter="deleteChapter"
        />

        <CourseActionsTab
          v-else-if="activeTab === 'actions'"
          :course-status="course.status"
          @publish="publishCourse"
          @unpublish="unpublishCourse"
          @archive="archiveCourse"
          @delete="deleteCourse"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import type { AdminChapter } from '@/infrastructure/api/clients/panel/admin'
import { useCourseEditor } from './composables/useCourseEditor'
import CourseMetadataTab from './components/CourseMetadataTab.vue'
import CourseChaptersTab from './components/CourseChaptersTab.vue'
import CourseActionsTab from './components/CourseActionsTab.vue'

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const windowStore = useWindowStore()

const courseId = computed(() => props.window.payload?.courseId as string)

const {
  course,
  chapters,
  loading,
  loadingChapters,
  loadingCategories,
  error,
  saving,
  activeTab,
  form,
  tagsInput,
  flatCategories,
  tabs,
  loadCourse,
  saveCourse,
  resetForm,
  publishCourse,
  unpublishCourse,
  archiveCourse,
  deleteCourse,
  deleteChapter
} = useCourseEditor({
  courseId: () => courseId.value,
  onClose: () => emit('close'),
  onCourseUpdated: (updatedCourse) => {
    windowStore.updateWindowPayload(props.window.id, {
      course: updatedCourse
    })
  }
})

function openChapterEditor(chapter: AdminChapter | null): void {
  windowStore.openWindow({
    type: 'admin-kapitel-editor',
    title: chapter ? `Kapitel bearbeiten: ${chapter.title}` : 'Neues Kapitel',
    icon: '',
    payload: {
      courseId: courseId.value,
      courseTitle: course.value?.title,
      chapterId: chapter?.chapter_id,
      chapter: chapter
    }
  })
}
</script>
