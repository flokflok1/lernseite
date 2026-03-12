<template>
  <div class="h-full flex flex-col">
    <!-- Tab Navigation -->
    <div class="bg-[var(--color-surface)] border-b border-[var(--color-border)] px-6">
      <nav class="flex gap-1 -mb-px" aria-label="Crawler tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
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
      <div class="h-full overflow-y-auto p-6">
        <CrawlDashboardTab v-if="activeTab === 'dashboard'" />
        <CrawlJobsTab v-else-if="activeTab === 'jobs'" />
        <CrawlPdfLibraryTab v-else-if="activeTab === 'pdfs'" />
        <CrawlDomainSettingsTab v-else-if="activeTab === 'domains'" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCrawlManagement } from '@/application/composables/panel/admin/crawler'
import CrawlDashboardTab from '@/presentation/components/panel/admin/crawler/CrawlDashboardTab.vue'
import CrawlJobsTab from '@/presentation/components/panel/admin/crawler/CrawlJobsTab.vue'
import CrawlPdfLibraryTab from '@/presentation/components/panel/admin/crawler/CrawlPdfLibraryTab.vue'
import CrawlDomainSettingsTab from '@/presentation/components/panel/admin/crawler/CrawlDomainSettingsTab.vue'

const { t } = useI18n()
const store = useCrawlManagement()

const activeTab = ref<'dashboard' | 'jobs' | 'pdfs' | 'domains'>('dashboard')

const tabs = computed(() => [
  { key: 'dashboard' as const, label: t('panel.crawler.tabs.dashboard') },
  { key: 'jobs' as const, label: t('panel.crawler.tabs.jobs') },
  { key: 'pdfs' as const, label: t('panel.crawler.tabs.pdfs') },
  { key: 'domains' as const, label: t('panel.crawler.tabs.domains') },
])

onUnmounted(() => {
  store.stopPolling()
})
</script>
