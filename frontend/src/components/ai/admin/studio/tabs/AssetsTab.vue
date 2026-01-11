<!--
  Assets Tab - Media & Asset Management (Refactored)

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
        <h2 class="text-xl font-bold text-[var(--color-text-primary)]">{{ $t('windows.aiStudioAssets.title') }}</h2>
        <p class="text-sm text-[var(--color-text-secondary)] mt-1">
          {{ $t('windows.aiStudioAssets.subtitle') }}
        </p>
      </div>
      <div class="flex gap-2">
        <button
          @click="showUploadModal = true"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-2"
        >
          <span>📤</span> {{ $t('windows.aiStudioAssets.upload') }}
        </button>
        <button
          @click="showFormulaModal = true"
          class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
        >
          <span>ƒx</span> {{ $t('windows.aiStudioAssets.formula') }}
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
          :placeholder="$t('windows.aiStudioAssets.searchPlaceholder')"
          class="w-full pl-10 pr-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)]"
        />
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]">🔍</span>
      </div>
      <select
        v-model="selectedScope"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
      >
        <option value="all">{{ $t('windows.aiStudioAssets.scope.all') }}</option>
        <option value="course">{{ $t('windows.aiStudioAssets.scope.course') }}</option>
        <option value="lesson">{{ $t('windows.aiStudioAssets.scope.lesson') }}</option>
      </select>
      <select
        v-model="sortBy"
        class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
      >
        <option value="date">{{ $t('windows.aiStudioAssets.sort.date') }}</option>
        <option value="name">{{ $t('windows.aiStudioAssets.sort.name') }}</option>
        <option value="size">{{ $t('windows.aiStudioAssets.sort.size') }}</option>
        <option value="usage">{{ $t('windows.aiStudioAssets.sort.usage') }}</option>
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
        <span class="text-sm text-[var(--color-text-secondary)]">{{ $t('windows.aiStudioAssets.dragDrop') }}</span>
        <span class="text-xs text-[var(--color-text-tertiary)]">{{ $t('windows.aiStudioAssets.orClick') }}</span>
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
            :title="$t('windows.aiStudioAssets.copy')"
          >📋</button>
          <button
            @click.stop="editAsset(asset)"
            class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors"
            :title="$t('windows.aiStudioAssets.edit')"
          >✏️</button>
          <button
            @click.stop="deleteAsset(asset)"
            class="p-2 bg-white rounded-full hover:bg-gray-100 transition-colors text-red-500"
            :title="$t('windows.aiStudioAssets.delete')"
          >🗑️</button>
        </div>

        <!-- Selection Indicator -->
        <div
          v-if="selectedAssets.includes(asset.id)"
          class="absolute top-2 right-2 w-6 h-6 bg-[var(--color-primary)] rounded-full flex items-center justify-center text-white text-sm"
        >✓</div>

        <!-- Asset Info -->
        <div class="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black/70 to-transparent">
          <p class="text-xs text-white truncate">{{ asset.name }}</p>
          <p class="text-xs text-white/70">{{ asset.size }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredAssets.length === 0" class="text-center py-12">
      <span class="text-5xl mb-4 block">📭</span>
      <h3 class="text-lg font-medium text-[var(--color-text-primary)] mb-2">{{ $t('windows.aiStudioAssets.noAssetsTitle') }}</h3>
      <p class="text-sm text-[var(--color-text-secondary)]">{{ $t('windows.aiStudioAssets.noAssetsHint') }}</p>
    </div>

    <!-- Sub-Components -->
    <AssetDetailsSidebar
      :asset="selectedAsset"
      @close="selectedAsset = null"
      @insert="insertAsset"
      @download="downloadAsset"
      @update:name="updateAssetName"
    />

    <FormulaModal
      :show="showFormulaModal"
      v-model="formulaInput"
      @close="showFormulaModal = false"
      @save="saveFormula"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { FormulaModal, AssetDetailsSidebar } from '../../settings/exams'

const { t } = useI18n()

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
const assetTabs = computed(() => [
  { id: 'all', name: t('windows.aiStudioAssets.tabs.all'), emoji: '📁' },
  { id: 'images', name: t('windows.aiStudioAssets.tabs.images'), emoji: '🖼️' },
  { id: 'formulas', name: t('windows.aiStudioAssets.tabs.formulas'), emoji: 'ƒx' },
  { id: 'diagrams', name: t('windows.aiStudioAssets.tabs.diagrams'), emoji: '📊' },
  { id: 'icons', name: t('windows.aiStudioAssets.tabs.icons'), emoji: '⭐' }
])

// Sample Assets
const assets = ref<Asset[]>([
  { id: '1', name: 'Bezugskalkulation.png', type: 'image', thumbnail: '/placeholder.jpg', size: '245 KB', createdAt: '10.12.2025', usageCount: 3 },
  { id: '2', name: 'Formel Rabatt', type: 'formula', preview: 'R = P × r%', size: '< 1 KB', createdAt: '09.12.2025', usageCount: 5 },
  { id: '3', name: 'Flussdiagramm', type: 'diagram', preview: '📊', size: '12 KB', createdAt: '08.12.2025', usageCount: 2 },
  { id: '4', name: 'Check Icon', type: 'icon', preview: '✓', size: '< 1 KB', createdAt: '07.12.2025', usageCount: 8 }
])

// Computed
const filteredAssets = computed(() => {
  let result = assets.value
  if (activeTab.value !== 'all') {
    const typeMap: Record<string, string> = { images: 'image', formulas: 'formula', diagrams: 'diagram', icons: 'icon' }
    result = result.filter(a => a.type === typeMap[activeTab.value])
  }
  if (searchQuery.value) {
    result = result.filter(a => a.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  return result
})

// Methods
function triggerUpload() { fileInput.value?.click() }

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files) handleFiles(Array.from(input.files))
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  if (event.dataTransfer?.files) handleFiles(Array.from(event.dataTransfer.files))
}

function handleFiles(files: File[]) { console.log('Uploading files:', files) }

function selectAsset(asset: Asset) { selectedAsset.value = asset }
function copyAsset(asset: Asset) { console.log('Copy asset:', asset) }
function editAsset(asset: Asset) { selectedAsset.value = asset }

function deleteAsset(asset: Asset) {
  if (confirm(t('windows.aiStudioAssets.confirmDelete', { name: asset.name }))) {
    assets.value = assets.value.filter(a => a.id !== asset.id)
    if (selectedAsset.value?.id === asset.id) selectedAsset.value = null
  }
}

function insertAsset(asset: Asset) { console.log('Insert asset:', asset) }
function downloadAsset(asset: Asset) { console.log('Download asset:', asset) }

function updateAssetName(name: string) {
  if (selectedAsset.value) selectedAsset.value.name = name
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
.assets-tab { min-height: 400px; }
</style>
