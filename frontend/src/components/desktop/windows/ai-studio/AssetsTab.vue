<!--
  Assets Tab - Media & Asset Management

  Features:
  - Bilder hochladen und verwalten
  - Formeln erstellen (LaTeX)
  - Diagramme erstellen
  - Icons und Grafiken
  - Asset-Galerie pro Kurs/Lektion
-->

<template>
  <div class="assets-tab p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">Asset-Manager</h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          Bilder, Formeln und Grafiken für deine Lektionen
        </p>
      </div>
      <div class="flex gap-2">
        <button
          @click="showUploadModal = true"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-2"
        >
          <span>📤</span> Upload
        </button>
        <button
          @click="showFormulaModal = true"
          class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
        >
          <span>ƒx</span> Formel
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 mb-6 p-1 bg-[var(--color-surface)] rounded-lg w-fit">
      <button
        v-for="tab in assetTabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
        :class="activeTab === tab.id
          ? 'bg-white dark:bg-gray-700 text-[var(--color-text-primary)] shadow-sm'
          : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'"
      >
        {{ tab.emoji }} {{ tab.name }}
      </button>
    </div>

    <!-- Filter Bar -->
    <div class="flex items-center gap-4 mb-6">
      <div class="flex-1 relative">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Assets durchsuchen..."
          class="w-full pl-10 pr-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)]"
        />
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]">🔍</span>
      </div>
      <select
        v-model="selectedScope"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
      >
        <option value="all">Alle Assets</option>
        <option value="course">Nur dieser Kurs</option>
        <option value="lesson">Nur diese Lektion</option>
      </select>
      <select
        v-model="sortBy"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
      >
        <option value="date">Neueste zuerst</option>
        <option value="name">Name (A-Z)</option>
        <option value="size">Größe</option>
        <option value="usage">Nutzung</option>
      </select>
    </div>

    <!-- Asset Grid -->
    <div class="grid grid-cols-4 gap-4">
      <!-- Upload Drop Zone -->
      <div
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="handleDrop"
        class="aspect-square border-2 border-dashed rounded-xl flex flex-col items-center justify-center cursor-pointer transition-all"
        :class="isDragging
          ? 'border-[var(--color-primary)] bg-[var(--color-primary-subtle)]'
          : 'border-[var(--color-border)] hover:border-[var(--color-primary)]'"
        @click="triggerUpload"
      >
        <span class="text-3xl mb-2">📤</span>
        <span class="text-sm text-[var(--color-text-secondary)]">Drag & Drop</span>
        <span class="text-xs text-[var(--color-text-tertiary)]">oder klicken</span>
        <input
          ref="fileInput"
          type="file"
          multiple
          accept="image/*"
          class="hidden"
          @change="handleFileSelect"
        />
      </div>

      <!-- Asset Items -->
      <div
        v-for="asset in filteredAssets"
        :key="asset.id"
        class="relative group aspect-square bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] overflow-hidden cursor-pointer hover:border-[var(--color-primary)] transition-all"
        @click="selectAsset(asset)"
      >
        <!-- Image Preview -->
        <img
          v-if="asset.type === 'image'"
          :src="asset.thumbnail"
          :alt="asset.name"
          class="w-full h-full object-cover"
        />

        <!-- Formula Preview -->
        <div
          v-else-if="asset.type === 'formula'"
          class="w-full h-full flex items-center justify-center bg-white dark:bg-gray-800 p-4"
        >
          <span class="text-2xl text-[var(--color-text-primary)]">{{ asset.preview }}</span>
        </div>

        <!-- Diagram Preview -->
        <div
          v-else-if="asset.type === 'diagram'"
          class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20"
        >
          <span class="text-4xl">📊</span>
        </div>

        <!-- Icon Preview -->
        <div
          v-else-if="asset.type === 'icon'"
          class="w-full h-full flex items-center justify-center"
        >
          <span class="text-4xl">{{ asset.preview }}</span>
        </div>

        <!-- Hover Overlay -->
        <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            @click.stop="copyAsset(asset)"
            class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
            title="Kopieren"
          >
            📋
          </button>
          <button
            @click.stop="editAsset(asset)"
            class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
            title="Bearbeiten"
          >
            ✏️
          </button>
          <button
            @click.stop="deleteAsset(asset)"
            class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors text-red-500"
            title="Löschen"
          >
            🗑️
          </button>
        </div>

        <!-- Selection Indicator -->
        <div
          v-if="selectedAssets.includes(asset.id)"
          class="absolute top-2 right-2 w-6 h-6 bg-[var(--color-primary)] rounded-full flex items-center justify-center text-white text-sm"
        >
          ✓
        </div>

        <!-- Asset Info -->
        <div class="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/70 to-transparent">
          <p class="text-xs text-white truncate">{{ asset.name }}</p>
          <p class="text-xs text-white/70">{{ asset.size }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-if="filteredAssets.length === 0"
      class="text-center py-12"
    >
      <span class="text-5xl mb-4 block">📭</span>
      <h3 class="text-lg font-medium text-[var(--color-text-primary)] mb-2">Keine Assets gefunden</h3>
      <p class="text-sm text-[var(--color-text-secondary)]">
        Lade Bilder hoch oder erstelle Formeln und Diagramme.
      </p>
    </div>

    <!-- Asset Details Sidebar -->
    <div
      v-if="selectedAsset"
      class="fixed top-0 right-0 w-80 h-full bg-[var(--color-surface)] border-l border-[var(--color-border)] p-4 shadow-xl z-50"
    >
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold text-[var(--color-text-primary)]">Asset Details</h3>
        <button
          @click="selectedAsset = null"
          class="p-1 hover:bg-[var(--color-surface-secondary)] rounded"
        >
          ✕
        </button>
      </div>

      <!-- Preview -->
      <div class="aspect-video bg-[var(--color-surface-secondary)] rounded-lg mb-4 flex items-center justify-center overflow-hidden">
        <img
          v-if="selectedAsset.type === 'image'"
          :src="selectedAsset.thumbnail"
          :alt="selectedAsset.name"
          class="max-w-full max-h-full object-contain"
        />
        <span v-else class="text-4xl">{{ selectedAsset.preview }}</span>
      </div>

      <!-- Info -->
      <div class="space-y-3 text-sm">
        <div>
          <label class="text-[var(--color-text-tertiary)]">Name</label>
          <input
            v-model="selectedAsset.name"
            type="text"
            class="w-full mt-1 px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
          />
        </div>
        <div>
          <label class="text-[var(--color-text-tertiary)]">Typ</label>
          <p class="text-[var(--color-text-primary)]">{{ selectedAsset.type }}</p>
        </div>
        <div>
          <label class="text-[var(--color-text-tertiary)]">Größe</label>
          <p class="text-[var(--color-text-primary)]">{{ selectedAsset.size }}</p>
        </div>
        <div>
          <label class="text-[var(--color-text-tertiary)]">Erstellt</label>
          <p class="text-[var(--color-text-primary)]">{{ selectedAsset.createdAt }}</p>
        </div>
        <div>
          <label class="text-[var(--color-text-tertiary)]">Verwendet in</label>
          <p class="text-[var(--color-text-primary)]">{{ selectedAsset.usageCount }} Lektionen</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-6 space-y-2">
        <button
          @click="insertAsset(selectedAsset)"
          class="w-full py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors"
        >
          In Lektion einfügen
        </button>
        <button
          @click="downloadAsset(selectedAsset)"
          class="w-full py-2 bg-[var(--color-surface-secondary)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface)] transition-colors"
        >
          Herunterladen
        </button>
      </div>
    </div>

    <!-- Formula Modal -->
    <div
      v-if="showFormulaModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showFormulaModal = false"
    >
      <div class="bg-[var(--color-surface)] rounded-xl p-6 w-[600px] max-h-[80vh] overflow-y-auto">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Formel erstellen</h3>

        <div class="space-y-4">
          <!-- LaTeX Input -->
          <div>
            <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">LaTeX-Code</label>
            <textarea
              v-model="formulaInput"
              class="w-full h-32 px-3 py-2 bg-[var(--color-surface-secondary)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] font-mono resize-none"
              placeholder="z.B. \frac{a}{b} + \sqrt{c}"
            ></textarea>
          </div>

          <!-- Preview -->
          <div>
            <label class="text-sm text-[var(--color-text-secondary)] mb-1 block">Vorschau</label>
            <div class="h-24 bg-white dark:bg-gray-800 border border-[var(--color-border)] rounded-lg flex items-center justify-center">
              <span class="text-2xl">{{ formulaPreview }}</span>
            </div>
          </div>

          <!-- Common Formulas -->
          <div>
            <label class="text-sm text-[var(--color-text-secondary)] mb-2 block">Häufige Formeln</label>
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="formula in commonFormulas"
                :key="formula.latex"
                @click="formulaInput = formula.latex"
                class="p-2 bg-[var(--color-surface-secondary)] rounded-lg hover:bg-[var(--color-primary-subtle)] transition-colors text-center"
                :title="formula.name"
              >
                {{ formula.preview }}
              </button>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-6">
          <button
            @click="showFormulaModal = false"
            class="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          >
            Abbrechen
          </button>
          <button
            @click="saveFormula"
            class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)]"
          >
            Speichern
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Asset {
  id: string
  name: string
  type: 'image' | 'formula' | 'diagram' | 'icon'
  thumbnail?: string
  preview?: string
  size: string
  createdAt: string
  usageCount: number
}

