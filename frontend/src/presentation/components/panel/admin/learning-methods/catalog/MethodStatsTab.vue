<!--
  MethodStatsTab - Statistics overview for the learning methods
  in a chapter, showing counts by difficulty and tier.
-->

<template>
  <div class="h-full overflow-y-auto p-6">
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
        {{ $t('learningMethodEditor.stats.title') }}
      </h3>
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ $t('learningMethodEditor.stats.description') }}
      </p>
    </div>

    <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
        <p class="text-3xl font-bold text-[var(--color-text-primary)]">{{ stats.total_methods }}</p>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('learningMethodEditor.stats.total') }}</p>
      </div>
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
        <p class="text-3xl font-bold" style="color: var(--color-success, #16a34a);">{{ stats.published_count }}</p>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('learningMethodEditor.stats.publishedCount') }}</p>
      </div>
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
        <p class="text-3xl font-bold text-[var(--color-primary)]">{{ stats.unique_types }}</p>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('learningMethodEditor.stats.methodTypes') }}</p>
      </div>
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
        <p class="text-3xl font-bold text-[var(--color-text-primary)]">{{ stats.total_duration }} {{ $t('learningMethodEditor.minutes') }}</p>
        <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('learningMethodEditor.stats.totalDuration') }}</p>
      </div>
    </div>

    <!-- Difficulty & Tier Distribution -->
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <h4 class="font-medium text-[var(--color-text-primary)] mb-3">
          {{ $t('learningMethodEditor.stats.difficultyTitle') }}
        </h4>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">{{ $t('learningMethodEditor.difficultyOptions.easy') }}</span>
            <span class="font-medium" style="color: var(--color-success, #16a34a);">{{ stats.easy_count }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">{{ $t('learningMethodEditor.difficultyOptions.medium') }}</span>
            <span class="font-medium" style="color: var(--color-warning, #ea580c);">{{ stats.medium_count }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">{{ $t('learningMethodEditor.difficultyOptions.hard') }}</span>
            <span class="font-medium" style="color: var(--color-error, #dc2626);">{{ stats.hard_count }}</span>
          </div>
        </div>
      </div>

      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <h4 class="font-medium text-[var(--color-text-primary)] mb-3">
          {{ $t('learningMethodEditor.stats.tierTitle') }}
        </h4>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">Basic</span>
            <span class="font-medium" style="color: var(--color-success, #16a34a);">{{ stats.basic_count }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">Premium</span>
            <span class="font-medium" style="color: var(--color-warning, #ea580c);">{{ stats.premium_count }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">Pro</span>
            <span class="font-medium" style="color: var(--color-premium-text, #6b21a8);">{{ stats.pro_count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LearningMethodStats } from './composables/useLearningMethodEditor'

interface Props {
  stats: LearningMethodStats | null
}

defineProps<Props>()
</script>
