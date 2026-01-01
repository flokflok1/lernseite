<template>
  <Card title="Organisation">
    <div class="space-y-3">
      <!-- Organisation Info -->
      <div v-if="organisationName">
        <p class="text-sm text-gray-500">Name</p>
        <p class="font-semibold text-lg">{{ organisationName }}</p>
      </div>

      <!-- Placeholder Stats -->
      <div class="grid grid-cols-2 gap-4 pt-3 border-t border-gray-200">
        <div class="text-center p-3 bg-gray-50 rounded">
          <p class="text-sm text-gray-500">Mitglieder</p>
          <p class="text-2xl font-bold text-gray-400">-</p>
          <p class="text-xs text-gray-400 mt-1">Demnächst</p>
        </div>

        <div class="text-center p-3 bg-gray-50 rounded">
          <p class="text-sm text-gray-500">Kurse</p>
          <p class="text-2xl font-bold text-gray-400">-</p>
          <p class="text-xs text-gray-400 mt-1">Demnächst</p>
        </div>
      </div>

      <!-- Info Notice -->
      <div class="bg-blue-50 border border-blue-200 p-3 rounded">
        <p class="text-xs text-blue-800">
          📊 Organisations-Statistiken werden in einer späteren Phase implementiert
        </p>
      </div>
    </div>

    <template #footer>
      <span class="text-gray-400 text-sm">
        Verwaltung demnächst verfügbar
      </span>
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

const organisationName = computed(() => {
  return authStore.profile?.organisation_name || 'Keine Organisation'
})
</script>
