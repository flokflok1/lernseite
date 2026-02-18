/**
 * useChapterTheoryActions - Business logic for chapter theory generation and actions.
 *
 * Extracts the generate, clipboard, and print logic from ChapterTheoryView.
 *
 * @param deps.chapterId - Getter for current chapter ID
 * @param deps.theoryMgmt - Theory management composable instance
 * @param deps.onGenerated - Callback when a theory is generated
 */

import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/infrastructure/api/http'
import type { ChapterTheoryActions, TheoryStyle } from './chapter-theory.types'

interface UseChapterTheoryActionsDeps {
  getChapterId: () => string | undefined
  theoryMgmt: {
    selectedTheoryId: { value: string | null }
    selectedTheory: { value: { overview: string; learningGoals?: string[]; concepts?: { name: string; description: string }[]; terms?: { term: string; definition: string }[] } | null }
    currentTheoryTitle: { value: string }
    currentTheoryStyle: { value: string }
    loadChapterTheories: (chapterId: string) => Promise<unknown>
    selectTheory: (theoryId: string) => Promise<unknown>
  }
  onGenerated?: (theoryId: string) => void
}

export function useChapterTheoryActions(deps: UseChapterTheoryActionsDeps): ChapterTheoryActions {
  const { t } = useI18n()

  const showCreateForm = ref(false)
  const newTitle = ref('')
  const selectedStyle = ref<TheoryStyle>('standard')
  const generateWithAudio = ref(false)
  const isGenerating = ref(false)
  const localError = ref<string | null>(null)

  async function generateNewTheory(): Promise<void> {
    const chapterId = deps.getChapterId()
    if (!chapterId) return

    isGenerating.value = true
    localError.value = null

    try {
      const response = await http.post('/admin/ai/generate-chapter-theory', {
        chapter_id: chapterId,
        style: selectedStyle.value,
        title: newTitle.value || undefined,
        generate_tts: generateWithAudio.value
      })

      if (response.data.success) {
        await deps.theoryMgmt.loadChapterTheories(chapterId)
        showCreateForm.value = false
        newTitle.value = ''

        const newTheoryId = response.data.data?.theory_id
        if (newTheoryId) {
          await deps.theoryMgmt.selectTheory(newTheoryId)
          deps.onGenerated?.(newTheoryId)
        }
      } else {
        throw new Error(response.data.error?.message || t('chapterTheoryView.generationFailed'))
      }
    } catch (err: any) {
      console.error('Theory generation failed:', err)
      localError.value = err.response?.data?.error?.message || err.message || t('chapterTheoryView.generationError')
    } finally {
      isGenerating.value = false
    }
  }

  function regenerateTheory(): void {
    if (deps.theoryMgmt.selectedTheoryId.value) {
      selectedStyle.value = (deps.theoryMgmt.currentTheoryStyle.value as TheoryStyle) || 'standard'
      showCreateForm.value = true
    }
  }

  function copyToClipboard(): void {
    const theory = deps.theoryMgmt.selectedTheory.value
    if (!theory) return

    const content = [
      `# ${deps.theoryMgmt.currentTheoryTitle.value}`,
      '',
      theory.overview,
      '',
      t('chapterTheoryView.clipboard.learningGoals'),
      ...(theory.learningGoals || []).map((g: string) => `- ${g}`),
      '',
      t('chapterTheoryView.clipboard.concepts'),
      ...(theory.concepts || []).map((c: { name: string; description: string }) => `### ${c.name}\n${c.description}`),
      '',
      t('chapterTheoryView.clipboard.terms'),
      ...(theory.terms || []).map((term: { term: string; definition: string }) => `**${term.term}**: ${term.definition}`)
    ].join('\n')

    navigator.clipboard.writeText(content)
  }

  function printTheory(): void {
    window.print()
  }

  function clearError(): void {
    localError.value = null
  }

  return {
    showCreateForm,
    newTitle,
    selectedStyle,
    generateWithAudio,
    isGenerating,
    localError,
    generateNewTheory,
    regenerateTheory,
    copyToClipboard,
    printTheory,
    clearError
  }
}
