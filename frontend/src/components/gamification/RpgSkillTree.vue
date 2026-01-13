<!--
  RPG Skill Tree Component
  Phase G1: RPG Dashboard - Skill-System

  Features:
  - 5 Skill-Nodes mit Abhaengigkeiten
  - Locked/Available/Unlocked States
  - Skillpunkte-Kosten
  - Visuelles Feedback (Glow, Pulse)
  - Effekt-Beschreibungen
-->

<template>
  <div class="rpg-skill-tree">
    <!-- Header -->
    <div class="skill-header">
      <h3 class="skill-title">
        <span class="skill-icon">🌟</span>
        Skillbaum
      </h3>
      <div class="skill-points-display">
        <span class="points-icon">⭐</span>
        <span class="points-value">{{ skillPoints }}</span>
        <span class="points-label">Punkte</span>
      </div>
    </div>

    <!-- Skill Tree Visualization -->
    <div class="skill-tree-container">
      <!-- Connection Lines -->
      <svg class="skill-connections" viewBox="0 0 300 280">
        <!-- Focus to Logic -->
        <line
          x1="75" y1="80"
          x2="75" y2="160"
          :class="['skill-line', { active: isSkillUnlocked('focus') }]"
        />
        <!-- Focus to Endurance -->
        <line
          x1="75" y1="80"
          x2="225" y2="160"
          :class="['skill-line', { active: isSkillUnlocked('focus') }]"
        />
        <!-- Logic to Codemaster -->
        <line
          x1="75" y1="200"
          x2="150" y2="260"
          :class="['skill-line', { active: isSkillUnlocked('logic') }]"
        />
        <!-- Endurance to Codemaster -->
        <line
          x1="225" y1="200"
          x2="150" y2="260"
          :class="['skill-line', { active: isSkillUnlocked('endurance') }]"
        />
      </svg>

      <!-- Skill Nodes -->
      <div class="skill-nodes">
        <!-- Row 1: Focus & Golddigger -->
        <div class="skill-row row-1">
          <div
            class="skill-node"
            :class="getNodeClass('focus')"
            @click="handleSkillClick('focus')"
          >
            <div class="node-glow"></div>
            <div class="node-icon">🎯</div>
            <div class="node-name">Hyper Focus</div>
            <div class="node-cost" v-if="!isSkillUnlocked('focus')">
              {{ getSkillCost('focus') }} ⭐
            </div>
          </div>

          <div
            class="skill-node"
            :class="getNodeClass('golddigger')"
            @click="handleSkillClick('golddigger')"
          >
            <div class="node-glow"></div>
            <div class="node-icon">💰</div>
            <div class="node-name">Goldgraeber</div>
            <div class="node-cost" v-if="!isSkillUnlocked('golddigger')">
              {{ getSkillCost('golddigger') }} ⭐
            </div>
          </div>
        </div>

        <!-- Row 2: Logic & Endurance -->
        <div class="skill-row row-2">
          <div
            class="skill-node"
            :class="getNodeClass('logic')"
            @click="handleSkillClick('logic')"
          >
            <div class="node-glow"></div>
            <div class="node-icon">🧠</div>
            <div class="node-name">Logik-Meister</div>
            <div class="node-cost" v-if="!isSkillUnlocked('logic')">
              {{ getSkillCost('logic') }} ⭐
            </div>
          </div>

          <div
            class="skill-node"
            :class="getNodeClass('endurance')"
            @click="handleSkillClick('endurance')"
          >
            <div class="node-glow"></div>
            <div class="node-icon">💪</div>
            <div class="node-name">Ausdauer</div>
            <div class="node-cost" v-if="!isSkillUnlocked('endurance')">
              {{ getSkillCost('endurance') }} ⭐
            </div>
          </div>
        </div>

        <!-- Row 3: Codemaster -->
        <div class="skill-row row-3">
          <div
            class="skill-node ultimate"
            :class="getNodeClass('codemaster')"
            @click="handleSkillClick('codemaster')"
          >
            <div class="node-glow"></div>
            <div class="node-icon">⚔️</div>
            <div class="node-name">Code-Meister</div>
            <div class="node-cost" v-if="!isSkillUnlocked('codemaster')">
              {{ getSkillCost('codemaster') }} ⭐
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Skill Info -->
    <Transition name="fade">
      <div v-if="selectedSkill" class="skill-info-panel">
        <div class="info-header">
          <span class="info-icon">{{ selectedSkill.icon }}</span>
          <h4 class="info-title">{{ selectedSkill.name }}</h4>
        </div>
        <p class="info-description">{{ selectedSkill.description }}</p>

        <div class="info-details">
          <div class="info-cost">
            <span class="detail-label">Kosten:</span>
            <span class="detail-value">{{ selectedSkill.cost }} Skillpunkte</span>
          </div>
          <div v-if="selectedSkill.requires && selectedSkill.requires.length > 0" class="info-requires">
            <span class="detail-label">Benoetigt:</span>
            <span class="detail-value">{{ getRequirementNames(selectedSkill.requires) }}</span>
          </div>
        </div>

        <button
          v-if="!selectedSkill.unlocked && canUnlock(selectedSkill.id)"
          class="unlock-btn"
          @click="handleUnlock(selectedSkill.id)"
        >
          Freischalten
        </button>
        <div v-else-if="selectedSkill.unlocked" class="unlocked-badge">
          ✓ Freigeschaltet
        </div>
        <div v-else class="locked-message">
          {{ getLockedReason(selectedSkill.id) }}
        </div>
      </div>
    </Transition>

    <!-- Legend -->
    <div class="skill-legend">
      <div class="legend-item">
        <span class="legend-dot locked"></span>
        <span class="legend-label">Gesperrt</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot available"></span>
        <span class="legend-label">Verfuegbar</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot unlocked"></span>
        <span class="legend-label">Freigeschaltet</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGamificationStore } from '@/store/modules/system'
