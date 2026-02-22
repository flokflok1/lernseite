<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'
import { useConfirmDialog } from '../composables/useConfirmDialog'

const { t } = useI18n()
const editorStore = useCourseEditorStore()
const { confirm: confirmDialog, prompt: promptDialog } = useConfirmDialog()

const handleAddChapter = async () => {
  const title = await promptDialog(t('panel.manualEditor.structure.addChapter'), t('panel.manualEditor.structure.chapterName'))
  if (!title) return
  await editorStore.addChapter(title)
}

const handleRemoveChapter = async (chapterId: string) => {
  const chapter = editorStore.sortedChapters.find(c => c.chapter_id === chapterId)
  const name = chapter?.title || ''
  if (!(await confirmDialog(t('panel.manualEditor.structure.confirmDeleteChapter', { name })))) return
  await editorStore.removeChapter(chapterId)
}

const handleAddLesson = async (chapterId: string) => {
  const title = await promptDialog(t('panel.manualEditor.structure.addLesson'), t('panel.manualEditor.structure.lessonName'))
  if (!title) return
  await editorStore.addLesson(chapterId, title)
}

const handleRemoveLesson = async (chapterId: string, lessonId: number) => {
  const lessons = editorStore.sortedLessons(chapterId)
  const lesson = lessons.find(l => l.lesson_id === lessonId)
  const name = lesson?.title || ''
  if (!(await confirmDialog(t('panel.manualEditor.structure.confirmDeleteLesson', { name })))) return
  await editorStore.removeLesson(chapterId, lessonId)
}
</script>

<template>
  <div class="chapter-tree">
    <h3 class="tree-title">{{ $t('panel.manualEditor.structure.title') }}</h3>

    <button class="btn-add-chapter" @click="handleAddChapter">
      + {{ $t('panel.manualEditor.structure.addChapter') }}
    </button>

    <div class="chapters-list">
      <div
        v-for="chapter in editorStore.sortedChapters"
        :key="chapter.chapter_id"
        class="chapter-item"
      >
        <!-- Chapter Header -->
        <div
          @click="editorStore.selectChapter(chapter.chapter_id)"
          :class="['chapter-header', { selected: editorStore.selectedChapterId === chapter.chapter_id }]"
        >
          <span class="chapter-title">{{ chapter.title }}</span>
          <button
            @click.stop="handleRemoveChapter(chapter.chapter_id)"
            class="btn-delete"
            :aria-label="$t('panel.manualEditor.structure.deleteChapter')"
          >&times;</button>
        </div>

        <!-- Lessons List -->
        <div
          v-if="editorStore.selectedChapterId === chapter.chapter_id"
          class="lessons-list"
        >
          <button class="btn-add-lesson" @click="handleAddLesson(chapter.chapter_id)">
            + {{ $t('panel.manualEditor.structure.addLesson') }}
          </button>

          <div
            v-for="lesson in editorStore.sortedLessons(chapter.chapter_id)"
            :key="lesson.lesson_id"
            @click="editorStore.selectLesson(chapter.chapter_id, lesson.lesson_id)"
            :class="['lesson-item', { selected: editorStore.selectedLessonId === lesson.lesson_id }]"
          >
            <span>{{ lesson.title }}</span>
            <button
              @click.stop="handleRemoveLesson(chapter.chapter_id, lesson.lesson_id)"
              class="btn-delete btn-delete-sm"
              :aria-label="$t('panel.manualEditor.structure.deleteLesson')"
            >&times;</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chapter-tree {
  padding: 12px;
  height: 100%;
  overflow-y: auto;
}

.tree-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px;
}

.btn-add-chapter {
  width: 100%;
  padding: 6px 10px;
  margin-bottom: 10px;
  border: 1px dashed var(--color-border);
  border-radius: 4px;
  background: none;
  color: var(--color-accent);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-add-chapter:hover { background: color-mix(in srgb, var(--color-accent) 8%, transparent); }

.chapters-list { display: flex; flex-direction: column; gap: 4px; }

.chapter-item {
  border: 1px solid var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}

.chapter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  cursor: pointer;
  transition: background 0.15s;
}

.chapter-header:hover { background: var(--color-surface-secondary); }
.chapter-header.selected { background: color-mix(in srgb, var(--color-accent) 10%, transparent); }

.chapter-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-delete {
  border: none;
  background: none;
  color: var(--color-error);
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0 2px;
  opacity: 0.6;
  transition: opacity 0.15s;
}

.btn-delete:hover { opacity: 1; }
.btn-delete-sm { font-size: 14px; }

.lessons-list {
  border-top: 1px solid var(--color-border);
  padding: 6px 8px;
  background: var(--color-surface-secondary);
}

.btn-add-lesson {
  width: 100%;
  text-align: left;
  padding: 4px 8px;
  border: none;
  background: none;
  color: var(--color-accent);
  font-size: 12px;
  cursor: pointer;
  border-radius: 3px;
}

.btn-add-lesson:hover { background: color-mix(in srgb, var(--color-accent) 8%, transparent); }

.lesson-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 8px;
  font-size: 13px;
  cursor: pointer;
  border-radius: 3px;
  color: var(--color-text-primary);
  transition: background 0.15s;
}

.lesson-item:hover { background: color-mix(in srgb, var(--color-text-primary) 5%, transparent); }
.lesson-item.selected { background: color-mix(in srgb, var(--color-accent) 15%, transparent); color: var(--color-accent); }
</style>
