<script setup lang="ts">
/**
 * Admin LM Model Routing - Simplified Version
 *
 * OBEN: Kategorien zum Einstellen (Audio, Chat, Video, etc.)
 * UNTEN: LMs mit Anzeige welche Kategorien sie brauchen
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  getAllLMSlotsOverview,
  adminGetAIModels,
  applySlotPreset,
  setDefaultModelForCategory,
  type LMSlotOverview,
  type AIModel
} from '@/application/services/api/admin'

const { t } = useI18n()

// State
const loading = ref(true)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// Data
const lmsOverview = ref<LMSlotOverview[]>([])
const models = ref<AIModel[]>([])

// Selected default model for each category
const selectedDefaults = ref<Record<string, number | null>>({})

// Category definitions - same as AI Model Selector
const categories = computed(() => [
  { code: 'audio', name: t('admin.lmRouting.categories.audio'), emoji: '🎵', color: 'bg-green-500' },
  { code: 'chat', name: t('admin.lmRouting.categories.chat'), emoji: '💬', color: 'bg-blue-500' },
  { code: 'embedding', name: t('admin.lmRouting.categories.embedding'), emoji: '📊', color: 'bg-cyan-500' },
  { code: 'image', name: t('admin.lmRouting.categories.image'), emoji: '🖼️', color: 'bg-pink-500' },
  { code: 'moderation', name: t('admin.lmRouting.categories.moderation'), emoji: '🛡️', color: 'bg-gray-500' },
  { code: 'realtime', name: t('admin.lmRouting.categories.realtime'), emoji: '⚡', color: 'bg-yellow-500' },
  { code: 'reasoning', name: t('admin.lmRouting.categories.reasoning'), emoji: '🧠', color: 'bg-orange-500' },
  { code: 'video', name: t('admin.lmRouting.categories.video'), emoji: '🎬', color: 'bg-red-500' },
  { code: 'vision', name: t('admin.lmRouting.categories.vision'), emoji: '👁️', color: 'bg-indigo-500' }
])

// Models grouped by category
const modelsByCategory = computed(() => {
  const grouped: Record<string, AIModel[]> = {}
  for (const cat of categories) {
    grouped[cat.code] = models.value.filter(m => m.category === cat.code)
  }
  return grouped
})

// Get category info by code
const getCategoryInfo = (code: string) => categories.find(c => c.code === code)

// What categories does each LM need?
const getLMRequirements = (lm: LMSlotOverview) => {
  const required: string[] = []
  const optional: string[] = []

  for (const slot of lm.slots) {
    // Map slot codes to categories
    let catCode = slot.slot_code
    // Map specific slots to categories
    if (slot.slot_code === 'tts' || slot.slot_code === 'stt') catCode = 'audio'
    if (slot.slot_code === 'image_gen') catCode = 'image'
    if (slot.slot_code === 'code_exec') catCode = 'chat' // fallback

    if (slot.is_required && !required.includes(catCode)) {
      required.push(catCode)
    } else if (!slot.is_required && !optional.includes(catCode) && !required.includes(catCode)) {
      optional.push(catCode)
    }
  }

  return { required, optional }
}

// Load data
const loadData = async () => {
  loading.value = true
  error.value = null

  try {
    const [overviewData, modelsData] = await Promise.all([
      getAllLMSlotsOverview(),
      adminGetAIModels({ active_only: true })
    ])

    lmsOverview.value = overviewData.lms
    const modelsArray = (modelsData as any)?.data?.models || (modelsData as any)?.models || []
    models.value = Array.isArray(modelsArray) ? modelsArray : []
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.lmRouting.loadError')
  } finally {
    loading.value = false
  }
}

// Preset handlers
const presetRunning = ref<string | null>(null)

const applyPreset = async (preset: 'cheap' | 'medium' | 'expensive') => {
  presetRunning.value = preset
  try {
    const result = await applySlotPreset(preset)
    successMessage.value = t('admin.lmRouting.slotsConfigured', { count: result.configured })
    await loadData()
    setTimeout(() => { successMessage.value = null }, 3000)
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.lmRouting.loadError')
  } finally {
    presetRunning.value = null
  }
}

const getLMCode = (id: number) => `LM${id.toString().padStart(2, '0')}`

// Save default model for category
const savingCategory = ref<string | null>(null)
const saveDefaultModel = async (categoryCode: string, modelId: number | null) => {
  if (!modelId) return

  savingCategory.value = categoryCode
  try {
    await setDefaultModelForCategory(categoryCode, modelId)
    successMessage.value = t('admin.lmRouting.defaultModelSet', { category: categoryCode })
    setTimeout(() => { successMessage.value = null }, 2000)
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('admin.lmRouting.saveError')
  } finally {
    savingCategory.value = null
  }
}

// Watch for changes in selected defaults
watch(selectedDefaults, (newVal, oldVal) => {
  for (const [category, modelId] of Object.entries(newVal)) {
    if (oldVal[category] !== modelId && modelId !== null) {
      saveDefaultModel(category, modelId)
    }
  }
}, { deep: true })

// LM Groups
const lmGroups = computed(() => {
  const groups: Record<string, LMSlotOverview[]> = {
    'A': [], 'B': [], 'C': [], 'D': [], 'E': [], 'F': []
  }
  for (const lm of lmsOverview.value) {
    if (lm.group && groups[lm.group]) {
      groups[lm.group].push(lm)
    }
  }
  return groups
})

const getGroupName = (key: string) => t(`admin.lmRouting.groupNames.${key}`)

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ $t('admin.lmRouting.title') }}</h1>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
        {{ $t('admin.lmRouting.subtitle') }}
      </p>
    </div>

    <!-- Messages -->
    <div v-if="successMessage" class="mb-4 p-3 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-lg">
      {{ successMessage }}
    </div>
    <div v-if="error" class="mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg">
      {{ error }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>

    <template v-else>
      <!-- SECTION 1: Quick Presets -->
      <div class="mb-8 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.lmRouting.quickSetup') }}</span>
          <div class="flex gap-2">
            <button
              @click="applyPreset('cheap')"
              :disabled="presetRunning !== null"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium disabled:opacity-50"
            >
              {{ presetRunning === 'cheap' ? '...' : '💰 ' + $t('admin.lmRouting.presetCheap') }}
            </button>
            <button
              @click="applyPreset('medium')"
              :disabled="presetRunning !== null"
              class="px-4 py-2 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg font-medium disabled:opacity-50"
            >
              {{ presetRunning === 'medium' ? '...' : '⚖️ ' + $t('admin.lmRouting.presetMedium') }}
            </button>
            <button
              @click="applyPreset('expensive')"
              :disabled="presetRunning !== null"
              class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium disabled:opacity-50"
            >
              {{ presetRunning === 'expensive' ? '...' : '👑 ' + $t('admin.lmRouting.presetPremium') }}
            </button>
          </div>
        </div>
      </div>

      <!-- SECTION 2: Category Model Selection -->
      <div class="mb-8">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ $t('admin.lmRouting.defaultModelsPerCategory') }}</h2>
        <div class="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-3">
          <div
            v-for="cat in categories"
            :key="cat.code"
            class="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-200 dark:border-gray-700"
          >
            <div class="text-center mb-2">
              <span class="text-2xl">{{ cat.emoji }}</span>
              <div class="text-xs font-medium text-gray-700 dark:text-gray-300 mt-1">{{ cat.name }}</div>
              <div class="text-xs text-gray-400">{{ modelsByCategory[cat.code]?.length || 0 }}</div>
            </div>
            <select
              v-model="selectedDefaults[cat.code]"
              class="w-full text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option :value="null">-</option>
              <option
                v-for="model in modelsByCategory[cat.code]"
                :key="model.model_id"
                :value="model.model_id"
              >
                {{ model.display_name || model.model_name }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- SECTION 3: LMs and their requirements -->
      <div>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ $t('admin.lmRouting.lmRequirements') }}</h2>

        <div class="space-y-6">
          <div v-for="(lms, groupKey) in lmGroups" :key="groupKey">
            <template v-if="lms.length > 0">
              <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
                {{ $t('admin.lmRouting.group', { key: groupKey, name: getGroupName(groupKey as string) }) }}
              </h3>

              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                <div
                  v-for="lm in lms"
                  :key="lm.learning_method_id"
                  class="bg-white dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700"
                >
                  <div class="flex items-center justify-between mb-2">
                    <div>
                      <span class="font-mono text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded mr-2">
                        {{ getLMCode(lm.learning_method_id) }}
                      </span>
                      <span class="text-sm font-medium text-gray-900 dark:text-white">{{ lm.name }}</span>
                    </div>
                    <span
                      :class="[
                        'text-xs px-2 py-0.5 rounded-full',
                        lm.ready
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                          : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                      ]"
                    >
                      {{ lm.ready ? '✓' : '!' }}
                    </span>
                  </div>

                  <!-- Required & Optional Categories -->
                  <div class="flex flex-wrap gap-1">
                    <template v-for="catCode in getLMRequirements(lm).required" :key="catCode">
                      <span
                        class="text-xs px-2 py-0.5 rounded-full text-white"
                        :class="getCategoryInfo(catCode)?.color || 'bg-gray-500'"
                        :title="'Required: ' + getCategoryInfo(catCode)?.name"
                      >
                        {{ getCategoryInfo(catCode)?.emoji }} {{ getCategoryInfo(catCode)?.name }}
                      </span>
                    </template>
                    <template v-for="catCode in getLMRequirements(lm).optional" :key="catCode + '-opt'">
                      <span
                        class="text-xs px-2 py-0.5 rounded-full bg-gray-200 text-gray-600 dark:bg-gray-700 dark:text-gray-400"
                        :title="'Optional: ' + getCategoryInfo(catCode)?.name"
                      >
                        {{ getCategoryInfo(catCode)?.emoji }}
                      </span>
                    </template>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <h4 class="font-medium text-blue-900 dark:text-blue-300 mb-2">{{ $t('admin.lmRouting.legend') }}</h4>
        <div class="flex flex-wrap gap-4 text-sm text-blue-700 dark:text-blue-400">
          <span>🎵 {{ $t('admin.lmRouting.legendAudio') }}</span>
          <span>💬 {{ $t('admin.lmRouting.legendChat') }}</span>
          <span>🎬 {{ $t('admin.lmRouting.legendVideo') }}</span>
          <span>⚡ {{ $t('admin.lmRouting.legendRealtime') }}</span>
          <span>🧠 {{ $t('admin.lmRouting.legendReasoning') }}</span>
        </div>
        <div class="mt-2 text-xs text-blue-600 dark:text-blue-500">
          {{ $t('admin.lmRouting.legendColoredRequired') }} | {{ $t('admin.lmRouting.legendGrayOptional') }}
        </div>
      </div>
    </template>
  </div>
</template>
