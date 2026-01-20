<template>
  <div class="video-lesson bg-white rounded-lg shadow-sm p-8">
    <!-- Video Player -->
    <div v-if="videoUrl" class="mb-6">
      <div class="relative w-full" style="padding-bottom: 56.25%">
        <iframe
          v-if="isYouTube || isVimeo"
          :src="embedUrl"
          class="absolute top-0 left-0 w-full h-full rounded-lg"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
        <video
          v-else
          :src="videoUrl"
          controls
          class="absolute top-0 left-0 w-full h-full rounded-lg"
        >
          {{ $t('lesson.video.browserNotSupported') }}
        </video>
      </div>
    </div>

    <!-- Video Description -->
    <div v-if="content.description" class="mb-6">
      <h3 class="font-semibold text-gray-900 mb-2">{{ $t('lesson.video.description') }}</h3>
      <p class="text-gray-700 whitespace-pre-wrap">{{ content.description }}</p>
    </div>

    <!-- Transcript -->
    <div v-if="content.transcript" class="p-4 bg-gray-50 rounded-lg">
      <details>
        <summary class="font-semibold text-gray-900 cursor-pointer">{{ $t('lesson.video.showTranscript') }}</summary>
        <p class="mt-3 text-gray-700 whitespace-pre-wrap">{{ content.transcript }}</p>
      </details>
    </div>

    <!-- Additional Notes -->
    <div v-if="content.notes" class="mt-6 prose prose-lg max-w-none">
      <h3 class="font-semibold text-gray-900 mb-2">{{ $t('lesson.video.notes') }}</h3>
      <div class="text-gray-700 whitespace-pre-wrap">{{ content.notes }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Lesson } from '@/infrastructure/api/clients/learning'

const { t } = useI18n()

// ============================================================================
// Props
// ============================================================================

interface Props {
  lesson: Lesson
}

const props = defineProps<Props>()

// ============================================================================
// Computed
// ============================================================================

const content = computed(() => {
  return props.lesson.content || {}
})

const videoUrl = computed(() => {
  return content.value.video_url || content.value.url || ''
})

const isYouTube = computed(() => {
  return videoUrl.value.includes('youtube.com') || videoUrl.value.includes('youtu.be')
})

const isVimeo = computed(() => {
  return videoUrl.value.includes('vimeo.com')
})

const embedUrl = computed(() => {
  const url = videoUrl.value

  // YouTube
  if (isYouTube.value) {
    const videoId = extractYouTubeId(url)
    return videoId ? `https://www.youtube.com/embed/${videoId}` : ''
  }

  // Vimeo
  if (isVimeo.value) {
    const videoId = extractVimeoId(url)
    return videoId ? `https://player.vimeo.com/video/${videoId}` : ''
  }

  return url
})

// ============================================================================
// Methods
// ============================================================================

const extractYouTubeId = (url: string): string | null => {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/,
    /youtube\.com\/embed\/([^&\n?#]+)/
  ]

  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match && match[1]) {
      return match[1]
    }
  }

  return null
}

const extractVimeoId = (url: string): string | null => {
  const match = url.match(/vimeo\.com\/(\d+)/)
  return match ? match[1] : null
}
</script>

<style scoped>
details summary {
  list-style: none;
}

details summary::-webkit-details-marker {
  display: none;
}

details[open] summary {
  margin-bottom: 0.75rem;
}
</style>
