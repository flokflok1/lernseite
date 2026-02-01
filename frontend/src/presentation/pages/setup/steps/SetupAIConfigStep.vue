<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">{{ $t('setup.ai.title') }}</h2>
    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ $t('setup.ai.description') }}</p>

    <form v-if="!success" @submit.prevent="submit" class="space-y-4 mb-6">
      <Input v-model="form.openai_api_key" :label="$t('setup.ai.openaiKey')" placeholder="sk-..." :hint="$t('setup.ai.optional')" />
      <Input v-model="form.anthropic_api_key" :label="$t('setup.ai.anthropicKey')" placeholder="sk-ant-..." :hint="$t('setup.ai.optional')" />
      <Input v-model="form.deepl_api_key" :label="$t('setup.ai.deeplKey')" placeholder="..." :hint="$t('setup.ai.optional')" />
    </form>

    <div v-else class="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 rounded-lg">
      <p class="font-medium text-green-900 dark:text-green-100">{{ $t('setup.ai.success') }}</p>
    </div>

    <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-300 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button variant="outline" @click="$emit('back')">{{ $t('setup.common.back') }}</Button>
      <Button variant="outline" @click="skip">{{ $t('setup.ai.skip') }}</Button>
      <Button v-if="!success" variant="primary" :loading="loading" @click="submit">{{ $t('setup.common.save') }}</Button>
      <Button v-else variant="primary" @click="$emit('next')">{{ $t('setup.common.next') }}</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import * as setupApi from '@/application/services/api/system'
import Input from '@/presentation/components/shared/ui/Input.vue'
import Button from '@/presentation/components/shared/ui/Button.vue'

const { t } = useI18n()
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
    error.value = err.response?.data?.message || t('setup.ai.saveFailed')
  } finally {
    loading.value = false
  }
}

const skip = () => {
  emit('next')
}
</script>
