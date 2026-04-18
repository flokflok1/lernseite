<template>
  <div class="ap2-phase">
    <header class="ap2-phase-header">
      <h3>{{ t('ap2Trainer.study.blurt.title') }}</h3>
      <p class="ap2-phase-instr">{{ t('ap2Trainer.study.blurt.instruction') }}</p>
    </header>

    <div v-if="item" class="ap2-phase-prompt">
      <strong>{{ t('ap2Trainer.study.blurt.promptLabel') }}:</strong> {{ item.prompt }}
    </div>

    <textarea
      v-model="answer"
      class="ap2-phase-textarea"
      :placeholder="t('ap2Trainer.study.blurt.answerPlaceholder')"
      :disabled="submitting || !!response"
      rows="14"
    />

    <div v-if="!response" class="ap2-phase-actions">
      <button
        class="ap2-btn ap2-btn-primary"
        :disabled="submitting || answer.trim().length < 5"
        @click="$emit('submit', answer)"
      >
        {{ submitting ? t('ap2Trainer.study.blurt.submitting') : t('ap2Trainer.study.blurt.submit') }}
      </button>
    </div>

    <AttemptFeedback v-if="response" :response="response" />

    <div v-if="response" class="ap2-phase-actions">
      <button class="ap2-btn ap2-btn-primary" @click="onNext">
        {{ t('ap2Trainer.study.feedback.next') }}
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
.ap2-phase-prompt { padding: 12px; background: rgba(99, 102, 241, 0.08); border-left: 3px solid #4338ca; border-radius: 4px; margin-bottom: 12px; color: #e2e8f0; font-size: 13px; }
.ap2-phase-textarea { width: 100%; padding: 12px; background: rgba(0, 0, 0, 0.2); border: 1px solid var(--color-border, #334155); border-radius: 8px; color: #fff; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 13px; line-height: 1.5; resize: vertical; }
.ap2-phase-textarea:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2); }
.ap2-phase-textarea:disabled { opacity: 0.7; }
.ap2-phase-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; }
.ap2-btn { padding: 10px 20px; border-radius: 8px; border: 1px solid; cursor: pointer; font-size: 13px; font-weight: 600; transition: all .15s; }
.ap2-btn-primary { background: #4338ca; border-color: #4338ca; color: #fff; }
.ap2-btn-primary:hover:not(:disabled) { background: #3730a3; }
.ap2-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
