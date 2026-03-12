<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { useCrawlManagement } from '@/application/composables/panel/admin/crawler'

const { t } = useI18n()
const store = useCrawlManagement()
const { pdfs, domains, totalPdfs, loading } = storeToRefs(store)
const { loadPdfs, loadDomains, removePdf } = store

const search = ref('')
const domainFilter = ref('')
const page = ref(1)
const perPage = 20
const confirmDeleteId = ref<string | null>(null)

let searchTimeout: ReturnType<typeof setTimeout> | null = null

const totalPages = computed(() => Math.max(1, Math.ceil(totalPdfs.value / perPage)))

onMounted(async () => {
  await loadDomains()
  await fetchPdfs()
})

onUnmounted(() => {
  if (searchTimeout) clearTimeout(searchTimeout)
})

async function fetchPdfs() {
  await loadPdfs({
    page: page.value,
    per_page: perPage,
    search: search.value || undefined,
    domain_id: domainFilter.value || undefined,
  })
}

function onSearchInput() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    page.value = 1
    fetchPdfs()
  }, 300)
}

function onDomainChange() {
  page.value = 1
  fetchPdfs()
}

function goPage(delta: number) {
  const target = page.value + delta
  if (target >= 1 && target <= totalPages.value) {
    page.value = target
    fetchPdfs()
  }
}

function requestDelete(urlId: string) {
  confirmDeleteId.value = urlId
}

async function handleDelete() {
  if (!confirmDeleteId.value) return
  await removePdf(confirmDeleteId.value)
  confirmDeleteId.value = null
  await fetchPdfs()
}

