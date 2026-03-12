<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { CrawlDomain } from '@/infrastructure/api/clients/panel/admin/crawler'

const { t } = useI18n()

defineProps<{
  domains: CrawlDomain[]
}>()

const emit = defineEmits<{
  start: [domainId?: string]
  cancel: []
}>()

const mode = ref<'all' | 'single'>('all')
const selectedDomainId = ref('')

function handleStart() {
  emit('start', mode.value === 'single' ? selectedDomainId.value : undefined)
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="emit('cancel')"
  >
    <div class="bg-[var(--color-surface)] rounded-lg shadow-xl p-6 w-full max-w-md">
      <h3 class="text-lg font-semibold mb-2">
        {{ t('panel.crawler.startDialog.title') }}
      </h3>
      <p class="text-sm text-[var(--color-text-secondary)] mb-4">
        {{ t('panel.crawler.startDialog.description') }}
      </p>

      <div class="space-y-3 mb-6">
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            v-model="mode"
            type="radio"
            value="all"
            class="text-[var(--color-primary)]"
          />
          <span>{{ t('panel.crawler.startDialog.allDomains') }}</span>
        </label>

        <label class="flex items-center gap-2 cursor-pointer">
          <input
            v-model="mode"
            type="radio"
            value="single"
            class="text-[var(--color-primary)]"
          />
          <span>{{ t('panel.crawler.startDialog.singleDomain') }}</span>
        </label>

        <select
          v-if="mode === 'single'"
          v-model="selectedDomainId"
          class="w-full border border-[var(--color-border)] rounded px-3 py-2 bg-[var(--color-surface)]"
        >
          <option value="">{{ t('panel.crawler.startDialog.selectDomain') }}</option>
          <option v-for="d in domains" :key="d.domain_id" :value="d.domain_id">
            {{ d.display_name }}
          </option>
        </select>
      </div>

      <div class="flex justify-end gap-2">
        <button
          class="px-4 py-2 text-sm border border-[var(--color-border)] rounded hover:bg-[var(--color-surface-hover)] transition-colors"
          @click="emit('cancel')"
        >
          {{ t('panel.crawler.startDialog.cancel') }}
        </button>
        <button
          class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="mode === 'single' && !selectedDomainId"
          @click="handleStart"
        >
          {{ t('panel.crawler.startDialog.start') }}
        </button>
      </div>
    </div>
  </div>
</template>
