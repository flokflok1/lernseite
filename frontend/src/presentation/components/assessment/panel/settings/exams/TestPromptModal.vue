<!--
  TestPromptModal - Prompt Testing Modal
  Sub-component of PromptsTab
-->

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-xl p-6 w-[700px] max-h-[80vh] overflow-y-auto">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
        {{ $t('aiEditorPrompts.testPromptTitle') }}
      </h3>

      <!-- Variable Inputs -->
      <div class="space-y-3 mb-4">
        <div v-for="variable in variables" :key="variable">
          <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">{{ variable }}</label>
          <input
            :value="testVariables[variable]"
            @input="updateVariable(variable, ($event.target as HTMLInputElement).value)"
            type="text"
            class="w-full px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg"
            :placeholder="$t('aiEditorPrompts.valuePlaceholder', { variable })"
          />
        </div>
      </div>

      <!-- Rendered Prompt -->
      <div class="mb-4">
        <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">
          {{ $t('aiEditorPrompts.renderedPrompt') }}
        </label>
        <div class="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-sm max-h-48 overflow-y-auto">
          {{ renderedPrompt }}
        </div>
      </div>

      <!-- Test Result -->
      <div v-if="testResult">
        <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">
          {{ $t('aiEditorPrompts.aiResponse') }}
        </label>
        <div class="bg-[var(--color-surface-secondary)] rounded-lg p-4 text-sm max-h-48 overflow-y-auto">
          {{ testResult }}
        </div>
      </div>

      <div class="flex justify-end gap-2 mt-6">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
        >
          {{ $t('aiEditorPrompts.close') }}
        </button>
        <button
          @click="$emit('run')"
          :disabled="isRunning"
          class="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 disabled:opacity-50"
        >
          {{ isRunning ? $t('aiEditorPrompts.running') : $t('aiEditorPrompts.runTest') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
  variables: string[]
  testVariables: Record<string, string>
  renderedPrompt: string
  testResult: string | null
  isRunning: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'run'): void
  (e: 'update:variable', variable: string, value: string): void
}>()

function updateVariable(variable: string, value: string) {
  emit('update:variable', variable, value)
}
</script>
