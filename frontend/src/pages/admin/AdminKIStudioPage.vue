<!--
  Admin KI-Studio Page

  Öffnet automatisch das KI-Studio Pro Fenster.
  Das KI-Studio vereint alle KI-Funktionen:
  - Content & Video Generierung
  - Prompts Management
  - Modell-Konfiguration
  - Statistiken
-->

<template>
  <div class="p-6">
    <!-- Info Card -->
    <div class="max-w-2xl mx-auto">
      <div class="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-8 text-white text-center">
        <div class="w-20 h-20 mx-auto mb-6 bg-white/20 rounded-2xl flex items-center justify-center">
          <span class="text-5xl">✨</span>
        </div>
        <h1 class="text-3xl font-bold mb-3">{{ $t('admin.kiStudio.title') }}</h1>
        <p class="text-white/80 mb-6 max-w-md mx-auto">
          {{ $t('admin.kiStudio.description') }}
        </p>

        <button
          @click="openKIStudio()"
          class="px-8 py-4 bg-white text-violet-600 font-bold rounded-xl hover:bg-white/90 transition-colors text-lg"
        >
          {{ $t('admin.kiStudio.openStudio') }}
        </button>

        <!-- Features -->
        <div class="grid grid-cols-3 gap-4 mt-8 text-sm">
          <div class="bg-white/10 rounded-xl p-4">
            <span class="text-2xl mb-2 block">🎬</span>
            <span class="font-medium">{{ $t('admin.kiStudio.features.videos') }}</span>
            <p class="text-white/60 text-xs mt-1">{{ $t('admin.kiStudio.features.videosDesc') }}</p>
          </div>
          <div class="bg-white/10 rounded-xl p-4">
            <span class="text-2xl mb-2 block">📝</span>
            <span class="font-medium">{{ $t('admin.kiStudio.features.prompts') }}</span>
            <p class="text-white/60 text-xs mt-1">{{ $t('admin.kiStudio.features.promptsDesc') }}</p>
          </div>
          <div class="bg-white/10 rounded-xl p-4">
            <span class="text-2xl mb-2 block">⚙️</span>
            <span class="font-medium">{{ $t('admin.kiStudio.features.models') }}</span>
            <p class="text-white/60 text-xs mt-1">{{ $t('admin.kiStudio.features.modelsDesc') }}</p>
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-4 gap-4 mt-6">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            <span v-if="loading" class="animate-pulse">--</span>
            <span v-else>{{ stats.videos }}</span>
          </div>
          <div class="text-sm text-gray-500">{{ $t('admin.kiStudio.stats.videosGenerated') }}</div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            <span v-if="loading" class="animate-pulse">--</span>
            <span v-else>{{ stats.prompts }}</span>
          </div>
          <div class="text-sm text-gray-500">{{ $t('admin.kiStudio.stats.prompts') }}</div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div class="text-2xl font-bold text-gray-900 dark:text-white">
            <span v-if="loading" class="animate-pulse">--</span>
            <span v-else>{{ stats.tokens }}</span>
          </div>
          <div class="text-sm text-gray-500">{{ $t('admin.kiStudio.stats.tokensMonth') }}</div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div class="text-2xl font-bold text-green-600">
            <span v-if="loading" class="animate-pulse">--</span>
            <span v-else>{{ stats.cost }}</span>
          </div>
          <div class="text-sm text-gray-500">{{ $t('admin.kiStudio.stats.costMonth') }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useWindowStore } from '@/store/window.store'
import http from '@/api/http'

useI18n()
const windowStore = useWindowStore()

// State
const loading = ref(true)
const stats = ref({
  videos: '0',
  prompts: '0',
  tokens: '0',
  cost: '$0'
})

// Load real stats from API (using existing usage-stats endpoint)
async function loadStats() {
  loading.value = true
  try {
    const response = await http.get('/admin/ai/usage-stats?period=month')
    if (response.data.success) {
      const data = response.data.data
      stats.value = {
        videos: data.total_generations?.toString() || '0',
        prompts: data.total_requests?.toString() || '0',
        tokens: formatTokens(data.total_tokens || 0),
        cost: formatCost(parseFloat(data.total_cost) || 0)
      }
    }
  } catch (error) {
    console.log('AI stats error:', error)
    stats.value = {
      videos: '0',
      prompts: '0',
      tokens: '0',
      cost: '$0'
    }
  } finally {
    loading.value = false
  }
}

function formatTokens(tokens: number): string {
  if (tokens >= 1000000) {
    return (tokens / 1000000).toFixed(1) + 'M'
  } else if (tokens >= 1000) {
    return (tokens / 1000).toFixed(0) + 'K'
  }
  return tokens.toString()
}

function formatCost(cost: number): string {
  return '$' + cost.toFixed(2)
}

// Open KI-Studio Window
function openKIStudio() {
  windowStore.openWindow({
    type: 'admin-ai-studio',
    title: 'KI-Studio Pro'
  })
}

// Load stats on mount
onMounted(() => {
  loadStats()
})
</script>
