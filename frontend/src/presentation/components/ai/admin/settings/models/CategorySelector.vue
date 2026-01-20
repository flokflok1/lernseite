<!--
  CategorySelector - Default Model Selection per Category
  Sub-component of ModelsTab
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
    <div class="flex items-center gap-3 mb-3">
      <span
        class="w-10 h-10 rounded-lg flex items-center justify-center text-xl text-white"
        :class="categoryStyle.bgColor"
      >
        {{ categoryStyle.emoji }}
      </span>
      <div>
        <h4 class="font-medium text-[var(--color-text-primary)] capitalize">{{ category }}</h4>
        <p class="text-xs text-[var(--color-text-tertiary)]">{{ categoryStyle.description }}</p>
      </div>
    </div>
    <select
      :value="selectedModelId"
      @change="$emit('update:selectedModelId', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : null)"
      class="w-full px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] text-sm"
    >
      <option :value="null">-- {{ $t('windows.aiStudioModels.notConfigured') }} --</option>
      <option
        v-for="model in models"
        :key="model.model_id"
        :value="model.model_id"
      >
        {{ model.display_name || model.model_name }} ({{ model.provider_name }})
      </option>
    </select>
    <div class="mt-2 flex items-center justify-between text-xs">
      <span class="text-[var(--color-text-tertiary)]">
        {{ models.length }} {{ $t('windows.aiStudioModels.available') }}
      </span>
      <span v-if="selectedModelId" class="text-green-500">
        ✓ {{ $t('windows.aiStudioModels.configured') }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface AIModel {
  model_id: number
  model_name: string
  display_name: string
  provider_name: string
}

interface CategoryStyle {
  emoji: string
  bgColor: string
  description: string
}

defineProps<{
  category: string
  categoryStyle: CategoryStyle
  models: AIModel[]
  selectedModelId: number | null
}>()

defineEmits<{
  (e: 'update:selectedModelId', value: number | null): void
}>()
</script>
