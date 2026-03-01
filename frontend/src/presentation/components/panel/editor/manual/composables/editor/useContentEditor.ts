/**
 * useContentEditor - Composable for TipTap rich text editor management.
 *
 * Encapsulates editor initialization, toolbar actions, and content
 * synchronization with the course editor store.
 */

import { computed, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Image from '@tiptap/extension-image'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'

export function useContentEditor() {
  const { t } = useI18n()
  const store = useCourseEditorStore()

  const lesson = computed(() => store.currentLesson)
  const lessonType = computed(() => lesson.value?.lesson_type || 'text')

  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: () => t('panel.manualEditor.content.placeholder'),
      }),
      Image,
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Underline,
      Link.configure({ openOnClick: false }),
    ],
    content: '',
    onUpdate: ({ editor: ed }) => {
      if (lesson.value) {
        store.setLocalContent(lesson.value.lesson_id, ed.getHTML())
      }
    },
  })

  // Watch both lesson AND editor — useEditor creates the instance in onMounted,
  // so the immediate watcher on lesson alone fires before editor.value exists.
  watch([lesson, editor], ([newLesson]) => {
    if (!editor.value) return

    if (newLesson) {
      const content = typeof newLesson.content === 'string' ? newLesson.content : ''
      if (editor.value.getHTML() !== content) {
        editor.value.commands.setContent(content, false)
      }
    } else {
      editor.value.commands.setContent('', false)
    }
  }, { immediate: true })

  onBeforeUnmount(() => {
    editor.value?.destroy()
  })

  // Toolbar actions
  function toggleBold(): void { editor.value?.chain().focus().toggleBold().run() }
  function toggleItalic(): void { editor.value?.chain().focus().toggleItalic().run() }
  function toggleUnderline(): void { editor.value?.chain().focus().toggleUnderline().run() }
  function toggleStrike(): void { editor.value?.chain().focus().toggleStrike().run() }
  function setHeading(level: 1 | 2 | 3): void { editor.value?.chain().focus().toggleHeading({ level }).run() }
  function toggleBulletList(): void { editor.value?.chain().focus().toggleBulletList().run() }
  function toggleOrderedList(): void { editor.value?.chain().focus().toggleOrderedList().run() }
  function toggleCodeBlock(): void { editor.value?.chain().focus().toggleCodeBlock().run() }
  function setAlignLeft(): void { editor.value?.chain().focus().setTextAlign('left').run() }
  function setAlignCenter(): void { editor.value?.chain().focus().setTextAlign('center').run() }
  function setAlignRight(): void { editor.value?.chain().focus().setTextAlign('right').run() }
  function undoAction(): void { editor.value?.chain().focus().undo().run() }
  function redoAction(): void { editor.value?.chain().focus().redo().run() }

  function insertLink(url?: string): void {
    if (url) {
      editor.value?.chain().focus().setLink({ href: url }).run()
    }
  }

  function insertImage(url?: string): void {
    if (url) {
      editor.value?.chain().focus().setImage({ src: url }).run()
    }
  }

  function isActive(name: string | Record<string, unknown>, attrs?: Record<string, unknown>): boolean {
    return editor.value?.isActive(name, attrs) || false
  }

  return {
    editor,
    lesson,
    lessonType,
    toggleBold,
    toggleItalic,
    toggleUnderline,
    toggleStrike,
    setHeading,
    toggleBulletList,
    toggleOrderedList,
    toggleCodeBlock,
    setAlignLeft,
    setAlignCenter,
    setAlignRight,
    undoAction,
    redoAction,
    insertLink,
    insertImage,
    isActive,
  }
}
