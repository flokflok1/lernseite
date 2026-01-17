/**
 * useTabManagement - Tab State & Configuration
 * ==============================================
 * Manages active tab state and provides i18n-aware tab configuration
 */
import { ref, computed, readonly, type ComputedRef, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'

export interface TabConfig {
  id: string
  icon: string
  label: string
  badge?: string | number
  badgeColor?: string
}

export function useTabManagement(kursBuilderRef?: Ref<any>) {
  const { t } = useI18n()

  // State
  const activeTab = ref('builder') // Default to Kurs-Builder tab

  // Computed
  const tabs: ComputedRef<TabConfig[]> = computed(() => [
    {
      id: 'builder',
      icon: '📚',
      label: t('features.aiEditorPro.tabs.builder'),
      badge: kursBuilderRef?.value?.hasSession ? '●' : undefined,
      badgeColor: 'bg-green-500 text-white'
    },
    {
      id: 'tutor',
      icon: '🤖',
      label: t('features.aiEditorPro.tabs.tutor')
    },
    {
      id: 'methods',
      icon: '🧩',
      label: t('features.aiEditorPro.tabs.methods')
    },
    {
      id: 'exams',
      icon: '📝',
      label: t('features.aiEditorPro.tabs.exams')
    },
    {
      id: 'features',
      icon: '🎛️',
      label: t('features.aiEditorPro.tabs.features')
    },
    {
      id: 'prompts',
      icon: '📄',
      label: t('features.aiEditorPro.tabs.prompts')
    },
    {
      id: 'analytics',
      icon: '📊',
      label: t('features.aiEditorPro.tabs.analytics')
    },
    {
      id: 'settings',
      icon: '⚙️',
      label: t('features.aiEditorPro.tabs.settings')
    },
    {
      id: 'global',
      icon: '🌐',
      label: t('features.aiEditorPro.tabs.global')
    }
  ])

  // Methods
  function setActiveTab(tabId: string): void {
    activeTab.value = tabId
  }

  // Expose
  return {
    activeTab: readonly(activeTab),
    tabs,
    setActiveTab
  }
}