interface Props {
  courseId?: string
  lessonId?: string
}

defineProps<Props>()

// State
const activeTab = ref('all')
const searchQuery = ref('')
const selectedScope = ref('all')
const sortBy = ref('date')
const isDragging = ref(false)
const selectedAssets = ref<string[]>([])
const selectedAsset = ref<Asset | null>(null)
const showUploadModal = ref(false)
const showFormulaModal = ref(false)
const formulaInput = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

// Asset Tabs
const assetTabs = [
  { id: 'all', name: 'Alle', emoji: '📁' },
  { id: 'images', name: 'Bilder', emoji: '🖼️' },
  { id: 'formulas', name: 'Formeln', emoji: 'ƒx' },
  { id: 'diagrams', name: 'Diagramme', emoji: '📊' },
  { id: 'icons', name: 'Icons', emoji: '⭐' }
]

// Sample Assets
const assets = ref<Asset[]>([
  { id: '1', name: 'Bezugskalkulation.png', type: 'image', thumbnail: '/placeholder.jpg', size: '245 KB', createdAt: '10.12.2025', usageCount: 3 },
  { id: '2', name: 'Formel Rabatt', type: 'formula', preview: 'R = P × r%', size: '< 1 KB', createdAt: '09.12.2025', usageCount: 5 },
  { id: '3', name: 'Flussdiagramm', type: 'diagram', preview: '📊', size: '12 KB', createdAt: '08.12.2025', usageCount: 2 },
  { id: '4', name: 'Check Icon', type: 'icon', preview: '✓', size: '< 1 KB', createdAt: '07.12.2025', usageCount: 8 }
])

