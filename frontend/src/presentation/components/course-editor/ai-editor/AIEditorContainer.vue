/**
 * AIEditorContainer.vue
 *
 * Main container for AI-assisted course editing.
 */

<script setup lang="ts">
import { ref } from 'vue'
import ChatInterface from './ChatInterface.vue'
import ContentGenerator from './ContentGenerator.vue'
import VariantSelector from './VariantSelector.vue'
import GenerationHistory from './GenerationHistory.vue'

interface Props {
  projectId: string
}

interface Emits {
  (e: 'save'): void
}

defineProps<Props>()
defineEmits<Emits>()

const activeTab = ref<'chat' | 'generator' | 'variants' | 'history'>('chat')
</script>

<template>
  <div class="ai-editor-container">
    <!-- Tab Navigation -->
    <div class="ai-tabs">
      <button
        :class="['tab-btn', { active: activeTab === 'chat' }]"
        @click="activeTab = 'chat'"
      >
        💬 {{ $t('courses.editor.aiChat') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'generator' }]"
        @click="activeTab = 'generator'"
      >
        ⚡ {{ $t('courses.editor.generate') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'variants' }]"
        @click="activeTab = 'variants'"
      >
        📋 {{ $t('courses.editor.variants') }}
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'history' }]"
        @click="activeTab = 'history'"
      >
        📜 {{ $t('courses.editor.history') }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="ai-content">
      <ChatInterface v-if="activeTab === 'chat'" />
      <ContentGenerator v-else-if="activeTab === 'generator'" />
      <VariantSelector v-else-if="activeTab === 'variants'" />
      <GenerationHistory v-else-if="activeTab === 'history'" />
    </div>
  </div>
</template>

<style scoped>
.ai-editor-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 10px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.ai-tabs {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.tab-btn:hover {
  background: #e8e8e8;
}

.tab-btn.active {
  background: #2196f3;
  color: white;
  border-color: #1976d2;
}

.ai-content {
  flex: 1;
  overflow: auto;
  padding: 16px;
}
</style>
