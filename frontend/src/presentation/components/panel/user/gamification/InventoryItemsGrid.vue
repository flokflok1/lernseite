<!--
  Inventory Items Grid Sub-Component
  Extracted from RpgInventorySummary to satisfy G01 (max 500 LOC).

  Renders premium or free item cards with an optional upgrade hint.
-->

<template>
  <div class="inventory-section">
    <template v-if="isPremium">
      <h4 class="section-title">{{ $t('gamification.premiumItems') }}</h4>
      <div class="items-grid">
        <div class="item-card epic">
          <span class="item-icon">&#x26A1;</span>
          <span class="item-name">{{ $t('gamification.prioritySupport') }}</span>
        </div>
        <div class="item-card rare">
          <span class="item-icon">&#x1F3A8;</span>
          <span class="item-name">{{ $t('gamification.customThemes') }}</span>
        </div>
        <div class="item-card rare">
          <span class="item-icon">&#x1F4CA;</span>
          <span class="item-name">{{ $t('gamification.analytics') }}</span>
        </div>
        <div class="item-card legendary">
          <span class="item-icon">&#x1F916;</span>
          <span class="item-name">{{ $t('gamification.aiTutor') }}</span>
        </div>
      </div>
    </template>

    <template v-else>
      <h4 class="section-title">{{ $t('gamification.basicItems') }}</h4>
      <div class="items-grid">
        <div class="item-card common">
          <span class="item-icon">&#x1F4DA;</span>
          <span class="item-name">{{ $t('gamification.basicCourses') }}</span>
        </div>
        <div class="item-card common">
          <span class="item-icon">&#x1F4DD;</span>
          <span class="item-name">{{ $t('gamification.quizSystem') }}</span>
        </div>
      </div>

      <div class="upgrade-hint">
        <span class="hint-icon">&#x1F48E;</span>
        <span class="hint-text">{{ $t('gamification.upgradeHint') }}</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  isPremium: boolean
}

defineProps<Props>()
</script>

<style scoped>
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

.item-card.common {
  border-color: var(--color-border);
}

.item-card.rare {
  border-color: #3b82f6;
  background: linear-gradient(
    145deg,
    rgba(59, 130, 246, 0.05) 0%,
    var(--color-background) 100%
  );
}

.item-card.epic {
  border-color: #8b5cf6;
  background: linear-gradient(
    145deg,
    rgba(139, 92, 246, 0.05) 0%,
    var(--color-background) 100%
  );
}

.item-card.legendary {
  border-color: #f59e0b;
  background: linear-gradient(
    145deg,
    rgba(245, 158, 11, 0.05) 0%,
    var(--color-background) 100%
  );
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.15);
}

.upgrade-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px;
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.1) 0%,
    var(--color-background) 100%
  );
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

@media (max-width: 640px) {
  .items-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
