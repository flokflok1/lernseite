<!--
  RPG Quest List Component
  Phase G1: RPG Dashboard - Quest-System

  Features:
  - Liste aller aktiven Quests
  - Difficulty Badges (Einfach/Mittel/Schwer)
  - XP & Gold Belohnungen
  - Quest abgeben Button
  - Visuelles Feedback bei Abschluss
-->

<template>
  <div class="rpg-quest-list">
    <!-- Header -->
    <div class="quest-header">
      <h3 class="quest-title">
        <span class="quest-icon">📜</span>
        Lern-Quests
      </h3>
      <div class="quest-counter">
        <span class="active-count">{{ activeQuests.length }}</span>
        <span class="count-label">aktiv</span>
      </div>
    </div>

    <!-- Quest List -->
    <div class="quest-content">
      <!-- Empty State -->
      <div v-if="activeQuests.length === 0" class="empty-state">
        <span class="empty-icon">🎉</span>
        <p class="empty-text">Alle Quests abgeschlossen!</p>
        <p class="empty-hint">Schreibe dich in neue Kurse ein, um mehr Quests freizuschalten.</p>
      </div>

      <!-- Quest Items -->
      <TransitionGroup name="quest" tag="div" class="quest-items">
        <div
          v-for="quest in activeQuests"
          :key="quest.id"
          class="quest-item"
          :class="{ 'completing': completingQuestId === quest.id }"
        >
          <!-- Quest Icon -->
          <div class="quest-item-icon" :class="quest.difficulty">
            <span>{{ quest.icon || getDifficultyIcon(quest.difficulty) }}</span>
          </div>

          <!-- Quest Content -->
          <div class="quest-item-content">
            <div class="quest-item-header">
              <h4 class="quest-item-title">{{ quest.title }}</h4>
              <span class="difficulty-badge" :class="quest.difficulty">
                {{ getDifficultyLabel(quest.difficulty) }}
              </span>
            </div>
            <p class="quest-item-description">{{ quest.description }}</p>

            <!-- Rewards -->
            <div class="quest-rewards">
              <span class="reward xp">
                <span class="reward-icon">✨</span>
                <span class="reward-value">+{{ quest.xpReward }}</span>
                <span class="reward-label">XP</span>
              </span>
              <span class="reward gold">
                <span class="reward-icon">💰</span>
                <span class="reward-value">+{{ quest.goldReward }}</span>
                <span class="reward-label">Gold</span>
              </span>
            </div>
          </div>

          <!-- Complete Button -->
          <button
            class="complete-btn"
            @click="handleCompleteQuest(quest.id)"
            :disabled="completingQuestId === quest.id"
          >
            <span v-if="completingQuestId === quest.id" class="loading-spinner"></span>
            <span v-else>Abgeben</span>
          </button>

          <!-- Reward Animation Overlay -->
          <Transition name="reward-popup">
            <div v-if="showRewardPopup && rewardPopupQuestId === quest.id" class="reward-popup">
              <div class="reward-popup-content">
                <span class="popup-xp">+{{ lastReward?.xpGained }} XP</span>
                <span class="popup-gold">+{{ lastReward?.goldGained }} Gold</span>
                <span v-if="lastReward?.leveledUp" class="popup-levelup">LEVEL UP!</span>
              </div>
            </div>
          </Transition>
        </div>
      </TransitionGroup>
    </div>

    <!-- Completed Quests Toggle -->
    <div v-if="completedQuests.length > 0" class="completed-section">
      <button class="toggle-completed" @click="showCompleted = !showCompleted">
        <span class="toggle-icon">{{ showCompleted ? '▼' : '▶' }}</span>
        <span>Abgeschlossen ({{ completedQuests.length }})</span>
      </button>

      <Transition name="slide">
        <div v-if="showCompleted" class="completed-list">
          <div
            v-for="quest in completedQuests"
            :key="quest.id"
            class="quest-item completed"
          >
            <div class="quest-item-icon completed">
              <span>✅</span>
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
import { useGamificationStore } from '@/store/gamification.store'
import type { Quest, QuestDifficulty } from '@/store/gamification.store'

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

const getDifficultyIcon = (difficulty: QuestDifficulty): string => {
  switch (difficulty) {
    case 'easy': return '🌱'
    case 'medium': return '⚡'
    case 'hard': return '🔥'
    default: return '📜'
  }
}

const getDifficultyLabel = (difficulty: QuestDifficulty): string => {
  switch (difficulty) {
    case 'easy': return 'Einfach'
    case 'medium': return 'Mittel'
    case 'hard': return 'Schwer'
    default: return 'Normal'
  }
}

const handleCompleteQuest = async (questId: string) => {
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

.quest-item-icon.easy {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.05) 100%);
}

.quest-item-icon.medium {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(251, 191, 36, 0.05) 100%);
}

.quest-item-icon.hard {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.05) 100%);
}

.quest-item-icon.completed {
  background: var(--color-surface);
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

.quest-rewards.small {
  gap: 8px;
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

.reward-popup-enter-active,
.reward-popup-leave-active {
  transition: all 0.3s ease;
}

.reward-popup-enter-from,
.reward-popup-leave-to {
  opacity: 0;
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
