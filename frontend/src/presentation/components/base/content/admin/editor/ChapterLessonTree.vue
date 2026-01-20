<!--
  Chapter Lesson Tree Component
  Displays course structure with chapters and lessons
  Refactored: modules → chapters (2025-11-27)
-->
<template>
  <div class="bg-white shadow sm:rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <h3 class="text-base font-semibold leading-6 text-gray-900 mb-4">Kursstruktur</h3>

      <!-- Add Chapter Button -->
      <button
        @click="handleAddChapter"
        class="w-full mb-4 inline-flex justify-center items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
      >
        <svg class="-ml-0.5 mr-2 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
        </svg>
        Kapitel hinzufügen
      </button>

      <!-- Chapters List -->
      <div class="space-y-2">
        <div
          v-for="chapter in editorStore.sortedChapters"
          :key="chapter.chapter_id"
          class="border rounded-md"
        >
          <!-- Chapter Header -->
          <div
            @click="editorStore.selectChapter(chapter.chapter_id)"
            :class="[
              'px-3 py-2 cursor-pointer flex items-center justify-between',
              editorStore.selectedChapterId === chapter.chapter_id ? 'bg-blue-50' : 'hover:bg-gray-50',
            ]"
          >
            <div class="flex items-center space-x-2">
              <svg class="h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
              </svg>
              <span class="text-sm font-medium text-gray-900">{{ chapter.title }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click.stop="handleRemoveChapter(chapter.chapter_id)"
                class="text-red-600 hover:text-red-800"
              >
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Lessons List -->
          <div
            v-if="editorStore.selectedChapterId === chapter.chapter_id"
            class="px-3 py-2 bg-gray-50 border-t space-y-1"
          >
            <button
              @click="handleAddLesson(chapter.chapter_id)"
              class="w-full text-left px-2 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded"
            >
              + Lektion hinzufügen
            </button>

            <div
              v-for="lesson in editorStore.sortedLessons(chapter.chapter_id)"
              :key="lesson.lesson_id"
              @click="editorStore.selectLesson(chapter.chapter_id, lesson.lesson_id)"
              :class="[
                'px-2 py-1 text-sm cursor-pointer rounded flex items-center justify-between',
                editorStore.selectedLessonId === lesson.lesson_id
                  ? 'bg-blue-100 text-blue-900'
                  : 'hover:bg-gray-100',
              ]"
            >
              <span>{{ lesson.title }}</span>
              <button
                @click.stop="handleRemoveLesson(chapter.chapter_id, lesson.lesson_id)"
                class="text-red-600 hover:text-red-800"
              >
                <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useCourseEditorStore } from '@/application/stores/modules/content'

const editorStore = useCourseEditorStore()

const handleAddChapter = async () => {
  const title = prompt('Kapitel-Titel:')
  if (!title) return

  await editorStore.addChapter(title)
}

const handleRemoveChapter = async (chapterId: string) => {
  if (!confirm('Kapitel wirklich löschen?')) return

  await editorStore.removeChapter(chapterId)
}

const handleAddLesson = async (chapterId: string) => {
  const title = prompt('Lektion-Titel:')
  if (!title) return

  await editorStore.addLesson(chapterId, title)
}

const handleRemoveLesson = async (chapterId: string, lessonId: number) => {
  if (!confirm('Lektion wirklich löschen?')) return

  await editorStore.removeLesson(chapterId, lessonId)
}
</script>
