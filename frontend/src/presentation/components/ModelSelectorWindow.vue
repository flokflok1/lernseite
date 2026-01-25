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
-->

<template>
  <div class="admin-model-selector-window flex flex-col" style="height: 100%; max-height: 100%; overflow: hidden;">
    <!-- Header -->
    <div class="p-4 border-b border-[var(--color-border)]">
      <div class="flex items-center justify-between mb-3">
        <div>
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">AI Model Selector</h3>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ scopeLabel }}
          </p>
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
              🔒
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
          <div class="animate-pulse text-4xl mb-3">🤖</div>
          <p class="text-[var(--color-text-secondary)]">Lade Modelle...</p>
        </div>
      </div>

      <div v-else-if="filteredModels.length === 0" class="text-center py-12">
        <div class="text-4xl mb-3 opacity-30">🔍</div>
        <p class="text-[var(--color-text-secondary)]">Keine Modelle gefunden</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="model in filteredModels"
          :key="model.model_id"
          @click="selectModel(model)"
          :class="[
            'model-card p-4 rounded-lg border transition-all cursor-pointer',
            selectedModel?.model_id === model.model_id
              ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5'
              : 'border-[var(--color-border)] hover:border-[var(--color-primary)]/50 hover:bg-[var(--color-surface)]'
          ]"
        >
          <!-- Model Header -->
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2">
              <span class="text-xl">{{ getCategoryIcon(model.category) }}</span>
              <div>
                <h4 class="font-medium text-[var(--color-text-primary)]">{{ model.display_name }}</h4>
                <p class="text-xs text-[var(--color-text-muted)] font-mono">{{ model.model_name }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <!-- Provider Badge -->
              <span v-if="model.provider" :class="['px-2 py-0.5 rounded text-xs font-medium', getProviderBadgeClass(model.provider)]">
                {{ model.provider }}
              </span>
              <span v-if="model.is_default" class="px-2 py-0.5 rounded text-xs bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]">
                Default
              </span>
            </div>
          </div>

          <!-- Description -->
          <p v-if="model.description" class="text-sm text-[var(--color-text-secondary)] mb-3 line-clamp-2">
            {{ model.description }}
          </p>

          <!-- Badges -->
          <div class="flex flex-wrap gap-2 mb-2">
            <!-- Cost Badge -->
            <span :class="['px-2 py-0.5 rounded text-xs font-medium', getCostBadgeClass(model.cost_level)]">
              {{ getCostLabel(model.cost_level) }}
            </span>

            <!-- Speed Badge -->
            <span :class="['px-2 py-0.5 rounded text-xs font-medium', getSpeedBadgeClass(model.speed)]">
              {{ getSpeedLabel(model.speed) }}
            </span>

            <!-- Context Window -->
            <span v-if="model.context_window" class="px-2 py-0.5 rounded text-xs bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
              {{ formatContextWindow(model.context_window) }} ctx
            </span>

            <!-- Vision Support -->
            <span v-if="model.supports_vision" class="px-2 py-0.5 rounded text-xs bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#1e40af)]">
              Vision
            </span>

            <!-- Function Calling -->
            <span v-if="model.supports_functions" class="px-2 py-0.5 rounded text-xs bg-[var(--color-info-bg,#eff6ff)] text-[var(--color-info-text,#1e40af)]">
              Functions
            </span>
          </div>

          <!-- Price Display & Edit -->
          <div class="flex items-center justify-between pt-2 border-t border-[var(--color-border)]">
            <div class="flex gap-4 text-xs">
              <div>
                <span class="text-[var(--color-text-muted)]">Input:</span>
                <span class="ml-1 font-mono text-[var(--color-text-secondary)]">{{ formatPrice(model.input_price_per_1k) }}/1K</span>
              </div>
              <div>
                <span class="text-[var(--color-text-muted)]">Output:</span>
                <span class="ml-1 font-mono text-[var(--color-text-secondary)]">{{ formatPrice(model.output_price_per_1k) }}/1K</span>
              </div>
            </div>
            <button
              @click="openPriceEditor(model, $event)"
              class="px-2 py-1 text-xs bg-[var(--color-surface)] text-[var(--color-text-secondary)] rounded border border-[var(--color-border)] hover:bg-[var(--color-background)] hover:text-[var(--color-text-primary)] transition-colors"
              title="Preise bearbeiten"
            >
              Preise
            </button>
          </div>
        </div>
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
          <span class="ml-2 text-[var(--color-text-primary)]">{{ getCategoryLabel(selectedModel.category) }}</span>
        </div>
        <div>
          <span class="text-[var(--color-text-muted)]">Kosten:</span>
          <span class="ml-2 text-[var(--color-text-primary)]">{{ getCostLabel(selectedModel.cost_level) }}</span>
        </div>
        <div>
          <span class="text-[var(--color-text-muted)]">Geschwindigkeit:</span>
          <span class="ml-2 text-[var(--color-text-primary)]">{{ getSpeedLabel(selectedModel.speed) }}</span>
        </div>
        <div v-if="selectedModel.context_window">
          <span class="text-[var(--color-text-muted)]">Kontext:</span>
          <span class="ml-2 text-[var(--color-text-primary)]">{{ formatContextWindow(selectedModel.context_window) }} Tokens</span>
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
        <!-- Set as Default Button (only for global scope) -->
        <button
          v-if="selectedModel && scope === 'global'"
          @click="setAsDefault"
          :disabled="selectedModel.is_default || settingDefault"
          class="px-4 py-2 bg-[var(--color-surface)] text-[var(--color-text-primary)] rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-background)] transition-colors disabled:opacity-50"
        >
          {{ settingDefault ? 'Setze...' : (selectedModel.is_default ? 'Ist Default' : 'Als Default setzen') }}
        </button>

        <!-- Select Button -->
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
    <div
      v-if="editingModel"
      class="absolute inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="closePriceEditor"
    >
      <div class="bg-[var(--color-background)] rounded-xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        <!-- Modal Header -->
        <div class="px-6 py-4 border-b border-[var(--color-border)]">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">Preise bearbeiten</h3>
          <p class="text-sm text-[var(--color-text-secondary)] mt-1">
            {{ editingModel.display_name }}
            <span class="font-mono text-xs text-[var(--color-text-muted)]">({{ editingModel.model_name }})</span>
          </p>
        </div>

        <!-- Modal Body -->
        <div class="p-6 space-y-4">
          <div class="bg-[var(--color-surface)] rounded-lg p-4 text-sm text-[var(--color-text-secondary)]">
            <p>Preise werden pro 1.000 Tokens in USD angegeben.</p>
            <p class="mt-1 text-xs text-[var(--color-text-muted)]">Beispiel: 0.005 = $0.005 pro 1K Tokens</p>
          </div>

          <!-- Input Price -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              Input-Preis (pro 1K Tokens)
            </label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]">$</span>
              <input
                v-model.number="editPriceInput"
                type="number"
                step="0.0001"
                min="0"
                placeholder="0.0050"
                class="w-full pl-7 pr-4 py-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/50"
              />
            </div>
          </div>

          <!-- Output Price -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              Output-Preis (pro 1K Tokens)
            </label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]">$</span>
              <input
                v-model.number="editPriceOutput"
                type="number"
                step="0.0001"
                min="0"
                placeholder="0.0150"
                class="w-full pl-7 pr-4 py-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/50"
              />
            </div>
          </div>

          <!-- Quick Info -->
          <div class="grid grid-cols-2 gap-4 pt-2 text-xs text-[var(--color-text-muted)]">
            <div>
              <span class="block">Provider:</span>
              <span class="text-[var(--color-text-secondary)]">{{ editingModel.provider || '-' }}</span>
            </div>
            <div>
              <span class="block">Kategorie:</span>
              <span class="text-[var(--color-text-secondary)]">{{ getCategoryLabel(editingModel.category) }}</span>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="px-6 py-4 bg-[var(--color-surface)] border-t border-[var(--color-border)] flex justify-end gap-3">
          <button
            @click="closePriceEditor"
            class="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
          >
            Abbrechen
          </button>
          <button
            @click="savePrices"
            :disabled="savingPrice"
            class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors disabled:opacity-50"
          >
            {{ savingPrice ? 'Speichern...' : 'Speichern' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { LsxWindow } from '@/application/stores/modules/desktop'
import * as adminApi from '@/application/services/api/admin'
import type { AIModelRegistryItem, AIModelRegistryCategory, AIModelUpdateRequest, AIProviderInfo } from '@/application/services/api/admin'

// Props
interface Props {
  window: LsxWindow
}

// Emits
interface Emits {
  (e: 'close'): void
  (e: 'select', model: AIModelRegistryItem): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Price Editor State
const editingModel = ref<AIModelRegistryItem | null>(null)
const editPriceInput = ref<number | null>(null)
const editPriceOutput = ref<number | null>(null)
const savingPrice = ref(false)

// Extract payload data
const scope = computed(() => (props.window.payload?.scope as 'global' | 'course' | 'module') || 'global')
const courseId = computed(() => props.window.payload?.courseId as string | undefined)
const moduleId = computed(() => props.window.payload?.moduleId as number | undefined)
const onSelectCallback = computed(() => props.window.payload?.onSelectModel as ((modelName: string) => void) | undefined)

// Scope label for header
const scopeLabel = computed(() => {
  if (scope.value === 'course' && courseId.value) {
    return `Modell für Kurs auswählen`
  } else if (scope.value === 'module' && moduleId.value) {
    return `Modell für Modul auswählen`
  }
  return 'System-Default Modell auswählen'
})

// Select button label
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
const showConfiguredOnly = ref(true)  // Default: nur Provider mit API Key zeigen
const selectedModel = ref<AIModelRegistryItem | null>(null)
const searchQuery = ref('')

// Category tabs
const categoryTabs = computed(() => {
  const tabs = [
    { value: 'all', label: 'Alle', icon: '🤖' }
  ]

  const categoryConfig: Record<string, { label: string; icon: string }> = {
    chat: { label: 'Chat', icon: '💬' },
    reasoning: { label: 'Reasoning', icon: '🧠' },
    realtime: { label: 'Realtime', icon: '⚡' },
    audio: { label: 'Audio', icon: '🎵' },
    image: { label: 'Bild', icon: '🖼️' },
    video: { label: 'Video', icon: '🎬' },
    embedding: { label: 'Embedding', icon: '📊' },
    moderation: { label: 'Moderation', icon: '🛡️' }
  }

  for (const cat of categories.value) {
    if (categoryConfig[cat.id]) {
      tabs.push({
        value: cat.id,
        label: categoryConfig[cat.id].label,
        icon: categoryConfig[cat.id].icon
      })
    }
  }

  return tabs
})

// Provider tabs
const providerTabs = computed(() => {
  const tabs = [
    { value: 'all', label: 'Alle Provider', icon: '🌐', hasKey: true }
  ]

  const providerIcons: Record<string, string> = {
    openai: '🟢',
    anthropic: '🟠',
    google: '🔵',
    mistral: '🟣',
    cohere: '🔴',
    meta: '🔷'
  }

  // Filter providers based on showConfiguredOnly
  const filteredProviders = showConfiguredOnly.value
    ? providers.value.filter(p => p.has_api_key)
    : providers.value

  for (const provider of filteredProviders) {
    tabs.push({
      value: provider.name,
      label: provider.display_name,
      icon: providerIcons[provider.name] || '⚪',
      hasKey: provider.has_api_key
    })
  }

  return tabs
})

// Count models per provider for badges
const modelCountByProvider = computed(() => {
  const counts: Record<string, number> = { all: models.value.length }
  for (const model of models.value) {
    const prov = model.provider || 'unknown'
    counts[prov] = (counts[prov] || 0) + 1
  }
  return counts
})

// Filtered models
const filteredModels = computed(() => {
  let result = models.value

  // Filter by category
  if (selectedCategory.value !== 'all') {
    result = result.filter(m => m.category === selectedCategory.value)
  }

  // Filter by provider
  if (selectedProvider.value !== 'all') {
    result = result.filter(m => m.provider === selectedProvider.value)
  }

  // Filter by configured providers only (client-side backup for toggle)
  if (showConfiguredOnly.value) {
    const configuredProviderNames = new Set(
      providers.value.filter(p => p.has_api_key).map(p => p.name)
    )
    result = result.filter(m => configuredProviderNames.has(m.provider || ''))
  }

  // Filter by search
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
const getCategoryIcon = (category: string): string => {
  const icons: Record<string, string> = {
    chat: '💬',
    reasoning: '🧠',
    realtime: '⚡',
    audio: '🎵',
    image: '🖼️',
    video: '🎬',
    embedding: '📊',
    moderation: '🛡️'
  }
  return icons[category] || '🤖'
}

const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    chat: 'Chat',
    reasoning: 'Reasoning',
    realtime: 'Realtime',
    audio: 'Audio',
    image: 'Bild',
    video: 'Video',
    embedding: 'Embedding',
    moderation: 'Moderation'
  }
  return labels[category] || category
}

const getProviderBadgeClass = (provider: string): string => {
  const classes: Record<string, string> = {
    openai: 'bg-emerald-100 text-emerald-800',
    anthropic: 'bg-orange-100 text-orange-800',
    google: 'bg-blue-100 text-blue-800',
    mistral: 'bg-purple-100 text-purple-800',
    cohere: 'bg-red-100 text-red-800',
    meta: 'bg-indigo-100 text-indigo-800'
  }
  return classes[provider] || 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] border border-[var(--color-border)]'
}

const getCostLabel = (level: string): string => {
  const labels: Record<string, string> = {
    free: 'Kostenlos',
    low: 'Günstig',
    medium: 'Mittel',
    high: 'Teuer',
    very_high: 'Sehr teuer'
  }
  return labels[level] || level
}

const getCostBadgeClass = (level: string): string => {
  const classes: Record<string, string> = {
    free: 'bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]',
    low: 'bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]',
    medium: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
    high: 'bg-[var(--color-error,#dc2626)]/10 text-[var(--color-error,#dc2626)]',
    very_high: 'bg-[var(--color-error,#dc2626)]/20 text-[var(--color-error,#dc2626)]'
  }
  return classes[level] || 'bg-[var(--color-surface)] text-[var(--color-text-secondary)]'
}

const getSpeedLabel = (speed: string): string => {
  const labels: Record<string, string> = {
    very_fast: 'Sehr schnell',
    fast: 'Schnell',
    medium: 'Mittel',
    slow: 'Langsam'
  }
  return labels[speed] || speed
}

const getSpeedBadgeClass = (speed: string): string => {
  const classes: Record<string, string> = {
    very_fast: 'bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]',
    fast: 'bg-[var(--color-success-bg,#d1fae5)] text-[var(--color-success-text,#065f46)]',
    medium: 'bg-[var(--color-warning-bg,#fef3c7)] text-[var(--color-warning-text,#92400e)]',
    slow: 'bg-[var(--color-error,#dc2626)]/10 text-[var(--color-error,#dc2626)]'
  }
  return classes[speed] || 'bg-[var(--color-surface)] text-[var(--color-text-secondary)]'
}

const formatContextWindow = (tokens: number): string => {
  if (tokens >= 1000000) {
    return `${(tokens / 1000000).toFixed(1)}M`
  } else if (tokens >= 1000) {
    return `${Math.round(tokens / 1000)}K`
  }
  return String(tokens)
}

const selectModel = (model: AIModelRegistryItem): void => {
  selectedModel.value = model
}

const loadModels = async (): Promise<void> => {
  loading.value = true

  try {
    // Use registry endpoint for Model Selector Window
    // configured_only is handled client-side for instant filtering
    const response = await adminApi.adminGetAIModelsRegistry({
      active_only: true
    })

    models.value = response.data
    categories.value = response.categories
    providers.value = response.providers || []

    // Pre-select default chat model if available
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

const syncModels = async (): Promise<void> => {
  syncing.value = true

  try {
    const response = await adminApi.adminSyncAIModels()
    console.log('Sync result:', response.data)

    // Reload models
    await loadModels()
  } catch (err) {
    console.error('Failed to sync AI models:', err)
  } finally {
    syncing.value = false
  }
}

const setAsDefault = async (): Promise<void> => {
  if (!selectedModel.value) return

  settingDefault.value = true

  try {
    await adminApi.adminSetAIModelDefault(selectedModel.value.model_id, true)

    // Update local state
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

const confirmSelection = (): void => {
  if (!selectedModel.value) return

  // Emit through Vue emit
  emit('select', selectedModel.value)

  // Call callback if provided
  if (onSelectCallback.value) {
    onSelectCallback.value(selectedModel.value.model_name)
  }

  // Dispatch global event for cross-window communication
  const callbackId = props.window.payload?.callbackId as string | undefined
  if (callbackId) {
    window.dispatchEvent(new CustomEvent('model-selected', {
      detail: {
        callbackId,
        model: selectedModel.value
      }
    }))
  }

  emit('close')
}

// ============================================================================
// Price Editor Functions
// ============================================================================

const formatPrice = (price: number | string | null | undefined): string => {
  if (price === null || price === undefined || price === '') return '-'
  const numPrice = typeof price === 'string' ? parseFloat(price) : price
  if (isNaN(numPrice)) return '-'
  if (numPrice === 0) return 'Kostenlos'
  // Price is per 1K tokens, format as currency
  return `$${numPrice.toFixed(4)}`
}

const openPriceEditor = (model: AIModelRegistryItem, event: Event): void => {
  event.stopPropagation()
  editingModel.value = model
  editPriceInput.value = model.input_price_per_1k ?? null
  editPriceOutput.value = model.output_price_per_1k ?? null
}

const closePriceEditor = (): void => {
  editingModel.value = null
  editPriceInput.value = null
  editPriceOutput.value = null
}

const savePrices = async (): Promise<void> => {
  if (!editingModel.value) return

  savingPrice.value = true

  try {
    const updateData: AIModelUpdateRequest = {
      input_price_per_1k: editPriceInput.value,
      output_price_per_1k: editPriceOutput.value
    }

    await adminApi.adminUpdateAIModel(editingModel.value.model_id, updateData)

    // Update local model
    const modelIndex = models.value.findIndex(m => m.model_id === editingModel.value!.model_id)
    if (modelIndex >= 0) {
      models.value[modelIndex].input_price_per_1k = editPriceInput.value
      models.value[modelIndex].output_price_per_1k = editPriceOutput.value
    }

    closePriceEditor()
  } catch (err) {
    console.error('Failed to update model prices:', err)
  } finally {
    savingPrice.value = false
  }
}

// Lifecycle
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

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.model-card:hover {
  transform: translateY(-1px);
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
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
