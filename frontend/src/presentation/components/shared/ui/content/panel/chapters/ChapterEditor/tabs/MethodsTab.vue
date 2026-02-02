<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MethodGroupStats, GroupInfo } from '../types'

interface Props {
  methodStats: Record<string, MethodGroupStats>
  isLoading: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'open-editor': [group: string]
}>()

const { t } = useI18n()

// Computed
const groups = computed(() => ['A', 'B', 'C', 'D'])

const getGroupColor = (group: string) => {
  const colors: Record<string, { bg: string; border: string }> = {
    A: { bg: '#dbeafe', border: '#0ea5e9' },
    B: { bg: '#dcfce7', border: '#22c55e' },
    C: { bg: '#fef3c7', border: '#eab308' },
    D: { bg: '#f3e8ff', border: '#a855f7' }
  }
  return colors[group] || colors.A
}

const getGroupName = (group: string) => {
  const names: Record<string, string> = {
    A: t('features.chapterEditor.groups.A'),
    B: t('features.chapterEditor.groups.B'),
    C: t('features.chapterEditor.groups.C'),
    D: t('features.chapterEditor.groups.D')
  }
  return names[group] || group
}

const getTierBadge = (group: string) => {
  const tiers: Record<string, string> = {
    A: 'Basic',
    B: 'Basic',
    C: 'Premium',
    D: 'Pro'
  }
  return tiers[group] || 'Basic'
}

// Methods
const handleOpenEditor = (group: string) => {
  emit('open-editor', group)
}

const getProgressPercentage = (active: number, total: number): number => {
  if (total === 0) return 0
  return Math.round((active / total) * 100)
}
</script>

<template>
  <div class="methods-tab">
    <div class="methods-header">
      <h3>{{ $t('features.chapterEditor.tabs.methods') }}</h3>
      <p class="text-muted">{{ $t('features.chapterEditor.info.methodsInfo') }}</p>
    </div>

    <div v-if="isLoading" class="loading-state">
      <span class="loader">⏳</span>
      {{ $t('common.loading') }}
    </div>

    <div v-else class="methods-grid">
      <div
        v-for="group in groups"
        :key="group"
        class="method-group-card"
        :style="{
          borderColor: getGroupColor(group).border,
          backgroundColor: getGroupColor(group).bg
        }"
      >
        <div class="card-header">
          <div class="group-title">
            <h4>{{ getGroupName(group) }}</h4>
            <span class="tier-badge">{{ getTierBadge(group) }}</span>
          </div>
        </div>

        <div class="card-body">
          <!-- Total Methods -->
          <div class="stat-item">
            <span class="stat-label">{{ $t('features.chapterEditor.stats.total') }}</span>
            <span class="stat-value">{{ methodStats[group]?.total || 0 }}</span>
          </div>

          <!-- Active Methods -->
          <div class="stat-item">
            <span class="stat-label">{{ $t('features.chapterEditor.stats.active') }}</span>
            <span class="stat-value">{{ methodStats[group]?.active || 0 }}</span>
          </div>

          <!-- Published Methods -->
          <div class="stat-item">
            <span class="stat-label">{{ $t('features.chapterEditor.stats.published') }}</span>
            <span class="stat-value">{{ methodStats[group]?.published || 0 }}</span>
          </div>

          <!-- Progress Bar -->
          <div class="progress-wrapper">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{
                  width: getProgressPercentage(
                    methodStats[group]?.active || 0,
                    methodStats[group]?.total || 0
                  ) + '%'
                }"
              />
            </div>
            <span class="progress-text">
              {{ getProgressPercentage(
                methodStats[group]?.active || 0,
                methodStats[group]?.total || 0
              ) }}%
            </span>
          </div>
        </div>

        <div class="card-footer">
          <button
            class="btn btn-secondary btn-sm"
            @click="handleOpenEditor(group)"
          >
            <span class="icon">✏️</span>
            {{ $t('features.chapterEditor.buttons.editMethods') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.methods-tab {
  padding: 1rem;
}

.methods-header {
  margin-bottom: 1.5rem;
}

.methods-header h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  color: var(--color-text-primary);
}

.text-muted {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.methods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.method-group-card {
  border: 2px solid;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.method-group-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.group-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.group-title h4 {
  margin: 0;
  font-size: 1rem;
  color: var(--color-text-primary);
}

.tier-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.card-body {
  padding: 1rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-top: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #06b6d4);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 3rem;
  text-align: right;
}

.card-footer {
  padding: 0.75rem 1rem;
  background-color: rgba(0, 0, 0, 0.02);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.btn {
  padding: 0.4rem 0.6rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.btn-secondary {
  background-color: var(--color-primary);
  color: white;
}

.btn-secondary:hover {
  background-color: var(--color-primary-dark);
}

.btn-sm {
  padding: 0.35rem 0.5rem;
  font-size: 0.8rem;
}

.icon {
  font-size: 0.95rem;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.loader {
  font-size: 1.25rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
