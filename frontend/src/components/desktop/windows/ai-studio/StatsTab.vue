<!--
  Stats Tab - AI Usage Statistics & Analytics (Production-Ready)

  Features:
  - KI-Nutzungsstatistiken aus der Datenbank
  - Token-Verbrauch und Kosten
  - Modell-basierte Nutzung
  - Letzte Aktivitäten
  - Performance-Metriken
-->

<template>
  <div class="stats-tab p-6">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-20">
      <div class="animate-spin text-4xl">⏳</div>
      <span class="ml-3 text-[var(--color-text-secondary)]">Lade Statistiken...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="loadError" class="p-6 bg-red-50 dark:bg-red-900/20 rounded-xl text-center">
      <div class="text-4xl mb-3">❌</div>
      <h3 class="text-lg font-semibold text-red-600 dark:text-red-400 mb-2">Fehler beim Laden</h3>
      <p class="text-red-500 dark:text-red-300 mb-4">{{ loadError }}</p>
      <button @click="loadStats" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
        Erneut versuchen
      </button>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-xl font-bold text-[var(--color-text-primary)]">Statistiken</h2>
          <p class="text-sm text-[var(--color-text-secondary)] mt-1">
            KI-Nutzung und Performance überwachen
          </p>
        </div>
        <div class="flex gap-2">
          <select
            v-model="selectedPeriod"
            @change="loadStats"
            class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
          >
            <option value="today">Heute</option>
            <option value="week">Diese Woche</option>
            <option value="month">Dieser Monat</option>
            <option value="year">Dieses Jahr</option>
          </select>
          <button
            @click="loadStats"
            :disabled="isLoading"
            class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded-lg hover:bg-[var(--color-surface-secondary)] transition-colors flex items-center gap-2"
          >
            <span :class="{ 'animate-spin': isLoading }">🔄</span>
            Aktualisieren
          </button>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="grid grid-cols-4 gap-4 mb-8">
        <div class="bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl p-4 text-white">
          <div class="flex items-center justify-between mb-2">
            <span class="text-blue-100">Tokens gesamt</span>
            <span class="text-2xl">🪙</span>
          </div>
          <div class="text-3xl font-bold">{{ formatNumber(stats.total_tokens) }}</div>
          <div class="text-sm text-blue-100 mt-1">
            {{ selectedPeriodLabel }}
          </div>
        </div>

        <div class="bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl p-4 text-white">
          <div class="flex items-center justify-between mb-2">
            <span class="text-green-100">Kosten (geschätzt)</span>
            <span class="text-2xl">💰</span>
          </div>
          <div class="text-3xl font-bold">${{ stats.total_cost.toFixed(2) }}</div>
          <div class="text-sm text-green-100 mt-1">
            ~$0.002/1K Tokens
          </div>
        </div>

        <div class="bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl p-4 text-white">
          <div class="flex items-center justify-between mb-2">
            <span class="text-purple-100">Generierungen</span>
            <span class="text-2xl">✨</span>
          </div>
          <div class="text-3xl font-bold">{{ formatNumber(stats.total_generations) }}</div>
          <div class="text-sm text-purple-100 mt-1">
            {{ stats.total_sessions }} Sessions
          </div>
        </div>

        <div class="bg-gradient-to-br from-orange-500 to-red-500 rounded-xl p-4 text-white">
          <div class="flex items-center justify-between mb-2">
            <span class="text-orange-100">Erfolgsrate</span>
            <span class="text-2xl">📈</span>
          </div>
          <div class="text-3xl font-bold">{{ performance.success_rate }}%</div>
          <div class="text-sm text-orange-100 mt-1">
            {{ performance.total_requests }} Requests
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-2 gap-6 mb-8">
        <!-- Usage by Category -->
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] mb-4">Nutzung nach Kategorie</h3>
          <div v-if="byCategory.length > 0" class="space-y-3">
            <div
              v-for="item in byCategory"
              :key="item.category"
              class="flex items-center gap-3"
            >
              <span class="text-xl">{{ getCategoryEmoji(item.category) }}</span>
              <div class="flex-1">
                <div class="flex items-center justify-between text-sm mb-1">
                  <span class="text-[var(--color-text-primary)] capitalize">{{ item.category }}</span>
                  <span class="font-medium text-[var(--color-text-primary)]">{{ formatNumber(item.tokens) }} Tokens</span>
                </div>
                <div class="h-2 bg-[var(--color-surface-secondary)] rounded-full overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all bg-blue-500"
                    :style="{ width: getCategoryPercentage(item.tokens) + '%' }"
                  ></div>
                </div>
              </div>
              <span class="text-xs text-[var(--color-text-tertiary)] w-16 text-right">
                {{ item.count }} mal
              </span>
            </div>
          </div>
          <div v-else class="text-center py-8 text-[var(--color-text-tertiary)]">
            Keine Daten für diesen Zeitraum
          </div>
        </div>

        <!-- Performance Metrics -->
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] mb-4">Performance-Metriken</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="text-center p-4 bg-[var(--color-surface-secondary)] rounded-lg">
              <div class="text-3xl font-bold text-[var(--color-text-primary)]">{{ performance.avg_latency_ms }}ms</div>
              <div class="text-xs text-[var(--color-text-tertiary)] mt-1">Durchschn. Latenz</div>
            </div>
            <div class="text-center p-4 bg-[var(--color-surface-secondary)] rounded-lg">
              <div class="text-3xl font-bold text-green-500">{{ performance.success_rate }}%</div>
              <div class="text-xs text-[var(--color-text-tertiary)] mt-1">Erfolgsrate</div>
            </div>
            <div class="text-center p-4 bg-[var(--color-surface-secondary)] rounded-lg">
              <div class="text-3xl font-bold text-[var(--color-text-primary)]">{{ avgTokensPerRequest }}</div>
              <div class="text-xs text-[var(--color-text-tertiary)] mt-1">Tokens/Request</div>
            </div>
            <div class="text-center p-4 bg-[var(--color-surface-secondary)] rounded-lg">
              <div class="text-3xl font-bold text-[var(--color-text-primary)]">{{ stats.total_sessions }}</div>
              <div class="text-xs text-[var(--color-text-tertiary)] mt-1">Sessions</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Model Usage & Recent Activity -->
      <div class="grid grid-cols-2 gap-6">
        <!-- Model Usage -->
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] mb-4">Modell-Nutzung</h3>
          <div v-if="byModel.length > 0" class="space-y-3">
            <div
              v-for="model in byModel"
              :key="model.model_name"
              class="flex items-center justify-between p-3 bg-[var(--color-surface-secondary)] rounded-lg"
            >
              <div class="flex items-center gap-3">
                <span
                  class="w-8 h-8 rounded-lg flex items-center justify-center text-sm"
                  :class="getProviderStyle(model.provider)"
                >
                  {{ getProviderIcon(model.provider) }}
                </span>
                <div>
                  <div class="text-sm font-medium text-[var(--color-text-primary)]">{{ model.model_name }}</div>
                  <div class="text-xs text-[var(--color-text-tertiary)]">{{ model.provider || 'Unknown' }}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-sm font-medium text-[var(--color-text-primary)]">{{ model.request_count }} Requests</div>
                <div class="text-xs text-[var(--color-text-tertiary)]">{{ formatNumber(model.tokens_used) }} Tokens</div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-[var(--color-text-tertiary)]">
            Keine Modell-Nutzung in diesem Zeitraum
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="bg-[var(--color-surface)] rounded-xl border border-[var(--color-border)] p-4">
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] mb-4">Letzte Aktivitäten</h3>
          <div v-if="recentActivity.length > 0" class="space-y-2 max-h-64 overflow-y-auto">
            <div
              v-for="activity in recentActivity"
              :key="activity.id"
              class="flex items-start gap-3 p-2 hover:bg-[var(--color-surface-secondary)] rounded-lg transition-colors"
            >
              <span
                class="w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0"
                :class="getActivityColor(activity.type)"
              >
                {{ getActivityIcon(activity.type) }}
              </span>
              <div class="flex-1 min-w-0">
                <div class="text-sm text-[var(--color-text-primary)] truncate">{{ activity.title }}</div>
                <div class="text-xs text-[var(--color-text-tertiary)]">
                  {{ activity.model }} • {{ activity.tokens > 0 ? `${activity.tokens} tokens` : '-' }}
                </div>
              </div>
              <div class="text-xs text-[var(--color-text-tertiary)] flex-shrink-0">
                {{ activity.time }}
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-[var(--color-text-tertiary)]">
            Keine Aktivitäten in diesem Zeitraum
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import http from '@/api/http'

