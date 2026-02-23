<script setup lang="ts">
/**
 * PromptBuilderPanel — Template selection, variable editor, live preview
 */
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { PROMPT_PRESETS, type PromptPreset } from '../types'
import { usePromptBuilder } from '../composables'

interface Props {
  skillCode: string
}

const props = defineProps<Props>()
const emit = defineEmits<{ override: [prompt: string | undefined] }>()
const { t } = useI18n()

const builder = usePromptBuilder()

const presets = PROMPT_PRESETS

const customPrompt = ref('')
const useCustom = ref(false)

function selectPreset(preset: PromptPreset) {
  builder.applyPreset(preset)
  emit('override', builder.getOverridePrompt())
}

function handleCustomChange() {
  emit('override', useCustom.value ? customPrompt.value : undefined)
}

watch(customPrompt, handleCustomChange)
watch(useCustom, handleCustomChange)
</script>

<template>
  <div class="space-y-3">
    <!-- Presets -->
    <div>
      <label class="text-xs text-gray-400 block mb-1.5">{{ t('aiEditor.prompts.style') }}</label>
      <div class="flex gap-2">
        <button
          v-for="preset in presets"
          :key="preset.id"
          class="px-2.5 py-1 rounded text-xs transition-colors"
          :class="builder.selectedPreset.value?.id === preset.id
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-800 text-gray-400 hover:text-white'"
          @click="selectPreset(preset)"
        >
          {{ t(preset.name_i18n_key) }}
        </button>
      </div>
    </div>

    <!-- Custom Prompt Toggle -->
    <div class="flex items-center gap-2">
      <input
        v-model="useCustom"
        type="checkbox"
        class="rounded bg-gray-800 border-gray-600 text-indigo-600"
      />
      <label class="text-xs text-gray-400">{{ t('aiEditor.prompts.useCustom') }}</label>
    </div>

    <!-- Custom Prompt Textarea -->
    <div v-if="useCustom">
      <textarea
        v-model="customPrompt"
        rows="4"
        :placeholder="t('aiEditor.prompts.customPlaceholder')"
        class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-xs text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none resize-none"
      />
    </div>

    <!-- Preview -->
    <div v-if="builder.hasCustomizations.value || useCustom" class="space-y-1">
      <label class="text-xs text-gray-500">{{ t('aiEditor.prompts.preview') }}</label>
      <div class="p-2 bg-gray-900 rounded text-[11px] text-gray-400 max-h-24 overflow-y-auto font-mono">
        {{ useCustom ? customPrompt : builder.renderedPrompt.value }}
      </div>
    </div>
  </div>
</template>
