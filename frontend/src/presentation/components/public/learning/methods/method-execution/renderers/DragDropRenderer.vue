<template>
  <div class="renderer">
    <p class="instruction">{{ t('lesson.methodExecution.renderer.dragDrop.assignItems') }}</p>
    <div class="items-grid">
      <div v-for="(item, i) in items" :key="i" class="item-row" :class="{ 'item--correct': checked && isCorrect(i), 'item--wrong': checked && !isCorrect(i) }">
        <span class="item-label">{{ item.term }}</span>
        <select v-model="selections[i]" class="category-select" :disabled="checked">
          <option value="">{{ t('lesson.methodExecution.renderer.dragDrop.selectCategory') }}</option>
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
        <span v-if="checked" class="item-status">{{ isCorrect(i) ? '✓' : '✗' }}</span>
      </div>
    </div>
    <div class="actions">
      <button v-if="!checked" class="check-btn" :disabled="selections.some(s => !s)" @click="checked = true">{{ t('lesson.methodExecution.renderer.common.check') }}</button>
      <button v-else class="reset-btn" @click="reset">{{ t('lesson.methodExecution.renderer.common.reset') }}</button>
    </div>
    <div v-if="checked" class="score">{{ t('lesson.methodExecution.renderer.dragDrop.correctCount', { correct: correctCount, total: items.length }) }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DragDropData } from './types'

const { t } = useI18n()
const props = defineProps<{ data: DragDropData | null; solution: null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const checked = ref(false)
const categories = computed(() => props.data?.categories || [])
const items = computed(() => props.data?.items || [])
const selections = ref<string[]>(items.value.map(() => ''))

watch(() => props.data, () => reset(), { deep: true })

const correctCount = computed(() =>
  items.value.filter((item: any, i: number) => selections.value[i] === item.correctCategory).length
)

function isCorrect(i: number): boolean {
  return selections.value[i] === items.value[i]?.correctCategory
}

watch(checked, (val) => {
  if (val) emit('complete', correctCount.value, items.value.length)
})

function reset() {
  checked.value = false
  selections.value = items.value.map(() => '')
}
</script>

<style scoped>
.instruction {
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
  color: var(--color-text-secondary);
}

.items-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 0.625rem;
  transition: all 0.25s ease;
}

.item--correct {
  border-color: rgba(16, 185, 129, 0.35);
  background: rgba(16, 185, 129, 0.06);
}

.item--wrong {
  border-color: rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.05);
}

.item-label {
  font-size: 0.875rem;
  font-weight: 500;
  flex: 1;
  min-width: 0;
  color: var(--color-text-primary);
}

.category-select {
  padding: 0.375rem 0.75rem;
  font-size: 0.8125rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-primary);
  min-width: 140px;
  transition: border-color 0.15s;
  cursor: pointer;
}

.category-select:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1);
}

.category-select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.item-status {
  font-weight: 700;
  font-size: 0.875rem;
  width: 1.5rem;
  text-align: center;
}

.item--correct .item-status {
  color: var(--color-success);
}

.item--wrong .item-status {
  color: var(--color-error);
}

.actions {
  display: flex;
  gap: 0.625rem;
  margin-bottom: 0.75rem;
}

.check-btn {
  padding: 0.5rem 1.5rem;
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  transition: all 0.15s;
}

.check-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
  transform: translateY(-1px);
}

.check-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.reset-btn {
  padding: 0.5rem 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.score {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-accent-light);
}
</style>
