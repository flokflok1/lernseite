/**
 * StructureTreePanel.vue
 *
 * Hierarchical chapter/lesson tree for the manual course editor.
 * Supports inline add/rename, delete with confirmation, and selection.
 * Replaces the shared StructurePanel stub.
 */

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

const { t } = useI18n()
const store = useCourseEditorStore()

const expandedChapters = ref<Set<string>>(new Set())
const addingChapter = ref(false)
const addingLessonChapterId = ref<string | null>(null)
const newItemName = ref('')
const confirmDeleteId = ref<string | null>(null)
const confirmDeleteType = ref<'chapter' | 'lesson'>('chapter')

const chapters = computed(() => store.sortedChapters)

const toggleChapter = (chapterId: string): void => {
  if (expandedChapters.value.has(chapterId)) {
    expandedChapters.value.delete(chapterId)
  } else {
    expandedChapters.value.add(chapterId)
  }
}

const isExpanded = (chapterId: string): boolean => {
  return expandedChapters.value.has(chapterId)
}

const getLessons = (chapterId: string) => {
  return store.sortedLessons(chapterId)
}

const startAddChapter = (): void => {
  addingChapter.value = true
  addingLessonChapterId.value = null
  newItemName.value = ''
}

const startAddLesson = (chapterId: string): void => {
  addingLessonChapterId.value = chapterId
  addingChapter.value = false
  newItemName.value = ''
  expandedChapters.value.add(chapterId)
}

const confirmAdd = async (): Promise<void> => {
  const name = newItemName.value.trim()
  if (!name) return

  if (addingChapter.value) {
    const chapter = await store.addChapter(name)
    expandedChapters.value.add(chapter.chapter_id)
    store.selectChapter(chapter.chapter_id)
  } else if (addingLessonChapterId.value) {
    const lesson = await store.addLesson(addingLessonChapterId.value, name)
    store.selectLesson(addingLessonChapterId.value, lesson.lesson_id)
  }

  cancelAdd()
}

const cancelAdd = (): void => {
  addingChapter.value = false
  addingLessonChapterId.value = null
  newItemName.value = ''
}

const handleAddKeydown = (e: KeyboardEvent): void => {
  if (e.key === 'Enter') confirmAdd()
  if (e.key === 'Escape') cancelAdd()
}

const requestDelete = (type: 'chapter' | 'lesson', id: string): void => {
  confirmDeleteType.value = type
  confirmDeleteId.value = id
}

const executeDelete = async (): Promise<void> => {
  if (!confirmDeleteId.value) return

  if (confirmDeleteType.value === 'chapter') {
    await store.removeChapter(confirmDeleteId.value)
  } else {
    const chapterId = store.selectedChapterId
    if (chapterId) {
      await store.removeLesson(chapterId, Number(confirmDeleteId.value))
    }
  }
  confirmDeleteId.value = null
}

const cancelDelete = (): void => {
  confirmDeleteId.value = null
}

const selectChapter = (chapterId: string): void => {
  store.selectChapter(chapterId)
  expandedChapters.value.add(chapterId)
}

const selectLesson = (chapterId: string, lessonId: number): void => {
  store.selectLesson(chapterId, lessonId)
}

const getDeleteLabel = (): string => {
  if (!confirmDeleteId.value) return ''
  if (confirmDeleteType.value === 'chapter') {
    const ch = chapters.value.find(c => c.chapter_id === confirmDeleteId.value)
    return t('panel.manualEditor.structure.confirmDeleteChapter', { name: ch?.title || '' })
  }
  return t('panel.manualEditor.structure.confirmDeleteLesson', { name: '' })
}
</script>

