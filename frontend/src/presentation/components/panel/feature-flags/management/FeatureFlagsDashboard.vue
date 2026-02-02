<template>
  <div class="feature-flags-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1 class="dashboard-title">{{ $t('panel.featureFlags.title') }}</h1>
        <p class="dashboard-subtitle">{{ $t('panel.featureFlags.subtitle') }}</p>
      </div>
      <button class="btn-primary" @click="handleCreateFlag">
        {{ $t('panel.featureFlags.createFlag') }}
      </button>
    </div>

    <!-- Tab Navigation -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
        <span v-if="tab.badge" class="badge">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button class="btn-secondary" @click="clearError">
        {{ $t('common.dismiss') }}
      </button>
    </div>

    <!-- Feature Flags Tab -->
    <div v-else-if="activeTab === 'flags'" class="tab-content">
      <FeatureFlagList
        :flags="flags"
        :loading="loading"
        @toggle-flag="handleToggleFlag"
        @edit-flag="handleEditFlag"
        @create-rollout="handleCreateRollout"
      />
    </div>

    <!-- Rollout Plans Tab -->
    <div v-else-if="activeTab === 'rollouts'" class="tab-content">
      <RolloutPlanList
        :plans="rolloutPlans"
        :loading="loading"
        @update-percentage="handleUpdatePercentage"
        @pause="handlePauseRollout"
        @resume="handleResumeRollout"
        @rollback="handleRollbackFeature"
      />
    </div>

    <!-- Analytics Tab -->
    <div v-else-if="activeTab === 'analytics'" class="tab-content">
      <FeatureFlagsAnalytics :flags="flags" :plans="rolloutPlans" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useFeatureFlagsStore } from '@/application/stores/modules/panel/feature-flags.store'
import type { FeatureFlag, RolloutPlan } from '@/application/services/api/admin'
import FeatureFlagList from './FeatureFlagList.vue'
import RolloutPlanList from './RolloutPlanList.vue'
import FeatureFlagsAnalytics from './FeatureFlagsAnalytics.vue'

const { t } = useI18n()
const store = useFeatureFlagsStore()

// State
const activeTab = ref<'flags' | 'rollouts' | 'analytics'>('flags')

// Computed
const flags = computed(() => store.flags)
const rolloutPlans = computed(() => store.rolloutPlans)
const loading = computed(() => store.loading)
const error = computed(() => store.error)

const tabs = computed(() => [
  {
    id: 'flags',
    label: t('panel.featureFlags.flags'),
    badge: store.totalFlags
  },
  {
    id: 'rollouts',
    label: t('panel.featureFlags.rolloutPlans'),
    badge: store.rolloutPlans.length
  },
  {
    id: 'analytics',
    label: t('panel.featureFlags.analytics')
  }
])

// Methods
async function handleCreateFlag() {
  // TODO: Open create flag modal
  console.log('Create flag clicked')
}

async function handleToggleFlag(flag: FeatureFlag) {
  try {
    await store.toggleFlag(flag.feature_id, !flag.is_enabled)
  } catch (err) {
    console.error('Failed to toggle flag:', err)
  }
}

async function handleEditFlag(flag: FeatureFlag) {
  // TODO: Open edit flag modal
  console.log('Edit flag:', flag)
}

async function handleCreateRollout(featureId: string) {
  // TODO: Open create rollout modal
  console.log('Create rollout for feature:', featureId)
}

async function handleUpdatePercentage(planId: string, percentage: number) {
  try {
    await store.updateRolloutPercentage(planId, percentage)
  } catch (err) {
    console.error('Failed to update percentage:', err)
  }
}

async function handlePauseRollout(planId: string) {
  try {
    await store.pauseRollout(planId)
  } catch (err) {
    console.error('Failed to pause rollout:', err)
  }
}

async function handleResumeRollout(planId: string) {
  try {
    await store.resumeRollout(planId)
  } catch (err) {
    console.error('Failed to resume rollout:', err)
  }
}

async function handleRollbackFeature(planId: string) {
  try {
    await store.rollbackFeature(planId)
  } catch (err) {
    console.error('Failed to rollback feature:', err)
  }
}

function clearError() {
  store.clearError()
}

// Lifecycle
onMounted(async () => {
  try {
    await store.fetchFlags()
    await store.fetchRolloutPlans()
  } catch (err) {
    console.error('Failed to load data:', err)
  }
})
</script>

<style scoped>
.feature-flags-dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.dashboard-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: #1f2937;
}

.dashboard-subtitle {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.btn-primary {
  padding: 10px 16px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-secondary {
  padding: 8px 12px;
  background-color: #6b7280;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.tab {
  padding: 12px 16px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  position: relative;
}

.tab:hover {
  color: #3b82f6;
}

.tab.active {
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.badge {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 6px;
  background-color: #e5e7eb;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
}

.tab.active .badge {
  background-color: #3b82f6;
  color: white;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  gap: 16px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-container {
  padding: 16px;
  background-color: #fee2e2;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  margin-bottom: 24px;
}

.error-message {
  color: #991b1b;
  margin: 0 0 12px 0;
  font-size: 14px;
}

.tab-content {
  animation: fadeIn 0.2s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
