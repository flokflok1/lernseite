<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { UserProgram } from '@/infrastructure/api/clients/panel/user/programs.api'

const props = defineProps<{
  programs: UserProgram[]
  activeId: number | null
}>()

const emit = defineEmits<{
  select: [program: UserProgram]
}>()

const { t, locale } = useI18n()
const search = ref('')

const displayName = (obj: Record<string, string>) =>
  obj[locale.value] || obj.de || ''

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  if (!q) return props.programs
  return props.programs.filter(p =>
    displayName(p.display_name).toLowerCase().includes(q)
  )
})

const grouped = computed(() => {
  const groups: Record<string, UserProgram[]> = {}
  for (const p of filtered.value) {
    const typeLabel = p.type_display_name
      ? displayName(p.type_display_name)
      : p.program_type
    groups[typeLabel] = groups[typeLabel] || []
    groups[typeLabel].push(p)
  }
  return groups
})
</script>

<template>
  <div class="w-64 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-surface)] h-full overflow-y-auto">
    <!-- Search -->
    <div class="p-3">
      <input
        v-model="search"
        type="text"
        :placeholder="t('panel.programs.catalog.search')"
        class="w-full px-3 py-2 text-sm rounded-lg border border-[var(--color-border)]
               bg-[var(--color-background)] text-[var(--color-text)]
               focus:outline-none focus:border-blue-500"
      />
    </div>

    <!-- Grouped programs -->
    <div v-for="(progs, typeLabel) in grouped" :key="typeLabel" class="mb-2">
      <div class="px-3 py-1 text-xs font-semibold uppercase text-[var(--color-text-secondary)] tracking-wider">
        {{ typeLabel }}
      </div>
      <button
        v-for="p in progs"
        :key="p.program_id"
        class="w-full text-left px-3 py-2.5 text-sm transition-colors flex items-center gap-2"
        :class="p.program_id === activeId
          ? 'bg-blue-500/10 text-blue-400 border-r-2 border-blue-500'
          : 'text-[var(--color-text)] hover:bg-[var(--color-background)]'"
        @click="emit('select', p)"
      >
        <span v-if="p.icon" class="text-base">{{ p.icon }}</span>
        <span class="truncate">{{ displayName(p.display_name) }}</span>
      </button>
    </div>

    <!-- Empty state -->
    <div v-if="filtered.length === 0" class="p-4 text-center text-sm text-[var(--color-text-secondary)]">
      {{ t('panel.programs.catalog.noPrograms') }}
    </div>
  </div>
</template>
