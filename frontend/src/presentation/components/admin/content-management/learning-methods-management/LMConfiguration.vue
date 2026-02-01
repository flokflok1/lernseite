<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface LearningMethod {
  id: string
  name: string
  group: string
  description: string
  tier: 'basic' | 'premium' | 'enterprise'
  isActive: boolean
  kiUsage: 'optional' | 'medium' | 'intensive'
}

const learningMethods = ref<LearningMethod[]>([
  {
    id: 'lm00',
    name: 'Reading & Explanation',
    group: 'A',
    description: 'Classic reading material with explanations',
    tier: 'basic',
    isActive: true,
    kiUsage: 'optional'
  },
  {
    id: 'lm01',
    name: 'Video Tutorial',
    group: 'A',
    description: 'Video-based learning content',
    tier: 'basic',
    isActive: true,
    kiUsage: 'optional'
  },
  {
    id: 'lm02',
    name: 'Interactive Simulation',
    group: 'A',
    description: 'Interactive simulations and visualizations',
    tier: 'premium',
    isActive: true,
    kiUsage: 'medium'
  },
  {
    id: 'lm05',
    name: 'Practice Exercises',
    group: 'B',
    description: 'Hands-on practice and exercises',
    tier: 'basic',
    isActive: true,
    kiUsage: 'medium'
  },
  {
    id: 'lm09',
    name: 'Quiz Assessment',
    group: 'C',
    description: 'Knowledge assessment via quizzes',
    tier: 'basic',
    isActive: true,
    kiUsage: 'optional'
  }
])

const filterGroup = ref<'all' | 'A' | 'B' | 'C'>('all')
const filterTier = ref<'all' | 'basic' | 'premium' | 'enterprise'>('all')
const searchQuery = ref('')

