/**
 * AiEditorSection.vue
 *
 * AI-powered lesson editor sub-component with prompt input
 * and content generation trigger.
 */

<script setup lang="ts">
import { ref } from 'vue'

const aiPrompt = ref('')
</script>

<template>
  <div class="ai-editor">
    <h3>{{ $t('panel.manualEditor.content.aiPrompt') }}</h3>
    <textarea
      v-model="aiPrompt"
      :placeholder="$t('panel.manualEditor.content.aiPrompt')"
      rows="6"
    />
    <button class="ai-generate-btn">
      {{ $t('panel.manualEditor.content.aiGenerate') }}
    </button>
  </div>
</template>

<style scoped>
.ai-editor {
  padding: 16px;
}

.ai-editor h3 {
  font-size: 14px;
  margin: 0 0 8px;
}

.ai-editor textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  resize: vertical;
}

.ai-generate-btn {
  margin-top: 8px;
  padding: 8px 16px;
  background: #7c4dff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}

.ai-generate-btn:hover {
  background: #651fff;
}
</style>
