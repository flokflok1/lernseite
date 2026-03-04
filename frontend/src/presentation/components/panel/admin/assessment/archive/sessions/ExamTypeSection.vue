<!--
  ExamTypeSection - Renders one exam type (e.g. "IHK FISI") with its regions and sessions.
  Groups sessions by region, each region collapsible.
-->

<template>
  <div class="space-y-4">
    <!-- Exam Type Header -->
    <div class="flex items-center gap-3">
      <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
        {{ displayName }}
      </h2>
      <span
        v-if="group.parts?.length"
        class="text-xs text-[var(--color-text-secondary)]"
      >
        {{ group.parts.join(', ') }}
      </span>
      <span class="text-xs text-[var(--color-text-secondary)]">
        {{ t('panel.examArchive.examCount', { count: totalSessions }) }}
      </span>
    </div>

    <!-- Regions -->
    <div
      v-for="(region, regionCode) in group.regions"
      :key="regionCode"
      class="ml-2"
    >
      <button
        class="flex items-center gap-2 mb-2 text-sm font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
        @click="toggleRegion(regionCode as string)"
      >
        <svg
          class="w-3.5 h-3.5 transition-transform"
          :class="{ 'rotate-90': expandedRegions.has(regionCode as string) }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
        {{ regionDisplayName(region) }}
        <span class="text-xs opacity-60">
          ({{ region.sessions.length }})
        </span>
      </button>

      <!-- Sessions within region -->
      <div
        v-if="expandedRegions.has(regionCode as string)"
        class="ml-4 space-y-2"
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
