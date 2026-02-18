/**
 * useKursBuilderActions - Context selection, analysis, theory, confirmation,
 * structure actions, file management, and tutor integration.
 *
 * Split from useKursBuilderTab for Quality Gate G01 compliance.
 */
import { ref, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/application/stores/modules/ui/window.store'
import { useTheoryManagement } from '@/application/composables/learning/useTheoryManagement'
import http from '@/infrastructure/api/http'
import { getActionsForEntity, getLMSuggestions, type LMSuggestion } from '@/application/services/api/learning'
import type {
  Course, ChatMessage, CourseFile, Chapter, Lesson,
  QuickAction, SelectedContext, PendingAction, DraftStructure, Session
} from './kursBuilder.types'

interface ActionsDeps {
  courseRef: Ref<Course | null>
  session: Ref<Session | null>
  chatMessages: Ref<ChatMessage[]>
  draftStructure: Ref<DraftStructure | null>
  sessionFiles: Ref<CourseFile[]>
  selectedFileIds: Ref<string[]>
  inputMessage: Ref<string>
  selectedMode: Ref<string>
  sendMessage: (msg: string, mode: string) => Promise<void>
}

/** Composable for KursBuilder context, analysis, confirmation, structure, files, and tutor. */
export function useKursBuilderActions(deps: ActionsDeps) {
  const { t } = useI18n()
  const windowStore = useWindowStore()
  const theoryMgmt = useTheoryManagement()

  const selectedContext = ref<SelectedContext | null>(null)
  const contextActionsLoading = ref(false)
  const contextActions = ref<QuickAction[]>([])
  const lmSuggestions = ref<LMSuggestion[]>([])
  const lmSuggestionsLoading = ref(false)
  const analyzingLessonId = ref<string | null>(null)
  const isAnalyzing = ref(false)
  const isGeneratingTheory = ref(false)
  const pendingAction = ref<PendingAction | null>(null)
  const confirmLoading = ref(false)
  const materialFileInput = ref<HTMLInputElement | null>(null)
  const isUploadingFile = ref(false)
  const selectedTheoryId = ref<string | null>(null)

  function addSystemMessage(content: string): void {
    deps.chatMessages.value.push({ role: 'assistant', content, timestamp: new Date().toISOString() })
  }

  async function selectChapterForChat(chapter: Chapter): Promise<void> {
    selectedContext.value = { type: 'chapter', id: chapter.id, title: chapter.title, data: chapter }
    lmSuggestions.value = []
    await Promise.all([loadContextActions('chapter'), theoryMgmt.loadChapterTheories(chapter.id)])
  }

  async function selectLessonForChat(chapter: Chapter, lesson: Lesson): Promise<void> {
    selectedContext.value = {
      type: 'lesson', id: lesson.id, title: lesson.title, data: lesson, parentChapter: chapter
    }
    await Promise.all([
      loadContextActions('lesson'), loadLMSuggestions(lesson, chapter),
      theoryMgmt.loadLessonExplanations(lesson.id)
    ])
  }

  async function loadContextActions(entityType: 'chapter' | 'lesson' | 'method'): Promise<void> {
    contextActionsLoading.value = true
    try {
      const actions = await getActionsForEntity(entityType)
      contextActions.value = actions?.length
        ? actions.map(a => ({
            action_id: a.action_id, action_key: a.action_key, label: a.label,
            icon: a.icon || '', prompt_template: a.prompt_template, mode: a.mode, color: a.color
          }))
        : []
    } catch {
      contextActions.value = []
    } finally {
      contextActionsLoading.value = false
    }
  }

  async function loadLMSuggestions(lesson: Lesson, chapter: Chapter): Promise<void> {
    lmSuggestionsLoading.value = true
    lmSuggestions.value = []
    try {
      const existingLmIds = (lesson.methods || [])
        .map(m => {
          const match = m.type?.match(/LM(\d+)/i)
          return match ? parseInt(match[1]) : null
        })
        .filter((id): id is number => id !== null)

      const result = await getLMSuggestions({
        lesson_title: lesson.title,
        lesson_content: lesson.description || '',
        chapter_title: chapter.title,
        course_title: deps.courseRef.value?.title || '',
        existing_lm_ids: existingLmIds,
        max_suggestions: 6
      })
      lmSuggestions.value = result.suggestions || []
    } catch {
      lmSuggestions.value = []
    } finally {
      lmSuggestionsLoading.value = false
    }
  }

  function clearContext(): void {
    selectedContext.value = null
    contextActions.value = []
    lmSuggestions.value = []
    theoryMgmt.reset()
  }

  function sendContextAction(action: QuickAction): void {
    let prompt = action.prompt_template
    if (selectedContext.value) {
      prompt = prompt.replace('{{context_title}}', selectedContext.value.title)
        .replace('{{context_type}}', selectedContext.value.type)
    }
    deps.selectedMode.value = action.mode || ''
    deps.sendMessage(prompt, action.mode || '')
  }

  async function analyzeLessonWithFiles(chapter: Chapter, lesson: Lesson): Promise<void> {
    if (!deps.courseRef.value) return
    analyzingLessonId.value = lesson.id
    try {
      const response = await http.post('/admin/ai-studio/analyze-lesson', {
        course_id: deps.courseRef.value.course_id, chapter_id: chapter.id,
        chapter_title: chapter.title, lesson_id: lesson.id, lesson_title: lesson.title,
        file_ids: deps.selectedFileIds.value, request_type: 'lm_recommendation'
      })
      if (response.data.success) {
        const analysis = response.data.data
        addSystemMessage(
          `**${t('kursBuilder.messages.analysisFor', { name: lesson.title })}**\n\n${analysis.summary || ''}\n\n` +
          `**${t('kursBuilder.messages.recommendedMethods')}**\n` +
          (analysis.recommended_lms || []).map((lm: any) => `- ${lm.name}: ${lm.reason}`).join('\n')
        )
        if (analysis.recommended_lms?.length) {
          lmSuggestions.value = analysis.recommended_lms.map((lm: any) => ({
            lm_id: lm.lm_id, name: lm.name, reason: lm.reason,
            confidence: lm.confidence || 0.8
          }))
        }
      }
    } catch {
      addSystemMessage(t('kursBuilder.messages.analysisError', { name: lesson.title }))
    } finally {
      analyzingLessonId.value = null
    }
  }

  async function analyzeSelectedContext(): Promise<void> {
    if (!selectedContext.value || !deps.courseRef.value) return
    isAnalyzing.value = true
    try {
      const isChapter = selectedContext.value.type === 'chapter'
      const response = await http.post('/admin/ai-studio/analyze-lesson', {
        course_id: deps.courseRef.value.course_id,
        chapter_id: isChapter ? selectedContext.value.id : selectedContext.value.parentChapter?.id,
        chapter_title: isChapter ? selectedContext.value.title : selectedContext.value.parentChapter?.title,
        lesson_id: isChapter ? null : selectedContext.value.id,
        lesson_title: isChapter ? null : selectedContext.value.title,
        file_ids: deps.selectedFileIds.value,
        request_type: 'lm_recommendation'
      })
      if (response.data.success) {
        const analysis = response.data.data
        const contextName = isChapter
          ? `${t('kursBuilder.chapter')} "${selectedContext.value.title}"`
          : `${t('kursBuilder.lesson')} "${selectedContext.value.title}"`
        addSystemMessage(
          `**${t('kursBuilder.messages.analysisFor', { name: contextName })}**\n\n${analysis.summary || ''}` +
          (deps.selectedFileIds.value.length
            ? `\n\n${t('kursBuilder.messages.filesAnalyzed', { count: deps.selectedFileIds.value.length })}`
            : '')
        )
        if (!isChapter && analysis.recommended_lms?.length) {
          lmSuggestions.value = analysis.recommended_lms.map((lm: any) => ({
            lm_id: lm.lm_id, name: lm.name, reason: lm.reason,
            confidence: lm.confidence || 0.8, icon: lm.icon || '', group: lm.group || 'B'
          }))
        }
      }
    } catch {
      addSystemMessage(t('kursBuilder.messages.analysisErrorGeneric'))
    } finally {
      isAnalyzing.value = false
    }
  }

  async function generateTheory(): Promise<void> {
    if (!selectedContext.value || !deps.courseRef.value) return
    isGeneratingTheory.value = true
    try {
      const isChapter = selectedContext.value.type === 'chapter'
      const prompt = isChapter
        ? `Erstelle eine Zusammenfassung für das Kapitel "${selectedContext.value.title}".`
        : `Erstelle ein detailliertes Theorieblatt für die Lektion "${selectedContext.value.title}".`
      deps.selectedMode.value = isChapter ? 'chapter_summary' : 'lesson_theory'
      await deps.sendMessage(prompt, deps.selectedMode.value)
      addSystemMessage(
        t('kursBuilder.messages.generatingTheory', { title: selectedContext.value.title })
      )
    } catch {
      addSystemMessage(t('kursBuilder.messages.generatingTheoryError'))
    } finally {
      isGeneratingTheory.value = false
    }
  }

  function createLMFromSuggestion(suggestion: LMSuggestion): void {
    const prompt = `Erstelle eine Lernmethode vom Typ "${suggestion.name}" (LM${String(suggestion.lm_id).padStart(2, '0')}) für die Lektion "${selectedContext.value?.title}". Begründung: ${suggestion.reason}`
    deps.selectedMode.value = 'method'
    deps.sendMessage(prompt, 'method')
  }

  // ---- Confirmation Flow ----

  function checkForGeneratedContent(response: any): PendingAction | null {
    if (!response.generated_content || !response.requires_confirmation) return null
    const entity = response.output_entity || 'chapter'
    let previewText = ''

    if (entity === 'chapter' && response.generated_content.title) {
      previewText = `Neues Kapitel: "${response.generated_content.title}"\n\n${response.generated_content.description || ''}` +
        (response.generated_content.lessons?.length
          ? `\n\n${response.generated_content.lessons.length} Lektionen`
          : '')
    } else if (entity === 'lesson' && response.generated_content.title) {
      previewText = `Neue Lektion: "${response.generated_content.title}"\n\n${response.generated_content.description || ''}`
    } else {
      previewText = typeof response.generated_content === 'string'
        ? response.generated_content.slice(0, 300)
        : JSON.stringify(response.generated_content, null, 2).slice(0, 300)
    }

    return {
      type: 'create', entity: entity as any, actionKey: response.action_key || 'unknown',
      generatedData: response.generated_content, previewText,
      parentChapter: selectedContext.value?.parentChapter,
      session_id: response.session_id
    }
  }

  async function confirmPendingAction(): Promise<void> {
    if (!pendingAction.value || !deps.session.value) return
    confirmLoading.value = true
    try {
      const action = pendingAction.value
      if (action.entity === 'chapter' && action.generatedData) {
        if (!deps.draftStructure.value) deps.draftStructure.value = { chapters: [] }
        if (!deps.draftStructure.value.chapters) deps.draftStructure.value.chapters = []
        const newChapter: Chapter = {
          id: `ch-${Date.now()}`,
          title: action.generatedData.title || 'Neues Kapitel',
          description: action.generatedData.description || '',
          lessons: (action.generatedData.lessons || []).map((l: any, i: number) => ({
            id: `ls-${Date.now()}-${i}`,
            title: l.title || `Lektion ${i + 1}`,
            description: l.description || '',
            methods: l.methods || []
          }))
        }
        deps.draftStructure.value.chapters.push(newChapter)
        deps.chatMessages.value.push({
          role: 'assistant',
          content: `Kapitel "${newChapter.title}" wurde erstellt mit ${newChapter.lessons?.length || 0} Lektionen.`
        })
      } else if (action.entity === 'lesson' && action.generatedData && action.parentChapter) {
        const chapter = deps.draftStructure.value?.chapters?.find(
          c => c.id === action.parentChapter?.id
        )
        if (chapter) {
          if (!chapter.lessons) chapter.lessons = []
          const newLesson: Lesson = {
            id: `ls-${Date.now()}`,
            title: action.generatedData.title || 'Neue Lektion',
            description: action.generatedData.description || '',
            content: action.generatedData.content,
            methods: action.generatedData.methods || []
          }
          chapter.lessons.push(newLesson)
          deps.chatMessages.value.push({
            role: 'assistant',
            content: `Lektion "${newLesson.title}" wurde zum Kapitel "${chapter.title}" hinzugefügt.`
          })
        }
      }
      pendingAction.value = null
    } catch (err: any) {
      deps.chatMessages.value.push({
        role: 'assistant',
        content: 'Fehler beim Speichern: ' + (err.message || 'Unbekannt'),
        error: true
      })
    } finally {
      confirmLoading.value = false
    }
  }

  function rejectPendingAction(): void {
    deps.chatMessages.value.push({ role: 'assistant', content: 'Aktion wurde verworfen.' })
    pendingAction.value = null
  }

  function modifyPendingAction(): void {
    deps.inputMessage.value = 'Bitte ändere das Ergebnis. Folgende Anpassungen: '
    pendingAction.value = null
  }

  // ---- Structure Actions ----

  function openChapterPreview(chapter: Chapter): void {
    windowStore.openWindow({
      type: 'admin-chapter-preview',
      title: `Kapitel: ${chapter.title}`,
      icon: '',
      payload: {
        chapter: {
          chapter_id: chapter.id, title: chapter.title,
          description: chapter.description, lessons: chapter.lessons,
          created_at: new Date().toISOString()
        }
      },
      size: { width: 650, height: 700 }
    })
  }

  function openLessonPreview(chapter: Chapter, lesson: Lesson): void {
    const lessonIndex = chapter.lessons?.findIndex(l => l.id === lesson.id) ?? 0
    windowStore.openWindow({
      type: 'admin-lesson-preview',
      title: `Vorschau: ${lesson.title}`,
      icon: '',
      payload: {
        lesson: {
          lesson_id: lesson.id, title: lesson.title, description: lesson.description,
          content: lesson.content, duration_minutes: lesson.duration_minutes,
          methods: lesson.methods
        },
        chapter: { chapter_id: chapter.id, title: chapter.title },
        position: `${lessonIndex + 1}/${chapter.lessons?.length ?? 1}`
      },
      size: { width: 600, height: 700 }
    })
  }

  function editChapter(chapter: Chapter): void {
    console.log('Edit chapter:', chapter.id)
  }

  function editLesson(chapter: Chapter, lesson: Lesson): void {
    console.log('Edit lesson:', lesson.id, 'in chapter:', chapter.id)
  }

  function deleteChapter(chapterId: string, chapterIndex: number): void {
    if (!confirm('Kapitel wirklich löschen?') || !deps.draftStructure.value?.chapters) return
    deps.draftStructure.value.chapters.splice(chapterIndex, 1)
  }

  function deleteLesson(
    chapterId: string, chapterIndex: number,
    lessonId: string, lessonIndex: number
  ): void {
    if (!confirm('Lektion wirklich löschen?') ||
        !deps.draftStructure.value?.chapters?.[chapterIndex]?.lessons) return
    deps.draftStructure.value.chapters[chapterIndex].lessons!.splice(lessonIndex, 1)
  }

  // ---- File Management ----

  function clearFileSelection(): void {
    deps.selectedFileIds.value = []
  }

  function openFilePreview(file: CourseFile): void {
    windowStore.openWindow({
      type: 'admin-file-preview', title: `Vorschau: ${file.name}`,
      icon: '', payload: { file }, size: { width: 800, height: 600 }
    })
  }

  function triggerFileUpload(): void {
    materialFileInput.value?.click()
  }

  async function handleMaterialUpload(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement
    if (!input.files?.length || !deps.courseRef.value) return
    isUploadingFile.value = true
    try {
      for (const file of Array.from(input.files)) {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('file_category', 'material')
        await http.post(
          `/admin/courses/${deps.courseRef.value.course_id}/files`,
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )
      }
    } catch (err) {
      console.error('File upload failed:', err)
    } finally {
      isUploadingFile.value = false
      input.value = ''
    }
  }

  // ---- Tutor Integration ----

  function openTheoryInTutor(theory: { theoryId: string }): void {
    windowStore.openWindow({
      type: 'admin-ai-studio', title: 'KI-Studio: Tutor', icon: '',
      payload: {
        tab: 'tutor', chapter: selectedContext.value?.data, theoryId: theory.theoryId
      },
      size: { width: 1200, height: 800 }
    })
  }

  function openExplanationInTutor(expl: { explanationId: string }): void {
    windowStore.openWindow({
      type: 'admin-ai-studio', title: 'KI-Studio: Tutor', icon: '',
      payload: {
        tab: 'tutor', lesson: selectedContext.value?.data,
        chapter: selectedContext.value?.parentChapter,
        explanationId: expl.explanationId
      },
      size: { width: 1200, height: 800 }
    })
  }

  return {
    // State
    selectedContext, contextActionsLoading, contextActions, lmSuggestions,
    lmSuggestionsLoading, selectedTheoryId, analyzingLessonId, isAnalyzing,
    isGeneratingTheory, pendingAction, confirmLoading, materialFileInput,
    isUploadingFile,
    // Theory (from theoryMgmt)
    chapterTheories: theoryMgmt.chapterTheories,
    lessonExplanations: theoryMgmt.lessonExplanations,
    isLoadingTheories: theoryMgmt.isLoading,
    // Context & Analysis
    selectChapterForChat, selectLessonForChat, clearContext, sendContextAction,
    analyzeSelectedContext, analyzeLessonWithFiles, generateTheory, createLMFromSuggestion,
    // Confirmation
    checkForGeneratedContent, confirmPendingAction, rejectPendingAction, modifyPendingAction,
    // Structure
    openChapterPreview, openLessonPreview, editChapter, editLesson, deleteChapter, deleteLesson,
    // Files
    clearFileSelection, openFilePreview, triggerFileUpload, handleMaterialUpload,
    // Tutor
    openTheoryInTutor, openExplanationInTutor
  }
}
