<template>
  <div class="ap2-dash">
    <div v-if="loading && !stats" class="ap2-loading">{{ t('ap2Trainer.dashboard.loading') }}</div>

    <div v-else-if="overall && overall.attempts === 0" class="ap2-empty">
      <h2>{{ t('ap2Trainer.dashboard.empty.title') }}</h2>
      <p>{{ t('ap2Trainer.dashboard.empty.subtitle') }}</p>
      <div class="ap2-empty-actions">
        <RouterLink to="/ap2-training/study" class="ap2-cta ap2-cta-primary">
          {{ t('ap2Trainer.dashboard.empty.ctaStudy') }}
        </RouterLink>
        <RouterLink to="/ap2-training/review" class="ap2-cta">
          {{ t('ap2Trainer.dashboard.empty.ctaReview') }} ({{ reviewQueueCount }})
        </RouterLink>
      </div>
    </div>

    <template v-else-if="overall">
      <section class="ap2-qstats">
        <div class="ap2-qs">
          <div class="ap2-qs-val">{{ overall.attempts }}</div>
          <div class="ap2-qs-label">{{ t('ap2Trainer.dashboard.stats.attempted') }}</div>
        </div>
        <div class="ap2-qs ap2-qs-correct">
          <div class="ap2-qs-val">{{ overall.correct }}</div>
          <div class="ap2-qs-label">{{ t('ap2Trainer.dashboard.stats.correct') }}</div>
        </div>
        <div class="ap2-qs ap2-qs-wrong">
          <div class="ap2-qs-val">{{ overall.attempts - overall.correct }}</div>
          <div class="ap2-qs-label">{{ t('ap2Trainer.dashboard.stats.wrong') }}</div>
        </div>
        <div class="ap2-qs">
          <div class="ap2-qs-val" :class="overallPctClass">{{ overall.pct }}%</div>
          <div class="ap2-qs-label">{{ t('ap2Trainer.dashboard.stats.overall') }}</div>
        </div>
        <div class="ap2-qs">
          <div class="ap2-qs-val">{{ reviewQueueCount }}</div>
          <div class="ap2-qs-label">{{ t('ap2Trainer.dashboard.stats.due') }}</div>
        </div>
      </section>

      <section class="ap2-grid">
        <div class="ap2-card ap2-prognose">
          <h3 class="ap2-card-title">{{ t('ap2Trainer.dashboard.prognose.title') }}</h3>
          <div class="ap2-ring">
            <svg viewBox="0 0 120 120">
              <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="9" />
              <circle
                cx="60" cy="60" r="52" fill="none"
                :stroke="ringColor"
                stroke-width="9" stroke-linecap="round"
                :stroke-dasharray="`${overall.pct / 100 * 326.7} 326.7`"
                transform="rotate(-90 60 60)"
              />
            </svg>
            <div class="ap2-ring-text">
              <div class="ap2-ring-pct" :class="overallPctClass">{{ overall.pct }}%</div>
              <div class="ap2-ring-status">{{ predictionLabel }}</div>
            </div>
          </div>
          <p class="ap2-prognose-target">{{ t('ap2Trainer.dashboard.prognose.target') }}</p>
        </div>

        <div class="ap2-card ap2-bereiche">
          <h3 class="ap2-card-title">{{ t('ap2Trainer.dashboard.bereich.title') }}</h3>
          <div
            v-for="key in bereichKeys"
            :key="key"
            class="ap2-b-row"
            :class="bereichRowClass(key)"
          >
            <div class="ap2-b-info">
              <span class="ap2-b-key">{{ key }}</span>
              <span class="ap2-b-label">{{ t(`ap2Trainer.dashboard.bereich.${key}`) }}</span>
            </div>
            <div class="ap2-b-bar-wrap">
              <div class="ap2-b-bar">
                <div
                  v-if="bereichStats[key]"
                  class="ap2-b-bar-fill"
                  :style="{ width: Math.min(bereichStats[key].pct, 100) + '%' }"
                  :class="bereichBarClass(bereichStats[key].pct)"
                />
                <div class="ap2-b-bar-mark50" />
              </div>
              <span v-if="bereichStats[key]" class="ap2-b-pct">{{ bereichStats[key].pct }}%</span>
              <span v-else class="ap2-b-pct ap2-b-nodata">{{ t('ap2Trainer.dashboard.bereich.noData') }}</span>
            </div>
          </div>
        </div>
      </section>

      <section v-if="recentRegressions.length > 0" class="ap2-card ap2-mini-weak">
        <h3 class="ap2-card-title">{{ t('ap2Trainer.dashboard.miniWeak.title') }}</h3>
        <p class="ap2-card-sub">{{ t('ap2Trainer.dashboard.miniWeak.subtitle') }}</p>
        <ul class="ap2-mini-list">
          <li v-for="r in recentRegressions" :key="r.item_id" class="ap2-mini-item">
            <div class="ap2-mini-topic">{{ r.topic_name }}</div>
            <div class="ap2-mini-prompt">{{ r.item_prompt }}</div>
            <div class="ap2-mini-trend">
              <span class="ap2-mini-prev">{{ r.prev_pct }}%</span>
              <span class="ap2-mini-arrow">→</span>
              <span class="ap2-mini-last">{{ r.last_pct }}%</span>
              <span class="ap2-mini-delta">{{ t('ap2Trainer.dashboard.miniWeak.delta', { n: r.regression_size }) }}</span>
            </div>
          </li>
        </ul>
      </section>

      <section v-if="weaknesses.length > 0" class="ap2-card ap2-weaknesses">
        <h3 class="ap2-card-title">{{ t('ap2Trainer.dashboard.topWeak.title') }}</h3>
        <div class="ap2-weak-tags">
          <RouterLink
            v-for="w in weaknesses.slice(0, 8)"
            :key="w.topic_slug"
            :to="`/ap2-training/study/${w.topic_slug}`"
            class="ap2-weak-tag"
          >
            <span class="ap2-weak-name">{{ w.topic_name }}</span>
            <span class="ap2-weak-pct">{{ Math.round(w.mastery_score) }}%</span>
          </RouterLink>
        </div>
      </section>

      <TelegramConnectCard />
    </template>

    <div v-if="error" class="ap2-error">
      ⚠️ {{ t('ap2Trainer.dashboard.error') }}: {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAp2Stats } from '../composables'
