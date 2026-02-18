<!--
  Method Type Selector Modal

  Displays a modal for selecting a learning method type to create.
  Shows method types grouped by categories (A-F) with tier badges.
-->

<template>
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
      <!-- Header -->
      <div class="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
          Lernmethode auswählen
        </h3>
        <button
          @click="$emit('close')"
          class="p-1 rounded hover:bg-[var(--color-background)]"
        >
          <svg class="w-5 h-5 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Group Tabs -->
      <div class="flex border-b border-[var(--color-border)] bg-[var(--color-background)]">
        <button
          v-for="group in methodGroups"
          :key="group.id"
          @click="activeGroup = group.id"
          :class="[
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
            activeGroup === group.id
              ? 'border-[var(--color-primary)] text-[var(--color-primary)]'
              : 'border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
          ]"
        >
          {{ group.label }}
        </button>
      </div>

      <!-- Method Types List -->
      <div class="p-4 overflow-y-auto max-h-[50vh]">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <button
            v-for="methodType in filteredMethodTypes"
            :key="methodType.lm_id"
            @click="$emit('select', methodType)"
            class="text-left p-3 rounded-lg border border-[var(--color-border)] hover:border-[var(--color-primary)] hover:bg-[var(--color-primary)]/5 transition-colors"
          >
            <div class="flex items-center gap-3">
              <span
                class="text-sm font-mono px-2 py-1 rounded"
                :style="getGroupStyle(methodType.group)"
              >
                {{ String(getGroupPosition(methodType)).padStart(2, '0') }}
              </span>
              <div class="flex-1">
                <p class="font-medium text-[var(--color-text-primary)]">{{ methodType.name }}</p>
                <p class="text-xs text-[var(--color-text-secondary)]">{{ methodType.description }}</p>
              </div>
              <span
                class="text-xs px-2 py-0.5 rounded"
                :style="getTierStyle(getTierFromGroup(methodType.group))"
              >
                {{ getTierLabel(getTierFromGroup(methodType.group)) }}
              </span>
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { LearningMethodType, LearningMethodGroup } from '@/application/services/api/panel-admin'

interface Props {
  methodTypes: LearningMethodType[]
  methodGroups: Array<{ id: LearningMethodGroup; label: string; count: number }>
  initialGroup?: LearningMethodGroup
  getGroupStyle: (group: LearningMethodGroup) => string
  getGroupPosition: (methodType: LearningMethodType) => number
  getTierStyle: (tier: string) => string
  getTierLabel: (tier: string) => string
  getTierFromGroup: (group: LearningMethodGroup) => 'basic' | 'premium' | 'pro'
}

interface Emits {
  (e: 'close'): void
  (e: 'select', methodType: LearningMethodType): void
}

const props = withDefaults(defineProps<Props>(), {
  initialGroup: 'A'
})
defineEmits<Emits>()

const activeGroup = ref<LearningMethodGroup>(props.initialGroup)

const filteredMethodTypes = computed((): LearningMethodType[] => {
  return props.methodTypes.filter(mt => mt.group === activeGroup.value)
})
</script>
