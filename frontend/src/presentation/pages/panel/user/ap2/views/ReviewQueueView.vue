<template>
  <div class="ap2-review">
    <header class="ap2-review-header">
      <div>
        <h2>{{ t('ap2Trainer.review.title') }}</h2>
        <p class="ap2-review-sub">{{ t('ap2Trainer.review.subtitle') }}</p>
      </div>
      <div v-if="data" class="ap2-review-count">
        {{ t('ap2Trainer.review.totalDue', { n: data.count_total_due }) }}
      </div>
    </header>

    <div v-if="loading" class="ap2-review-loading">
      {{ t('ap2Trainer.review.loading') }}
    </div>

    <div v-else-if="data && data.items.length === 0" class="ap2-review-empty">
      <h3>{{ t('ap2Trainer.review.empty.title') }}</h3>
      <p>{{ t('ap2Trainer.review.empty.subtitle') }}</p>
      <RouterLink to="/ap2-training/study" class="ap2-btn ap2-btn-primary">
        {{ t('ap2Trainer.dashboard.empty.ctaStudy') }}
      </RouterLink>
    </div>

    <ul v-else class="ap2-review-list">
      <li v-for="item in data?.items ?? []" :key="item.item_id" class="ap2-review-item">
        <div class="ap2-rev-info">
          <div class="ap2-rev-topic">
            <span class="ap2-rev-bereich">{{ item.topic_bereich }}</span>
            {{ item.topic_name }}
          </div>
          <div class="ap2-rev-prompt">{{ item.prompt }}</div>
          <div class="ap2-rev-meta">
            <span class="ap2-rev-type">{{ phaseLabel(item.item_type) }}</span>
            <span>{{ t('ap2Trainer.review.card.points', { n: item.points }) }}</span>
            <span>{{ t('ap2Trainer.review.card.estimated', { n: item.estimated_time_sec }) }}</span>
            <span>{{ t('ap2Trainer.review.card.rep', { n: item.repetitions }) }}</span>
          </div>
        </div>
        <RouterLink
          :to="`/ap2-training/study/${slugFromTopicId(item.topic_id)}`"
          class="ap2-btn ap2-btn-primary"
        >
          {{ t('ap2Trainer.review.startBtn') }}
        </RouterLink>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  getAp2ReviewQueue, listAp2Topics,
  type Ap2ReviewQueueItem,
} from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

const data = ref<{ count_total_due: number; items: Ap2ReviewQueueItem[] } | null>(null)
const topicSlugMap = ref<Record<string, string>>({})
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const [q, topicsRes] = await Promise.all([
      getAp2ReviewQueue(50),
      listAp2Topics(),
    ])
    data.value = { count_total_due: q.count_total_due, items: q.items }
    topicSlugMap.value = Object.fromEntries(
      topicsRes.topics.map((tp) => [tp.topic_id, tp.slug])
    )
  } catch (e) {
    console.warn('[AP2] review queue load failed:', e)
  } finally {
    loading.value = false
  }
}

function phaseLabel(type: string) {
  const map: Record<string, string> = {
    blurt: t('ap2Trainer.study.phases.blurt'),
    cued: t('ap2Trainer.study.phases.cued'),
    application: t('ap2Trainer.study.phases.application'),
  }
  return map[type] ?? type
}

function slugFromTopicId(topicId: string): string {
  return topicSlugMap.value[topicId] ?? ''
}

onMounted(load)
</script>

<style scoped>
.ap2-review { display: flex; flex-direction: column; gap: 12px; }
.ap2-review-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.ap2-review-header h2 { margin: 0 0 4px; color: var(--color-text-primary, #fff); font-size: 22px; }
.ap2-review-sub { color: #94a3b8; margin: 0; font-size: 13px; }
.ap2-review-count { padding: 6px 12px; background: rgba(99, 102, 241, 0.15); border: 1px solid #4338ca; border-radius: 999px; color: #a5b4fc; font-size: 12px; font-weight: 700; }
.ap2-review-loading { padding: 48px; text-align: center; color: #94a3b8; }
.ap2-review-empty { text-align: center; padding: 48px 24px; background: var(--color-surface, #1e293b); border: 1px solid #16a34a; border-radius: 12px; }
.ap2-review-empty h3 { color: #4ade80; margin: 0 0 8px; }
.ap2-review-empty p { color: #94a3b8; margin: 0 0 16px; }
.ap2-review-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.ap2-review-item { display: grid; grid-template-columns: 1fr auto; gap: 12px; align-items: center; padding: 12px 16px; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 10px; }
.ap2-rev-topic { font-size: 11px; color: #cbd5e1; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
.ap2-rev-bereich { display: inline-block; padding: 2px 6px; background: #4338ca; color: #fff; border-radius: 4px; font-size: 9px; margin-right: 6px; }
.ap2-rev-prompt { color: #fff; font-size: 13px; line-height: 1.4; margin-bottom: 6px; }
.ap2-rev-meta { display: flex; gap: 12px; font-size: 11px; color: #94a3b8; }
.ap2-rev-type { color: #a5b4fc; font-weight: 600; }
.ap2-btn { padding: 8px 16px; border-radius: 8px; border: 1px solid; cursor: pointer; font-size: 12px; font-weight: 600; text-decoration: none; }
.ap2-btn-primary { background: #4338ca; border-color: #4338ca; color: #fff; }
.ap2-btn-primary:hover { background: #3730a3; }
</style>