<template>
  <div class="structure-tree">
    <!-- Header -->
    <div class="tree-header">
      <span class="tree-title">{{ $t('panel.manualEditor.structure.title') }}</span>
      <span class="chapter-count">
        {{ $t('panel.manualEditor.structure.chapters', { count: chapters.length }) }}
      </span>
    </div>

    <!-- Chapter list -->
    <div class="tree-content">
      <!-- Empty state -->
      <div v-if="chapters.length === 0 && !addingChapter" class="empty-state">
        <p>{{ $t('panel.manualEditor.structure.emptyState') }}</p>
      </div>

      <!-- Chapters -->
      <div
        v-for="chapter in chapters"
        :key="chapter.chapter_id"
        class="chapter-node"
      >
        <!-- Chapter row -->
        <div
          class="chapter-row"
          :class="{ selected: store.selectedChapterId === chapter.chapter_id && !store.selectedLessonId }"
          @click="selectChapter(chapter.chapter_id)"
        >
          <button
            class="expand-btn"
            :aria-label="isExpanded(chapter.chapter_id) ? 'Collapse' : 'Expand'"
            @click.stop="toggleChapter(chapter.chapter_id)"
          >
            {{ isExpanded(chapter.chapter_id) ? '▼' : '▶' }}
          </button>
          <span class="chapter-title">{{ chapter.title }}</span>
          <span class="lesson-count">
            ({{ getLessons(chapter.chapter_id).length }})
          </span>
          <button
            class="delete-btn"
            :aria-label="$t('panel.manualEditor.structure.deleteChapter')"
            @click.stop="requestDelete('chapter', chapter.chapter_id)"
          >
            &times;
          </button>
        </div>

        <!-- Lessons -->
        <div v-if="isExpanded(chapter.chapter_id)" class="lessons-list">
          <div
            v-for="lesson in getLessons(chapter.chapter_id)"
            :key="lesson.lesson_id"
            class="lesson-row"
            :class="{ selected: store.selectedLessonId === lesson.lesson_id }"
            @click="selectLesson(chapter.chapter_id, lesson.lesson_id)"
          >
            <span class="lesson-icon">{{ lesson.lesson_type === 'video' ? '🎬' : lesson.lesson_type === 'quiz' ? '❓' : '📝' }}</span>
            <span class="lesson-title">{{ lesson.title }}</span>
            <button
              class="delete-btn"
              :aria-label="$t('panel.manualEditor.structure.deleteLesson')"
              @click.stop="requestDelete('lesson', String(lesson.lesson_id))"
            >
              &times;
            </button>
          </div>

          <!-- Add lesson inline input -->
          <div v-if="addingLessonChapterId === chapter.chapter_id" class="inline-input">
            <input
              v-model="newItemName"
              type="text"
              :placeholder="$t('panel.manualEditor.structure.lessonName')"
              autofocus
              @keydown="handleAddKeydown"
              @blur="cancelAdd"
            />
          </div>

          <!-- Add lesson button -->
          <button
            v-else
            class="add-lesson-btn"
            @click.stop="startAddLesson(chapter.chapter_id)"
          >
            + {{ $t('panel.manualEditor.structure.addLesson') }}
          </button>
        </div>
      </div>

      <!-- Add chapter inline input -->
      <div v-if="addingChapter" class="inline-input">
        <input
          v-model="newItemName"
          type="text"
          :placeholder="$t('panel.manualEditor.structure.chapterName')"
          autofocus
          @keydown="handleAddKeydown"
          @blur="cancelAdd"
        />
      </div>
    </div>

    <!-- Add chapter button -->
    <button
      class="add-chapter-btn"
      @click="startAddChapter"
    >
      + {{ $t('panel.manualEditor.structure.addChapter') }}
    </button>

    <!-- Delete confirmation overlay -->
    <div v-if="confirmDeleteId" class="confirm-overlay" @click="cancelDelete">
      <div class="confirm-dialog" @click.stop>
        <p>{{ getDeleteLabel() }}</p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="cancelDelete">
            {{ $t('common.cancel') }}
          </button>
          <button class="btn-delete" @click="executeDelete">
            {{ $t('common.delete') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.structure-tree {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.tree-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.tree-title {
  font-weight: 600;
  font-size: 13px;
}

.chapter-count {
  font-size: 11px;
  color: #888;
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 6px;
}

.empty-state {
  padding: 24px 12px;
  text-align: center;
  color: #999;
  font-size: 13px;
}

.chapter-row {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.chapter-row:hover {
  background: #f0f0f0;
}

.chapter-row.selected {
  background: #e3f2fd;
}

.expand-btn {
  border: none;
  background: none;
  cursor: pointer;
  padding: 0 2px;
  font-size: 10px;
  color: #666;
  line-height: 1;
}

.chapter-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lesson-count {
  font-size: 11px;
  color: #999;
  flex-shrink: 0;
}

.delete-btn {
  border: none;
  background: none;
  cursor: pointer;
  color: #ccc;
  font-size: 16px;
  padding: 0 4px;
  line-height: 1;
  opacity: 0;
  transition: opacity 0.15s;
}

.chapter-row:hover .delete-btn,
.lesson-row:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #e53935;
}

.lessons-list {
  padding-left: 20px;
}

.lesson-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.lesson-row:hover {
  background: #f5f5f5;
}

.lesson-row.selected {
  background: #e3f2fd;
}

.lesson-icon {
  font-size: 12px;
  flex-shrink: 0;
}

.lesson-title {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inline-input {
  padding: 4px 8px;
}

.inline-input input {
  width: 100%;
  padding: 4px 8px;
  border: 1px solid #2196f3;
  border-radius: 4px;
  font-size: 12px;
  outline: none;
}

.add-lesson-btn {
  border: none;
  background: none;
  color: #2196f3;
  cursor: pointer;
  font-size: 11px;
  padding: 4px 8px;
  text-align: left;
  width: 100%;
}

.add-lesson-btn:hover {
  background: #f0f7ff;
  border-radius: 4px;
}

.add-chapter-btn {
  padding: 10px 12px;
  border: none;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
  color: #2196f3;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  text-align: left;
}

.add-chapter-btn:hover {
  background: #f0f7ff;
}

.confirm-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.confirm-dialog {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 280px;
}

.confirm-dialog p {
  margin: 0 0 12px;
  font-size: 13px;
}

.confirm-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-delete {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-cancel {
  background: white;
}

.btn-delete {
  background: #e53935;
  color: white;
  border-color: #c62828;
}
</style>
