<template>
  <div class="sc-panel" :class="{ 'sc-collapsed': !isOpen }">
    <!-- Header -->
    <button class="sc-header" @click="isOpen = !isOpen">
      <div class="sc-header-left">
        <span class="sc-toggle">{{ isOpen ? '&#9660;' : '&#9654;' }}</span>
        <span class="sc-badge">Handlungssituation</span>
        <span class="sc-title">{{ context.title }}</span>
      </div>
      <span class="sc-aufgaben" v-if="context.aufgabenNummern.length">
        Aufgabe {{ context.aufgabenNummern.join(', ') }}
      </span>
    </button>

    <!-- Inhalt -->
    <transition name="sc-slide">
      <div v-if="isOpen" class="sc-body">
        <!-- Beschreibung -->
        <div class="sc-description">
          {{ context.description }}
        </div>

        <!-- Zusätzliche Kontext-Details -->
        <div v-if="context.contextDetails" class="sc-details">
          <div class="sc-details-header">
            <span class="sc-info-icon">&#9432;</span>
            Zusatzinformationen
          </div>
          <div class="sc-details-content" v-html="formatDetails(context.contextDetails)"></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ScenarioContext } from '../types'

const props = defineProps<{
  context: ScenarioContext
  /** Automatisch aufklappen */
  autoExpand?: boolean
}>()

const isOpen = ref(props.autoExpand !== false)

/** Einfaches Formatting: Zeilenumbrüche → <br>, **fett** → <strong> */
function formatDetails(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
.sc-panel {
  border: 1px solid rgba(255, 193, 7, 0.2);
  border-radius: 10px;
  overflow: hidden;
  margin: 14px 0;
  background: rgba(255, 193, 7, 0.03);
  transition: all 0.3s ease;
}
.sc-collapsed {
  border-color: rgba(255, 193, 7, 0.1);
}

.sc-header {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(255, 193, 7, 0.06);
  border: none;
  cursor: pointer;
  transition: background 0.2s ease;
  text-align: left;
}
.sc-header:hover {
  background: rgba(255, 193, 7, 0.1);
}
.sc-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}
.sc-toggle {
  font-size: 0.7rem;
  color: #ffc107;
  width: 14px;
  text-align: center;
}
.sc-badge {
  background: rgba(255, 193, 7, 0.15);
  color: #ffc107;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
}
.sc-title {
  color: #e3f2fd;
  font-size: 0.9rem;
  font-weight: 600;
}
.sc-aufgaben {
  font-size: 0.78rem;
  color: #78909c;
  white-space: nowrap;
}

/* Slide */
.sc-slide-enter-active, .sc-slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.sc-slide-enter-from, .sc-slide-leave-to {
  max-height: 0; opacity: 0;
}
.sc-slide-enter-to, .sc-slide-leave-from {
  max-height: 1000px; opacity: 1;
}

.sc-body {
  padding: 16px;
  border-top: 1px solid rgba(255, 193, 7, 0.08);
}

.sc-description {
  font-size: 0.88rem;
  color: #b0bec5;
  line-height: 1.65;
  white-space: pre-line;
}

.sc-details {
  margin-top: 14px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  border-left: 3px solid rgba(255, 193, 7, 0.3);
}
.sc-details-header {
  font-size: 0.82rem;
  font-weight: 600;
  color: #ffc107;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.sc-info-icon {
  font-size: 1rem;
}
.sc-details-content {
  font-size: 0.84rem;
  color: #90a4ae;
  line-height: 1.55;
}
.sc-details-content :deep(strong) {
  color: #e0e0e0;
  font-weight: 600;
}
</style>
