<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-4">Datenbank initialisieren</h2>
    <p class="text-gray-600 mb-6">
      Erstellt alle Tabellen, Indizes und die Datenbankstruktur.
    </p>

    <div v-if="result" class="mb-6 p-4 rounded-lg border" :class="result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'">
      <p class="font-medium mb-2">{{ result.success ? 'Erfolgreich!' : 'Fehler' }}</p>
      <p class="text-sm">Tabellen: {{ result.tables_created || 0 }}</p>
      <p class="text-sm">Indizes: {{ result.indexes_created || 0 }}</p>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button variant="outline" @click="$emit('back')">Zurück</Button>
      <Button v-if="!result || !result.success" variant="primary" :loading="loading" @click="initialize">Initialisieren</Button>
      <Button v-else variant="primary" @click="$emit('next')">Weiter</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import * as setupApi from '@/api/setup.api'
import type { DatabaseInitResponse } from '@/api/setup.api'
import Button from '@/components/ui/Button.vue'

defineEmits<{ next: []; back: [] }>()

const loading = ref(false)
const result = ref<DatabaseInitResponse | null>(null)
const error = ref('')

const initialize = async () => {
  loading.value = true
  error.value = ''
  try {
    result.value = await setupApi.initDatabase()
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Datenbankinitialisierung fehlgeschlagen'
  } finally {
    loading.value = false
  }
}
</script>
