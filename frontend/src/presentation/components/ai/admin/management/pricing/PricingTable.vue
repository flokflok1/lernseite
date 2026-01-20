<!--
  PricingTable.vue

  Table component for displaying AI model pricing
  Supports selection, sorting, and row actions
-->

<template>
  <div class="pricing-table-wrapper">
    <table class="pricing-table">
      <thead>
        <tr>
          <th class="col-checkbox">
            <input
              type="checkbox"
              :checked="allSelected"
              :indeterminate="someSelected"
              @change="$emit('toggle-all')"
            />
          </th>
          <th class="col-provider">{{ $t('windows.aiPricing.provider') }}</th>
          <th class="col-model">{{ $t('windows.aiPricing.model') }}</th>
          <th class="col-category">{{ $t('windows.aiPricing.category') }}</th>
          <th class="col-cost">{{ $t('windows.aiPricing.inputCost') }}</th>
          <th class="col-cost">{{ $t('windows.aiPricing.outputCost') }}</th>
          <th class="col-price">{{ $t('windows.aiPricing.inputPrice') }}</th>
          <th class="col-price">{{ $t('windows.aiPricing.outputPrice') }}</th>
          <th class="col-margin">{{ $t('windows.aiPricing.margin') }}</th>
          <th class="col-actions">{{ $t('common.actions') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="model in models"
          :key="model.model_id"
          :class="{ 'row-selected': selectedIds.includes(model.model_id), 'row-inactive': !model.active }"
        >
          <td class="col-checkbox">
            <input
              type="checkbox"
              :checked="selectedIds.includes(model.model_id)"
              @change="$emit('toggle-select', model.model_id)"
            />
          </td>
          <td class="col-provider">
            <span class="provider-name">{{ model.provider_name }}</span>
          </td>
          <td class="col-model">
            <div class="model-info">
              <span class="model-name">{{ model.display_name || model.model_name }}</span>
              <span v-if="model.is_default" class="default-badge">Default</span>
            </div>
          </td>
          <td class="col-category">
            <span class="category-badge">{{ model.category }}</span>
          </td>
          <td class="col-cost">
            <span class="price-value cost">{{ formatPrice(model.cost_per_1k_input) }}</span>
          </td>
          <td class="col-cost">
            <span class="price-value cost">{{ formatPrice(model.cost_per_1k_output) }}</span>
          </td>
          <td class="col-price">
            <span class="price-value price">{{ formatPrice(model.input_price_per_1k) }}</span>
          </td>
          <td class="col-price">
            <span class="price-value price">{{ formatPrice(model.output_price_per_1k) }}</span>
          </td>
          <td class="col-margin">
            <div class="margin-display">
              <MarginCalculator
                :margin-percent="model.margin_input"
                :show-indicator="false"
              />
              <span class="margin-separator">/</span>
              <MarginCalculator
                :margin-percent="model.margin_output"
                :show-indicator="false"
              />
            </div>
          </td>
          <td class="col-actions">
            <button
              @click="$emit('edit', model)"
              class="action-btn edit-btn"
              :title="$t('common.edit')"
            >
              ✏️
            </button>
          </td>
        </tr>
        <tr v-if="models.length === 0">
          <td colspan="10" class="empty-state">
            {{ $t('windows.aiPricing.noModels') }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AIModelPricing } from '@/infrastructure/api/admin/types'
import MarginCalculator from './MarginCalculator.vue'

const { t } = useI18n()

interface Props {
  models: AIModelPricing[]
  selectedIds: number[]
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'toggle-select', modelId: number): void
  (e: 'toggle-all'): void
  (e: 'edit', model: AIModelPricing): void
}>()

const allSelected = computed(() => {
  return props.models.length > 0 && props.selectedIds.length === props.models.length
})

const someSelected = computed(() => {
  return props.selectedIds.length > 0 && props.selectedIds.length < props.models.length
})

function formatPrice(value: number | null): string {
  if (value === null || value === undefined) return '-'
  if (value === 0) return '0.0000'
  if (value < 0.0001) return `${(value * 1000).toFixed(3)}m`
  return value.toFixed(4)
}
</script>

<style scoped>
.pricing-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
}

.pricing-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.pricing-table th,
.pricing-table td {
  padding: 0.625rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.pricing-table th {
  background: var(--color-surface-secondary);
  font-weight: 600;
  color: var(--color-text-secondary);
  white-space: nowrap;
}

.pricing-table tbody tr:hover {
  background: var(--color-surface-hover);
}

.row-selected {
  background: rgba(var(--color-primary-rgb), 0.05) !important;
}

.row-inactive {
  opacity: 0.5;
}

.col-checkbox {
  width: 40px;
  text-align: center;
}

.col-provider {
  width: 100px;
}

.col-model {
  min-width: 180px;
}

.col-category {
  width: 90px;
}

.col-cost,
.col-price {
  width: 100px;
  text-align: right;
  font-family: monospace;
}

.col-margin {
  width: 120px;
  text-align: center;
}

.col-actions {
  width: 60px;
  text-align: center;
}

.provider-name {
  font-weight: 500;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.model-name {
  font-weight: 500;
}

.default-badge {
  font-size: 0.625rem;
  padding: 0.0625rem 0.375rem;
  background: var(--color-primary);
  color: white;
  border-radius: 9999px;
}

.category-badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  background: var(--color-surface-secondary);
  border-radius: 0.25rem;
}

.price-value {
  display: inline-block;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.price-value.cost {
  background: rgba(239, 68, 68, 0.1);
  color: rgb(180, 50, 50);
}

.price-value.price {
  background: rgba(16, 185, 129, 0.1);
  color: rgb(16, 140, 90);
}

.margin-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
}

.margin-separator {
  color: var(--color-text-tertiary);
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 0.875rem;
  border-radius: 0.25rem;
}

.action-btn:hover {
  background: var(--color-surface-secondary);
}

.empty-state {
  text-align: center;
  padding: 2rem !important;
  color: var(--color-text-tertiary);
}
</style>
