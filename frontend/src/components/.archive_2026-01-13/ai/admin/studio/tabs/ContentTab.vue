<!--
  Content Tab - Lesson Content Editor

  Layout: Drei-Spalten wie ExamsTab
  - Links: Content-Typen & Versionen
  - Mitte: Editor
  - Rechts: Teaching Steps & Aktionen
-->

<template>
  <div class="content-tab">
    <!-- No Lesson Selected -->
    <div v-if="!lesson" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>{{ $t('windows.aiStudioContent.emptyTitle') }}</h3>
      <p>{{ $t('windows.aiStudioContent.emptyText') }}</p>
    </div>

    <!-- Main Content -->
    <div v-else class="content-main">
      <!-- Header -->
      <ContentHeader
        :lesson-title="lesson.title"
        :chapter-title="chapter?.title || ''"
        :word-count="wordCount"
        :steps-count="teachingSteps.length"
      />

      <!-- Three-Column Layout -->
      <div class="main-layout">
        <!-- Left: Content Types -->
        <TypesPanel
          :content-types="contentTypes"
          v-model:selected-type="selectedContentType"
          :lesson-type="lesson.lm_type || 'LM00'"
          :has-content="hasContent"
          @back="$emit('back-to-chapter')"
        />

        <!-- Middle: Editor -->
        <EditorPanel
          v-model:content="contentText"
          :content-type-name="getContentTypeName(selectedContentType)"
          :word-count="wordCount"
          :character-count="characterCount"
          :is-generating="isGenerating"
          :is-saving="isSaving"
          @generate="generateContent"
          @save="saveContent"
          @reset="resetContent"
        />

        <!-- Right: Teaching Steps -->
        <TeachingStepsPanel
          :steps="teachingSteps"
          :is-generating="isGenerating"
          @add="addTeachingStep"
          @remove="removeTeachingStep"
          @generate="generateTeachingSteps"
          @update="updateTeachingStep"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ContentHeader, TypesPanel, EditorPanel, TeachingStepsPanel } from '@/components/studio/assessment/admin/settings/exams'

const { t } = useI18n()

interface Lesson {
  lesson_id: string
  title: string
  lm_type?: string
  content?: Record<string, unknown>
}

interface Chapter {
  chapter_id: string
  title: string
}

interface Course {
  course_id: string
  title: string
}

interface TeachingStep {
  title: string
  speech: string
  animation: string
  duration: string
  whiteboard?: unknown[]
}

interface Props {
  lesson?: Lesson | null
  chapter?: Chapter | null
  course?: Course | null
}

const props = withDefaults(defineProps<Props>(), {
  lesson: null,
  chapter: null,
  course: null
})

const emit = defineEmits<{
  (e: 'save', data: { content: string; teachingSteps: TeachingStep[] }): void
  (e: 'back-to-chapter'): void
}>()

// State
const contentText = ref('')
const selectedContentType = ref('theory')
const teachingSteps = ref<TeachingStep[]>([])
const isGenerating = ref(false)
const isSaving = ref(false)
const lastSaved = ref<string | null>(null)

// Content Types - computed to use i18n
const contentTypes = computed(() => [
  { id: 'theory', name: t('windows.aiStudioContent.theory'), emoji: '📚' },
  { id: 'example', name: t('windows.aiStudioContent.example'), emoji: '💡' },
  { id: 'exercise', name: t('windows.aiStudioContent.exercise'), emoji: '✏️' },
  { id: 'summary', name: t('windows.aiStudioContent.summary'), emoji: '📋' }
])

// Computed
const wordCount = computed(() => {
  return contentText.value.trim().split(/\s+/).filter(w => w).length
})

const characterCount = computed(() => {
  return contentText.value.length
})

const hasContent = computed(() => {
  return contentText.value.trim().length > 0 || teachingSteps.value.length > 0
})

// Get content type name
function getContentTypeName(typeId: string): string {
  const type = contentTypes.value.find(ct => ct.id === typeId)
  return type ? type.name : t('windows.aiStudioContent.content')
}

// Methods
function addTeachingStep() {
  teachingSteps.value.push({
    title: t('windows.aiStudioContent.stepN', { n: teachingSteps.value.length + 1 }),
    speech: '',
    animation: 'talking',
    duration: '0:30'
  })
}

function removeTeachingStep(index: number) {
  teachingSteps.value.splice(index, 1)
}

function updateTeachingStep(index: number, field: string, value: string) {
  if (teachingSteps.value[index]) {
    (teachingSteps.value[index] as Record<string, unknown>)[field] = value
  }
}

async function generateContent() {
  if (!props.lesson) return
  isGenerating.value = true

  try {
    // TODO: API call to generate content
    await new Promise(resolve => setTimeout(resolve, 2000))
    contentText.value = `# ${props.lesson.title}\n\n## Einführung\n\nHier kommt der generierte Inhalt für die Lektion...\n\n## Hauptteil\n\n...\n\n## Zusammenfassung\n\n...`
  } catch (error) {
    console.error('Content generation failed:', error)
  } finally {
    isGenerating.value = false
  }
}

async function generateTeachingSteps() {
  isGenerating.value = true

  try {
    // TODO: API call to generate teaching steps
    await new Promise(resolve => setTimeout(resolve, 1500))
    teachingSteps.value = [
      { title: 'Einführung', speech: 'Willkommen zu dieser Lektion...', animation: 'talking', duration: '0:30' },
      { title: 'Hauptkonzept', speech: 'Das wichtigste Konzept ist...', animation: 'pointing', duration: '1:00' },
      { title: 'Beispiel', speech: 'Schauen wir uns ein Beispiel an...', animation: 'gesture', duration: '1:30' },
      { title: 'Zusammenfassung', speech: 'Fassen wir zusammen...', animation: 'talking', duration: '0:30' }
    ]
  } catch (error) {
    console.error('Teaching steps generation failed:', error)
  } finally {
    isGenerating.value = false
  }
}

async function saveContent() {
  isSaving.value = true

  try {
    // TODO: API call to save content
    await new Promise(resolve => setTimeout(resolve, 500))
    emit('save', { content: contentText.value, teachingSteps: teachingSteps.value })
    lastSaved.value = new Date().toLocaleTimeString('de-DE')
  } catch (error) {
    console.error('Save failed:', error)
  } finally {
    isSaving.value = false
  }
}

function resetContent() {
  if (confirm(t('windows.aiStudioContent.confirmReset'))) {
    contentText.value = ''
    teachingSteps.value = []
    lastSaved.value = null
  }
}

// Watch for lesson changes
watch(() => props.lesson, (newLesson) => {
  if (newLesson) {
    contentText.value = ''
    teachingSteps.value = []
    lastSaved.value = null
  }
}, { immediate: true })
</script>

<style scoped>
.content-tab {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1rem;
  color: var(--color-text-secondary);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: var(--color-text-primary);
  margin: 0 0 0.5rem;
}

.empty-state p { margin: 0; }

/* Main Content */
.content-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  overflow: hidden;
}

/* Three-Column Layout */
.main-layout {
  display: grid;
  grid-template-columns: 240px 1fr 280px;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
}
</style>
