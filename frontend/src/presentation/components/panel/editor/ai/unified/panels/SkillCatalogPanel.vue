<script setup lang="ts">
/**
 * SkillCatalogPanel — Skill grid with search, category filter
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SkillConfig, SkillCategory } from '../types'

interface Props {
  skills: SkillConfig[]
  selectedSkillCode?: string | null
  isLoading: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{ selectSkill: [skill: SkillConfig] }>()
const { t } = useI18n()

const searchQuery = ref('')
const activeCategory = ref<SkillCategory | 'all'>('all')

const categoryLabels: Record<string, string> = {
  all: 'aiEditor.skills.categories.all',
  explanatory: 'aiEditor.skills.categories.explanatory',
  practice: 'aiEditor.skills.categories.practice',
  assessment: 'aiEditor.skills.categories.assessment',
  content: 'aiEditor.skills.categories.content',
  review: 'aiEditor.skills.categories.review',
}

const categoryColors: Record<string, string> = {
  explanatory: 'border-blue-500/30 hover:border-blue-500/60',
  practice: 'border-emerald-500/30 hover:border-emerald-500/60',
  assessment: 'border-orange-500/30 hover:border-orange-500/60',
  content: 'border-purple-500/30 hover:border-purple-500/60',
  review: 'border-yellow-500/30 hover:border-yellow-500/60',
}

const filteredSkills = computed(() => {
  let result = props.skills
  if (activeCategory.value !== 'all') {
    result = result.filter(s => s.category === activeCategory.value)
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(s =>
      s.code.toLowerCase().includes(q) ||
      t(s.name_i18n_key).toLowerCase().includes(q)
    )
  }
  return result
})

const availableCategories = computed(() => {
  const cats = new Set(props.skills.map(s => s.category))
  return ['all', ...cats]
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Search & Filter -->
    <div class="p-4 space-y-3 border-b border-gray-700">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="t('aiEditor.skills.searchPlaceholder')"
        class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none"
      />
      <div class="flex gap-1.5 flex-wrap">
        <button
          v-for="cat in availableCategories"
          :key="cat"
          class="px-2.5 py-1 rounded-full text-xs font-medium transition-colors"
          :class="activeCategory === cat
            ? 'bg-indigo-600 text-white'
            : 'bg-gray-800 text-gray-400 hover:text-white'"
          @click="activeCategory = cat as any"
        >
          {{ t(categoryLabels[cat] || cat) }}
        </button>
      </div>
    </div>

    <!-- Skills Grid -->
    <div class="flex-1 overflow-y-auto p-4">
      <div v-if="isLoading" class="flex items-center justify-center h-32">
        <div class="text-gray-500 text-sm animate-pulse">{{ t('common.loading') }}</div>
      </div>
      <div v-else-if="filteredSkills.length === 0" class="text-center text-gray-500 text-sm py-8">
        {{ t('aiEditor.skills.noResults') }}
      </div>
      <div v-else class="grid grid-cols-2 gap-3">
        <button
          v-for="skill in filteredSkills"
          :key="skill.code"
          class="p-3 rounded-lg border bg-gray-800/50 text-left transition-all"
          :class="[
            categoryColors[skill.category] || 'border-gray-700',
            selectedSkillCode === skill.code ? 'ring-2 ring-indigo-500' : '',
          ]"
          @click="emit('selectSkill', skill)"
        >
          <div class="flex items-start gap-2">
            <span class="text-lg mt-0.5">{{ skill.icon }}</span>
            <div class="min-w-0">
              <div class="text-sm font-medium text-white truncate">{{ t(skill.name_i18n_key) }}</div>
              <div class="text-xs text-gray-500 mt-0.5">
                {{ t(skill.description_i18n_key) }}
              </div>
              <div class="flex items-center gap-2 mt-1.5">
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-gray-700 text-gray-400">
                  {{ t(categoryLabels[skill.category] || skill.category) }}
                </span>
                <span class="text-[10px] text-gray-600">~{{ skill.estimated_tokens }} tokens</span>
              </div>
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>
