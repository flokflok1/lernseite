/**
 * Learning Methods Panel Composable
 *
 * Encapsulates all business logic for managing learning methods in a panel.
 * Used by LearningMethodEditorPanelMain component.
 *
 * Features:
 * - Load methods and types from API
 * - CRUD operations (create, update, delete)
 * - Drag & drop reordering
 * - Publishing/unpublishing
 * - Statistics calculation
 * - Group management
 */

import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/desktop'
import {
  adminGetLearningMethodTypes,
  adminGetChapterLearningMethods,
  adminCreateLearningMethod,
  adminUpdateLearningMethod,
  adminDeleteLearningMethod,
  adminReorderLearningMethods,
  adminPublishLearningMethod,
  adminUnpublishLearningMethod,
  type AdminLearningMethod,
  type LearningMethodType,
  type LearningMethodGroup
} from '@/infrastructure/api/clients/admin'

export function useLearningMethodsPanel(props: any) {
  const { t } = useI18n()
  const panelStore = usePanelStore()

  // State
  const methods = ref<AdminLearningMethod[]>([])
  const methodTypes = ref<LearningMethodType[]>([])
  const loading = ref(true)
  const error = ref<string | null>(null)
  const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')

  // Tab state
  const activeTab = ref<'instances' | 'catalog' | 'stats'>('instances')

  // Modal states
  const showMethodTypeSelector = ref(false)
  const selectorGroup = ref<LearningMethodGroup>('A')
  const selectedGroup = ref<LearningMethodGroup | null>(null)
  const catalogActiveGroup = ref<LearningMethodGroup>('A')

  // Edit form
  const editingMethod = ref<AdminLearningMethod | null>(null)
  const editForm = ref({
    title: '',
    instructions: '',
    duration_minutes: 15,
    difficulty: 'medium' as 'easy' | 'medium' | 'hard',
    tier: 'basic' as 'basic' | 'premium' | 'pro'
  })

  // Statistics
  const stats = ref<{
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
  } | null>(null)

  // Drag & Drop State
  const dragState = ref({
    draggedIndex: null as number | null,
    targetIndex: null as number | null
  })

  // Computed
  const chapterId = computed(() => props.panel.payload?.chapterId as string)
  const chapterTitle = computed(() => props.panel.payload?.chapterTitle as string || 'Unbekannt')
  const courseId = computed(() => props.panel.payload?.courseId as string)
  const courseTitle = computed(() => props.panel.payload?.courseTitle as string || 'Unbekannt')

  const sortedMethods = computed(() => {
    return [...methods.value].sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
  })

  const methodGroups = computed(() => [
    { id: 'A' as LearningMethodGroup, label: 'A: Erklärend', count: 5 },
    { id: 'B' as LearningMethodGroup, label: 'B: Praxis', count: 6 },
    { id: 'C' as LearningMethodGroup, label: 'C: Prüfung', count: 8 },
    { id: 'D' as LearningMethodGroup, label: 'D: Pro', count: 5 },
    { id: 'E' as LearningMethodGroup, label: 'E: IT', count: 4 },
    { id: 'F' as LearningMethodGroup, label: 'F: Kollaborativ', count: 7 }
  ])

  const filteredMethodTypes = computed(() => {
    if (!selectedGroup.value) return methodTypes.value
    return methodTypes.value.filter(mt => mt.group === selectedGroup.value)
  })

  const selectorMethodTypes = computed(() => {
    return methodTypes.value.filter(mt => mt.group === selectorGroup.value)
  })

  // Methods
  const loadLearningMethods = async () => {
    if (!chapterId.value) {
      error.value = 'Keine Kapitel-ID angegeben'
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
      error.value = err.response?.data?.message || 'Fehler beim Laden der Lernmethoden'
    } finally {
      loading.value = false
    }
  }

  const calculateStats = () => {
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

  const getMethodTypeName = (methodType: number): string => {
    const type = methodTypes.value.find(t => t.lm_id === methodType)
    return type?.name || `Methode ${methodType}`
  }

  const getGroupPosition = (methodType: LearningMethodType): number => {
    const groupMethods = methodTypes.value
      .filter(mt => mt.group === methodType.group)
      .sort((a, b) => a.lm_id - b.lm_id)
    return groupMethods.findIndex(mt => mt.lm_id === methodType.lm_id) + 1
  }

  const getGroupPositionById = (methodTypeId: number): string => {
    const type = methodTypes.value.find(t => t.lm_id === methodTypeId)
    if (!type) return String(methodTypeId).padStart(2, '0')
    return String(getGroupPosition(type)).padStart(2, '0')
  }

  const getMethodGroup = (methodType: number): LearningMethodGroup => {
    const type = methodTypes.value.find(t => t.lm_id === methodType)
    return type?.group || 'A'
  }

  const getGroupStyle = (group: LearningMethodGroup): string => {
    const styles: Record<string, string> = {
      'A': 'background-color: var(--color-info-bg, #dbeafe); color: var(--color-info-text, #1e40af);',
      'B': 'background-color: var(--color-success-bg, #dcfce7); color: var(--color-success-text, #15803d);',
      'C': 'background-color: var(--color-warning-bg, #fef3c7); color: var(--color-warning-text, #92400e);',
      'D': 'background-color: var(--color-premium-bg, #f3e8ff); color: var(--color-premium-text, #6b21a8);',
      'E': 'background-color: #cffafe; color: #0e7490;',
      'F': 'background-color: #fce7f3; color: #be185d;'
    }
    return styles[group] || styles['A']
  }

  const getGroupStyleFilled = (group: LearningMethodGroup): string => {
    const styles: Record<string, string> = {
      'A': 'background-color: #2563eb;',
      'B': 'background-color: #16a34a;',
      'C': 'background-color: #ea580c;',
      'D': 'background-color: #7c3aed;',
      'E': 'background-color: #0891b2;',
      'F': 'background-color: #db2777;'
    }
    return styles[group] || styles['A']
  }

  const getTierStyle = (tier: string): string => {
    const styles: Record<string, string> = {
      basic: 'color: var(--color-success, #16a34a);',
      premium: 'color: var(--color-warning, #ea580c);',
      pro: 'color: var(--color-premium-text, #6b21a8);'
    }
    return styles[tier] || ''
  }

  const getTierLabel = (tier: string): string => {
    const labels: Record<string, string> = {
      basic: 'Basic',
      premium: 'Premium',
      pro: 'Pro'
    }
    return labels[tier] || tier
  }

  const getTierFromGroup = (group: LearningMethodGroup): 'basic' | 'premium' | 'pro' => {
    if (group === 'A' || group === 'B') return 'basic'
    if (group === 'C' || group === 'E') return 'premium'
    return 'pro'
  }

  const getMethodsByGroup = (groupId: LearningMethodGroup): LearningMethodType[] => {
    return methodTypes.value.filter(mt => mt.group === groupId)
  }

  const createMethodFromType = (methodType: LearningMethodType) => {
    if (!chapterId.value) return

    showMethodTypeSelector.value = false

    const panelType = `learning-method-${methodType.lm_id}-form` as any
    panelStore.openPanel({
      type: panelType,
      title: `${methodType.name} erstellen`,
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

  const editMethod = (method: AdminLearningMethod) => {
    const panelType = `learning-method-${method.method_type}-form` as any
    const methodTypeInfo = methodTypes.value.find(t => t.lm_id === method.method_type)

    panelStore.openPanel({
      type: panelType,
      title: `${methodTypeInfo?.name || 'Lernmethode'} bearbeiten`,
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

  const saveEditedMethod = async () => {
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

  const togglePublish = async (method: AdminLearningMethod) => {
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

  const deleteMethod = async (methodId: string) => {
    if (!confirm('Möchten Sie diese Lernmethode wirklich löschen?')) return

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

  // Drag & Drop Handlers
  const handleDragStart = (index: number) => {
    dragState.value.draggedIndex = index
  }

  const handleDragOver = (index: number) => {
    dragState.value.targetIndex = index
  }

  const handleDrop = async (targetIndex: number) => {
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

  const handleDragEnd = () => {
    dragState.value.draggedIndex = null
    dragState.value.targetIndex = null
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
    selectedGroup,
    catalogActiveGroup,
    editingMethod,
    editForm,
    stats,
    dragState,

    // Computed
    chapterId,
    chapterTitle,
    courseId,
    courseTitle,
    sortedMethods,
    methodGroups,
    filteredMethodTypes,
    selectorMethodTypes,

    // Methods
    loadLearningMethods,
    calculateStats,
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
  }
}
