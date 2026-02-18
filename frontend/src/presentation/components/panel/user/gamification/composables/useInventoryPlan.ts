/**
 * Composable for inventory membership/plan computations.
 *
 * Extracts plan-related logic from RpgInventorySummary to keep the
 * parent component under 500 LOC (Quality Gate G01).
 */

import { computed, type Ref } from 'vue'

interface SubscriptionData {
  plan?: string
  tier?: string
  status?: string
}

interface UseInventoryPlanOptions {
  subscription: Ref<SubscriptionData | null | undefined>
}

const PREMIUM_TIERS = ['premium', 'creator', 'teacher', 'pro', 'enterprise'] as const

const PLAN_ICONS: Record<string, string> = {
  premium: '\uD83D\uDC8E',
  creator: '\uD83C\uDFA8',
  teacher: '\uD83D\uDCDA',
  pro: '\uD83C\uDFC6',
  enterprise: '\uD83C\uDFE2'
}

const PLAN_NAMES: Record<string, string> = {
  premium: 'Premium',
  creator: 'Creator',
  teacher: 'Teacher',
  pro: 'Pro',
  enterprise: 'Enterprise'
}

export function useInventoryPlan({ subscription }: UseInventoryPlanOptions) {
  const planTier = computed((): string => {
    const tier = subscription.value?.tier || subscription.value?.plan || 'free'
    return tier.toLowerCase()
  })

  const isPremium = computed((): boolean => {
    return (PREMIUM_TIERS as readonly string[]).includes(planTier.value)
  })

  const planIcon = computed((): string => {
    return PLAN_ICONS[planTier.value] || '\u2B50'
  })

  const planName = computed((): string => {
    return PLAN_NAMES[planTier.value] || 'Free'
  })

  const planTierLabel = computed((): string => {
    if (isPremium.value) {
      return 'Vollzugriff'
    }
    return 'Basis-Zugang'
  })

  return {
    planTier,
    isPremium,
    planIcon,
    planName,
    planTierLabel
  }
}
