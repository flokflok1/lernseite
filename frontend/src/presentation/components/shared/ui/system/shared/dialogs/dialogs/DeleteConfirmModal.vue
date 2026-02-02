<!--
  Delete Confirmation Modal

  Confirmation dialog for category deletion
-->

<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-content">
      <!-- Header -->
      <div class="modal-header">
        <h2 class="text-xl font-bold text-red-600">Kategorie löschen?</h2>
        <button
          @click="$emit('cancel')"
          class="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] text-2xl leading-none"
        >
          ×
        </button>
      </div>

      <!-- Body -->
      <div class="modal-body">
        <div class="flex items-start gap-4 mb-6">
          <div class="text-4xl">⚠️</div>
          <div class="flex-1">
            <p class="text-[var(--color-text-primary)] mb-2">
              Möchten Sie die Kategorie <strong>"{{ category.name }}"</strong> wirklich löschen?
            </p>
            <p class="text-sm text-[var(--color-text-secondary)]">
              Diese Aktion kann nicht rückgängig gemacht werden.
            </p>
          </div>
        </div>

        <!-- Warning: Will delete children (cascade) -->
        <div v-if="hasChildren" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <div class="flex items-start gap-3">
            <div class="text-xl">⚠️</div>
            <div class="flex-1">
              <p class="text-sm font-medium text-yellow-800 mb-1">
                Achtung: Kaskadenlöschung!
              </p>
              <p class="text-xs text-yellow-700">
                {{ totalDescendants }} Unterkategorie(n) werden ebenfalls gelöscht.
              </p>
            </div>
          </div>
        </div>

        <!-- Error: Cannot delete with courses -->
        <div v-if="hasCourses" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div class="flex items-start gap-3">
            <div class="text-xl">🚫</div>
            <div class="flex-1">
              <p class="text-sm font-medium text-red-800 mb-1">
                Löschen nicht möglich!
              </p>
              <p class="text-xs text-red-700 mb-2">
                Diese Kategorie (oder Unterkategorien) enthält {{ category.course_count || 0 }} Kurs(e).
              </p>
              <p class="text-xs text-red-600 font-medium">
                Bitte verschieben oder löschen Sie zuerst alle Kurse.
              </p>
            </div>
          </div>
        </div>

        <!-- Confirmation checkbox (only if deletable) -->
        <label v-if="canDelete" class="flex items-start gap-2 cursor-pointer">
          <input
            v-model="confirmed"
            type="checkbox"
            class="mt-1 w-4 h-4 text-red-600 border-[var(--color-border)] rounded focus:ring-red-500"
          />
          <span class="text-sm text-[var(--color-text-primary)]">
            Ich verstehe, dass diese Aktion nicht rückgängig gemacht werden kann
            <span v-if="hasChildren" class="text-red-600 font-medium">
              (inkl. {{ totalDescendants }} Unterkategorie(n))
            </span>
          </span>
        </label>

        <!-- Hint for non-deletable -->
        <div v-if="!canDelete" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p class="text-sm text-blue-700">
            <strong>Tipp:</strong> Sie können die Kategorie stattdessen deaktivieren, um sie auszublenden.
          </p>
        </div>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button
          type="button"
          @click="$emit('cancel')"
          class="btn-secondary"
        >
          {{ canDelete ? 'Abbrechen' : 'Schließen' }}
        </button>
        <button
          v-if="canDelete"
          type="button"
          @click="$emit('confirm')"
          :disabled="!confirmed"
          class="btn-danger"
        >
          Löschen
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  category: any
}

const props = defineProps<Props>()

defineEmits(['confirm', 'cancel'])

// State
const confirmed = ref(false)

// Computed
const hasChildren = computed(() => {
  return props.category.children && props.category.children.length > 0
})

const hasCourses = computed(() => {
  return props.category.course_count > 0
})

// Recursively count all descendants
const countDescendants = (category: any): number => {
  if (!category.children || category.children.length === 0) return 0
  return category.children.reduce((sum: number, child: any) => {
    return sum + 1 + countDescendants(child)
  }, 0)
}

const totalDescendants = computed(() => {
  return countDescendants(props.category)
})

// Can delete if no courses (children will be cascade deleted)
const canDelete = computed(() => {
  return !hasCourses.value
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background-color: var(--color-surface);
  border-radius: 0.75rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 500px;
  width: 100%;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  border-radius: 0.5rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: var(--color-background);
}

.btn-danger {
  padding: 0.625rem 1.25rem;
  background-color: #DC2626;
  color: white;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: opacity 0.2s;
}

.btn-danger:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
