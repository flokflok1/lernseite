<template>
  <Card title="Abo & KI">
    <div class="space-y-3">
      <!-- Subscription Info -->
      <div>
        <p class="text-sm text-gray-500">Plan</p>
        <p class="font-bold text-lg capitalize">{{ subscription?.plan || 'Free' }}</p>
        <span
          class="px-2 py-1 text-xs font-medium rounded mt-1 inline-block"
          :class="subscriptionStatusClass"
        >
          {{ subscriptionStatusLabel }}
        </span>
      </div>

      <!-- Included Tokens -->
      <div v-if="subscription?.features?.included_tokens">
        <p class="text-sm text-gray-500">Inkl. Tokens / Monat</p>
        <p class="font-medium">{{ subscription.features.included_tokens.toLocaleString() }}</p>
      </div>

      <!-- Token Balance -->
      <div class="pt-3 border-t border-gray-200">
        <p class="text-sm text-gray-500">Verfügbare Tokens</p>
        <p class="text-2xl font-bold" :class="tokenBalanceClass">
          {{ tokenBalance?.available?.toLocaleString() || 0 }}
        </p>
      </div>

      <!-- Low Token Warning -->
      <div v-if="tokenBalance && tokenBalance.available < 1000" class="bg-yellow-50 border border-yellow-200 p-2 rounded">
        <p class="text-xs text-yellow-800">⚠️ Tokens fast aufgebraucht!</p>
      </div>
    </div>

    <template #footer>
      <router-link to="/profile" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
        Plan verwalten →
      </router-link>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Card from '@/components/ui/Card.vue'
import type { BaseWidgetProps } from '@/types/widgets'

// ============================================================================
// Props
// ============================================================================

interface Props extends BaseWidgetProps {
  dataContext: any
}

const props = defineProps<Props>()

// ============================================================================
// Computed
// ============================================================================

const subscription = computed(() => props.dataContext.subscription)
const tokenBalance = computed(() => props.dataContext.tokenBalance)

const subscriptionStatusClass = computed(() => {
  if (!subscription.value) return 'bg-gray-100 text-gray-800'

  switch (subscription.value.status) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'trial':
      return 'bg-blue-100 text-blue-800'
    case 'cancelled':
      return 'bg-yellow-100 text-yellow-800'
    case 'expired':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
})

const subscriptionStatusLabel = computed(() => {
  if (!subscription.value) return 'Kein Abo'

  const statusMap: Record<string, string> = {
    active: 'Aktiv',
    trial: 'Testversion',
    cancelled: 'Gekündigt',
    expired: 'Abgelaufen',
    none: 'Kein Abo'
  }
  return statusMap[subscription.value.status] || subscription.value.status
})

const tokenBalanceClass = computed(() => {
  if (!tokenBalance.value) return 'text-gray-900'

  const available = tokenBalance.value.available
  if (available < 1000) return 'text-red-600'
  if (available < 5000) return 'text-yellow-600'
  return 'text-green-600'
})
</script>
