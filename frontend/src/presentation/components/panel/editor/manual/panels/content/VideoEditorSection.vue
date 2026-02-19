/**
 * VideoEditorSection.vue
 *
 * Video lesson editor sub-component with platform selection,
 * URL input, and YouTube embed preview.
 */

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

interface Props {
  lesson: Record<string, any>
}

const props = defineProps<Props>()

const store = useCourseEditorStore()

const videoUrl = ref('')
const videoPlatform = ref<'youtube' | 'vimeo' | 'custom'>('youtube')

watch(() => props.lesson, (newLesson) => {
  if (newLesson?.lesson_type === 'video') {
    const meta = newLesson.content_meta || {}
    videoUrl.value = meta.video_url || ''
    videoPlatform.value = meta.platform || 'youtube'
  }
}, { immediate: true })

function saveVideoMeta(): void {
  store.updateLessonMeta(props.lesson.lesson_id, {
    content_meta: {
      video_url: videoUrl.value,
      platform: videoPlatform.value,
    },
  })
}
</script>

<template>
  <div class="video-editor">
    <h3>{{ $t('panel.manualEditor.content.videoUrl') }}</h3>
    <div class="form-row">
      <select v-model="videoPlatform" @change="saveVideoMeta">
        <option value="youtube">YouTube</option>
        <option value="vimeo">Vimeo</option>
        <option value="custom">{{ $t('panel.manualEditor.content.videoPlatform') }}</option>
      </select>
      <input
        v-model="videoUrl"
        type="url"
        :placeholder="$t('panel.manualEditor.content.videoUrl')"
        @change="saveVideoMeta"
      />
    </div>
    <div v-if="videoUrl" class="video-preview">
      <iframe
        v-if="videoPlatform === 'youtube'"
        :src="`https://www.youtube.com/embed/${videoUrl.split('v=')[1]?.split('&')[0] || ''}`"
        frameborder="0"
        allowfullscreen
      />
      <p v-else class="preview-url">{{ videoUrl }}</p>
    </div>
  </div>
</template>

<style scoped>
.video-editor {
  padding: 16px;
}

.video-editor h3 {
  font-size: 14px;
  margin: 0 0 8px;
}

.form-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.form-row select {
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.form-row input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.video-preview {
  margin-top: 12px;
}

.video-preview iframe {
  width: 100%;
  height: 280px;
  border-radius: 8px;
}

.preview-url {
  color: #666;
  font-size: 13px;
}
</style>