// Types
interface UsageStats {
  total_tokens: number
  total_cost: number
  total_generations: number
  total_sessions: number
  avg_latency_ms: number
}

interface ModelUsage {
  model_name: string
  provider: string
  request_count: number
  tokens_used: number
}

interface CategoryUsage {
  category: string
  count: number
  tokens: number
}

interface Activity {
  id: string
  type: string
  title: string
  model: string
  tokens: number
  time: string
}

interface Performance {
  avg_latency_ms: number
  success_rate: number
  total_requests: number
}

// State
const isLoading = ref(true)
const loadError = ref<string | null>(null)
const selectedPeriod = ref('month')

const stats = ref<UsageStats>({
  total_tokens: 0,
  total_cost: 0,
  total_generations: 0,
  total_sessions: 0,
  avg_latency_ms: 0
})

const byModel = ref<ModelUsage[]>([])
const byCategory = ref<CategoryUsage[]>([])
const recentActivity = ref<Activity[]>([])
const performance = ref<Performance>({
  avg_latency_ms: 0,
  success_rate: 0,
  total_requests: 0
})

// Computed
const selectedPeriodLabel = computed(() => {
  const labels: Record<string, string> = {
    today: 'Heute',
    week: 'Diese Woche',
    month: 'Dieser Monat',
    year: 'Dieses Jahr'
  }
  return labels[selectedPeriod.value] || selectedPeriod.value
})

