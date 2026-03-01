<!--
  RPG Quest List Component
  Phase G1: RPG Dashboard - Quest-System

  Features:
  - Liste aller aktiven Quests
  - Difficulty Badges (Einfach/Mittel/Schwer)
  - XP & Gold Belohnungen
  - Quest abgeben Button
  - Visuelles Feedback bei Abschluss

  Delegates individual quest rendering to RpgQuestItem.vue
-->

<template>
  <div class="rpg-quest-list">
    <!-- Header -->
    <div class="quest-header">
      <h3 class="quest-title">
        <span class="quest-icon">&#x1F4DC;</span>
        {{ $t('gamification.quests.title') }}
      </h3>
      <div class="quest-counter">
        <span class="active-count">{{ activeQuests.length }}</span>
        <span class="count-label">{{ $t('gamification.quests.active') }}</span>
      </div>
    </div>

    <!-- Quest List -->
    <div class="quest-content">
      <!-- Empty State -->
      <div v-if="activeQuests.length === 0" class="empty-state">
        <span class="empty-icon">&#x1F389;</span>
        <p class="empty-text">{{ $t('gamification.quests.allCompleted') }}</p>
        <p class="empty-hint">{{ $t('gamification.quests.enrollHint') }}</p>
      </div>

      <!-- Quest Items -->
      <TransitionGroup name="quest" tag="div" class="quest-items">
        <RpgQuestItem
          v-for="quest in activeQuests"
          :key="quest.id"
          :quest="quest"
          :is-completing="completingQuestId === quest.id"
          :show-reward="showRewardPopup && rewardPopupQuestId === quest.id"
          :reward="lastReward"
          @complete="handleCompleteQuest"
        />
      </TransitionGroup>
    </div>

    <!-- Completed Quests Toggle -->
    <div v-if="completedQuests.length > 0" class="completed-section">
      <button class="toggle-completed" @click="showCompleted = !showCompleted">
        <span class="toggle-icon">{{ showCompleted ? '\u25BC' : '\u25B6' }}</span>
        <span>{{ $t('gamification.quests.completed') }} ({{ completedQuests.length }})</span>
      </button>

      <Transition name="slide">
        <div v-if="showCompleted" class="completed-list">
          <div
            v-for="quest in completedQuests"
            :key="quest.id"
            class="quest-item completed"
          >
            <div class="quest-item-icon completed">
              <span>&#x2705;</span>
            </div>
            <div class="quest-item-content">
              <h4 class="quest-item-title">{{ quest.title }}</h4>
              <div class="quest-rewards small">
                <span class="reward xp">+{{ quest.xpReward }} XP</span>
                <span class="reward gold">+{{ quest.goldReward }} Gold</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGamificationStore } from '@/application/stores/modules/system/gamification.store'
import type { Quest } from '@/application/stores/modules/system/gamification.store'
import RpgQuestItem from './RpgQuestItem.vue'

// ============================================================================
// Store
// ============================================================================

const gamificationStore = useGamificationStore()

// ============================================================================
// State
// ============================================================================

const completingQuestId = ref<string | null>(null)
const showRewardPopup = ref(false)
const rewardPopupQuestId = ref<string | null>(null)
const showCompleted = ref(false)
const lastReward = ref<{
  xpGained?: number
  goldGained?: number
  leveledUp?: boolean
  newLevel?: number
} | null>(null)

// ============================================================================
// Computed
// ============================================================================

const activeQuests = computed<Quest[]>(() => gamificationStore.activeQuests)
const completedQuests = computed<Quest[]>(() => gamificationStore.completedQuests)

// ============================================================================
// Methods
// ============================================================================

async function handleCompleteQuest(questId: string): Promise<void> {
  completingQuestId.value = questId

  // Simulate slight delay for animation
  await new Promise(resolve => setTimeout(resolve, 300))

  const result = gamificationStore.completeQuest(questId)

  if (result.success) {
    lastReward.value = result
    rewardPopupQuestId.value = questId
    showRewardPopup.value = true

    // Hide popup after animation
    setTimeout(() => {
      showRewardPopup.value = false
      rewardPopupQuestId.value = null
    }, 2000)
  }

  completingQuestId.value = null
}
</script>

<style scoped>
.rpg-quest-list {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
}

/* Header */
.quest-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(
    145deg,
    var(--color-background) 0%,
    var(--color-surface) 100%
  );
  border-bottom: 1px solid var(--color-border);
}

.quest-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.quest-icon {
  font-size: 20px;
}

.quest-counter {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: var(--color-primary);
  border-radius: 20px;
}

.active-count {
  font-size: 14px;
  font-weight: 700;
  color: white;
}

.count-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

/* Content */
.quest-content {
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}

/* Quest Items */
.quest-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Completed Quest Items (inline since they are simpler than active quests) */
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

.quest-item.completed {
  opacity: 0.6;
  background: transparent;
  border: 1px dashed var(--color-border);
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

.quest-item-icon.completed {
  background: var(--color-surface);
}

/* Quest Content */
.quest-item-content {
  flex: 1;
  min-width: 0;
}

.quest-item-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

/* Rewards */
.quest-rewards {
  display: flex;
  gap: 12px;
}

.quest-rewards.small {
  gap: 8px;
}

.reward {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.reward.xp {
  color: #8b5cf6;
  font-weight: 600;
}

.reward.gold {
  color: #f59e0b;
  font-weight: 600;
}

/* Completed Section */
.completed-section {
  border-top: 1px solid var(--color-border);
  padding: 12px 16px;
}

.toggle-completed {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 0;
}

.toggle-completed:hover {
  color: var(--color-text-primary);
}

.toggle-icon {
  font-size: 10px;
}

.completed-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* Transitions */
.quest-enter-active,
.quest-leave-active {
  transition: all 0.3s ease;
}

.quest-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.quest-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

/* Scrollbar */
.quest-content::-webkit-scrollbar {
  width: 6px;
}

.quest-content::-webkit-scrollbar-track {
  background: transparent;
}

.quest-content::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

.quest-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-muted);
}

/* Responsive */
@media (max-width: 640px) {
  .quest-item {
    flex-wrap: wrap;
  }

  .quest-item-icon {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
}
</style>
