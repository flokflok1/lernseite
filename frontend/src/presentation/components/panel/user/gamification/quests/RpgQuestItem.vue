<!--
  RPG Quest Item Component
  Renders a single active quest with difficulty badge, rewards, and complete button.
  Extracted from RpgQuestList.vue for G01 compliance (<500 LOC).
-->

<template>
  <div
    class="quest-item"
    :class="{ 'completing': isCompleting }"
  >
    <!-- Quest Icon -->
    <div class="quest-item-icon" :class="quest.difficulty">
      <span>{{ quest.icon || difficultyIcon }}</span>
    </div>

    <!-- Quest Content -->
    <div class="quest-item-content">
      <div class="quest-item-header">
        <h4 class="quest-item-title">{{ quest.title }}</h4>
        <span class="difficulty-badge" :class="quest.difficulty">
          {{ difficultyLabel }}
        </span>
      </div>
      <p class="quest-item-description">{{ quest.description }}</p>

      <!-- Rewards -->
      <div class="quest-rewards">
        <span class="reward xp">
          <span class="reward-icon">&#x2728;</span>
          <span class="reward-value">+{{ quest.xpReward }}</span>
          <span class="reward-label">XP</span>
        </span>
        <span class="reward gold">
          <span class="reward-icon">&#x1F4B0;</span>
          <span class="reward-value">+{{ quest.goldReward }}</span>
          <span class="reward-label">Gold</span>
        </span>
      </div>
    </div>

    <!-- Complete Button -->
    <button
      class="complete-btn"
      @click="emit('complete', quest.id)"
      :disabled="isCompleting"
    >
      <span v-if="isCompleting" class="loading-spinner"></span>
      <span v-else>{{ $t('common.submit') }}</span>
    </button>

    <!-- Reward Animation Overlay -->
    <Transition name="reward-popup">
      <div v-if="showReward" class="reward-popup">
        <div class="reward-popup-content">
          <span class="popup-xp">+{{ reward?.xpGained }} XP</span>
          <span class="popup-gold">+{{ reward?.goldGained }} Gold</span>
          <span v-if="reward?.leveledUp" class="popup-levelup">LEVEL UP!</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Quest } from '@/application/stores/modules/system/gamification.store'

interface QuestReward {
  xpGained?: number
  goldGained?: number
  leveledUp?: boolean
  newLevel?: number
}

interface Props {
  quest: Quest
  isCompleting: boolean
  showReward: boolean
  reward: QuestReward | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  complete: [questId: string]
}>()

const difficultyIcon = computed((): string => {
  switch (props.quest.difficulty) {
    case 'easy': return '\u{1F331}'
    case 'medium': return '\u26A1'
    case 'hard': return '\u{1F525}'
    default: return '\u{1F4DC}'
  }
})

const difficultyLabel = computed((): string => {
  switch (props.quest.difficulty) {
    case 'easy': return 'Einfach'
    case 'medium': return 'Mittel'
    case 'hard': return 'Schwer'
    default: return 'Normal'
  }
})
</script>

<style scoped>
.quest-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--color-background);
  border-radius: 12px;
  border: 1px solid var(--color-border);
  position: relative;
  transition: all 0.3s ease;
}

.quest-item:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

.quest-item.completing {
  opacity: 0.7;
  transform: scale(0.98);
}

/* Quest Icon */
.quest-item-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 20px;
  flex-shrink: 0;
}

.quest-item-icon.easy {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.05) 100%);
}

.quest-item-icon.medium {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(251, 191, 36, 0.05) 100%);
}

.quest-item-icon.hard {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.05) 100%);
}

/* Quest Content */
.quest-item-content {
  flex: 1;
  min-width: 0;
}

.quest-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.quest-item-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.quest-item-description {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 10px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Difficulty Badge */
.difficulty-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.difficulty-badge.easy {
  background: rgba(34, 197, 94, 0.15);
  color: #16a34a;
}

.difficulty-badge.medium {
  background: rgba(251, 191, 36, 0.15);
  color: #d97706;
}

.difficulty-badge.hard {
  background: rgba(239, 68, 68, 0.15);
  color: #dc2626;
}

/* Rewards */
.quest-rewards {
  display: flex;
  gap: 12px;
}

.reward {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.reward-icon {
  font-size: 14px;
}

.reward-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.reward-label {
  color: var(--color-text-muted);
}

.reward.xp .reward-value {
  color: #8b5cf6;
}

.reward.gold .reward-value {
  color: #f59e0b;
}

/* Complete Button */
.complete-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--color-primary) 0%, #818cf8 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
  align-self: center;
  min-width: 80px;
}

.complete-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.complete-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Reward Popup */
.reward-popup {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 12px;
  z-index: 10;
}

.reward-popup-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px;
}

.popup-xp {
  font-size: 18px;
  font-weight: 700;
  color: #a78bfa;
  text-shadow: 0 2px 8px rgba(167, 139, 250, 0.5);
}

.popup-gold {
  font-size: 16px;
  font-weight: 600;
  color: #fbbf24;
  text-shadow: 0 2px 8px rgba(251, 191, 36, 0.5);
}

.popup-levelup {
  font-size: 20px;
  font-weight: 800;
  color: #fbbf24;
  text-shadow: 0 0 20px rgba(251, 191, 36, 0.8);
  animation: pulse 0.5s ease-in-out infinite alternate;
}

@keyframes pulse {
  from { transform: scale(1); }
  to { transform: scale(1.1); }
}

/* Transition */
.reward-popup-enter-active,
.reward-popup-leave-active {
  transition: all 0.3s ease;
}

.reward-popup-enter-from,
.reward-popup-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 640px) {
  .quest-item {
    flex-wrap: wrap;
  }

  .complete-btn {
    width: 100%;
    margin-top: 8px;
  }

  .quest-item-icon {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
}
</style>
