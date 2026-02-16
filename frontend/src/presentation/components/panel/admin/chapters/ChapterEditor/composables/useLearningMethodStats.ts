/**
 * useLearningMethodStats Composable
 * Handles loading learning methods and calculating statistics
 */

import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { usePanelStore } from '@/application/stores/modules/workspace'
import {
  adminGetChapterLearningMethods,
  adminGetLearningMethodTypes,
  type AdminLearningMethod,
  type LearningMethodType
} from '@/application/services/api/panel-admin'
import type { MethodGroupStats, GroupInfo } from '../types'

export function useLearningMethodStats() {
  const panelStore = usePanelStore()
  const { t } = useI18n()

  // State
  const learningMethods = ref<AdminLearningMethod[]>([])
  const methodTypes = ref<LearningMethodType[]>([])
  const loadingMethods = ref(false)

  // Learning method stats per group
  const methodStats = ref<Record<string, MethodGroupStats>>({
    A: { total: 8, active: 0, published: 0 },
    B: { total: 11, active: 0, published: 0 },
    C: { total: 8, active: 0, published: 0 },
    D: { total: 6, active: 0, published: 0 }
  })

  /**
   * Load learning methods stats
   */
  const loadLearningMethodsStats = async (chapterId: string, isNewChapter: boolean) => {
    if (isNewChapter || !chapterId) return

    loadingMethods.value = true
    try {
      const [methodsResponse, typesData] = await Promise.all([
        adminGetChapterLearningMethods(chapterId),
        adminGetLearningMethodTypes()
      ])

      learningMethods.value = methodsResponse.learning_methods
      methodTypes.value = typesData.types

      // Calculate stats per group
      const stats: Record<string, MethodGroupStats> = {
        A: { total: 0, active: 0, published: 0 },
        B: { total: 0, active: 0, published: 0 },
        C: { total: 0, active: 0, published: 0 },
        D: { total: 0, active: 0, published: 0 }
      }

      // Count total types per group
      methodTypes.value.forEach(mt => {
        if (stats[mt.group]) {
          stats[mt.group].total++
        }
      })

      // Count active methods per group (methods in this chapter)
      learningMethods.value.forEach(method => {
        const type = methodTypes.value.find(t => t.lm_id === method.method_type)
        if (type && stats[type.group]) {
          stats[type.group].active++
          if (method.published) {
            stats[type.group].published++
          }
        }
      })

      methodStats.value = stats
    } catch (err) {
      console.error('Error loading learning methods stats:', err)
    } finally {
      loadingMethods.value = false
    }
  }

  /**
   * Get group info (name, colors, tier)
   */
  const getGroupInfo = (group: string): GroupInfo => {
    const groupNames: Record<string, string> = {
      A: t('features.chapterEditor.groups.A'),
      B: t('features.chapterEditor.groups.B'),
      C: t('features.chapterEditor.groups.C'),
      D: t('features.chapterEditor.groups.D')
    }
    const groupColors: Record<string, { bg: string; text: string }> = {
      A: { bg: 'var(--color-info-bg, #dbeafe)', text: 'var(--color-info-text, #1e40af)' },
      B: { bg: 'var(--color-success-bg, #dcfce7)', text: 'var(--color-success-text, #15803d)' },
      C: { bg: 'var(--color-warning-bg, #fef3c7)', text: 'var(--color-warning-text, #92400e)' },
      D: { bg: 'var(--color-premium-bg, #f3e8ff)', text: 'var(--color-premium-text, #6b21a8)' }
    }
    const groupTiers: Record<string, string> = {
      A: 'Basic',
      B: 'Basic',
      C: 'Premium',
      D: 'Pro'
    }
    return {
      name: groupNames[group] || group,
      colors: groupColors[group] || groupColors.A,
      tier: groupTiers[group] || 'Basic'
    }
  }

  /**
   * Open learning methods editor panel
   */
  const openLearningMethodsEditor = (courseId: string, chapterId: string, chapterTitle: string, isNewChapter: boolean, preSelectedGroup?: string) => {
    if (isNewChapter || !chapterId) {
      alert(t('features.chapterEditor.methods.saveFirstAlert'))
      return
    }

    panelStore.openPanel({
      type: 'admin-learning-method-editor',
      title: t('features.chapterEditor.methods.panelTitle', { title: chapterTitle || t('features.chapterEditor.tabs.info') }),
      icon: '🎯',
      payload: {
        courseId: courseId,
        courseTitle: '',
        chapterId: chapterId,
        chapterTitle: chapterTitle,
        preSelectedGroup
      },
      preferredPosition: { x: 150, y: 50 },
      size: { width: 750, height: 600 }
    })
  }

  return {
    // State
    learningMethods,
    methodTypes,
    loadingMethods,
    methodStats,

    // Methods
    loadLearningMethodsStats,
    getGroupInfo,
    openLearningMethodsEditor
  }
}