import TelegramConnectCard from '../components/TelegramConnectCard.vue'

const { t } = useI18n()
const {
  stats, loading, error, overall,
  bereichStats, recentRegressions, weaknesses, reviewQueueCount,
} = useAp2Stats()

const bereichKeys = ['PB2', 'PB3', 'WISO'] as const

const overallPctClass = computed(() => {
  const pct = overall.value?.pct ?? 0
  if (pct >= 65) return 'ap2-good'
  if (pct >= 50) return 'ap2-ok'
  return 'ap2-bad'
})

const ringColor = computed(() => {
  const pct = overall.value?.pct ?? 0
  if (pct >= 65) return '#22c55e'
  if (pct >= 50) return '#f59e0b'
  return '#ef4444'
})

const predictionLabel = computed(() => {
  const p = overall.value?.pass_prediction
  if (p === 'bestanden') return t('ap2Trainer.dashboard.prognose.passed')
  if (p === 'gefaehrdet') return t('ap2Trainer.dashboard.prognose.endangered')
  return t('ap2Trainer.dashboard.prognose.noData')
})

function bereichRowClass(key: string) {
  const s = bereichStats.value[key]
  if (!s) return ''
  return s.pct >= 50 ? 'ap2-b-row-pass' : 'ap2-b-row-fail'
}
function bereichBarClass(pct: number) {
  if (pct >= 65) return 'ap2-bf-good'
  if (pct >= 50) return 'ap2-bf-ok'
  return 'ap2-bf-bad'
}
</script>

