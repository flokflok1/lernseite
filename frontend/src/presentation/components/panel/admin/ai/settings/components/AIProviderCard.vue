<!--
  Single AI provider card with API key management and settings controls.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
    <!-- Provider Header -->
    <div class="px-6 py-4 border-b border-[var(--color-border)] flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="text-3xl">{{ providerIcon }}</div>
        <div>
          <h3 class="text-lg font-bold text-[var(--color-text-primary)]">
            {{ provider.display_name }}
          </h3>
          <p class="text-sm text-[var(--color-text-secondary)]">
            {{ provider.provider_type }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-4">
        <span
          :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            provider.active
              ? 'bg-green-100 text-green-700'
              : 'bg-gray-100 text-gray-600'
          ]"
        >
          {{ provider.active ? $t('panel.aiSettingsPage.status.active') : $t('panel.aiSettingsPage.status.inactive') }}
        </span>

        <span
          :class="[
            'px-3 py-1 rounded-full text-sm font-medium',
            provider.has_api_key
              ? 'bg-blue-100 text-blue-700'
              : 'bg-yellow-100 text-yellow-700'
          ]"
        >
          {{ provider.has_api_key ? $t('panel.aiSettingsPage.status.apiKeySet') : $t('panel.aiSettingsPage.status.noApiKey') }}
        </span>
      </div>
    </div>

    <!-- Provider Body -->
    <div class="p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Left Column: API Key Input -->
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('panel.aiSettingsPage.apiKey.label') }}
          </label>
          <div class="flex gap-2">
            <input
              :value="apiKey"
              :type="isApiKeyVisible ? 'text' : 'password'"
              :placeholder="provider.has_api_key ? $t('panel.aiSettingsPage.apiKey.placeholderSet') : $t('panel.aiSettingsPage.apiKey.placeholderEmpty')"
              class="flex-1 px-4 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
              @input="$emit('update:apiKey', ($event.target as HTMLInputElement).value)"
            />
            <button
              class="px-3 py-2 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors"
              :title="isApiKeyVisible ? $t('panel.aiSettingsPage.apiKey.hide') : $t('panel.aiSettingsPage.apiKey.show')"
              @click="$emit('toggleVisibility')"
            >
              {{ isApiKeyVisible ? '&#x1F648;' : '&#x1F441;' }}
            </button>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-2 mt-3">
            <button
              :disabled="!apiKey || isSaving"
              class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity flex items-center gap-2"
              @click="$emit('saveKey')"
            >
              <span v-if="isSaving" class="animate-spin">&#x23F3;</span>
              <span>{{ isSaving ? $t('panel.aiSettingsPage.apiKey.saving') : $t('panel.aiSettingsPage.apiKey.save') }}</span>
            </button>

            <button
              v-if="provider.has_api_key"
              :disabled="isTesting"
              class="px-4 py-2 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface-secondary)] disabled:opacity-50 transition-colors flex items-center gap-2"
              @click="$emit('testKey')"
            >
              <span v-if="isTesting" class="animate-spin">&#x23F3;</span>
              <span>{{ isTesting ? $t('panel.aiSettingsPage.apiKey.testing') : $t('panel.aiSettingsPage.apiKey.test') }}</span>
            </button>

            <button
              v-if="provider.has_api_key"
              :disabled="isDeleting"
              class="px-4 py-2 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 disabled:opacity-50 transition-colors"
              @click="$emit('deleteKey')"
            >
              {{ $t('panel.aiSettingsPage.apiKey.remove') }}
            </button>
          </div>

          <!-- Test Result -->
          <div
            v-if="testResult"
            :class="[
              'mt-3 p-3 rounded-lg text-sm',
              testResult.success
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            ]"
          >
            <div class="flex items-start gap-2">
              <span>{{ testResult.success ? '&#x2705;' : '&#x274C;' }}</span>
              <div>
                <p class="font-medium">{{ testResult.message }}</p>
                <p v-if="testResult.response_time" class="text-xs opacity-75">
                  {{ $t('panel.aiSettingsPage.messages.responseTime', { time: testResult.response_time }) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Settings -->
        <div>
          <div class="space-y-4">
            <!-- Active Toggle -->
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium text-[var(--color-text-primary)]">
                {{ $t('panel.aiSettingsPage.settings.enableProvider') }}
              </label>
              <button
                :class="[
                  'relative w-12 h-6 rounded-full transition-colors',
                  provider.active ? 'bg-green-500' : 'bg-gray-300'
                ]"
                @click="$emit('toggleActive')"
              >
                <span
                  :class="[
                    'absolute top-1 w-4 h-4 bg-white rounded-full transition-transform',
                    provider.active ? 'right-1' : 'left-1'
                  ]"
                ></span>
              </button>
            </div>

            <!-- Priority -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                {{ $t('panel.aiSettingsPage.settings.priority') }}
              </label>
              <input
                type="number"
                :value="provider.priority"
                min="0"
                max="100"
                class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                @change="$emit('updatePriority', $event)"
              />
            </div>

            <!-- Rate Limit -->
            <div>
              <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                {{ $t('panel.aiSettingsPage.settings.rateLimit') }}
              </label>
              <input
                type="number"
                :value="provider.rate_limit_per_minute"
                min="1"
                max="1000"
                class="w-24 px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)]"
                @change="$emit('updateRateLimit', $event)"
              />
            </div>

            <!-- Last Validated -->
            <div v-if="provider.last_validated" class="text-sm text-[var(--color-text-secondary)]">
              {{ $t('panel.aiSettingsPage.settings.lastValidated') }} {{ formattedLastValidated }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { AIProvider, TestResult } from '../types'

interface Props {
  provider: AIProvider
  apiKey: string
  isApiKeyVisible: boolean
  isSaving: boolean
  isTesting: boolean
  isDeleting: boolean
  testResult: TestResult | undefined
  providerIcon: string
}

const props = defineProps<Props>()

defineEmits<{
  'update:apiKey': [value: string]
  toggleVisibility: []
  saveKey: []
  testKey: []
  deleteKey: []
  toggleActive: []
  updatePriority: [event: Event]
  updateRateLimit: [event: Event]
}>()

const formattedLastValidated = computed((): string => {
  if (!props.provider.last_validated) return ''
  return new Date(props.provider.last_validated).toLocaleString('de-DE')
})
</script>
