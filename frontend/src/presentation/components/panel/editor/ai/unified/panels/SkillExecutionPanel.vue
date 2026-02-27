<script setup lang="ts">
/**
 * SkillExecutionPanel — Active skill execution with embedded Prompt Builder
 */
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
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

const paramValues = ref<Record<string, unknown>>({})
const promptOverride = ref<string | undefined>(undefined)
const showPromptBuilder = ref(false)

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

function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'code', 'pre'],
    ALLOWED_ATTR: [],
  })
}
</script>

<template>
  <div class="skill-execution">
    <!-- Skill Header -->
    <div class="skill-header">
      <div class="skill-header-left">
        <button class="back-btn" @click="emit('back')">←</button>
        <span class="skill-icon">{{ skill.icon }}</span>
        <div>
          <h3 class="skill-name">{{ t(skill.name_i18n_key) }}</h3>
          <p class="skill-desc">{{ t(skill.description_i18n_key) }}</p>
        </div>
      </div>
      <span class="skill-tokens">~{{ skill.estimated_tokens }} tokens</span>
    </div>

    <!-- Parameters -->
    <div class="skill-params">
      <div v-for="param in skill.parameters" :key="param.key" class="param-group">
        <label class="param-label">{{ t(param.label_i18n_key) }}</label>
        <select
          v-if="param.type === 'select' && param.options"
          v-model="paramValues[param.key]"
          class="param-input"
        >
          <option v-for="opt in param.options" :key="opt.value" :value="opt.value">
            {{ t(opt.label_i18n_key) }}
          </option>
        </select>
        <input
          v-else-if="param.type === 'number'"
          v-model.number="paramValues[param.key]"
          type="number"
          class="param-input"
        />
        <input
          v-else
          v-model="paramValues[param.key]"
          type="text"
          class="param-input"
        />
      </div>
    </div>

    <!-- Prompt Builder (Collapsible) -->
    <div class="prompt-section">
      <button class="prompt-toggle" @click="showPromptBuilder = !showPromptBuilder">
        <span>{{ t('aiEditor.prompts.customize') }}</span>
        <span>{{ showPromptBuilder ? '▲' : '▼' }}</span>
      </button>
      <div v-if="showPromptBuilder" class="prompt-builder-wrap">
        <PromptBuilderPanel
          :skill-code="skill.code"
          @override="handlePromptOverride"
        />
      </div>
    </div>

    <!-- Execute Button -->
    <div class="execute-section">
      <button
        class="execute-btn"
        :disabled="isExecuting"
        @click="handleExecute"
      >
        <span v-if="isExecuting" class="pulse">{{ t('aiEditor.skills.generating') }}</span>
        <span v-else>{{ t('aiEditor.skills.generate') }}</span>
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-section">
      <div class="error-msg">{{ error }}</div>
    </div>

    <!-- Result -->
    <div v-if="result" class="result-section">
      <div class="result-card">
        <div class="result-header">
          <span class="result-ready">{{ t('aiEditor.skills.resultReady') }}</span>
          <span class="result-tokens">
            {{ result.tokens_input + result.tokens_output }} tokens
          </span>
        </div>
        <div v-if="typeof result.content === 'string'" class="result-content" v-html="sanitizeHtml(result.content)" />
        <div v-else class="result-content result-fields">
          <div v-for="(value, key) in result.content" :key="String(key)" class="result-field">
            <span class="result-field-key">{{ key }}:</span>
            <span class="result-field-value">{{ typeof value === 'string' ? value : JSON.stringify(value) }}</span>
          </div>
        </div>
      </div>
      <div class="result-actions">
        <button class="action-accept" @click="emit('accept')">
          {{ t('aiEditor.skills.accept') }}
        </button>
        <button class="action-reject" @click="emit('reject')">
          {{ t('aiEditor.skills.reject') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skill-execution {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.skill-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.skill-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.back-btn {
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem;
}

.back-btn:hover { color: var(--color-text-primary); }

.skill-icon { font-size: 1.25rem; }

.skill-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.skill-desc {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin: 0;
}

.skill-tokens {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.skill-params {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.param-group {
  margin-bottom: 0.625rem;
}

.param-group:last-child { margin-bottom: 0; }

.param-label {
  display: block;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.param-input {
  width: 100%;
  padding: 0.375rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  color: var(--color-text-primary);
}

.param-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.prompt-section {
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.prompt-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: none;
  border: none;
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.prompt-toggle:hover { color: var(--color-text-primary); }

.prompt-builder-wrap { padding: 0 0.75rem 0.75rem; }

.execute-section { padding: 0.75rem; flex-shrink: 0; }

.execute-btn {
  width: 100%;
  padding: 0.625rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: filter 0.15s;
}

.execute-btn:hover:not(:disabled) { filter: brightness(1.1); }
.execute-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.pulse { animation: pulse 1.5s infinite; }
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.error-section { padding: 0 0.75rem 0.75rem; }

.error-msg {
  padding: 0.75rem;
  background: var(--color-danger-subtle, #3b1a1a);
  border: 1px solid var(--color-danger, #e53e3e);
  border-radius: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-danger, #fc8181);
}

.result-section {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}

.result-card {
  padding: 0.75rem;
  background: var(--color-surface-secondary, var(--color-surface));
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  margin-bottom: 0.625rem;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.result-ready {
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--color-success, #48bb78);
}

.result-tokens {
  font-size: 0.5625rem;
  color: var(--color-text-tertiary);
}

.result-content {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  max-height: 16rem;
  overflow-y: auto;
  margin: 0;
  line-height: 1.5;
}

.result-fields {
  display: flex;
  flex-direction: column;
}

.result-field {
  padding: 0.25rem 0;
  border-bottom: 1px solid var(--color-border);
}

.result-field:last-child { border-bottom: none; }

.result-field-key {
  font-weight: 600;
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-right: 0.5rem;
}

.result-field-value {
  font-size: 0.75rem;
  color: var(--color-text-primary);
}

.result-actions {
  display: flex;
  gap: 0.5rem;
}

.action-accept,
.action-reject {
  flex: 1;
  padding: 0.5rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  cursor: pointer;
  color: white;
}

.action-accept {
  background: var(--color-success, #22c55e);
}

.action-accept:hover { filter: brightness(0.9); }

.action-reject {
  background: var(--color-surface-secondary, var(--color-surface));
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.action-reject:hover { color: var(--color-text-primary); }
</style>