function formatSize(bytes: number | null): string {
  if (!bytes) return '-'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function relevanceClass(score: number): string {
  if (score >= 0.7) return 'bg-green-100 text-green-700'
  if (score >= 0.4) return 'bg-yellow-100 text-yellow-700'
  return 'bg-red-100 text-red-700'
}

function truncateUrl(url: string, maxLen = 60): string {
  return url.length > maxLen ? url.slice(0, maxLen) + '...' : url
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}
</script>

<template>
  <div class="space-y-4">
    <!-- Filter bar -->
    <div class="flex flex-col sm:flex-row gap-3">
      <input
        v-model="search"
        type="text"
        :placeholder="t('panel.crawler.pdfs.search')"
        class="flex-1 px-3 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] placeholder-[var(--color-text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        @input="onSearchInput"
      />
      <select
        v-model="domainFilter"
        class="px-3 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        @change="onDomainChange"
      >
        <option value="">
          {{ t('panel.crawler.pdfs.domain') }} — {{ t('panel.crawler.startDialog.allDomains') }}
        </option>
        <option v-for="d in domains" :key="d.domain_id" :value="d.domain_id">
          {{ d.display_name }}
        </option>
      </select>
    </div>

    <!-- Loading spinner -->
    <div v-if="loading && pdfs.length === 0" class="flex justify-center p-8">
      <div
        class="animate-spin h-6 w-6 border-2 border-[var(--color-primary)] border-t-transparent rounded-full"
      />
    </div>

    <!-- Empty state -->
    <div
      v-else-if="pdfs.length === 0"
      class="text-center py-12 text-[var(--color-text-secondary)]"
    >
      {{ t('panel.crawler.pdfs.noResults') }}
    </div>

    <!-- PDF Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-[var(--color-border)] text-left text-[var(--color-text-secondary)]">
            <th class="pb-2 pr-4 font-medium">URL</th>
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.pdfs.domain') }}</th>
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.pdfs.relevance') }}</th>
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.pdfs.pages') }}</th>
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.pdfs.size') }}</th>
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.pdfs.textQuality') }}</th>
            <th class="pb-2 pr-4 font-medium">{{ t('panel.crawler.pdfs.lastChecked') }}</th>
            <th class="pb-2 font-medium" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="pdf in pdfs"
            :key="pdf.url_id"
            class="border-b border-[var(--color-border)] hover:bg-[var(--color-surface-hover,var(--color-surface))]"
          >
            <!-- URL -->
            <td class="py-2 pr-4 max-w-[300px]">
              <a
                :href="pdf.url"
                target="_blank"
                rel="noopener"
                :title="pdf.url"
                class="text-[var(--color-primary)] hover:underline"
              >
                {{ truncateUrl(pdf.url) }}
              </a>
            </td>

            <!-- Domain -->
            <td class="py-2 pr-4 whitespace-nowrap">{{ pdf.domain_name }}</td>

            <!-- Relevance -->
            <td class="py-2 pr-4">
              <span
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                :class="relevanceClass(pdf.relevance_score)"
                :title="pdf.relevance_reason || ''"
              >
                {{ (pdf.relevance_score * 100).toFixed(0) }}%
              </span>
            </td>

            <!-- Pages -->
            <td class="py-2 pr-4 whitespace-nowrap">
              {{ pdf.page_count ?? '-' }}
            </td>

            <!-- Size -->
            <td class="py-2 pr-4 whitespace-nowrap">
              {{ formatSize(pdf.file_size_bytes) }}
            </td>

            <!-- Text Quality -->
            <td class="py-2 pr-4 whitespace-nowrap">
              <span v-if="pdf.has_extractable_text === true" class="text-green-600">
                {{ t('panel.crawler.pdfs.hasText') }}
              </span>
              <span v-else-if="pdf.has_extractable_text === false" class="text-red-500">
                {{ t('panel.crawler.pdfs.noText') }}
              </span>
              <span v-else class="text-[var(--color-text-secondary)]">
                {{ t('panel.crawler.pdfs.unknown') }}
              </span>
            </td>

            <!-- Date -->
            <td class="py-2 pr-4 whitespace-nowrap text-[var(--color-text-secondary)]">
              {{ formatDate(pdf.last_checked_at) }}
            </td>

            <!-- Delete -->
            <td class="py-2">
              <button
                class="text-red-500 hover:text-red-700 text-xs px-2 py-1 rounded hover:bg-red-50 transition-colors"
                :title="t('panel.crawler.pdfs.delete')"
                @click="requestDelete(pdf.url_id)"
              >
                {{ t('panel.crawler.pdfs.delete') }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="totalPages > 1"
      class="flex items-center justify-between pt-2"
    >
      <button
        :disabled="page <= 1"
        class="px-3 py-1.5 text-sm rounded border border-[var(--color-border)] bg-[var(--color-surface)] disabled:opacity-40 hover:bg-[var(--color-surface-hover,var(--color-surface))] transition-colors"
        @click="goPage(-1)"
      >
        &larr;
      </button>
      <span class="text-sm text-[var(--color-text-secondary)]">
        {{ page }} / {{ totalPages }}
      </span>
      <button
        :disabled="page >= totalPages"
        class="px-3 py-1.5 text-sm rounded border border-[var(--color-border)] bg-[var(--color-surface)] disabled:opacity-40 hover:bg-[var(--color-surface-hover,var(--color-surface))] transition-colors"
        @click="goPage(1)"
      >
        &rarr;
      </button>
    </div>

    <!-- Confirm delete dialog -->
    <Teleport to="body">
      <div
        v-if="confirmDeleteId"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
        @click.self="confirmDeleteId = null"
      >
        <div class="bg-[var(--color-surface)] rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
          <p class="text-[var(--color-text)] mb-4">
            {{ t('panel.crawler.pdfs.confirmDelete') }}
          </p>
          <div class="flex justify-end gap-3">
            <button
              class="px-4 py-2 text-sm rounded border border-[var(--color-border)] hover:bg-[var(--color-surface-hover,var(--color-surface))] transition-colors"
              @click="confirmDeleteId = null"
            >
              {{ t('panel.crawler.startDialog.cancel') }}
            </button>
            <button
              class="px-4 py-2 text-sm rounded bg-red-600 text-white hover:bg-red-700 transition-colors"
              @click="handleDelete"
            >
              {{ t('panel.crawler.pdfs.delete') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
