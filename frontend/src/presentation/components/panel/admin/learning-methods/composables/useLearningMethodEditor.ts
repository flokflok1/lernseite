import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import { useGroupTier } from '@/application/composables/learning/useGroupTier'
import type { LsxWindow } from '@/application/stores/modules/ui/window.store'
import {
  adminGetLearningMethodTypes,
  adminGetChapterLearningMethods,
  adminUpdateLearningMethod,
  adminDeleteLearningMethod,
  adminReorderLearningMethods,
  adminPublishLearningMethod,
  adminUnpublishLearningMethod,
  type AdminLearningMethod,
  type LearningMethodType,
  type LearningMethodGroup
} from '@/application/services/api/panel-admin'

export interface LearningMethodStats {
  total_methods: number
  published_count: number
  unique_types: number
  total_duration: number
  easy_count: number
  medium_count: number
  hard_count: number
  basic_count: number
  premium_count: number
  pro_count: number
}

export interface EditFormData {
  title: string
  instructions: string
  duration_minutes: number
  difficulty: 'easy' | 'medium' | 'hard'
  tier: 'basic' | 'premium' | 'pro'
}

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error'
export type EditorTab = 'instances' | 'catalog' | 'stats'

/**
 * Composable for the LearningMethodEditor component.
 * Encapsulates all state management, API calls, drag-and-drop, and
 * helper functions for learning method CRUD operations.
 */
