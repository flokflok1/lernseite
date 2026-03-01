<!--
  RPG Inventory Summary Component
  Phase G1: RPG Dashboard - Inventar/Abo-Box

  Features:
  - Abo-Plan als "Membership"-Item
  - Tokens als Ressource
  - Kurse als Items
  - RPG-Styled Item Cards
-->

<template>
  <div class="rpg-inventory-summary">
    <!-- Header -->
    <div class="inventory-header">
      <h3 class="inventory-title">
        <span class="inventory-icon">🎒</span>
        {{ $t('dashboard.gamification.inventory') }}
      </h3>
    </div>

    <!-- Membership Card -->
    <div class="inventory-section">
      <h4 class="section-title">{{ $t('dashboard.gamification.membership') }}</h4>
      <div class="membership-card" :class="planTier">
        <div class="membership-badge">
          <span class="badge-icon">{{ planIcon }}</span>
        </div>
        <div class="membership-info">
          <span class="plan-name">{{ planName }}</span>
          <span class="plan-tier">{{ planTierLabel }}</span>
        </div>
        <div class="membership-status" :class="{ active: isPremium }">
          {{ isPremium ? $t('dashboard.gamification.active') : $t('dashboard.gamification.free') }}
        </div>
      </div>
    </div>

    <!-- Token Wallet -->
    <div class="inventory-section">
      <h4 class="section-title">{{ $t('dashboard.gamification.resources') }}</h4>
      <div class="resource-cards">
        <!-- AI Tokens -->
        <div class="resource-card tokens">
          <div class="resource-icon-wrapper">
            <span class="resource-icon">🔮</span>
          </div>
          <div class="resource-info">
            <span class="resource-name">{{ $t('dashboard.gamification.aiTokens') }}</span>
            <span class="resource-value">{{ formattedTokens }}</span>
          </div>
          <div class="resource-bar-container">
            <div
              class="resource-bar"
              :style="{ width: `${tokenPercent}%` }"
            ></div>
          </div>
        </div>

        <!-- Storage (placeholder) -->
        <div class="resource-card storage">
          <div class="resource-icon-wrapper">
            <span class="resource-icon">📦</span>
          </div>
          <div class="resource-info">
            <span class="resource-name">{{ $t('dashboard.gamification.storage') }}</span>
            <span class="resource-value">{{ $t('dashboard.gamification.coursesCount', { count: coursesCount }) }}</span>
          </div>
          <div class="resource-bar-container">
            <div
              class="resource-bar"
              :style="{ width: `${Math.min(coursesCount * 10, 100)}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Items + Quick Stats (extracted sub-component) -->
    <RpgInventoryItems
      :isPremium="isPremium"
      :completedLessons="completedLessons"
      :achievements="achievements"
      :streak="streak"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import RpgInventoryItems from './RpgInventoryItems.vue'

const { t } = useI18n()

// ============================================================================
// Props
// ============================================================================

interface Props {
  subscription?: {
    plan?: string
    tier?: string
    status?: string
  } | null
  tokenBalance?: {
    balance?: number
    total_earned?: number
  } | null
  coursesCount?: number
  completedLessons?: number
}

const props = withDefaults(defineProps<Props>(), {
  subscription: null,
  tokenBalance: null,
  coursesCount: 0,
  completedLessons: 0
})

// ============================================================================
// Computed
// ============================================================================

const planTier = computed(() => {
  const tier = props.subscription?.tier || props.subscription?.plan || 'free'
  return tier.toLowerCase()
})

const isPremium = computed(() => {
  const premiumTiers = ['premium', 'creator', 'teacher', 'pro', 'enterprise']
  return premiumTiers.includes(planTier.value)
})

const planIcon = computed(() => {
  switch (planTier.value) {
    case 'premium': return '💎'
    case 'creator': return '🎨'
    case 'teacher': return '📚'
    case 'pro': return '🏆'
    case 'enterprise': return '🏢'
    default: return '⭐'
  }
})

const planName = computed(() => {
  const key = `dashboard.gamification.plan${planTier.value.charAt(0).toUpperCase() + planTier.value.slice(1)}`
  return t(key)
})

const planTierLabel = computed(() => {
  return isPremium.value
    ? t('dashboard.gamification.fullAccess')
    : t('dashboard.gamification.basicAccess')
})

const formattedTokens = computed(() => {
  const balance = props.tokenBalance?.balance || 0
  if (balance >= 10000) {
    return `${(balance / 1000).toFixed(1)}K`
  }
  return balance.toLocaleString('de-DE')
})

const tokenPercent = computed(() => {
  const balance = props.tokenBalance?.balance || 0
  const max = isPremium.value ? 10000 : 1000
  return Math.min((balance / max) * 100, 100)
})

const achievements = computed(() => {
  // Placeholder - could be calculated from actual achievements
  return Math.floor(props.completedLessons / 5)
})

const streak = computed(() => {
  // Placeholder - would come from actual user data
  return 0
})
</script>

<style scoped>
.rpg-inventory-summary {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
}

/* Header */
.inventory-header {
  padding: 16px 20px;
  background: linear-gradient(
    145deg,
    var(--color-background) 0%,
    var(--color-surface) 100%
  );
  border-bottom: 1px solid var(--color-border);
}

.inventory-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.inventory-icon {
  font-size: 20px;
}

/* Sections */
.inventory-section {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
}

.inventory-section:last-of-type {
  border-bottom: none;
}

.section-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px 0;
}

/* Membership Card */
.membership-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-background);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.membership-card.premium,
.membership-card.creator,
.membership-card.teacher,
.membership-card.pro {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, var(--color-background) 100%);
  border-color: rgba(139, 92, 246, 0.3);
}

.membership-card.enterprise {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, var(--color-background) 100%);
  border-color: rgba(251, 191, 36, 0.3);
}

.membership-badge {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border-radius: 10px;
  font-size: 24px;
}

.membership-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.plan-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.plan-tier {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.membership-status {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 12px;
  background: var(--color-surface);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.membership-status.active {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.05) 100%);
  color: #16a34a;
}

/* Resource Cards */
.resource-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.resource-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: var(--color-background);
  border-radius: 10px;
  border: 1px solid var(--color-border);
}

.resource-icon-wrapper {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 18px;
}

.resource-card.tokens .resource-icon-wrapper {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, var(--color-background) 100%);
}

.resource-card.storage .resource-icon-wrapper {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, var(--color-background) 100%);
}

.resource-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.resource-name {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.resource-value {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.resource-bar-container {
  width: 60px;
  height: 6px;
  background: var(--color-surface);
  border-radius: 3px;
  overflow: hidden;
}

.resource-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.resource-card.tokens .resource-bar {
  background: linear-gradient(90deg, #8b5cf6 0%, #a78bfa 100%);
}

.resource-card.storage .resource-bar {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

/* Responsive */
@media (max-width: 640px) {
  .membership-card {
    flex-wrap: wrap;
  }

  .membership-status {
    width: 100%;
    text-align: center;
    margin-top: 8px;
  }
}
</style>
