<template>
  <div class="system-feature it-sandbox">
    <h2>{{ $t('systemFeatures.itSandbox.title') }}</h2>
    <p>{{ $t('systemFeatures.itSandbox.description') }}</p>

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
 * IT Sandbox - System Feature (it_environments)
 *
 * Isolated IT environment for hands-on practice with infrastructure.
 *
 * Feature code: it_sandbox
 * Category: it_environments
 */
import { onMounted } from 'vue'
import { useSystemFeature } from '@/application/composables/system-features'

const props = defineProps<{
  courseId?: string
}>()

const { isAvailable, isLoading, checkAvailability } = useSystemFeature('it_sandbox')

onMounted(() => checkAvailability())
</script>

<style scoped>
.it-sandbox {
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
