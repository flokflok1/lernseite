<template>
  <div v-if="editingMethod" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
    <div class="bg-[var(--color-background)] rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="sticky top-0 bg-[var(--color-surface)] border-b border-[var(--color-border)] p-4 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-[var(--color-text-primary)]">
          {{ $t('learningMethodEditor.editMethod') }}
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
            {{ $t('learningMethodEditor.title') }}
          </label>
          <input
            v-model="localForm.title"
            type="text"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            :placeholder="$t('learningMethodEditor.titlePlaceholder')"
          />
        </div>

        <!-- Instructions -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('learningMethodEditor.instructions') }}
          </label>
          <textarea
            v-model="localForm.instructions"
            rows="3"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] resize-none"
            :placeholder="$t('learningMethodEditor.instructionsPlaceholder')"
          />
        </div>

        <!-- Duration -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('learningMethodEditor.duration') }}
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model.number="localForm.duration_minutes"
                type="number"
                min="0"
                max="480"
                class="flex-1 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
              <span class="text-sm text-[var(--color-text-secondary)]">
                {{ $t('learningMethodEditor.minutes') }}
              </span>
            </div>
          </div>

          <!-- Difficulty -->
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
              {{ $t('learningMethodEditor.difficulty') }}
            </label>
            <select
              v-model="localForm.difficulty"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="easy">{{ $t('learningMethodEditor.easy') }}</option>
              <option value="medium">{{ $t('learningMethodEditor.medium') }}</option>
              <option value="hard">{{ $t('learningMethodEditor.hard') }}</option>
            </select>
          </div>
        </div>

        <!-- Tier -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
            {{ $t('learningMethodEditor.tier') }}
          </label>
          <select
            v-model="localForm.tier"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-background)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="basic">{{ $t('learningMethodEditor.tierOptions.basic') }}</option>
            <option value="premium">{{ $t('learningMethodEditor.tierOptions.premium') }}</option>
            <option value="pro">{{ $t('learningMethodEditor.tierOptions.pro') }}</option>
          </select>
        </div>
      </div>

      <!-- Actions -->
      <div class="sticky bottom-0 bg-[var(--color-surface)] border-t border-[var(--color-border)] p-4 flex gap-2">
        <button
          @click="$emit('close')"
          class="flex-1 px-4 py-2 border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-background)] transition-colors"
        >
          {{ $t('learningMethodEditor.cancel') }}
        </button>
        <button
          @click="handleSave"
          class="flex-1 px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors"
        >
          {{ $t('learningMethodEditor.save') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { AdminLearningMethod } from '@/application/services/api/admin'

interface EditFormData {
  title: string
  instructions: string
  duration_minutes: number
  difficulty: 'easy' | 'medium' | 'hard'
  tier: 'basic' | 'premium' | 'pro'
}

interface Props {
  editingMethod: AdminLearningMethod | null
  editForm: EditFormData
}

interface Emits {
  (e: 'close'): void
  (e: 'save', formData: EditFormData): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Local state for controlled component pattern (no prop mutation)
const localForm = ref<EditFormData>({
  title: '',
  instructions: '',
  duration_minutes: 0,
  difficulty: 'medium',
  tier: 'basic'
})

// Sync local state when prop changes (deep clone to avoid reference sharing)
watch(
  () => props.editForm,
  (newForm) => {
    if (newForm) {
      localForm.value = {
        title: newForm.title ?? '',
        instructions: newForm.instructions ?? '',
        duration_minutes: newForm.duration_minutes ?? 0,
        difficulty: newForm.difficulty ?? 'medium',
        tier: newForm.tier ?? 'basic'
      }
    }
  },
  { immediate: true, deep: true }
)

// Emit form data on save
function handleSave(): void {
  emit('save', { ...localForm.value })
}
</script>

<style scoped>
/* Modal styles */
</style>
