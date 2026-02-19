<template>
  <div class="catalog-tab-container">
    <!-- Fixed Header -->
    <div class="catalog-header">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-1">
        Lernmethoden-Katalog
      </h3>
      <!-- Group Tabs -->
      <div class="flex gap-1 mt-3">
        <button
          v-for="group in methodGroups"
          :key="group.id"
          @click="$emit('update:catalogActiveGroup', group.id)"
          :class="[
            'px-3 py-1.5 text-xs font-medium rounded-lg transition-all',
            catalogActiveGroup === group.id
              ? 'text-white shadow-sm'
              : 'bg-[var(--color-background)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
          ]"
          :style="catalogActiveGroup === group.id ? getGroupStyleFilled(group.id) : ''"
        >
          {{ group.label }} ({{ group.count }})
        </button>
      </div>
    </div>

    <!-- Scrollable Content -->
    <div class="catalog-content">
      <div class="space-y-2">
        <div
          v-for="methodType in getMethodsByGroup(catalogActiveGroup)"
          :key="methodType.lm_id"
          @click="$emit('create-method', methodType)"
          class="method-type-card bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-3 hover:border-[var(--color-primary)] hover:shadow-md transition-all cursor-pointer"
        >
          <div class="flex items-center gap-3">
            <div
              class="w-9 h-9 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0"
              :style="getGroupStyle(methodType.group)"
            >
              {{ String(getGroupPosition(methodType)).padStart(2, '0') }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h4 class="font-semibold text-[var(--color-text-primary)] text-sm">{{ methodType.name }}</h4>
                <span
                  class="text-xs px-1.5 py-0.5 rounded"
                  :style="getTierStyle(getTierFromGroup(methodType.group))"
                >
                  {{ getTierLabel(getTierFromGroup(methodType.group)) }}
                </span>
              </div>
              <p class="text-xs text-[var(--color-text-secondary)] mt-0.5">{{ methodType.description }}</p>
            </div>
            <svg class="w-4 h-4 text-[var(--color-text-tertiary)] flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LearningMethodType, LearningMethodGroup } from '@/infrastructure/api/clients/panel/admin'

interface Props {
  catalogActiveGroup: LearningMethodGroup
  methodGroups: Array<{ id: LearningMethodGroup; label: string; count: number }>
  getMethodsByGroup: (groupId: LearningMethodGroup) => LearningMethodType[]
  getGroupStyle: (group: string) => string
  getGroupStyleFilled: (group: string) => string
  getGroupPosition: (methodType: LearningMethodType) => number
  getTierStyle: (tier: string) => string
  getTierLabel: (tier: string) => string
  getTierFromGroup: (group: LearningMethodGroup) => 'basic' | 'premium' | 'pro'
}

interface Emits {
  (e: 'update:catalogActiveGroup', groupId: string): void
  (e: 'create-method', methodType: LearningMethodType): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
/* Catalog Tab Layout - using absolute positioning for reliable scroll */
.catalog-tab-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.catalog-header {
  flex-shrink: 0;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
}

.catalog-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  min-height: 0;
}

/* Method card hover effect */
.method-type-card {
  transition: all 0.15s ease;
}

.method-type-card:hover {
  transform: translateX(4px);
}
</style>