const filteredMethods = computed(() => {
  return learningMethods.value.filter(lm => {
    if (filterGroup.value !== 'all' && lm.group !== filterGroup.value) return false
    if (filterTier.value !== 'all' && lm.tier !== filterTier.value) return false
    if (searchQuery.value && !lm.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
      return false
    return true
  })
})

const toggleMethod = (id: string) => {
  const method = learningMethods.value.find(m => m.id === id)
  if (method) {
    method.isActive = !method.isActive
  }
}

const groupLabel = (group: string) => {
  const groups: Record<string, string> = {
    A: t('lm.group.explanation'),
    B: t('lm.group.practice'),
    C: t('lm.group.assessment')
  }
  return groups[group] || group
}
</script>

<template>
  <div class="lm-configuration">
    <h2>{{ $t('admin.learningMethods.title') }}</h2>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="$t('common.search')"
          class="search-box__input"
        />
      </div>

      <div class="filter-group">
        <label>{{ $t('filter.group') }}:</label>
        <select v-model="filterGroup" class="select">
          <option value="all">{{ $t('filter.all') }}</option>
          <option value="A">{{ $t('lm.group.explanation') }}</option>
          <option value="B">{{ $t('lm.group.practice') }}</option>
          <option value="C">{{ $t('lm.group.assessment') }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label>{{ $t('filter.tier') }}:</label>
        <select v-model="filterTier" class="select">
          <option value="all">{{ $t('filter.all') }}</option>
          <option value="basic">{{ $t('tier.basic') }}</option>
          <option value="premium">{{ $t('tier.premium') }}</option>
          <option value="enterprise">{{ $t('tier.enterprise') }}</option>
        </select>
      </div>
    </div>

    <!-- LM Table -->
    <div class="table-container">
      <table v-if="filteredMethods.length > 0" class="lm-table">
        <thead>
          <tr>
            <th>{{ $t('lm.name') }}</th>
            <th>{{ $t('lm.group') }}</th>
            <th>{{ $t('lm.tier') }}</th>
            <th>{{ $t('lm.kiUsage') }}</th>
            <th>{{ $t('lm.status') }}</th>
            <th>{{ $t('table.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lm in filteredMethods" :key="lm.id" :class="{ 'row--inactive': !lm.isActive }">
            <td class="cell-name">
              <strong>{{ lm.name }}</strong>
              <p class="description">{{ lm.description }}</p>
            </td>
            <td>
              <span class="badge badge--group">{{ groupLabel(lm.group) }}</span>
            </td>
            <td>
              <span :class="['badge', `badge--tier-${lm.tier}`]">
                {{ $t(`tier.${lm.tier}`) }}
              </span>
            </td>
            <td>
              <span :class="['badge', `badge--ki-${lm.kiUsage}`]">
                {{ $t(`lm.kiUsage.${lm.kiUsage}`) }}
              </span>
            </td>
            <td>
              <label class="toggle">
                <input type="checkbox" :checked="lm.isActive" @change="toggleMethod(lm.id)" />
                <span class="toggle__slider"></span>
              </label>
            </td>
            <td class="cell-actions">
              <button class="btn btn--sm btn--secondary">{{ $t('common.configure') }}</button>
              <button class="btn btn--sm btn--outline">{{ $t('common.preview') }}</button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-state">
        <p>{{ $t('common.noData') }}</p>
      </div>
    </div>

    <!-- Configuration Info -->
    <div class="config-info">
      <h3>{{ $t('admin.learningMethods.info') }}</h3>
      <div class="info-box">
        <p>
          <strong>{{ $t('admin.learningMethods.groupA') }}:</strong>
          {{ $t('admin.learningMethods.groupADesc') }}
        </p>
        <p>
          <strong>{{ $t('admin.learningMethods.groupB') }}:</strong>
          {{ $t('admin.learningMethods.groupBDesc') }}
        </p>
        <p>
          <strong>{{ $t('admin.learningMethods.groupC') }}:</strong>
          {{ $t('admin.learningMethods.groupCDesc') }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.lm-configuration {
  h2 {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--color-text-primary);
  }
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.search-box {
  flex: 1;
  min-width: 250px;

  &__input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    font-size: 0.95rem;
    background: var(--color-background-primary);
    color: var(--color-text-primary);

    &:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
    }
  }
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;

  label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-secondary);
  }

  .select {
    padding: 0.6rem 0.8rem;
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    font-size: 0.9rem;
    background: var(--color-background-primary);
    color: var(--color-text-primary);
    cursor: pointer;
  }
}

.table-container {
  overflow-x: auto;
  margin-bottom: 2rem;
}

.lm-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  overflow: hidden;

  thead {
    background: var(--color-background-tertiary);
    border-bottom: 2px solid var(--color-border);

    th {
      padding: 1rem;
      text-align: left;
      font-weight: 600;
      color: var(--color-text-primary);
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
  }

  tbody {
    tr {
      border-bottom: 1px solid var(--color-border);
      transition: all 0.2s ease-in-out;

      &:hover {
        background: var(--color-background-primary);
      }

      &--inactive {
        opacity: 0.6;
      }

      td {
        padding: 1rem;
        color: var(--color-text-primary);
      }
    }
  }
}

.cell-name {
  strong {
    display: block;
    margin-bottom: 0.25rem;
  }

  .description {
    margin: 0;
    font-size: 0.85rem;
    color: var(--color-text-secondary);
  }
}

.badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.8rem;
  font-weight: 600;

  &--group {
    background: var(--color-info-light);
    color: var(--color-info-dark);
  }

  &--tier-basic {
    background: var(--color-success-light);
    color: var(--color-success-dark);
  }

  &--tier-premium {
    background: var(--color-warning-light);
    color: var(--color-warning-dark);
  }

  &--tier-enterprise {
    background: var(--color-primary-light);
    color: var(--color-primary-dark);
  }

  &--ki-optional {
    background: var(--color-success-light);
    color: var(--color-success-dark);
  }

  &--ki-medium {
    background: var(--color-warning-light);
    color: var(--color-warning-dark);
  }

  &--ki-intensive {
    background: var(--color-error-light);
    color: var(--color-error-dark);
  }
}

.toggle {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  position: relative;

  input {
    display: none;

    &:checked + .toggle__slider {
      background: var(--color-success);
    }

    &:checked + .toggle__slider::after {
      transform: translateX(1.25rem);
    }
  }

  &__slider {
    display: inline-flex;
    width: 2.5rem;
    height: 1.3rem;
    background: var(--color-border);
    border-radius: 999px;
    position: relative;
    transition: all 0.3s ease-in-out;

    &::after {
      content: '';
      position: absolute;
      width: 1.1rem;
      height: 1.1rem;
      background: white;
      border-radius: 50%;
      top: 0.1rem;
      left: 0.1rem;
      transition: transform 0.3s ease-in-out;
    }
  }
}

.cell-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 0.8rem;
  border: none;
  border-radius: 0.4rem;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease-in-out;

  &--sm {
    padding: 0.4rem 0.7rem;
    font-size: 0.75rem;
  }

  &--secondary {
    background: var(--color-secondary);
    color: white;

    &:hover {
      background: var(--color-secondary-hover);
    }
  }

  &--outline {
    background: transparent;
    border: 1px solid var(--color-border);
    color: var(--color-text-secondary);

    &:hover {
      background: var(--color-background-secondary);
    }
  }
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-secondary);
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
}

.config-info {
  padding: 1.5rem;
  background: var(--color-background-secondary);
  border-radius: 0.5rem;
  border-left: 4px solid var(--color-primary);

  h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--color-text-primary);
    margin: 0 0 1rem 0;
  }
}

.info-box {
  p {
    margin: 0.75rem 0;
    color: var(--color-text-secondary);
    line-height: 1.6;

    strong {
      color: var(--color-text-primary);
    }

    &:last-child {
      margin-bottom: 0;
    }
  }
}
</style>
