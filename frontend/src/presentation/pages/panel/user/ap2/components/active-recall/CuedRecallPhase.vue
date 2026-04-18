<template>
  <div class="ap2-phase">
    <header class="ap2-phase-header">
      <h3>{{ t('ap2Trainer.study.cued.title', { current: currentIdx + 1, total: total }) }}</h3>
      <p class="ap2-phase-instr">{{ t('ap2Trainer.study.cued.instruction') }}</p>
    </header>

    <div v-if="item" class="ap2-card-flash">
      <div class="ap2-card-q">{{ item.prompt }}</div>
      <div class="ap2-card-meta">{{ item.points }} P · {{ item.estimated_time_sec }} sec</div>
    </div>

    <textarea
      v-model="answer"
      class="ap2-phase-textarea"
      :placeholder="t('ap2Trainer.study.cued.answerPlaceholder')"
      :disabled="submitting || !!response"
      rows="6"
    />

    <div v-if="!response" class="ap2-phase-actions">
      <button
        class="ap2-btn ap2-btn-primary"
        :disabled="submitting || answer.trim().length < 2"
        @click="$emit('submit', answer)"
      >
        {{ submitting ? t('ap2Trainer.study.blurt.submitting') : t('ap2Trainer.study.cued.submit') }}
      </button>
    </div>

    <AttemptFeedback v-if="response" :response="response" />

    <div v-if="response" class="ap2-phase-actions">
      <button class="ap2-btn ap2-btn-primary" @click="onNext">
        {{ isLast ? t('ap2Trainer.study.cued.finish') : t('ap2Trainer.study.cued.next') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AttemptFeedback from './AttemptFeedback.vue'
import type { Ap2Item, Ap2SubmitResponse } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  item: Ap2Item | null
  response: Ap2SubmitResponse | null
  submitting: boolean
  currentIdx: number
  total: number
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
.ap2-card-flash { padding: 24px; background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.1) 100%); border: 1px solid #4338ca; border-radius: 10px; margin-bottom: 12px; min-height: 100px; display: flex; flex-direction: column; justify-content: center; }
.ap2-card-q { color: #fff; font-size: 16px; line-height: 1.4; font-weight: 500; }
.ap2-card-meta { font-size: 11px; color: #94a3b8; margin-top: 12px; text-align: right; }
.ap2-phase-textarea { width: 100%; padding: 12px; background: rgba(0, 0, 0, 0.2); border: 1px solid var(--color-border, #334155); border-radius: 8px; color: #fff; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 13px; line-height: 1.5; resize: vertical; }
.ap2-phase-textarea:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2); }
.ap2-phase-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; }
.ap2-btn { padding: 10px 20px; border-radius: 8px; border: 1px solid; cursor: pointer; font-size: 13px; font-weight: 600; }
.ap2-btn-primary { background: #4338ca; border-color: #4338ca; color: #fff; }
.ap2-btn-primary:hover:not(:disabled) { background: #3730a3; }
.ap2-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
