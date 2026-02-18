<template>
  <div class="bg-[var(--color-surface)] rounded shadow-sm p-3 mb-3 border border-[var(--color-border)]">
    <div class="grid grid-cols-1 md:grid-cols-6 gap-2 items-end">
      <!-- Search -->
      <div class="md:col-span-2">
        <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
          {{ $t('common.search') }}
        </label>
        <input
          :value="searchQuery"
          type="text"
          :placeholder="$t('panel.courses.searchPlaceholder')"
          class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)] focus:border-transparent"
          @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
        />
      </div>

      <!-- Category Filter -->
      <div>
        <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
          {{ $t('courses.category') }}
        </label>
        <select
          :value="categoryFilter"
          class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)] focus:border-transparent"
          @change="$emit('update:categoryFilter', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : undefined)"
        >
          <option :value="undefined">{{ $t('panel.courses.allCategories') }}</option>
          <option
            v-for="cat in flatCategories"
            :key="cat.category_id"
            :value="cat.category_id"
          >
            {{ '\u2014'.repeat(cat.level - 1) }} {{ cat.name }}
          </option>
        </select>
      </div>

      <!-- Status Filter -->
      <div>
        <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
          {{ $t('common.status') }}
        </label>
        <select
          :value="statusFilter"
          class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)] focus:border-transparent"
          @change="$emit('update:statusFilter', ($event.target as HTMLSelectElement).value)"
        >
          <option value="all">{{ $t('panel.courses.allStatus') }}</option>
          <option value="draft">{{ $t('panel.courses.draft') }}</option>
          <option value="published">{{ $t('panel.courses.statusPublished') }}</option>
          <option value="archived">{{ $t('panel.courses.archived') }}</option>
        </select>
      </div>

      <!-- Level Filter -->
      <div>
        <label class="block text-xs font-medium text-[var(--color-text-secondary)] mb-1">
          Level
        </label>
        <select
          :value="levelFilter"
          class="w-full px-2 py-1.5 text-sm border border-[var(--color-border)] rounded bg-[var(--color-background)] text-[var(--color-text-primary)] focus:ring-1 focus:ring-[var(--color-primary)] focus:border-transparent"
          @change="$emit('update:levelFilter', ($event.target as HTMLSelectElement).value)"
        >
          <option value="">{{ $t('courses.level_all') }}</option>
          <option value="beginner">{{ $t('courses.level_beginner') }}</option>
          <option value="intermediate">{{ $t('courses.level_intermediate') }}</option>
          <option value="advanced">{{ $t('courses.level_advanced') }}</option>
        </select>
      </div>

      <!-- Reset Filters Button -->
      <div>
        <button
          @click="$emit('reset')"
          class="w-full px-2 py-1.5 text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] border border-[var(--color-border)] rounded hover:bg-[var(--color-background)]"
        >
          {{ $t('common.reset') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Category } from '@/application/services/api/panel-admin'

interface Props {
  searchQuery: string
  statusFilter: 'all' | 'draft' | 'published' | 'archived'
  levelFilter: string
  categoryFilter: number | undefined
  flatCategories: Category[]
}

defineProps<Props>()

defineEmits<{
  'update:searchQuery': [value: string]
  'update:statusFilter': [value: string]
  'update:levelFilter': [value: string]
  'update:categoryFilter': [value: number | undefined]
  reset: []
}>()
</script>
