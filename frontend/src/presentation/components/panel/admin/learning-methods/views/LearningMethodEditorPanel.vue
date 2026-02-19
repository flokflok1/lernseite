<!--
  Admin Learning Method Editor Panel - Phase D3.4

  Editor for Learning Method Instances (31 Methoden, LM00-LM32 ohne LM05/LM07).
  Manages learning methods attached to a specific module.

  Features:
  - List all learning methods for a module
  - Create/Edit/Delete learning method instances
  - Select from 31 method types (6 groups A-F)
  - Auto-save (debounced)
  - Drag & drop reordering

  Sub-components:
  - InstancesTab: Method instances list with drag & drop
  - CatalogTab: Method type catalog grouped by A-F
  - StatsTab: Statistics overview
  - MethodTypeSelectorModal: Modal for selecting method type to create
  - LearningMethodEditModal: Modal for editing a method instance
-->

<template>
  <div class="admin-learning-method-editor h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header with Chapter Context -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-4 py-3">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-[var(--color-text-secondary)]">
            Kurs: <span class="font-medium text-[var(--color-text-primary)]">{{ courseTitle }}</span>
          </p>
          <p class="text-xs text-[var(--color-text-tertiary)]">
            Kapitel: {{ chapterTitle }}
          </p>
        </div>
        <!-- Save Status Indicator -->
        <div class="flex items-center gap-2 text-xs">
          <span v-if="saveStatus === 'saving'" class="flex items-center gap-1" style="color: var(--color-info, #2563eb);">
            <svg class="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Speichern...
          </span>
          <span v-else-if="saveStatus === 'saved'" class="flex items-center gap-1" style="color: var(--color-success, #16a34a);">
            <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            Gespeichert
          </span>
          <span v-else-if="saveStatus === 'error'" style="color: var(--color-error, #dc2626);">
            Fehler beim Speichern
          </span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[var(--color-primary)] mx-auto mb-3"></div>
        <p class="text-sm text-[var(--color-text-secondary)]">Lade Lernmethoden...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 p-6">
      <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fee2e2); border-color: var(--color-error-border, #fecaca);">
        <p style="color: var(--color-error-text, #b91c1c);">{{ error }}</p>
        <button
          @click="loadLearningMethods"
          class="mt-3 px-3 py-1.5 text-white text-sm rounded"
          style="background-color: var(--color-error, #dc2626);"
        >
          Erneut versuchen
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="flex-1 flex flex-col overflow-hidden min-h-0">
      <!-- Tabs -->
      <div class="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div class="flex px-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              'px-4 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
                : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            ]"
          >
            <span class="mr-2">{{ tab.icon }}</span>
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-hidden min-h-0 relative">
        <InstancesTab
          v-if="activeTab === 'instances'"
          :methods="methods"
          :sorted-methods="sortedMethods"
          :drag-state="dragState"
          :get-group-style="getGroupStyle"
          :get-method-group="getMethodGroup"
          :get-group-position-by-id="getGroupPositionById"
          :get-method-type-name="getMethodTypeName"
          :get-tier-style="getTierStyle"
          :get-tier-label="getTierLabel"
          :handle-drag-start="handleDragStart"
          :handle-drag-over="handleDragOver"
          :handle-drop="handleDrop"
          :handle-drag-end="handleDragEnd"
          :toggle-publish="togglePublish"
          :delete-method="deleteMethod"
          @open-selector="showMethodTypeSelector = true"
          @edit="editMethod"
        />

        <CatalogTab
          v-else-if="activeTab === 'catalog'"
          :catalog-active-group="catalogActiveGroup"
          :method-groups="methodGroups"
          :get-methods-by-group="getMethodsByGroup"
          :get-group-style="getGroupStyle"
          :get-group-style-filled="getGroupStyleFilled"
          :get-group-position="getGroupPosition"
          :get-tier-style="getTierStyle"
          :get-tier-label="getTierLabel"
          :get-tier-from-group="getTierFromGroup"
          @update:catalog-active-group="catalogActiveGroup = $event"
          @create-method="createMethodFromType"
        />

        <StatsTab
          v-else-if="activeTab === 'stats'"
          :stats="stats"
        />
      </div>
    </div>

    <!-- Method Type Selector Modal -->
    <MethodTypeSelectorModal
      v-if="showMethodTypeSelector"
      :method-types="methodTypes"
      :method-groups="methodGroups"
      :initial-group="selectorGroup"
      :get-group-style="getGroupStyle"
      :get-group-position="getGroupPosition"
      :get-tier-style="getTierStyle"
      :get-tier-label="getTierLabel"
      :get-tier-from-group="getTierFromGroup"
      @close="showMethodTypeSelector = false"
      @select="createMethodFromType"
    />

    <!-- Edit Method Modal -->
    <LearningMethodEditModal
      v-if="editingMethod"
      :editing-method="editingMethod"
      :edit-form="editForm"
      :get-group-style="getGroupStyle"
      :get-method-group="getMethodGroup"
      :get-group-position-by-id="getGroupPositionById"
      :get-method-type-name="getMethodTypeName"
      @close="editingMethod = null"
      @save="saveEditedMethod"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGroupTier } from '@/application/composables/learning/useGroupTier'
