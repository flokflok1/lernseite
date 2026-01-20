<template>
  <div class="course-quick-actions bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
    <!-- Header -->
    <div class="px-4 py-2 border-b border-gray-200 dark:border-gray-700 animated-header-gradient flex items-center gap-2">
      <div class="w-5 h-5 bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 rounded flex items-center justify-center">
        <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
        </svg>
      </div>
      <span class="text-xs font-bold text-gray-900 dark:text-white">{{ $t('admin.courseDetail.actions.title') }}</span>
    </div>

    <!-- Action Buttons Grid -->
    <div class="p-2 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-1.5">
      <!-- Chapters Button -->
      <button
        @click="$emit('open-chapters')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-blue-500 via-indigo-500 to-blue-600 hover:from-blue-600 hover:via-indigo-600 hover:to-blue-700 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.chapters') }}</span>
      </button>

      <!-- Files Button -->
      <button
        @click="$emit('open-files')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-orange-500 via-amber-500 to-orange-600 hover:from-orange-600 hover:via-amber-600 hover:to-orange-700 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.files') }}</span>
      </button>

      <!-- Exams Button -->
      <button
        @click="$emit('open-exams')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-pink-500 via-rose-500 to-pink-600 hover:from-pink-600 hover:via-rose-600 hover:to-pink-700 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.exams') }}</span>
      </button>

      <!-- AI Exam Generation Button -->
      <button
        @click="$emit('generate-exam')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-purple-500 via-violet-500 to-fuchsia-500 hover:from-purple-600 hover:via-violet-600 hover:to-fuchsia-600 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.aiExam') }}</span>
      </button>

      <!-- AI Studio Button -->
      <button
        @click="$emit('open-ai-editor')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-indigo-500 via-blue-500 to-cyan-500 hover:from-indigo-600 hover:via-blue-600 hover:to-cyan-600 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.aiEditor') }}</span>
      </button>

      <!-- Publish Button (only if draft) -->
      <button
        v-if="status === 'draft'"
        @click="$emit('publish')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-600 hover:from-emerald-600 hover:via-teal-600 hover:to-cyan-700 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.publish') }}</span>
      </button>

      <!-- Unpublish Button (only if published) -->
      <button
        v-if="status === 'published'"
        @click="$emit('unpublish')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-amber-500 via-orange-500 to-rose-500 hover:from-amber-600 hover:via-orange-600 hover:to-rose-600 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.unpublish') }}</span>
      </button>

      <!-- Archive Button (if not archived) -->
      <button
        v-if="status !== 'archived'"
        @click="$emit('archive')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-slate-500 via-gray-500 to-slate-600 hover:from-slate-600 hover:via-gray-600 hover:to-slate-700 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.archive') }}</span>
      </button>

      <!-- Edit Button -->
      <button
        @click="$emit('edit')"
        class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-green-500 via-emerald-500 to-green-600 hover:from-green-600 hover:via-emerald-600 hover:to-green-700 shadow-sm hover:shadow-md transition-all text-center"
      >
        <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
          <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
        </div>
        <span class="text-[11px] font-semibold text-white">{{ $t('admin.courseDetail.actions.edit') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseQuickActions Component
 * =============================
 * Quick action buttons for course management
 */

interface Props {
  status: string
}

defineProps<Props>()

defineEmits<{
  'open-chapters': []
  'open-files': []
  'open-exams': []
  'generate-exam': []
  'open-ai-editor': []
  'publish': []
  'unpublish': []
  'archive': []
  'edit': []
}>()
</script>

<style scoped>
.animated-header-gradient {
  background: linear-gradient(90deg,
    rgba(147, 197, 253, 0.1) 0%,
    rgba(196, 181, 253, 0.1) 50%,
    rgba(147, 197, 253, 0.1) 100%
  );
  background-size: 200% 200%;
  animation: gradient-shift 3s ease infinite;
}

@keyframes gradient-shift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.action-btn:active {
  transform: scale(0.98);
}
</style>
