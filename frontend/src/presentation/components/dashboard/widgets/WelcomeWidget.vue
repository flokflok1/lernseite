<template>
  <Card :title="$t('widgets.welcome.title')">
    <div class="space-y-4">
      <!-- Quick Stats Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center">
          <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('widgets.welcome.role') }}</p>
          <span class="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded inline-block mt-1">
            {{ roleLabel }}
          </span>
        </div>

        <div v-if="dataContext.subscription" class="text-center">
          <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('widgets.welcome.plan') }}</p>
          <p class="font-medium text-[var(--color-text-primary)] capitalize">{{ dataContext.subscription.plan || 'Free' }}</p>
        </div>

        <div v-if="dataContext.tokenBalance" class="text-center">
          <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('widgets.welcome.tokens') }}</p>
          <p class="font-medium text-[var(--color-text-primary)]">{{ dataContext.tokenBalance.available?.toLocaleString() || 0 }}</p>
        </div>

        <div v-if="dataContext.enrolledCourses" class="text-center">
          <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('widgets.welcome.courses') }}</p>
          <p class="font-medium text-[var(--color-text-primary)]">{{ dataContext.enrolledCourses.length }}</p>
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/auth.store'
import Card from '@/presentation/components/base/Card.vue'
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

const _firstName = computed(() => authStore.user?.first_name || 'User')

const roleLabel = computed(() => {
  const role = authStore.userRole
  const key = `widgets.roles.${role}`
  return t(key) !== key ? t(key) : role
})
</script>
