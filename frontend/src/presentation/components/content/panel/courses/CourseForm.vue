<template>
  <form @submit.prevent="$emit('submit')" class="space-y-4">
    <!-- Title -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
        {{ $t('courseForm.titleLabel') }}
      </label>
      <input
        :value="modelValue.title"
        @input="updateField('title', ($event.target as HTMLInputElement).value)"
        type="text"
        required
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
        :placeholder="$t('courseForm.titlePlaceholder')"
      />
    </div>

    <!-- Description -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
        {{ $t('courseForm.descriptionLabel') }}
      </label>
      <textarea
        v-model="localData.description"
        rows="4"
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
        :placeholder="$t('courseForm.descriptionPlaceholder')"
      ></textarea>
    </div>

    <!-- Category Picker -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
        {{ $t('courseForm.categoryLabel') }}
      </label>
      <select
        v-model="localData.category_id"
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
      >
        <option :value="null">{{ $t('courseForm.categoryNone') }}</option>
        <option
          v-for="category in flatCategories"
          :key="category.category_id"
          :value="category.category_id"
        >
          {{ getCategoryIndent(category.level) }}{{ category.name }}
        </option>
      </select>
      <p class="mt-1 text-xs text-[var(--color-text-secondary)]">
        {{ $t('courseForm.categoryHint') }}
      </p>
    </div>

    <!-- Level -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
        {{ $t('courseForm.levelLabel') }}
      </label>
      <select
        v-model="localData.level"
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
      >
        <option value="beginner">{{ $t('courseForm.levelBeginner') }}</option>
        <option value="intermediate">{{ $t('courseForm.levelIntermediate') }}</option>
        <option value="advanced">{{ $t('courseForm.levelAdvanced') }}</option>
      </select>
    </div>

    <!-- Language -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
        {{ $t('courseForm.languageLabel') }}
      </label>
      <select
        v-model="localData.language"
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
      >
        <option value="de">{{ $t('courseForm.langDe') }}</option>
        <option value="en">{{ $t('courseForm.langEn') }}</option>
        <option value="fr">{{ $t('courseForm.langFr') }}</option>
        <option value="es">{{ $t('courseForm.langEs') }}</option>
      </select>
    </div>

    <!-- Price -->
    <div>
      <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
        {{ $t('courseForm.priceLabel') }}
      </label>
      <input
        v-model.number="localData.price"
        type="number"
        min="0"
        step="0.01"
        class="w-full px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
        :placeholder="$t('courseForm.pricePlaceholder')"
      />
    </div>

    <!-- Is Public -->
    <div>
      <label class="flex items-center gap-2 cursor-pointer">
        <input
          v-model="localData.is_public"
          type="checkbox"
          class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded focus:ring-[var(--color-primary)]"
        />
        <span class="text-sm text-[var(--color-text-secondary)]">
          {{ $t('courseForm.isPublic') }}
        </span>
      </label>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AdminCourseCreateRequest, Category } from '@/application/services/api/admin'

interface Props {
  modelValue: AdminCourseCreateRequest
  categories?: Category[]
  isSubmitting?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: AdminCourseCreateRequest): void
  (e: 'submit'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Individual computed properties for each field to ensure reactivity
const localData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Helper to update individual fields
const updateField = <K extends keyof AdminCourseCreateRequest>(field: K, value: AdminCourseCreateRequest[K]) => {
  emit('update:modelValue', {
    ...props.modelValue,
    [field]: value
  })
}

const flatCategories = computed(() => {
  if (!props.categories) return []
  // Flatten tree - assuming categories are already flat or will be flattened by parent
  return props.categories
})

const getCategoryIndent = (level: number): string => {
  return '—'.repeat(level - 1) + (level > 1 ? ' ' : '')
}
</script>
