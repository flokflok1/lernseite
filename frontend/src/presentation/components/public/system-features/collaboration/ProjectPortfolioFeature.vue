<template>
  <div class="system-feature project-portfolio">
    <h2>{{ $t('systemFeatures.projectPortfolio.title') }}</h2>
    <p>{{ $t('systemFeatures.projectPortfolio.description') }}</p>

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
 * Project Portfolio - System Feature (collaboration)
 *
 * Project portfolio management for showcasing learning achievements.
 *
 * Feature code: project_portfolio
 * Category: collaboration
 */
import { onMounted } from 'vue'
import { useSystemFeature } from '@/application/composables/system-features'

const props = defineProps<{
  courseId?: string
}>()

const { isAvailable, isLoading, checkAvailability } = useSystemFeature('project_portfolio')

onMounted(() => checkAvailability())
</script>

<style scoped>
.project-portfolio {
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
