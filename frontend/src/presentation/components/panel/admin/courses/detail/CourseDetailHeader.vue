<template>
  <div class="course-detail-header relative overflow-hidden mx-3 mt-1 rounded-lg shadow-sm">
    <!-- Background: Thumbnail or Animated Gradient -->
    <div class="hero-background absolute inset-0">
      <img
        v-if="course.thumbnail_url"
        :src="course.thumbnail_url"
        :alt="course.title"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full animated-gradient"></div>
      <!-- Overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-[var(--color-background)] via-[var(--color-background)]/70 to-transparent"></div>
    </div>

    <!-- Hero Content -->
    <div class="hero-content relative z-10 px-3 pt-3 pb-2">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <!-- Left: Title & Info -->
        <div class="flex-1">
          <!-- Status Badges -->
          <div class="flex items-center gap-1 mb-1.5 flex-wrap">
            <span
              class="px-2 py-0.5 rounded-full text-xs font-semibold backdrop-blur-sm"
              :style="statusBadgeStyle"
            >
              {{ statusText }}
            </span>
            <span
              v-if="showAdBadge"
              class="px-2 py-0.5 rounded-full text-xs font-semibold backdrop-blur-sm bg-amber-500/20 text-amber-700 dark:text-amber-300"
            >
              {{ $t('panel.courseDetail.withAds') }}
            </span>
            <span
              v-if="showPremiumBadge"
              class="px-2 py-0.5 rounded-full text-xs font-semibold backdrop-blur-sm bg-purple-500/20 text-purple-700 dark:text-purple-300"
            >
              {{ $t('panel.courseDetail.premium') }}
            </span>
            <span class="px-2 py-0.5 rounded-full text-xs font-medium backdrop-blur-sm bg-white/10 dark:bg-black/20 text-[var(--color-text-secondary)]">
              {{ languageLabel }}
            </span>
            <span class="px-2 py-0.5 rounded-full text-xs font-medium backdrop-blur-sm bg-white/10 dark:bg-black/20 text-[var(--color-text-secondary)]">
              {{ levelLabel }}
            </span>
          </div>

          <!-- Title -->
          <h1 class="text-xl lg:text-2xl font-bold text-[var(--color-text-primary)] mb-1.5">
            {{ course.title }}
          </h1>

          <!-- Description -->
          <p v-if="course.description" class="text-sm text-[var(--color-text-secondary)] leading-relaxed max-w-4xl">
            {{ course.description }}
          </p>
        </div>
      </div>
    </div>

    <!-- Quick Stats Grid -->
    <div class="relative z-10 px-4 md:px-8 pb-2 flex justify-center">
      <div class="grid grid-cols-4 md:grid-cols-8 gap-1.5 w-full max-w-4xl">
        <!-- Chapter Count -->
        <div
          class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all cursor-pointer group flex flex-col items-center border border-gray-100 dark:border-gray-700"
          @click="$emit('open-chapters')"
        >
          <div class="w-7 h-7 mb-1 bg-blue-100 dark:bg-blue-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
          </div>
          <p class="text-base font-bold text-gray-900 dark:text-white">{{ course.chapter_count || 0 }}</p>
          <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">{{ $t('panel.courseDetail.stats.chapters') }}</p>
        </div>

        <!-- Lesson Count -->
        <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 mb-1 bg-green-100 dark:bg-green-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <p class="text-base font-bold text-gray-900 dark:text-white">{{ lessonCount }}</p>
          <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">{{ $t('panel.courseDetail.stats.lessons') }}</p>
        </div>

        <!-- Enrollments -->
        <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 mb-1 bg-purple-100 dark:bg-purple-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
            </svg>
          </div>
          <p class="text-base font-bold text-gray-900 dark:text-white">{{ course.enrollment_count || 0 }}</p>
          <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">{{ $t('panel.courseDetail.stats.enrollments') }}</p>
        </div>

        <!-- Files -->
        <div
          class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all cursor-pointer group flex flex-col items-center border border-gray-100 dark:border-gray-700"
          @click="$emit('open-files')"
        >
          <div class="w-7 h-7 mb-1 bg-orange-100 dark:bg-orange-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg class="w-4 h-4 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <p class="text-base font-bold text-gray-900 dark:text-white">{{ fileCount }}</p>
          <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">{{ $t('panel.courseDetail.stats.files') }}</p>
        </div>

        <!-- Revenue -->
        <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 mb-1 bg-pink-100 dark:bg-pink-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg class="w-4 h-4 text-pink-600 dark:text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <p class="text-base font-bold text-gray-900 dark:text-white">{{ revenueDisplay }}</p>
          <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">{{ $t('panel.courseDetail.stats.revenue') }}</p>
        </div>

        <!-- Rating -->
        <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 mb-1 bg-yellow-100 dark:bg-yellow-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg class="w-4 h-4 text-yellow-600 dark:text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </div>
          <p class="text-base font-bold text-gray-900 dark:text-white">{{ ratingDisplay }}</p>
          <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">{{ $t('panel.courseDetail.stats.rating') }}</p>
        </div>

        <!-- Completion Rate -->
        <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 mb-1 bg-amber-100 dark:bg-amber-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg class="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
            </svg>
          </div>
          <p class="text-base font-bold text-gray-900 dark:text-white">{{ completionRateDisplay }}</p>
          <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">{{ $t('panel.courseDetail.stats.completionRate') }}</p>
        </div>

        <!-- Price -->
        <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
          <div class="w-7 h-7 mb-1 bg-teal-100 dark:bg-teal-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
            <svg class="w-4 h-4 text-teal-600 dark:text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
            </svg>
          </div>
          <p class="text-base font-bold text-gray-900 dark:text-white">{{ course.price ? `${course.price}€` : $t('panel.courseDetail.free') }}</p>
          <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">{{ $t('panel.courseDetail.stats.price') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * CourseDetailHeader Component
 * ============================
 * Hero section with course info and stats cards
 */
import type { AdminCourseDetail } from '@/infrastructure/api/clients/panel/admin'

interface Props {
  course: AdminCourseDetail
  statusBadgeStyle: string
  statusText: string
  languageLabel: string
  levelLabel: string
  showAdBadge: boolean
  showPremiumBadge: boolean
  lessonCount: number
  fileCount: number
  revenueDisplay: string
  ratingDisplay: string
  completionRateDisplay: string
}

defineProps<Props>()

defineEmits<{
  'open-chapters': []
  'open-files': []
}>()
</script>

<style scoped>
.animated-gradient {
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
}

@keyframes gradient {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}
</style>
