<template>
  <div class="chapter-hero relative overflow-hidden">
    <!-- Animated gradient background -->
    <div class="hero-gradient absolute inset-0"></div>
    <!-- Floating orbs -->
    <div class="absolute -top-10 right-[15%] w-48 h-48 bg-white/[0.06] rounded-full blur-3xl hero-float"></div>
    <div class="absolute top-4 right-[40%] w-32 h-32 bg-cyan-300/[0.05] rounded-full blur-2xl hero-float-delayed"></div>
    <div class="absolute -bottom-12 left-[10%] w-56 h-56 bg-purple-400/[0.07] rounded-full blur-3xl hero-float-slow"></div>
    <div class="absolute -bottom-6 right-[25%] w-36 h-36 bg-indigo-300/[0.05] rounded-full blur-2xl hero-float-delayed"></div>

    <div class="relative max-w-7xl mx-auto px-6 pt-3 pb-5">
      <!-- Back Button -->
      <button
        @click="emit('back')"
        class="inline-flex items-center gap-1.5 text-xs text-blue-200 hover:text-white transition-colors mb-3 group"
      >
        <svg class="w-3.5 h-3.5 transition-transform group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        {{ $t('chapter.backToCourse') }}
      </button>

      <!-- Main row: Ring + Info + CTA -->
      <div class="flex items-center gap-5">
        <!-- Progress Ring -->
        <div v-if="progress !== null" class="flex-shrink-0 hidden sm:block">
          <div class="ring-glow rounded-full p-1">
            <ProgressRing :percentage="progress" :size="72" :stroke-width="5" dark />
          </div>
        </div>

        <!-- Info column -->
        <div class="flex-1 min-w-0">
          <p v-if="courseName" class="text-xs text-blue-200/80 font-medium mb-0.5">{{ courseName }}</p>
          <h1 class="text-2xl md:text-3xl font-extrabold text-white leading-tight tracking-tight">
            {{ chapter?.title || $t('chapter.loading') }}
          </h1>

          <!-- Meta chips + CTA on same row -->
          <div class="flex flex-wrap items-center gap-2 mt-2.5">
            <span v-if="lessonCount > 0" class="meta-chip">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              {{ $t('chapter.lessonsCount', { count: lessonCount }) }}
            </span>
            <span v-if="totalDuration > 0" class="meta-chip">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ $t('chapter.estimatedDuration', { minutes: totalDuration }) }}
            </span>
            <span v-if="completedLessons > 0" class="meta-chip">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ $t('chapter.completedLessons', { completed: completedLessons, total: lessonCount }) }}
            </span>
            <span v-for="(count, type) in lessonTypeBreakdown" :key="type" class="meta-chip">
              {{ typeEmoji(type as string) }} {{ count }}
            </span>

            <!-- Separator + CTA inline -->
            <span class="w-px h-5 bg-white/20 mx-1 hidden sm:block"></span>
            <button
              v-if="hasNextLesson && !isChapterCompleted"
              @click="emit('continue-learning')"
              class="inline-flex items-center gap-2 px-4 py-1.5 bg-white text-blue-700 text-xs font-bold rounded-lg hover:bg-blue-50 transition-all shadow-md shadow-black/20 hover:scale-[1.02] active:scale-[0.98]"
            >
              <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
              {{ progress && progress > 0 ? $t('chapter.continueLearning') : $t('chapter.startLearning') }}
            </button>
            <div v-if="isChapterCompleted" class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 border border-green-400/30 rounded-lg text-green-100 text-xs font-semibold">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
              </svg>
              {{ $t('chapter.chapterComplete') }}
            </div>
          </div>

          <!-- Description -->
          <p v-if="chapter?.description" class="mt-2 text-xs text-blue-100/70 line-clamp-1 max-w-2xl">
            {{ chapter.description }}
          </p>
        </div>

        <!-- Mobile progress ring -->
        <div v-if="progress !== null" class="flex-shrink-0 sm:hidden">
          <ProgressRing :percentage="progress" :size="56" :stroke-width="4" dark />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import ProgressRing from './timeline/ProgressRing.vue'

interface Props {
  chapter: any
  courseName: string
  progress: number | null
  lessonCount: number
  completedLessons: number
  totalDuration: number
  lessonTypeBreakdown: Record<string, number>
  isChapterCompleted: boolean
  hasNextLesson: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  back: []
  'continue-learning': []
}>()

function typeEmoji(type: string): string {
  const map: Record<string, string> = {
    text: '📝', video: '🎬', quiz: '❓', ai: '🤖', interactive: '🎮', mixed: '🔀'
  }
  return map[type] || '📄'
}
</script>

<style scoped>
.hero-gradient {
  background: linear-gradient(
    135deg,
    #1e40af 0%,
    #4338ca 25%,
    #6d28d9 50%,
    #4338ca 75%,
    #1e40af 100%
  );
  background-size: 300% 300%;
  animation: gradientShift 8s ease-in-out infinite;
}

:root.dark .hero-gradient {
  background: linear-gradient(
    135deg,
    #1e3a5f 0%,
    #312e81 25%,
    #4c1d95 50%,
    #312e81 75%,
    #1e3a5f 100%
  );
  background-size: 300% 300%;
  animation: gradientShift 8s ease-in-out infinite;
}

@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  50%  { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.hero-float {
  animation: floatOrb 6s ease-in-out infinite;
}
.hero-float-delayed {
  animation: floatOrb 7s ease-in-out 2s infinite;
}
.hero-float-slow {
  animation: floatOrb 9s ease-in-out 1s infinite;
}

@keyframes floatOrb {
  0%, 100% { transform: translateY(0) scale(1); }
  50%      { transform: translateY(-12px) scale(1.05); }
}

.meta-chip {
  @apply inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
         bg-white/15 text-white/90 backdrop-blur-sm border border-white/10;
}

.ring-glow {
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
