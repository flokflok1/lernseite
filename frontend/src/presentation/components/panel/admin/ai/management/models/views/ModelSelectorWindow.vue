<!--
  Admin Model Selector Window
  Phase C3.1: AI Model Selector System

  Features:
  - Liste aller verfügbaren AI-Modelle aus Datenbank
  - Filter nach Kategorie (reasoning, chat, realtime, etc.)
  - Suchfeld
  - Badges für Cost & Speed
  - Button: Als Default setzen
  - Button: Für Kurs/Modul übernehmen
  - LSX Desktop-Fenster Integration (draggable, minimize, restore, zIndex)

  Sub-components:
  - ModelCardItem.vue - Individual model card rendering
  - ModelPriceEditor.vue - Price editing modal
  - composables/useModelFormatters.ts - Shared formatting utilities
-->

<template>
  <div class="admin-model-selector-window flex flex-col" style="height: 100%; max-height: 100%; overflow: hidden;">
    <!-- Header -->
    <div class="p-4 border-b border-[var(--color-border)]">
      <div class="flex items-center justify-between mb-3">
        <div>
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">AI Model Selector</h3>
          <p class="text-sm text-[var(--color-text-secondary)]">{{ scopeLabel }}</p>
        </div>
        <div class="flex items-center gap-2">
          <button
            @click="syncModels"
            :disabled="syncing"
            class="px-3 py-1.5 text-sm bg-[var(--color-surface)] text-[var(--color-text-secondary)] rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-background)] transition-colors disabled:opacity-50"
          >
            {{ syncing ? 'Synchronisiere...' : 'Modelle sync' }}
          </button>
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-[var(--color-primary)]/10 text-[var(--color-primary)]">
            {{ filteredModels.length }} Modelle
          </span>
        </div>
      </div>

      <!-- Search -->
      <div class="mb-3">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Modell suchen..."
          class="w-full px-3 py-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/50"
        />
      </div>

      <!-- Category Filter Tabs -->
      <div class="flex gap-2 flex-wrap">
        <button
          v-for="cat in categoryTabs"
          :key="cat.value"
          @click="selectedCategory = cat.value"
          :class="[
            'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
            selectedCategory === cat.value
              ? 'bg-[var(--color-primary)] text-white'
              : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-background)] border border-[var(--color-border)]'
          ]"
        >
          {{ cat.icon }} {{ cat.label }}
        </button>
      </div>

      <!-- Provider Filter Tabs -->
      <div class="flex items-center gap-3 mt-3">
        <div class="flex gap-2 flex-wrap flex-1">
          <button
            v-for="prov in providerTabs"
            :key="prov.value"
            @click="selectedProvider = prov.value"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-1',
              selectedProvider === prov.value
                ? 'bg-[var(--color-primary)] text-white'
                : prov.hasKey
                  ? 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-background)] border border-[var(--color-border)]'
                  : 'bg-[var(--color-surface)] text-[var(--color-text-muted)] border border-dashed border-[var(--color-border)] opacity-60'
            ]"
          >
            <span>{{ prov.icon }}</span>
            <span>{{ prov.label }}</span>
            <span v-if="prov.value !== 'all' && modelCountByProvider[prov.value]" class="ml-1 text-xs opacity-70">
              ({{ modelCountByProvider[prov.value] }})
            </span>
            <span v-if="!prov.hasKey && prov.value !== 'all'" class="ml-1 text-xs" title="Kein API Key">
              &#x1F512;
            </span>
          </button>
        </div>

        <!-- Toggle: Only configured providers -->
        <label class="flex items-center gap-2 text-sm text-[var(--color-text-secondary)] cursor-pointer whitespace-nowrap">
          <input
            v-model="showConfiguredOnly"
            type="checkbox"
            class="w-4 h-4 rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)]/50"
          />
          <span>Nur konfiguriert</span>
        </label>
      </div>
    </div>

    <!-- Model List -->
    <div class="flex-1 overflow-y-auto p-4" style="max-height: calc(100% - 200px); min-height: 200px;">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-pulse text-4xl mb-3">&#x1F916;</div>
          <p class="text-[var(--color-text-secondary)]">Lade Modelle...</p>
        </div>
      </div>

      <div v-else-if="filteredModels.length === 0" class="text-center py-12">
        <div class="text-4xl mb-3 opacity-30">&#x1F50D;</div>
        <p class="text-[var(--color-text-secondary)]">Keine Modelle gefunden</p>
      </div>

      <div v-else class="space-y-3">
        <ModelCardItem
          v-for="model in filteredModels"
          :key="model.model_id"
          :model="model"
          :is-selected="selectedModel?.model_id === model.model_id"
          @select="selectModel"
          @edit-price="openPriceEditor"
        />
      </div>
    </div>

    <!-- Selected Model Preview -->
    <div v-if="selectedModel" class="border-t border-[var(--color-border)] p-4 bg-[var(--color-surface)]">
      <div class="flex items-center justify-between mb-2">
        <h4 class="font-semibold text-[var(--color-text-primary)]">Ausgewählt: {{ selectedModel.display_name }}</h4>
        <span class="text-xs text-[var(--color-text-muted)] font-mono">{{ selectedModel.model_name }}</span>
      </div>
      <div class="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span class="text-[var(--color-text-muted)]">Kategorie:</span>
          <span class="ml-2 text-[var(--color-text-primary)]">{{ fmt.getCategoryLabel(selectedModel.category) }}</span>
        </div>
        <div>
          <span class="text-[var(--color-text-muted)]">Kosten:</span>
          <span class="ml-2 text-[var(--color-text-primary)]">{{ fmt.getCostLabel(selectedModel.cost_level) }}</span>
        </div>
        <div>
          <span class="text-[var(--color-text-muted)]">Geschwindigkeit:</span>
          <span class="ml-2 text-[var(--color-text-primary)]">{{ fmt.getSpeedLabel(selectedModel.speed) }}</span>
        </div>
        <div v-if="selectedModel.context_window">
          <span class="text-[var(--color-text-muted)]">Kontext:</span>
          <span class="ml-2 text-[var(--color-text-primary)]">{{ fmt.formatContextWindow(selectedModel.context_window) }} Tokens</span>
        </div>
      </div>
    </div>

    <!-- Footer Actions -->
    <div class="px-4 py-3 bg-[var(--color-background)] border-t border-[var(--color-border)] flex justify-between items-center">
      <button
        type="button"
        @click="$emit('close')"
        class="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
      >
        Abbrechen
      </button>

      <div class="flex gap-2">
        <button
          v-if="selectedModel && scope === 'global'"
          @click="setAsDefault"
          :disabled="selectedModel.is_default || settingDefault"
          class="px-4 py-2 bg-[var(--color-surface)] text-[var(--color-text-primary)] rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-background)] transition-colors disabled:opacity-50"
        >
          {{ settingDefault ? 'Setze...' : (selectedModel.is_default ? 'Ist Default' : 'Als Default setzen') }}
        </button>

        <button
          v-if="selectedModel"
          @click="confirmSelection"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors"
        >
          {{ selectButtonLabel }}
        </button>
      </div>
    </div>

    <!-- Price Editor Modal -->
    <ModelPriceEditor
      :model="editingModel"
      @close="editingModel = null"
      @saved="handlePriceSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import * as adminApi from '@/infrastructure/api/clients/panel/admin'
