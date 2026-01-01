<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-4">Organisation einrichten</h2>
    <p class="text-gray-600 mb-6">Erstelle deine erste Organisation (Schule/Unternehmen).</p>

    <form v-if="!success" @submit.prevent="submit" class="space-y-4 mb-6">
      <Input v-model="form.name" label="Organisationsname" required placeholder="Meine Schule" />
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Typ</label>
        <select v-model="form.org_type" class="input-field">
          <option value="academy">Academy (Plattform)</option>
          <option value="school">Schule</option>
          <option value="company">Unternehmen</option>
          <option value="creator_org">Creator Organisation</option>
          <option value="community">Community</option>
          <option value="system">System</option>
        </select>
      </div>
    </form>

    <div v-else class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
      <p class="font-medium text-green-900">Organisation erstellt!</p>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button variant="outline" @click="$emit('back')">Zurück</Button>
      <Button v-if="!success" variant="primary" :loading="loading" @click="submit">Erstellen</Button>
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

const form = reactive({
  name: '',
  org_type: 'academy' as 'system' | 'school' | 'company' | 'academy' | 'creator_org' | 'community',
})

const submit = async () => {
  loading.value = true
  error.value = ''
  try {
    await setupApi.createOrganisation(form)
    success.value = true
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Organisations-Erstellung fehlgeschlagen'
  } finally {
    loading.value = false
  }
}
</script>
