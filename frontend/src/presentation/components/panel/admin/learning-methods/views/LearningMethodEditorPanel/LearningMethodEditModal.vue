<template>
  <div
    v-if="editingMethod"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
      <!-- Header -->
      <div class="p-4 border-b border-[var(--color-border)] flex items-center justify-between sticky top-0 bg-[var(--color-surface)]">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)]">
          Lernmethode bearbeiten
        </h3>
        <button
          @click="$emit('close')"
          class="p-1 rounded hover:bg-[var(--color-background)] transition-colors"
        >
          <svg class="w-5 h-5 text-[var(--color-text-secondary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form Content -->
      <div class="p-4 overflow-y-auto max-h-[60vh] space-y-4">
        <!-- Method Type (readonly) -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Methoden-Typ
          </label>
          <div class="flex items-center gap-2">
            <span
              class="text-sm font-mono px-2 py-1 rounded"
              :style="getGroupStyle(getMethodGroup(editingMethod.method_type))"
            >
              {{ getGroupPositionById(editingMethod.method_type) }}
            </span>
            <span class="text-[var(--color-text-primary)]">
              {{ getMethodTypeName(editingMethod.method_type) }}
            </span>
          </div>
        </div>

        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Titel *
          </label>
          <input
            v-model="localForm.title"
            type="text"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            placeholder="Titel eingeben..."
          />
        </div>

        <!-- Instructions -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Anweisungen
          </label>
          <textarea
            v-model="localForm.instructions"
            rows="3"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            placeholder="Anweisungen eingeben..."
          ></textarea>
        </div>

        <!-- Duration & Difficulty -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              Dauer (Minuten)
            </label>
            <input
              v-model.number="localForm.duration_minutes"
              type="number"
              min="1"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              Schwierigkeit
            </label>
            <select
              v-model="localForm.difficulty"
              class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="easy">Einfach</option>
              <option value="medium">Mittel</option>
              <option value="hard">Schwer</option>
            </select>
          </div>
        </div>

        <!-- Tier -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Tier
          </label>
          <select
            v-model="localForm.tier"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="basic">Basic (Kostenlos)</option>
            <option value="premium">Premium</option>
            <option value="pro">Pro</option>
          </select>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-4 border-t border-[var(--color-border)] flex justify-end gap-3 sticky bottom-0 bg-[var(--color-surface)]">
        <button
          @click="$emit('close')"
          class="px-4 py-2 text-sm border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-background)] transition-colors"
        >
          Abbrechen
        </button>
        <button
          @click="handleSave"
          class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 transition-colors"
        >
          Speichern
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { AdminLearningMethod, LearningMethodGroup } from '@/application/services/api/panel-admin'

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
  getGroupStyle: (group: LearningMethodGroup) => string
  getMethodGroup: (methodType: number) => LearningMethodGroup
  getGroupPositionById: (methodTypeId: number) => string
  getMethodTypeName: (methodType: number) => string
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
