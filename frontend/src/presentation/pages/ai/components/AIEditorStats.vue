<!--
  AI Editor Stats Component
  Displays AI usage statistics (admin sees full stats, users see limited)
-->

<template>
  <div class="grid grid-cols-4 gap-4 mt-6">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
      <div class="text-2xl font-bold text-gray-900 dark:text-white">
        <span v-if="loading" class="animate-pulse">--</span>
        <span v-else>{{ stats.videos }}</span>
      </div>
      <div class="text-sm text-gray-500">{{ $t('admin.aiEditor.stats.videosGenerated') }}</div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
      <div class="text-2xl font-bold text-gray-900 dark:text-white">
        <span v-if="loading" class="animate-pulse">--</span>
        <span v-else>{{ stats.prompts }}</span>
      </div>
      <div class="text-sm text-gray-500">{{ $t('admin.aiEditor.stats.prompts') }}</div>
    </div>
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
      <div class="text-2xl font-bold text-gray-900 dark:text-white">
        <span v-if="loading" class="animate-pulse">--</span>
        <span v-else>{{ stats.tokens }}</span>
      </div>
      <div class="text-sm text-gray-500">{{ $t('admin.aiEditor.stats.tokensMonth') }}</div>
    </div>
    <!-- Cost only shown for admins -->
    <div
      v-if="showCost"
      class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700"
    >
      <div class="text-2xl font-bold text-green-600">
        <span v-if="loading" class="animate-pulse">--</span>
        <span v-else>{{ stats.cost }}</span>
      </div>
      <div class="text-sm text-gray-500">{{ $t('admin.aiEditor.stats.costMonth') }}</div>
    </div>
    <!-- Users see courses count instead of cost -->
    <div
      v-else
      class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700"
    >
      <div class="text-2xl font-bold text-blue-600">
        <span v-if="loading" class="animate-pulse">--</span>
        <span v-else>{{ stats.courses || '0' }}</span>
      </div>
      <div class="text-sm text-gray-500">{{ $t('admin.aiEditor.stats.courses') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

useI18n()

interface Stats {
  videos: string
  prompts: string
  tokens: string
  cost?: string
  courses?: string
}

defineProps<{
  stats: Stats
  loading: boolean
  showCost?: boolean
}>()
</script>
