<script setup lang="ts">
/**
 * ComparisonPanel Component
 *
 * Orchestrates side-by-side comparison of frontend JSON vs database translations.
 * Allows admin to review and resolve changes in MANUAL mode.
 * Shows similarity scores and automatically suggests actions.
 *
 * Delegates rendering to sub-components:
 * - ComparisonStatusBar: Status display and apply button
 * - CategoryFilter: Filter buttons for categories
 * - ComparisonItemRow: Individual item display with expand/collapse
 * - ApplyConfirmationModal: Confirmation dialog
 * - ComparisonPagination: Pagination controls
 */

import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSyncManager } from '@/features/admin/useSyncManager'
import ComparisonStatusBar from './ComparisonStatusBar.vue'
import CategoryFilter from './CategoryFilter.vue'
import ComparisonItemRow from './ComparisonItemRow.vue'
import ApplyConfirmationModal from './ApplyConfirmationModal.vue'
import ComparisonPagination from './ComparisonPagination.vue'
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

// ============================================================================
// METHODS
// ============================================================================

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

async function handleApplyConfirm() {
  try {
    showApplyConfirm.value = false
    await applySync()
  } catch (err) {
    console.error('Failed to apply sync:', err)
  }
}

function handleApplyCancel() {
  showApplyConfirm.value = false
}

function handleApplyRequested() {
  showApplyConfirm.value = true
}

function getResolutionStatus(detailId: string): string {
  const resolution = resolutions[detailId]
  if (!resolution) return 'pending'
  return 'resolved'
}
</script>

<template>
  <div class="comparison-panel">
    <!-- Status Bar with Apply Button -->
    <ComparisonStatusBar
      :pending-resolutions-count="pendingResolutionsCount"
      :conflicts-count="conflictsCount"
      :can-apply="canApply"
      :is-applying="isApplying"
      :apply-error="applyError"
      @apply-requested="handleApplyRequested"
    />

    <!-- Main Content -->
    <div v-if="!isLoadingComparison && comparisonPanel" class="comparison-content">
      <!-- Category Filter -->
      <CategoryFilter
        :categories="categories"
        :selected-category="selectedCategory"
        @category-selected="handleCategorySelect"
      />

      <!-- Comparison Items List -->
      <div v-if="paginatedComparisonItems.length > 0" class="items-list">
        <ComparisonItemRow
          v-for="(item, index) in paginatedComparisonItems"
          :key="`${item.key_path}-${item.language}-${index}`"
          :item="item"
          :index="index"
          :is-expanded="expandedItems.has(`${item.key_path}-${item.language}`)"
          :selected-mode="selectedMode"
          :resolution-status="getResolutionStatus"
          @toggle-expanded="toggleExpand(`${item.key_path}-${item.language}`)"
          @set-resolution="handleSetResolution(`${item.key_path}-${item.language}`, $event)"
          @clear-resolution="handleClearResolution(`${item.key_path}-${item.language}`)"
        />
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <p>{{ $t('admin.i18n.no_items') }}</p>
      </div>

      <!-- Pagination -->
      <ComparisonPagination
        :current-page="comparisonPage"
        :total-pages="comparisonTotalPages"
        @page-change="handlePageChange"
      />
    </div>

    <!-- Loading State -->
    <div v-else-if="isLoadingComparison" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('common.loading') }}</p>
    </div>

    <!-- Confirmation Modal -->
    <ApplyConfirmationModal
      :is-visible="showApplyConfirm"
      :selected-mode="selectedMode"
      :pending-resolutions-count="pendingResolutionsCount"
      :conflicts-count="conflictsCount"
      :is-applying="isApplying"
      @confirm="handleApplyConfirm"
      @cancel="handleApplyCancel"
    />
  </div>
</template>

<style scoped>
.comparison-panel {
  display: flex;
  flex-direction: column;
  gap: 0;
  height: 100%;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.comparison-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow-y: auto;
}

.items-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  gap: 12px;
  display: flex;
  flex-direction: column;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary, #666);
  font-size: 14px;
  padding: 40px 24px;
  text-align: center;
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: var(--color-text-secondary, #666);
  font-size: 14px;
}

.spinner {
  display: inline-block;
  width: 32px;
  height: 32px;
  border: 3px solid rgba(33, 150, 243, 0.1);
  border-top-color: var(--color-primary, #2196f3);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .items-list {
    padding: 12px 16px;
  }

  .empty-state {
    padding: 24px 16px;
  }
}
</style>
