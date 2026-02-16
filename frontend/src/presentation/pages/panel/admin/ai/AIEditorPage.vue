<!--
  AI Editor Page

  GBA-based architecture:
  - All authenticated users can access basic AI features
  - Admin users see additional system-wide stats and controls
  - Feature visibility controlled by GBA permissions, not route guards
-->

<template>
  <div class="p-6">
    <div class="max-w-2xl mx-auto">
      <!-- Core AI Editor (for all authenticated users) -->
      <AIEditorCore @open-editor="openAIEditor" />

      <!-- Stats Section -->
      <AIEditorStats
        :stats="stats"
        :loading="loading"
        :show-cost="isAdmin"
      />

      <!-- Admin-only: Additional Controls -->
      <div v-if="isAdmin" class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800">
        <div class="flex items-center gap-2 text-amber-800 dark:text-amber-200">
          <span class="text-lg">🔐</span>
          <span class="font-medium">{{ $t('panel.aiEditor.adminSection') }}</span>
        </div>
        <p class="text-sm text-amber-600 dark:text-amber-400 mt-1">
          {{ $t('panel.aiEditor.adminSectionDesc') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
import { usePanelStore } from '@/application/stores/modules/workspace'
import http from '@/infrastructure/api/http'
import AIEditorCore from './components/AIEditorCore.vue'
import AIEditorStats from './components/AIEditorStats.vue'

useI18n()

const authStore = useAuthStore()
const panelStore = usePanelStore()

// GBA-based role check
const isAdmin = computed(() => authStore.isSystemAdmin || authStore.isOrgAdmin)

// State
const loading = ref(true)
const stats = ref({
  videos: '0',
  prompts: '0',
  tokens: '0',
  cost: '$0',
  courses: '0'
})

// Load stats based on user role
async function loadStats() {
  loading.value = true
  try {
    // Admin sees system-wide stats
    const endpoint = isAdmin.value
      ? '/panel/ai/usage-stats?period=month'
      : '/ai/my-usage-stats?period=month'

    const response = await http.get(endpoint)
    if (response.data.success) {
      const data = response.data.data
      stats.value = {
        videos: data.total_generations?.toString() || '0',
        prompts: data.total_requests?.toString() || '0',
        tokens: formatTokens(data.total_tokens || 0),
        cost: formatCost(parseFloat(data.total_cost) || 0),
        courses: data.courses_count?.toString() || '0'
      }
    }
  } catch (error) {
    console.log('AI stats error:', error)
    stats.value = {
      videos: '0',
      prompts: '0',
      tokens: '0',
      cost: '$0',
      courses: '0'
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

// Open AI Editor Panel
function openAIEditor() {
  panelStore.openPanel({
    type: 'admin-ai-editor'
  })
}

// Load stats on mount
onMounted(() => {
  loadStats()
})
</script>
