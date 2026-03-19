<!--
  Task-specific AI model defaults: each AI task category can have its own model.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
    <div class="px-4 py-3">
      <div class="flex items-center gap-2 mb-3">
        <h3 class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ $t('panel.aiSettingsPage.taskDefaults.title') }}
        </h3>
        <span class="text-xs text-[var(--color-text-secondary)]">
          {{ $t('panel.aiSettingsPage.taskDefaults.subtitle') }}
        </span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center gap-2 py-2">
        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-[var(--color-primary)]"></div>
        <span class="text-xs text-[var(--color-text-secondary)]">{{ $t('panel.aiSettingsPage.loadingProviders') }}</span>
      </div>

      <!-- Task rows -->
      <div v-else class="space-y-2">
        <div
          v-for="task in taskDefaults"
          :key="task.category"
          class="flex items-center gap-3 py-1.5 px-2 rounded-md hover:bg-[var(--color-bg)] transition-colors"
        >
          <!-- Category label -->
          <div class="w-32 shrink-0">
            <div class="text-sm font-medium text-[var(--color-text-primary)]">
              {{ task.display_name || task.category }}
            </div>
            <div class="text-[10px] text-[var(--color-text-secondary)] truncate">
              {{ task.description }}
            </div>
          </div>

          <!-- Provider -->
          <select
            :value="editState[task.category]?.provider || task.provider_name"
            class="w-36 px-2 py-1 text-xs border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
            @change="onProviderChange(task.category, ($event.target as HTMLSelectElement).value)"
          >
            <option
              v-for="(providerData, providerName) in availableModels"
              :key="providerName"
              :value="providerName"
            >
              {{ providerData.display_name }}
            </option>
          </select>

          <!-- Model -->
          <select
            :value="editState[task.category]?.model || task.model_name"
            class="flex-1 px-2 py-1 text-xs border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
            @change="onModelChange(task.category, ($event.target as HTMLSelectElement).value)"
          >
            <option
              v-for="model in getModelsForProvider(editState[task.category]?.provider || task.provider_name)"
              :key="model.name"
              :value="model.name"
            >
              {{ model.name }}
            </option>
          </select>

          <!-- Save button -->
          <button
            :disabled="savingCategory === task.category || !hasChanges(task)"
            class="shrink-0 px-3 py-1 text-xs bg-[var(--color-primary)] text-white rounded hover:opacity-90 disabled:opacity-30 disabled:cursor-not-allowed transition-opacity"
            @click="saveTaskDefault(task.category)"
          >
            {{ savingCategory === task.category
              ? $t('panel.aiSettingsPage.defaultModel.savingSettings')
              : $t('panel.aiSettingsPage.defaultModel.saveSettings') }}
          </button>

          <!-- Result indicator -->
          <span
            v-if="saveResults[task.category]"
            :class="[
              'text-[10px] shrink-0',
              saveResults[task.category]?.success
                ? 'text-green-600 dark:text-green-400'
                : 'text-red-600 dark:text-red-400'
            ]"
          >
            {{ saveResults[task.category]?.success ? '\u2713' : '\u2717' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import type { ProviderModels } from '../types'

interface TaskDefault {
  category: string
  provider_name: string
  model_name: string
  display_name: string
  description: string
}

interface Props {
  availableModels: Record<string, ProviderModels>
}

const props = defineProps<Props>()
const { t } = useI18n()

const taskDefaults = ref<TaskDefault[]>([])
const loading = ref(true)
const savingCategory = ref<string | null>(null)
const saveResults = reactive<Record<string, { success: boolean } | null>>({})
const editState = reactive<Record<string, { provider: string; model: string }>>({})

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('access_token')
  return { Authorization: `Bearer ${token}` }
}

function getModelsForProvider(providerName: string) {
  return props.availableModels[providerName]?.models || []
}

function onProviderChange(category: string, provider: string): void {
  const task = taskDefaults.value.find(t => t.category === category)
  if (!editState[category]) {
    editState[category] = {
      provider,
      model: task?.model_name || '',
    }
  } else {
    editState[category].provider = provider
  }
  // Auto-select first model for new provider
  const models = getModelsForProvider(provider)
  if (models.length > 0) {
    editState[category].model = models[0].name
  }
}

function onModelChange(category: string, model: string): void {
  const task = taskDefaults.value.find(t => t.category === category)
  if (!editState[category]) {
    editState[category] = {
      provider: task?.provider_name || '',
      model,
    }
  } else {
    editState[category].model = model
  }
}

function hasChanges(task: TaskDefault): boolean {
  const edit = editState[task.category]
  if (!edit) return false
  return edit.provider !== task.provider_name || edit.model !== task.model_name
}

async function loadTaskDefaults(): Promise<void> {
  loading.value = true
  try {
    const response = await axios.get(
      '/api/v1/panel/settings/ai/models/task-defaults',
      { headers: getAuthHeaders() },
    )
    if (response.data.success) {
      taskDefaults.value = response.data.data || []
    }
  } catch (err) {
    console.error('Error loading task defaults:', err)
  } finally {
    loading.value = false
  }
}

async function saveTaskDefault(category: string): Promise<void> {
  const edit = editState[category]
  if (!edit) return

  savingCategory.value = category
  saveResults[category] = null

  try {
    const response = await axios.put(
      `/api/v1/panel/settings/ai/models/task-defaults/${category}`,
      { provider: edit.provider, model: edit.model },
      { headers: getAuthHeaders() },
    )

    if (response.data.success) {
      saveResults[category] = { success: true }
      // Update local state to reflect saved values
      const task = taskDefaults.value.find(t => t.category === category)
      if (task) {
        task.provider_name = edit.provider
        task.model_name = edit.model
      }
      // Clear edit state
      delete editState[category]
      // Auto-clear success after 3 seconds
      setTimeout(() => { saveResults[category] = null }, 3000)
    } else {
      saveResults[category] = { success: false }
    }
  } catch (err) {
    console.error('Error saving task default:', err)
    saveResults[category] = { success: false }
  } finally {
    savingCategory.value = null
  }
}

onMounted(() => {
  loadTaskDefaults()
})
</script>
