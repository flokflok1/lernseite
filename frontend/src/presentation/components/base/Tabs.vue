<template>
  <div class="tabs">
    <div class="tabs-header">
      <button
        v-for="(tab, index) in tabs"
        :key="index"
        :class="['tab', { 'tab-active': activeTab === index }]"
        @click="activeTab = index"
      >
        {{ tab.label }}
      </button>
    </div>
    <div class="tabs-content">
      <slot :name="`tab-${activeTab}`"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Tab {
  label: string
}

const props = defineProps<{
  tabs: Tab[]
  defaultTab?: number
}>()

const activeTab = ref(props.defaultTab || 0)
</script>

<style scoped>
.tabs {
  width: 100%;
}

.tabs-header {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
}

.tab {
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.tab:hover {
  background-color: #f9fafb;
}

.tab-active {
  border-bottom-color: #3b82f6;
  color: #3b82f6;
}

.tabs-content {
  padding: 1rem 0;
}
</style>
