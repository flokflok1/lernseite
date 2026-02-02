<template>
  <div class="course-creator-info bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
    <!-- Header -->
    <div class="px-3 py-2 border-b border-gray-200 dark:border-gray-700 animated-header-gradient flex items-center gap-2">
      <div class="w-5 h-5 bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 rounded flex items-center justify-center">
        <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
      </div>
      <span class="text-xs font-bold text-gray-900 dark:text-white">{{ $t('panel.courseDetail.creator.title') }}</span>
    </div>

    <!-- Creator Details -->
    <div class="p-3 space-y-2 text-sm">
      <!-- Creator Name -->
      <div class="flex justify-between">
        <span class="text-gray-500 dark:text-gray-400">{{ $t('panel.courseDetail.creator.name') }}</span>
        <span class="text-gray-900 dark:text-white font-medium">{{ creatorName || $t('panel.courseDetail.creator.unknown') }}</span>
      </div>

      <!-- Creator Email -->
      <div v-if="creatorEmail" class="flex justify-between">
        <span class="text-gray-500 dark:text-gray-400">{{ $t('panel.courseDetail.creator.email') }}</span>
        <a :href="`mailto:${creatorEmail}`" class="text-purple-600 dark:text-purple-400 hover:underline">
          {{ creatorEmail }}
        </a>
      </div>

      <!-- Organisation -->
      <div class="flex justify-between">
        <span class="text-gray-500 dark:text-gray-400">{{ $t('panel.courseDetail.creator.organisation') }}</span>
        <span class="text-gray-900 dark:text-white">{{ organisationName || $t('panel.courseDetail.creator.noOrganisation') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseCreatorInfo Component
 * ===========================
 * Displays course creator information
 */

interface Props {
  creatorName?: string | null
  creatorEmail?: string | null
  organisationName?: string | null
}

defineProps<Props>()
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
</style>
