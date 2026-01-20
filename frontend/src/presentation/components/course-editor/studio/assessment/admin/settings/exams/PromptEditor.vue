<!--
  PromptEditor - Prompt Edit Panel
  Sub-component of PromptsTab
-->

<template>
  <div class="space-y-4">
    <template v-if="prompt">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wide">
          {{ $t('features.aiEditorPrompts.editor') }}
        </h3>
        <div class="flex gap-2">
          <button
            @click="$emit('test')"
            class="px-3 py-1.5 text-sm bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400 rounded-lg hover:bg-violet-200 dark:hover:bg-violet-900/50 transition-colors"
          >
            🧪 {{ $t('features.aiEditorPrompts.test') }}
          </button>
          <button
            @click="$emit('duplicate')"
            class="px-3 py-1.5 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)]"
          >
            📋
          </button>
        </div>
      </div>

      <!-- Prompt Name -->
      <div>
        <label class="text-xs text-[var(--color-text-tertiary)] mb-1 block">
          {{ $t('features.aiEditorPrompts.name') }}
        </label>
        <input
          :value="prompt.name"
          @input="updateField('name', ($event.target as HTMLInputElement).value)"
          type="text"
          class="w-full px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="text-xs text-[var(--color-text-tertiary)] mb-1 block">
          {{ $t('features.aiEditorPrompts.description') }}
        </label>
        <input
          :value="prompt.description"
          @input="updateField('description', ($event.target as HTMLInputElement).value)"
          type="text"
          class="w-full px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
        />
      </div>

      <!-- Prompt Content -->
      <div class="flex-1">
        <div class="flex items-center justify-between mb-1">
          <label class="text-xs text-[var(--color-text-tertiary)]">
            {{ $t('features.aiEditorPrompts.prompt') }}
          </label>
          <span class="text-xs text-[var(--color-text-tertiary)]">
            {{ prompt.content.length }} {{ $t('features.aiEditorPrompts.characters') }}
          </span>
        </div>
        <textarea
          :value="prompt.content"
          @input="updateField('content', ($event.target as HTMLTextAreaElement).value)"
          class="w-full h-48 px-3 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono text-sm resize-none"
          :placeholder="$t('features.aiEditorPrompts.placeholder')"
        ></textarea>
      </div>

      <!-- Variables -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="text-xs text-[var(--color-text-tertiary)]">
            {{ $t('features.aiEditorPrompts.variables') }}
          </label>
          <button
            @click="$emit('addVariable')"
            class="text-xs text-[var(--color-primary)] hover:underline"
          >
            {{ $t('features.aiEditorPrompts.addVariable') }}
          </button>
        </div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="variable in prompt.variables"
            :key="variable"
            class="px-2 py-1 bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 rounded text-xs font-mono cursor-pointer hover:bg-blue-200"
            @click="$emit('insertVariable', variable)"
          >
            {{ formatVariable(variable) }}
          </span>
        </div>
        <p class="text-xs text-[var(--color-text-tertiary)] mt-1">
          {{ $t('features.aiEditorPrompts.variableHint') }}
        </p>
      </div>

      <!-- Target LMs -->
      <div>
        <label class="text-xs text-[var(--color-text-tertiary)] mb-2 block">
          {{ $t('features.aiEditorPrompts.targetLMs') }}
        </label>
        <div class="flex flex-wrap gap-1">
          <button
            v-for="lm in learningMethods.slice(0, 10)"
            :key="lm.id"
            @click="$emit('toggleLM', lm.id)"
            class="px-2 py-1 text-xs rounded transition-colors"
            :class="prompt.targetLMs.includes(lm.id)
              ? 'bg-[var(--color-primary)] text-white'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)]'"
          >
            {{ lm.code }}
          </button>
          <button class="px-2 py-1 text-xs text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)]">
            {{ $t('features.aiEditorPrompts.moreCount', { count: learningMethods.length - 10 }) }}
          </button>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-2 pt-4 border-t border-[var(--color-border)]">
        <button
          @click="$emit('save')"
          class="flex-1 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
        >
          {{ $t('features.aiEditorPrompts.save') }}
        </button>
        <button
          @click="$emit('delete')"
          class="px-4 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
        >
          🗑️
        </button>
      </div>
    </template>

    <!-- No Prompt Selected -->
    <div v-else class="flex flex-col items-center justify-center h-full text-center py-12">
      <span class="text-4xl mb-4">📝</span>
      <h3 class="text-lg font-medium text-[var(--color-text-primary)] mb-2">
        {{ $t('features.aiEditorPrompts.selectPrompt') }}
      </h3>
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ $t('features.aiEditorPrompts.selectPromptHint') }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Prompt {
  id: string
  name: string
  description: string
  content: string
  category: string
  variables: string[]
  targetLMs: string[]
  tokens: number
  isActive: boolean
  lastUpdated: string
}

interface LearningMethod {
  id: string
  code: string
  name: string
}

const props = defineProps<{
  prompt: Prompt | null
  learningMethods: LearningMethod[]
}>()

const emit = defineEmits<{
  (e: 'test'): void
  (e: 'duplicate'): void
  (e: 'save'): void
  (e: 'delete'): void
  (e: 'addVariable'): void
  (e: 'insertVariable', variable: string): void
  (e: 'toggleLM', lmId: string): void
  (e: 'update:field', field: keyof Prompt, value: unknown): void
}>()

function updateField(field: keyof Prompt, value: unknown) {
  emit('update:field', field, value)
}

function formatVariable(variable: string): string {
  return '{{' + variable + '}}'
}
</script>
