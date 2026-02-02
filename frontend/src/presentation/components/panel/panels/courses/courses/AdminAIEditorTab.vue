<!--
  AI Editor Tab Content

  Wrapper component that renders the AI Editor interface within a tab.
  Handles the window prop requirement by providing a minimal panel object.
-->

<template>
  <div class="admin-ai-editor-tab h-full">
    <AiEditorPanel :panel="windowData" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AiEditorPanel from '@/presentation/components/studio/ai/panel/studio/views/AiEditorPanel.vue'

// Create a minimal panel object that satisfies AiEditorPanel's requirements
const windowData = ref({
  id: 'admin-ai-editor-tab',
  type: 'admin-ai-editor',
  title: 'AI Editor',
  icon: '🤖',
  minimized: false,
  maximized: false,
  position: { x: 0, y: 0 },
  size: { width: 1100, height: 750 },
  payload: null,
  zIndex: 1000
})
</script>

<style scoped>
.admin-ai-editor-tab {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
