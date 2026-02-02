<!--
  Category Tree Node

  Recursive component for displaying category hierarchy
  Supports unlimited depth (practical limit: 20 levels)
  Shows path information for deep navigation
-->

<template>
  <div class="category-node" :style="{ marginLeft: `${level * 16}px` }">
    <!-- Category Row - Compact -->
    <div
      class="category-row flex items-center gap-2 px-2 py-1.5 rounded border border-[var(--color-border)] bg-[var(--color-background)] hover:bg-[var(--color-surface)] transition-colors mb-1"
      :class="{ 'opacity-60': !category.is_active }"
    >
      <!-- Expand/Collapse Toggle -->
      <button
        v-if="hasChildren"
        @click="toggleExpanded"
        class="w-5 h-5 flex items-center justify-center text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors text-xs"
      >
        {{ isExpanded ? '▼' : '▶' }}
      </button>
      <div v-else class="w-5"></div>

      <!-- Level Indicator -->
      <div
        class="level-badge px-1.5 py-0.5 rounded text-[10px] font-mono"
        :class="getLevelClass()"
      >
        L{{ category.level }}
      </div>

      <!-- Icon -->
      <div v-if="category.icon" class="text-base">
        {{ category.icon }}
      </div>
      <div v-else class="w-5 h-5 rounded bg-[var(--color-surface)] flex items-center justify-center text-[var(--color-text-secondary)] text-xs">
        📁
      </div>

      <!-- Category Info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-1.5">
          <h3 class="font-medium text-sm text-[var(--color-text-primary)] truncate" :title="category.path || category.name">
            {{ category.name }}
          </h3>
          <span v-if="!category.is_active" class="text-[10px] px-1.5 py-0.5 bg-gray-200 text-gray-600 rounded flex-shrink-0">
            Inaktiv
          </span>
          <span v-if="category.slug" class="text-[10px] text-[var(--color-text-secondary)] font-mono truncate hidden lg:inline">
            /{{ category.slug }}
          </span>
        </div>
        <!-- Path display for deeper levels -->
        <p v-if="category.path && category.level > 2" class="text-[10px] text-[var(--color-text-secondary)] truncate mt-0.5 hidden xl:block" :title="category.path">
          📍 {{ category.path }}
        </p>
      </div>

      <!-- Color Indicator -->
      <div
        v-if="category.color"
        class="w-3 h-3 rounded border border-[var(--color-border)] flex-shrink-0"
        :style="{ backgroundColor: category.color }"
      ></div>

      <!-- Stats - Hidden on smaller screens -->
      <div class="hidden xl:flex items-center gap-2 text-xs text-[var(--color-text-secondary)]">
        <span v-if="category.course_count !== undefined">
          📚 {{ category.course_count }}
        </span>
        <span v-if="hasChildren">
          📂 {{ category.children.length }}
        </span>
      </div>

      <!-- Actions - Compact -->
      <div class="flex items-center gap-1">
        <button
          v-if="category.level < 20"
          @click="$emit('create-child', category)"
          class="w-7 h-7 flex items-center justify-center text-xs bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-primary)] rounded hover:bg-[var(--color-background)] transition-colors"
          :title="$t('panel.actions.createSubcategory')"
        >
          +
        </button>

        <button
          @click="$emit('toggle-active', category)"
          class="w-7 h-7 flex items-center justify-center text-xs rounded transition-colors"
          :class="category.is_active
            ? 'bg-yellow-50 text-yellow-700 hover:bg-yellow-100'
            : 'bg-green-50 text-green-700 hover:bg-green-100'"
          :title="category.is_active ? 'Deaktivieren' : 'Aktivieren'"
        >
          {{ category.is_active ? '⏸' : '▶' }}
        </button>

        <button
          @click="$emit('edit', category)"
          class="w-7 h-7 flex items-center justify-center text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors"
          :title="$t('panel.actions.edit')"
        >
          ✏️
        </button>

        <button
          @click="$emit('delete', category)"
          class="w-7 h-7 flex items-center justify-center text-xs bg-red-50 text-red-700 rounded hover:bg-red-100 transition-colors"
          :title="$t('panel.actions.delete')"
        >
          🗑️
        </button>
      </div>
    </div>

    <!-- Children (Recursive) -->
    <div v-if="hasChildren && isExpanded" class="children-container mt-1">
      <CategoryTreeNode
        v-for="child in category.children"
        :key="child.category_id"
        :category="child"
        :level="level + 1"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @toggle-active="$emit('toggle-active', $event)"
        @create-child="$emit('create-child', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

interface Props {
  category: any
  level: number
}

const props = defineProps<Props>()

defineEmits(['edit', 'delete', 'toggle-active', 'create-child'])

// State
const isExpanded = ref(false)

// Computed
const hasChildren = computed(() => {
  return props.category.children && props.category.children.length > 0
})

// Methods
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const getLevelClass = () => {
  const classes = [
    'bg-purple-100 text-purple-700',  // Level 1
    'bg-blue-100 text-blue-700',      // Level 2
    'bg-green-100 text-green-700',    // Level 3
    'bg-yellow-100 text-yellow-700',  // Level 4
    'bg-orange-100 text-orange-700',  // Level 5
    'bg-red-100 text-red-700',        // Level 6
    'bg-pink-100 text-pink-700',      // Level 7
    'bg-indigo-100 text-indigo-700',  // Level 8
    'bg-cyan-100 text-cyan-700',      // Level 9
    'bg-teal-100 text-teal-700',      // Level 10
    'bg-lime-100 text-lime-700',      // Level 11
    'bg-amber-100 text-amber-700',    // Level 12
    'bg-emerald-100 text-emerald-700', // Level 13
    'bg-sky-100 text-sky-700',        // Level 14
    'bg-violet-100 text-violet-700',  // Level 15
    'bg-fuchsia-100 text-fuchsia-700', // Level 16
    'bg-rose-100 text-rose-700',      // Level 17
    'bg-slate-100 text-slate-700',    // Level 18
    'bg-zinc-100 text-zinc-700',      // Level 19
    'bg-stone-100 text-stone-700'     // Level 20
  ]
  return classes[props.category.level - 1] || classes[classes.length - 1]
}
</script>

<style scoped>
.category-node {
  position: relative;
}

.category-row {
  min-height: 36px;
}

.children-container {
  position: relative;
}

/* Subtle indent guide line */
.children-container::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--color-border);
  opacity: 0.3;
}
</style>
