<!--
  PromptStatsCards - Displays summary statistics for prompt templates

  Shows total templates, categories, usage count (30d), and tokens consumed.
-->

<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
    <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)] mb-1">{{ $t('panel.prompts.stats.totalTemplates') }}</p>
          <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ stats.total }}</p>
        </div>
        <div class="text-3xl opacity-60">T</div>
      </div>
    </div>

    <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)] mb-1">{{ $t('panel.prompts.stats.categories') }}</p>
          <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ categoryCount }}</p>
        </div>
        <div class="text-3xl opacity-60">C</div>
      </div>
    </div>

    <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)] mb-1">{{ $t('panel.prompts.stats.usage30d') }}</p>
          <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ stats.usageCount }}</p>
        </div>
        <div class="text-3xl opacity-60">U</div>
      </div>
    </div>

    <div class="bg-[var(--color-surface)] rounded-lg p-4 border border-[var(--color-border)]">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)] mb-1">{{ $t('panel.prompts.stats.tokensUsed') }}</p>
          <p class="text-2xl font-bold text-[var(--color-text-primary)]">{{ formattedTokens }}</p>
        </div>
        <div class="text-3xl opacity-60">$</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PromptStats } from './types/prompt.types.ts'

const { t } = useI18n()

const props = defineProps<{
  stats: PromptStats
  categoryCount: number
}>()

function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formattedTokens = computed(() => formatNumber(props.stats.tokensUsed))
</script>
