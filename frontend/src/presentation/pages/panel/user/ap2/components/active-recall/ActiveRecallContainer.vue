<template>
  <div class="ap2-ar">
    <PhaseNavigator :current="session.currentPhase.value" />

    <div v-if="session.loading.value" class="ap2-ar-loading">
      {{ t('ap2Trainer.study.loading') }}
    </div>

    <BlurtingPhase
      v-else-if="session.currentPhase.value === 'blurt' && session.currentItem.value"
      :item="session.currentItem.value"
      :response="session.lastResponse.value"
      :submitting="session.submitting.value"
      @submit="onSubmit"
      @next="session.nextItem"
    />

    <CuedRecallPhase
      v-else-if="session.currentPhase.value === 'cued' && session.currentItem.value"
      :item="session.currentItem.value"
      :response="session.lastResponse.value"
      :submitting="session.submitting.value"
      :current-idx="session.currentIndex.value"
      :total="session.totalInPhase.value"
      :is-last="session.isLastInPhase.value"
      @submit="onSubmit"
      @next="session.nextItem"
    />

    <ApplicationPhase
      v-else-if="session.currentPhase.value === 'application' && session.currentItem.value"
      :item="session.currentItem.value"
      :response="session.lastResponse.value"
      :submitting="session.submitting.value"
      :is-last="session.isLastInPhase.value"
      @submit="onSubmit"
      @next="session.nextItem"
    />

    <div v-else-if="session.currentPhase.value === 'done'" class="ap2-ar-complete">
      <h3>{{ t('ap2Trainer.study.complete.title') }}</h3>
      <p class="ap2-ar-sub">{{ t('ap2Trainer.study.complete.subtitle') }}</p>
      <p class="ap2-ar-stats">
        {{ t('ap2Trainer.study.complete.stats', {
          earned: session.phaseScores.value.earned.toFixed(1),
          total: session.phaseScores.value.total.toFixed(1)
        }) }}
      </p>
      <div class="ap2-ar-actions">
        <RouterLink
          v-if="session.topic.value"
          :to="`/ap2-training/cheatsheet/${session.topic.value.slug}`"
          class="ap2-btn ap2-btn-primary"
        >
          {{ t('ap2Trainer.study.complete.writeCheatsheet') }}
        </RouterLink>
        <button class="ap2-btn" @click="onFinish">
          {{ t('ap2Trainer.study.complete.backToStudy') }}
        </button>
      </div>
    </div>

    <div v-if="session.error.value" class="ap2-ar-error">
      ⚠️ {{ session.error.value }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { RouterLink } from 'vue-router'
import PhaseNavigator from './PhaseNavigator.vue'
import BlurtingPhase from './BlurtingPhase.vue'
import CuedRecallPhase from './CuedRecallPhase.vue'
import ApplicationPhase from './ApplicationPhase.vue'

const { t } = useI18n()

interface Props {
  session: ReturnType<typeof import('../../composables').useStudySession>
}
const props = defineProps<Props>()
const emit = defineEmits<{ finish: [] }>()

async function onSubmit(text: string) {
  await props.session.submitAnswer(text)
}

async function onFinish() {
  await props.session.end()
  emit('finish')
}
</script>

<style scoped>
.ap2-ar { display: flex; flex-direction: column; gap: 12px; }
.ap2-ar-loading, .ap2-ar-error { padding: 24px; text-align: center; color: #94a3b8; }
.ap2-ar-error { color: #f87171; }
.ap2-ar-complete { background: var(--color-surface, #1e293b); border: 1px solid #16a34a; border-radius: 12px; padding: 32px; text-align: center; }
.ap2-ar-complete h3 { color: #4ade80; font-size: 22px; margin: 0 0 8px; }
.ap2-ar-sub { color: #94a3b8; margin: 0 0 8px; }
.ap2-ar-stats { color: #cbd5e1; font-weight: 600; margin: 0 0 16px; }
.ap2-ar-actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.ap2-btn { padding: 10px 20px; border-radius: 8px; border: 1px solid var(--color-border, #334155); background: rgba(255,255,255,0.05); color: #cbd5e1; cursor: pointer; font-size: 13px; font-weight: 600; text-decoration: none; }
.ap2-btn-primary { background: #4338ca; border-color: #4338ca; color: #fff; }
</style>