// Common Formulas
const commonFormulas = [
  { name: 'Bruch', latex: '\\frac{a}{b}', preview: 'a/b' },
  { name: 'Wurzel', latex: '\\sqrt{x}', preview: '√x' },
  { name: 'Potenz', latex: 'x^{n}', preview: 'xⁿ' },
  { name: 'Summe', latex: '\\sum_{i=1}^{n}', preview: 'Σ' },
  { name: 'Prozent', latex: 'P \\times r\\%', preview: 'P×r%' },
  { name: 'Gleichung', latex: 'a + b = c', preview: 'a+b=c' },
  { name: 'Multiplikation', latex: 'a \\times b', preview: 'a×b' },
  { name: 'Division', latex: 'a \\div b', preview: 'a÷b' }
]

// Computed
const filteredAssets = computed(() => {
  let result = assets.value

  // Filter by tab
  if (activeTab.value !== 'all') {
    const typeMap: Record<string, string> = {
      images: 'image',
      formulas: 'formula',
      diagrams: 'diagram',
      icons: 'icon'
    }
    result = result.filter(a => a.type === typeMap[activeTab.value])
  }

  // Filter by search
  if (searchQuery.value) {
    result = result.filter(a =>
      a.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  return result
})

const formulaPreview = computed(() => {
  // Simple preview (real implementation would use KaTeX/MathJax)
  return formulaInput.value || '...'
})

// Methods
function triggerUpload() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files) {
    handleFiles(Array.from(input.files))
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  if (event.dataTransfer?.files) {
    handleFiles(Array.from(event.dataTransfer.files))
  }
}

function handleFiles(files: File[]) {
  // TODO: Upload files
  console.log('Uploading files:', files)
}

function selectAsset(asset: Asset) {
  selectedAsset.value = asset
}

function copyAsset(asset: Asset) {
  // TODO: Copy asset reference to clipboard
  console.log('Copy asset:', asset)
}

function editAsset(asset: Asset) {
  selectedAsset.value = asset
}

function deleteAsset(asset: Asset) {
  if (confirm(`Asset "${asset.name}" wirklich löschen?`)) {
    assets.value = assets.value.filter(a => a.id !== asset.id)
    if (selectedAsset.value?.id === asset.id) {
      selectedAsset.value = null
    }
  }
}

function insertAsset(asset: Asset) {
  // TODO: Insert asset into current lesson
  console.log('Insert asset:', asset)
}

function downloadAsset(asset: Asset) {
  // TODO: Download asset
  console.log('Download asset:', asset)
}

function saveFormula() {
  if (!formulaInput.value) return

  assets.value.unshift({
    id: Date.now().toString(),
    name: `Formel ${assets.value.filter(a => a.type === 'formula').length + 1}`,
    type: 'formula',
    preview: formulaInput.value,
    size: '< 1 KB',
    createdAt: new Date().toLocaleDateString('de-DE'),
    usageCount: 0
  })

  showFormulaModal.value = false
  formulaInput.value = ''
}
</script>

<style scoped>
.assets-tab {
  min-height: 400px;
}
</style>
