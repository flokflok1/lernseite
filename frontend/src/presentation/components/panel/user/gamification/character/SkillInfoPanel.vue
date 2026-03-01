<!--
  SkillInfoPanel - Selected skill detail panel
  Displays skill description, cost, requirements, and unlock action.
-->

<template>
  <div class="skill-info-panel">
    <div class="info-header">
      <span class="info-icon">{{ skill.icon }}</span>
      <h4 class="info-title">{{ skill.name }}</h4>
    </div>
    <p class="info-description">{{ skill.description }}</p>

    <div class="info-details">
      <div class="info-cost">
        <span class="detail-label">Kosten:</span>
        <span class="detail-value">{{ skill.cost }} Skillpunkte</span>
      </div>
      <div v-if="skill.requires && skill.requires.length > 0" class="info-requires">
        <span class="detail-label">Benoetigt:</span>
        <span class="detail-value">{{ requirementNames }}</span>
      </div>
    </div>

    <button
      v-if="!skill.unlocked && unlockable"
      class="unlock-btn"
      @click="emit('unlock', skill.id)"
    >
      Freischalten
    </button>
    <div v-else-if="skill.unlocked" class="unlocked-badge">
      &#x2713; Freigeschaltet
    </div>
    <div v-else class="locked-message">
      {{ lockedReason }}
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SkillInfoPanel
 *
 * Displays the detail panel for a selected skill node in the RPG skill tree.
 */

import type { SkillNode } from '@/application/stores/modules/system/gamification.store'

interface Props {
  skill: SkillNode
  unlockable: boolean
  lockedReason: string
  requirementNames: string
}

defineProps<Props>()

const emit = defineEmits<{
  unlock: [skillId: string]
}>()
</script>

<style scoped>
.skill-info-panel {
  margin: 0 16px 16px;
  padding: 16px;
  background: var(--color-background);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.info-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.info-icon {
  font-size: 24px;
}

.info-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.info-description {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.info-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 12px;
}

.info-cost,
.info-requires {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.detail-label {
  color: var(--color-text-muted);
  margin-right: 4px;
}

.detail-value {
  font-weight: 600;
  color: var(--color-text-primary);
}

.unlock-btn {
  width: 100%;
  padding: 10px;
  background: linear-gradient(135deg, var(--color-primary) 0%, #818cf8 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.unlock-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.unlocked-badge {
  text-align: center;
  padding: 10px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, var(--color-background) 100%);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #16a34a;
}

.locked-message {
  text-align: center;
  padding: 10px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--color-text-muted);
}
</style>
