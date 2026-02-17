<template>
  <div class="system-feature inverted-classroom">
    <h2>{{ $t('systemFeatures.invertedClassroom.title') }}</h2>
    <p>{{ $t('systemFeatures.invertedClassroom.description') }}</p>

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
 * Inverted Classroom - System Feature (collaboration)
 *
 * Flipped classroom model with pre-learning and in-class activities.
 *
 * Feature code: inverted_classroom
 * Category: collaboration
 */
import { onMounted } from 'vue'
import { useSystemFeature } from '@/application/composables/system-features'

const props = defineProps<{
  courseId?: string
}>()

const { isAvailable, isLoading, loadConfig } = useSystemFeature('inverted_classroom')

onMounted(() => loadConfig(props.courseId))
</script>

<style scoped>
.inverted-classroom {
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
