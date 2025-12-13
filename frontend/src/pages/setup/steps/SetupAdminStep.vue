<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-4">Admin-Account erstellen</h2>
    <p class="text-gray-600 mb-6">Erstelle den ersten Administrator-Account.</p>

    <form v-if="!success" @submit.prevent="submit" class="space-y-4 mb-6">
      <div class="grid grid-cols-2 gap-4">
        <Input v-model="form.first_name" label="Vorname" required />
        <Input v-model="form.last_name" label="Nachname" required />
      </div>
      <Input v-model="form.email" type="email" label="E-Mail" required />
      <Input v-model="form.password" type="password" label="Passwort" required hint="Min. 8 Zeichen, 1 Großbuchstabe, 1 Zahl" />
      <Input v-model="confirmPassword" type="password" label="Passwort wiederholen" required />
    </form>

    <div v-else class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
      <p class="font-medium text-green-900">Admin-Account erfolgreich erstellt!</p>
      <p class="text-sm text-green-700 mt-2">E-Mail: {{ form.email }}</p>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button variant="outline" @click="$emit('back')">Zurück</Button>
      <Button v-if="!success" type="submit" variant="primary" :loading="loading" @click="submit">Erstellen</Button>
      <Button v-else variant="primary" @click="$emit('next')">Weiter</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import * as setupApi from '@/api/setup.api'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'

defineEmits<{ next: []; back: [] }>()

const loading = ref(false)
const success = ref(false)
const error = ref('')
const confirmPassword = ref('')

const form = reactive({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
})

const submit = async () => {
  if (form.password !== confirmPassword.value) {
    error.value = 'Passwörter stimmen nicht überein'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await setupApi.createAdmin(form)
    success.value = true
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Admin-Erstellung fehlgeschlagen'
  } finally {
    loading.value = false
  }
}
</script>
