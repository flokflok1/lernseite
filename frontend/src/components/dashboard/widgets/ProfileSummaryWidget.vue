<template>
  <Card title="Mein Profil">
    <div class="space-y-3">
      <div>
        <p class="text-sm text-gray-500">Name</p>
        <p class="font-medium">{{ authStore.fullName }}</p>
      </div>

      <div>
        <p class="text-sm text-gray-500">E-Mail</p>
        <p class="font-medium text-sm">{{ authStore.user?.email }}</p>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <p class="text-sm text-gray-500">Rolle</p>
          <span class="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded">
            {{ roleLabel }}
          </span>
        </div>

        <div v-if="authStore.profile?.organisation_name">
          <p class="text-sm text-gray-500">Organisation</p>
          <p class="font-medium text-sm">{{ authStore.profile.organisation_name }}</p>
        </div>
      </div>
    </div>

    <template #footer>
      <router-link to="/profile" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
        Profil bearbeiten →
      </router-link>
    </template>
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
