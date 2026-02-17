<template>
  <div class="system-feature speech-to-text">
    <h2>{{ $t('systemFeatures.speechToText.title') }}</h2>
    <p>{{ $t('systemFeatures.speechToText.description') }}</p>

    <div v-if="isLoading" class="feature-loading">
      {{ $t('systemFeatures.loading') }}
    </div>

    <div v-else-if="!isAvailable" class="feature-locked">
      {{ $t('systemFeatures.locked') }}
    </div>

    <div v-else class="stub-notice">
      {{ $t('systemFeatures.comingSoon') }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * Speech-to-Text - System Feature (audio)
 *
 * Voice input and transcription for learning activities.
 *
 * Feature code: speech_to_text
 * Category: audio
 */
import { onMounted } from 'vue'
import { useSystemFeature } from '@/application/composables/system-features'

const props = defineProps<{
  courseId?: string
}>()

const { isAvailable, isLoading, checkAvailability } = useSystemFeature('speech_to_text')

onMounted(() => checkAvailability())
</script>

<style scoped>
.speech-to-text {
  padding: 1rem;
}

.stub-notice {
  margin-top: 1rem;
  padding: 1rem;
  background: #d1ecf1;
  border: 1px solid #bee5eb;
  border-radius: 4px;
  color: #0c5460;
}

.feature-locked {
  padding: 1rem;
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  color: #721c24;
}

.feature-loading {
  padding: 1rem;
  color: #6c757d;
}
</style>