import type { SkillNode } from '@/store/modules/system'

// ============================================================================
// Store
// ============================================================================

const gamificationStore = useGamificationStore()

// ============================================================================
// State
// ============================================================================

const selectedSkill = ref<SkillNode | null>(null)

// ============================================================================
// Computed
// ============================================================================

const skillTree = computed(() => gamificationStore.skillTree)
const skillPoints = computed(() => gamificationStore.stats.skillPoints)
const availableSkills = computed(() => gamificationStore.availableSkills)

// ============================================================================
// Methods
// ============================================================================

const isSkillUnlocked = (skillId: string): boolean => {
  const skill = skillTree.value.find(s => s.id === skillId)
  return skill?.unlocked || false
}

const isSkillAvailable = (skillId: string): boolean => {
  return availableSkills.value.some(s => s.id === skillId)
}

const getSkillCost = (skillId: string): number => {
  const skill = skillTree.value.find(s => s.id === skillId)
  return skill?.cost || 0
}

const getNodeClass = (skillId: string): Record<string, boolean> => {
  const skill = skillTree.value.find(s => s.id === skillId)
  if (!skill) return { locked: true }

  return {
    unlocked: skill.unlocked,
    available: !skill.unlocked && isSkillAvailable(skillId),
    locked: !skill.unlocked && !isSkillAvailable(skillId),
    selected: selectedSkill.value?.id === skillId
  }
}

const handleSkillClick = (skillId: string) => {
  const skill = skillTree.value.find(s => s.id === skillId)
  if (skill) {
    selectedSkill.value = selectedSkill.value?.id === skillId ? null : skill
  }
}

const canUnlock = (skillId: string): boolean => {
  const skill = skillTree.value.find(s => s.id === skillId)
  if (!skill || skill.unlocked) return false

  // Check skill points
  if (skillPoints.value < skill.cost) return false

  // Check requirements
  if (skill.requires && skill.requires.length > 0) {
    return skill.requires.every(reqId => isSkillUnlocked(reqId))
  }

  return true
}

const getLockedReason = (skillId: string): string => {
  const skill = skillTree.value.find(s => s.id === skillId)
  if (!skill) return 'Skill nicht gefunden'

  if (skillPoints.value < skill.cost) {
    return `Benoetigt ${skill.cost} Skillpunkte (${skillPoints.value} vorhanden)`
  }

  if (skill.requires && skill.requires.length > 0) {
    const missing = skill.requires.filter(reqId => !isSkillUnlocked(reqId))
    if (missing.length > 0) {
      return `Benoetigt: ${getRequirementNames(missing)}`
    }
  }

  return 'Nicht verfuegbar'
}

