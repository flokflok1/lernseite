<!--
  AIPricingMain.vue

  Main component for AI model pricing management.
  Features:
  - Table of all AI models with pricing columns
  - Edit both Einkaufspreis (cost) AND Verkaufspreis (price)
  - Margin calculator (auto-calculate percentage)
  - Bulk update functionality
  - Filter by provider, category
-->

<template>
  <div class="ai-pricing-window">
    <!-- Header -->
    <div class="window-header">
      <div class="header-left">
        <h2>{{ $t('aiPricing.title') }}</h2>
        <div class="header-stats">
          <span class="stat-item">
            {{ models.length }} {{ $t('aiPricing.models') }}
          </span>
          <span v-if="selectedIds.length > 0" class="stat-divider">|</span>
          <span v-if="selectedIds.length > 0" class="stat-item stat-selected">
            {{ selectedIds.length }} {{ $t('aiPricing.selected') }}
          </span>
        </div>
      </div>
      <div class="header-actions">
        <button
          v-if="selectedIds.length > 0"
          @click="showMarginModal = true"
          class="action-btn primary"
        >
          {{ $t('aiPricing.applyMargin') }} ({{ selectedIds.length }})
        </button>
        <button @click="loadPricing" class="action-btn" :disabled="loading">
          {{ $t('common.refresh') }}
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <select v-model="providerFilter" class="filter-select" @change="applyFilters">
          <option value="">{{ $t('aiPricing.allProviders') }}</option>
          <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
        </select>
        <select v-model="categoryFilter" class="filter-select" @change="applyFilters">
          <option value="">{{ $t('aiPricing.allCategories') }}</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
        <label class="filter-checkbox">
          <input type="checkbox" v-model="includeInactive" @change="loadPricing" />
          {{ $t('aiPricing.includeInactive') }}
        </label>
      </div>
      <div class="filter-group">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('aiPricing.search')"
          class="filter-input"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>{{ $t('aiPricing.loading') }}</p>
    </div>

    <!-- Table -->
    <div v-else class="table-container">
      <PricingTable
        :models="filteredModels"
        :selected-ids="selectedIds"
        @toggle-select="toggleModelSelect"
        @toggle-all="toggleAllModels"
        @edit="openEditModal"
      />
    </div>

    <!-- Edit Modal -->
    <PricingEditModal
      v-if="editingModel"
      :model="editingModel"
      @close="editingModel = null"
      @save="handleSavePricing"
    />

    <!-- Margin Modal -->
    <PricingMarginModal
      v-if="showMarginModal"
      :selected-count="selectedIds.length"
      :applying="applyingMargin"
      @close="showMarginModal = false"
      @apply="handleApplyMargin"
    />

    <!-- Toast -->
    <div v-if="toast" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AIModelPricing, AIModelPricingUpdateRequest } from '@/application/services/api/panel-admin'
import {
  adminGetAIPricing,
  adminUpdateAIPricing,
  adminApplyPricingMargin
} from '@/application/services/api/panel-admin'
import PricingTable from './PricingTable.vue'
import PricingEditModal from './PricingEditModal.vue'
import PricingMarginModal from './PricingMarginModal.vue'

const { t } = useI18n()

// State
const loading = ref(false)
const models = ref<AIModelPricing[]>([])
const providers = ref<string[]>([])
const categories = ref<string[]>([])
const selectedIds = ref<number[]>([])
const editingModel = ref<AIModelPricing | null>(null)

// Filters
const providerFilter = ref('')
const categoryFilter = ref('')
const includeInactive = ref(false)
const searchQuery = ref('')

// Margin Modal
const showMarginModal = ref(false)
const applyingMargin = ref(false)

// Toast
const toast = ref<{ message: string; type: 'success' | 'error' } | null>(null)