const avgTokensPerRequest = computed(() => {
  if (performance.value.total_requests === 0) return '0'
  const avg = stats.value.total_tokens / performance.value.total_requests
  return formatNumber(Math.round(avg))
})

const maxCategoryTokens = computed(() => {
  if (byCategory.value.length === 0) return 1
  return Math.max(...byCategory.value.map(c => c.tokens), 1)
})

// Methods
function formatNumber(num: number): string {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
  return num.toString()
}

function getCategoryPercentage(tokens: number): number {
  return Math.round((tokens / maxCategoryTokens.value) * 100)
}

function getCategoryEmoji(category: string): string {
  const emojis: Record<string, string> = {
    content_generation: '📝',
    quiz_generation: '❓',
    theory_generation: '📚',
    video_generation: '🎬',
    audio_generation: '🎵',
    image_generation: '🖼️',
    translation: '🌍',
    summarization: '📋',
    variant_generation: '🔄',
    default: '⚙️'
  }
  return emojis[category] || emojis.default
}

function getProviderIcon(provider: string): string {
  const icons: Record<string, string> = {
    openai: '🤖',
    anthropic: '🧠',
    google: '🔍',
    deepl: '🌍'
  }
  return icons[provider?.toLowerCase()] || '⚙️'
}

function getProviderStyle(provider: string): string {
  const styles: Record<string, string> = {
    openai: 'bg-green-100 dark:bg-green-900/30',
    anthropic: 'bg-orange-100 dark:bg-orange-900/30',
    google: 'bg-blue-100 dark:bg-blue-900/30',
    deepl: 'bg-cyan-100 dark:bg-cyan-900/30'
  }
  return styles[provider?.toLowerCase()] || 'bg-gray-100 dark:bg-gray-900/30'
}

function getActivityIcon(type: string): string {
  const icons: Record<string, string> = {
    video: '🎬',
    content: '📝',
    quiz: '❓',
    audio: '🎵',
    image: '🖼️',
    content_generation: '📝',
    quiz_generation: '❓',
    theory_generation: '📚',
    variant_generation: '🔄'
  }
  return icons[type] || '⚙️'
}

function getActivityColor(type: string): string {
  const colors: Record<string, string> = {
    video: 'bg-red-100 dark:bg-red-900/30',
    content: 'bg-blue-100 dark:bg-blue-900/30',
    quiz: 'bg-purple-100 dark:bg-purple-900/30',
    audio: 'bg-green-100 dark:bg-green-900/30',
    image: 'bg-pink-100 dark:bg-pink-900/30',
    content_generation: 'bg-blue-100 dark:bg-blue-900/30',
    quiz_generation: 'bg-purple-100 dark:bg-purple-900/30',
    theory_generation: 'bg-cyan-100 dark:bg-cyan-900/30',
    variant_generation: 'bg-yellow-100 dark:bg-yellow-900/30'
  }
  return colors[type] || 'bg-gray-100 dark:bg-gray-900/30'
}

// Load stats from API
async function loadStats() {
  isLoading.value = true
  loadError.value = null

  try {
    const response = await http.get('/admin/ai/usage-stats', {
      params: { period: selectedPeriod.value }
    })

    if (response.data.success) {
      const data = response.data.data

      stats.value = {
        total_tokens: data.overview?.total_tokens || 0,
        total_cost: data.overview?.total_cost || 0,
        total_generations: data.overview?.total_generations || 0,
        total_sessions: data.overview?.total_sessions || 0,
        avg_latency_ms: data.overview?.avg_latency_ms || 0
      }

      byModel.value = data.by_model || []
      byCategory.value = data.by_category || []
      recentActivity.value = data.recent_activity || []

      performance.value = {
        avg_latency_ms: data.performance?.avg_latency_ms || 0,
        success_rate: data.performance?.success_rate || 0,
        total_requests: data.performance?.total_requests || 0
      }
    } else {
      throw new Error(response.data.error?.message || 'Fehler beim Laden')
    }
  } catch (error: any) {
    console.error('Failed to load stats:', error)
    loadError.value = error.response?.data?.error?.message || error.message || 'Fehler beim Laden der Statistiken'
  } finally {
    isLoading.value = false
  }
}

// Load on mount
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stats-tab {
  min-height: 400px;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}
</style>
