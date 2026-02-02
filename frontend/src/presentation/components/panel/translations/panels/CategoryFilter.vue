<script setup lang="ts">
/**
 * CategoryFilter Component
 *
 * Filter buttons for selecting translation categories
 * Shows count of items in each category
 */

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface Category {
  category: string
  count: number
}

interface CategoryOption {
  label: string
  value: string
  icon: string
  count: number
}

interface Props {
  categories: Category[]
  selectedCategory: string | null
}

interface Emits {
  (e: 'category-selected', category: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { t } = useI18n()

const categoryOptions = computed(() => {
  return props.categories.map(cat => ({
    label: t(`panel.i18n.category_${cat.category.toLowerCase()}`),
    value: cat.category,
    icon: getCategoryIcon(cat.category),
    count: cat.count
  }))
})

function getCategoryIcon(category: string): string {
  const icons: Record<string, string> = {
    NEW_KEYS: '➕',
    CHANGED_KEYS: '✏️',
    DELETED_KEYS: '🗑️',
    CONFLICTS: '⚠️'
  }
  return icons[category] || '📌'
}

function handleCategorySelect(category: string): void {
  emit('category-selected', category)
}
</script>

<template>
  <div v-if="categoryOptions.length > 0" class="category-filter">
    <button
      v-for="cat in categoryOptions"
      :key="cat.value"
      class="category-button"
      :class="{ active: selectedCategory === cat.value }"
      :title="`${cat.label}: ${cat.count} ${cat.count === 1 ? 'item' : 'items'}`"
      @click="handleCategorySelect(cat.value)"
    >
      <span class="category-icon">{{ cat.icon }}</span>
      <span class="category-label">{{ cat.label }}</span>
      <span class="category-count">{{ cat.count }}</span>
    </button>
  </div>
</template>

<style scoped>
.category-filter {
  display: flex;
  gap: 8px;
  padding: 12px 0;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--color-border, #e0e0e0);
  margin-bottom: 16px;
}

.category-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background-color: var(--color-surface, #f5f5f5);
  border: 1px solid var(--color-border, #e0e0e0);
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary, #333);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.category-button:hover {
  border-color: var(--color-primary, #2196f3);
  background-color: var(--color-primary-light, #e3f2fd);
}

.category-button.active {
  background-color: var(--color-primary, #2196f3);
  color: white;
  border-color: var(--color-primary, #2196f3);
}

.category-icon {
  flex-shrink: 0;
  font-size: 16px;
}

.category-label {
  flex: 1;
}

.category-count {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 600;
  min-width: 24px;
  text-align: center;
}

.category-button.active .category-count {
  background-color: rgba(255, 255, 255, 0.3);
}
</style>
