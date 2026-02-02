<!--
  StructurePanel - Course structure tree with drag & drop

  Displays the hierarchical course structure (chapters > lessons)
  with actions for preview, edit, delete, and AI chat context.
-->

<template>
  <div class="panel structure-panel">
    <div class="panel-header">
      <span class="panel-icon">📚</span>
      <span class="panel-title">Kursstruktur</span>
      <span v-if="stats.chapters > 0" class="panel-badge">{{ stats.chapters }}</span>
    </div>

    <div class="panel-content">
      <div v-if="!chapters?.length" class="panel-empty">
        <span>📋</span>
        <p>Noch keine Struktur</p>
      </div>

      <div v-else class="structure-tree">
        <div
          v-for="(chapter, chapterIndex) in chapters"
          :key="chapter.id"
          class="tree-chapter"
          :class="{ 'drag-over': dragOverChapterId === chapter.id }"
          draggable="true"
          @dragstart="handleChapterDragStart($event, chapterIndex)"
          @dragover.prevent="handleChapterDragOver($event, chapter.id)"
          @dragleave="handleChapterDragLeave"
          @drop="handleChapterDrop($event, chapterIndex)"
          @dragend="handleDragEnd"
        >
          <div class="chapter-header">
            <span
              class="expand-icon"
              @click.stop="toggleChapter(chapter.id)"
            >{{ expandedChapters.has(chapter.id) ? '▼' : '▶' }}</span>
            <span class="chapter-icon">📖</span>
            <span class="chapter-title" @click="toggleChapter(chapter.id)">{{ chapter.title }}</span>
            <span class="chapter-count">{{ chapter.lessons?.length || 0 }}</span>
            <div class="item-actions">
              <button
                @click.stop="$emit('select-chapter', chapter)"
                class="action-btn action-btn--primary"
                :title="$t('panel.actions.editWithAi')"
              >🤖</button>
              <button
                @click.stop="$emit('preview-chapter', chapter)"
                class="action-btn"
                :title="$t('panel.actions.preview')"
              >👁️</button>
              <button
                @click.stop="$emit('edit-chapter', chapter)"
                class="action-btn"
                :title="$t('panel.actions.edit')"
              >✏️</button>
              <button
                @click.stop="$emit('delete-chapter', chapter.id, chapterIndex)"
                class="action-btn action-btn--danger"
                :title="$t('panel.actions.delete')"
              >🗑️</button>
            </div>
          </div>

          <div v-if="expandedChapters.has(chapter.id)" class="chapter-lessons">
            <div
              v-for="(lesson, lessonIndex) in chapter.lessons"
              :key="lesson.id"
              class="tree-lesson"
              :class="{ 'drag-over': dragOverLessonId === lesson.id }"
              draggable="true"
              @dragstart.stop="handleLessonDragStart($event, chapterIndex, lessonIndex)"
              @dragover.prevent.stop="handleLessonDragOver($event, lesson.id)"
              @dragleave="handleLessonDragLeave"
              @drop.stop="handleLessonDrop($event, chapterIndex, lessonIndex)"
              @dragend="handleDragEnd"
            >
              <span class="drag-handle" :title="$t('panel.actions.dragToReorder')">⋮⋮</span>
              <span class="lesson-icon">📄</span>
              <span class="lesson-title">{{ lesson.title }}</span>
              <span v-if="lesson.methods?.length" class="lesson-methods">
                {{ lesson.methods.length }} LM
              </span>
              <div class="item-actions">
                <button
                  @click.stop="$emit('analyze-lesson', chapter, lesson)"
                  class="action-btn action-btn--analyze"
                  :class="{ 'is-loading': analyzingLessonId === lesson.id }"
                  :disabled="analyzingLessonId === lesson.id"
                  :title="selectedFileCount ? `Analysieren (${selectedFileCount} Dateien)` : 'Analysieren'"
                >{{ analyzingLessonId === lesson.id ? '⏳' : '🔍' }}</button>
                <button
                  @click.stop="$emit('select-lesson', chapter, lesson)"
                  class="action-btn action-btn--primary"
                  :title="$t('panel.actions.editWithAi')"
                >🤖</button>
                <button
                  @click.stop="$emit('preview-lesson', chapter, lesson)"
                  class="action-btn"
                  :title="$t('panel.actions.preview')"
                >👁️</button>
                <button
                  @click.stop="$emit('edit-lesson', chapter, lesson)"
                  class="action-btn"
                  :title="$t('panel.actions.edit')"
                >✏️</button>
                <button
                  @click.stop="$emit('delete-lesson', chapter.id, chapterIndex, lesson.id, lessonIndex)"
                  class="action-btn action-btn--danger"
                  :title="$t('panel.actions.delete')"
                >🗑️</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="stats.chapters > 0" class="panel-footer">
      {{ stats.chapters }} Kapitel · {{ stats.lessons }} Lektionen · {{ stats.methods }} Methoden
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Types
interface Lesson {
  id: string
  title: string
  description?: string
  content?: any
  duration_minutes?: number
  methods?: { id: string; type: string; title?: string }[]
}

