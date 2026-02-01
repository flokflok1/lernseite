<template>
  <div class="course-list-editor-window">
    <!-- Tab Navigation -->
    <div class="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
      <div class="flex gap-1 p-4">
        <button
          @click="activeTab = 'manual'"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-all duration-200',
            activeTab === 'manual'
              ? 'bg-blue-600 text-white'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-border)]'
          ]"
        >
          ✏️ Manueller Editor
        </button>
        <button
          @click="activeTab = 'ai'"
          :class="[
            'px-4 py-2 rounded-lg font-medium transition-all duration-200',
            activeTab === 'ai'
              ? 'bg-purple-600 text-white'
              : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-border)]'
          ]"
        >
          🤖 AI Editor
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 overflow-y-auto">
      <!-- Manual Editor Tab -->
      <div v-if="activeTab === 'manual'" class="h-full">
        <AdminCourseListContent />
      </div>

      <!-- AI Editor Tab -->
      <div v-if="activeTab === 'ai'" class="h-full">
        <AdminAIEditorTab />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AdminCourseListContent from './AdminCourseListContent.vue'
import AdminAIEditorTab from './AdminAIEditorTab.vue'

/**
 * Course List Editor Panel
 *
 * Panel component for managing courses with tabs for:
 * - Manueller Editor: Course listing with filtering and management
 * - AI Editor: Full AI Editor interface for content authoring
 */

// Active tab state
const activeTab = ref<'manual' | 'ai'>('manual')
</script>

<style scoped>
.course-list-editor-window {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  color: var(--color-text-primary);
}
</style>
