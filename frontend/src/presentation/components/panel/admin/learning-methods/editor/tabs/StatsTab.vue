<template>
  <div class="h-full overflow-y-auto p-6">
    <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-6">
      {{ $t('learningMethodEditor.tabs.statistics') }}
    </h3>

    <!-- Key Metrics -->
    <div class="grid grid-cols-2 gap-4 mb-8">
      <!-- Total Methods -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          {{ $t('learningMethodEditor.totalMethods') }}
        </p>
        <p class="text-3xl font-bold text-[var(--color-primary)]">
          {{ stats?.total_methods || 0 }}
        </p>
      </div>

      <!-- Published Count -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          {{ $t('learningMethodEditor.publishedCount') }}
        </p>
        <p class="text-3xl font-bold text-[var(--color-success)]">
          {{ stats?.published_count || 0 }}
        </p>
      </div>

      <!-- Unique Types -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          {{ $t('learningMethodEditor.uniqueTypes') }}
        </p>
        <p class="text-3xl font-bold text-[var(--color-info)]">
          {{ stats?.unique_types || 0 }}
        </p>
      </div>

      <!-- Total Duration -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <p class="text-xs text-[var(--color-text-secondary)] mb-2">
          {{ $t('learningMethodEditor.totalDuration') }}
        </p>
        <p class="text-3xl font-bold text-[var(--color-warning)]">
          {{ stats?.total_duration || 0 }} {{ $t('learningMethodEditor.minutes') }}
        </p>
      </div>
    </div>

    <!-- Distribution Breakdown -->
    <div class="grid grid-cols-2 gap-4">
      <!-- Difficulty Distribution -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <h4 class="text-sm font-semibold text-[var(--color-text-primary)] mb-4">
          {{ $t('learningMethodEditor.difficultyDistribution') }}
        </h4>
        <div class="space-y-3">
          <!-- Easy -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('learningMethodEditor.easy') }}
              </span>
              <span class="text-sm font-semibold text-[var(--color-success)]">
                {{ stats?.easy_count || 0 }}
              </span>
            </div>
            <div class="h-2 bg-[var(--color-border)] rounded overflow-hidden">
              <div
                class="h-full bg-[var(--color-success)]"
                :style="{ width: getPercentage(stats?.easy_count || 0) }"
              />
            </div>
          </div>

          <!-- Medium -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('learningMethodEditor.medium') }}
              </span>
              <span class="text-sm font-semibold text-[var(--color-warning)]">
                {{ stats?.medium_count || 0 }}
              </span>
            </div>
            <div class="h-2 bg-[var(--color-border)] rounded overflow-hidden">
              <div
                class="h-full bg-[var(--color-warning)]"
                :style="{ width: getPercentage(stats?.medium_count || 0) }"
              />
            </div>
          </div>

          <!-- Hard -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('learningMethodEditor.hard') }}
              </span>
              <span class="text-sm font-semibold text-[var(--color-error)]">
                {{ stats?.hard_count || 0 }}
              </span>
            </div>
            <div class="h-2 bg-[var(--color-border)] rounded overflow-hidden">
              <div
                class="h-full bg-[var(--color-error)]"
                :style="{ width: getPercentage(stats?.hard_count || 0) }"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Tier Distribution -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <h4 class="text-sm font-semibold text-[var(--color-text-primary)] mb-4">
          {{ $t('learningMethodEditor.tierDistribution') }}
        </h4>
        <div class="space-y-3">
          <!-- Basic -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('learningMethodEditor.tierOptions.basic') }}
              </span>
              <span class="text-sm font-semibold text-[var(--color-success)]">
                {{ stats?.basic_count || 0 }}
              </span>
            </div>
            <div class="h-2 bg-[var(--color-border)] rounded overflow-hidden">
              <div
                class="h-full bg-[var(--color-success)]"
                :style="{ width: getPercentage(stats?.basic_count || 0) }"
              />
            </div>
          </div>

          <!-- Premium -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('learningMethodEditor.tierOptions.premium') }}
              </span>
              <span class="text-sm font-semibold text-[var(--color-warning)]">
                {{ stats?.premium_count || 0 }}
              </span>
            </div>
            <div class="h-2 bg-[var(--color-border)] rounded overflow-hidden">
              <div
                class="h-full bg-[var(--color-warning)]"
                :style="{ width: getPercentage(stats?.premium_count || 0) }"
              />
            </div>
          </div>

          <!-- Pro -->
          <div>
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs text-[var(--color-text-secondary)]">
                {{ $t('learningMethodEditor.tierOptions.pro') }}
              </span>
              <span class="text-sm font-semibold" style="color: var(--color-premium-text, #6b21a8);">
                {{ stats?.pro_count || 0 }}
              </span>
            </div>
            <div class="h-2 bg-[var(--color-border)] rounded overflow-hidden">
              <div
                class="h-full"
                style="background-color: var(--color-premium-text, #6b21a8);"
                :style="{ width: getPercentage(stats?.pro_count || 0) }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  stats: {
    total_methods: number
    published_count: number
    unique_types: number
    total_duration: number
    easy_count: number
    medium_count: number
    hard_count: number
    basic_count: number
    premium_count: number
    pro_count: number
  } | null
}

defineProps<Props>()

/**
 * Calculate percentage width for progress bar
 */
const getPercentage = (value: number): string => {
  if (!value) return '0%'
  const total = (props.stats?.total_methods || 1)
  return `${Math.min((value / total) * 100, 100)}%`
}
</script>

<style scoped>
/* Stats Tab styles */
</style>