interface Chapter {
  id: string
  title: string
  description?: string
  lessons?: Lesson[]
}

// Props
const props = defineProps<{
  chapters: Chapter[]
  analyzingLessonId?: string | null
  selectedFileCount?: number
}>()

// Emits
defineEmits<{
  (e: 'select-chapter', chapter: Chapter): void
  (e: 'preview-chapter', chapter: Chapter): void
  (e: 'edit-chapter', chapter: Chapter): void
  (e: 'delete-chapter', chapterId: string, chapterIndex: number): void
  (e: 'select-lesson', chapter: Chapter, lesson: Lesson): void
  (e: 'preview-lesson', chapter: Chapter, lesson: Lesson): void
  (e: 'edit-lesson', chapter: Chapter, lesson: Lesson): void
  (e: 'delete-lesson', chapterId: string, chapterIndex: number, lessonId: string, lessonIndex: number): void
  (e: 'analyze-lesson', chapter: Chapter, lesson: Lesson): void
  (e: 'reorder-chapters', fromIndex: number, toIndex: number): void
  (e: 'reorder-lessons', fromChapterIndex: number, fromLessonIndex: number, toChapterIndex: number, toLessonIndex: number): void
}>()

// Local State
const expandedChapters = ref<Set<string>>(new Set())

// Drag & Drop State
const dragOverChapterId = ref<string | null>(null)
const dragOverLessonId = ref<string | null>(null)
const draggingType = ref<'chapter' | 'lesson' | null>(null)
const draggingFromIndex = ref<number>(-1)
const draggingFromChapterIndex = ref<number>(-1)

// Computed
const stats = computed(() => {
  let lessons = 0, methods = 0
  for (const ch of props.chapters || []) {
    lessons += ch.lessons?.length || 0
    for (const l of ch.lessons || []) {
      methods += l.methods?.length || 0
    }
  }
  return { chapters: props.chapters?.length || 0, lessons, methods }
})

// Methods
function toggleChapter(chapterId: string) {
  if (expandedChapters.value.has(chapterId)) {
    expandedChapters.value.delete(chapterId)
  } else {
    expandedChapters.value.add(chapterId)
  }
}

// Drag & Drop Handlers
function handleChapterDragStart(e: DragEvent, chapterIndex: number) {
  draggingType.value = 'chapter'
  draggingFromIndex.value = chapterIndex
  e.dataTransfer!.effectAllowed = 'move'
  e.dataTransfer!.setData('text/plain', `chapter:${chapterIndex}`)
}

function handleChapterDragOver(e: DragEvent, chapterId: string) {
  if (draggingType.value !== 'chapter') return
  dragOverChapterId.value = chapterId
}

function handleChapterDragLeave() {
  dragOverChapterId.value = null
}

function handleChapterDrop(e: DragEvent, targetIndex: number) {
  if (draggingType.value !== 'chapter') return
  const fromIndex = draggingFromIndex.value
  if (fromIndex !== targetIndex && fromIndex !== -1) {
    // Emit reorder event - parent handles the actual reordering
    // For now, we'll handle it locally since we have the chapters prop
    const chapters = [...props.chapters]
    const [moved] = chapters.splice(fromIndex, 1)
    chapters.splice(targetIndex, 0, moved)
    // Note: Parent should handle the mutation via emit
  }
  handleDragEnd()
}

