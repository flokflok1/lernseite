<template>
  <div class="ap2-phase">
    <header class="ap2-phase-header">
      <h3>{{ t('ap2Trainer.study.application.title') }}</h3>
      <p class="ap2-phase-instr">{{ t('ap2Trainer.study.application.instruction') }}</p>
    </header>

    <div v-if="item" class="ap2-app-task">
      <div class="ap2-app-meta">
        <span class="ap2-app-source">{{ item.source_exam || '—' }}</span>
        <span class="ap2-app-points">{{ item.points }} P</span>
      </div>
      <div class="ap2-app-prompt">{{ item.prompt }}</div>
      <div v-if="item.anlage_id" class="ap2-app-anlage-hint">
        📎 Diese Aufgabe hat eine Anlage (kommt in Phase 4)
      </div>
      <CalculatorHintPanel :hint="item.calculator_hint ?? null" />
    </div>

    <textarea
      v-model="answer"
      class="ap2-phase-textarea"
      :placeholder="t('ap2Trainer.study.application.answerPlaceholder')"
      :disabled="submitting || !!response"
      rows="14"
    />

    <div v-if="!response" class="ap2-phase-actions">
      <button
        class="ap2-btn ap2-btn-primary"
        :disabled="submitting || answer.trim().length < 10"
        @click="$emit('submit', answer)"
      >
        {{ submitting ? t('ap2Trainer.study.blurt.submitting') : t('ap2Trainer.study.application.submit') }}
      </button>
    </div>

    <AttemptFeedback v-if="response" :response="response" />

    <div v-if="response" class="ap2-phase-actions">
      <button class="ap2-btn ap2-btn-primary" @click="onNext">
        {{ isLast ? t('ap2Trainer.study.application.finish') : t('ap2Trainer.study.application.next') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AttemptFeedback from './AttemptFeedback.vue'
import CalculatorHintPanel from './CalculatorHintPanel.vue'
import type { Ap2Item, Ap2SubmitResponse } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  item: Ap2Item | null
  response: Ap2SubmitResponse | null
  submitting: boolean
  isLast: boolean
}
const props = defineProps<Props>()
const emit = defineEmits<{ submit: [text: string]; next: [] }>()
const { t } = useI18n()

const answer = ref('')
watch(() => props.item?.item_id, () => { answer.value = '' })

function onNext() { answer.value = ''; emit('next') }
</script>

<style scoped>
.ap2-phase { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 12px; padding: 20px; }
.ap2-phase-header { margin-bottom: 16px; }
.ap2-phase-header h3 { margin: 0 0 6px; color: var(--color-text-primary, #fff); font-size: 16px; }
.ap2-phase-instr { font-size: 12px; color: #94a3b8; margin: 0; }
.ap2-app-task { background: rgba(0, 0, 0, 0.2); border: 1px solid var(--color-border, #334155); border-radius: 10px; padding: 16px; margin-bottom: 12px; }
.ap2-app-meta { display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 600; }
.ap2-app-source { font-family: ui-monospace, monospace; }
.ap2-app-points { background: #4338ca; color: #fff; padding: 2px 8px; border-radius: 4px; }
.ap2-app-prompt { color: #fff; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
.ap2-app-anlage-hint { margin-top: 12px; padding: 8px; background: rgba(245, 158, 11, 0.08); border-left: 3px solid #f59e0b; border-radius: 4px; font-size: 12px; color: #fbbf24; }
.ap2-phase-textarea { width: 100%; padding: 12px; background: rgba(0, 0, 0, 0.2); border: 1px solid var(--color-border, #334155); border-radius: 8px; color: #fff; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 13px; line-height: 1.5; resize: vertical; }
.ap2-phase-textarea:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2); }
.ap2-phase-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; }
.ap2-btn { padding: 10px 20px; border-radius: 8px; border: 1px solid; cursor: pointer; font-size: 13px; font-weight: 600; }
.ap2-btn-primary { background: #4338ca; border-color: #4338ca; color: #fff; }
.ap2-btn-primary:hover:not(:disabled) { background: #3730a3; }
.ap2-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
