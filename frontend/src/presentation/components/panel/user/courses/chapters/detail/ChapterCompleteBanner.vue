<template>
  <div class="mx-auto max-w-5xl px-6 mt-4 mb-4">
    <div class="relative overflow-hidden rounded-2xl bg-gradient-to-r from-emerald-500 via-green-500 to-teal-500 p-6 text-white shadow-xl shadow-green-500/20">
      <!-- Decorative circles -->
      <div class="absolute -right-6 -top-6 h-24 w-24 rounded-full bg-white/10"></div>
      <div class="absolute -right-2 -bottom-4 h-16 w-16 rounded-full bg-white/10"></div>

      <div class="relative flex items-center gap-5">
        <div class="flex-shrink-0 rounded-full bg-white/20 p-4">
          <svg class="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <h3 class="text-xl font-extrabold">{{ $t('chapter.chapterComplete') }}</h3>
          <p class="mt-1 text-sm text-green-100">
            {{ $t('chapter.chapterCompleteDesc', { count: lessonCount }) }}
          </p>
          <button
            @click="$emit('continue')"
            class="mt-3 px-4 py-2 bg-white/20 hover:bg-white/30 text-white font-semibold text-sm rounded-lg transition-all border border-white/20"
          >
            {{ $t('chapter.backToCourse') }}
            <svg class="inline-block w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  lessonCount: number
}

defineProps<Props>()
defineEmits<{
  continue: []
}>()
</script>
