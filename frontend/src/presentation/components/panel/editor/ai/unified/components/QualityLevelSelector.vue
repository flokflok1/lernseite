<!--
  QualityLevelSelector — Compact dropdown with tooltip details for quality level selection.
  Shown in the AI Editor top bar next to the model selector.
-->
<template>
  <div class="quality-selector" :class="{ open: showDetails }">
    <button
      class="quality-btn"
      :title="currentLevel?.description"
      @click="showDetails = !showDetails"
    >
      <span class="quality-icon">{{ iconMap[currentLevel?.icon ?? 'star'] }}</span>
      <span class="quality-label">{{ currentLevel?.label ?? 'Standard' }}</span>
      <span class="quality-chevron">{{ showDetails ? '▴' : '▾' }}</span>
    </button>

    <Transition name="dropdown">
      <div v-if="showDetails" class="quality-dropdown">
        <button
          v-for="level in levels"
          :key="level.level"
          class="quality-option"
          :class="{ active: level.level === selectedLevel }"
          @click="selectLevel(level.level)"
        >
          <span class="option-icon">{{ iconMap[level.icon] }}</span>
          <div class="option-info">
            <span class="option-label">{{ level.label }}</span>
            <span class="option-desc">{{ level.description }}</span>
          </div>
          <div class="option-meta">
            <span class="option-time">{{ level.estimated_time }}</span>
            <span class="option-ratio">{{ Math.round(level.token_ratio * 100) }}%</span>
          </div>
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue'
import type { useQualityLevel } from '../composables/plan/useQualityLevel'

const qualityLevel = inject<ReturnType<typeof useQualityLevel>>('qualityLevel')
if (!qualityLevel) throw new Error('[QualityLevelSelector] Missing qualityLevel inject')

const { levels, selectedLevel, currentLevel } = qualityLevel

const showDetails = ref(false)

const iconMap: Record<string, string> = {
  zap: '\u26A1',
  star: '\u2B50',
  target: '\uD83C\uDFAF',
  diamond: '\uD83D\uDC8E',
}

function selectLevel(level: string): void {
  qualityLevel.setLevel(level)
  showDetails.value = false
}
</script>

<style scoped>
.quality-selector {
  position: relative;
}

.quality-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.quality-btn:hover {
  border-color: var(--color-primary, #6366f1);
  color: var(--color-primary, #6366f1);
}

.quality-selector.open .quality-btn {
  border-color: var(--color-primary, #6366f1);
  color: var(--color-primary, #6366f1);
}

.quality-icon {
  font-size: 0.8125rem;
}

.quality-label {
  font-size: 0.6875rem;
}

.quality-chevron {
  font-size: 0.5rem;
  opacity: 0.6;
}

.quality-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  z-index: 50;
  min-width: 280px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.quality-option {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: none;
  background: transparent;
  color: var(--color-text-primary);
  cursor: pointer;
  text-align: left;
  transition: background 0.1s;
}

.quality-option:hover {
  background: var(--color-primary-subtle, rgba(99, 102, 241, 0.06));
}

.quality-option.active {
  background: var(--color-primary-subtle, rgba(99, 102, 241, 0.1));
  border-left: 2px solid var(--color-primary, #6366f1);
}

.option-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.option-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.option-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.option-desc {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.option-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  flex-shrink: 0;
  gap: 0.125rem;
}

.option-time {
  font-size: 0.625rem;
  color: var(--color-text-tertiary);
}

.option-ratio {
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--color-primary, #6366f1);
}

/* Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
