<template>
  <Card :title="$t('widgets.profileSummary.title')">
    <div class="space-y-3">
      <div>
        <p class="text-sm text-gray-500">{{ $t('widgets.profileSummary.name') }}</p>
        <p class="font-medium">{{ authStore.fullName }}</p>
      </div>

      <div>
        <p class="text-sm text-gray-500">{{ $t('widgets.profileSummary.email') }}</p>
        <p class="font-medium text-sm">{{ authStore.user?.email }}</p>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-sm text-gray-500">{{ $t('widgets.profileSummary.role') }}</p>
          <span class="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
            {{ roleLabel }}
          </span>
        </div>

        <div v-if="authStore.profile?.organisation_name">
          <p class="text-sm text-gray-500">{{ $t('widgets.profileSummary.organisation') }}</p>
          <p class="font-medium text-sm">{{ authStore.profile.organisation_name }}</p>
        </div>
      </div>
    </div>

    <template #footer>
      <router-link to="/profile" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
        {{ $t('widgets.profileSummary.editProfile') }}
      </router-link>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/store/modules/core'
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

const roleLabel = computed(() => {
  const role = authStore.userRole
  const key = `widgets.roles.${role}`
  return t(key) !== key ? t(key) : role
})
</script>
