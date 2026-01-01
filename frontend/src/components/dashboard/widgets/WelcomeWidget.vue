<template>
  <Card title="Schnellübersicht">
    <div class="space-y-4">
      <!-- Quick Stats Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center">
          <p class="text-sm text-[var(--color-text-secondary)]">Rolle</p>
          <span class="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded inline-block mt-1">
            {{ roleLabel }}
          </span>
        </div>

        <div v-if="dataContext.subscription" class="text-center">
          <p class="text-sm text-[var(--color-text-secondary)]">Plan</p>
          <p class="font-medium text-[var(--color-text-primary)] capitalize">{{ dataContext.subscription.plan || 'Free' }}</p>
        </div>

        <div v-if="dataContext.tokenBalance" class="text-center">
          <p class="text-sm text-[var(--color-text-secondary)]">Tokens</p>
          <p class="font-medium text-[var(--color-text-primary)]">{{ dataContext.tokenBalance.available?.toLocaleString() || 0 }}</p>
        </div>

        <div v-if="dataContext.enrolledCourses" class="text-center">
          <p class="text-sm text-[var(--color-text-secondary)]">Kurse</p>
          <p class="font-medium text-[var(--color-text-primary)]">{{ dataContext.enrolledCourses.length }}</p>
        </div>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth.store'
import Card from '@/components/ui/Card.vue'
import type { BaseWidgetProps } from '@/types/widgets'

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
  const roleMap: Record<string, string> = {
    user: 'User',
    premium: 'Premium',
    creator: 'Creator',
    teacher: 'Lehrer',
    school_admin: 'Schule',
    company_admin: 'Unternehmen',
    admin: 'Admin'
  }
  return roleMap[authStore.userRole] || authStore.userRole
})
</script>
