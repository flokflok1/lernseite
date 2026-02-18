<!--
  Course Actions Tab

  Quick actions for course status management: publish,
  unpublish, archive, and delete.
-->

<template>
  <div class="p-6">
    <div class="space-y-6">
      <!-- Status Actions -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg p-4">
        <h3 class="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Status-Aktionen</h3>
        <div class="space-y-3">
          <div v-if="courseStatus === 'draft'" class="flex items-center justify-between">
            <div>
              <p class="font-medium text-[var(--color-text-primary)]">Kurs veroeffentlichen</p>
              <p class="text-sm text-[var(--color-text-secondary)]">Macht den Kurs fuer Lernende sichtbar</p>
            </div>
            <button
              @click="$emit('publish')"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Veroeffentlichen
            </button>
          </div>

          <div v-if="courseStatus === 'published'" class="flex items-center justify-between">
            <div>
              <p class="font-medium text-[var(--color-text-primary)]">Veroeffentlichung zurueckziehen</p>
              <p class="text-sm text-[var(--color-text-secondary)]">Setzt Kurs auf "Entwurf" zurueck</p>
            </div>
            <button
              @click="$emit('unpublish')"
              class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
            >
              Zurueckziehen
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <p class="font-medium text-[var(--color-text-primary)]">Kurs archivieren</p>
              <p class="text-sm text-[var(--color-text-secondary)]">Archiviert den Kurs</p>
            </div>
            <button
              @click="$emit('archive')"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Archivieren
            </button>
          </div>
        </div>
      </div>

      <!-- Danger Zone -->
      <div class="rounded-lg p-4 border" style="background-color: var(--color-error-bg, #fef2f2); border-color: var(--color-error-border, #fecaca);">
        <h3 class="text-lg font-semibold mb-4" style="color: var(--color-error-text, #b91c1c);">Danger Zone</h3>
        <div class="flex items-center justify-between">
          <div>
            <p class="font-medium" style="color: var(--color-error-text, #b91c1c);">Kurs loeschen</p>
            <p class="text-sm" style="color: var(--color-error, #dc2626);">Diese Aktion kann nicht rueckgaengig gemacht werden</p>
          </div>
          <button
            @click="$emit('delete')"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Kurs loeschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  courseStatus: string
}

defineProps<Props>()

defineEmits<{
  (e: 'publish'): void
  (e: 'unpublish'): void
  (e: 'archive'): void
  (e: 'delete'): void
}>()
</script>
