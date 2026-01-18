<script setup lang="ts">
/**
 * ComparisonPanel Component
 *
 * Side-by-side comparison of frontend JSON vs database translations
 * Allows admin to review and resolve changes in MANUAL mode
 * Shows similarity scores and automatically suggests actions
 */

import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSyncManager } from '@/features/admin/useSyncManager'
import type { ResolutionAction } from '../types/sync.types'

interface Props {
  syncId: string
}

defineProps<Props>()

const { t } = useI18n()
const {
  selectedMode,
  selectedCategory,
  comparisonPanel,
  paginatedComparisonItems,
  comparisonPage,
  comparisonTotalPages,
  comparisonPageSize,
  pendingResolutionsCount,
  conflictsCount,
  isLoadingComparison,
  canApply,
  resolutions,
  isApplying,
  applyError,
  getComparisonPanel,
  setResolution,
  clearResolution,
  applySync
} = useSyncManager()

// Local UI state
const expandedItems = ref<Set<string>>(new Set())
const showApplyConfirm = ref(false)

// ============================================================================
// LIFECYCLE
// ============================================================================

onMounted(async () => {
  await getComparisonPanel(true)
})

// ============================================================================
// COMPUTED
// ============================================================================

const categories = computed(() => {
  if (!comparisonPanel?.categories) return []
  return comparisonPanel.categories
})

const categoryOptions = computed(() => {
  return categories.value.map(cat => ({
    label: t(`admin.i18n.category_${cat.category.toLowerCase()}`),
    value: cat.category,
    icon: getCategoryIcon(cat.category),
    count: cat.count
  }))
})

// ============================================================================
// METHODS
// ============================================================================

function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    NEW_KEYS: '➕',
    CHANGED_KEYS: '✏️',
    DELETED_KEYS: '🗑️',
    CONFLICTS: '⚠️'
  }
  return icons[category] || '📌'
}

function getSimilarityColor(similarity: number): string {
  if (similarity >= 0.95) return 'high'
  if (similarity >= 0.9) return 'medium'
  return 'low'
}

function toggleExpand(itemId: string) {
  if (expandedItems.value.has(itemId)) {
    expandedItems.value.delete(itemId)
  } else {
    expandedItems.value.add(itemId)
  }
}

async function handleCategorySelect(category: string) {
  selectedCategory.value = category === selectedCategory.value ? null : category
  await getComparisonPanel(true)
}

async function handlePageChange(newPage: number) {
  comparisonPage.value = newPage
  await getComparisonPanel(false)
}

function handleSetResolution(
  detailId: string,
  action: ResolutionAction,
  manualValue?: string
) {
  setResolution(detailId, action, manualValue)
}

function handleClearResolution(detailId: string) {
  clearResolution(detailId)
}

async function handleApplySync() {
  try {
    showApplyConfirm.value = false
    await applySync()
  } catch (err) {
    console.error('Failed to apply sync:', err)
  }
}

function getResolutionStatus(detailId: string): string {
  const resolution = resolutions[detailId]
  if (!resolution) return 'pending'
  return 'resolved'
}
</script>

