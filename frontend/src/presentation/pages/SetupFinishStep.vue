<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">{{ $t('setup.finish.title') }}</h2>
    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ $t('setup.finish.description') }}</p>

    <div v-if="verifyResult" class="mb-6 space-y-3">
      <div class="p-4 rounded-lg border" :class="verifyResult.success ? 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-700' : 'bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-700'">
        <p class="font-medium mb-3 text-gray-900 dark:text-gray-100">{{ verifyResult.success ? $t('setup.finish.allChecksPassed') : $t('setup.finish.verifying') }}</p>

        <div class="space-y-2">
          <div v-for="(check, index) in verifyResult.checks" :key="index" class="flex items-center text-sm">
            <span v-if="check.status === 'passed'" class="text-green-600 dark:text-green-400 mr-2">✓</span>
            <span v-else class="text-red-600 dark:text-red-400 mr-2">✗</span>
            <span class="text-gray-800 dark:text-gray-200">{{ check.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="completed" class="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 rounded-lg">
      <p class="font-medium text-green-900 dark:text-green-100 mb-2">{{ $t('setup.finish.success') }}</p>
      <p class="text-sm text-green-700 dark:text-green-300 mb-2">{{ $t('setup.finish.successDesc') }}</p>
      <p class="text-sm text-blue-600 dark:text-blue-400">{{ $t('setup.finish.reloadNote') }}</p>
    </div>

    <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-300 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button v-if="!completed" variant="outline" @click="$emit('back')">{{ $t('setup.common.back') }}</Button>
      <div v-else></div>
      <div class="flex gap-3">
        <Button v-if="!verifyResult" variant="outline" :loading="verifying" @click="verify">{{ $t('setup.finish.verify') }}</Button>
        <Button v-if="verifyResult && !completed" variant="primary" :loading="loading" @click="complete">
          {{ $t('setup.finish.complete') }}
        </Button>
        <Button v-if="completed" variant="primary" @click="goToLogin">{{ $t('setup.finish.goToLogin') }}</Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import * as setupApi from '@/application/services/api/system'
import Button from '@/presentation/components/shared/ui/Button.vue'
import { useAppStore } from '@/application/stores/modules/core'

const { t } = useI18n()

defineEmits<{ back: [] }>();

interface VerifyCheck {
  name: string
  status: 'passed' | 'failed' | 'error'
  message: string
  details?: any
}

interface VerifyResponse {
  success: boolean
  checks: VerifyCheck[]
  errors?: string[]
  warnings?: string[]
  timestamp?: string
}

const _router = useRouter()
const appStore = useAppStore()

const verifying = ref(false)
const loading = ref(false)
const completed = ref(false)
const error = ref('')
const verifyResult = ref<VerifyResponse | null>(null)

// Auto-run verification on mount
onMounted(() => {
  verify()
})

const verify = async () => {
  verifying.value = true
  error.value = ''
  try {
    const response = await setupApi.verifyInstallation()
    verifyResult.value = response as VerifyResponse
  } catch (err: any) {
    error.value = err.response?.data?.message || t('setup.finish.verifyFailed')
  } finally {
    verifying.value = false
  }
}

const complete = async () => {
  loading.value = true
  error.value = ''
  try {
    await setupApi.completeInstallation()
    completed.value = true
    // Mark installation as complete in app store (which also saves to localStorage)
    appStore.markAsInstalled()
    // Also update full status from backend
    await appStore.checkInstallationStatus()
  } catch (err: any) {
    error.value = err.response?.data?.message || t('setup.finish.completeFailed')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  // Full page reload to ensure fresh app state after setup
  window.location.href = '/login'
}
</script>
