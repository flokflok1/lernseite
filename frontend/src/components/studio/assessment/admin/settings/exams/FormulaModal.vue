<!--
  FormulaModal - LaTeX Formula Creator
  Sub-component of AssetsTab
-->

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-xl p-6 w-[600px] max-h-[80vh] overflow-y-auto">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
        {{ $t('windows.aiEditorAssets.formulaModal.title') }}
      </h3>

      <div class="space-y-4">
        <!-- LaTeX Input -->
        <div>
          <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">
            {{ $t('windows.aiEditorAssets.formulaModal.latexCode') }}
          </label>
          <textarea
            :value="modelValue"
            @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
            class="w-full h-32 px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono resize-none"
            :placeholder="$t('windows.aiEditorAssets.formulaModal.latexPlaceholder')"
          ></textarea>
        </div>

        <!-- Preview -->
        <div>
          <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">
            {{ $t('windows.aiEditorAssets.formulaModal.preview') }}
          </label>
          <div class="h-24 bg-white dark:bg-gray-800 border border-[var(--color-border)] rounded-lg flex items-center justify-center">
            <span class="text-2xl">{{ preview }}</span>
          </div>
        </div>

        <!-- Common Formulas -->
        <div>
          <label class="text-sm text-[var(--color-text-secondary)] mb-2 block">
            {{ $t('windows.aiEditorAssets.formulaModal.commonFormulas') }}
          </label>
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="formula in commonFormulas"
              :key="formula.latex"
              @click="$emit('update:modelValue', formula.latex)"
              class="p-2 bg-[var(--color-surface-secondary)] rounded-lg hover:bg-[var(--color-primary-subtle)] transition-colors text-center"
              :title="formula.name"
            >
              {{ formula.preview }}
            </button>
          </div>
        </div>
      </div>

      <div class="flex justify-end gap-2 mt-6">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
        >
          {{ $t('windows.aiEditorAssets.cancel') }}
        </button>
        <button
          @click="$emit('save')"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)]"
        >
          {{ $t('windows.aiEditorAssets.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'


defineEmits<{
  (e: 'close'): void
  (e: 'save'): void
  (e: 'update:modelValue', value: string): void
}>()

const commonFormulas = [
  { name: 'Bruch', latex: '\\frac{a}{b}', preview: 'a/b' },
  { name: 'Wurzel', latex: '\\sqrt{x}', preview: '√x' },
  { name: 'Potenz', latex: 'x^{n}', preview: 'xⁿ' },
  { name: 'Summe', latex: '\\sum_{i=1}^{n}', preview: 'Σ' },
  { name: 'Prozent', latex: 'P \\times r\\%', preview: 'P×r%' },
  { name: 'Gleichung', latex: 'a + b = c', preview: 'a+b=c' },
  { name: 'Multiplikation', latex: 'a \\times b', preview: 'a×b' },
  { name: 'Division', latex: 'a \\div b', preview: 'a÷b' }
]

const props = defineProps<{
  show: boolean
  modelValue: string
}>()

const preview = computed(() => props.modelValue || '...')
</script>
