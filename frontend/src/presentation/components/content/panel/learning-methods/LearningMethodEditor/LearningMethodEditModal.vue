<template>
  <div v-if="editingMethod" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
    <div class="bg-[var(--color-background)] rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-[var(--color-surface)] border-b border-[var(--color-border)] p-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
          {{ $t('windows.learningMethodEditor.editMethod') }}
        </h2>
        <button
          @click="$emit('close')"
          class="p-1 hover:bg-[var(--color-border)] rounded transition-colors"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form Content -->
      <div class="p-4 space-y-4">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('windows.learningMethodEditor.title') }}
          </label>
          <input
            v-model="editForm.title"
            type="text"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            :placeholder="$t('windows.learningMethodEditor.titlePlaceholder')"
          />
        </div>

        <!-- Instructions -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('windows.learningMethodEditor.instructions') }}
          </label>
          <textarea
            v-model="editForm.instructions"
            rows="3"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] resize-none"
            :placeholder="$t('windows.learningMethodEditor.instructionsPlaceholder')"
          />
        </div>

        <!-- Duration -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('windows.learningMethodEditor.duration') }}
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="editForm.duration_minutes"
                type="number"
                min="0"
                max="480"
                class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              <span class="text-sm text-[var(--color-text-secondary)]">
                {{ $t('windows.learningMethodEditor.minutes') }}
              </span>
            </div>
          </div>

          <!-- Difficulty -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('windows.learningMethodEditor.difficulty') }}
            </label>
            <select
              v-model="editForm.difficulty"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="easy">{{ $t('windows.learningMethodEditor.easy') }}</option>
              <option value="medium">{{ $t('windows.learningMethodEditor.medium') }}</option>
              <option value="hard">{{ $t('windows.learningMethodEditor.hard') }}</option>
            </select>
          </div>
        </div>

        <!-- Tier -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('windows.learningMethodEditor.tier') }}
          </label>
          <select
            v-model="editForm.tier"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="basic">{{ $t('windows.learningMethodEditor.tierOptions.basic') }}</option>
            <option value="premium">{{ $t('windows.learningMethodEditor.tierOptions.premium') }}</option>
            <option value="pro">{{ $t('windows.learningMethodEditor.tierOptions.pro') }}</option>
          </select>
        </div>
      </div>

      <!-- Actions -->
      <div class="sticky bottom-0 bg-[var(--color-surface)] border-t border-[var(--color-border)] p-4 flex gap-2">
        <button
          @click="$emit('close')"
          class="flex-1 px-4 py-2 border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-background)] transition-colors"
        >
          {{ $t('windows.learningMethodEditor.cancel') }}
        </button>
        <button
          @click="$emit('save')"
          class="flex-1 px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors"
        >
          {{ $t('windows.learningMethodEditor.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminLearningMethod } from '@/application/services/api/admin'

interface Props {
  editingMethod: AdminLearningMethod | null
  editForm: {
    title: string
    instructions: string
    duration_minutes: number
    difficulty: 'easy' | 'medium' | 'hard'
    tier: 'basic' | 'premium' | 'pro'
  }
}

interface Emits {
  (e: 'close'): void
  (e: 'save'): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped>
/* Modal styles */
</style>
