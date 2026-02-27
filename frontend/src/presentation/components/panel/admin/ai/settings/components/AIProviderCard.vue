<!--
  Compact AI provider card with API key management and settings.
-->

<template>
  <div class="bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)] overflow-hidden">
    <!-- Provider Row: Icon + Name + Status + Toggle -->
    <div class="px-4 py-3 flex items-center gap-3">
      <!-- Icon -->
      <div class="text-xl shrink-0">{{ providerIcon }}</div>

      <!-- Name + Type -->
      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] truncate">
            {{ provider.display_name }}
          </h3>
          <span
            :class="[
              'shrink-0 px-2 py-0.5 rounded-full text-[10px] font-medium',
              provider.has_api_key
                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
            ]"
          >
            {{ provider.has_api_key ? $t('panel.aiSettingsPage.status.apiKeySet') : $t('panel.aiSettingsPage.status.noApiKey') }}
          </span>
        </div>
        <p class="text-xs text-[var(--color-text-secondary)] truncate">{{ provider.provider_type }}</p>
      </div>

      <!-- Settings Cluster (compact) -->
      <div class="flex items-center gap-3 shrink-0">
        <!-- Priority -->
        <div class="flex items-center gap-1">
          <span class="text-[10px] text-[var(--color-text-secondary)] uppercase tracking-wide">Pri</span>
          <input
            type="number"
            :value="provider.priority"
            min="0"
            max="100"
            class="w-12 px-1.5 py-0.5 text-xs text-center border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            @change="$emit('updatePriority', $event)"
          />
        </div>

        <!-- Rate Limit -->
        <div class="flex items-center gap-1">
          <span class="text-[10px] text-[var(--color-text-secondary)] uppercase tracking-wide">RPM</span>
          <input
            type="number"
            :value="provider.rate_limit_per_minute"
            min="1"
            max="1000"
            class="w-14 px-1.5 py-0.5 text-xs text-center border border-[var(--color-border)] rounded bg-[var(--color-bg)] text-[var(--color-text-primary)]"
            @change="$emit('updateRateLimit', $event)"
          />
        </div>

        <!-- Active Toggle -->
        <button
          :class="[
            'relative w-9 h-5 rounded-full transition-colors shrink-0',
            provider.active ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'
          ]"
          :title="$t('panel.aiSettingsPage.settings.enableProvider')"
          @click="$emit('toggleActive')"
        >
          <span
            :class="[
              'absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform shadow-sm',
              provider.active ? 'left-[18px]' : 'left-0.5'
            ]"
          />
        </button>

        <!-- Expand Toggle -->
        <button
          class="p-1 rounded hover:bg-[var(--color-bg)] transition-colors text-[var(--color-text-secondary)]"
          @click="expanded = !expanded"
        >
          <svg
            :class="['w-4 h-4 transition-transform', expanded ? 'rotate-180' : '']"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Expandable: API Key + Test -->
    <div v-if="expanded" class="px-4 pb-3 border-t border-[var(--color-border)] pt-3">
      <div class="flex gap-2 items-start">
        <!-- API Key Input -->
        <div class="flex-1 flex gap-1.5">
          <input
            :value="apiKey"
            :type="isApiKeyVisible ? 'text' : 'password'"
            :placeholder="provider.has_api_key ? $t('panel.aiSettingsPage.apiKey.placeholderSet') : $t('panel.aiSettingsPage.apiKey.placeholderEmpty')"
            class="flex-1 px-3 py-1.5 text-sm border border-[var(--color-border)] rounded-lg bg-[var(--color-bg)] text-[var(--color-text-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
            @input="$emit('update:apiKey', ($event.target as HTMLInputElement).value)"
          />
          <button
            class="px-2 py-1.5 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-bg)] transition-colors text-sm"
            :title="isApiKeyVisible ? $t('panel.aiSettingsPage.apiKey.hide') : $t('panel.aiSettingsPage.apiKey.show')"
            @click="$emit('toggleVisibility')"
          >
            {{ isApiKeyVisible ? '&#x1F648;' : '&#x1F441;' }}
          </button>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-1.5 shrink-0">
          <button
            :disabled="!apiKey || isSaving"
            class="px-3 py-1.5 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            @click="$emit('saveKey')"
          >
            {{ isSaving ? $t('panel.aiSettingsPage.apiKey.saving') : $t('panel.aiSettingsPage.apiKey.save') }}
          </button>

          <button
            v-if="provider.has_api_key"
            :disabled="isTesting"
            class="px-3 py-1.5 text-sm border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-bg)] disabled:opacity-50 transition-colors"
            @click="$emit('testKey')"
          >
            {{ isTesting ? $t('panel.aiSettingsPage.apiKey.testing') : $t('panel.aiSettingsPage.apiKey.test') }}
          </button>

          <button
            v-if="provider.has_api_key"
            :disabled="isDeleting"
            class="px-3 py-1.5 text-sm text-red-600 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 disabled:opacity-50 transition-colors"
            @click="$emit('deleteKey')"
          >
            {{ $t('panel.aiSettingsPage.apiKey.remove') }}
          </button>
        </div>
      </div>

      <!-- Test Result -->
      <div
        v-if="testResult"
        :class="[
          'mt-2 px-3 py-2 rounded-lg text-xs flex items-center gap-2',
          testResult.success
            ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400'
            : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'
        ]"
      >
        <span>{{ testResult.success ? '&#x2705;' : '&#x274C;' }}</span>
        <span class="flex-1">{{ testResult.message }}</span>
        <span v-if="testResult.response_time" class="opacity-75">
          {{ $t('panel.aiSettingsPage.messages.responseTime', { time: testResult.response_time }) }}
        </span>
      </div>

      <!-- Last Validated -->
      <div v-if="provider.last_validated" class="mt-2 text-[10px] text-[var(--color-text-secondary)]">
        {{ $t('panel.aiSettingsPage.settings.lastValidated') }} {{ formattedLastValidated }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

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

const expanded = ref(false)

const formattedLastValidated = computed((): string => {
  if (!props.provider.last_validated) return ''
  return new Date(props.provider.last_validated).toLocaleString('de-DE')
})
</script>
