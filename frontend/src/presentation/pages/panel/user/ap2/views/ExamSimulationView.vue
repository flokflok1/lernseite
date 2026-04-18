<template>
  <div class="ap2-sim">
    <!-- Setup-Modus -->
    <template v-if="mode === 'setup'">
      <header class="ap2-sim-header">
        <div>
          <h2>{{ t('ap2Trainer.exam.title') }}</h2>
          <p class="ap2-sim-sub">{{ t('ap2Trainer.exam.subtitle') }}</p>
        </div>
      </header>

      <div class="ap2-sim-setup">
        <div class="ap2-sim-filter">
          <label>{{ t('ap2Trainer.exam.filterBereich') }}:</label>
          <select v-model="bereichFilter">
            <option value="all">{{ t('ap2Trainer.exam.filterAll') }}</option>
            <option value="PB2">PB2</option>
            <option value="PB3">PB3</option>
            <option value="WISO">WISO</option>
          </select>
        </div>

        <div v-if="loading" class="ap2-sim-loading">{{ t('ap2Trainer.exam.loading') }}</div>

        <div v-else-if="filteredApplicationItems.length === 0" class="ap2-sim-empty">
          {{ t('ap2Trainer.exam.empty') }}
        </div>

        <div v-else class="ap2-sim-summary">
          <p>
            {{ t('ap2Trainer.exam.startCount', {
              n: filteredApplicationItems.length,
              pts: totalPoints,
              min: totalEstMin
            }) }}
          </p>
          <button class="ap2-btn ap2-btn-primary" @click="start">
            {{ t('ap2Trainer.exam.startBtn') }}
          </button>
        </div>
      </div>
    </template>

    <!-- Running-Modus -->
    <template v-else-if="mode === 'running' && currentItem">
      <header class="ap2-sim-running-header">
        <span class="ap2-sim-progress">
          {{ t('ap2Trainer.exam.progressLabel', {
            current: currentIdx + 1,
            total: selectedItems.length
          }) }}
        </span>
        <span class="ap2-sim-timer" :class="{ 'ap2-timer-urgent': timeLeftSec < 300 }">
          ⏱ {{ formatTime(timeLeftSec) }}
        </span>
      </header>

      <ApplicationPhase
        :item="currentItem"
        :response="currentResponse"
        :submitting="submitting"
        :is-last="currentIdx === selectedItems.length - 1"
        @submit="onSubmit"
        @next="onNext"
      />
    </template>

    <!-- Results -->
    <template v-else-if="mode === 'results'">
      <div class="ap2-sim-results">
        <h2>{{ t('ap2Trainer.exam.resultsTitle') }}</h2>
        <div class="ap2-sim-score" :class="scoreClass">
          {{ t('ap2Trainer.exam.resultsScore', {
            pct: overallPct,
            earned: totalEarned.toFixed(1),
            total: totalAttempted.toFixed(1)
          }) }}
        </div>
        <ul class="ap2-sim-per-item">
          <li v-for="(r, i) in resultsList" :key="i">
            {{ t('ap2Trainer.exam.resultsPerItem', { n: i + 1, pct: r.pct }) }}
          </li>
        </ul>
        <button class="ap2-btn" @click="reset">
          {{ t('ap2Trainer.exam.backToList') }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  listAp2Topics, getAp2TopicDetail, submitAp2Attempt, startAp2Session, endAp2Session,
  type Ap2Item, type Ap2SubmitResponse,
} from '@/infrastructure/api/clients/panel/user/exams'
import ApplicationPhase from '../components/active-recall/ApplicationPhase.vue'

const { t } = useI18n()

const mode = ref<'setup' | 'running' | 'results'>('setup')
const loading = ref(false)
const submitting = ref(false)
const bereichFilter = ref<'all' | 'PB2' | 'PB3' | 'WISO'>('all')

const allApplicationItems = ref<Array<Ap2Item & { bereich: string }>>([])
const selectedItems = ref<Array<Ap2Item & { bereich: string }>>([])
const currentIdx = ref(0)
const currentResponse = ref<Ap2SubmitResponse | null>(null)
const results = ref<Ap2SubmitResponse[]>([])
const sessionId = ref<string | null>(null)

const timeLeftSec = ref(90 * 60)
let timerInterval: ReturnType<typeof setInterval> | null = null

const filteredApplicationItems = computed(() => {
  if (bereichFilter.value === 'all') return allApplicationItems.value
  return allApplicationItems.value.filter(
    (i) => i.bereich === bereichFilter.value || i.bereich === 'both'
  )
})
const totalPoints = computed(() =>
  filteredApplicationItems.value.reduce((s, i) => s + i.points, 0).toFixed(0)
)
const totalEstMin = computed(() =>
  Math.round(filteredApplicationItems.value.reduce((s, i) => s + i.estimated_time_sec, 0) / 60)
)
const currentItem = computed(() => selectedItems.value[currentIdx.value] || null)

const totalEarned = computed(() =>
  results.value.reduce((s, r) => s + r.points_earned, 0)
)
const totalAttempted = computed(() =>
  results.value.reduce((s, r) => s + r.points_total, 0)
)
const overallPct = computed(() =>
  totalAttempted.value > 0
    ? Math.round((totalEarned.value / totalAttempted.value) * 100)
    : 0
)
const scoreClass = computed(() => {
  if (overallPct.value >= 65) return 'ap2-score-good'
  if (overallPct.value >= 50) return 'ap2-score-ok'
  return 'ap2-score-bad'
})
const resultsList = computed(() =>
  results.value.map((r) => ({ pct: r.pct }))
)

