/**
 * EditorSwitcher.vue
 *
 * Component to toggle between Manual and AI editor modes.
 */

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

type EditorMode = 'manual' | 'ai'

interface Props {
  currentMode: EditorMode
}

interface Emits {
  (e: 'switch', mode: EditorMode): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

const modes = computed(() => [
  { id: 'manual', label: t('courses.editor.manualMode'), icon: '✏️' },
  { id: 'ai', label: t('courses.editor.aiMode'), icon: '🤖' }
])

const handleSwitch = (mode: EditorMode) => {
  if (mode !== props.currentMode) {
    emit('switch', mode)
  }
}
</script>

<template>
  <div class="editor-switcher">
    <button
      v-for="mode in modes"
      :key="mode.id"
      :class="['switcher-btn', { active: currentMode === mode.id }]"
      @click="handleSwitch(mode.id as EditorMode)"
      :title="mode.label"
    >
      <span class="icon">{{ mode.icon }}</span>
      <span class="label">{{ mode.label }}</span>
    </button>
  </div>
</template>

<style scoped>
.editor-switcher {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #f0f0f0;
  border-radius: 8px;
}

.switcher-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 2px solid transparent;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.switcher-btn:hover {
  background: #e8e8e8;
}

.switcher-btn.active {
  background: #2196f3;
  color: white;
  border-color: #1976d2;
}

.icon {
  font-size: 18px;
}

.label {
  font-size: 14px;
}
</style>
