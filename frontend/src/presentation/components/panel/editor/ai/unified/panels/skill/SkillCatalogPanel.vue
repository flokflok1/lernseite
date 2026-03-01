<script setup lang="ts">
/**
 * SkillCatalogPanel — Skill grid with search, category filter
 */
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SkillConfig, SkillCategory } from '../../types'

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

const CATEGORY_ICON: Record<string, string> = {
  explanatory: '📖',
  practice: '🎯',
  assessment: '📝',
  content: '📄',
  review: '✅',
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
  <div class="skill-catalog">
    <!-- Search & Filter -->
    <div class="catalog-header">
      <input
        v-model="searchQuery"
        type="text"
        :placeholder="t('aiEditor.skills.searchPlaceholder')"
        class="search-input"
      />
      <div class="category-filters">
        <button
          v-for="cat in availableCategories"
          :key="cat"
          class="category-btn"
          :class="{ active: activeCategory === cat }"
          @click="activeCategory = cat as any"
        >
          {{ t('aiEditor.skills.categories.' + cat) }}
        </button>
      </div>
    </div>

    <!-- Skills Grid -->
    <div class="catalog-body">
      <div v-if="isLoading" class="loading-state">
        {{ t('common.loading') }}
      </div>
      <div v-else-if="filteredSkills.length === 0" class="empty-state">
        {{ t('aiEditor.skills.noResults') }}
      </div>
      <div v-else class="skills-grid">
        <button
          v-for="skill in filteredSkills"
          :key="skill.code"
          class="skill-card"
          :class="{ selected: selectedSkillCode === skill.code }"
          @click="emit('selectSkill', skill)"
        >
          <div class="skill-content">
            <span class="skill-icon">{{ CATEGORY_ICON[skill.category] || '⚡' }}</span>
            <div class="skill-info">
              <div class="skill-name">{{ t(skill.name_i18n_key) }}</div>
              <div class="skill-desc">{{ t(skill.description_i18n_key) }}</div>
              <div class="skill-meta">
                <span class="skill-category" :class="'cat-' + skill.category">
                  {{ t('aiEditor.skills.categories.' + skill.category) }}
                </span>
                <span class="skill-tokens">~{{ skill.estimated_tokens }} tokens</span>
              </div>
            </div>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.skill-catalog {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.catalog-header {
  padding: 0.75rem;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-primary);
  margin-bottom: 0.5rem;
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.category-filters {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.category-btn {
  padding: 0.25rem 0.625rem;
  border-radius: 1rem;
  font-size: 0.6875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  background: var(--color-surface-secondary, var(--color-surface));
  color: var(--color-text-secondary);
}

.category-btn:hover {
  color: var(--color-text-primary);
}

.category-btn.active {
  background: var(--color-primary);
  color: white;
}

.catalog-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 8rem;
  font-size: 0.8125rem;
  color: var(--color-text-tertiary);
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.625rem;
}

.skill-card {
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.skill-card:hover {
  border-color: var(--color-primary);
}

.skill-card.selected {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.skill-content {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
}

.skill-icon {
  font-size: 1.125rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.skill-info {
  min-width: 0;
}

.skill-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.skill-desc {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary);
  margin-top: 0.125rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.skill-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.375rem;
}

.skill-category {
  font-size: 0.5625rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-weight: 600;
  text-transform: uppercase;
  background: var(--color-surface-secondary, var(--color-surface));
  color: var(--color-text-secondary);
}

.cat-explanatory { color: var(--color-info, #63b3ed); }
.cat-practice { color: var(--color-success, #48bb78); }
.cat-assessment { color: var(--color-warning, #ecc94b); }
.cat-content { color: var(--color-primary); }
.cat-review { color: var(--color-success, #48bb78); }

.skill-tokens {
  font-size: 0.5625rem;
  color: var(--color-text-tertiary);
}
</style>
