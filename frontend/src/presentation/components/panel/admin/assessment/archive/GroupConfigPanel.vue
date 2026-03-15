<!-- GroupConfigPanel — Admin UI to reorder/toggle folder grouping levels. -->
<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { GroupLevel } from '@/application/composables/panel/admin/assessment'

interface Props {
  levels: GroupLevel[]
}

defineProps<Props>()

const emit = defineEmits<{
  toggle: [field: string]
  moveUp: [index: number]
  moveDown: [index: number]
  reset: []
}>()

const { t } = useI18n()

const open = ref(false)
</script>

<template>
  <div class="relative">
    <!-- Trigger button -->
    <button
      class="p-2 rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-surface)] transition-colors"
      :title="t('panel.examArchive.groupBy.title')"
      @click="open = !open"
    >
      <svg class="w-4 h-4 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12" />
      </svg>
    </button>

    <!-- Popover -->
    <Teleport to="body">
      <div
        v-if="open"
        class="fixed inset-0 z-40"
        @click="open = false"
      />
    </Teleport>

    <div
      v-if="open"
      class="absolute right-0 top-full mt-2 z-50 w-72 bg-[var(--color-surface)] rounded-xl shadow-xl border border-[var(--color-border)] p-4"
    >
      <div class="flex items-center justify-between mb-3">
        <h4 class="text-sm font-semibold text-[var(--color-text-primary)]">
          {{ t('panel.examArchive.groupBy.title') }}
        </h4>
        <button
          @click="emit('reset')"
          class="text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] transition-colors"
        >
          {{ t('panel.examArchive.groupBy.reset') }}
        </button>
      </div>

      <p class="text-xs text-[var(--color-text-secondary)] mb-3">
        {{ t('panel.examArchive.groupBy.hint') }}
      </p>

      <div class="space-y-1.5">
        <div
          v-for="(level, index) in levels"
          :key="level.field"
          class="flex items-center gap-2 px-2.5 py-2 rounded-lg border transition-colors"
          :class="level.enabled
            ? 'border-[var(--color-primary)]/30 bg-[var(--color-primary-bg,#ede9fe)]'
            : 'border-[var(--color-border)] bg-[var(--color-bg)]'"
        >
          <!-- Checkbox -->
          <button
            @click="emit('toggle', level.field)"
            class="w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 transition-colors"
            :class="level.enabled
              ? 'bg-[var(--color-primary)] border-[var(--color-primary)]'
              : 'border-[var(--color-border)] bg-[var(--color-bg)]'"
          >
            <svg v-if="level.enabled" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
          </button>

          <!-- Label -->
          <span
            class="flex-1 text-sm"
            :class="level.enabled
              ? 'text-[var(--color-text-primary)] font-medium'
              : 'text-[var(--color-text-secondary)]'"
          >
            {{ t(level.labelKey) }}
          </span>

          <!-- Order position (enabled only) -->
          <span
            v-if="level.enabled"
            class="w-5 h-5 rounded-full bg-[var(--color-primary)] text-white text-[10px] font-bold flex items-center justify-center"
          >
            {{ levels.filter(l => l.enabled).indexOf(level) + 1 }}
          </span>

          <!-- Up/Down arrows -->
          <div class="flex flex-col gap-0.5">
            <button
              :disabled="index === 0"
              @click="emit('moveUp', index)"
              class="p-0.5 rounded hover:bg-[var(--color-surface-secondary)] disabled:opacity-20 transition-all"
            >
              <svg class="w-3 h-3 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
            </button>
            <button
              :disabled="index === levels.length - 1"
              @click="emit('moveDown', index)"
              class="p-0.5 rounded hover:bg-[var(--color-surface-secondary)] disabled:opacity-20 transition-all"
            >
              <svg class="w-3 h-3 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
