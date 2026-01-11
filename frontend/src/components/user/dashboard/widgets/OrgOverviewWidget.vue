<template>
  <Card :title="$t('widgets.orgOverview.title')">
    <div class="space-y-3">
      <!-- Organisation Info -->
      <div v-if="organisationName">
        <p class="text-sm text-gray-500">{{ $t('widgets.orgOverview.name') }}</p>
        <p class="font-semibold text-lg">{{ organisationName }}</p>
      </div>

      <!-- Placeholder Stats -->
      <div class="grid grid-cols-2 gap-4 pt-3 border-t border-gray-200">
        <div class="text-center p-3 bg-gray-50 rounded">
          <p class="text-sm text-gray-500">{{ $t('widgets.orgOverview.members') }}</p>
          <p class="text-2xl font-bold text-gray-400">-</p>
          <p class="text-xs text-gray-400 mt-1">{{ $t('widgets.orgOverview.comingSoon') }}</p>
        </div>

        <div class="text-center p-3 bg-gray-50 rounded">
          <p class="text-sm text-gray-500">{{ $t('widgets.orgOverview.courses') }}</p>
          <p class="text-2xl font-bold text-gray-400">-</p>
          <p class="text-xs text-gray-400 mt-1">{{ $t('widgets.orgOverview.comingSoon') }}</p>
        </div>
      </div>

      <!-- Info Notice -->
      <div class="bg-blue-50 border border-blue-200 p-3 rounded">
        <p class="text-xs text-blue-800">
          📊 {{ $t('widgets.orgOverview.statsInfo') }}
        </p>
      </div>
    </div>

    <template #footer>
      <span class="text-gray-400 text-sm">
        {{ $t('widgets.orgOverview.managementSoon') }}
      </span>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/store/auth.store'
import Card from '@/components/base/Card.vue'
import type { BaseWidgetProps } from '@/types/widgets'

const { t } = useI18n()

// ============================================================================
// Props
// ============================================================================

interface Props extends BaseWidgetProps {
  dataContext: any
}

defineProps<Props>()

// ============================================================================
// Store
// ============================================================================

const authStore = useAuthStore()

// ============================================================================
// Computed
// ============================================================================

const organisationName = computed(() => {
  return authStore.profile?.organisation_name || t('widgets.orgOverview.noOrganisation')
})
</script>