import type {
  AIModelRegistryItem,
  AIModelRegistryCategory,
  AIProviderInfo
} from '@/infrastructure/api/clients/panel/admin'
import { useModelFormatters } from './composables/useModelFormatters'
import ModelCardItem from './ModelCardItem.vue'
import ModelPriceEditor from './ModelPriceEditor.vue'

interface Props {
  window: LsxWindow
}

interface Emits {
  (e: 'close'): void
  (e: 'select', model: AIModelRegistryItem): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const fmt = useModelFormatters()

// Price Editor State
const editingModel = ref<AIModelRegistryItem | null>(null)

// Extract payload data
const scope = computed(() =>
  (props.window.payload?.scope as 'global' | 'course' | 'module') || 'global'
)
const courseId = computed(() => props.window.payload?.courseId as string | undefined)
const moduleId = computed(() => props.window.payload?.moduleId as number | undefined)
const onSelectCallback = computed(() =>
  props.window.payload?.onSelectModel as ((modelName: string) => void) | undefined
)

const scopeLabel = computed(() => {
  if (scope.value === 'course' && courseId.value) return 'Modell für Kurs auswählen'
  if (scope.value === 'module' && moduleId.value) return 'Modell für Modul auswählen'
  return 'System-Default Modell auswählen'
})

const selectButtonLabel = computed(() => {
  if (scope.value === 'course') return 'Für Kurs übernehmen'
  if (scope.value === 'module') return 'Für Modul übernehmen'
  return 'Modell auswählen'
})

// State
const loading = ref(true)
const syncing = ref(false)
const settingDefault = ref(false)
const models = ref<AIModelRegistryItem[]>([])
const categories = ref<AIModelRegistryCategory[]>([])
const providers = ref<AIProviderInfo[]>([])
const selectedCategory = ref<string>('all')
const selectedProvider = ref<string>('all')
const showConfiguredOnly = ref(true)
const selectedModel = ref<AIModelRegistryItem | null>(null)
const searchQuery = ref('')

// Category tabs
const categoryTabs = computed(() => {
  const categoryConfig: Record<string, { label: string; icon: string }> = {
    chat: { label: 'Chat', icon: '\uD83D\uDCAC' },
    reasoning: { label: 'Reasoning', icon: '\uD83E\uDDE0' },
    realtime: { label: 'Realtime', icon: '\u26A1' },
    audio: { label: 'Audio', icon: '\uD83C\uDFB5' },
    image: { label: 'Bild', icon: '\uD83D\uDDBC\uFE0F' },
    video: { label: 'Video', icon: '\uD83C\uDFAC' },
    embedding: { label: 'Embedding', icon: '\uD83D\uDCCA' },
    moderation: { label: 'Moderation', icon: '\uD83D\uDEE1\uFE0F' }
  }

  const tabs = [{ value: 'all', label: 'Alle', icon: '\uD83E\uDD16' }]
  for (const cat of categories.value) {
    if (categoryConfig[cat.id]) {
      tabs.push({ value: cat.id, ...categoryConfig[cat.id] })
    }
  }
  return tabs
})

// Provider tabs
const providerTabs = computed(() => {
  const tabs = [{ value: 'all', label: 'Alle Provider', icon: '\uD83C\uDF10', hasKey: true }]
  const filteredProviders = showConfiguredOnly.value
    ? providers.value.filter(p => p.has_api_key)
    : providers.value

  for (const provider of filteredProviders) {
    tabs.push({
      value: provider.name,
      label: provider.display_name,
      icon: fmt.getProviderIcon(provider.name),
      hasKey: provider.has_api_key
    })
  }
  return tabs
})

const modelCountByProvider = computed(() => {
  const counts: Record<string, number> = { all: models.value.length }
  for (const model of models.value) {
    const prov = model.provider || 'unknown'
    counts[prov] = (counts[prov] || 0) + 1
  }
  return counts
})

const filteredModels = computed(() => {
  let result = models.value

  if (selectedCategory.value !== 'all') {
    result = result.filter(m => m.category === selectedCategory.value)
  }

  if (selectedProvider.value !== 'all') {
    result = result.filter(m => m.provider === selectedProvider.value)
  }

  if (showConfiguredOnly.value) {
    const configuredProviderNames = new Set(
      providers.value.filter(p => p.has_api_key).map(p => p.name)
    )
    result = result.filter(m => configuredProviderNames.has(m.provider || ''))
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(m =>
      m.model_name.toLowerCase().includes(query) ||
      m.display_name.toLowerCase().includes(query) ||
      (m.description?.toLowerCase().includes(query)) ||
      (m.provider?.toLowerCase().includes(query))
    )
  }

  return result
})

// Methods
function selectModel(model: AIModelRegistryItem): void {
  selectedModel.value = model
}

function openPriceEditor(model: AIModelRegistryItem): void {
  editingModel.value = model
}

function handlePriceSaved(
  modelId: string,
  inputPrice: number | null,
  outputPrice: number | null
): void {
  const modelIndex = models.value.findIndex(m => m.model_id === modelId)
  if (modelIndex >= 0) {
    models.value[modelIndex].input_price_per_1k = inputPrice
    models.value[modelIndex].output_price_per_1k = outputPrice
  }
}

async function loadModels(): Promise<void> {
  loading.value = true
  try {
    const response = await adminApi.adminGetAIModelsRegistry({ active_only: true })
    models.value = response.data
    categories.value = response.categories
    providers.value = response.providers || []

    const defaultChat = models.value.find(m => m.category === 'chat' && m.is_default)
    if (defaultChat) {
      selectedModel.value = defaultChat
    }
  } catch (err) {
    console.error('Failed to load AI models:', err)
  } finally {
    loading.value = false
  }
}

async function syncModels(): Promise<void> {
  syncing.value = true
  try {
    await adminApi.adminSyncAIModels()
    await loadModels()
  } catch (err) {
    console.error('Failed to sync AI models:', err)
  } finally {
    syncing.value = false
  }
}

async function setAsDefault(): Promise<void> {
  if (!selectedModel.value) return
  settingDefault.value = true
  try {
    await adminApi.adminSetAIModelDefault(selectedModel.value.model_id, true)
    models.value.forEach(m => {
      if (m.category === selectedModel.value!.category) {
        m.is_default = m.model_id === selectedModel.value!.model_id
      }
    })
  } catch (err) {
    console.error('Failed to set default model:', err)
  } finally {
    settingDefault.value = false
  }
}

function confirmSelection(): void {
  if (!selectedModel.value) return

  emit('select', selectedModel.value)

  if (onSelectCallback.value) {
    onSelectCallback.value(selectedModel.value.model_name)
  }

  const callbackId = props.window.payload?.callbackId as string | undefined
  if (callbackId) {
    window.dispatchEvent(new CustomEvent('model-selected', {
      detail: { callbackId, model: selectedModel.value }
    }))
  }

  emit('close')
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.admin-model-selector-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100%;
  overflow: hidden;
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Scrollbar Styling */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}
.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}
.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}
</style>
