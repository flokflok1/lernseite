<template>
  <div>
    <h2 class="text-xl font-bold text-white mb-3">
      {{ $t('setup.environment.title') }}
    </h2>
    <p class="text-sm text-gray-400 mb-5">
      {{ $t('setup.environment.description') }}
    </p>

    <!-- Environment Selection Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <!-- Development Card -->
      <div
        @click="selectedEnvironment = 'development'"
        :class="[
          'p-6 rounded-lg border-2 cursor-pointer transition-all',
          selectedEnvironment === 'development'
            ? 'border-primary-500 bg-primary-500/10'
            : 'border-[#2a3350] bg-[#0f1419] hover:border-[#3a4360]'
        ]"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="text-lg font-semibold text-white mb-1">
              {{ $t('setup.environment.development.title') }}
            </h3>
            <p class="text-xs text-gray-400">
              {{ $t('setup.environment.development.description') }}
            </p>
          </div>
          <div
            :class="[
              'w-6 h-6 rounded-full border-2 flex items-center justify-center',
              selectedEnvironment === 'development'
                ? 'border-primary-500 bg-primary-500'
                : 'border-[#2a3350]'
            ]"
          >
            <svg
              v-if="selectedEnvironment === 'development'"
              class="w-4 h-4 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>

        <ul class="space-y-2 text-sm text-gray-300">
          <li class="flex items-center">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            {{ $t('setup.environment.development.debugMode') }}
          </li>
          <li class="flex items-center">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            {{ $t('setup.environment.development.localhostCors') }}
          </li>
          <li class="flex items-center">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            {{ $t('setup.environment.development.detailedLogging') }}
          </li>
          <li class="flex items-center">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            {{ $t('setup.environment.development.hotReload') }}
          </li>
        </ul>
      </div>

      <!-- Production Card -->
      <div
        @click="selectedEnvironment = 'production'"
        :class="[
          'p-6 rounded-lg border-2 cursor-pointer transition-all',
          selectedEnvironment === 'production'
            ? 'border-primary-500 bg-primary-500/10'
            : 'border-[#2a3350] bg-[#0f1419] hover:border-[#3a4360]'
        ]"
      >
        <div class="flex items-start justify-between mb-3">
          <div>
            <h3 class="text-lg font-semibold text-white mb-1">
              {{ $t('setup.environment.production.title') }}
            </h3>
            <p class="text-xs text-gray-400">
              {{ $t('setup.environment.production.description') }}
            </p>
          </div>
          <div
            :class="[
              'w-6 h-6 rounded-full border-2 flex items-center justify-center',
              selectedEnvironment === 'production'
                ? 'border-primary-500 bg-primary-500'
                : 'border-[#2a3350]'
            ]"
          >
            <svg
              v-if="selectedEnvironment === 'production'"
              class="w-4 h-4 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>

        <ul class="space-y-2 text-sm text-gray-300">
          <li class="flex items-center">
            <svg class="w-4 h-4 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            {{ $t('setup.environment.production.optimizedPerformance') }}
          </li>
          <li class="flex items-center">
            <svg class="w-4 h-4 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            {{ $t('setup.environment.production.securityHeaders') }}
          </li>
          <li class="flex items-center">
            <svg class="w-4 h-4 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            {{ $t('setup.environment.production.rateLimiting') }}
          </li>
          <li class="flex items-center">
            <svg class="w-4 h-4 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
            </svg>
            {{ $t('setup.environment.production.productionLogging') }}
          </li>
        </ul>
      </div>
    </div>

    <!-- Status Message -->
    <div
      v-if="statusMessage"
      class="mb-6 p-4 rounded-lg"
      :class="statusSuccess ? 'bg-green-900/30 border border-green-700 text-green-200' : 'bg-red-900/30 border border-red-700 text-red-200'"
    >
      <div class="flex items-center">
        <svg
          v-if="statusSuccess"
          class="w-5 h-5 mr-2"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clip-rule="evenodd"
          />
        </svg>
        <svg
          v-else
          class="w-5 h-5 mr-2"
          fill="currentColor"
          viewBox="0 0 20 20"
        >
          <path
            fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
            clip-rule="evenodd"
          />
        </svg>
        <span>{{ statusMessage }}</span>
      </div>
    </div>

    <!-- Info Box -->
    <div class="mb-6 p-4 bg-blue-900/20 border border-blue-700/50 rounded-lg">
      <div class="flex">
        <svg class="w-5 h-5 text-blue-400 mr-3 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
        </svg>
        <div>
          <p class="text-sm text-blue-200 font-semibold mb-1">
            {{ $t('setup.environment.infoBox.title') }}
          </p>
          <p class="text-xs text-blue-300/80">
            {{ $t('setup.environment.infoBox.description') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <div class="flex justify-end gap-3">
      <Button
        @click="configureEnvironment"
        :loading="loading"
        :disabled="!selectedEnvironment"
        variant="primary"
        class="px-6"
      >
        {{ loading ? $t('setup.environment.configuring') : $t('setup.environment.configureButton') }}
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from '@/presentation/components/base/Button.vue'
import * as setupApi from '@/infrastructure/api/clients/system'

const { t } = useI18n()

const emit = defineEmits(['next', 'back'])

const selectedEnvironment = ref<'development' | 'production'>('development')
const loading = ref(false)
const statusMessage = ref('')
const statusSuccess = ref(false)

const configureEnvironment = async () => {
  if (!selectedEnvironment.value) return

  loading.value = true
  statusMessage.value = ''

  try {
    const response = await setupApi.configureEnvironment({
      environment: selectedEnvironment.value,
      overwrite: true
    })

    if (response.success) {
      statusSuccess.value = true
      statusMessage.value = t('setup.environment.success', { env: selectedEnvironment.value })

      // Auto-advance after 1.5 seconds
      setTimeout(() => {
        emit('next')
      }, 1500)
    } else {
      statusSuccess.value = false
      statusMessage.value = response.error || t('setup.environment.configFailed')
    }
  } catch (error: any) {
    statusSuccess.value = false
    statusMessage.value = error.message || t('setup.environment.networkError')
  } finally {
    loading.value = false
  }
}
</script>
