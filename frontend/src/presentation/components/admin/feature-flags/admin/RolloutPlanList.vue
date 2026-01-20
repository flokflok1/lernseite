<template>
  <div class="rollout-plan-list">
    <!-- Filter -->
    <div class="list-controls">
      <select v-model="filterStatus" class="filter-select">
        <option value="">{{ $t('admin.featureFlags.allStatuses') }}</option>
        <option value="in_progress">{{ $t('admin.featureFlags.inProgress') }}</option>
        <option value="completed">{{ $t('admin.featureFlags.completed') }}</option>
        <option value="paused">{{ $t('admin.featureFlags.paused') }}</option>
        <option value="rolled_back">{{ $t('admin.featureFlags.rolledBack') }}</option>
      </select>
    </div>

    <!-- Plans Table -->
    <div class="table-container">
      <table class="plans-table">
        <thead>
          <tr>
            <th>{{ $t('admin.featureFlags.featureName') }}</th>
            <th>{{ $t('admin.featureFlags.status') }}</th>
            <th>{{ $t('admin.featureFlags.currentPercentage') }}</th>
            <th>{{ $t('admin.featureFlags.targetPercentage') }}</th>
            <th>{{ $t('admin.featureFlags.startDate') }}</th>
            <th>{{ $t('admin.featureFlags.estimatedEndDate') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="plan in filteredPlans" :key="plan.plan_id" class="plan-row">
            <td class="feature-name">{{ plan.feature_name }}</td>
            <td class="status">
              <span :class="['status-badge', plan.status]">
                {{ plan.status }}
              </span>
            </td>
            <td class="percentage">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: plan.current_percentage + '%' }">
                  <span class="progress-text">{{ plan.current_percentage }}%</span>
                </div>
              </div>
            </td>
            <td class="target-percentage">{{ plan.target_percentage }}%</td>
            <td class="date">{{ formatDate(plan.start_date) }}</td>
            <td class="date">{{ formatDate(plan.estimated_end_date) }}</td>
            <td class="actions">
              <button
                v-if="plan.status === 'in_progress'"
                class="btn-small btn-info"
                @click="showPercentageDialog(plan)"
                :title="$t('admin.featureFlags.updatePercentage')"
              >
                {{ $t('admin.featureFlags.update') }}
              </button>
              <button
                v-if="plan.status === 'in_progress'"
                class="btn-small btn-warning"
                @click="$emit('pause', plan.plan_id)"
                :title="$t('admin.featureFlags.pauseRollout')"
              >
                {{ $t('admin.featureFlags.pause') }}
              </button>
              <button
                v-if="plan.status === 'paused'"
                class="btn-small btn-success"
                @click="$emit('resume', plan.plan_id)"
                :title="$t('admin.featureFlags.resumeRollout')"
              >
                {{ $t('admin.featureFlags.resume') }}
              </button>
              <button
                v-if="plan.status !== 'rolled_back'"
                class="btn-small btn-danger"
                @click="$emit('rollback', plan.plan_id)"
                :title="$t('admin.featureFlags.rollbackFeature')"
              >
                {{ $t('admin.featureFlags.rollback') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredPlans.length === 0" class="empty-state">
        <p v-if="plans.length === 0">
          {{ $t('admin.featureFlags.noRolloutPlans') }}
        </p>
        <p v-else>
          {{ $t('admin.featureFlags.noMatchingPlans') }}
        </p>
      </div>
    </div>

    <!-- Percentage Update Dialog -->
    <div v-if="selectedPlan" class="dialog-overlay" @click="selectedPlan = null">
      <div class="dialog" @click.stop>
        <h2>{{ $t('admin.featureFlags.updatePercentage') }}</h2>
        <p>{{ $t('admin.featureFlags.updatePercentageHelp') }}</p>

        <div class="percentage-options">
          <button
            v-for="pct in [5, 25, 50, 100]"
            :key="pct"
            class="percentage-btn"
            @click="confirmPercentageUpdate(pct)"
          >
            {{ pct }}%
          </button>
        </div>

        <div class="dialog-footer">
          <button class="btn-secondary" @click="selectedPlan = null">
            {{ $t('common.cancel') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div class="summary">
      <div class="summary-item">
        <span class="summary-label">{{ $t('admin.featureFlags.activeRollouts') }}:</span>
        <span class="summary-value">{{ activeRolloutsCount }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">{{ $t('admin.featureFlags.completedRollouts') }}:</span>
        <span class="summary-value">{{ completedRolloutsCount }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">{{ $t('admin.featureFlags.pausedRollouts') }}:</span>
        <span class="summary-value">{{ pausedRolloutsCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { RolloutPlan } from '@/infrastructure/api/clients/admin'

const { t } = useI18n()

defineProps<{
  plans: RolloutPlan[]
  loading: boolean
}>()

const emit = defineEmits<{
  updatePercentage: [planId: string, percentage: number]
  pause: [planId: string]
  resume: [planId: string]
  rollback: [planId: string]
}>()

// State
const filterStatus = ref('')
const selectedPlan = ref<RolloutPlan | null>(null)

// Computed
const filteredPlans = computed(() => {
  if (!filterStatus.value) {
    return props.plans
  }
  return props.plans.filter((plan) => plan.status === filterStatus.value)
})

const activeRolloutsCount = computed(
  () => props.plans.filter((p) => p.status === 'in_progress').length
)
const completedRolloutsCount = computed(
  () => props.plans.filter((p) => p.status === 'completed').length
)
const pausedRolloutsCount = computed(
  () => props.plans.filter((p) => p.status === 'paused').length
)

// Methods
function formatDate(date: string | null): string {
  if (!date) return '-'
  return new Date(date).toLocaleDateString()
}

function showPercentageDialog(plan: RolloutPlan) {
  selectedPlan.value = plan
}

function confirmPercentageUpdate(percentage: number) {
  if (selectedPlan.value) {
    emit('updatePercentage', selectedPlan.value.plan_id, percentage)
    selectedPlan.value = null
  }
}
</script>

<style scoped>
.rollout-plan-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.list-controls {
  display: flex;
  gap: 12px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  min-width: 140px;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.table-container {
  overflow-x: auto;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}

.plans-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
}

.plans-table thead {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.plans-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #374151;
}

.plans-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
  transition: background-color 0.2s;
}

.plans-table tbody tr:hover {
  background-color: #f9fafb;
}

.plans-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #1f2937;
}

.feature-name {
  font-weight: 500;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.in_progress {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.completed {
  background-color: #d1fae5;
  color: #065f46;
}

.status-badge.paused {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.rolled_back {
  background-color: #fee2e2;
  color: #991b1b;
}

.progress-bar {
  width: 100%;
  height: 24px;
  background-color: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background-color: #3b82f6;
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.actions {
  display: flex;
  gap: 8px;
}

.btn-small {
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-info {
  background-color: #e0e7ff;
  color: #3730a3;
}

.btn-info:hover {
  background-color: #c7d2fe;
}

.btn-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.btn-warning:hover {
  background-color: #fde68a;
}

.btn-success {
  background-color: #d1fae5;
  color: #065f46;
}

.btn-success:hover {
  background-color: #a7f3d0;
}

.btn-danger {
  background-color: #fee2e2;
  color: #991b1b;
}

.btn-danger:hover {
  background-color: #fecaca;
}

.empty-state {
  padding: 48px 16px;
  text-align: center;
  color: #6b7280;
  background-color: #f9fafb;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.dialog h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #1f2937;
}

.dialog p {
  margin: 0 0 16px 0;
  color: #6b7280;
  font-size: 14px;
}

.percentage-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.percentage-btn {
  padding: 10px;
  border: 1px solid #d1d5db;
  background-color: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.percentage-btn:hover {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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

.summary {
  display: flex;
  gap: 24px;
  padding: 16px;
  background-color: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-weight: 500;
  color: #6b7280;
  font-size: 14px;
}

.summary-value {
  font-weight: 700;
  color: #1f2937;
  font-size: 18px;
}
</style>
