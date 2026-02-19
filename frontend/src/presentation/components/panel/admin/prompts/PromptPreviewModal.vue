<!--
  PromptPreviewModal - Shows rendered system and user prompts with sample data
-->

<template>
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-xl shadow-xl max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col">
      <div class="px-6 py-4 border-b border-[var(--color-border)] flex justify-between items-center">
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">Prompt-Vorschau</h2>
        <button @click="$emit('close')" class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
          X
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-6 space-y-4">
        <div>
          <h3 class="text-sm font-medium text-[var(--color-text-secondary)] mb-2">System Prompt</h3>
          <pre class="bg-[var(--color-bg)] p-4 rounded-lg text-sm whitespace-pre-wrap font-mono">{{ previewData?.system_prompt }}</pre>
        </div>
        <div>
          <h3 class="text-sm font-medium text-[var(--color-text-secondary)] mb-2">User Prompt (mit Beispieldaten)</h3>
          <pre class="bg-[var(--color-bg)] p-4 rounded-lg text-sm whitespace-pre-wrap font-mono">{{ previewData?.rendered_prompt }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PromptPreviewData } from './types/prompt.types.ts'

defineProps<{
  previewData: PromptPreviewData | null
}>()

defineEmits<{
  (e: 'close'): void
}>()
</script>
