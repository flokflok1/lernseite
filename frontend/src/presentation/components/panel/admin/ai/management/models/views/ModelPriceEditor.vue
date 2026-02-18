<!--
  ModelPriceEditor - Modal for editing AI model token prices
  Extracted from ModelSelectorWindow for quality gate G01 compliance.
-->

<template>
  <div
    v-if="model"
    class="absolute inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-background)] rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-[var(--color-border)]">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">Preise bearbeiten</h3>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          {{ model.display_name }}
          <span class="font-mono text-xs text-[var(--color-text-muted)]">({{ model.model_name }})</span>
        </p>
      </div>

      <!-- Modal Body -->
      <div class="p-6 space-y-4">
        <div class="bg-[var(--color-surface)] rounded-lg p-4 text-sm text-[var(--color-text-secondary)]">
          <p>Preise werden pro 1.000 Tokens in USD angegeben.</p>
          <p class="mt-1 text-xs text-[var(--color-text-muted)]">Beispiel: 0.005 = $0.005 pro 1K Tokens</p>
        </div>

        <!-- Input Price -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Input-Preis (pro 1K Tokens)
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]">$</span>
            <input
              v-model.number="inputPrice"
              type="number"
              step="0.0001"
              min="0"
              placeholder="0.0050"
              class="w-full pl-7 pr-4 py-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/50"
            />
          </div>
        </div>

        <!-- Output Price -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Output-Preis (pro 1K Tokens)
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]">$</span>
            <input
              v-model.number="outputPrice"
              type="number"
              step="0.0001"
              min="0"
              placeholder="0.0150"
              class="w-full pl-7 pr-4 py-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/50"
            />
          </div>
        </div>

        <!-- Quick Info -->
        <div class="grid grid-cols-2 gap-4 pt-2 text-xs text-[var(--color-text-muted)]">
          <div>
            <span class="block">Provider:</span>
            <span class="text-[var(--color-text-secondary)]">{{ model.provider || '-' }}</span>
          </div>
          <div>
            <span class="block">Kategorie:</span>
            <span class="text-[var(--color-text-secondary)]">{{ fmt.getCategoryLabel(model.category) }}</span>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 bg-[var(--color-surface)] border-t border-[var(--color-border)] flex justify-end gap-3">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
        >
          Abbrechen
        </button>
        <button
          @click="handleSave"
          :disabled="saving"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors disabled:opacity-50"
        >
          {{ saving ? 'Speichern...' : 'Speichern' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { AIModelRegistryItem, AIModelUpdateRequest } from '@/application/services/api/panel-admin'
import * as adminApi from '@/application/services/api/panel-admin'
import { useModelFormatters } from './composables/useModelFormatters'

const props = defineProps<{
  model: AIModelRegistryItem | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved', modelId: string, inputPrice: number | null, outputPrice: number | null): void
}>()

const fmt = useModelFormatters()

const inputPrice = ref<number | null>(null)
const outputPrice = ref<number | null>(null)
const saving = ref(false)

watch(() => props.model, (newModel) => {
  if (newModel) {
    inputPrice.value = newModel.input_price_per_1k ?? null
    outputPrice.value = newModel.output_price_per_1k ?? null
  } else {
    inputPrice.value = null
    outputPrice.value = null
  }
}, { immediate: true })

async function handleSave(): Promise<void> {
  if (!props.model) return

  saving.value = true

  try {
    const updateData: AIModelUpdateRequest = {
      input_price_per_1k: inputPrice.value,
      output_price_per_1k: outputPrice.value
    }

    await adminApi.adminUpdateAIModel(props.model.model_id, updateData)

    emit('saved', props.model.model_id, inputPrice.value, outputPrice.value)
    emit('close')
  } catch (err) {
    console.error('Failed to update model prices:', err)
  } finally {
    saving.value = false
  }
}
</script>
