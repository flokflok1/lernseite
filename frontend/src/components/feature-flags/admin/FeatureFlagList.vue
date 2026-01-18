<template>
  <div class="feature-flag-list">
    <!-- Search and Filter -->
    <div class="list-controls">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="$t('common.search')"
        class="search-input"
      />
      <select v-model="filterEnabled" class="filter-select">
        <option value="">{{ $t('admin.featureFlags.allFlags') }}</option>
        <option value="enabled">{{ $t('admin.featureFlags.enabledOnly') }}</option>
        <option value="disabled">{{ $t('admin.featureFlags.disabledOnly') }}</option>
      </select>
      <select v-model="filterCategory" class="filter-select">
        <option value="">{{ $t('admin.featureFlags.allCategories') }}</option>
        <option v-for="cat in categories" :key="cat" :value="cat">
          {{ cat }}
        </option>
      </select>
    </div>

    <!-- Flags Table -->
    <div class="table-container">
      <table class="flags-table">
        <thead>
          <tr>
            <th>{{ $t('admin.featureFlags.featureCode') }}</th>
            <th>{{ $t('admin.featureFlags.description') }}</th>
            <th>{{ $t('admin.featureFlags.category') }}</th>
            <th>{{ $t('admin.featureFlags.status') }}</th>
            <th>{{ $t('admin.featureFlags.rolloutPercentage') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="flag in filteredFlags" :key="flag.feature_id" class="flag-row">
            <td class="feature-code">
              <code>{{ flag.feature_code }}</code>
            </td>
            <td class="description">{{ flag.description }}</td>
            <td class="category">
              <span class="category-badge">{{ flag.category }}</span>
            </td>
            <td class="status">
              <label class="toggle-switch">
                <input
                  type="checkbox"
                  :checked="flag.is_enabled"
                  @change="$emit('toggleFlag', flag)"
                />
                <span class="toggle-slider"></span>
              </label>
            </td>
            <td class="rollout-percentage">
              <span v-if="flag.rollout_percentage === 100" class="badge-full">
                {{ $t('admin.featureFlags.fullyRolledOut') }}
              </span>
              <span v-else-if="flag.rollout_percentage > 0" class="badge-partial">
                {{ flag.rollout_percentage }}%
              </span>
              <span v-else class="badge-none">
                {{ $t('admin.featureFlags.notRollingOut') }}
              </span>
            </td>
            <td class="actions">
              <button
                class="btn-small btn-view"
                @click="$emit('editFlag', flag)"
                :title="$t('common.edit')"
              >
                {{ $t('common.edit') }}
              </button>
              <button
                class="btn-small btn-info"
                @click="$emit('createRollout', flag.feature_id)"
                :title="$t('admin.featureFlags.startRollout')"
              >
                {{ $t('admin.featureFlags.rollout') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredFlags.length === 0" class="empty-state">
        <p v-if="flags.length === 0">
          {{ $t('admin.featureFlags.noFlags') }}
        </p>
        <p v-else>
          {{ $t('admin.featureFlags.noMatchingFlags') }}
        </p>
      </div>
    </div>

    <!-- Summary -->
    <div class="summary">
      <div class="summary-item">
        <span class="summary-label">{{ $t('admin.featureFlags.totalFlags') }}:</span>
        <span class="summary-value">{{ flags.length }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">{{ $t('admin.featureFlags.enabledCount') }}:</span>
        <span class="summary-value">{{ enabledCount }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">{{ $t('admin.featureFlags.disabledCount') }}:</span>
        <span class="summary-value">{{ disabledCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FeatureFlag } from '@/api/admin'

const { t } = useI18n()

defineProps<{
  flags: FeatureFlag[]
  loading: boolean
}>()

defineEmits<{
  toggleFlag: [flag: FeatureFlag]
  editFlag: [flag: FeatureFlag]
  createRollout: [featureId: string]
}>()

// State
const searchQuery = ref('')
const filterEnabled = ref('')
const filterCategory = ref('')

// Computed
const categories = computed(() => {
  return Array.from(new Set(props.flags.map((f) => f.category))).sort()
})

const filteredFlags = computed(() => {
  return props.flags.filter((flag) => {
    // Search filter
    if (
      searchQuery.value &&
      !flag.feature_code.toLowerCase().includes(searchQuery.value.toLowerCase()) &&
      !flag.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    ) {
      return false
    }

    // Enabled filter
    if (filterEnabled.value === 'enabled' && !flag.is_enabled) {
      return false
    }
    if (filterEnabled.value === 'disabled' && flag.is_enabled) {
      return false
    }

    // Category filter
    if (filterCategory.value && flag.category !== filterCategory.value) {
      return false
    }

    return true
  })
})

const enabledCount = computed(() => props.flags.filter((f) => f.is_enabled).length)
const disabledCount = computed(() => props.flags.filter((f) => !f.is_enabled).length)
</script>

<style scoped>
.feature-flag-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.list-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.filter-select {
  min-width: 140px;
}

.search-input:focus,
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

.flags-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
}

.flags-table thead {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.flags-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #374151;
}

.flags-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
  transition: background-color 0.2s;
}

.flags-table tbody tr:hover {
  background-color: #f9fafb;
}

.flags-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: #1f2937;
}

.feature-code code {
  background-color: #f3f4f6;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.category-badge {
  display: inline-block;
  padding: 4px 8px;
  background-color: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.toggle-switch {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  display: inline-block;
  width: 44px;
  height: 24px;
  background-color: #d1d5db;
  border-radius: 12px;
  position: relative;
  transition: background-color 0.2s;
}

.toggle-slider::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.2s;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: #10b981;
}

.toggle-switch input:checked + .toggle-slider::after {
  transform: translateX(20px);
}

.badge-full {
  display: inline-block;
  padding: 4px 8px;
  background-color: #d1fae5;
  color: #065f46;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-partial {
  display: inline-block;
  padding: 4px 8px;
  background-color: #fef3c7;
  color: #92400e;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-none {
  display: inline-block;
  padding: 4px 8px;
  background-color: #fee2e2;
  color: #991b1b;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
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
}

.btn-view {
  background-color: #dbeafe;
  color: #1e40af;
}

.btn-view:hover {
  background-color: #bfdbfe;
}

.btn-info {
  background-color: #e0e7ff;
  color: #3730a3;
}

.btn-info:hover {
  background-color: #c7d2fe;
}

.empty-state {
  padding: 48px 16px;
  text-align: center;
  color: #6b7280;
  background-color: #f9fafb;
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
