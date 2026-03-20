<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { BlockType } from './types/structogram.types'

const emit = defineEmits<{
  add: [type: BlockType]
  clear: []
}>()

const { t } = useI18n()

const tools: { type: BlockType; icon: string; color: string; labelKey: string; descKey: string }[] = [
  { type: 'sequence', icon: '\u25A0', color: 'text-emerald-500', labelKey: 'structogramBuilder.addSequence', descKey: 'structogramBuilder.descSequence' },
  { type: 'if', icon: '\u25C6', color: 'text-amber-500', labelKey: 'structogramBuilder.addIf', descKey: 'structogramBuilder.descIf' },
  { type: 'while', icon: '\u21BB', color: 'text-violet-500', labelKey: 'structogramBuilder.addWhile', descKey: 'structogramBuilder.descWhile' },
  { type: 'switch', icon: '\u2630', color: 'text-pink-500', labelKey: 'structogramBuilder.addSwitch', descKey: 'structogramBuilder.descSwitch' },
]
</script>

<template>
  <div class="space-y-1.5">
    <p class="text-xs font-semibold text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">
      {{ t('structogramBuilder.blocks') }}
    </p>
    <button
      v-for="tool in tools"
      :key="tool.type"
      class="w-full text-left px-3 py-2.5 rounded-lg border border-[var(--color-border)]
             bg-[var(--color-surface)] hover:border-blue-500/50 transition-all cursor-pointer"
      @click="emit('add', tool.type)"
    >
      <span :class="['mr-2', tool.color]">{{ tool.icon }}</span>
      <span class="text-sm font-medium text-[var(--color-text)]">{{ t(tool.labelKey) }}</span>
      <span class="block text-xs text-[var(--color-text-secondary)] ml-5">{{ t(tool.descKey) }}</span>
    </button>

    <div class="pt-3 mt-3 border-t border-[var(--color-border)]">
      <button
        class="w-full text-left px-3 py-2 rounded-lg border border-red-500/20
               bg-[var(--color-surface)] hover:border-red-500/50 transition-all cursor-pointer
               text-sm text-red-400"
        @click="emit('clear')"
      >
        {{ t('structogramBuilder.clear') }}
      </button>
    </div>
  </div>
</template>
