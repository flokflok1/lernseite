<template>
  <div class="system-feature peer-review">
    <h2>{{ $t('systemFeatures.peerReview.title') }}</h2>
    <p>{{ $t('systemFeatures.peerReview.description') }}</p>

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
 * Peer Review - System Feature (collaboration)
 *
 * Structured peer review workflows for collaborative assessment.
 *
 * Feature code: peer_review
 * Category: collaboration
 */
import { onMounted } from 'vue'
import { useSystemFeature } from '@/application/composables/system-features'

const props = defineProps<{
  courseId?: string
}>()

const { isAvailable, isLoading, loadConfig } = useSystemFeature('peer_review')

onMounted(() => loadConfig(props.courseId))
</script>

<style scoped>
.peer-review {
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
