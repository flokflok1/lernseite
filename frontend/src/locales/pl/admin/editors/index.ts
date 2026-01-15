/**
 * Editor translations index
 * Re-exports all editor sub-modules (courseEditor, aiEditor)
 */

import courseEditor from './course-editor.json'
import aiEditor from './ai-editor.json'

export default {
  courseEditor: courseEditor.courseEditor,
  aiEditor: aiEditor.aiEditor
}
