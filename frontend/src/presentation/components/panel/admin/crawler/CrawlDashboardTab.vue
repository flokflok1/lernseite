<script setup lang="ts">
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { useCrawlManagement } from '@/application/composables/panel/admin/crawler'

const { t } = useI18n()
const store = useCrawlManagement()
const { dashboard, loading } = storeToRefs(store)
const { refreshDashboard, triggerCrawl } = store

onMounted(() => {
  refreshDashboard()
})

function formatDate(dateStr: string | null): string {
  if (!dateStr) return t('panel.crawler.dashboard.neverCrawled')
  return new Date(dateStr).toLocaleDateString()
}

function healthColor(health: string): string {
  const colors: Record<string, string> = {
    good: 'bg-green-100 text-green-700',
    stale: 'bg-yellow-100 text-yellow-700',
    error: 'bg-red-100 text-red-700',
    never: 'bg-gray-100 text-gray-500',
  }
  return colors[health] || colors.never
}
</script>

<template>
  <div v-if="!dashboard && loading" class="flex justify-center p-8">
    <div
      class="animate-spin h-6 w-6 border-2 border-[var(--color-primary)] border-t-transparent rounded-full"
    />
  </div>

  <div v-else-if="dashboard" class="space-y-6">
    <!-- KPI Cards -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <!-- Total PDFs -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.crawler.dashboard.totalPdfs') }}
        </p>
        <p class="text-2xl font-bold mt-1">{{ dashboard.total_pdfs }}</p>
      </div>

      <!-- Domains -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.crawler.dashboard.activeDomains') }}
        </p>
        <p class="text-2xl font-bold mt-1">
          {{ dashboard.active_domains }}/{{ dashboard.total_domains }}
        </p>
      </div>

      <!-- Active Jobs -->
      <div
        class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4"
        :class="dashboard.active_jobs > 0 ? 'ring-2 ring-[var(--color-primary)]' : ''"
      >
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.crawler.dashboard.activeJobs') }}
        </p>
        <p class="text-2xl font-bold mt-1">{{ dashboard.active_jobs }}</p>
      </div>

      <!-- Cache Size -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.crawler.dashboard.cacheSize') }}
        </p>
        <p class="text-2xl font-bold mt-1">{{ dashboard.cache_size_mb }} MB</p>
      </div>

      <!-- Last Crawl -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <p class="text-sm text-[var(--color-text-secondary)]">
          {{ t('panel.crawler.dashboard.lastCrawl') }}
        </p>
        <p class="text-lg font-semibold mt-1">{{ formatDate(dashboard.last_crawl_at) }}</p>
      </div>
    </div>

    <!-- Domain Status Grid -->
    <div>
      <h2 class="text-lg font-semibold mb-3">
        {{ t('panel.crawler.dashboard.domainStatus') }}
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="domain in dashboard.domain_status"
          :key="domain.domain_id"
          class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-medium truncate mr-2">{{ domain.display_name }}</h3>
            <span
              class="px-2 py-0.5 rounded-full text-xs font-medium shrink-0"
              :class="healthColor(domain.health)"
            >
              {{ t(`panel.crawler.dashboard.health.${domain.health}`) }}
            </span>
          </div>
          <div class="text-sm text-[var(--color-text-secondary)] space-y-1">
            <p>{{ t('panel.crawler.pdfs.pages') }}: {{ domain.total_pdfs_found }}</p>
            <p>{{ formatDate(domain.last_crawled_at) }}</p>
          </div>
          <button
            class="mt-3 w-full px-3 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded hover:opacity-90 transition-opacity"
            @click="triggerCrawl(domain.domain_id)"
          >
            {{ t('panel.crawler.jobs.startCrawl') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
