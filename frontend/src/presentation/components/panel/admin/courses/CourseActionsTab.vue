<!--
  CourseActionsTab - Quick actions tab for course editor

  Provides publish, unpublish, archive, and delete actions.
-->

<template>
  <div class="p-6">
    <div class="space-y-6">
      <!-- Status Actions -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
          {{ $t('courseEditor.actions.title') }}
        </h3>
        <div class="space-y-3">
          <div v-if="course.status === 'draft'" class="flex items-center justify-between">
            <div>
              <p class="font-medium text-[var(--color-text-primary)]">{{ $t('courseEditor.actions.publishCourse') }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('courseEditor.actions.publishHint') }}</p>
            </div>
            <button
              @click="$emit('publish')"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              {{ $t('courseEditor.actions.publishButton') }}
            </button>
          </div>

          <div v-if="course.status === 'published'" class="flex items-center justify-between">
            <div>
              <p class="font-medium text-[var(--color-text-primary)]">{{ $t('courseEditor.actions.unpublishCourse') }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('courseEditor.actions.unpublishHint') }}</p>
            </div>
            <button
              @click="$emit('unpublish')"
              class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
            >
              {{ $t('courseEditor.actions.unpublishButton') }}
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-[var(--color-text-primary)]">{{ $t('courseEditor.actions.archiveCourse') }}</p>
              <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('courseEditor.actions.archiveHint') }}</p>
            </div>
            <button
              @click="$emit('archive')"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              {{ $t('courseEditor.actions.archiveButton') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Danger Zone -->
      <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fef2f2); border-color: var(--color-error-border, #fecaca);">
        <h3 class="text-lg font-semibold mb-4" style="color: var(--color-error-text, #b91c1c);">
          {{ $t('courseEditor.actions.dangerZone') }}
        </h3>
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium" style="color: var(--color-error-text, #b91c1c);">{{ $t('courseEditor.actions.deleteCourse') }}</p>
            <p class="text-sm" style="color: var(--color-error, #dc2626);">{{ $t('courseEditor.actions.deleteHint') }}</p>
          </div>
          <button
            @click="$emit('delete')"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            {{ $t('courseEditor.actions.deleteButton') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminCourseDetail } from './composables/useCourseEditor'

interface Props {
  course: AdminCourseDetail
}

defineProps<Props>()

defineEmits<{
  (e: 'publish'): void
  (e: 'unpublish'): void
  (e: 'archive'): void
  (e: 'delete'): void
}>()
</script>