<style scoped>
.ap2-dash { display: flex; flex-direction: column; gap: 16px; }
.ap2-loading, .ap2-error { padding: 16px; color: #94a3b8; text-align: center; }
.ap2-error { color: #f87171; }
.ap2-empty { text-align: center; padding: 48px 24px; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 14px; }
.ap2-empty h2 { color: var(--color-text-primary, #fff); margin-bottom: 8px; }
.ap2-empty p  { color: #94a3b8; margin-bottom: 20px; }
.ap2-empty-actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.ap2-cta { padding: 12px 24px; border-radius: 10px; font-weight: 600; text-decoration: none; background: rgba(99, 102, 241, 0.15); color: #a5b4fc; border: 1px solid #4338ca; }
.ap2-cta-primary { background: #4338ca; color: #fff; }
.ap2-qstats { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; }
.ap2-qs { text-align: center; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); padding: 12px 8px; border-radius: 10px; }
.ap2-qs-val { font-size: 26px; font-weight: 800; line-height: 1.1; }
.ap2-qs-label { font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
.ap2-qs-correct .ap2-qs-val { color: #4ade80; }
.ap2-qs-wrong .ap2-qs-val { color: #f87171; }
.ap2-good { color: #4ade80 !important; }
.ap2-ok { color: #fbbf24 !important; }
.ap2-bad { color: #f87171 !important; }
.ap2-grid { display: grid; grid-template-columns: 320px 1fr; gap: 12px; }
@media (max-width: 768px) { .ap2-grid { grid-template-columns: 1fr; } }
.ap2-card { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 12px; padding: 14px; }
.ap2-card-title { font-size: 13px; color: #cbd5e1; margin: 0 0 8px; font-weight: 700; }
.ap2-card-sub { font-size: 11px; color: #94a3b8; margin: 0 0 10px; }
.ap2-prognose { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.ap2-ring { position: relative; width: 140px; height: 140px; }
.ap2-ring svg { width: 100%; height: 100%; }
.ap2-ring-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.ap2-ring-pct { font-size: 28px; font-weight: 800; }
.ap2-ring-status { font-size: 10px; color: #94a3b8; text-transform: uppercase; }
.ap2-prognose-target { font-size: 10px; color: #64748b; margin: 0; text-align: center; }
.ap2-b-row { display: grid; grid-template-columns: minmax(150px, 1fr) 2fr; align-items: center; gap: 12px; padding: 8px 0; border-top: 1px solid var(--color-border, #334155); }
.ap2-b-row:first-of-type { border-top: 0; }
.ap2-b-key { font-weight: 700; font-size: 14px; color: #cbd5e1; margin-right: 8px; }
.ap2-b-label { font-size: 11px; color: #94a3b8; }
.ap2-b-bar-wrap { display: flex; align-items: center; gap: 8px; }
.ap2-b-bar { position: relative; flex: 1; height: 8px; background: rgba(255,255,255,0.06); border-radius: 4px; overflow: hidden; }
.ap2-b-bar-fill { position: absolute; inset: 0; border-radius: 4px; }
.ap2-bf-good { background: #22c55e; }
.ap2-bf-ok   { background: #f59e0b; }
.ap2-bf-bad  { background: #ef4444; }
.ap2-b-bar-mark50 { position: absolute; left: 50%; top: -2px; bottom: -2px; width: 1px; background: rgba(255, 255, 255, 0.4); }
.ap2-b-pct { font-size: 12px; font-weight: 700; min-width: 36px; text-align: right; color: #cbd5e1; }
.ap2-b-nodata { color: #475569; }
.ap2-mini-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.ap2-mini-item { display: grid; grid-template-columns: 1fr auto; gap: 12px; padding: 8px 12px; background: rgba(245, 158, 11, 0.08); border-left: 3px solid #f59e0b; border-radius: 4px; }
.ap2-mini-topic { font-size: 11px; color: #fbbf24; font-weight: 700; text-transform: uppercase; }
.ap2-mini-prompt { font-size: 12px; color: #cbd5e1; }
.ap2-mini-trend { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.ap2-mini-prev { color: #4ade80; font-weight: 700; }
.ap2-mini-arrow { color: #64748b; }
.ap2-mini-last { color: #f87171; font-weight: 700; }
.ap2-mini-delta { font-size: 10px; color: #94a3b8; }
.ap2-weak-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.ap2-weak-tag { display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 999px; background: rgba(239, 68, 68, 0.12); border: 1px solid #dc2626; color: #fca5a5; font-size: 12px; font-weight: 600; text-decoration: none; }
.ap2-weak-tag:hover { background: rgba(239, 68, 68, 0.2); }
.ap2-weak-pct { font-weight: 800; color: #f87171; }
</style>
