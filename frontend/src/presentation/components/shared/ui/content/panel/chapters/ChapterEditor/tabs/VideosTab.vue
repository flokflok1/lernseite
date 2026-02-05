<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { VideoItem } from '../types'

interface Props {
  videos: VideoItem[]
  isLoading: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'add-video': []
  'remove-video': [index: number]
  'update-video': [index: number, video: VideoItem]
}>()

const { t } = useI18n()

// Computed
const isEmpty = computed(() => props.videos.length === 0)

// Methods
const handleAddVideo = () => {
  emit('add-video')
}

const handleRemoveVideo = (index: number) => {
  emit('remove-video', index)
}

const handleTitleChange = (index: number, title: string) => {
  emit('update-video', index, {
    ...props.videos[index],
    title
  })
}

const handleUrlChange = (index: number, url: string) => {
  emit('update-video', index, {
    ...props.videos[index],
    url
  })
}

const _getVideoPreview = (url: string): string | null => {
  if (!url) return null

  // YouTube
  const youtubeMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)
  if (youtubeMatch) {
    return `https://img.youtube.com/vi/${youtubeMatch[1]}/hqdefault.jpg`
  }

  // Vimeo
  const vimeoMatch = url.match(/vimeo\.com\/(\d+)/)
  if (vimeoMatch) {
    return `https://vimeo.com/api/v2/video/${vimeoMatch[1]}.json`
  }

  return null
}
</script>

<template>
  <div class="videos-tab">
    <div class="videos-header">
      <h3>{{ $t('features.chapterEditor.tabs.videos') }}</h3>
      <button class="btn btn-primary btn-sm" @click="handleAddVideo">
        <span class="icon">➕</span>
        {{ $t('features.chapterEditor.buttons.addVideo') }}
      </button>
    </div>

    <div v-if="isEmpty" class="empty-state">
      <p>{{ $t('features.chapterEditor.empty.videos') }}</p>
    </div>

    <div v-else class="videos-list">
      <div
        v-for="(video, index) in videos"
        :key="index"
        class="video-card"
      >
        <div class="video-index">{{ index + 1 }}</div>

        <div class="video-form">
          <div class="form-group">
            <label class="form-label-small">{{ $t('features.chapterEditor.fields.title') }}</label>
            <input
              type="text"
              class="form-input-small"
              :placeholder="$t('features.chapterEditor.placeholders.videoTitle')"
              :value="video.title"
              @input="handleTitleChange(index, ($event.target as HTMLInputElement).value)"
            />
          </div>

          <div class="form-group">
            <label class="form-label-small">{{ $t('features.chapterEditor.fields.url') }}</label>
            <input
              type="url"
              class="form-input-small"
              :placeholder="$t('features.chapterEditor.placeholders.videoUrl')"
              :value="video.url"
              @input="handleUrlChange(index, ($event.target as HTMLInputElement).value)"
            />
          </div>
        </div>

        <button
          class="btn btn-danger btn-sm"
          :title="$t('features.chapterEditor.buttons.removeVideo')"
          @click="handleRemoveVideo(index)"
        >
          <span class="icon">🗑️</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.videos-tab {
  padding: 1rem;
}

.videos-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.videos-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: var(--color-text-primary);
}

.videos-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.video-card {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  background-color: var(--color-bg-secondary);
}

.video-index {
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 2rem;
  text-align: center;
  line-height: 2.5;
}

.video-form {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-label-small {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-input-small {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.25rem;
  font-size: 0.95rem;
}

.form-input-small:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-light);
}

.btn {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-sm {
  padding: 0.4rem 0.6rem;
  font-size: 0.875rem;
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

.btn-danger {
  background-color: var(--color-error);
  color: white;
}

.btn-danger:hover {
  background-color: var(--color-error-dark);
}

.icon {
  font-size: 1rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
}
</style>
