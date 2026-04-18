<template>
  <!-- Modus 1: Topic-Detail (3-Phasen-Flow) -->
  <ActiveRecallContainer
    v-if="topicSlug && session.topic.value"
    :session="session"
    @finish="onFinishSession"
  />

  <!-- Modus 2: Topic-Liste -->
  <div v-else class="ap2-study-list">
    <header class="ap2-study-header">
      <div>
        <h2>{{ t('ap2Trainer.study.title') }}</h2>
        <p class="ap2-study-sub">{{ t('ap2Trainer.study.subtitle') }}</p>
      </div>
      <div class="ap2-filter">
        <button
          v-for="b in bereichFilters"
          :key="b.key"
          class="ap2-filter-btn"
          :class="{ 'ap2-filter-active': filter === b.key }"
          @click="filter = b.key"
        >
          {{ b.label }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="ap2-study-loading">{{ t('ap2Trainer.study.loading') }}</div>

    <div v-else class="ap2-topic-grid">
      <RouterLink
        v-for="topic in filteredTopics"
        :key="topic.slug"
        :to="`/ap2-training/study/${topic.slug}`"
        class="ap2-topic-card"
        :class="cardClass(topic)"
      >
        <div class="ap2-topic-header">
          <span class="ap2-topic-prio" :class="`ap2-prio-${topic.priority}`">
            {{ priorityIcon(topic.priority) }}
          </span>
          <span class="ap2-topic-bereich">{{ topic.bereich }}</span>
        </div>
        <div class="ap2-topic-name">{{ topic.name_de }}</div>
        <div class="ap2-topic-meta">
          <span>{{ t('ap2Trainer.study.topicCard.expectedPts', { n: topic.expected_points }) }}</span>
          <span>{{ t('ap2Trainer.study.topicCard.examCount', { n: topic.exam_count }) }}</span>
        </div>
        <div class="ap2-topic-mastery">
          <div v-if="topicMastery[topic.slug]" class="ap2-mastery-bar">
            <div
              class="ap2-mastery-fill"
              :style="{ width: topicMastery[topic.slug].mastery_score + '%' }"
              :class="masteryClass(topicMastery[topic.slug].mastery_score)"
            />
          </div>
          <div class="ap2-mastery-label">
            <template v-if="topicMastery[topic.slug]">
              {{ t('ap2Trainer.study.topicCard.mastery', { n: Math.round(topicMastery[topic.slug].mastery_score) }) }}
            </template>
            <template v-else>
              {{ t('ap2Trainer.study.topicCard.noMastery') }}
            </template>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useStudySession, useAp2Stats } from '../composables'
import {
  listAp2Topics,
  type Ap2Topic,
} from '@/infrastructure/api/clients/panel/user/exams'
import { ActiveRecallContainer } from '../components/active-recall'

const { t } = useI18n()
const router = useRouter()

interface Props { topicSlug?: string }
const props = defineProps<Props>()

const session = useStudySession()
const stats = useAp2Stats(false)   // manuell laden

const topics = ref<Ap2Topic[]>([])
const loading = ref(false)
const filter = ref<'all' | 'PB2' | 'PB3' | 'WISO'>('all')

const bereichFilters = computed(() => [
  { key: 'all' as const, label: t('ap2Trainer.study.filterAll') },
  { key: 'PB2' as const, label: 'PB2' },
  { key: 'PB3' as const, label: 'PB3' },
  { key: 'WISO' as const, label: 'WISO' },
])

const topicMastery = computed(() => {
  const m: Record<string, { mastery_score: number; attempts_count: number }> = {}
  for (const ts of stats.topicStats.value) {
    m[ts.topic_slug] = { mastery_score: ts.mastery_score, attempts_count: ts.attempts_count }
  }
  return m
})

const filteredTopics = computed(() => {
  if (filter.value === 'all') return topics.value
  // WISO ist eine separate Prüfung (eigener Tag) — 'both' bedeutet PB2+PB3,
  // nicht WISO. Deshalb WISO-Tab zeigt NUR WISO-Topics.
  if (filter.value === 'WISO') return topics.value.filter((t) => t.bereich === 'WISO')
  return topics.value.filter(
    (t) => t.bereich === filter.value || t.bereich === 'both'
  )
})

