<!--
  ModelCardItem - Individual AI model card in the selector list
  Extracted from ModelSelectorWindow for quality gate G01 compliance.
-->

<template>
  <div
    @click="$emit('select', model)"
    :class="[
      'model-card p-4 rounded-lg border transition-all cursor-pointer',
      isSelected
        ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5'
        : 'border-[var(--color-border)] hover:border-[var(--color-primary)]/50 hover:bg-[var(--color-surface)]'
    ]"
  >
    <!-- Model Header -->
    <div class="flex items-start justify-between mb-2">
      <div class="flex items-center gap-2">
        <span class="text-xl">{{ fmt.getCategoryIcon(model.category) }}</span>
        <div>
          <h4 class="font-medium text-[var(--color-text-primary)]">{{ model.display_name }}</h4>
          <p class="text-xs text-[var(--color-text-muted)] font-mono">{{ model.model_name }}</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <span
          v-if="model.provider"
          :class="['px-2 py-0.5 rounded text-xs font-medium', fmt.getProviderBadgeClass(model.provider)]"
        >
          {{ model.provider }}
        </span>
        <span
          v-if="model.is_default"
          class="px-2 py-0.5 rounded text-xs bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]"
        >
          Default
        </span>
      </div>
    </div>

    <!-- Description -->
    <p v-if="model.description" class="text-sm text-[var(--color-text-secondary)] mb-3 line-clamp-2">
      {{ model.description }}
    </p>

    <!-- Badges -->
    <div class="flex flex-wrap gap-2 mb-2">
      <span :class="['px-2 py-0.5 rounded text-xs font-medium', fmt.getCostBadgeClass(model.cost_level)]">
        {{ fmt.getCostLabel(model.cost_level) }}
      </span>
      <span :class="['px-2 py-0.5 rounded text-xs font-medium', fmt.getSpeedBadgeClass(model.speed)]">
        {{ fmt.getSpeedLabel(model.speed) }}
      </span>
      <span
        v-if="model.context_window"
        class="px-2 py-0.5 rounded text-xs bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)]"
      >
        {{ fmt.formatContextWindow(model.context_window) }} ctx
      </span>
      <span
        v-if="model.supports_vision"
        class="px-2 py-0.5 rounded text-xs bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#1e40af)]"
      >
        Vision
      </span>
      <span
        v-if="model.supports_functions"
        class="px-2 py-0.5 rounded text-xs bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#1e40af)]"
      >
        Functions
      </span>
    </div>

    <!-- Price Display & Edit -->
    <div class="flex items-center justify-between pt-2 border-t border-[var(--color-border)]">
      <div class="flex gap-4 text-xs">
        <div>
          <span class="text-[var(--color-text-muted)]">Input:</span>
          <span class="ml-1 font-mono text-[var(--color-text-secondary)]">
            {{ fmt.formatPrice(model.input_price_per_1k) }}/1K
          </span>
        </div>
        <div>
          <span class="text-[var(--color-text-muted)]">Output:</span>
          <span class="ml-1 font-mono text-[var(--color-text-secondary)]">
            {{ fmt.formatPrice(model.output_price_per_1k) }}/1K
          </span>
        </div>
      </div>
      <button
        @click.stop="$emit('edit-price', model)"
        class="px-2 py-1 text-xs bg-[var(--color-surface)] text-[var(--color-text-secondary)] rounded border border-[var(--color-border)] hover:bg-[var(--color-background)] hover:text-[var(--color-text-primary)] transition-colors"
        title="Preise bearbeiten"
      >
        Preise
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AIModelRegistryItem } from '@/infrastructure/api/clients/panel/admin'
import { useModelFormatters } from './composables/useModelFormatters'

defineProps<{
  model: AIModelRegistryItem
  isSelected: boolean
}>()

defineEmits<{
  (e: 'select', model: AIModelRegistryItem): void
  (e: 'edit-price', model: AIModelRegistryItem): void
}>()

const fmt = useModelFormatters()
</script>

<style scoped>
.model-card:hover {
  transform: translateY(-1px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
