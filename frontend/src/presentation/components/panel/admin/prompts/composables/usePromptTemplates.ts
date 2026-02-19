/**
 * usePromptTemplates Composable
 *
 * Manages prompt template state, filtering, and all CRUD API operations
 * for the PanelPromptsPage.
 */

import { ref, computed, type Ref } from 'vue'
import http from '@/infrastructure/api/http'
import type { PromptTemplate, PromptStats, PromptPreviewData } from '../types/prompt.types.ts'
import { createEmptyTemplate } from '../types/prompt.types.ts'

export function usePromptTemplates() {
  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  const templates = ref<PromptTemplate[]>([])
  const categories = ref<string[]>([])
  const availableStyles = ref<string[]>(['standard', 'adhs', 'detailed', 'short', 'exam_focus'])
  const loading = ref(true)
  const error = ref('')
  const searchQuery = ref('')
  const selectedCategory = ref('')
  const selectedStyle = ref('')

  const showEditModal = ref(false)
  const showPreviewModal = ref(false)
  const showDeleteModal = ref(false)
  const editingTemplate = ref<PromptTemplate>(createEmptyTemplate())
  const previewData = ref<PromptPreviewData | null>(null)
  const deleteTarget = ref<PromptTemplate | null>(null)
  const saving = ref(false)
  const deleting = ref(false)

  const stats: Ref<PromptStats> = ref({
    total: 0,
    usageCount: 0,
    tokensUsed: 0
  })

  // ---------------------------------------------------------------------------
  // Computed
  // ---------------------------------------------------------------------------
  const filteredTemplates = computed(() => {
    let result = templates.value

    if (selectedCategory.value) {
      result = result.filter(t => t.category === selectedCategory.value)
    }

    if (selectedStyle.value) {
      result = result.filter(t => t.style === selectedStyle.value)
    }

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(t =>
        t.name.toLowerCase().includes(query) ||
        t.code.toLowerCase().includes(query) ||
        (t.description?.toLowerCase().includes(query))
      )
    }

    return result
  })

  // ---------------------------------------------------------------------------
  // API Functions
  // ---------------------------------------------------------------------------
  async function loadTemplates(): Promise<void> {
    loading.value = true
    error.value = ''

    try {
      const response = await http.get('/panel/prompts')
      if (response.data.success) {
        templates.value = response.data.templates || response.data.data || []
        stats.value.total = templates.value.length
        categories.value = [...new Set(templates.value.map(t => t.category))]
      }
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Fehler beim Laden der Templates'
      console.error('Error loading templates:', e)
    } finally {
      loading.value = false
    }
  }

  async function loadStats(): Promise<void> {
    try {
      const response = await http.get('/panel/prompts/usage-stats')
      if (response.data.success) {
        const data = response.data.data
        stats.value.usageCount = data.total_usage || 0
        stats.value.tokensUsed = data.total_tokens || 0
      }
    } catch (e) {
      console.error('Error loading stats:', e)
    }
  }

  async function duplicateTemplate(template: PromptTemplate): Promise<void> {
    try {
      const response = await http.post(`/panel/prompts/${template.template_id}/duplicate`)
      if (response.data.success) {
        await loadTemplates()
      }
    } catch (e: any) {
      console.error('Error duplicating template:', e)
      alert('Fehler beim Duplizieren: ' + (e.response?.data?.error || e.message))
    }
  }

  async function previewTemplate(template: PromptTemplate): Promise<void> {
    try {
      const response = await http.post('/panel/prompts/preview', {
        template_id: template.template_id,
        variables: {
          chapter_title: 'IT1: Beschaffung & Kalkulation',
          course_title: 'AP1 Pruefungsvorbereitung',
          chapter_description: 'Grundlagen der Warenbeschaffung und Kalkulationsverfahren',
          lesson_titles: 'Bezugskalkulation, Verkaufskalkulation, Handelskalkulation',
          target_audience: 'Fachinformatiker Systemintegration (FISI)'
        }
      })

      if (response.data.success) {
        previewData.value = response.data.data
        showPreviewModal.value = true
      }
    } catch {
      previewData.value = {
        system_prompt: template.system_prompt,
        rendered_prompt: template.user_prompt
      }
      showPreviewModal.value = true
    }
  }

  async function deleteTemplate(): Promise<void> {
    if (!deleteTarget.value?.template_id) return

    deleting.value = true
    try {
      await http.delete(`/panel/prompts/${deleteTarget.value.template_id}`)
      await loadTemplates()
      showDeleteModal.value = false
      deleteTarget.value = null
    } catch (e: any) {
      console.error('Error deleting template:', e)
      alert('Fehler beim Loeschen: ' + (e.response?.data?.error || e.message))
    } finally {
      deleting.value = false
    }
  }

  async function saveTemplate(): Promise<void> {
    if (!editingTemplate.value.name || !editingTemplate.value.code) {
      alert('Name und Code sind erforderlich')
      return
    }

    saving.value = true
    try {
      const payload = {
        ...editingTemplate.value,
        title: editingTemplate.value.name,
        user_prompt_template: editingTemplate.value.user_prompt
      }

      if (editingTemplate.value.template_id) {
        await http.patch(`/panel/prompts/${editingTemplate.value.template_id}`, payload)
      } else {
        await http.post('/panel/prompts', payload)
      }

      await loadTemplates()
      closeModal()
    } catch (e: any) {
      console.error('Error saving template:', e)
      alert('Fehler beim Speichern: ' + (e.response?.data?.error || e.message))
    } finally {
      saving.value = false
    }
  }

  // ---------------------------------------------------------------------------
  // Modal Controls
  // ---------------------------------------------------------------------------
  function openCreateModal(): void {
    editingTemplate.value = createEmptyTemplate()
    showEditModal.value = true
  }

  function editTemplate(template: PromptTemplate): void {
    editingTemplate.value = {
      ...template,
      name: template.name || template.title || '',
      user_prompt: template.user_prompt || template.user_prompt_template || ''
    }
    showEditModal.value = true
  }

  function confirmDelete(template: PromptTemplate): void {
    deleteTarget.value = template
    showDeleteModal.value = true
  }

  function closeModal(): void {
    showEditModal.value = false
    editingTemplate.value = createEmptyTemplate()
  }

  function closePreview(): void {
    showPreviewModal.value = false
    previewData.value = null
  }

  // ---------------------------------------------------------------------------
  // Utility
  // ---------------------------------------------------------------------------
  function formatNumber(num: number): string {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
    return num.toString()
  }

  return {
    // State
    templates,
    categories,
    availableStyles,
    loading,
    error,
    searchQuery,
    selectedCategory,
    selectedStyle,
    showEditModal,
    showPreviewModal,
    showDeleteModal,
    editingTemplate,
    previewData,
    deleteTarget,
    saving,
    deleting,
    stats,
    filteredTemplates,

    // Actions
    loadTemplates,
    loadStats,
    duplicateTemplate,
    previewTemplate,
    deleteTemplate,
    saveTemplate,
    openCreateModal,
    editTemplate,
    confirmDelete,
    closeModal,
    closePreview,
    formatNumber,
  }
}
