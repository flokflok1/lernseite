<script setup lang="ts">
/**
 * GenerationResultPanel — Result display, variant comparison, accept/reject
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { GenerationResult } from '../types'

interface Props {
  result: GenerationResult
}

const props = defineProps<Props>()

const emit = defineEmits<{
  accept: []
  reject: []
  requestVariant: []
}>()

const { t } = useI18n()

const totalTokens = computed(() => props.result.tokens_input + props.result.tokens_output)

const contentPreview = computed(() => {
  const content = props.result.content
  if (content.raw_text) return content.raw_text as string
  return JSON.stringify(content, null, 2)
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="p-4 border-b border-gray-700 flex items-center justify-between">
      <div>
        <h3 class="text-sm font-semibold text-white">{{ t('aiEditor.result.title') }}</h3>
        <p class="text-xs text-gray-500">{{ result.skill_code }} · {{ result.model_name }}</p>
      </div>
      <div class="text-right">
        <div class="text-xs text-gray-400">{{ totalTokens.toLocaleString() }} tokens</div>
        <div class="text-[10px] text-gray-600">{{ result.provider_name }}</div>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-4">
      <pre class="text-xs text-gray-300 whitespace-pre-wrap bg-gray-800/50 p-3 rounded-lg">{{ contentPreview }}</pre>
    </div>

    <!-- Variants -->
    <div v-if="result.variants && result.variants.length > 0" class="px-4 pb-2">
      <label class="text-xs text-gray-500 mb-1 block">{{ t('aiEditor.result.variants') }}</label>
      <div class="flex gap-2">
        <button
          v-for="variant in result.variants"
          :key="variant.variant_id"
          class="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-300"
        >
          {{ variant.label }}
        </button>
      </div>
    </div>

    <!-- Actions -->
    <div class="p-4 border-t border-gray-700 flex gap-2">
      <button
        class="flex-1 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg text-sm font-medium"
        @click="emit('accept')"
      >
        {{ t('aiEditor.result.accept') }}
      </button>
      <button
        class="py-2 px-4 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm"
        @click="emit('requestVariant')"
      >
        {{ t('aiEditor.result.newVariant') }}
      </button>
      <button
        class="py-2 px-4 bg-gray-700 hover:bg-gray-600 text-red-400 rounded-lg text-sm"
        @click="emit('reject')"
      >
        {{ t('aiEditor.result.reject') }}
      </button>
    </div>
  </div>
</template>
