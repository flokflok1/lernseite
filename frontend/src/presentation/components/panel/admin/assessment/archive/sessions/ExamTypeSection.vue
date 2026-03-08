<!--
  ExamTypeSection - Renders one exam type (e.g. "IHK FISI") with its regions and sessions.
  Groups sessions by region, each region collapsible.
-->

<template>
  <div class="space-y-5">
    <!-- Exam Type Header Card -->
    <div
      class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] border-l-4 border-l-[var(--color-primary)] px-5 py-4"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <!-- Document Icon -->
          <div class="w-9 h-9 rounded-lg bg-[var(--color-primary-bg,#ede9fe)] flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
            </svg>
          </div>

          <div>
            <h2 class="text-base font-semibold text-[var(--color-text-primary)] leading-tight">
              {{ displayName }}
            </h2>
            <div class="flex items-center gap-2 mt-1">
              <!-- Parts as pills -->
              <span
                v-for="part in (group.parts || [])"
                :key="part"
                class="inline-flex px-2 py-0.5 rounded-md text-xs font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]"
              >
                {{ part }}
              </span>
            </div>
          </div>
        </div>

        <!-- Session count badge -->
        <div class="px-3 py-1 rounded-full bg-[var(--color-primary-bg,#ede9fe)] text-[var(--color-primary-text,#6d28d9)] text-xs font-semibold">
          {{ t('panel.examArchive.examCount', { count: totalSessions }) }}
        </div>
      </div>
    </div>

    <!-- Regions -->
    <div
      v-for="(region, regionCode) in group.regions"
      :key="regionCode"
      class="ml-3"
    >
      <!-- Region Toggle Header -->
      <button
        class="group w-full flex items-center gap-3 mb-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all hover:bg-[var(--color-surface-secondary)]"
        :class="expandedRegions.has(regionCode as string)
          ? 'bg-[var(--color-surface)] text-[var(--color-text-primary)] border border-[var(--color-border)]'
          : 'text-[var(--color-text-secondary)]'"
        @click="toggleRegion(regionCode as string)"
      >
        <svg
          class="w-4 h-4 transition-transform duration-200 flex-shrink-0"
          :class="{ 'rotate-90': expandedRegions.has(regionCode as string) }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>

        <!-- Region icon -->
        <svg class="w-4 h-4 flex-shrink-0 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
        </svg>

        <span class="flex-1 text-left">{{ regionDisplayName(region) }}</span>

        <!-- Session count badge -->
        <span class="px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
          {{ region.sessions.length }}
        </span>
      </button>

      <!-- Sessions within region -->
      <div
        v-if="expandedRegions.has(regionCode as string)"
        class="ml-5 space-y-2.5 pb-2"
      >
        <ExamSessionCard
          v-for="session in region.sessions"
          :key="session.session_id"
          :session="session"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SessionGroup, SessionRegion } from '@/infrastructure/api/clients/panel/admin/exams/archive.api'
import ExamSessionCard from './ExamSessionCard.vue'

interface Props {
  group: SessionGroup
}

const props = defineProps<Props>()
const { t, locale } = useI18n()

// All regions expanded by default
const expandedRegions = ref<Set<string>>(
  new Set(Object.keys(props.group.regions))
)

const displayName = computed(() => {
  const names = props.group.display_name
  return names?.[locale.value] || names?.de || props.group.exam_type
})

const totalSessions = computed(() =>
  Object.values(props.group.regions).reduce(
    (sum, r) => sum + r.sessions.length, 0
  )
)

const regionDisplayName = (region: SessionRegion): string => {
  if (!region.region_name) return region.region_code
  return (region.region_name as Record<string, string>)[locale.value]
    || (region.region_name as Record<string, string>).de
    || region.region_code
}

const toggleRegion = (code: string) => {
  if (expandedRegions.value.has(code)) {
    expandedRegions.value.delete(code)
  } else {
    expandedRegions.value.add(code)
  }
}
</script>
