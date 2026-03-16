<template>
  <div class="h-full flex flex-col">
    <!-- Tab Navigation -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6">
      <nav class="flex gap-1 -mb-px" aria-label="Exam tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="handleTab(tab.key)"
          class="px-4 py-3 text-sm font-medium transition-colors border-b-2 whitespace-nowrap"
          :class="activeTab === tab.key
            ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
            : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-border)]'"
          :aria-selected="activeTab === tab.key"
          role="tab"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 overflow-hidden">
      <FileExplorer v-if="activeTab === 'archive'" :key="0" @close="() => {}" />
      <div v-else-if="activeTab === 'curriculum'" class="h-full overflow-y-auto p-6">
        <CurriculumManager />
      </div>
      <div v-else-if="activeTab === 'courses'" class="h-full overflow-y-auto p-6">
        <ExamCourseGenerator />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import FileExplorer from '@/presentation/components/panel/admin/assessment/archive/FileExplorer.vue'
import CurriculumManager from '@/presentation/components/panel/admin/assessment/curriculum/CurriculumManager.vue'
import ExamCourseGenerator from '@/presentation/components/panel/admin/assessment/exams/ExamCourseGenerator.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()

type TabKey = 'archive' | 'curriculum' | 'courses'

const activeTab = ref<TabKey>(
  (route.query.tab as TabKey) || 'archive'
)

const tabs = computed(() => [
  { key: 'archive' as const, label: t('panel.exams.tabs.archive') },
  { key: 'curriculum' as const, label: t('panel.exams.tabs.curriculum') },
  { key: 'courses' as const, label: t('panel.exams.tabs.courses') },
])

function handleTab(key: TabKey) {
  if (key === 'archive') {
    router.push({ name: 'PanelExamArchive' })
  } else {
    activeTab.value = key
  }
}

// Auto-redirect to file explorer if no tab specified
onMounted(() => {
  if (!route.query.tab) {
    router.replace({ name: 'PanelExamArchive' })
  }
})
</script>
