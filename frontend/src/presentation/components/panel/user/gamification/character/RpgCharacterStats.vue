<!--
  RPG Character Base Stats + Total
  Extracted from RpgCharacterCard.vue (G01 split)
-->

<template>
  <!-- Base Stats -->
  <div class="stats-section">
    <h4 class="stats-title">{{ $t('dashboard.gamification.attributes') }}</h4>
    <div class="stats-grid">
      <div class="stat-item">
        <div class="stat-icon strength">⚔️</div>
        <div class="stat-info">
          <span class="stat-name">{{ $t('dashboard.gamification.strength') }}</span>
          <div class="stat-bar-container">
            <div class="stat-bar strength" :style="{ width: `${getStatPercent(baseStats.strength)}%` }"></div>
          </div>
          <span class="stat-value">{{ baseStats.strength }}</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon intelligence">🧠</div>
        <div class="stat-info">
          <span class="stat-name">{{ $t('dashboard.gamification.intelligence') }}</span>
          <div class="stat-bar-container">
            <div class="stat-bar intelligence" :style="{ width: `${getStatPercent(baseStats.intelligence)}%` }"></div>
          </div>
          <span class="stat-value">{{ baseStats.intelligence }}</span>
        </div>
      </div>

      <div class="stat-item">
        <div class="stat-icon stamina">💪</div>
        <div class="stat-info">
          <span class="stat-name">{{ $t('dashboard.gamification.stamina') }}</span>
          <div class="stat-bar-container">
            <div class="stat-bar stamina" :style="{ width: `${getStatPercent(baseStats.stamina)}%` }"></div>
          </div>
          <span class="stat-value">{{ baseStats.stamina }}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Total Stats -->
  <div class="total-stats">
    <span class="total-label">{{ $t('dashboard.gamification.totalPower') }}</span>
    <span class="total-value">{{ totalStats }}</span>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface BaseStats {
  strength: number
  intelligence: number
  stamina: number
}

interface Props {
  baseStats: BaseStats
  totalStats: number
}

defineProps<Props>()

function getStatPercent(value: number): number {
  return Math.min((value / 50) * 100, 100)
}
</script>

<style scoped>
.stats-section {
  padding: 14px 16px;
}

.stats-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px 0;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 16px;
}

.stat-icon.strength {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, var(--color-background) 100%);
}

.stat-icon.intelligence {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, var(--color-background) 100%);
}

.stat-icon.stamina {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, var(--color-background) 100%);
}

.stat-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 72px;
}

.stat-bar-container {
  flex: 1;
  height: 8px;
  background: var(--color-surface);
  border-radius: 4px;
  overflow: hidden;
}

.stat-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.stat-bar.strength {
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
}

.stat-bar.intelligence {
  background: linear-gradient(90deg, #3b82f6 0%, #60a5fa 100%);
}

.stat-bar.stamina {
  background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
}

.stat-value {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary);
  min-width: 28px;
  text-align: right;
}

.total-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.05) 0%,
    var(--color-background) 100%
  );
  border-top: 1px solid var(--color-border);
}

.total-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.total-value {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-text-primary);
}
</style>
