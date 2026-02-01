<template>
  <div class="h-full overflow-y-auto p-6">
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-2">Statistiken</h3>
      <p class="text-sm text-[var(--color-text-secondary)]">
        Übersicht der Lernmethoden-Nutzung in diesem Kapitel
      </p>
    </div>

    <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
        <p class="text-3xl font-bold text-[var(--color-text-primary)]">{{ stats.total_methods }}</p>
        <p class="text-sm text-[var(--color-text-secondary)]">Gesamt</p>
      </div>
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
        <p class="text-3xl font-bold" style="color: var(--color-success, #16a34a);">{{ stats.published_count }}</p>
        <p class="text-sm text-[var(--color-text-secondary)]">Veröffentlicht</p>
      </div>
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
        <p class="text-3xl font-bold text-[var(--color-primary)]">{{ stats.unique_types }}</p>
        <p class="text-sm text-[var(--color-text-secondary)]">Methoden-Typen</p>
      </div>
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4 text-center">
        <p class="text-3xl font-bold text-[var(--color-text-primary)]">{{ stats.total_duration }} Min</p>
        <p class="text-sm text-[var(--color-text-secondary)]">Gesamtdauer</p>
      </div>
    </div>

    <!-- Difficulty Distribution -->
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <h4 class="font-medium text-[var(--color-text-primary)] mb-3">Schwierigkeit</h4>
        <div class="space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">Einfach</span>
            <span class="font-medium" style="color: var(--color-success, #16a34a);">{{ stats.easy_count }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">Mittel</span>
            <span class="font-medium" style="color: var(--color-warning, #ea580c);">{{ stats.medium_count }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm text-[var(--color-text-secondary)]">Schwer</span>
            <span class="font-medium" style="color: var(--color-error, #dc2626);">{{ stats.hard_count }}</span>
          </div>
        </div>
      </div>

      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <h4 class="font-medium text-[var(--color-text-primary)] mb-3">Tier-Verteilung</h4>
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
</script>
