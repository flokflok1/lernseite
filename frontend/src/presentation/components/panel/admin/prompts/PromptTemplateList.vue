<!--
  PromptTemplateList - Displays the filterable list of prompt templates

  Each row shows template name, category, style, metadata, and action buttons
  for preview, edit, duplicate, and delete.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
    <div class="px-6 py-4 border-b border-[var(--color-border)] flex justify-between items-center">
      <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
        {{ $t('panel.prompts.list.title') }} ({{ templates.length }})
      </h2>
    </div>

    <div v-if="templates.length === 0" class="p-8 text-center text-[var(--color-text-secondary)]">
      {{ $t('panel.prompts.list.empty') }}
    </div>

    <div v-else class="divide-y divide-[var(--color-border)]">
      <div
        v-for="template in templates"
        :key="template.template_id"
        class="p-4 hover:bg-[var(--color-bg)] transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
                {{ template.name }}
              </h3>
              <span
                v-if="template.is_default"
                class="px-2 py-0.5 text-xs rounded bg-green-100 text-green-700"
              >
                {{ $t('panel.prompts.list.default') }}
              </span>
              <span class="px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-700">
                {{ categoryLabels[template.category] || template.category }}
              </span>
              <span class="px-2 py-0.5 text-xs rounded bg-purple-100 text-purple-700">
                {{ styleLabels[template.style] || template.style }}
              </span>
            </div>

            <p class="text-sm text-[var(--color-text-secondary)] mb-2">
              {{ template.description || t('panel.prompts.list.noDescription') }}
            </p>

            <div class="flex items-center gap-4 text-xs text-[var(--color-text-secondary)]">
              <span>Code: <code class="bg-[var(--color-bg)] px-1 rounded">{{ template.code }}</code></span>
              <span>Model: {{ template.model || 'gpt-4o-mini' }}</span>
              <span>Max Tokens: {{ template.max_tokens || 4000 }}</span>
              <span v-if="template.usage_count">{{ template.usage_count }}x {{ t('panel.prompts.list.used') }}</span>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button
              @click="$emit('preview', template)"
              class="px-3 py-1.5 text-sm rounded-lg border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
              :title="t('panel.prompts.actions.preview')"
            >
              {{ $t('panel.prompts.actions.preview') }}
            </button>
            <button
              @click="$emit('edit', template)"
              class="px-3 py-1.5 text-sm rounded-lg border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
              :title="t('panel.prompts.actions.edit')"
            >
              {{ $t('panel.prompts.actions.edit') }}
            </button>
            <button
              @click="$emit('duplicate', template)"
              class="px-3 py-1.5 text-sm rounded-lg border border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-bg)] transition-colors"
              :title="t('panel.prompts.actions.duplicate')"
            >
              {{ $t('panel.prompts.actions.duplicate') }}
            </button>
            <button
              v-if="!template.is_default"
              @click="$emit('delete', template)"
              class="px-3 py-1.5 text-sm rounded-lg border border-red-300 text-red-600 hover:bg-red-50 transition-colors"
              :title="t('panel.prompts.actions.delete')"
            >
              X
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { PromptTemplate } from './types/prompt.types.ts'
import { CATEGORY_LABELS, STYLE_LABELS } from './types/prompt.types.ts'

const { t } = useI18n()

const categoryLabels = CATEGORY_LABELS
const styleLabels = STYLE_LABELS

defineProps<{
  templates: PromptTemplate[]
}>()

defineEmits<{
  (e: 'preview', template: PromptTemplate): void
  (e: 'edit', template: PromptTemplate): void
  (e: 'duplicate', template: PromptTemplate): void
  (e: 'delete', template: PromptTemplate): void
}>()
</script>
