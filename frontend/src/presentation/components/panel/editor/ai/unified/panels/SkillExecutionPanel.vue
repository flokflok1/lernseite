<script setup lang="ts">
/**
 * SkillExecutionPanel — Active skill execution with embedded Prompt Builder
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SkillConfig, GenerationResult } from '../types'
import PromptBuilderPanel from './PromptBuilderPanel.vue'

interface Props {
  skill: SkillConfig
  courseId: string
  isExecuting: boolean
  result: GenerationResult | null
  error: string | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  execute: [params: Record<string, unknown>]
  accept: []
  reject: []
  requestVariant: []
  back: []
}>()

const { t } = useI18n()

// Parameter values (filled from skill.parameters defaults)
const paramValues = ref<Record<string, unknown>>({})
const promptOverride = ref<string | undefined>(undefined)
const showPromptBuilder = ref(false)

// Initialize defaults
function initParams() {
  const defaults: Record<string, unknown> = {}
  for (const param of props.skill.parameters) {
    defaults[param.key] = param.default_value
  }
  paramValues.value = defaults
}
initParams()

function handleExecute() {
  emit('execute', {
    parameters: paramValues.value,
    promptOverride: promptOverride.value,
  })
}

function handlePromptOverride(prompt: string | undefined) {
  promptOverride.value = prompt
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Skill Header -->
    <div class="p-4 border-b border-gray-700">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button class="text-gray-500 hover:text-white" @click="emit('back')">←</button>
          <span class="text-xl">{{ skill.icon }}</span>
          <div>
            <h3 class="text-sm font-semibold text-white">{{ t(skill.name_i18n_key) }}</h3>
            <p class="text-xs text-gray-500">{{ t(skill.description_i18n_key) }}</p>
          </div>
        </div>
        <span class="text-xs text-gray-600">~{{ skill.estimated_tokens }} tokens</span>
      </div>
    </div>

    <!-- Parameters -->
    <div class="p-4 space-y-3 border-b border-gray-700">
      <div v-for="param in skill.parameters" :key="param.key" class="space-y-1">
        <label class="text-xs text-gray-400">{{ t(param.label_i18n_key) }}</label>
        <select
          v-if="param.type === 'select' && param.options"
          v-model="paramValues[param.key]"
          class="w-full px-3 py-1.5 bg-gray-800 border border-gray-600 rounded text-sm text-white"
        >
          <option v-for="opt in param.options" :key="opt.value" :value="opt.value">
            {{ t(opt.label_i18n_key) }}
          </option>
        </select>
        <input
          v-else-if="param.type === 'number'"
          v-model.number="paramValues[param.key]"
          type="number"
          class="w-full px-3 py-1.5 bg-gray-800 border border-gray-600 rounded text-sm text-white"
        />
        <input
          v-else
          v-model="paramValues[param.key]"
          type="text"
          class="w-full px-3 py-1.5 bg-gray-800 border border-gray-600 rounded text-sm text-white"
        />
      </div>
    </div>

    <!-- Prompt Builder (Collapsible) -->
    <div class="border-b border-gray-700">
      <button
        class="w-full px-4 py-2 flex items-center justify-between text-xs text-gray-400 hover:text-white"
        @click="showPromptBuilder = !showPromptBuilder"
      >
        <span>{{ t('aiEditor.prompts.customize') }}</span>
        <span>{{ showPromptBuilder ? '▲' : '▼' }}</span>
      </button>
      <div v-if="showPromptBuilder" class="px-4 pb-4">
        <PromptBuilderPanel
          :skill-code="skill.code"
          @override="handlePromptOverride"
        />
      </div>
    </div>

    <!-- Execute Button -->
    <div class="p-4">
      <button
        class="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg text-sm font-medium transition-colors"
        :disabled="isExecuting"
        @click="handleExecute"
      >
        <span v-if="isExecuting" class="animate-pulse">{{ t('aiEditor.skills.generating') }}</span>
        <span v-else>{{ t('aiEditor.skills.generate') }}</span>
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="px-4 pb-4">
      <div class="p-3 bg-red-900/30 border border-red-800 rounded-lg text-xs text-red-300">
        {{ error }}
      </div>
    </div>

    <!-- Result -->
    <div v-if="result" class="flex-1 overflow-y-auto p-4 space-y-3">
      <div class="p-3 bg-gray-800 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs text-green-400 font-medium">{{ t('aiEditor.skills.resultReady') }}</span>
          <span class="text-[10px] text-gray-500">
            {{ result.tokens_input + result.tokens_output }} tokens
          </span>
        </div>
        <pre class="text-xs text-gray-300 whitespace-pre-wrap max-h-64 overflow-y-auto">{{ JSON.stringify(result.content, null, 2) }}</pre>
      </div>
      <div class="flex gap-2">
        <button
          class="flex-1 py-2 bg-green-600 hover:bg-green-500 text-white rounded text-sm"
          @click="emit('accept')"
        >
          {{ t('aiEditor.skills.accept') }}
        </button>
        <button
          class="flex-1 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm"
          @click="emit('reject')"
        >
          {{ t('aiEditor.skills.reject') }}
        </button>
      </div>
    </div>
  </div>
</template>