async function loadTopics() {
  loading.value = true
  try {
    const res = await listAp2Topics()
    topics.value = res.topics
    await stats.refresh()
  } catch (e) {
    console.warn('[AP2] load topics failed:', e)
  } finally {
    loading.value = false
  }
}

function priorityIcon(p: string) {
  return ({ 'sehr-hoch': '🔴', hoch: '🟠', mittel: '🟡', niedrig: '🟢' } as Record<string, string>)[p] ?? '⚪'
}

function cardClass(topic: Ap2Topic) {
  const m = topicMastery.value[topic.slug]
  if (!m) return ''
  if (m.mastery_score >= 80) return 'ap2-card-mastered'
  if (m.mastery_score >= 50) return 'ap2-card-passing'
  if (m.attempts_count >= 3) return 'ap2-card-weak'
  return ''
}

function masteryClass(score: number) {
  if (score >= 65) return 'ap2-mf-good'
  if (score >= 50) return 'ap2-mf-ok'
  return 'ap2-mf-bad'
}

async function onFinishSession() {
  await session.end()
  router.push('/ap2-training/study')
}

watch(() => props.topicSlug, async (slug) => {
  if (slug) {
    await session.start(slug)
  }
}, { immediate: true })

onMounted(() => {
  if (!props.topicSlug) loadTopics()
})

onBeforeUnmount(async () => {
  if (session.sessionId.value) await session.end()
})
</script>

<style scoped>
.ap2-study-list { display: flex; flex-direction: column; gap: 16px; }
.ap2-study-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; }
.ap2-study-header h2 { margin: 0 0 4px; color: var(--color-text-primary, #fff); font-size: 22px; }
.ap2-study-sub { color: #94a3b8; margin: 0; font-size: 13px; }
.ap2-filter { display: inline-flex; gap: 4px; background: var(--color-surface, #1e293b); padding: 4px; border-radius: 8px; border: 1px solid var(--color-border, #334155); }
.ap2-filter-btn { padding: 6px 12px; border: 0; background: transparent; color: #cbd5e1; cursor: pointer; font-size: 12px; font-weight: 600; border-radius: 6px; }
.ap2-filter-btn:hover { background: rgba(255,255,255,0.05); }
.ap2-filter-active { background: #4338ca !important; color: #fff !important; }
.ap2-study-loading { padding: 48px; text-align: center; color: #94a3b8; }

.ap2-topic-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
.ap2-topic-card {
  display: flex; flex-direction: column; gap: 8px;
  padding: 14px;
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 12px;
  text-decoration: none;
  color: inherit;
  transition: all .15s;
}
.ap2-topic-card:hover { transform: translateY(-1px); border-color: #4338ca; }
.ap2-card-mastered { border-color: #16a34a; }
.ap2-card-passing  { border-color: #f59e0b; }
.ap2-card-weak     { border-color: #dc2626; }

.ap2-topic-header { display: flex; justify-content: space-between; align-items: center; }
.ap2-topic-prio { font-size: 14px; }
.ap2-topic-bereich { font-size: 10px; font-weight: 700; color: #94a3b8; padding: 2px 6px; background: rgba(255,255,255,0.05); border-radius: 4px; }
.ap2-topic-name { color: #fff; font-size: 14px; font-weight: 600; line-height: 1.3; min-height: 36px; }
.ap2-topic-meta { display: flex; justify-content: space-between; font-size: 10px; color: #64748b; }

.ap2-topic-mastery { margin-top: 4px; }
.ap2-mastery-bar { height: 4px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; margin-bottom: 4px; }
.ap2-mastery-fill { height: 100%; border-radius: 2px; transition: width .3s; }
.ap2-mf-good { background: #22c55e; }
.ap2-mf-ok   { background: #f59e0b; }
.ap2-mf-bad  { background: #ef4444; }
.ap2-mastery-label { font-size: 10px; color: #94a3b8; text-align: right; }
</style>
