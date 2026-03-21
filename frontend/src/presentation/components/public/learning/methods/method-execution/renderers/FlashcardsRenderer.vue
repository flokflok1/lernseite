<template>
  <div class="renderer">
    <div class="card-counter">{{ t('lesson.methodExecution.renderer.flashcards.cardOf', { current: current + 1, total: cards.length }) }}</div>
    <div class="flashcard" :class="{ 'flashcard--flipped': flipped }" @click="flipped = !flipped">
      <div class="flashcard-inner">
        <div class="flashcard-face flashcard-front">
          <span class="face-label">{{ t('lesson.methodExecution.renderer.flashcards.questionLabel') }}</span>
          <p>{{ currentCard?.front }}</p>
          <span class="flip-hint">{{ t('lesson.methodExecution.renderer.flashcards.flipHint') }}</span>
        </div>
        <div class="flashcard-face flashcard-back">
          <span class="face-label face-label--answer">{{ t('lesson.methodExecution.renderer.flashcards.answerLabel') }}</span>
          <p>{{ currentCard?.back }}</p>
        </div>
      </div>
    </div>
    <div class="card-nav">
      <button :disabled="current === 0" class="nav-btn" @click="prev">&larr;</button>
      <div class="card-dots">
        <span v-for="(_, i) in cards" :key="i" class="dot" :class="{ 'dot--active': i === current, 'dot--known': known.has(i) }" @click="goTo(i)" />
      </div>
      <button :disabled="current >= cards.length - 1" class="nav-btn" @click="next">&rarr;</button>
    </div>
    <div class="card-actions">
      <button class="action-btn action-btn--skip" @click="next">{{ t('lesson.methodExecution.renderer.flashcards.practiceAgain') }}</button>
      <button class="action-btn action-btn--know" @click="markKnown">{{ t('lesson.methodExecution.renderer.flashcards.known') }} ✓</button>
    </div>
    <div class="progress-info">{{ t('lesson.methodExecution.renderer.flashcards.knownCount', { known: known.size, total: cards.length }) }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FlashcardsData } from './types'

const { t } = useI18n()
const props = defineProps<{ data: (FlashcardsData & { content_html?: string; raw_text?: string }) | null; solution: null }>()
const emit = defineEmits<{ complete: [score: number, maxScore: number] }>()
const current = ref(0)
const flipped = ref(false)
const known = ref(new Set<number>())
const cards = computed(() => {
  if (props.data?.cards?.length) return props.data.cards
  // Fallback: extract Q&A from content_html or raw_text headings
  const fallbackText = props.data?.content_html || props.data?.raw_text
  if (fallbackText) {
    const sections = fallbackText.split(/\n##\s+/)
    const extracted: { front: string; back: string }[] = []
    for (const sec of sections.slice(1)) {
      const lines = sec.trim().split('\n')
      const heading = lines[0]?.trim()
      const body = lines.slice(1).join('\n').trim().split('\n\n')[0]?.trim()
      if (heading && body) extracted.push({ front: heading, back: body.substring(0, 300) })
    }
    if (extracted.length) return extracted
  }
  return []
})
const currentCard = computed(() => cards.value[current.value])

watch(() => props.data, () => {
  current.value = 0
  flipped.value = false
  known.value = new Set()
}, { deep: true })

function prev() { flipped.value = false; current.value = Math.max(0, current.value - 1) }
function next() { flipped.value = false; current.value = Math.min(cards.value.length - 1, current.value + 1) }
function goTo(i: number) { flipped.value = false; current.value = i }
function markKnown() {
  known.value.add(current.value)
  known.value = new Set(known.value)
  // Emit when all cards are known
  if (known.value.size === cards.value.length) {
    emit('complete', known.value.size, cards.value.length)
  }
  // Find next un-known card (wrap around if needed)
  if (current.value < cards.value.length - 1) {
    next()
  } else {
    const nextUnknown = cards.value.findIndex((_: any, i: number) => !known.value.has(i))
    if (nextUnknown !== -1) goTo(nextUnknown)
  }
}

function handleFlashcardKeydown(e: KeyboardEvent): void {
  const tag = (e.target as HTMLElement)?.tagName
  if (tag === 'INPUT' || tag === 'TEXTAREA') return

  switch (e.key) {
    case ' ':
      e.preventDefault()
      flipped.value = !flipped.value
      break
    case 'ArrowLeft':
      prev()
      break
    case 'ArrowRight':
      next()
      break
    case 'Enter':
      if (flipped.value) markKnown()
      break
  }
}

onMounted(() => window.addEventListener('keydown', handleFlashcardKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleFlashcardKeydown))
</script>

<style scoped>
.card-counter {
  text-align: center;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.875rem;
}

.flashcard {
  perspective: 1000px;
  cursor: pointer;
  margin-bottom: 1.25rem;
  height: 240px;
}

.flashcard-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
}

.flashcard--flipped .flashcard-inner {
  transform: rotateY(180deg);
}

.flashcard-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border-radius: 0.875rem;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  border: 1px solid var(--color-border, #e5e7eb);
}

.flashcard-front {
  background: var(--color-surface-secondary, #f9fafb);
}

:root.dark .flashcard-front {
  background: linear-gradient(145deg, rgba(255,255,255,0.035), rgba(255,255,255,0.015));
  border-color: rgba(255,255,255,0.08);
}

.flashcard-back {
  background: rgba(99,102,241,0.06);
  border-color: rgba(99,102,241,0.2);
  transform: rotateY(180deg);
}

:root.dark .flashcard-back {
  background: linear-gradient(145deg, rgba(99,102,241,0.1), rgba(139,92,246,0.06));
  border-color: rgba(99,102,241,0.2);
}

.face-label {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--color-text-secondary);
  margin-bottom: 0.875rem;
  opacity: 0.7;
}

.face-label--answer {
  color: var(--color-accent-light);
  opacity: 1;
}

.flashcard-face p {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.6;
  max-width: 500px;
}

:root.dark .flashcard-face p {
  color: var(--color-text-primary);
}

.flip-hint {
  font-size: 0.6875rem;
  color: var(--color-text-secondary);
  margin-top: auto;
  opacity: 0.4;
}

.card-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.nav-btn {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(99, 102, 241, 0.1);
  border-color: rgba(99, 102, 241, 0.25);
  color: var(--color-accent-light);
}

.nav-btn:disabled {
  opacity: 0.2;
  cursor: not-allowed;
}

.card-dots {
  display: flex;
  gap: 0.375rem;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.2);
}

.dot--active {
  background: var(--color-accent);
  transform: scale(1.3);
  box-shadow: 0 0 6px rgba(99, 102, 241, 0.4);
}

.dot--known {
  background: var(--color-success);
}

.card-actions {
  display: flex;
  gap: 0.625rem;
  justify-content: center;
  margin-bottom: 0.75rem;
}

.action-btn {
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.15s;
}

.action-btn--skip {
  background: rgba(255, 255, 255, 0.04);
  color: var(--color-text-secondary);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.action-btn--skip:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.12);
}

.action-btn--know {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
}

.action-btn--know:hover {
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  transform: translateY(-1px);
}

.progress-info {
  text-align: center;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  opacity: 0.7;
}
</style>
