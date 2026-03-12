<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { useCrawlManagement } from '@/application/composables/panel/admin/crawler'
import StartCrawlDialog from './StartCrawlDialog.vue'
import type { CrawlJob } from '@/infrastructure/api/clients/panel/admin/crawler'

const { t } = useI18n()
const store = useCrawlManagement()
const { jobs, domains, loading } = storeToRefs(store)
const { loadJobs, loadDomains, triggerCrawl, startPolling, stopPolling } = store

const showStartDialog = ref(false)

const hasActiveJobs = computed(() =>
  jobs.value.some(j => j.status === 'running' || j.status === 'pending')
)

onMounted(async () => {
  await Promise.all([loadJobs(), loadDomains()])
  if (hasActiveJobs.value) startPolling()
})

onUnmounted(() => {
  stopPolling()
})

// Auto-start/stop polling when active jobs change
watch(hasActiveJobs, (active) => {
  if (active) startPolling()
  else stopPolling()
})

async function handleStartCrawl(domainId?: string) {
  showStartDialog.value = false
  await triggerCrawl(domainId)
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const statusColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-600',
  running: 'bg-blue-100 text-blue-700 animate-pulse',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  cancelled: 'bg-yellow-100 text-yellow-700',
}

function statusBadge(status: string): string {
  return statusColors[status] ?? statusColors.pending
}

function formatDuration(job: CrawlJob): string {
  const start = job.started_at ? new Date(job.started_at).getTime() : null
  if (!start) return '-'
  const end = job.completed_at ? new Date(job.completed_at).getTime() : Date.now()
  const seconds = Math.round((end - start) / 1000)
  if (seconds < 60) return `${seconds}s`
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}m ${secs}s`
}

function formatTime(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold">{{ t('panel.crawler.jobs.title') }}</h2>
      <button
        class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded hover:opacity-90 transition-opacity"
        @click="showStartDialog = true"
      >
        {{ t('panel.crawler.jobs.startCrawl') }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="!jobs.length && loading" class="flex justify-center p-8">
      <div
        class="animate-spin h-6 w-6 border-2 border-[var(--color-primary)] border-t-transparent rounded-full"
      />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="!jobs.length"
      class="text-center py-12 text-[var(--color-text-secondary)]"
    >
      <p>{{ t('panel.crawler.jobs.noJobs') }}</p>
    </div>

    <!-- Jobs table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-[var(--color-border)] text-left text-[var(--color-text-secondary)]">
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.pdfs.domain') }}</th>
            <th class="pb-2 pr-4 font-medium">Status</th>
            <th class="pb-2 pr-4 font-medium text-right">{{ t('panel.crawler.jobs.pages') }}</th>
            <th class="pb-2 pr-4 font-medium text-right">{{ t('panel.crawler.jobs.pdfsFound') }}</th>
            <th class="pb-2 pr-4 font-medium text-right">{{ t('panel.crawler.jobs.pdfsNew') }}</th>
            <th class="pb-2 pr-4 font-medium text-right">{{ t('panel.crawler.jobs.errors') }}</th>
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.jobs.progress') }}</th>
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.jobs.duration') }}</th>
            <th class="pb-2 font-medium">{{ t('panel.crawler.jobs.started') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="job in jobs"
            :key="job.job_id"
            class="border-b border-[var(--color-border)] last:border-0"
          >
            <!-- Domain -->
            <td class="py-3 pr-4">
              {{ job.domain_name || '-' }}
            </td>

            <!-- Status badge -->
            <td class="py-3 pr-4">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-medium"
                :class="statusBadge(job.status)"
              >
                {{ t(`panel.crawler.jobs.status.${job.status}`) }}
              </span>
            </td>

            <!-- Pages -->
            <td class="py-3 pr-4 text-right tabular-nums">
              {{ job.pages_crawled }}
            </td>

            <!-- PDFs found -->
            <td class="py-3 pr-4 text-right tabular-nums">
              {{ job.pdfs_discovered }}
            </td>

            <!-- New PDFs -->
            <td class="py-3 pr-4 text-right tabular-nums">
              {{ job.pdfs_new }}
            </td>

            <!-- Errors -->
            <td class="py-3 pr-4 text-right tabular-nums">
              <span :class="job.errors_count > 0 ? 'text-red-600 font-medium' : ''">
                {{ job.errors_count }}
              </span>
            </td>

            <!-- Progress bar -->
            <td class="py-3 pr-4 min-w-[100px]">
              <div class="flex items-center gap-2">
                <div class="flex-1 h-2 bg-[var(--color-border)] rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-300"
                    :class="job.status === 'failed' ? 'bg-red-500' : 'bg-[var(--color-primary)]'"
                    :style="{ width: `${job.progress_pct}%` }"
                  />
                </div>
                <span class="text-xs text-[var(--color-text-secondary)] tabular-nums w-8 text-right">
                  {{ job.progress_pct }}%
                </span>
              </div>
            </td>

            <!-- Duration -->
            <td class="py-3 pr-4 tabular-nums text-[var(--color-text-secondary)]">
              {{ formatDuration(job) }}
            </td>

            <!-- Started -->
            <td class="py-3 text-[var(--color-text-secondary)] whitespace-nowrap">
              {{ formatTime(job.started_at) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Start Crawl Dialog -->
    <StartCrawlDialog
      v-if="showStartDialog"
      :domains="domains"
      @start="handleStartCrawl"
      @cancel="showStartDialog = false"
    />
  </div>
</template>