<template>
  <div class="comparison-panel">
    <!-- Status Bar -->
    <div class="status-bar">
      <div class="status-left">
        <span class="status-info">
          <strong>{{ pendingResolutionsCount }}</strong>
          {{ $t('admin.i18n.pending_resolutions') }}
        </span>
        <span class="status-separator">•</span>
        <span class="status-info warning">
          <strong>{{ conflictsCount }}</strong>
          {{ $t('admin.i18n.conflicts') }}
        </span>
      </div>

      <button
        class="btn btn-primary"
        :disabled="!canApply || isApplying"
        @click="showApplyConfirm = true"
      >
        <span v-if="isApplying" class="spinner-small"></span>
        {{ $t('admin.i18n.apply_changes') }}
      </button>
    </div>

    <!-- Error Alert -->
    <div v-if="applyError" class="alert alert-error">
      <span class="alert-icon">⚠️</span>
      <span class="alert-message">{{ applyError }}</span>
    </div>

    <!-- Category Filter -->
    <div class="category-filter">
      <button
        v-for="cat in categoryOptions"
        :key="cat.value"
        class="category-button"
        :class="{ active: selectedCategory === cat.value }"
        @click="handleCategorySelect(cat.value)"
      >
        <span class="category-icon">{{ cat.icon }}</span>
        <span class="category-label">{{ cat.label }}</span>
        <span class="category-count">{{ cat.count }}</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoadingComparison" class="loading">
      <span class="spinner"></span>
      {{ $t('common.loading') }}
    </div>

    <!-- Comparison Items -->
    <div v-else-if="paginatedComparisonItems.length > 0" class="items-list">
      <div
        v-for="(item, index) in paginatedComparisonItems"
        :key="`${item.key_path}-${item.language}-${index}`"
        class="comparison-item"
        :class="{
          expanded: expandedItems.has(`${item.key_path}-${item.language}`),
          resolved: getResolutionStatus(`${item.key_path}-${item.language}`) === 'resolved'
        }"
      >
        <!-- Item Header -->
        <div class="item-header" @click="toggleExpand(`${item.key_path}-${item.language}`)">
          <div class="item-info">
            <div class="key-path">{{ item.key_path }}</div>
            <div class="meta-info">
              <span class="namespace">{{ item.namespace_code }}</span>
              <span class="language-badge">{{ item.language.toUpperCase() }}</span>
              <span v-if="item.similarity < 1" class="similarity" :class="getSimilarityColor(item.similarity)">
                {{ Math.round(item.similarity * 100) }}% {{ $t('admin.i18n.similar') }}
              </span>
            </div>
          </div>

          <div class="item-action">
            <span class="action-icon">{{ item.action === 'SKIP' ? '⏭️' : item.action === 'ADD' ? '➕' : item.action === 'UPDATE' ? '✏️' : '🗑️' }}</span>
            <span v-if="getResolutionStatus(`${item.key_path}-${item.language}`) === 'resolved'" class="resolved-badge">
              ✓ {{ $t('admin.i18n.resolved') }}
            </span>
            <span v-else-if="item.resolution_status === 'PENDING'" class="pending-badge">
              ⏳ {{ $t('admin.i18n.pending') }}
            </span>
          </div>

          <button class="expand-toggle">
            {{ expandedItems.has(`${item.key_path}-${item.language}`) ? '▼' : '▶' }}
          </button>
        </div>

        <!-- Item Details (Expanded) -->
        <div v-if="expandedItems.has(`${item.key_path}-${item.language}`)" class="item-details">
          <!-- Values Comparison -->
          <div class="values-comparison">
            <div class="value-column">
              <div class="column-header">
                📱 {{ $t('admin.i18n.frontend_value') }}
              </div>
              <div v-if="item.frontend_value" class="value-content">
                {{ item.frontend_value }}
              </div>
              <div v-else class="value-empty">
                {{ $t('admin.i18n.no_value') }}
              </div>
            </div>

            <div class="value-column">
              <div class="column-header">
                💾 {{ $t('admin.i18n.database_value') }}
              </div>
              <div v-if="item.database_value" class="value-content">
                {{ item.database_value }}
              </div>
              <div v-else class="value-empty">
                {{ $t('admin.i18n.no_value') }}
              </div>
            </div>
          </div>

          <!-- Conflict Info -->
          <div v-if="item.conflict_reason" class="conflict-info">
            <span class="conflict-icon">⚠️</span>
            <div class="conflict-details">
              <div class="conflict-title">{{ $t('admin.i18n.conflict') }}</div>
              <div class="conflict-reason">{{ item.conflict_reason }}</div>
            </div>
          </div>

          <!-- Resolution Actions (MANUAL mode only) -->
          <div v-if="selectedMode === 'MANUAL'" class="resolution-actions">
            <div class="actions-label">{{ $t('admin.i18n.select_action') }}:</div>
            <div class="action-buttons">
              <button
                class="action-button"
                @click="handleSetResolution(`${item.key_path}-${item.language}`, 'ADD')"
              >
                ➕ {{ $t('admin.i18n.action_add') }}
              </button>
              <button
                class="action-button"
                @click="handleSetResolution(`${item.key_path}-${item.language}`, 'UPDATE')"
              >
                ✏️ {{ $t('admin.i18n.action_update') }}
              </button>
              <button
                class="action-button"
                @click="handleSetResolution(`${item.key_path}-${item.language}`, 'DELETE')"
              >
                🗑️ {{ $t('admin.i18n.action_delete') }}
              </button>
              <button
                class="action-button"
                @click="handleSetResolution(`${item.key_path}-${item.language}`, 'SKIP')"
              >
                ⏭️ {{ $t('admin.i18n.action_skip') }}
              </button>
              <button
                v-if="getResolutionStatus(`${item.key_path}-${item.language}`) === 'resolved'"
                class="action-button clear"
                @click="handleClearResolution(`${item.key_path}-${item.language}`)"
              >
                ✗ {{ $t('admin.i18n.clear') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <span class="empty-icon">🔍</span>
      {{ $t('admin.i18n.no_items_found') }}
    </div>

    <!-- Pagination -->
    <div v-if="comparisonTotalPages > 1" class="pagination">
      <button
        :disabled="comparisonPage === 0"
        @click="handlePageChange(comparisonPage - 1)"
      >
        {{ $t('common.previous') }}
      </button>

      <span class="pagination-info">
        {{ comparisonPage + 1 }} / {{ comparisonTotalPages }}
      </span>

      <button
        :disabled="comparisonPage >= comparisonTotalPages - 1"
        @click="handlePageChange(comparisonPage + 1)"
      >
        {{ $t('common.next') }}
      </button>
    </div>

    <!-- Apply Confirmation Modal -->
    <div v-if="showApplyConfirm" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          ⚠️ {{ $t('admin.i18n.apply_confirmation') }}
        </div>
        <div class="modal-body">
          {{ $t('admin.i18n.apply_confirmation_desc') }}
          <ul class="confirmation-list">
            <li v-if="selectedMode === 'MANUAL'">
              {{ $t('admin.i18n.mode_manual') }}: {{ pendingResolutionsCount }}
              {{ $t('admin.i18n.pending_resolutions') }}
            </li>
            <li v-if="conflictsCount > 0">
              ⚠️ {{ conflictsCount }} {{ $t('admin.i18n.conflicts') }}
            </li>
          </ul>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showApplyConfirm = false">
            {{ $t('common.cancel') }}
          </button>
          <button class="btn btn-primary" @click="handleApplySync">
            {{ $t('admin.i18n.apply_changes') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comparison-panel {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  gap: 16px;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
}

.status-info {
  color: #374151;
}

.status-info strong {
  color: #1f2937;
  font-weight: 700;
}

.status-info.warning {
  color: #92400e;
}

.status-info.warning strong {
  color: #b45309;
}

.status-separator {
  color: #d1d5db;
}

.alert {
  margin: 0;
  padding: 12px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  background: #fee2e2;
  color: #7f1d1d;
}

.alert-icon {
  flex-shrink: 0;
}

.alert-message {
  flex: 1;
}

.category-filter {
  display: flex;
  gap: 8px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  flex-wrap: wrap;
}

.category-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
  white-space: nowrap;
}

.category-button:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.category-button.active {
  border-color: #3b82f6;
  background: #dbeafe;
  color: #1e40af;
  font-weight: 600;
}

.category-icon {
  font-size: 14px;
}

.category-label {
  flex: 1;
}

.category-count {
  font-weight: 600;
  color: #6b7280;
  font-size: 12px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 60px 24px;
  color: #6b7280;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.items-list {
  flex: 1;
  overflow-y: auto;
}

.comparison-item {
  border-bottom: 1px solid #e5e7eb;
  background: white;
  transition: background 0.2s;
}

.comparison-item:hover {
  background: #f9fafb;
}

.comparison-item.resolved {
  background: #f0fdf4;
}

.item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  cursor: pointer;
  user-select: none;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.key-path {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
  word-break: break-all;
}

.meta-info {
  display: flex;
  gap: 8px;
  font-size: 12px;
  flex-wrap: wrap;
}

.namespace {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 3px;
  color: #6b7280;
}

.language-badge {
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.similarity {
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.similarity.high {
  background: #d1fae5;
  color: #065f46;
}

.similarity.medium {
  background: #fef3c7;
  color: #92400e;
}

.similarity.low {
  background: #fee2e2;
  color: #7f1d1d;
}

.item-action {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.action-icon {
  font-size: 16px;
}

.resolved-badge {
  background: #d1fae5;
  color: #065f46;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.pending-badge {
  background: #fef3c7;
  color: #92400e;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 600;
}

.expand-toggle {
  background: none;
  border: none;
  cursor: pointer;
  color: #6b7280;
  font-size: 12px;
  font-weight: bold;
  transition: transform 0.2s;
}

.item-details {
  padding: 0 24px 16px;
  background: white;
  animation: slideDown 0.3s;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 1000px;
  }
}

.values-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.value-column {
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.column-header {
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 12px;
}

.value-content {
  font-family: monospace;
  font-size: 13px;
  color: #1f2937;
  word-break: break-all;
  white-space: pre-wrap;
  line-height: 1.5;
  padding: 8px;
  background: white;
  border-radius: 4px;
}

.value-empty {
  font-size: 13px;
  color: #9ca3af;
  font-style: italic;
}

.conflict-info {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fef3c7;
  border-left: 3px solid #f59e0b;
  border-radius: 6px;
  margin-bottom: 16px;
}

.conflict-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.conflict-details {
  flex: 1;
}

.conflict-title {
  font-weight: 600;
  color: #92400e;
  font-size: 13px;
  margin-bottom: 4px;
}

.conflict-reason {
  font-size: 12px;
  color: #7c2d12;
}

.resolution-actions {
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
}

.actions-label {
  font-weight: 600;
  color: #374151;
  font-size: 13px;
  margin-bottom: 8px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-button {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.action-button:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
  color: #1e40af;
}

.action-button.clear {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #7f1d1d;
}

.action-button.clear:hover {
  background: #fecaca;
  border-color: #f87171;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 60px 24px;
  color: #9ca3af;
  font-size: 16px;
}

.empty-icon {
  font-size: 32px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.pagination button {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;
}

.pagination button:hover:not(:disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
  min-width: 60px;
  text-align: center;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner-small {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.6s linear infinite;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 400px;
  padding: 0;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 20px 24px;
  font-weight: 700;
  color: #1f2937;
  border-bottom: 1px solid #e5e7eb;
  font-size: 16px;
}

.modal-body {
  padding: 20px 24px;
  color: #374151;
  font-size: 14px;
  line-height: 1.6;
}

.confirmation-list {
  margin: 12px 0 0;
  padding-left: 20px;
}

.confirmation-list li {
  margin: 6px 0;
  color: #6b7280;
}

.modal-actions {
  display: flex;
  gap: 8px;
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
}

.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #d1d5db;
  flex: 1;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-primary {
  flex: 1;
}
</style>
