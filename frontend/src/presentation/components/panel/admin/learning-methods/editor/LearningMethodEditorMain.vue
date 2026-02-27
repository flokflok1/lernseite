<template>
  <div class="h-full flex flex-col bg-[var(--color-background)]">
    <!-- Header -->
    <div class="flex-shrink-0 border-b border-[var(--color-border)] bg-[var(--color-surface)] p-4">
      <div class="flex items-center justify-between mb-2">
        <div>
          <h2 class="text-xl font-bold text-[var(--color-text-primary)]">
            {{ courseTitle }}
          </h2>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ chapterTitle }}
          </p>
        </div>
        <div class="flex items-center gap-2">
          <!-- Save Status Indicator -->
          <div
            v-if="saveStatus !== 'idle'"
            :class="[
              'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
              saveStatus === 'saving'
                ? 'bg-[var(--color-info-bg)] text-[var(--color-info-text)]'
                : saveStatus === 'saved'
                  ? 'bg-[var(--color-success-bg)] text-[var(--color-success-text)]'
                  : 'bg-[var(--color-error-bg)] text-[var(--color-error-text)]'
            ]"
          >
            {{
              saveStatus === 'saving'
                ? $t('learningMethodEditor.saving')
                : saveStatus === 'saved'
                  ? $t('learningMethodEditor.saved')
                  : $t('learningMethodEditor.error')
            }}
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center">
      <div class="text-center">
        <div class="animate-spin inline-block">
          <svg class="w-12 h-12 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke-width="2" stroke-opacity="0.25" />
            <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <p class="mt-4 text-[var(--color-text-secondary)]">
          {{ $t('learningMethodEditor.loading') }}
        </p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center p-4">
      <div class="text-center max-w-md">
        <div class="text-4xl mb-3">⚠️</div>
        <h3 class="text-lg font-semibold text-[var(--color-error)] mb-2">
          {{ $t('learningMethodEditor.error') }}
        </h3>
        <p class="text-sm text-[var(--color-text-secondary)] mb-4">
          {{ error }}
        </p>
        <button
          @click="loadLearningMethods"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors"
        >
          {{ $t('learningMethodEditor.retry') }}
        </button>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="flex-1 flex flex-col min-h-0">
      <!-- Tab Navigation -->
      <div class="flex-shrink-0 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div class="flex gap-0">
          <button
            @click="activeTab = 'instances'"
            :class="[
              'flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2',
              activeTab === 'instances'
                ? 'text-[var(--color-primary)] border-[var(--color-primary)]'
                : 'text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-primary)]'
            ]"
          >
            {{ $t('learningMethodEditor.tabs.instances') }}
            <span class="ml-2 inline text-xs px-2 py-0.5 rounded bg-[var(--color-border)] text-[var(--color-text-secondary)]">
              {{ methods.length }}
            </span>
          </button>
          <button
            @click="activeTab = 'catalog'"
            :class="[
              'flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2',
              activeTab === 'catalog'
                ? 'text-[var(--color-primary)] border-[var(--color-primary)]'
                : 'text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-primary)]'
            ]"
          >
            {{ $t('learningMethodEditor.tabs.catalog') }}
          </button>
          <button
            @click="activeTab = 'stats'"
            :class="[
              'flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2',
              activeTab === 'stats'
                ? 'text-[var(--color-primary)] border-[var(--color-primary)]'
                : 'text-[var(--color-text-secondary)] border-transparent hover:text-[var(--color-text-primary)]'
            ]"
          >
            {{ $t('learningMethodEditor.tabs.statistics') }}
          </button>
        </div>
      </div>

      <!-- Tab Content (positioned relatively for tab components) -->
      <div class="flex-1 relative min-h-0">
        <!-- Instances Tab -->
        <InstancesTab
          v-if="activeTab === 'instances'"
          class="absolute inset-0"
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
          @edit="(method) => { editingMethod = method; editForm = { ...method } }"
        />

        <!-- Catalog Tab -->
        <CatalogTab
          v-if="activeTab === 'catalog'"
          class="absolute inset-0"
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

        <!-- Stats Tab -->
        <StatsTab
          v-if="activeTab === 'stats'"
          class="absolute inset-0"
          :stats="stats"
        />
      </div>
    </div>

    <!-- Method Type Selector Modal -->
    <div v-if="showMethodTypeSelector" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-[var(--color-background)] rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <!-- Header -->
        <div class="sticky top-0 bg-[var(--color-surface)] border-b border-[var(--color-border)] p-4 flex items-center justify-between">
          <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
            {{ $t('learningMethodEditor.selectMethod') }}
          </h2>
          <button
            @click="showMethodTypeSelector = false"
            class="p-1 hover:bg-[var(--color-border)] rounded transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Group Tabs -->
        <div class="sticky top-12 bg-[var(--color-surface)] border-b border-[var(--color-border)] p-3 flex gap-1">
          <button
            v-for="group in methodGroups"
            :key="group.id"
            @click="selectorGroup = group.id"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-lg transition-all',
              selectorGroup === group.id
                ? 'text-white shadow-sm'
                : 'bg-[var(--color-background)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            ]"
            :style="selectorGroup === group.id ? getGroupStyleFilled(group.id) : ''"
          >
            {{ group.label }}
          </button>
        </div>

        <!-- Methods List -->
        <div class="p-3">
          <div class="space-y-2">
            <div
              v-for="methodType in selectorMethodTypes"
              :key="methodType.lm_id"
              @click="() => { createMethodFromType(methodType); showMethodTypeSelector = false }"
              class="method-type-card bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-3 hover:border-[var(--color-primary)] hover:shadow-md transition-all cursor-pointer"
            >
              <div class="flex items-center gap-3">
                <div
                  class="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0"
                  :style="getGroupStyle(methodType.group)"
                >
                  {{ t(`lesson.methodExecution.methods.lm${String(methodType.lm_id).padStart(2, '0')}`) }}
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="font-semibold text-[var(--color-text-primary)] text-sm">{{ methodType.name }}</h4>
                  <p class="text-xs text-[var(--color-text-secondary)] mt-0.5">{{ methodType.description }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Method Modal -->
    <LearningMethodEditModal
      :editing-method="editingMethod"
      :edit-form="editForm"
      @close="editingMethod = null"
      @save="handleSaveFromModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
import { useLearningMethods } from './composables/useLearningMethods.ts'
import { InstancesTab, CatalogTab, StatsTab } from './tabs/index.ts'
import LearningMethodEditModal from './LearningMethodEditModal.vue'
import type { AdminLearningMethod, LearningMethodType as _LearningMethodType } from '@/infrastructure/api/clients/panel/admin'

interface Props {
  window: {
    payload?: {
      chapterId: string
      chapterTitle: string
      courseId: string
      courseTitle: string
    }
  }
}

const props = defineProps<Props>()

// Tab state
const activeTab = ref<'instances' | 'catalog' | 'stats'>('instances')

// Modal states
const showMethodTypeSelector = ref(false)
const editingMethod = ref<AdminLearningMethod | null>(null)

// Use composable for all business logic
const {
  methods,
  methodTypes: _methodTypes,
  loading,
  error,
  saveStatus,
  selectorGroup,
  selectedGroup: _selectedGroup,
  catalogActiveGroup,
  editForm,
  stats,
  dragState,
  chapterId: _chapterId,
  chapterTitle,
  courseId: _courseId,
  courseTitle,
  sortedMethods,
  methodGroups,
  filteredMethodTypes: _filteredMethodTypes,
  selectorMethodTypes,
  loadLearningMethods,
  calculateStats: _calculateStats,
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
  saveEditedMethod,
  togglePublish,
  deleteMethod,
  handleDragStart,
  handleDragOver,
  handleDrop,
  handleDragEnd,
  handleLearningMethodUpdate: _handleLearningMethodUpdate
} = useLearningMethods(props)

// Handle save from modal with form data
interface EditFormData {
  title: string
  instructions: string
  duration_minutes: number
  difficulty: 'easy' | 'medium' | 'hard'
  tier: 'basic' | 'premium' | 'pro'
}

function handleSaveFromModal(formData: EditFormData): void {
  if (!editingMethod.value) return
  // Merge form data with editing method and save
  const updatedMethod = {
    ...editingMethod.value,
    ...formData
  }
  saveEditedMethod(updatedMethod)
  editingMethod.value = null
}

// Load on mount
import { onMounted } from 'vue'
onMounted(() => {
  loadLearningMethods()
})
</script>

<style scoped>
.method-type-card {
  transition: all 0.15s ease;
}

.method-type-card:hover {
  transform: translateX(4px);
}
</style>