const getRequirementNames = (requireIds: string[]): string => {
  return requireIds
    .map(id => skillTree.value.find(s => s.id === id)?.name || id)
    .join(', ')
}

const handleUnlock = (skillId: string) => {
  const result = gamificationStore.unlockSkill(skillId)

  if (result.success) {
    // Update selected skill to show unlocked state
    const skill = skillTree.value.find(s => s.id === skillId)
    if (skill) {
      selectedSkill.value = { ...skill }
    }
  }
}
</script>

<style scoped>
.rpg-skill-tree {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
}

/* Header */
.skill-header {
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

.skill-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.skill-icon {
  font-size: 20px;
}

.skill-points-display {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.05) 100%);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 20px;
}

.points-icon {
  font-size: 16px;
}

.points-value {
  font-size: 16px;
  font-weight: 700;
  color: #8b5cf6;
}

.points-label {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* Tree Container */
.skill-tree-container {
  position: relative;
  padding: 24px;
  min-height: 320px;
}

/* Connection Lines */
.skill-connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.skill-line {
  stroke: var(--color-border);
  stroke-width: 3;
  stroke-linecap: round;
  transition: stroke 0.3s ease;
}

.skill-line.active {
  stroke: var(--color-primary);
  filter: drop-shadow(0 0 4px var(--color-primary));
}

/* Skill Nodes */
.skill-nodes {
  position: relative;
  z-index: 1;
}

.skill-row {
  display: flex;
  justify-content: center;
  gap: 60px;
  margin-bottom: 32px;
}

.skill-row.row-3 {
  margin-bottom: 0;
}

.skill-node {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-background);
  border: 2px solid var(--color-border);
}

.skill-node.ultimate {
  width: 90px;
  height: 90px;
}

/* Node States */
.skill-node.locked {
  opacity: 0.5;
  filter: grayscale(0.8);
}

.skill-node.available {
  border-color: var(--color-primary);
  animation: pulse-border 2s ease-in-out infinite;
}

.skill-node.unlocked {
  border-color: #fbbf24;
  background: linear-gradient(145deg, rgba(251, 191, 36, 0.1) 0%, var(--color-background) 100%);
  box-shadow: 0 0 20px rgba(251, 191, 36, 0.3);
}

.skill-node.selected {
  transform: scale(1.05);
  box-shadow: 0 0 24px var(--color-primary);
}

.skill-node:hover:not(.locked) {
  transform: scale(1.05);
}

/* Node Glow */
.node-glow {
  position: absolute;
  inset: -4px;
  border-radius: 20px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.skill-node.unlocked .node-glow {
  opacity: 1;
  background: radial-gradient(circle, rgba(251, 191, 36, 0.2) 0%, transparent 70%);
}

.skill-node.available .node-glow {
  opacity: 1;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%);
}

/* Node Content */
.node-icon {
  font-size: 28px;
  margin-bottom: 4px;
}

.node-name {
  font-size: 10px;
  font-weight: 600;
  color: var(--color-text-primary);
  text-align: center;
  line-height: 1.2;
}

.node-cost {
  position: absolute;
  bottom: -8px;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
}

/* Info Panel */
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

/* Legend */
.skill-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 12px;
  background: var(--color-background);
  border-top: 1px solid var(--color-border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 4px;
  border: 2px solid;
}

.legend-dot.locked {
  background: var(--color-background);
  border-color: var(--color-border);
  opacity: 0.5;
}

.legend-dot.available {
  background: var(--color-background);
  border-color: var(--color-primary);
}

.legend-dot.unlocked {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.3) 0%, var(--color-background) 100%);
  border-color: #fbbf24;
}

.legend-label {
  font-size: 11px;
  color: var(--color-text-muted);
}

/* Animations */
@keyframes pulse-border {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(99, 102, 241, 0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (max-width: 640px) {
  .skill-row {
    gap: 40px;
  }

  .skill-node {
    width: 70px;
    height: 70px;
  }

  .skill-node.ultimate {
    width: 80px;
    height: 80px;
  }

  .node-icon {
    font-size: 24px;
  }

  .node-name {
    font-size: 9px;
  }

  .skill-legend {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>