async function loadItems() {
  loading.value = true
  try {
    const topicsRes = await listAp2Topics()
    const items: Array<Ap2Item & { bereich: string }> = []
    for (const tp of topicsRes.topics) {
      const detail = await getAp2TopicDetail(tp.slug)
      for (const item of detail.items.application) {
        items.push({ ...item, bereich: tp.bereich })
      }
    }
    allApplicationItems.value = items
  } catch (e) {
    console.warn('[AP2] load items failed:', e)
  } finally {
    loading.value = false
  }
}

async function start() {
  selectedItems.value = [...filteredApplicationItems.value]
  currentIdx.value = 0
  results.value = []
  currentResponse.value = null
  timeLeftSec.value = 90 * 60
  try {
    const s = await startAp2Session({
      session_type: 'exam_simulation',
      metadata: { filter: bereichFilter.value, count: selectedItems.value.length },
    })
    sessionId.value = s.session_id
  } catch (e) {
    console.warn('[AP2] start session failed:', e)
  }
  mode.value = 'running'
  timerInterval = setInterval(() => {
    timeLeftSec.value = Math.max(0, timeLeftSec.value - 1)
    if (timeLeftSec.value === 0) finish()
  }, 1000)
}

async function onSubmit(text: string) {
  if (!currentItem.value) return
  submitting.value = true
  try {
    const res = await submitAp2Attempt({
      item_id: currentItem.value.item_id,
      phase: 'application',
      answer_text: text,
      session_id: sessionId.value ?? undefined,
    })
    currentResponse.value = res
    results.value.push(res)
  } catch (e) {
    console.warn('[AP2] submit failed:', e)
  } finally {
    submitting.value = false
  }
}

function onNext() {
  currentResponse.value = null
  if (currentIdx.value < selectedItems.value.length - 1) {
    currentIdx.value++
  } else {
    finish()
  }
}

async function finish() {
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null }
  if (sessionId.value) {
    try { await endAp2Session(sessionId.value) } catch (e) { /* noop */ }
  }
  mode.value = 'results'
}

function reset() {
  mode.value = 'setup'
  currentIdx.value = 0
  results.value = []
  currentResponse.value = null
  selectedItems.value = []
  sessionId.value = null
}

function formatTime(sec: number) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

onMounted(loadItems)
onUnmounted(() => { if (timerInterval) clearInterval(timerInterval) })
</script>

<style scoped>
.ap2-sim { display: flex; flex-direction: column; gap: 16px; }
.ap2-sim-header h2 { color: var(--color-text-primary, #fff); margin: 0 0 4px; font-size: 22px; }
.ap2-sim-sub { color: #94a3b8; margin: 0; font-size: 13px; }

.ap2-sim-setup { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 12px; padding: 20px; }
.ap2-sim-filter { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.ap2-sim-filter label { color: #cbd5e1; font-size: 13px; font-weight: 600; }
.ap2-sim-filter select { padding: 6px 12px; background: rgba(0,0,0,0.2); border: 1px solid var(--color-border, #334155); border-radius: 6px; color: #fff; font-size: 13px; }
.ap2-sim-loading, .ap2-sim-empty { padding: 24px; text-align: center; color: #94a3b8; }
.ap2-sim-summary p { color: #cbd5e1; font-size: 13px; margin: 0 0 12px; }

.ap2-sim-running-header { display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.1)); border: 1px solid #4338ca; border-radius: 10px; }
.ap2-sim-progress { font-weight: 700; color: #a5b4fc; font-size: 13px; }
.ap2-sim-timer { font-family: ui-monospace, monospace; font-size: 16px; font-weight: 700; color: #22c55e; padding: 4px 10px; background: rgba(34, 197, 94, 0.08); border-radius: 6px; }
.ap2-timer-urgent { color: #ef4444 !important; background: rgba(239, 68, 68, 0.1) !important; animation: pulse 1s infinite; }
@keyframes pulse { 50% { opacity: 0.6; } }

.ap2-sim-results { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 12px; padding: 32px; text-align: center; }
.ap2-sim-results h2 { color: #fff; font-size: 22px; margin: 0 0 16px; }
.ap2-sim-score { font-size: 32px; font-weight: 800; margin-bottom: 24px; }
.ap2-score-good { color: #4ade80; }
.ap2-score-ok { color: #fbbf24; }
.ap2-score-bad { color: #f87171; }
.ap2-sim-per-item { list-style: decimal inside; padding: 0; margin: 0 auto 20px; max-width: 400px; text-align: left; color: #cbd5e1; font-size: 13px; }
.ap2-sim-per-item li { padding: 4px 0; }

.ap2-btn { padding: 10px 24px; border-radius: 8px; border: 1px solid var(--color-border, #334155); background: rgba(255,255,255,0.05); color: #cbd5e1; cursor: pointer; font-size: 13px; font-weight: 600; }
.ap2-btn-primary { background: #4338ca; border-color: #4338ca; color: #fff; }
.ap2-btn-primary:hover { background: #3730a3; }
</style>
