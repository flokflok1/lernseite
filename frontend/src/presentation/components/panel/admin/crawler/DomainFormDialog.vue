<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type {
  CrawlDomain,
  CreateDomainPayload,
  UpdateDomainPayload,
} from '@/infrastructure/api/clients/panel/admin/crawler'

const { t } = useI18n()

type DomainFormData = CreateDomainPayload & Partial<UpdateDomainPayload>

const props = defineProps<{
  domain?: CrawlDomain | null
}>()

const emit = defineEmits<{
  save: [data: DomainFormData]
  cancel: []
}>()

const defaults = {
  domain_name: '',
  base_url: '',
  display_name: '',
  url_patterns_text: '',
  crawl_schedule: 'monthly' as string,
  rate_limit_seconds: 1.5,
  max_pages_per_crawl: 500,
  max_depth: 3,
  is_active: true,
}

const form = ref({ ...defaults })
const isEdit = computed(() => !!props.domain)

watch(
  () => props.domain,
  (d) => {
    if (d) {
      form.value = {
        domain_name: d.domain_name,
        base_url: d.base_url,
        display_name: d.display_name,
        url_patterns_text: (d.url_patterns || []).join('\n'),
        crawl_schedule: d.crawl_schedule,
        rate_limit_seconds: d.rate_limit_seconds,
        max_pages_per_crawl: d.max_pages_per_crawl,
        max_depth: d.max_depth,
        is_active: d.is_active,
      }
    } else {
      form.value = { ...defaults }
    }
  },
  { immediate: true },
)

const canSave = computed(() => {
  const f = form.value
  return f.domain_name.trim() !== '' && f.base_url.trim() !== '' && f.display_name.trim() !== ''
})

function handleSubmit() {
  if (!canSave.value) return
  const { url_patterns_text, ...rest } = form.value
  const data: DomainFormData = {
    ...rest,
    url_patterns: url_patterns_text
      .split('\n')
      .map((p) => p.trim())
      .filter(Boolean),
  }
  emit('save', data)
}

const schedules = ['daily', 'weekly', 'monthly'] as const
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="emit('cancel')">
    <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg shadow-xl w-full max-w-lg mx-4">
      <!-- Header -->
      <div class="flex items-center justify-between px-5 py-4 border-b border-[var(--color-border)]">
        <h3 class="text-lg font-semibold">
          {{ isEdit ? t('panel.crawler.domains.editDomain') : t('panel.crawler.domains.addDomain') }}
        </h3>
        <button class="text-[var(--color-text-secondary)] hover:text-[var(--color-text)] text-xl leading-none" @click="emit('cancel')">
          &times;
        </button>
      </div>

      <!-- Form -->
      <form class="px-5 py-4 space-y-4 max-h-[70vh] overflow-y-auto" @submit.prevent="handleSubmit">
        <!-- Domain Name -->
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('panel.crawler.domains.name') }} *</label>
          <input
            v-model="form.domain_name"
            type="text"
            :disabled="isEdit"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text)] disabled:opacity-50"
            placeholder="example.com"
          />
        </div>

        <!-- Base URL -->
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('panel.crawler.domains.baseUrl') }} *</label>
          <input
            v-model="form.base_url"
            type="text"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text)]"
            placeholder="https://example.com"
          />
        </div>

        <!-- Display Name -->
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('panel.crawler.domains.displayName') }} *</label>
          <input
            v-model="form.display_name"
            type="text"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text)]"
          />
        </div>

        <!-- URL Patterns -->
        <div>
          <label class="block text-sm font-medium mb-1">{{ t('panel.crawler.domains.urlPatterns') }}</label>
          <textarea
            v-model="form.url_patterns_text"
            rows="3"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text)] text-sm"
            :placeholder="t('panel.crawler.domains.urlPatternsHint')"
          />
          <p class="text-xs text-[var(--color-text-secondary)] mt-1">
            {{ t('panel.crawler.domains.urlPatternsHint') }}
          </p>
        </div>

        <!-- Schedule + Rate Limit row -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('panel.crawler.domains.schedule') }}</label>
            <select
              v-model="form.crawl_schedule"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text)]"
            >
              <option v-for="s in schedules" :key="s" :value="s">
                {{ t(`panel.crawler.domains.scheduleOptions.${s}`) }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('panel.crawler.domains.rateLimit') }}</label>
            <input
              v-model.number="form.rate_limit_seconds"
              type="number"
              step="0.5"
              min="0.5"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text)]"
            />
          </div>
        </div>

        <!-- Max Pages + Max Depth row -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('panel.crawler.domains.maxPages') }}</label>
            <input
              v-model.number="form.max_pages_per_crawl"
              type="number"
              min="1"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text)]"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">{{ t('panel.crawler.domains.maxDepth') }}</label>
            <input
              v-model.number="form.max_depth"
              type="number"
              min="1"
              max="10"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text)]"
            />
          </div>
        </div>

        <!-- Active toggle -->
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded" />
          <span class="text-sm">{{ t('panel.crawler.domains.active') }}</span>
        </label>
      </form>

      <!-- Footer -->
      <div class="flex justify-end gap-3 px-5 py-4 border-t border-[var(--color-border)]">
        <button
          class="px-4 py-2 text-sm border border-[var(--color-border)] rounded hover:bg-[var(--color-bg)] transition-colors"
          @click="emit('cancel')"
        >
          {{ t('panel.crawler.domainForm.cancel') }}
        </button>
        <button
          class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded hover:opacity-90 transition-opacity disabled:opacity-50"
          :disabled="!canSave"
          @click="handleSubmit"
        >
          {{ t('panel.crawler.domainForm.save') }}
        </button>
      </div>
    </div>
  </div>
</template>
