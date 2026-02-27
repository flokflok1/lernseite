<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-white">
        {{ $t('panel.systemFeatures.admin.title') }}
      </h2>
      <p class="text-gray-400 mt-1">
        {{ $t('panel.systemFeatures.admin.subtitle') }}
      </p>
    </div>

    <!-- Stats Bar -->
    <div
      v-if="!loading && features.length > 0"
      class="flex items-center gap-4 text-sm"
    >
      <span class="px-3 py-1 rounded-full bg-green-500/20 text-green-300 border border-green-500/30">
        {{ activeCount }} {{ $t('panel.systemFeatures.admin.active') }}
      </span>
      <span class="px-3 py-1 rounded-full bg-gray-500/20 text-gray-400 border border-gray-500/30">
        {{ features.length - activeCount }} {{ $t('panel.systemFeatures.admin.inactive') }}
      </span>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="space-y-4">
      <div
        v-for="i in 4"
        :key="i"
        class="bg-[#1a1f35] rounded-lg border border-[#2a3350] p-6 animate-pulse"
      >
        <div class="h-5 bg-[#2a3350] rounded w-48 mb-4" />
        <div class="space-y-3">
          <div class="h-4 bg-[#2a3350] rounded w-full" />
          <div class="h-4 bg-[#2a3350] rounded w-3/4" />
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-red-500/10 border border-red-500/30 rounded-lg p-6 text-red-300"
    >
      {{ error }}
    </div>

    <!-- Category Cards -->
    <div v-else class="space-y-4">
      <div
        v-for="category in groupedCategories"
        :key="category.name"
        class="bg-[#1a1f35] rounded-lg border border-[#2a3350] overflow-hidden"
      >
        <!-- Category Header (clickable) -->
        <button
          class="w-full flex items-center justify-between p-5 text-left hover:bg-[#1e2440] transition-colors"
          @click="toggleCategory(category.name)"
        >
          <div class="flex items-center gap-3">
            <svg
              class="w-5 h-5 text-primary-400 transition-transform"
              :class="{ 'rotate-90': expandedCategories.has(category.name) }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              />
            </svg>
            <h3 class="text-lg font-semibold text-white">
              {{ $t(`panel.systemFeatures.admin.categories.${category.name}`) }}
            </h3>
          </div>
          <span class="text-sm text-gray-400">
            {{ category.activeCount }}/{{ category.features.length }}
            {{ $t('panel.systemFeatures.admin.active') }}
          </span>
        </button>

        <!-- Feature List (collapsible) -->
        <div v-if="expandedCategories.has(category.name)" class="border-t border-[#2a3350]">
          <div
            v-for="feature in category.features"
            :key="feature.feature_id"
            class="flex items-center justify-between px-5 py-4 border-b border-[#2a3350]/50 last:border-b-0 hover:bg-[#1e2440]/50 transition-colors"
          >
            <div class="flex-1 min-w-0 pr-4">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-white font-medium">{{ feature.feature_name }}</span>
                <span class="text-xs px-2 py-0.5 rounded bg-[#2a3350] text-gray-400 font-mono">
                  {{ feature.feature_code }}
                </span>
                <span
                  v-if="feature.requires_infrastructure"
                  class="text-xs px-2 py-0.5 rounded bg-yellow-500/15 text-yellow-400 border border-yellow-500/30"
                >
                  {{ $t('panel.systemFeatures.admin.requiresInfrastructure') }}
                </span>
                <span
                  v-if="feature.requires_external_service"
                  class="text-xs px-2 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30"
                >
                  {{ $t('panel.systemFeatures.admin.requiresExternalService') }}
                </span>
              </div>
              <p v-if="feature.description" class="text-sm text-gray-400 truncate">
                {{ feature.description }}
              </p>
            </div>

            <!-- Toggle Switch -->
            <button
              :class="[
                'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-[#1a1f35]',
                feature.active ? 'bg-primary-500' : 'bg-gray-600',
                togglingIds.has(feature.feature_id) ? 'opacity-50 cursor-wait' : ''
              ]"
              :disabled="togglingIds.has(feature.feature_id)"
              role="switch"
              :aria-checked="feature.active"
              :aria-label="feature.feature_name"
              @click="toggleFeature(feature)"
            >
              <span
                :class="[
                  'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
                  feature.active ? 'translate-x-5' : 'translate-x-0'
                ]"
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  getSystemFeatures,
  updateSystemFeature,
  type SystemFeature
} from '@/infrastructure/api/clients/panel/admin'

const { t } = useI18n()

const features = ref<SystemFeature[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const expandedCategories = ref(new Set<string>())
const togglingIds = ref(new Set<number>())

const activeCount = computed(() => features.value.filter(f => f.active).length)

interface CategoryGroup {
  name: string
  features: SystemFeature[]
  activeCount: number
}

const groupedCategories = computed<CategoryGroup[]>(() => {
  const groups = new Map<string, SystemFeature[]>()
  for (const feature of features.value) {
    const list = groups.get(feature.category) || []
    list.push(feature)
    groups.set(feature.category, list)
  }
  return Array.from(groups.entries())
    .map(([name, feats]) => ({
      name,
      features: feats,
      activeCount: feats.filter(f => f.active).length
    }))
    .sort((a, b) => a.name.localeCompare(b.name))
})

function toggleCategory(name: string) {
  if (expandedCategories.value.has(name)) {
    expandedCategories.value.delete(name)
  } else {
    expandedCategories.value.add(name)
  }
}

async function loadFeatures() {
  loading.value = true
  error.value = null
  try {
    const result = await getSystemFeatures({ include_inactive: true })
    features.value = result.features
    // Expand all categories by default
    for (const f of features.value) {
      expandedCategories.value.add(f.category)
    }
  } catch (e: any) {
    error.value = e?.response?.data?.message || e?.message || 'Failed to load features'
  } finally {
    loading.value = false
  }
}

async function toggleFeature(feature: SystemFeature) {
  const newActive = !feature.active
  togglingIds.value.add(feature.feature_id)

  // Optimistic update
  feature.active = newActive

  try {
    await updateSystemFeature(feature.feature_id, { active: newActive })
  } catch (e: any) {
    // Revert on error
    feature.active = !newActive
    error.value = t('panel.systemFeatures.admin.toggleError')
    setTimeout(() => { error.value = null }, 3000)
  } finally {
    togglingIds.value.delete(feature.feature_id)
  }
}

onMounted(loadFeatures)
</script>