import type { LsxPanel } from '@/application/stores/modules/workspace'
import type { LearningMethodGroup } from '@/infrastructure/api/clients/panel/admin'
import { useLearningMethodsPanel } from './learning-method-editor-panel/composables/useLearningMethodsPanel'
import { InstancesTab, CatalogTab, StatsTab } from './learning-method-editor-panel/tabs'
import MethodTypeSelectorModal from './learning-method-editor-panel/MethodTypeSelectorModal.vue'
import LearningMethodEditModal from './learning-method-editor-panel/LearningMethodEditModal.vue'

interface Props {
  panel: LsxPanel
}

interface Emits {
  (e: 'close'): void
}

const props = defineProps<Props>()
defineEmits<Emits>()

const { t } = useI18n()
const groupTier = useGroupTier()

const {
  // State
  methods,
  methodTypes,
  loading,
  error,
  saveStatus,
  activeTab,
  showMethodTypeSelector,
  selectorGroup,
  catalogActiveGroup,
  editingMethod,
  editForm,
  stats,
  dragState,
  // Computed
  chapterTitle,
  courseTitle,
  sortedMethods,
  methodGroups,
  // Methods
  loadLearningMethods,
  getMethodTypeName,
  getGroupPosition,
  getGroupPositionById,
  getMethodGroup,
  getGroupStyle,
  getGroupStyleFilled,
  getTierStyle,
  getTierLabel,
  getTierFromGroup,
  getMethodsByGroup,
  createMethodFromType,
  editMethod,
  saveEditedMethod,
  togglePublish,
  deleteMethod,
  handleDragStart,
  handleDragOver,
  handleDrop,
  handleDragEnd
} = useLearningMethodsPanel(props)

const tabs = computed(() => [
  { id: 'instances' as const, label: t('panel.learningMethods.tabs.instances'), icon: '\uD83C\uDFAF' },
  { id: 'catalog' as const, label: t('panel.learningMethods.tabs.catalog'), icon: '\uD83D\uDCD6' },
  { id: 'stats' as const, label: t('panel.learningMethods.tabs.stats'), icon: '\uD83D\uDCCA' }
])

function handleLearningMethodUpdate(): void {
  loadLearningMethods()
}

onMounted(() => {
  groupTier.loadGroups()
  loadLearningMethods()

  const preSelectedGroup = props.panel.payload?.preSelectedGroup as LearningMethodGroup | undefined
  if (preSelectedGroup && ['A', 'B', 'C', 'D', 'E', 'F'].includes(preSelectedGroup)) {
    selectorGroup.value = preSelectedGroup
    catalogActiveGroup.value = preSelectedGroup
    activeTab.value = 'catalog'
  }

  window.addEventListener('learning-method-updated', handleLearningMethodUpdate)
})

onUnmounted(() => {
  window.removeEventListener('learning-method-updated', handleLearningMethodUpdate)
})
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
