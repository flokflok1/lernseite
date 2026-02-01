<template>
  <div class="h-full overflow-y-auto p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
        {{ $t('windows.learningMethodEditor.tabs.instances') }} {{ methods.length > 0 ? `(${methods.length})` : '' }}
      </h3>
      <button
        @click="$emit('open-selector')"
        class="px-3 py-1.5 bg-[var(--color-primary)] text-white text-sm rounded-lg hover:opacity-90 transition-colors flex items-center gap-2"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ $t('windows.learningMethodEditor.addMethod') }}
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="methods.length === 0" class="text-center py-12">
      <div class="text-5xl mb-3">🎯</div>
      <p class="text-[var(--color-text-secondary)] mb-2">{{ $t('windows.learningMethodEditor.emptyTitle') }}</p>
      <p class="text-sm text-[var(--color-text-tertiary)]">
        {{ $t('windows.learningMethodEditor.emptyDesc') }}
      </p>
    </div>

    <!-- Methods List with Drag & Drop -->
    <div v-else class="space-y-2">
      <div
        v-for="(method, index) in sortedMethods"
        :key="method.method_id"
        :draggable="true"
        @dragstart="handleDragStart(index)"
        @dragover.prevent="handleDragOver(index)"
        @drop="handleDrop(index)"
        @dragend="handleDragEnd"
        :class="[
          'method-item p-4 rounded-lg border transition-all cursor-move',
          dragState.draggedIndex === index
            ? 'opacity-50 border-[var(--color-primary)]'
            : 'bg-[var(--color-surface)] border-[var(--color-border)] hover:border-[var(--color-primary)]'
        ]"
      >
        <div class="flex items-start justify-between gap-3">
          <!-- Drag Handle + Content -->
          <div class="flex items-center gap-3 flex-1">
            <svg class="w-5 h-5 text-[var(--color-text-tertiary)] flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path d="M7 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 2zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 7 14zm6-8a2 2 0 1 0-.001-4.001A2 2 0 0 0 13 6zm0 2a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 8zm0 6a2 2 0 1 0 .001 4.001A2 2 0 0 0 13 14z"></path>
            </svg>

            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="text-sm font-bold text-[var(--color-text-tertiary)]">
                  {{ method.order_index + 1 }}.
                </span>
                <span
                  class="text-xs px-2 py-0.5 rounded font-mono"
                  :style="getGroupStyle(getMethodGroup(method.method_type))"
                >
                  {{ getGroupPositionById(method.method_type) }}
                </span>
                <h4 class="font-semibold text-[var(--color-text-primary)] truncate">
                  {{ method.title || getMethodTypeName(method.method_type) }}
                </h4>
                <span
                  v-if="method.published"
                  class="text-xs px-2 py-0.5 rounded"
                  style="background-color: var(--color-success-bg, #dcfce7); color: var(--color-success-text, #15803d);"
                >
                  {{ $t('windows.learningMethodEditor.published') }}
                </span>
              </div>
              <div class="flex gap-4 text-xs text-[var(--color-text-secondary)]">
                <span>{{ getMethodTypeName(method.method_type) }}</span>
                <span v-if="method.duration_minutes">{{ method.duration_minutes }} {{ $t('windows.learningMethodEditor.minutes') }}</span>
                <span :style="getTierStyle(method.tier)">{{ getTierLabel(method.tier) }}</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 flex-shrink-0">
            <button
              @click="$emit('edit', method)"
              class="p-1.5 rounded transition-colors"
              style="color: var(--color-text-secondary);"
              :title="$t('windows.learningMethodEditor.edit')"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              @click="togglePublish(method)"
              class="p-1.5 rounded transition-colors"
              :style="method.published ? 'color: var(--color-warning, #ea580c);' : 'color: var(--color-success, #16a34a);'"
              :title="method.published ? $t('windows.learningMethodEditor.withdraw') : $t('windows.learningMethodEditor.publish')"
            >
              <svg v-if="method.published" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
            <button
              @click="deleteMethod(method.method_id)"
              class="p-1.5 rounded transition-colors"
              style="color: var(--color-error, #dc2626);"
              :title="$t('windows.learningMethodEditor.delete')"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminLearningMethod } from '@/application/services/api/admin'

interface Props {
  methods: AdminLearningMethod[]
  sortedMethods: AdminLearningMethod[]
  dragState: { draggedIndex: number | null; targetIndex: number | null }
  getGroupStyle: (group: string) => string
  getMethodGroup: (methodType: number) => string
  getGroupPositionById: (methodTypeId: number) => string
  getMethodTypeName: (methodType: number) => string
  getTierStyle: (tier: string) => string
  getTierLabel: (tier: string) => string
  handleDragStart: (index: number) => void
  handleDragOver: (index: number) => void
  handleDrop: (targetIndex: number) => void
  handleDragEnd: () => void
  togglePublish: (method: AdminLearningMethod) => void
  deleteMethod: (methodId: string) => void
}

interface Emits {
  (e: 'open-selector'): void
  (e: 'edit', method: AdminLearningMethod): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
.method-item {
  user-select: none;
}

.method-item:hover {
  cursor: grab;
}

.method-item:active {
  cursor: grabbing;
}
</style>
