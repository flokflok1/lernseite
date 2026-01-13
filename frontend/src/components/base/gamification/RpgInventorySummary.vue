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
        Inventar
      </h3>
    </div>

    <!-- Membership Card -->
    <div class="inventory-section">
      <h4 class="section-title">Mitgliedschaft</h4>
      <div class="membership-card" :class="planTier">
        <div class="membership-badge">
          <span class="badge-icon">{{ planIcon }}</span>
        </div>
        <div class="membership-info">
          <span class="plan-name">{{ planName }}</span>
          <span class="plan-tier">{{ planTierLabel }}</span>
        </div>
        <div class="membership-status" :class="{ active: isPremium }">
          {{ isPremium ? 'Aktiv' : 'Free' }}
        </div>
      </div>
    </div>

    <!-- Token Wallet -->
    <div class="inventory-section">
      <h4 class="section-title">Ressourcen</h4>
      <div class="resource-cards">
        <!-- AI Tokens -->
        <div class="resource-card tokens">
          <div class="resource-icon-wrapper">
            <span class="resource-icon">🔮</span>
          </div>
          <div class="resource-info">
            <span class="resource-name">KI-Tokens</span>
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
            <span class="resource-name">Speicher</span>
            <span class="resource-value">{{ coursesCount }} Kurse</span>
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

    <!-- Premium Features as Items -->
    <div v-if="isPremium" class="inventory-section">
      <h4 class="section-title">Premium-Items</h4>
      <div class="items-grid">
        <div class="item-card epic">
          <span class="item-icon">⚡</span>
          <span class="item-name">Priority Support</span>
        </div>
        <div class="item-card rare">
          <span class="item-icon">🎨</span>
          <span class="item-name">Custom Themes</span>
        </div>
        <div class="item-card rare">
          <span class="item-icon">📊</span>
          <span class="item-name">Analytics</span>
        </div>
        <div class="item-card legendary">
          <span class="item-icon">🤖</span>
          <span class="item-name">KI-Tutor</span>
        </div>
      </div>
    </div>

    <!-- Free Features -->
    <div v-else class="inventory-section">
      <h4 class="section-title">Basis-Items</h4>
      <div class="items-grid">
        <div class="item-card common">
          <span class="item-icon">📚</span>
          <span class="item-name">Basis-Kurse</span>
        </div>
        <div class="item-card common">
          <span class="item-icon">📝</span>
          <span class="item-name">Quiz-System</span>
        </div>
      </div>

      <!-- Upgrade Hint -->
      <div class="upgrade-hint">
        <span class="hint-icon">💎</span>
        <span class="hint-text">Upgrade auf Premium fuer mehr Items!</span>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="quick-stats">
      <div class="stat-item">
        <span class="stat-value">{{ completedLessons }}</span>
        <span class="stat-label">Lektionen</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ achievements }}</span>
        <span class="stat-label">Erfolge</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ streak }}</span>
        <span class="stat-label">Streak</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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
  switch (planTier.value) {
    case 'premium': return 'Premium'
    case 'creator': return 'Creator'
    case 'teacher': return 'Teacher'
    case 'pro': return 'Pro'
    case 'enterprise': return 'Enterprise'
    default: return 'Free'
  }
})

const planTierLabel = computed(() => {
  if (isPremium.value) {
    return 'Vollzugriff'
  }
  return 'Basis-Zugang'
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

/* Items Grid */
.items-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.item-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 8px;
  background: var(--color-background);
  border-radius: 10px;
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
}

.item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.item-icon {
  font-size: 24px;
}

.item-name {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-align: center;
}

/* Item Rarity */
.item-card.common {
  border-color: var(--color-border);
}

.item-card.rare {
  border-color: #3b82f6;
  background: linear-gradient(145deg, rgba(59, 130, 246, 0.05) 0%, var(--color-background) 100%);
}

.item-card.epic {
  border-color: #8b5cf6;
  background: linear-gradient(145deg, rgba(139, 92, 246, 0.05) 0%, var(--color-background) 100%);
}

.item-card.legendary {
  border-color: #f59e0b;
  background: linear-gradient(145deg, rgba(245, 158, 11, 0.05) 0%, var(--color-background) 100%);
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.15);
}

/* Upgrade Hint */
.upgrade-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, var(--color-background) 100%);
  border: 1px dashed rgba(139, 92, 246, 0.3);
  border-radius: 8px;
}

.hint-icon {
  font-size: 18px;
}

.hint-text {
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* Quick Stats */
.quick-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--color-border);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 12px;
  background: var(--color-surface);
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 11px;
  color: var(--color-text-muted);
}

/* Responsive */
@media (max-width: 640px) {
  .items-grid {
    grid-template-columns: repeat(2, 1fr);
  }

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
