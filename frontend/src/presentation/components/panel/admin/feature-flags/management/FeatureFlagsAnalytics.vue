<template>
  <div class="feature-flags-analytics">
    <!-- Key Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-value">{{ totalFlags }}</div>
        <div class="metric-label">{{ $t('panel.featureFlags.totalFlags') }}</div>
        <div class="metric-bar">
          <div class="bar-fill" :style="{ width: '100%', backgroundColor: '#3b82f6' }"></div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-value">{{ enabledFlags }}</div>
        <div class="metric-label">{{ $t('panel.featureFlags.enabledCount') }}</div>
        <div class="metric-bar">
          <div
            class="bar-fill"
            :style="{ width: enabledPercentage + '%', backgroundColor: '#10b981' }"
          ></div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-value">{{ disabledFlags }}</div>
        <div class="metric-label">{{ $t('panel.featureFlags.disabledCount') }}</div>
        <div class="metric-bar">
          <div
            class="bar-fill"
            :style="{ width: disabledPercentage + '%', backgroundColor: '#ef4444' }"
          ></div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-value">{{ activeRollouts }}</div>
        <div class="metric-label">{{ $t('panel.featureFlags.activeRollouts') }}</div>
        <div class="metric-bar">
          <div
            class="bar-fill"
            :style="{ width: activeRolloutPercentage + '%', backgroundColor: '#f59e0b' }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Categories Breakdown -->
    <div class="category-section">
      <h3>{{ $t('panel.featureFlags.byCategory') }}</h3>
      <div class="category-list">
        <div v-for="(flags, category) in flagsByCategory" :key="category" class="category-item">
          <div class="category-header">
            <span class="category-name">{{ category }}</span>
            <span class="category-count">{{ flags.length }} {{ $t('panel.featureFlags.flags') }}</span>
          </div>
          <div class="category-bar">
            <div class="bar-container">
              <div
                class="bar-segment enabled"
                :style="{ width: getEnabledPercentage(flags) + '%' }"
                :title="`${getEnabledCount(flags)} enabled`"
              ></div>
              <div
                class="bar-segment disabled"
                :style="{ width: getDisabledPercentage(flags) + '%' }"
                :title="`${getDisabledCount(flags)} disabled`"
              ></div>
            </div>
          </div>
          <div class="category-stats">
            <span class="stat">{{ getEnabledCount(flags) }} {{ $t('panel.featureFlags.enabled') }}</span>
            <span class="stat">{{ getDisabledCount(flags) }} {{ $t('panel.featureFlags.disabled') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Rollout Progress -->
    <div class="rollout-section" v-if="plans.length > 0">
      <h3>{{ $t('panel.featureFlags.rolloutProgress') }}</h3>
      <div class="rollout-list">
        <div v-for="plan in plans" :key="plan.plan_id" class="rollout-item">
          <div class="rollout-header">
            <span class="rollout-name">{{ plan.feature_name }}</span>
            <span class="rollout-percentage">{{ plan.current_percentage }}%</span>
          </div>
          <div class="rollout-bar">
            <div
              class="rollout-progress"
              :style="{ width: plan.current_percentage + '%' }"
              :class="plan.status"
            ></div>
          </div>
          <div class="rollout-footer">
            <span class="rollout-status" :class="plan.status">
              {{ plan.status }}
            </span>
            <span class="rollout-dates">
              {{ formatDate(plan.start_date) }} → {{ formatDate(plan.estimated_end_date) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- No Data Message -->
    <div v-if="totalFlags === 0" class="empty-state">
      <p>{{ $t('panel.featureFlags.noAnalyticsData') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FeatureFlag, RolloutPlan } from '@/application/services/api/panel-admin'

const { t } = useI18n()

defineProps<{
  flags: FeatureFlag[]
  plans: RolloutPlan[]
}>()

// Computed
const totalFlags = computed(() => props.flags.length)
const enabledFlags = computed(() => props.flags.filter((f) => f.is_enabled).length)
const disabledFlags = computed(() => props.flags.filter((f) => !f.is_enabled).length)
const activeRollouts = computed(() => props.plans.filter((p) => p.status === 'in_progress').length)

const enabledPercentage = computed(() => {
  if (totalFlags.value === 0) return 0
  return (enabledFlags.value / totalFlags.value) * 100
})

const disabledPercentage = computed(() => {
  if (totalFlags.value === 0) return 0
  return (disabledFlags.value / totalFlags.value) * 100
})

const activeRolloutPercentage = computed(() => {
  if (props.plans.length === 0) return 0
  return (activeRollouts.value / props.plans.length) * 100
})

const flagsByCategory = computed(() => {
  const categories: Record<string, FeatureFlag[]> = {}
  props.flags.forEach((flag) => {
    const category = flag.category || 'uncategorized'
    if (!categories[category]) {
      categories[category] = []
    }
    categories[category].push(flag)
  })
  return categories
})

// Methods
function getEnabledCount(flags: FeatureFlag[]): number {
  return flags.filter((f) => f.is_enabled).length
}

function getDisabledCount(flags: FeatureFlag[]): number {
  return flags.filter((f) => !f.is_enabled).length
}

function getEnabledPercentage(flags: FeatureFlag[]): number {
  if (flags.length === 0) return 0
  return (getEnabledCount(flags) / flags.length) * 100
}

function getDisabledPercentage(flags: FeatureFlag[]): number {
  if (flags.length === 0) return 0
  return (getDisabledCount(flags) / flags.length) * 100
}

function formatDate(date: string | null): string {
  if (!date) return '-'
  return new Date(date).toLocaleDateString()
}
</script>

<style scoped>
.feature-flags-analytics {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.metric-card {
  padding: 20px;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.2s;
}

.metric-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
  font-weight: 500;
}

.metric-bar {
  height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

/* Categories Section */
.category-section {
  padding: 24px;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.category-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #1f2937;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.category-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.category-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 14px;
}

.category-count {
  font-size: 12px;
  color: #6b7280;
}

.category-bar {
  height: 20px;
}

.bar-container {
  display: flex;
  height: 100%;
  border-radius: 4px;
  overflow: hidden;
  background-color: #e5e7eb;
}

.bar-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.bar-segment.enabled {
  background-color: #10b981;
}

.bar-segment.disabled {
  background-color: #ef4444;
}

.category-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #6b7280;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Rollout Section */
.rollout-section {
  padding: 24px;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.rollout-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #1f2937;
}

.rollout-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rollout-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 6px;
}

.rollout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rollout-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 14px;
}

.rollout-percentage {
  font-weight: 600;
  color: #3b82f6;
  font-size: 14px;
}

.rollout-bar {
  height: 8px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.rollout-progress {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.rollout-progress.in_progress {
  background-color: #3b82f6;
}

.rollout-progress.completed {
  background-color: #10b981;
}

.rollout-progress.paused {
  background-color: #f59e0b;
}

.rollout-progress.rolled_back {
  background-color: #ef4444;
}

.rollout-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.rollout-status {
  font-weight: 500;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 3px;
}

.rollout-status.in_progress {
  background-color: #dbeafe;
  color: #1e40af;
}

.rollout-status.completed {
  background-color: #d1fae5;
  color: #065f46;
}

.rollout-status.paused {
  background-color: #fef3c7;
  color: #92400e;
}

.rollout-status.rolled_back {
  background-color: #fee2e2;
  color: #991b1b;
}

.rollout-dates {
  color: #6b7280;
}

/* Empty State */
.empty-state {
  padding: 48px 16px;
  text-align: center;
  color: #6b7280;
  background-color: #f9fafb;
  border-radius: 8px;
}
</style>
