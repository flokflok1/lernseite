/**
 * usePromptBuilder — Template loading, variable filling, live preview
 */
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PromptPreset } from '../../types'
import { PROMPT_PRESETS } from '../../types'

export function usePromptBuilder() {
  const { t } = useI18n()

  // ── State ───────────────────────────────────────────────────────
  const templateCode = ref('')
  const systemPrompt = ref('')
  const userPrompt = ref('')
  const variables = ref<Record<string, string>>({})
  const selectedPreset = ref<PromptPreset | null>(null)
  const isExpanded = ref(false)

  // ── Computed ────────────────────────────────────────────────────
  const presets = computed(() => PROMPT_PRESETS)

  const renderedPrompt = computed(() => {
    let rendered = userPrompt.value
    for (const [key, value] of Object.entries(variables.value)) {
      rendered = rendered.replace(new RegExp(`\\{\\{${key}\\}\\}`, 'g'), value)
    }
    return rendered
  })

  const hasCustomizations = computed(() => {
    return Object.values(variables.value).some(v => v !== '') || !!selectedPreset.value
  })

  // ── Actions ─────────────────────────────────────────────────────

  function loadTemplate(code: string, system: string, user: string, vars: Record<string, string> = {}) {
    templateCode.value = code
    systemPrompt.value = system
    userPrompt.value = user
    variables.value = { ...vars }
  }

  function setVariable(key: string, value: string) {
    variables.value[key] = value
  }

  function applyPreset(preset: PromptPreset) {
    selectedPreset.value = preset
    variables.value['tone'] = preset.tone
    variables.value['style'] = preset.style
  }

  function clearPreset() {
    selectedPreset.value = null
    delete variables.value['tone']
    delete variables.value['style']
  }

  function toggleExpanded() {
    isExpanded.value = !isExpanded.value
  }

  function getOverridePrompt(): string | undefined {
    if (!hasCustomizations.value) return undefined
    return renderedPrompt.value
  }

  function reset() {
    templateCode.value = ''
    systemPrompt.value = ''
    userPrompt.value = ''
    variables.value = {}
    selectedPreset.value = null
    isExpanded.value = false
  }

  return {
    templateCode,
    systemPrompt,
    userPrompt,
    variables,
    selectedPreset,
    isExpanded,
    presets,
    renderedPrompt,
    hasCustomizations,
    loadTemplate,
    setVariable,
    applyPreset,
    clearPreset,
    toggleExpanded,
    getOverridePrompt,
    reset,
  }
}
