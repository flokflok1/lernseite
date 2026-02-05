import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/window.store'
import { useGroupTier } from '@/application/composables/useGroupTier'
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
} from '@/application/services/api/admin'

export function useLearningMethods(props: any) {
  const { t } = useI18n()
  const windowStore = useWindowStore()

  // Initialize group tier composable (database-driven tier information)
  const groupTier = useGroupTier()

  // State
  const methods = ref<AdminLearningMethod[]>([])
  const methodTypes = ref<LearningMethodType[]>([])
  const loading = ref(true)
  const error = ref<string | null>(null)
  const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle')

  // Modal states
  const selectorGroup = ref<LearningMethodGroup>('A')
  const selectedGroup = ref<LearningMethodGroup | null>(null)
  const catalogActiveGroup = ref<LearningMethodGroup>('A')

  // Edit form
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
  const chapterId = computed(() => props.window.payload?.chapterId as string)
  const chapterTitle = computed(() => props.window.payload?.chapterTitle as string || t('common.unknown'))
  const courseId = computed(() => props.window.payload?.courseId as string)
  const courseTitle = computed(() => props.window.payload?.courseTitle as string || t('common.unknown'))

  const sortedMethods = computed(() => {
    return [...methods.value].sort((a, b) => (a.order_index || 0) - (b.order_index || 0))
  })

  /**
   * Learning method groups with database-driven names and counts.
   *
   * REPLACED hardcoded group definitions with data from @/application/composables/useGroupTier
   * Now fetches group metadata (name, icon, tier) from database instead of hardcoding
   *
   * Includes fallback for when groups haven't loaded yet.
   */
  const methodGroups = computed(() => {
    // Get all group codes from composable (may be empty if not loaded yet)
    const groupCodes = groupTier.getAllGroupCodes()

    // If groups not yet loaded, return empty array (will be populated once loadLearningMethods completes)
    if (groupCodes.length === 0) {
      return []
    }

    // Build groups array from database groups
    return groupCodes.map(code => {
      const groupInfo = groupTier.getGroupInfo(code)
      const methodsInGroup = methodTypes.value.filter(mt => mt.group === code)

      return {
        id: code as LearningMethodGroup,
        label: groupInfo?.name || code, // Use database name instead of i18n
        icon: groupInfo?.icon || '📋', // Use database icon
        description: groupInfo?.description || '',
        tier: groupInfo?.tier || 'basic',
        count: methodsInGroup.length // Dynamic count from methodTypes
      }
    })
  })

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
      error.value = t('windows.learningMethodEditor.noChapterId')
      loading.value = false
      return
    }

    loading.value = true
    error.value = null

    try {
      const [methodsResponse, typesData] = await Promise.all([
        adminGetChapterLearningMethods(chapterId.value),
        adminGetLearningMethodTypes(),
        groupTier.loadGroups() // Load group tier information from database
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
      error.value = err.response?.data?.message || t('windows.learningMethodEditor.loadError')
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

  /**
   * Get position number within group (1-based) for display
   * This ensures new methods get proper sequential numbers within their group
   */
  const getGroupPosition = (methodType: LearningMethodType): number => {
    const groupMethods = methodTypes.value
      .filter(mt => mt.group === methodType.group)
      .sort((a, b) => a.lm_id - b.lm_id)
    return groupMethods.findIndex(mt => mt.lm_id === methodType.lm_id) + 1
  }

  /**
   * Get position number within group by method_type ID (for existing instances)
   */
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
    return groupTier.getGroupStyle(group)
  }

  const getGroupStyleFilled = (group: LearningMethodGroup): string => {
    return groupTier.getGroupStyleFilled(group)
  }

  const getTierStyle = (tier: string): string => {
    return groupTier.getTierStyle(tier)
  }

  const getTierLabel = (tier: string): string => {
    const tierKeys: Record<string, string> = {
      basic: 'windows.learningMethodEditor.tierOptions.basic',
      premium: 'windows.learningMethodEditor.tierOptions.premium',
      pro: 'windows.learningMethodEditor.tierOptions.pro'
    }
    return tierKeys[tier] ? t(tierKeys[tier]) : tier
  }

  /**
   * Get tier from learning method group.
   * Uses database-driven group tier information via useGroupTier composable.
   *
   * REPLACES hardcoded tier mapping: now delegates to @/application/composables/useGroupTier
   *
   * @param group - Learning Method Group (A, B, C, etc.)
   * @returns Tier: 'basic' | 'premium' | 'pro' | 'enterprise'
   */
  const getTierFromGroup = (group: LearningMethodGroup): string => {
    // Use database-driven tier information from composable
    const dbTier = groupTier.getTierFromGroup(group)

    // Map database tiers to UI tiers (backward compatibility)
    const tierMap: Record<string, string> = {
      'basic': 'basic',
      'premium': 'premium',
      'enterprise': 'pro' // 'enterprise' in DB shown as 'pro' in UI
    }
    return tierMap[dbTier] || 'basic'
  }

  const getMethodsByGroup = (groupId: LearningMethodGroup): LearningMethodType[] => {
    return methodTypes.value.filter(mt => mt.group === groupId)
  }

  const createMethodFromType = (methodType: LearningMethodType) => {
    if (!chapterId.value) return

    const windowType = `learning-method-${methodType.lm_id}-form` as any
    windowStore.openWindow({
      type: windowType,
      title: t('windows.learningMethodEditor.createWindowTitle', { name: methodType.name }),
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

  const saveEditedMethod = async (editingMethod: AdminLearningMethod | null) => {
    if (!editingMethod) return

    saveStatus.value = 'saving'

    try {
      const updated = await adminUpdateLearningMethod(editingMethod.method_id, {
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

      calculateStats()
      saveStatus.value = 'saved'
      setTimeout(() => { saveStatus.value = 'idle' }, 2000)
      return updated
    } catch (err: any) {
      console.error('Error updating learning method:', err)
      saveStatus.value = 'error'
      setTimeout(() => { saveStatus.value = 'idle' }, 3000)
      throw err
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
    if (!confirm(t('windows.learningMethodEditor.deleteConfirm'))) return

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

  const handleLearningMethodUpdate = () => {
    loadLearningMethods()
  }

  return {
    // State
    methods,
    methodTypes,
    loading,
    error,
    saveStatus,
    selectorGroup,
    selectedGroup,
    catalogActiveGroup,
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
    saveEditedMethod,
    togglePublish,
    deleteMethod,
    handleDragStart,
    handleDragOver,
    handleDrop,
    handleDragEnd,
    handleLearningMethodUpdate
  }
}
