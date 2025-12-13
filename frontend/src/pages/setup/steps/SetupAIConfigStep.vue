<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-4">KI-Konfiguration</h2>
    <p class="text-gray-600 mb-6">Konfiguriere AI-Provider (optional, kann später nachgetragen werden).</p>

    <form v-if="!success" @submit.prevent="submit" class="space-y-4 mb-6">
      <Input v-model="form.openai_api_key" label="OpenAI API Key" placeholder="sk-..." hint="Optional" />
      <Input v-model="form.anthropic_api_key" label="Anthropic API Key" placeholder="sk-ant-..." hint="Optional" />
      <Input v-model="form.deepl_api_key" label="DeepL API Key" placeholder="..." hint="Optional" />
    </form>

    <div v-else class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
      <p class="font-medium text-green-900">KI-Konfiguration gespeichert!</p>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button variant="outline" @click="$emit('back')">Zurück</Button>
      <Button variant="outline" @click="skip">Überspringen</Button>
      <Button v-if="!success" variant="primary" :loading="loading" @click="submit">Speichern</Button>
      <Button v-else variant="primary" @click="$emit('next')">Weiter</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import * as setupApi from '@/api/setup.api'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'

const emit = defineEmits<{ next: []; back: [] }>()

const loading = ref(false)
const success = ref(false)
const error = ref('')

const form = reactive({
  openai_api_key: '',
  anthropic_api_key: '',
  deepl_api_key: '',
})

const submit = async () => {
  loading.value = true
  error.value = ''
  try {
    await setupApi.configureAI(form)
    success.value = true
  } catch (err: any) {
    error.value = err.response?.data?.message || 'KI-Konfiguration fehlgeschlagen'
  } finally {
    loading.value = false
  }
}

const skip = () => {
  emit('next')
}
</script>
