<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header with Save/Cancel -->
    <div class="bg-white shadow sticky top-0 z-10">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button
              @click="handleCancel"
              class="text-gray-600 hover:text-gray-900"
            >
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 class="text-2xl font-bold text-gray-900">
              {{ mode === 'create' ? $t('courseEditor.newCourse') : $t('courseEditor.editCourse') }}
            </h1>
            <span
              v-if="editorStore.isDirty"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"
            >
              {{ $t('courseEditor.unsaved') }}
            </span>
          </div>
          <div class="flex items-center space-x-3">
            <button
              @click="handleDiscard"
              :disabled="editorStore.saving"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              {{ $t('courseEditor.discard') }}
            </button>
            <button
              @click="handleSave"
              :disabled="editorStore.saving || !editorStore.hasCourse"
              class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
            >
              {{ editorStore.saving ? $t('courseEditor.saving') : $t('courseEditor.save') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="editorStore.loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Editor Content -->
    <div v-else-if="editorStore.hasCourse" class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
      <div class="grid grid-cols-12 gap-6">
        <!-- Left Sidebar: Module Tree -->
        <div class="col-span-3">
          <ModuleLessonTree />
        </div>

        <!-- Center: Content Editor -->
        <div class="col-span-9">
          <div class="bg-white shadow sm:rounded-lg">
            <CourseMetaForm v-if="!editorStore.selectedLessonId" />
            <LessonContentEditor v-else />
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="editorStore.error" class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
      <div class="bg-red-50 border-l-4 border-red-400 p-4 rounded-md">
        <p class="text-sm text-red-700">{{ editorStore.error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

const { t } = useI18n()
import CourseMetaForm from '@/presentation/components/panel/editor/manual/CourseMetaForm.vue'
import ModuleLessonTree from '@/presentation/components/panel/editor/manual/ChapterLessonTree.vue'
import LessonContentEditor from '@/presentation/components/panel/editor/manual/LessonContentEditor.vue'

const props = defineProps<{
  courseId?: number
  mode: 'create' | 'edit'
}>()

const router = useRouter()
const editorStore = useCourseEditorStore()

onMounted(async () => {
  if (props.mode === 'create') {
    await editorStore.createNewCourse()
  } else if (props.courseId) {
    await editorStore.loadCourseForEdit(props.courseId)
  }
})

onBeforeUnmount(() => {
  editorStore.clearEditor()
})

onBeforeRouteLeave((_to, _from, next) => {
  if (editorStore.isDirty) {
    const answer = window.confirm(t('courseEditor.confirmLeave'))
    if (!answer) {
      next(false)
      return
    }
  }
  next()
})

const handleSave = async () => {
  await editorStore.saveAllChanges()
}

const handleDiscard = async () => {
  if (confirm(t('courseEditor.confirmDiscard'))) {
    await editorStore.discardChanges()
  }
}

const handleCancel = () => {
  if (editorStore.isDirty) {
    if (!confirm(t('courseEditor.confirmCancel'))) {
      return
    }
  }
  router.push({ name: 'CreatorCourses' })
}
</script>
