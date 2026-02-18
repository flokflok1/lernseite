<!--
  PromptDeleteModal - Confirmation dialog for deleting a prompt template
-->

<template>
  <div
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-[var(--color-surface)] rounded-xl shadow-xl max-w-md w-full p-6">
      <h2 class="text-xl font-bold text-[var(--color-text-primary)] mb-4">Template loeschen?</h2>
      <p class="text-[var(--color-text-secondary)] mb-6">
        Sind Sie sicher, dass Sie das Template "<strong>{{ deleteTarget?.name }}</strong>" loeschen moechten?
        Diese Aktion kann nicht rueckgaengig gemacht werden.
      </p>
      <div class="flex justify-end gap-3">
        <button
          @click="$emit('close')"
          class="px-4 py-2 border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] hover:bg-[var(--color-bg)]"
        >
          Abbrechen
        </button>
        <button
          @click="$emit('confirm')"
          :disabled="deleting"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
        >
          {{ deleting ? 'Loeschen...' : 'Loeschen' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PromptTemplate } from './prompt.types.ts'

defineProps<{
  deleteTarget: PromptTemplate | null
  deleting: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'confirm'): void
}>()
</script>