export function useLearningMethodEditor(windowRef: { value: LsxWindow }) {
  const { t } = useI18n()
  const windowStore = useWindowStore()
  const groupTier = useGroupTier()

  // State
  const methods = ref<AdminLearningMethod[]>([])
  const methodTypes = ref<LearningMethodType[]>([])
  const loading = ref(true)
  const error = ref<string | null>(null)
  const saveStatus = ref<SaveStatus>('idle')
  const activeTab = ref<EditorTab>('instances')

  // Modal states
  const showMethodTypeSelector = ref(false)
  const selectorGroup = ref<LearningMethodGroup>('A')
  const selectedGroup = ref<LearningMethodGroup | null>(null)
  const editingMethod = ref<AdminLearningMethod | null>(null)
  const catalogActiveGroup = ref<LearningMethodGroup>('A')

  // Edit form
  const editForm = ref<EditFormData>({
    title: '',
    instructions: '',
    duration_minutes: 15,
    difficulty: 'medium',
    tier: 'basic'
  })

  // Statistics
  const stats = ref<LearningMethodStats | null>(null)

  // Drag & Drop
  const dragState = ref({
    draggedIndex: null as number | null,
    targetIndex: null as number | null
  })

  // Computed
  const tabs = computed(() => [
    { id: 'instances' as const, label: t('learningMethodEditor.tabs.instances'), icon: '🎯' },
    { id: 'catalog' as const, label: t('learningMethodEditor.tabs.catalog'), icon: '📖' },
    { id: 'stats' as const, label: t('learningMethodEditor.tabs.stats'), icon: '📊' }
  ])

  const chapterId = computed(() => windowRef.value.payload?.chapterId as string)
  const chapterTitle = computed(() => windowRef.value.payload?.chapterTitle as string || t('common.unknown'))
  const courseId = computed(() => windowRef.value.payload?.courseId as string)
  const courseTitle = computed(() => windowRef.value.payload?.courseTitle as string || t('common.unknown'))

  const sortedMethods = computed(() =>
    [...methods.value].sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
  )

  const methodGroups = computed(() => {
    const groupCodes = groupTier.getAllGroupCodes()
    if (groupCodes.length === 0) return []

    return groupCodes.map(code => {
      const groupInfo = groupTier.getGroupInfo(code)
      const methodsInGroup = methodTypes.value.filter(mt => mt.group === code)
      return {
        id: code as LearningMethodGroup,
        label: groupInfo?.name || code,
        count: methodsInGroup.length
      }
    })
  })

  const selectorMethodTypes = computed(() =>
    methodTypes.value.filter(mt => mt.group === selectorGroup.value)
  )

  // Data loading
  async function loadLearningMethods(): Promise<void> {
    if (!chapterId.value) {
      error.value = t('learningMethodEditor.noChapterId')
      loading.value = false
      return
    }

    loading.value = true
    error.value = null

    try {
      const [methodsResponse, typesData] = await Promise.all([
        adminGetChapterLearningMethods(chapterId.value),
        adminGetLearningMethodTypes()
      ])

      methods.value = methodsResponse.learning_methods
      methodTypes.value = typesData.types

      if (methodsResponse.statistics) {
        stats.value = methodsResponse.statistics
      } else {
        calculateStats()
      }
    } catch (err: any) {
      console.error('Error loading learning methods:', err)
      error.value = err.response?.data?.message || t('learningMethodEditor.loadError')
    } finally {
      loading.value = false
    }
  }

  function calculateStats(): void {
    const m = methods.value
    stats.value = {
      total_methods: m.length,
      published_count: m.filter(x => x.published).length,
      unique_types: new Set(m.map(x => x.method_type)).size,
      total_duration: m.reduce((sum, x) => sum + (x.duration_minutes || 0), 0),
      easy_count: m.filter(x => x.difficulty === 'easy').length,
      medium_count: m.filter(x => x.difficulty === 'medium').length,
      hard_count: m.filter(x => x.difficulty === 'hard').length,
      basic_count: m.filter(x => x.tier === 'basic').length,
      premium_count: m.filter(x => x.tier === 'premium').length,
      pro_count: m.filter(x => x.tier === 'pro').length
    }
  }

  // Display helpers
  function getMethodTypeName(methodType: number): string {
    const type = methodTypes.value.find(t => t.lm_id === methodType)
    return type?.name || `Methode ${methodType}`
  }

  function getGroupPosition(methodType: LearningMethodType): number {
    const groupMethods = methodTypes.value
      .filter(mt => mt.group === methodType.group)
      .sort((a, b) => a.lm_id - b.lm_id)
    return groupMethods.findIndex(mt => mt.lm_id === methodType.lm_id) + 1
  }

  function getGroupPositionById(methodTypeId: number): string {
    const type = methodTypes.value.find(t => t.lm_id === methodTypeId)
    if (!type) return String(methodTypeId).padStart(2, '0')
    return String(getGroupPosition(type)).padStart(2, '0')
  }

  function getMethodGroup(methodType: number): LearningMethodGroup {
    const type = methodTypes.value.find(t => t.lm_id === methodType)
    return type?.group || 'A'
  }

  function getGroupStyle(group: LearningMethodGroup): string {
    return groupTier.getGroupStyle(group)
  }

  function getGroupStyleFilled(group: LearningMethodGroup): string {
    return groupTier.getGroupStyleFilled(group)
  }

  function getTierStyle(tier: string): string {
    return groupTier.getTierStyle(tier)
  }

  function getTierLabel(tier: string): string {
    const tierKeys: Record<string, string> = {
      basic: 'learningMethodEditor.tierOptions.basic',
      premium: 'learningMethodEditor.tierOptions.premium',
      pro: 'learningMethodEditor.tierOptions.pro'
    }
    return tierKeys[tier] ? t(tierKeys[tier]) : tier
  }

  function getTierFromGroup(group: LearningMethodGroup): 'basic' | 'premium' | 'pro' {
    const dbTier = groupTier.getTierFromGroup(group)
    const tierMap: Record<string, string> = {
      basic: 'basic',
      premium: 'premium',
      enterprise: 'pro'
    }
    return (tierMap[dbTier] || 'basic') as 'basic' | 'premium' | 'pro'
  }

  function getMethodsByGroup(groupId: LearningMethodGroup): LearningMethodType[] {
    return methodTypes.value.filter(mt => mt.group === groupId)
  }

  // CRUD operations
  function createMethodFromType(methodType: LearningMethodType): void {
    if (!chapterId.value) return

    showMethodTypeSelector.value = false
    const windowType = `learning-method-${methodType.lm_id}-form` as any
    windowStore.openWindow({
      type: windowType,
      title: t('learningMethodEditor.createPanelTitle', { name: methodType.name }),
      icon: '📝',
      payload: {
        chapterId: chapterId.value,
        chapterTitle: chapterTitle.value,
        courseId: courseId.value,
        courseTitle: courseTitle.value,
        methodCode: methodType.lm_id
      },
      preferredPosition: { x: 120, y: 30 },
      size: { width: 600, height: 700 }
    })
  }

  function editMethod(method: AdminLearningMethod): void {
    const windowType = `learning-method-${method.method_type}-form` as any
    const methodTypeInfo = methodTypes.value.find(mt => mt.lm_id === method.method_type)

    windowStore.openWindow({
      type: windowType,
      title: t('learningMethodEditor.editPanelTitle', {
        name: methodTypeInfo?.name || t('learningMethodEditor.defaultMethodName')
      }),
      icon: '✏️',
      payload: {
        chapterId: chapterId.value,
        chapterTitle: chapterTitle.value,
        courseId: courseId.value,
        courseTitle: courseTitle.value,
        methodCode: method.method_type,
        instanceId: method.method_id,
        instanceData: {
          title: method.title,
          instructions: method.instructions,
          duration_minutes: method.duration_minutes,
          difficulty: method.difficulty,
          tier: method.tier,
          data: method.data || {}
        }
      },
      preferredPosition: { x: 120, y: 30 },
      size: { width: 600, height: 700 }
    })
  }

  async function saveEditedMethod(): Promise<void> {
    if (!editingMethod.value) return

    saveStatus.value = 'saving'
    try {
      const updated = await adminUpdateLearningMethod(editingMethod.value.method_id, {
        title: editForm.value.title,
        instructions: editForm.value.instructions || undefined,
        duration_minutes: editForm.value.duration_minutes,
        difficulty: editForm.value.difficulty,
        tier: editForm.value.tier
      })

      const index = methods.value.findIndex(m => m.method_id === updated.method_id)
      if (index !== -1) {
        methods.value[index] = updated
      }

      editingMethod.value = null
      calculateStats()
      saveStatus.value = 'saved'
      setTimeout(() => { saveStatus.value = 'idle' }, 2000)
    } catch (err: any) {
      console.error('Error updating learning method:', err)
      saveStatus.value = 'error'
      setTimeout(() => { saveStatus.value = 'idle' }, 3000)
    }
  }

  async function togglePublish(method: AdminLearningMethod): Promise<void> {
    saveStatus.value = 'saving'
    try {
      const updated = method.published
        ? await adminUnpublishLearningMethod(method.method_id)
        : await adminPublishLearningMethod(method.method_id)

      const index = methods.value.findIndex(m => m.method_id === method.method_id)
      if (index !== -1) {
        methods.value[index] = updated
      }

      calculateStats()
      saveStatus.value = 'saved'
      setTimeout(() => { saveStatus.value = 'idle' }, 2000)
    } catch (err: any) {
      console.error('Error toggling publish:', err)
      saveStatus.value = 'error'
      setTimeout(() => { saveStatus.value = 'idle' }, 3000)
    }
  }

  async function deleteMethod(methodId: string): Promise<void> {
    if (!confirm(t('learningMethodEditor.deleteConfirm'))) return

    saveStatus.value = 'saving'
    try {
      await adminDeleteLearningMethod(methodId)
      methods.value = methods.value.filter(m => m.method_id !== methodId)
      calculateStats()
      saveStatus.value = 'saved'
      setTimeout(() => { saveStatus.value = 'idle' }, 2000)
    } catch (err: any) {
      console.error('Error deleting learning method:', err)
      saveStatus.value = 'error'
      setTimeout(() => { saveStatus.value = 'idle' }, 3000)
    }
  }

  // Drag & Drop
  function handleDragStart(index: number): void {
    dragState.value.draggedIndex = index
  }

  function handleDragOver(index: number): void {
    dragState.value.targetIndex = index
  }

  async function handleDrop(targetIndex: number): Promise<void> {
    const draggedIndex = dragState.value.draggedIndex
    if (draggedIndex === null || draggedIndex === targetIndex) return

    const methodsCopy = [...sortedMethods.value]
    const [removed] = methodsCopy.splice(draggedIndex, 1)
    methodsCopy.splice(targetIndex, 0, removed)

    methodsCopy.forEach((method, idx) => {
      method.order_index = idx
    })

    methods.value = methodsCopy

    if (chapterId.value) {
      try {
        await adminReorderLearningMethods(chapterId.value, methodsCopy.map(m => m.method_id))
      } catch (err: any) {
        console.error('Error reordering:', err)
        await loadLearningMethods()
      }
    }

    dragState.value.draggedIndex = null
    dragState.value.targetIndex = null
  }

  function handleDragEnd(): void {
    dragState.value.draggedIndex = null
    dragState.value.targetIndex = null
  }

  // Lifecycle setup
  function setupLifecycle(): void {
    const handleUpdate = () => loadLearningMethods()

    onMounted(() => {
      groupTier.loadGroups()
      loadLearningMethods()

      const preSelectedGroup = windowRef.value.payload?.preSelectedGroup as LearningMethodGroup | undefined
      if (preSelectedGroup && ['A', 'B', 'C', 'D', 'E', 'F'].includes(preSelectedGroup)) {
        selectedGroup.value = preSelectedGroup
        selectorGroup.value = preSelectedGroup
        catalogActiveGroup.value = preSelectedGroup
        activeTab.value = 'catalog'
      }

      window.addEventListener('learning-method-updated', handleUpdate)
    })

    onUnmounted(() => {
      window.removeEventListener('learning-method-updated', handleUpdate)
    })
  }

  return {
    // State
    methods,
    methodTypes,
    loading,
    error,
    saveStatus,
    activeTab,
    showMethodTypeSelector,
    selectorGroup,
    editingMethod,
    catalogActiveGroup,
    editForm,
    stats,
    dragState,

    // Computed
    tabs,
    chapterTitle,
    courseTitle,
    sortedMethods,
    methodGroups,
    selectorMethodTypes,

    // Data
    loadLearningMethods,

    // Display helpers
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

    // CRUD
    createMethodFromType,
    editMethod,
    saveEditedMethod,
    togglePublish,
    deleteMethod,

    // Drag & Drop
    handleDragStart,
    handleDragOver,
    handleDrop,
    handleDragEnd,

    // Lifecycle
    setupLifecycle
  }
}
