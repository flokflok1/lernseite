<!--
  FeatureGroup - Collapsible Feature Group
  Sub-component of SystemFeaturesTab
-->

<template>
  <div class="feature-group">
    <div class="group-header" @click="$emit('toggle')">
      <div class="group-icon">{{ icon }}</div>
      <div class="group-info">
        <h3>{{ title }}</h3>
        <p>{{ description }}</p>
      </div>
      <div class="group-toggle">
        <input
          type="checkbox"
          :checked="groupEnabled"
          @click.stop="$emit('toggleAll')"
          class="toggle-switch"
        />
      </div>
      <svg
        class="expand-icon"
        :class="{ rotated: expanded }"
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </div>

    <div v-if="expanded" class="group-features">
      <div v-if="requirementNotice" class="requirement-notice">
        ⚠️ {{ requirementNotice }}
      </div>
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  icon: string
  title: string
  description: string
  expanded: boolean
  groupEnabled: boolean
  requirementNotice?: string
}>()

defineEmits<{
  (e: 'toggle'): void
  (e: 'toggleAll'): void
}>()
</script>

<style scoped>
.feature-group {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}

.group-header:hover { background: var(--color-surface-secondary); }

.group-icon {
  width: 48px;
  height: 48px;
  background: var(--color-primary-subtle);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.group-info { flex: 1; }
.group-info h3 { margin: 0; font-size: 1rem; color: var(--color-text-primary); }
.group-info p { margin: 0.25rem 0 0; font-size: 0.8125rem; color: var(--color-text-secondary); }

.group-toggle { padding: 0 0.5rem; }

.toggle-switch {
  width: 44px;
  height: 24px;
  cursor: pointer;
}

.expand-icon {
  width: 20px;
  height: 20px;
  color: var(--color-text-tertiary);
  transition: transform 0.2s;
}

.expand-icon.rotated { transform: rotate(180deg); }

.group-features {
  border-top: 1px solid var(--color-border);
  padding: 0.5rem;
}

.requirement-notice {
  padding: 0.75rem 1rem;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  color: #f59e0b;
  margin-bottom: 0.5rem;
}
</style>
