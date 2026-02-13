<!--
  PricingEditModal.vue

  Modal for editing pricing of a single AI model
  Shows both cost (Einkaufspreis) and price (Verkaufspreis)
-->

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <!-- Header -->
      <div class="modal-header">
        <div class="header-info">
          <h3>{{ model.display_name || model.model_name }}</h3>
          <span class="provider-badge">{{ model.provider_name }}</span>
          <span class="category-badge">{{ model.category }}</span>
        </div>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <div class="price-grid">
          <!-- Cost Section (Einkaufspreis) -->
          <div class="price-section cost-section">
            <h4>{{ $t('aiPricing.costSection') }}</h4>
            <p class="section-hint">{{ $t('aiPricing.costHint') }}</p>

            <div class="form-group">
              <label>{{ $t('aiPricing.inputCost') }}</label>
              <div class="input-with-unit">
                <input
                  v-model.number="form.cost_per_1k_input"
                  type="number"
                  step="0.000001"
                  min="0"
                  class="form-input"
                  placeholder="0.000000"
                />
                <span class="unit">USD/1K</span>
              </div>
            </div>

            <div class="form-group">
              <label>{{ $t('aiPricing.outputCost') }}</label>
              <div class="input-with-unit">
                <input
                  v-model.number="form.cost_per_1k_output"
                  type="number"
                  step="0.000001"
                  min="0"
                  class="form-input"
                  placeholder="0.000000"
                />
                <span class="unit">USD/1K</span>
              </div>
            </div>
          </div>

          <!-- Price Section (Verkaufspreis) -->
          <div class="price-section price-section">
            <h4>{{ $t('aiPricing.priceSection') }}</h4>
            <p class="section-hint">{{ $t('aiPricing.priceHint') }}</p>

            <div class="form-group">
              <label>{{ $t('aiPricing.inputPrice') }}</label>
              <div class="input-with-unit">
                <input
                  v-model.number="form.input_price_per_1k"
                  type="number"
                  step="0.000001"
                  min="0"
                  class="form-input"
                  placeholder="0.000000"
                />
                <span class="unit">USD/1K</span>
              </div>
            </div>

            <div class="form-group">
              <label>{{ $t('aiPricing.outputPrice') }}</label>
              <div class="input-with-unit">
                <input
                  v-model.number="form.output_price_per_1k"
                  type="number"
                  step="0.000001"
                  min="0"
                  class="form-input"
                  placeholder="0.000000"
                />
                <span class="unit">USD/1K</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Margin Display -->
        <div class="margin-section">
          <h4>{{ $t('aiPricing.calculatedMargins') }}</h4>
          <div class="margin-grid">
            <div class="margin-item">
              <span class="margin-label">Input</span>
              <MarginCalculator
                :cost="form.cost_per_1k_input"
                :price="form.input_price_per_1k"
              />
            </div>
            <div class="margin-item">
              <span class="margin-label">Output</span>
              <MarginCalculator
                :cost="form.cost_per_1k_output"
                :price="form.output_price_per_1k"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">
          {{ $t('common.cancel') }}
        </button>
        <button @click="handleSave" :disabled="saving" class="btn-primary">
          {{ saving ? $t('common.saving') : $t('common.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AIModelPricing, AIModelPricingUpdateRequest } from '@/application/services/api/admin'
import MarginCalculator from './MarginCalculator.vue'

const { t } = useI18n()

interface Props {
  model: AIModelPricing
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: AIModelPricingUpdateRequest): void
}>()

const saving = ref(false)

const form = reactive<AIModelPricingUpdateRequest>({
  cost_per_1k_input: null,
  cost_per_1k_output: null,
  input_price_per_1k: null,
  output_price_per_1k: null
})

onMounted(() => {
  // Initialize form with model values
  form.cost_per_1k_input = props.model.cost_per_1k_input
  form.cost_per_1k_output = props.model.cost_per_1k_output
  form.input_price_per_1k = props.model.input_price_per_1k
  form.output_price_per_1k = props.model.output_price_per_1k
})

function handleSave() {
  saving.value = true
  emit('save', { ...form })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-surface);
  border-radius: 0.5rem;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.header-info {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.header-info h3 {
  margin: 0;
  font-size: 1.125rem;
}

.provider-badge,
.category-badge {
  font-size: 0.75rem;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  background: var(--color-surface-secondary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-secondary);
  line-height: 1;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.price-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.price-section h4 {
  margin: 0 0 0.25rem 0;
  font-size: 0.875rem;
  color: var(--color-text-primary);
}

.section-hint {
  margin: 0 0 1rem 0;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.cost-section {
  background: rgba(239, 68, 68, 0.05);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(239, 68, 68, 0.1);
}

.price-section.price-section {
  background: rgba(16, 185, 129, 0.05);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(16, 185, 129, 0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  color: var(--color-text-secondary);
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background: var(--color-surface);
  font-size: 0.875rem;
  font-family: monospace;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

.unit {
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
  white-space: nowrap;
}

.margin-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.margin-section h4 {
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
}

.margin-grid {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.margin-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.margin-item .margin-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--color-border);
}

.btn-secondary,
.btn-primary {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary {
  background: var(--color-surface-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.btn-primary {
  background: var(--color-primary);
  border: none;
  color: white;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
