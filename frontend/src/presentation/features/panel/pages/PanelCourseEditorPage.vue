<template>
  <div class="panel-course-editor-page py-8">
    <!-- Header Section -->
    <div class="max-w-4xl mx-auto mb-12">
      <div class="text-center">
        <div class="text-5xl mb-4">📝</div>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">{{
          $t('panel.courseEditor.pageTitle')
        }}</h1>
        <p class="text-lg text-gray-600">{{
          $t('panel.courseEditor.pageSubtitle')
        }}</p>
      </div>
    </div>

    <!-- Main Action Button -->
    <div class="max-w-4xl mx-auto mb-12">
      <button
        @click="showModal = true"
        class="w-full group relative px-8 py-6 bg-gradient-to-r from-primary-500 to-primary-600 text-white rounded-lg hover:from-primary-600 hover:to-primary-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
      >
        <div class="flex items-center justify-center gap-3">
          <span class="text-3xl">🚀</span>
          <div class="text-left">
            <div class="text-xl font-bold">{{
              $t('panel.courseEditor.openCourseEditor')
            }}</div>
            <div class="text-sm opacity-90">{{
              $t('panel.courseEditor.chooseEditorType', 'Select between AI and Manual editing')
            }}</div>
          </div>
        </div>
      </button>
    </div>

    <!-- Features Grid -->
    <div class="max-w-4xl mx-auto mb-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">{{
        $t('panel.courseEditor.features', 'Features')
      }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- AI Editor Feature -->
        <div class="p-6 bg-gradient-to-br from-indigo-50 to-blue-50 border border-indigo-200 rounded-lg hover:shadow-lg transition-shadow">
          <div class="text-3xl mb-3">🤖</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">{{
            $t('panel.courseEditor.aiEditorFeature', 'AI-Powered Editor')
          }}</h3>
          <ul class="text-sm text-gray-700 space-y-2">
            <li>✓ {{ $t('panel.courseEditor.feature1', 'Upload documents (PDF, DOCX, PPTX, etc.)') }}</li>
            <li>✓ {{ $t('panel.courseEditor.feature2', 'Auto-generate course structure') }}</li>
            <li>✓ {{ $t('panel.courseEditor.feature3', 'AI-powered content generation') }}</li>
            <li>✓ {{ $t('panel.courseEditor.feature4', 'Smart learning method suggestions') }}</li>
          </ul>
        </div>

        <!-- Manual Editor Feature -->
        <div class="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded-lg hover:shadow-lg transition-shadow">
          <div class="text-3xl mb-3">✏️</div>
          <h3 class="text-xl font-bold text-gray-900 mb-2">{{
            $t('panel.courseEditor.manualEditorFeature', 'Manual Editor')
          }}</h3>
          <ul class="text-sm text-gray-700 space-y-2">
            <li>✓ {{ $t('panel.courseEditor.feature5', 'Full control over structure') }}</li>
            <li>✓ {{ $t('panel.courseEditor.feature6', 'Detailed chapter management') }}</li>
            <li>✓ {{ $t('panel.courseEditor.feature7', 'Granular lesson editing') }}</li>
            <li>✓ {{ $t('panel.courseEditor.feature8', 'Direct content input') }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Recent Courses Section -->
    <div v-if="recentCourses.length > 0" class="max-w-4xl mx-auto mb-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">{{
        $t('panel.courseEditor.recentCourses')
      }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          v-for="course in recentCourses"
          :key="course.course_id"
          @click="openCourseQuick(course)"
          class="p-4 bg-white border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-lg transition-all cursor-pointer group"
        >
          <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
            {{ course.title }}
          </h3>
          <p class="text-sm text-gray-500 mt-2">
            📚 {{ course.category }}
          </p>
          <p class="text-xs text-gray-400 mt-2">
            {{ formatDate(course.updated_at) }}
          </p>
          <div class="mt-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click.stop="openCourseWithEditor(course, 'ai')"
              class="flex-1 px-2 py-1 text-xs bg-indigo-50 text-indigo-700 rounded hover:bg-indigo-100"
            >
              🤖 AI
            </button>
            <button
              @click.stop="openCourseWithEditor(course, 'manual')"
              class="flex-1 px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100"
            >
              ✏️ Manual
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tips Section -->
    <div class="max-w-4xl mx-auto">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 class="font-bold text-blue-900 mb-3">💡 {{
          $t('panel.courseEditor.tips', 'Tips')
        }}</h3>
        <ul class="text-sm text-blue-800 space-y-2">
          <li>• {{ $t('panel.courseEditor.tip1', 'Use AI Editor to quickly structure courses from documents') }}</li>
          <li>• {{ $t('panel.courseEditor.tip2', 'Use Manual Editor for fine-grained control') }}</li>
          <li>• {{ $t('panel.courseEditor.tip3', 'You can open multiple editors at the same time') }}</li>
          <li>• {{ $t('panel.courseEditor.tip4', 'All changes are auto-saved to your workspace') }}</li>
        </ul>
      </div>
    </div>

    <!-- Course Selection Modal -->
    <CourseSelectionModal
      :show="showModal"
      @close="showModal = false"
      @courseOpened="handleCourseOpened"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/window.store'
import CourseSelectionModal from '@/presentation/components/content/admin/courses/modals/CourseSelectionModal.vue'

interface Course {
  course_id: string
  title: string
  category: string
  status: 'draft' | 'published' | 'archived'
  updated_at: string
}

const { t } = useI18n()
const windowStore = useWindowStore()

const showModal = ref(false)
const recentCourses = ref<Course[]>([])

onMounted(() => {
  loadRecentCourses()
})

function loadRecentCourses() {
  // TODO: Load from API or localStorage
  // For now, show mock data
  recentCourses.value = [
    {
      course_id: '1',
      title: 'Introduction to Python',
      category: 'Programming',
      status: 'published',
      updated_at: '2026-01-20T10:30:00Z'
    },
    {
      course_id: '2',
      title: 'Web Development',
      category: 'Web',
      status: 'draft',
      updated_at: '2026-01-19T14:20:00Z'
    },
    {
      course_id: '3',
      title: 'Data Science',
      category: 'Data',
      status: 'published',
      updated_at: '2026-01-18T08:45:00Z'
    }
  ]
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function openCourseQuick(course: Course) {
  // Open modal with course pre-selected
  showModal.value = true
}

function openCourseWithEditor(course: Course, editorType: 'ai' | 'manual') {
  if (editorType === 'ai') {
    windowStore.openWindow({
      type: 'panel-ai-studio',
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
      type: 'panel-course-editor',
      title: `Manual Editor: ${course.title}`,
      icon: '📝',
      payload: {
        courseId: course.course_id,
        courseTitle: course.title
      },
      size: { width: 1200, height: 800 }
    })
  }
}

function handleCourseOpened(courseId: string, editorType: 'ai' | 'manual') {
  console.log(`Opened course ${courseId} with ${editorType} editor`)
  // Optional: Track analytics
}
</script>

<style scoped>
.panel-course-editor-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}
</style>