// Computed
const filteredModels = computed(() => {
  let result = models.value

  if (providerFilter.value) {
    result = result.filter(m => m.provider_name === providerFilter.value)
  }

  if (categoryFilter.value) {
    result = result.filter(m => m.category === categoryFilter.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(m =>
      m.model_name.toLowerCase().includes(query) ||
      m.display_name?.toLowerCase().includes(query) ||
      m.provider_name?.toLowerCase().includes(query)
    )
  }

  return result
})

// Methods
async function loadPricing(): Promise<void> {
  loading.value = true
  try {
    const response = await adminGetAIPricing({
      include_inactive: includeInactive.value
    })
    models.value = response.data.models
    providers.value = response.data.providers
    categories.value = response.data.categories
  } catch (error) {
    showToast(t('aiPricing.errorLoad'), 'error')
    console.error('Failed to load pricing:', error)
  } finally {
    loading.value = false
  }
}

function applyFilters(): void {
  // Filters are applied via computed, no need to reload
}

function toggleModelSelect(modelId: number): void {
  const idx = selectedIds.value.indexOf(modelId)
  if (idx === -1) {
    selectedIds.value.push(modelId)
  } else {
    selectedIds.value.splice(idx, 1)
  }
}

function toggleAllModels(): void {
  if (selectedIds.value.length === filteredModels.value.length) {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredModels.value.map(m => m.model_id)
  }
}

function openEditModal(model: AIModelPricing): void {
  editingModel.value = model
}

async function handleSavePricing(data: AIModelPricingUpdateRequest): Promise<void> {
  if (!editingModel.value) return

  try {
    await adminUpdateAIPricing(editingModel.value.model_id, data)

    const idx = models.value.findIndex(m => m.model_id === editingModel.value!.model_id)
    if (idx !== -1) {
      models.value[idx] = {
        ...models.value[idx],
        ...data,
        margin_input: data.cost_per_1k_input && data.input_price_per_1k
          ? ((data.input_price_per_1k - data.cost_per_1k_input) / data.cost_per_1k_input) * 100
          : null,
        margin_output: data.cost_per_1k_output && data.output_price_per_1k
          ? ((data.output_price_per_1k - data.cost_per_1k_output) / data.cost_per_1k_output) * 100
          : null
      }
    }

    showToast(t('aiPricing.successUpdate'), 'success')
    editingModel.value = null
  } catch (error) {
    showToast(t('aiPricing.errorUpdate'), 'error')
    console.error('Failed to update pricing:', error)
  }
}

async function handleApplyMargin(data: { marginPercent: number; applyTo: 'input' | 'output' | 'both' }): Promise<void> {
  applyingMargin.value = true
  try {
    const result = await adminApplyPricingMargin({
      model_ids: selectedIds.value,
      margin_percent: data.marginPercent,
      apply_to: data.applyTo
    })

    showToast(t('aiPricing.successMargin', { count: result.data.updated_count }), 'success')
    showMarginModal.value = false
    selectedIds.value = []

    await loadPricing()
  } catch (error) {
    showToast(t('aiPricing.errorMargin'), 'error')
    console.error('Failed to apply margin:', error)
  } finally {
    applyingMargin.value = false
  }
}

function showToast(message: string, type: 'success' | 'error'): void {
  toast.value = { message, type }
  setTimeout(() => {
    toast.value = null
  }, 3000)
}

// Lifecycle
onMounted(() => {
  loadPricing()
})
</script>

<style scoped>
.ai-pricing-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
}

.window-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.header-left h2 {
  margin: 0;
  font-size: 1.25rem;
}

.header-stats {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.stat-divider {
  color: var(--color-text-tertiary);
}

.stat-selected {
  color: var(--color-primary);
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.action-btn:hover:not(:disabled) {
  background: var(--color-surface-hover);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.filters-bar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.filter-group {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.filter-select,
.filter-input {
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: var(--color-surface);
  font-size: 0.8125rem;
}

.filter-input {
  width: 200px;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 1rem;
  color: var(--color-text-secondary);
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.table-container {
  flex: 1;
  overflow: auto;
  padding: 1rem 1.5rem;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  z-index: 1100;
  animation: slideIn 0.2s ease-out;
}

.toast.success {
  background: rgb(16, 185, 129);
  color: white;
}

.toast.error {
  background: rgb(239, 68, 68);
  color: white;
}

@keyframes slideIn {
  from {
    transform: translateY(1rem);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