function handleLessonDragStart(e: DragEvent, chapterIndex: number, lessonIndex: number) {
  draggingType.value = 'lesson'
  draggingFromChapterIndex.value = chapterIndex
  draggingFromIndex.value = lessonIndex
  e.dataTransfer!.effectAllowed = 'move'
  e.dataTransfer!.setData('text/plain', `lesson:${chapterIndex}:${lessonIndex}`)
}

function handleLessonDragOver(e: DragEvent, lessonId: string) {
  if (draggingType.value !== 'lesson') return
  dragOverLessonId.value = lessonId
}

function handleLessonDragLeave() {
  dragOverLessonId.value = null
}

function handleLessonDrop(e: DragEvent, targetChapterIndex: number, targetLessonIndex: number) {
  if (draggingType.value !== 'lesson') return
  // Lesson drop handling - parent should handle the actual reordering
  handleDragEnd()
}

function handleDragEnd() {
  draggingType.value = null
  draggingFromIndex.value = -1
  draggingFromChapterIndex.value = -1
  dragOverChapterId.value = null
  dragOverLessonId.value = null
}

// Expose expand control
defineExpose({
  expandChapter(chapterId: string) {
    expandedChapters.value.add(chapterId)
  },
  collapseChapter(chapterId: string) {
    expandedChapters.value.delete(chapterId)
  },
  expandAll() {
    for (const ch of props.chapters) {
      expandedChapters.value.add(ch.id)
    }
  },
  collapseAll() {
    expandedChapters.value.clear()
  }
})
</script>

<style scoped>
.structure-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  background: var(--color-surface-secondary);
  border-bottom: 1px solid var(--color-border);
}

.panel-icon {
  font-size: 1rem;
}

.panel-title {
  font-size: 0.8125rem;
  font-weight: 600;
  flex: 1;
}

.panel-badge {
  padding: 0.125rem 0.5rem;
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 500;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.panel-footer {
  padding: 0.5rem 0.75rem;
  background: var(--color-surface-secondary);
  border-top: 1px solid var(--color-border);
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
}

.panel-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--color-text-tertiary);
  text-align: center;
}

.panel-empty span {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.panel-empty p {
  margin: 0;
  font-size: 0.8125rem;
}

/* Structure Tree */
.structure-tree {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.tree-chapter {
  border-radius: 0.375rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  transition: all 0.15s;
}

.tree-chapter.drag-over {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-subtle);
}

.chapter-header {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem;
}

.drag-handle {
  cursor: grab;
  color: var(--color-text-tertiary);
  font-size: 0.75rem;
  user-select: none;
}

.drag-handle:active {
  cursor: grabbing;
}

.expand-icon {
  font-size: 0.625rem;
  cursor: pointer;
  color: var(--color-text-tertiary);
  padding: 0.25rem;
}

.chapter-icon, .lesson-icon {
  font-size: 0.875rem;
}

.chapter-title, .lesson-title {
  flex: 1;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chapter-count {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  background: var(--color-surface-secondary);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.lesson-methods {
  font-size: 0.625rem;
  color: var(--color-primary);
  background: var(--color-primary-subtle);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

/* Item Actions */
.item-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.15s;
}

.chapter-header:hover .item-actions,
.tree-lesson:hover .item-actions {
  opacity: 1;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.15s;
}

.action-btn:hover {
  background: var(--color-surface-secondary);
}

.action-btn--primary:hover {
  background: var(--color-primary-subtle);
}

.action-btn--danger:hover {
  background: #fef2f2;
}

.action-btn--analyze {
  color: #6366f1;
}

.action-btn--analyze.is-loading {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Lessons */
.chapter-lessons {
  border-top: 1px solid var(--color-border);
  padding: 0.25rem 0.5rem 0.5rem 1.5rem;
}

.tree-lesson {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.15s;
}

.tree-lesson:hover {
  background: var(--color-surface-secondary);
}

.tree-lesson.drag-over {
  background: var(--color-primary-subtle);
}
</style>
