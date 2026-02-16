<!--
  CourseStructurePreview.vue

  Baumansicht der Kursstruktur im KI-Kurs-Builder.
  Zeigt Kapitel, Lektionen und Lernmethoden hierarchisch an.
  Erlaubt Auswahl für Detail-Ansicht.
-->

<template>
  <div class="course-structure-preview">
    <!-- Header -->
    <div class="panel-header">
      <span class="panel-icon">📚</span>
      <span class="panel-title">Kursstruktur</span>
      <span v-if="totalItems" class="item-count">{{ totalItems }}</span>
    </div>

    <!-- Empty State -->
    <div v-if="!structure?.chapters?.length" class="empty-state">
      <span class="empty-icon">📋</span>
      <p>Noch keine Struktur</p>
      <p class="hint">Nutze den Chat um Kapitel zu erstellen.</p>
    </div>

    <!-- Tree View -->
    <div v-else class="tree-container">
      <div
        v-for="chapter in structure.chapters"
        :key="chapter.id"
        class="tree-node chapter-node"
      >
        <!-- Chapter Header -->
        <div
          class="node-header"
          :class="{ expanded: expandedChapters.has(chapter.id), selected: selectedId === chapter.id }"
          @click="toggleChapter(chapter.id)"
        >
          <span class="expand-icon">{{ expandedChapters.has(chapter.id) ? '▼' : '▶' }}</span>
          <span class="node-icon">📖</span>
          <span class="node-title">{{ chapter.title }}</span>
          <span class="node-count">{{ chapter.lessons?.length || 0 }}</span>
        </div>

        <!-- Lessons -->
        <div v-if="expandedChapters.has(chapter.id)" class="node-children">
          <div
            v-for="lesson in chapter.lessons"
            :key="lesson.id"
            class="tree-node lesson-node"
          >
            <!-- Lesson Header -->
            <div
              class="node-header"
              :class="{ expanded: expandedLessons.has(lesson.id), selected: selectedId === lesson.id }"
              @click="toggleLesson(lesson.id)"
            >
              <span class="expand-icon">{{ lesson.methods?.length ? (expandedLessons.has(lesson.id) ? '▼' : '▶') : '○' }}</span>
              <span class="node-icon">📄</span>
              <span class="node-title">{{ lesson.title }}</span>
              <span v-if="lesson.methods?.length" class="node-count">{{ lesson.methods.length }}</span>
            </div>

            <!-- Methods -->
            <div v-if="expandedLessons.has(lesson.id) && lesson.methods?.length" class="node-children">
              <div
                v-for="method in lesson.methods"
                :key="method.id"
                class="tree-node method-node"
                :class="{ selected: selectedId === method.id }"
                @click="selectItem(method.id, 'method', method)"
              >
                <span class="method-icon">{{ getMethodIcon(method.type) }}</span>
                <span class="node-title">{{ method.title || getMethodName(method.type) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Footer -->
    <div v-if="structure?.chapters?.length" class="stats-footer">
      <span class="stat">
        <strong>{{ structure.chapters.length }}</strong> Kapitel
      </span>
      <span class="stat">
        <strong>{{ totalLessons }}</strong> Lektionen
      </span>
      <span class="stat">
        <strong>{{ totalMethods }}</strong> Methoden
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface LearningMethod {
  id: string
  type: string
  title?: string
  data?: Record<string, unknown>
}

interface Lesson {
  id: string
  title: string
  description?: string
  methods?: LearningMethod[]
}

interface Chapter {
  id: string
  title: string
  description?: string
  lessons?: Lesson[]
}

interface CourseStructure {
  chapters?: Chapter[]
}

const props = defineProps<{
  structure: CourseStructure | null
  selectedId?: string | null
}>()

const emit = defineEmits<{
  (e: 'select', payload: { id: string; type: 'chapter' | 'lesson' | 'method'; data: Chapter | Lesson | LearningMethod }): void
}>()

const expandedChapters = ref<Set<string>>(new Set())
const expandedLessons = ref<Set<string>>(new Set())

const totalLessons = computed(() => {
  if (!props.structure?.chapters) return 0
  return props.structure.chapters.reduce((sum, ch) => sum + (ch.lessons?.length || 0), 0)
})

const totalMethods = computed(() => {
  if (!props.structure?.chapters) return 0
  return props.structure.chapters.reduce((sum, ch) => {
    return sum + (ch.lessons?.reduce((lsum, l) => lsum + (l.methods?.length || 0), 0) || 0)
  }, 0)
})

const totalItems = computed(() => {
  const chapters = props.structure?.chapters?.length || 0
  return chapters + totalLessons.value + totalMethods.value
})

function toggleChapter(id: string) {
  if (expandedChapters.value.has(id)) {
    expandedChapters.value.delete(id)
  } else {
    expandedChapters.value.add(id)
  }
  const chapter = props.structure?.chapters?.find(c => c.id === id)
  if (chapter) {
    emit('select', { id, type: 'chapter', data: chapter })
  }
}

function toggleLesson(id: string) {
  if (expandedLessons.value.has(id)) {
    expandedLessons.value.delete(id)
  } else {
    expandedLessons.value.add(id)
  }
  // Find the lesson
  for (const chapter of props.structure?.chapters || []) {
    const lesson = chapter.lessons?.find(l => l.id === id)
    if (lesson) {
      emit('select', { id, type: 'lesson', data: lesson })
      break
    }
  }
}

function selectItem(id: string, type: 'chapter' | 'lesson' | 'method', data: Chapter | Lesson | LearningMethod) {
  emit('select', { id, type, data })
}

const methodIcons: Record<string, string> = {
  'calculator_tutorial': '🧮',
  'tool_tutorial': '🛠️',
  'step_by_step': '📋',
  'theory': '📖',
  'quiz': '❓',
  'flashcards': '🗂️',
  'exercise': '✏️',
  'exam': '🎓'
}

const methodNames: Record<string, string> = {
  'calculator_tutorial': 'Taschenrechner-Tutorial',
  'tool_tutorial': 'Tool-Tutorial',
  'step_by_step': 'Prozess-Anleitung',
  'theory': 'Theorieblatt',
  'quiz': 'Quiz',
  'flashcards': 'Karteikarten',
  'exercise': 'Übungsaufgabe',
  'exam': 'Prüfungssimulation'
}

function getMethodIcon(type: string): string {
  return methodIcons[type] || '📝'
}

function getMethodName(type: string): string {
  return methodNames[type] || type
}
</script>

<style scoped>
.course-structure-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.panel-icon { font-size: 1rem; }
.panel-title {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-primary);
}

.item-count {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 600;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
}

.empty-state .empty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.empty-state p { margin: 0.25rem 0; }
.empty-state .hint { font-size: 0.75rem; opacity: 0.7; }

.tree-container {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.tree-node {
  margin-bottom: 0.25rem;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s;
}

.node-header:hover {
  background: var(--color-surface-secondary);
}

.node-header.selected {
  background: var(--color-primary);
  color: white;
}

.node-header.selected .node-count {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.expand-icon {
  width: 1rem;
  font-size: 0.625rem;
  color: var(--color-text-secondary);
}

.node-icon {
  font-size: 0.875rem;
}

.node-title {
  flex: 1;
  font-size: 0.8125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-count {
  padding: 0.125rem 0.375rem;
  background: var(--color-surface);
  border-radius: 0.25rem;
  font-size: 0.625rem;
  color: var(--color-text-secondary);
}

.node-children {
  margin-left: 1.25rem;
  padding-left: 0.75rem;
  border-left: 1px solid var(--color-border);
}

.method-node {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.15s;
}

.method-node:hover {
  background: var(--color-surface-secondary);
}

.method-node.selected {
  background: var(--color-primary);
  color: white;
}

.method-icon {
  font-size: 0.75rem;
}

.method-node .node-title {
  font-size: 0.75rem;
}

.stats-footer {
  display: flex;
  gap: 1rem;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface-secondary);
}

.stat {
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
}

.stat strong {
  color: var(--color-text-primary);
}
</style>
