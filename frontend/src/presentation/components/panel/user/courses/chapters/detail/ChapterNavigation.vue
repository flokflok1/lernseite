<template>
  <div class="chapter-navigation bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <div class="max-w-7xl mx-auto px-6">
      <!-- Tab Navigation -->
      <nav class="flex gap-2" role="tablist">
        <!-- Theory Tab -->
        <button
          :class="[
            'px-4 py-2.5 font-medium text-sm transition-all border-b-2 -mb-px focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
            activeTab === 'theory'
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:border-gray-300'
          ]"
          role="tab"
          :aria-selected="activeTab === 'theory'"
          :aria-controls="'theory-panel'"
          @click="selectTab('theory')"
        >
          <div class="flex items-center gap-2">
            <!-- Book Icon -->
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span>{{ $t('chapter.tab_theory') }}</span>
            <!-- Theory Count Badge (if available) -->
            <span
              v-if="theoryCount > 0"
              class="px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
            >
              {{ theoryCount }}
            </span>
          </div>
        </button>

        <!-- Lessons Tab -->
        <button
          :class="[
            'px-4 py-2.5 font-medium text-sm transition-all border-b-2 -mb-px focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
            activeTab === 'lessons'
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:border-gray-300'
          ]"
          role="tab"
          :aria-selected="activeTab === 'lessons'"
          :aria-controls="'lessons-panel'"
          @click="selectTab('lessons')"
        >
          <div class="flex items-center gap-2">
            <!-- List Icon -->
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            <span>{{ $t('chapter.tab_lessons') }}</span>
            <!-- Lessons Count Badge -->
            <span
              v-if="lessonCount > 0"
              class="px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
            >
              {{ lessonCount }}
            </span>
          </div>
        </button>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * ChapterNavigation Component
 * ===========================
 * Tab navigation for chapter (theory and lessons)
 */
import { ref, watch } from 'vue'

type TabType = 'theory' | 'lessons'

interface Props {
  modelValue?: TabType
  theoryCount?: number
  lessonCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: 'theory',
  theoryCount: 0,
  lessonCount: 0
})

const emit = defineEmits<{
  'update:modelValue': [value: TabType]
  'tab-change': [tab: TabType]
}>()

// Local active tab state
const activeTab = ref<TabType>(props.modelValue)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  activeTab.value = newValue
})

/**
 * Handle tab selection
 */
function selectTab(tab: TabType) {
  if (activeTab.value === tab) return

  activeTab.value = tab
  emit('update:modelValue', tab)
  emit('tab-change', tab)
}
</script>

<style scoped>
/* Additional tab transition animations */
button[role="tab"] {
  position: relative;
  transition: all 0.2s ease;
}

button[role="tab"]:hover {
  transform: translateY(-1px);
}

button[role="tab"]:active {
  transform: translateY(0);
}

/* Focus ring positioning */
button[role="tab"]:focus {
  z-index: 10;
}
</style>
