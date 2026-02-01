<template>
  <div class="px-6 py-6 space-y-6">
    <h2 class="text-lg font-medium text-gray-900">Lesson bearbeiten</h2>

    <div v-if="lesson">
      <!-- Lesson Title -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Titel</label>
        <input
          v-model="localLesson.title"
          type="text"
          @blur="updateLesson"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        />
      </div>

      <!-- Lesson Type -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Typ</label>
        <select
          v-model="localLesson.lesson_type"
          @change="updateLesson"
          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
        >
          <option value="text">Text</option>
          <option value="video">Video</option>
          <option value="quiz">Quiz</option>
          <option value="ai">KI-Lesson</option>
        </select>
      </div>

      <!-- Content Editor based on type -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">Inhalt</label>

        <!-- Text Lesson -->
        <div v-if="localLesson.lesson_type === 'text'">
          <textarea
            v-model="localLesson.content.text"
            rows="12"
            @blur="updateLessonContent"
            placeholder="Lesson-Inhalt (Markdown unterstützt)..."
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm font-mono"
          ></textarea>
        </div>

        <!-- Video Lesson -->
        <div v-else-if="localLesson.lesson_type === 'video'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Video-URL</label>
            <input
              v-model="localLesson.content.video_url"
              type="url"
              @blur="updateLessonContent"
              placeholder="https://..."
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Plattform</label>
            <select
              v-model="localLesson.content.video_type"
              @change="updateLessonContent"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="youtube">YouTube</option>
              <option value="vimeo">Vimeo</option>
              <option value="direct">Direkt</option>
            </select>
          </div>
        </div>

        <!-- Quiz Lesson -->
        <div v-else-if="localLesson.lesson_type === 'quiz'">
          <p class="text-sm text-gray-500">Quiz-Builder (Platzhalter für F6-Integration)</p>
        </div>

        <!-- AI Lesson -->
        <div v-else-if="localLesson.lesson_type === 'ai'">
          <p class="text-sm text-gray-500">KI-Lesson Konfiguration (Platzhalter)</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCourseEditorStore } from '@/application/stores/courseEditor.store'

const editorStore = useCourseEditorStore()

const lesson = computed(() => editorStore.currentLesson)

const localLesson = ref<any>({
  title: '',
  lesson_type: 'text',
  content: { text: '', video_url: '', video_type: 'youtube' },
})

watch(
  lesson,
  (newLesson) => {
    if (newLesson) {
      localLesson.value = {
        ...newLesson,
        content: newLesson.content || { text: '', video_url: '', video_type: 'youtube' },
      }
    }
  },
  { immediate: true, deep: true }
)

const updateLesson = async () => {
  if (!lesson.value) return

  await editorStore.updateLessonMeta(lesson.value.lesson_id, {
    title: localLesson.value.title,
    lesson_type: localLesson.value.lesson_type,
  })
}

const updateLessonContent = async () => {
  if (!lesson.value) return

  await editorStore.updateLessonContent(lesson.value.lesson_id, localLesson.value.content)
}
</script>
