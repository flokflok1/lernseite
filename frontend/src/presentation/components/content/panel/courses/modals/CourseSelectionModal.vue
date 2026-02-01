<template>
  <Modal
    :show="show"
    :title="$t('panel.courseEditor.selectCourse')"
    size="lg"
    @close="$emit('close')"
  >
    <template #default>
      <!-- Search Bar -->
      <div class="mb-6">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="$t('panel.courseEditor.searchPlaceholder')"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <span class="absolute right-3 top-2.5 text-gray-400">🔍</span>
        </div>
      </div>

      <!-- Create New Course Button -->
      <div class="mb-6">
        <button
          @click="handleCreateNew"
          class="w-full px-4 py-3 bg-green-50 border-2 border-green-200 text-green-700 rounded-lg hover:bg-green-100 transition-colors font-semibold"
        >
          ➕ {{ $t('panel.courseEditor.createNewCourse') }}
        </button>
      </div>

      <!-- Divider -->
      <div class="relative mb-6">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-300"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-2 bg-white text-gray-500">{{
            $t('panel.courseEditor.existingCourses', 'Existing Courses')
          }}</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex flex-col justify-center items-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mb-3"></div>
        <p class="text-gray-600">{{ $t('common.loading') }}</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-8">
        <p class="text-red-600 font-medium">{{ error }}</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredCourses.length === 0" class="text-center py-8">
        <p class="text-gray-500 mb-2">{{
          $t('panel.courseEditor.noCourses')
        }}</p>
        <p class="text-sm text-gray-400">{{
          $t('panel.courseEditor.noCoursesDescription')
        }}</p>
      </div>

      <!-- Course List -->
      <div v-else class="space-y-3 max-h-96 overflow-y-auto">
        <div
          v-for="course in filteredCourses"
          :key="course.course_id"
          class="course-item p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-900">{{ course.title }}</h3>
              <p class="text-sm text-gray-500 mt-1">
                📚 {{ course.category }}
                <span class="mx-1">·</span>
                <span :class="{
                  'text-green-600': course.status === 'published',
                  'text-yellow-600': course.status === 'draft',
                  'text-gray-600': course.status === 'archived'
                }">
                  {{ course.status }}
                </span>
              </p>
            </div>
          </div>

          <div class="flex gap-2">
            <button
              @click="handleOpenCourse(course, 'ai')"
              :disabled="isOpening"
              class="flex-1 px-3 py-2 bg-indigo-50 border border-indigo-200 text-indigo-700 rounded hover:bg-indigo-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              <span v-if="!isOpening">🤖 {{ $t('panel.courseEditor.openWithAI') }}</span>
              <span v-else>⏳ {{ $t('common.loading') }}</span>
            </button>
            <button
              @click="handleOpenCourse(course, 'manual')"
              :disabled="isOpening"
              class="flex-1 px-3 py-2 bg-blue-50 border border-blue-200 text-blue-700 rounded hover:bg-blue-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
            >
              <span v-if="!isOpening">✏️ {{ $t('panel.courseEditor.openWithManual') }}</span>
              <span v-else>⏳ {{ $t('common.loading') }}</span>
            </button>
          </div>
        </div>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/window.store'
import Modal from '@/presentation/components/shared/ui/Modal.vue'
import * as courseApi from '@/application/services/api/content'

interface Course {
  course_id: number | string
  title: string
  category: string
  status: 'draft' | 'published' | 'archived'
  updated_at: string
  is_published?: boolean
}

interface Props {
  show: boolean
}

interface Emits {
  (e: 'close'): void
  (e: 'courseOpened', courseId: string | number, editorType: 'ai' | 'manual'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()
const windowStore = useWindowStore()

const searchQuery = ref('')
const courses = ref<Course[]>([])
const isLoading = ref(false)
const isOpening = ref(false)
const error = ref<string | null>(null)

const filteredCourses = computed(() => {
  if (!searchQuery.value) return courses.value
  const query = searchQuery.value.toLowerCase()
  return courses.value.filter(c =>
    c.title.toLowerCase().includes(query) ||
    c.category.toLowerCase().includes(query)
  )
})

onMounted(async () => {
  await loadCourses()
})

async function loadCourses() {
  isLoading.value = true
  error.value = null

  try {
    // Fetch courses created by current user (creator/teacher/admin)
    const myCourses = await courseApi.getMyCourses(true) // include_archived = true

    // Map API response to local Course interface
    courses.value = myCourses.map(course => ({
      course_id: course.course_id,
      title: course.title,
      category: course.category || 'Uncategorized',
      status: course.is_published ? 'published' : 'draft',
      updated_at: course.updated_at || course.created_at,
      is_published: course.is_published
    }))
  } catch (err) {
    console.error('Failed to load courses:', err)
    error.value = t('panel.courseEditor.loadError', 'Failed to load courses. Please try again.')
    // Fallback to empty list on error
    courses.value = []
  } finally {
    isLoading.value = false
  }
}

function handleCreateNew() {
  // Prompt for course title
  const title = window.prompt(t('panel.courseEditor.enterCourseName', 'Enter course name:'))
  if (!title || title.trim().length === 0) return

  isOpening.value = true

  // TODO: Call API to create new course
  // const newCourse = await courseApi.createCourse({ title, status: 'draft' })

  // For now, use AI editor with empty course
  windowStore.openWindow({
    type: 'admin-ai-studio',
    title: `AI Editor: ${title}`,
    icon: '🤖',
    payload: {
      courseId: 'new',
      courseTitle: title,
      editorMode: 'course',
      isNewCourse: true
    },
    size: { width: 1400, height: 900 }
  })

  emit('courseOpened', 'new', 'ai')
  emit('close')
}

function handleOpenCourse(course: Course, editorType: 'ai' | 'manual') {
  isOpening.value = true

  try {
    if (editorType === 'ai') {
      windowStore.openWindow({
        type: 'admin-ai-studio',
        title: `AI Editor: ${course.title}`,
        icon: '🤖',
        payload: {
          courseId: course.course_id,
          courseTitle: course.title,
          editorMode: 'course',
          isNewCourse: false
        },
        size: { width: 1400, height: 900 }
      })
    } else {
      windowStore.openWindow({
        type: 'admin-course-editor',
        title: `Manual Editor: ${course.title}`,
        icon: '📝',
        payload: {
          courseId: course.course_id,
          courseTitle: course.title
        },
        size: { width: 1200, height: 800 }
      })
    }

    emit('courseOpened', course.course_id, editorType)
    emit('close')
  } finally {
    isOpening.value = false
  }
}
</script>

<style scoped>
.course-item {
  transition: all 0.2s ease;
}

.course-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
