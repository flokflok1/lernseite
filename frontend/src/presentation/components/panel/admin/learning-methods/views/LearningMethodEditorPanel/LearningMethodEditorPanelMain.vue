<template>
  <div class="learning-method-editor-panel h-full flex flex-col">
    <!-- Header -->
    <div class="flex-shrink-0 border-b border-[var(--color-border)] p-4 bg-[var(--color-surface)]">
      <div class="flex items-center justify-between mb-2">
        <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
          {{ $t('panel.learningMethods.editor.header.course') }}: {{ courseName }}
        </h2>
        <div v-if="saveStatus === 'saving'" class="flex items-center gap-2">
          <div class="animate-spin">⚙️</div>
          <span class="text-sm text-[var(--color-text-secondary)]">
            {{ $t('panel.learningMethods.editor.status.saving') }}
          </span>
        </div>
        <div v-else-if="saveStatus === 'saved'" class="text-sm text-green-600">
          ✓ {{ $t('panel.learningMethods.editor.status.saved') }}
        </div>
        <div v-else-if="saveStatus === 'error'" class="text-sm text-red-600">
          ✗ {{ $t('panel.learningMethods.editor.status.error') }}
        </div>
      </div>

      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ $t('panel.learningMethods.editor.header.chapter') }}: {{ chapterName }}
      </p>
    </div>

    <!-- Tab Navigation -->
    <div class="flex-shrink-0 border-b border-[var(--color-border)] bg-[var(--color-surface)]">
      <div class="flex gap-1 p-2">
        <button
          v-for="tab in tabs"
          :key="tab"
          @click="activeTab = tab"
          :class="[
            'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
            activeTab === tab
              ? 'bg-[var(--color-primary)] text-white'
              : 'bg-[var(--color-background)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
          ]"
        >
          {{ getTabLabel(tab) }}
        </button>
      </div>
    </div>

    <!-- Content Area -->
    <div class="flex-1 overflow-hidden bg-[var(--color-background)]">
      <!-- Loading State -->
      <div v-if="isLoading" class="h-full flex items-center justify-center">
        <div class="text-center">
          <div class="animate-spin text-4xl mb-2">⚙️</div>
          <p class="text-[var(--color-text-secondary)]">
            {{ $t('panel.learningMethods.editor.status.loading') }}
          </p>
        </div>
      </div>

      <!-- Instances Tab -->
      <InstancesTab
        v-else-if="activeTab === 'instances'"
        :methods="methodInstances"
        :sorted-methods="sortedMethods"
        :drag-state="dragState"
        :style="{ position: 'absolute', top: '0', left: '0', right: '0', bottom: '0' }"
        @open-selector="openMethodTypeSelector"
        @edit="editingMethodId = $event"
        @reorder="handleReorderMethods"
      />

      <!-- Catalog Tab -->
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
        @create-method="handleCreateMethod"
      />

      <!-- Stats Tab -->
      <StatsTab
        v-else-if="activeTab === 'stats'"
        :stats="methodStats"
      />
    </div>

    <!-- Method Type Selector Modal -->
    <div
      v-if="showMethodTypeSelector"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showMethodTypeSelector = false"
    >
      <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
        <div class="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
          <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
            {{ $t('panel.learningMethods.editor.modal.selectMethod') }}
          </h3>
          <button
            @click="showMethodTypeSelector = false"
            class="p-1 rounded hover:bg-[var(--color-background)] transition-colors"
          >
            <svg class="w-5 h-5 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-4 overflow-y-auto max-h-[60vh]">
          <p class="text-sm text-[var(--color-text-secondary)]">
            Available method types will be displayed here
          </p>
        </div>

        <div class="p-4 border-t border-[var(--color-border)] flex justify-end gap-3">
          <button
            @click="showMethodTypeSelector = false"
            class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-background)] transition-colors"
          >
            {{ $t('panel.learningMethods.editor.buttons.cancel') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Method Modal -->
    <LearningMethodEditModal
      v-if="editingMethodId && editingMethod"
      :editing-method="editingMethod"
      :edit-form="editForm"
      :get-group-style="getGroupStyle"
      :get-method-group="getMethodGroup"
      :get-group-position-by-id="getGroupPositionById"
      :get-method-type-name="getMethodTypeName"
      @close="editingMethodId = null"
      @save="handleSaveMethodFromModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGroupTier } from '@/application/composables/learning/useGroupTier'
import type { AdminLearningMethod, LearningMethodType, LearningMethodGroup } from '@/application/services/api/panel-admin'
import { InstancesTab, CatalogTab, StatsTab } from './tabs'
import { LearningMethodEditModal } from '.'

interface Props {
  courseId: string
  courseName: string
  chapterId: string
  chapterName: string
  methodInstances?: AdminLearningMethod[]
  methodTypes?: LearningMethodType[]
  stats?: any
}

const props = withDefaults(defineProps<Props>(), {
  methodInstances: () => [],
  methodTypes: () => [],
  stats: () => null
})

const emit = defineEmits<{
  'update:methods': [methods: AdminLearningMethod[]]
  'save-method': [method: AdminLearningMethod]
}>()

// Composition
const { t } = useI18n()
const groupTier = useGroupTier()

// State
const activeTab = ref<'instances' | 'catalog' | 'stats'>('instances')
const isLoading = ref(false)
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')
const catalogActiveGroup = ref<LearningMethodGroup>('A')
const showMethodTypeSelector = ref(false)
const editingMethodId = ref<string | null>(null)

// Form state for editing
const editForm = ref({
  title: '',
  instructions: '',
  duration_minutes: 0,
  difficulty: 'medium' as const,
  tier: 'basic' as const
})

// Computed
const methodInstances = computed(() => props.methodInstances)
const sortedMethods = computed(() => {
  return [...methodInstances.value].sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
})

const methodStats = computed(() => props.stats)

const methodGroups = computed(() => {
  const groupCodes = groupTier.getAllGroupCodes()
  if (groupCodes.length === 0) {
    return []
  }
  return groupCodes.map(code => {
    const groupInfo = groupTier.getGroupInfo(code)
    const methodsInGroup = (props.methodTypes || []).filter(mt => mt.group === code)
    return {
      id: code as LearningMethodGroup,
      label: groupInfo?.name || code,
      count: methodsInGroup.length
    }
  })
})

const tabs = ['instances', 'catalog', 'stats'] as const

const editingMethod = computed(() => {
  return methodInstances.value.find(m => m.id === editingMethodId.value) || null
})

const dragState = ref({
  isDragging: false,
  draggedId: null as string | null,
  draggedOverId: null as string | null
})

// Methods
function getTabLabel(tab: string): string {
  return t(`panel.learningMethods.editor.tabs.${tab}`)
}

function getMethodsByGroup(group: LearningMethodGroup): LearningMethodType[] {
  return (props.methodTypes || []).filter(m => m.group === group)
}

/**
 * Get CSS styles for a group badge.
 * Delegates to composable for database-driven flexibility.
 */
function getGroupStyle(group: LearningMethodGroup): string {
  return groupTier.getGroupStyle(group)
}

/**
 * Get CSS styles for a filled group badge.
 * Delegates to composable.
 */
function getGroupStyleFilled(group: LearningMethodGroup): string {
  return groupTier.getGroupStyleFilled(group)
}

/**
 * Get position of method type within its group.
 * Derived from method_type metadata.
 */
function getGroupPosition(methodType: LearningMethodType): number {
  const groupMethods = (props.methodTypes || [])
    .filter(m => m.group === methodType.group)
    .sort((a, b) => a.method_type - b.method_type)
  return groupMethods.findIndex(m => m.method_type === methodType.method_type) + 1
}

/**
 * Get position of method type by ID, padded to 2 digits.
 * Derived from method_type metadata.
 */
function getGroupPositionById(methodTypeId: number): string {
  const methodType = (props.methodTypes || []).find(m => m.method_type === methodTypeId)
  if (!methodType) return String(methodTypeId).padStart(2, '0')
  const position = getGroupPosition(methodType)
  return String(position).padStart(2, '0')
}

function getTierFromGroup(group: LearningMethodGroup): 'basic' | 'premium' | 'pro' {
  const dbTier = groupTier.getTierFromGroup(group)
  const tierMap: Record<string, string> = {
    'basic': 'basic',
    'premium': 'premium',
    'enterprise': 'pro'
  }
  return (tierMap[dbTier] || 'basic') as 'basic' | 'premium' | 'pro'
}

/**
 * Get CSS styles for a tier badge.
 * Delegates to composable for consistency.
 */
function getTierStyle(tier: string): string {
  return groupTier.getTierStyle(tier)
}

/**
 * Get human-readable label for a tier.
 * Delegates to composable for database-driven flexibility.
 */
function getTierLabel(tier: string): string {
  return groupTier.getTierLabel(tier)
}

/**
 * Get group code for a method type ID.
 * Looks up the method type in props.methodTypes to find its group.
 * Falls back to mapping if method type not found.
 */
function getMethodGroup(methodTypeId: number): LearningMethodGroup {
  const methodType = (props.methodTypes || []).find(m => m.method_type === methodTypeId)
  if (methodType) return methodType.group as LearningMethodGroup

  // Fallback: reasonable defaults based on LM structure
  if (methodTypeId < 5) return 'A'
  if (methodTypeId < 9) return 'B'
  return 'C'
}

function getMethodTypeName(methodTypeId: number): string {
  const method = props.methodTypes?.find(m => m.method_type === methodTypeId)
  return method?.name || `Method ${methodTypeId}`
}

function openMethodTypeSelector(): void {
  showMethodTypeSelector.value = true
}

function handleCreateMethod(methodType: LearningMethodType): void {
  console.log('Creating method from type:', methodType)
  showMethodTypeSelector.value = false
  // Trigger API call to create new method instance
}

function handleReorderMethods(methods: AdminLearningMethod[]): void {
  saveStatus.value = 'saving'
  // Trigger API call to save reordering
  setTimeout(() => {
    saveStatus.value = 'saved'
    setTimeout(() => {
      saveStatus.value = 'idle'
    }, 2000)
  }, 500)
  emit('update:methods', methods)
}

interface EditFormData {
  title: string
  instructions: string
  duration_minutes: number
  difficulty: 'easy' | 'medium' | 'hard'
  tier: 'basic' | 'premium' | 'pro'
}

function handleSaveMethodFromModal(formData: EditFormData): void {
  if (!editingMethod.value) return

  saveStatus.value = 'saving'
  // Trigger API call to save method
  setTimeout(() => {
    saveStatus.value = 'saved'
    editingMethodId.value = null
    setTimeout(() => {
      saveStatus.value = 'idle'
    }, 2000)
  }, 500)

  emit('save-method', {
    ...editingMethod.value,
    ...formData
  })
}

// Watch for method changes
watch(editingMethodId, (newId) => {
  if (newId && editingMethod.value) {
    editForm.value = {
      title: editingMethod.value.title || '',
      instructions: editingMethod.value.instructions || '',
      duration_minutes: editingMethod.value.duration_minutes || 0,
      difficulty: editingMethod.value.difficulty || 'medium',
      tier: editingMethod.value.tier || 'basic'
    }
  }
})
</script>
