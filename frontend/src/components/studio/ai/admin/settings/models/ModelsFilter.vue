<!--
  ModelsFilter - Filter controls for model list
  Sub-component of ModelsTab
-->

<template>
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
      {{ $t('features.aiEditorModels.availableModels') }} ({{ modelCount }})
    </h3>
    <div class="flex gap-2">
      <select
        :value="providerFilter"
        @change="$emit('update:providerFilter', ($event.target as HTMLSelectElement).value)"
        class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"
      >
        <option value="">{{ $t('features.aiEditorModels.allProviders') }}</option>
        <option v-for="p in providers" :key="p.name" :value="p.name">
          {{ p.display_name }}
        </option>
      </select>
      <select
        :value="categoryFilter"
        @change="$emit('update:categoryFilter', ($event.target as HTMLSelectElement).value)"
        class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"
      >
        <option value="">{{ $t('features.aiEditorModels.allCategories') }}</option>
        <option v-for="c in categories" :key="c" :value="c">
          {{ c }}
        </option>
      </select>
      <input
        :value="search"
        @input="$emit('update:search', ($event.target as HTMLInputElement).value)"
        type="text"
        :placeholder="$t('features.aiEditorModels.search')"
        class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg w-48"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Provider {
  name: string
  display_name: string
}

defineProps<{
  modelCount: number
  providers: Provider[]
  categories: string[]
  providerFilter: string
  categoryFilter: string
  search: string
}>()

defineEmits<{
  (e: 'update:providerFilter', value: string): void
  (e: 'update:categoryFilter', value: string): void
  (e: 'update:search', value: string): void
}>()
</script>
