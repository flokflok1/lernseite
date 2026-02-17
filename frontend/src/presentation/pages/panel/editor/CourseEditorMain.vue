/**
 * CourseEditorMain.vue
 *
 * Background/launcher page shown behind editor windows.
 * Actual editors are opened as floating windows via the sidebar buttons in EditorLayout.
 */

<template>
  <div class="course-editor-launcher">
    <div class="launcher-content">
      <div class="launcher-icon">&#9997;&#65039;</div>
      <h2 class="launcher-title">{{ $t('panel.editor.launcher.title') }}</h2>
      <p class="launcher-description">{{ $t('panel.editor.launcher.description') }}</p>
    </div>
  </div>
</template>

<style scoped>
.course-editor-launcher {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
}

.launcher-content {
  text-align: center;
  color: #9ca3af;
}

.launcher-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.launcher-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #6b7280;
  margin: 0 0 0.5rem;
}

.launcher-description {
  font-size: 1rem;
  margin: 0;
}
</style>
