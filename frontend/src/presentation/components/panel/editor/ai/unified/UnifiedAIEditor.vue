<script setup lang="ts">
/**
 * UnifiedAIEditor — Main orchestrator component
 *
 * Replaces AIEditorContainer with a single unified editor.
 * Tab system: Plan | Skills | Content | Prompts | History
 */
import { onMounted, provide, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useEditorState, useTokenBudget } from './composables'
import { PlanTab, SkillsTab, HistoryTab } from './tabs'

const props = defineProps<{
  initialCourseId?: string
}>()

const { t } = useI18n()

const editor = useEditorState()
const tokenBudget = useTokenBudget()

// Provide editor state to descendants
provide('editorState', editor)
provide('tokenBudget', tokenBudget)

onMounted(async () => {
  await editor.loadCourses()
  // Auto-select course from window payload
  if (props.initialCourseId) {
    const course = editor.courses.value.find(c => c.id === props.initialCourseId)
    if (course) {
      editor.selectCourse(course.id, course.title)
    }
  }
})
</script>

<template>
  <div class="flex flex-col h-full bg-gray-900 text-white">
    <!-- Top Bar: Course Selector + Token Budget -->
    <div class="flex items-center justify-between px-4 py-2.5 border-b border-gray-700 bg-gray-900/95">
      <div class="flex items-center gap-3">
        <h2 class="text-sm font-semibold text-gray-300">{{ t('aiEditor.title') }}</h2>
        <select
          :value="editor.courseId.value || ''"
          class="px-3 py-1.5 bg-gray-800 border border-gray-600 rounded text-sm text-white min-w-[200px]"
          @change="(e: Event) => {
            const target = e.target as HTMLSelectElement
            const course = editor.courses.value.find(c => c.id === target.value)
            if (course) editor.selectCourse(course.id, course.title)
          }"
        >
          <option value="" disabled>{{ t('aiEditor.selectCourse') }}</option>
          <option v-for="course in editor.courses.value" :key="course.id" :value="course.id">
            {{ course.title }}
          </option>
        </select>
      </div>

      <!-- Token Budget Indicator -->
      <div class="flex items-center gap-3">
        <div class="text-xs text-gray-500">
          {{ tokenBudget.tokensUsed.value.toLocaleString() }} / {{ tokenBudget.totalBudget.value.toLocaleString() }}
        </div>
        <div class="w-24 h-1.5 bg-gray-800 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all"
            :class="{
              'bg-indigo-500': !tokenBudget.isWarning.value && !tokenBudget.isOverBudget.value,
              'bg-yellow-500': tokenBudget.isWarning.value,
              'bg-red-500': tokenBudget.isOverBudget.value,
            }"
            :style="{ width: `${Math.min(100, tokenBudget.usagePercent.value)}%` }"
          />
        </div>
      </div>
    </div>

    <!-- Tab Bar -->
    <div class="flex border-b border-gray-700 bg-gray-900/80">
      <button
        v-for="tab in editor.tabs.value"
        :key="tab.id"
        class="px-4 py-2.5 text-sm font-medium transition-colors relative"
        :class="editor.activeTab.value === tab.id
          ? 'text-white'
          : 'text-gray-500 hover:text-gray-300'"
        @click="editor.setTab(tab.id)"
      >
        {{ tab.label }}
        <div
          v-if="editor.activeTab.value === tab.id"
          class="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500"
        />
      </button>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 overflow-hidden">
      <!-- No course selected -->
      <div v-if="!editor.hasCourseSelected.value" class="flex items-center justify-center h-full">
        <div class="text-center space-y-2">
          <div class="text-3xl">📚</div>
          <p class="text-sm text-gray-500">{{ t('aiEditor.selectCoursePrompt') }}</p>
        </div>
      </div>

      <!-- Plan Tab -->
      <PlanTab
        v-else-if="editor.activeTab.value === 'plan'"
        :course-id="editor.courseId.value!"
      />

      <!-- Skills Tab -->
      <SkillsTab
        v-else-if="editor.activeTab.value === 'skills'"
        :course-id="editor.courseId.value!"
      />

      <!-- Content Tab (reuse existing) -->
      <div v-else-if="editor.activeTab.value === 'content'" class="p-8 text-center text-gray-500 text-sm">
        {{ t('aiEditor.tabs.contentPlaceholder') }}
      </div>

      <!-- Prompts Tab -->
      <div v-else-if="editor.activeTab.value === 'prompts'" class="p-8 text-center text-gray-500 text-sm">
        {{ t('aiEditor.tabs.promptsPlaceholder') }}
      </div>

      <!-- History Tab -->
      <HistoryTab
        v-else-if="editor.activeTab.value === 'history'"
        :course-id="editor.courseId.value!"
      />
    </div>

    <!-- Error Banner -->
    <div v-if="editor.error.value" class="px-4 py-2 bg-red-900/30 border-t border-red-800">
      <div class="flex items-center justify-between">
        <span class="text-xs text-red-300">{{ editor.error.value }}</span>
        <button class="text-xs text-red-400 hover:text-red-300" @click="editor.clearError">✕</button>
      </div>
    </div>
  </div>
</template>
