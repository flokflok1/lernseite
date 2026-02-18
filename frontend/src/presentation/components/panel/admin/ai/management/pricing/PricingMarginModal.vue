<!--
  PricingMarginModal.vue

  Modal for applying margin percentage to selected AI models.
  Calculates new prices based on cost and chosen margin.
-->

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content margin-modal">
      <div class="modal-header">
        <h3>{{ $t('aiPricing.applyMarginTitle') }}</h3>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>
      <div class="modal-body">
        <p class="modal-description">
          {{ $t('aiPricing.marginDescription', { count: selectedCount }) }}
        </p>

        <div class="form-group">
          <label>{{ $t('aiPricing.marginPercent') }}</label>
          <div class="margin-input-row">
            <input
              v-model.number="marginPercent"
              type="number"
              step="0.1"
              min="0"
              max="1000"
              class="form-input"
            />
            <span class="unit">%</span>
          </div>
          <p class="form-hint">
            {{ $t('aiPricing.marginFormula') }}: price = cost x (1 + {{ marginPercent }}%)
          </p>
        </div>

        <div class="form-group">
          <label>{{ $t('aiPricing.applyTo') }}</label>
          <div class="radio-group">
            <label class="radio-option">
              <input type="radio" v-model="marginApplyTo" value="both" />
              {{ $t('aiPricing.both') }}
            </label>
            <label class="radio-option">
              <input type="radio" v-model="marginApplyTo" value="input" />
              {{ $t('aiPricing.inputOnly') }}
            </label>
            <label class="radio-option">
              <input type="radio" v-model="marginApplyTo" value="output" />
              {{ $t('aiPricing.outputOnly') }}
            </label>
          </div>
        </div>

        <div class="preview-box">
          <h4>{{ $t('aiPricing.preview') }}</h4>
          <p>
            {{ $t('aiPricing.example') }}: $0.01 x 1.{{ marginPercent.toString().padStart(2, '0') }}
            = ${{ (0.01 * (1 + marginPercent / 100)).toFixed(4) }}
          </p>
        </div>
      </div>
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">
          {{ $t('common.cancel') }}
        </button>
        <button @click="handleApply" :disabled="applying" class="btn-primary">
          {{ applying ? $t('aiPricing.applying') : $t('aiPricing.apply') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  selectedCount: number
  applying?: boolean
}

withDefaults(defineProps<Props>(), {
  applying: false
})

const emit = defineEmits<{
  close: []
  apply: [data: { marginPercent: number; applyTo: 'input' | 'output' | 'both' }]
}>()

const marginPercent = ref(20)
const marginApplyTo = ref<'input' | 'output' | 'both'>('both')

function handleApply(): void {
  emit('apply', {
    marginPercent: marginPercent.value,
    applyTo: marginApplyTo.value
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-surface);
  border-radius: 0.5rem;
  max-width: 450px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.modal-body {
  padding: 1.5rem;
}

.modal-description {
  margin: 0 0 1.5rem 0;
  color: var(--color-text-secondary);
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.margin-input-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  width: 120px;
}

.unit {
  color: var(--color-text-secondary);
}

.form-hint {
  margin: 0.5rem 0 0 0;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

.radio-group {
  display: flex;
  gap: 1rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  cursor: pointer;
}

.preview-box {
  background: var(--color-surface-secondary);
  padding: 1rem;
  border-radius: 0.375rem;
  margin-top: 1rem;
}

.preview-box h4 {
  margin: 0 0 0.5rem 0;
  font-size: 0.8125rem;
}

.preview-box p {
  margin: 0;
  font-family: monospace;
  font-size: 0.875rem;
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
}

.btn-primary {
  background: var(--color-primary);
  border: none;
  color: white;
}

.btn-primary:disabled {
  opacity: 0.5;
}
</style>
