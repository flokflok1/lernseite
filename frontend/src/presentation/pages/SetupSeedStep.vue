<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">{{ $t('setup.seed.title') }}</h2>
    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ $t('setup.seed.description') }}</p>

    <div v-if="result" class="mb-6 p-4 rounded-lg border" :class="result.success ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700 text-green-900 dark:text-green-100' : 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-700 text-red-900 dark:text-red-100'">
      <p class="font-medium mb-2">{{ result.success ? $t('setup.seed.success') : $t('setup.seed.error') }}</p>
      <p class="text-sm text-green-800 dark:text-green-200">{{ $t('setup.seed.learningMethods') }}: {{ result.learning_methods || 0 }}</p>
      <p class="text-sm text-green-800 dark:text-green-200">{{ $t('setup.seed.systemFeatures') }}: {{ result.system_features || 0 }}</p>
      <p class="text-sm text-green-800 dark:text-green-200">{{ $t('setup.seed.categories') }}: {{ result.categories || 0 }}</p>
      <p class="text-sm text-green-800 dark:text-green-200">{{ $t('setup.seed.roles') }}: {{ result.roles || 0 }}</p>
    </div>

    <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-300 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button variant="outline" @click="$emit('back')">{{ $t('setup.common.back') }}</Button>
      <Button v-if="!result || !result.success" variant="primary" :loading="loading" @click="seed">{{ $t('setup.seed.install') }}</Button>
      <Button v-else variant="primary" @click="$emit('next')">{{ $t('setup.common.next') }}</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import * as setupApi from '@/application/services/api/system'
import type { SeedDataResponse } from '@/application/services/api/system'
import Button from '@/presentation/components/shared/ui/Button.vue'

const { t } = useI18n()

defineEmits<{ next: []; back: [] }>()

const loading = ref(false)
const result = ref<SeedDataResponse | null>(null)
const error = ref('')

const seed = async () => {
  loading.value = true
  error.value = ''
  try {
    result.value = await setupApi.seedData()
  } catch (err: any) {
    error.value = err.response?.data?.message || t('setup.seed.installFailed')
  } finally {
    loading.value = false
  }
}
</script>
