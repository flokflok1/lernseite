<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
import { useCrawlManagement } from '@/application/composables/panel/admin/crawler'
import DomainFormDialog from './DomainFormDialog.vue'
import type {
  CrawlDomain,
  CreateDomainPayload,
} from '@/infrastructure/api/clients/panel/admin/crawler'

const { t } = useI18n()
const store = useCrawlManagement()
const { domains } = storeToRefs(store)
const { loadDomains, addDomain, editDomain, removeDomain } = store

const showForm = ref(false)
const editingDomain = ref<CrawlDomain | null>(null)
const confirmDeleteId = ref<string | null>(null)

onMounted(() => loadDomains())

function openAdd() {
  editingDomain.value = null
  showForm.value = true
}

function openEdit(domain: CrawlDomain) {
  editingDomain.value = domain
  showForm.value = true
}

async function handleSave(data: CreateDomainPayload) {
  if (editingDomain.value) {
    await editDomain(editingDomain.value.domain_id, data)
  } else {
    await addDomain(data)
  }
  showForm.value = false
  editingDomain.value = null
}

async function handleDelete() {
  if (confirmDeleteId.value) {
    await removeDomain(confirmDeleteId.value)
    confirmDeleteId.value = null
  }
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return t('panel.crawler.dashboard.neverCrawled')
  return new Date(dateStr).toLocaleDateString()
}

function scheduleClass(schedule: string): string {
  const map: Record<string, string> = {
    daily: 'bg-blue-100 text-blue-700',
    weekly: 'bg-purple-100 text-purple-700',
    monthly: 'bg-gray-100 text-gray-600',
  }
  return map[schedule] || map.monthly
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold">{{ t('panel.crawler.domains.title') }}</h2>
      <button
        class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded hover:opacity-90 transition-opacity"
        @click="openAdd"
      >
        {{ t('panel.crawler.domains.addDomain') }}
      </button>
    </div>

    <!-- Empty state -->
    <div
      v-if="domains.length === 0"
      class="text-center py-12 text-[var(--color-text-secondary)] bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"
    >
      <p class="text-lg">{{ t('panel.crawler.domains.noDomains') }}</p>
    </div>

    <!-- Domain Cards -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div
        v-for="domain in domains"
        :key="domain.domain_id"
        class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4"
      >
        <!-- Card Header: Name + Status -->
        <div class="flex items-start justify-between mb-3">
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold truncate">{{ domain.display_name }}</h3>
            <p class="text-sm text-[var(--color-text-secondary)] truncate">{{ domain.domain_name }}</p>
          </div>
          <div class="flex items-center gap-2 ml-3 shrink-0">
            <span
              class="px-2 py-0.5 rounded-full text-xs font-medium"
              :class="scheduleClass(domain.crawl_schedule)"
            >
              {{ t(`panel.crawler.domains.scheduleOptions.${domain.crawl_schedule}`) }}
            </span>
            <span
              class="px-2 py-0.5 rounded-full text-xs font-medium"
              :class="domain.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'"
            >
              {{ domain.is_active ? t('panel.crawler.domains.active') : t('panel.crawler.domains.inactive') }}
            </span>
          </div>
        </div>

        <!-- URL Patterns as tags -->
        <div v-if="domain.url_patterns?.length" class="flex flex-wrap gap-1 mb-3">
          <span
            v-for="(pattern, idx) in domain.url_patterns"
            :key="idx"
            class="px-2 py-0.5 bg-[var(--color-bg)] border border-[var(--color-border)] rounded text-xs font-mono truncate max-w-[200px]"
            :title="pattern"
          >
            {{ pattern }}
          </span>
        </div>

        <!-- Stats row -->
        <div class="grid grid-cols-3 gap-3 text-sm text-[var(--color-text-secondary)] mb-3">
          <div>
            <span class="block text-xs uppercase tracking-wide">{{ t('panel.crawler.domains.rateLimit') }}</span>
            <span class="font-medium text-[var(--color-text)]">{{ domain.rate_limit_seconds }}s</span>
          </div>
          <div>
            <span class="block text-xs uppercase tracking-wide">{{ t('panel.crawler.domains.maxPages') }}</span>
            <span class="font-medium text-[var(--color-text)]">{{ domain.max_pages_per_crawl }}</span>
          </div>
          <div>
            <span class="block text-xs uppercase tracking-wide">{{ t('panel.crawler.domains.maxDepth') }}</span>
            <span class="font-medium text-[var(--color-text)]">{{ domain.max_depth }}</span>
          </div>
        </div>

        <!-- Crawl info -->
        <div class="flex items-center justify-between text-sm text-[var(--color-text-secondary)] mb-3">
          <span>{{ t('panel.crawler.domains.lastCrawled') }}: {{ formatDate(domain.last_crawled_at) }}</span>
          <span>{{ t('panel.crawler.domains.pdfsFound') }}: {{ domain.total_pdfs_found }}</span>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-2 border-t border-[var(--color-border)]">
          <button
            class="px-3 py-1.5 text-sm border border-[var(--color-border)] rounded hover:bg-[var(--color-bg)] transition-colors"
            @click="openEdit(domain)"
          >
            {{ t('panel.crawler.domains.editDomain') }}
          </button>
          <button
            class="px-3 py-1.5 text-sm text-red-600 border border-red-200 rounded hover:bg-red-50 transition-colors"
            @click="confirmDeleteId = domain.domain_id"
          >
            {{ t('panel.crawler.pdfs.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="confirmDeleteId"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      @click.self="confirmDeleteId = null"
    >
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg shadow-xl p-6 max-w-sm mx-4">
        <p class="mb-4">{{ t('panel.crawler.domains.confirmDelete') }}</p>
        <div class="flex justify-end gap-3">
          <button
            class="px-4 py-2 text-sm border border-[var(--color-border)] rounded hover:bg-[var(--color-bg)] transition-colors"
            @click="confirmDeleteId = null"
          >
            {{ t('panel.crawler.domainForm.cancel') }}
          </button>
          <button
            class="px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            @click="handleDelete"
          >
            {{ t('panel.crawler.pdfs.delete') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Domain Form Dialog -->
    <DomainFormDialog
      v-if="showForm"
      :domain="editingDomain"
      @save="handleSave"
      @cancel="showForm = false; editingDomain = null"
    />
  </div>
</template>
