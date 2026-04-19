<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  getModuleDetail,
  listModules,
  type ModuleDetailResponse,
  type ModuleItem,
  type ItemSkillState,
} from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'
import SubAreaHeatmap from '../components/active-recall/SubAreaHeatmap.vue'

interface Props { slug: string }
const props = defineProps<Props>()

const { t } = useI18n()
const router = useRouter()

const detail = ref<ModuleDetailResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

type FilterKey = 'all' | 'mastered' | 'in_progress' | 'recovery' | 'fresh'
const filter = ref<FilterKey>('all')
const subAreaFilter = ref<string | null>(null)

function selectSubArea(sa: string) {
  subAreaFilter.value = subAreaFilter.value === sa ? null : sa
}

const filters: Array<{ key: FilterKey; labelKey: string }> = [
  { key: 'all',         labelKey: 'ap2Trainer.moduleDetail.filterAll' },
  { key: 'mastered',    labelKey: 'ap2Trainer.moduleDetail.filterMastered' },
  { key: 'in_progress', labelKey: 'ap2Trainer.moduleDetail.filterInProgress' },
  { key: 'recovery',    labelKey: 'ap2Trainer.moduleDetail.filterRecovery' },
  { key: 'fresh',       labelKey: 'ap2Trainer.moduleDetail.filterFresh' },
]

async function load() {
  loading.value = true
  error.value = null
  try {
    const all = await listModules()
    const m = all.find(x => x.slug === props.slug)
    if (!m) {
      error.value = `Modul "${props.slug}" nicht gefunden.`
      return
    }
    detail.value = await getModuleDetail(m.module_id)
  } catch (e: any) {
    error.value = e?.response?.data?.error || 'Details konnten nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

function skillCategory(s: ItemSkillState): FilterKey {
  if (s.is_mastered) return 'mastered'
  if (s.is_in_recovery) return 'recovery'
  if (s.total_attempts > 0) return 'in_progress'
  return 'fresh'
}

const filteredItems = computed(() => {
  if (!detail.value) return []
  let items = detail.value.items
  if (subAreaFilter.value) {
    items = items.filter(i =>
      (i.sub_area || 'uncategorized') === subAreaFilter.value,
    )
  }
  if (filter.value === 'all') return items
  return items.filter(i => skillCategory(i.skill) === filter.value)
})

const progressPct = computed(() => {
  if (!detail.value) return 0
  const s = detail.value.item_stats
  if (!s.total) return 0
  return Math.round((s.mastered / s.total) * 100)
})

function startRunner() {
  if (detail.value) router.push(`/ap2-training/modules/${detail.value.module.slug}`)
}

function back() { router.push('/ap2-training/modules') }

function truncate(s: string, n = 120): string {
  if (s.length <= n) return s
  return s.substring(0, n).trim() + '…'
}

function formatTime(iso: string | null): string {
  if (!iso) return ''
  return new Date(iso).toLocaleString('de-DE', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
  })
}

function skillLabel(s: ItemSkillState): string {
  if (s.is_mastered) return t('ap2Trainer.moduleDetail.item.mastered')
  if (s.is_in_recovery) return t('ap2Trainer.moduleDetail.item.recovery')
  if (s.total_attempts === 0) return t('ap2Trainer.moduleDetail.item.notStarted')
  return t('ap2Trainer.moduleDetail.item.kopfSerie', {
    done: s.kopf_serie_count,
    target: s.effective_target ?? '?',
  })
}

onMounted(load)
watch(() => props.slug, load)
</script>

<template>
  <div class="mod-detail">
    <header class="md-head">
      <button class="md-back" @click="back">
        {{ $t('ap2Trainer.moduleDetail.back') }}
      </button>
      <button
        v-if="detail"
        class="btn btn-primary md-start"
        @click="startRunner"
      >
        {{ $t('ap2Trainer.moduleDetail.startBtn') }}
      </button>
    </header>

    <div v-if="loading" class="md-loading">
      {{ $t('ap2Trainer.moduleDetail.loading') }}
    </div>

    <div v-else-if="error" class="md-error">⚠️ {{ error }}</div>

    <template v-else-if="detail">
      <section class="md-title">
        <h2>{{ detail.module.name_de }}</h2>
        <p v-if="detail.module.description" class="md-desc">
          {{ detail.module.description }}
        </p>
      </section>

      <!-- PROGRESS OVERVIEW -->
      <section class="md-overview">
        <h3>{{ $t('ap2Trainer.moduleDetail.statsHeader') }}</h3>

        <div class="md-progress-bar">
          <div class="md-progress-fill" :style="{ width: progressPct + '%' }" />
        </div>
        <p class="md-progress-label">
          {{ $t('ap2Trainer.moduleDetail.progressBar', {
            done: detail.item_stats.mastered,
            total: detail.item_stats.total,
          }) }}
        </p>

        <div class="md-stats-grid">
          <div class="md-stat md-stat-mastered">
            <div class="md-stat-value">{{ detail.item_stats.mastered }}</div>
            <div class="md-stat-label">
              {{ $t('ap2Trainer.moduleDetail.stats.mastered') }}
            </div>
          </div>
          <div class="md-stat md-stat-progress">
            <div class="md-stat-value">{{ detail.item_stats.in_progress }}</div>
            <div class="md-stat-label">
              {{ $t('ap2Trainer.moduleDetail.stats.in_progress') }}
            </div>
          </div>
          <div class="md-stat md-stat-recovery">
            <div class="md-stat-value">{{ detail.item_stats.recovery }}</div>
            <div class="md-stat-label">
              {{ $t('ap2Trainer.moduleDetail.stats.recovery') }}
            </div>
          </div>
          <div class="md-stat">
            <div class="md-stat-value">{{ detail.item_stats.total_attempts }}</div>
            <div class="md-stat-label">
              {{ $t('ap2Trainer.moduleDetail.stats.total_attempts') }}
            </div>
          </div>
          <div class="md-stat">
            <div class="md-stat-value">{{ detail.item_stats.stuetzrad_uses }}</div>
            <div class="md-stat-label">
              {{ $t('ap2Trainer.moduleDetail.stats.stuetzrad_uses') }}
            </div>
          </div>
          <div class="md-stat">
            <div class="md-stat-value">{{ detail.item_stats.total }}</div>
            <div class="md-stat-label">
              {{ $t('ap2Trainer.moduleDetail.stats.total') }}
            </div>
          </div>
        </div>
      </section>

      <!-- SUB-AREA HEATMAP -->
      <SubAreaHeatmap
        :sub-areas="detail.sub_areas || []"
        @select="selectSubArea"
      />

      <!-- ITEMS -->
      <section class="md-items">
        <div class="md-items-head">
          <h3>
            {{ $t('ap2Trainer.moduleDetail.itemsHeader') }}
            <button
              v-if="subAreaFilter"
              type="button"
              class="md-subarea-chip"
              @click="subAreaFilter = null"
            >
              {{ subAreaFilter }} ✕
            </button>
          </h3>
          <div class="md-filters">
            <button
              v-for="f in filters"
              :key="f.key"
              type="button"
              class="md-filter"
              :class="{ 'md-filter--active': filter === f.key }"
              @click="filter = f.key"
            >
              {{ $t(f.labelKey) }}
            </button>
          </div>
        </div>

        <ul class="md-item-list">
          <li
            v-for="it in filteredItems"
            :key="it.item_id"
            class="md-item"
            :class="`md-item--${skillCategory(it.skill)}`"
          >
            <div class="md-item-main">
              <div class="md-item-prompt">{{ truncate(it.prompt) }}</div>
              <div class="md-item-meta">
                <span class="md-item-skill">{{ skillLabel(it.skill) }}</span>
                <span
                  v-if="it.skill.stuetzrad_uses > 0"
                  class="md-item-stuetzrad"
                >
                  {{ $t('ap2Trainer.moduleDetail.item.stuetzradUses',
                        { n: it.skill.stuetzrad_uses }) }}
                </span>
                <span
                  v-if="it.skill.last_score_pct !== null"
                  class="md-item-last"
                >
                  {{ $t('ap2Trainer.moduleDetail.item.lastScore',
                        { pct: Math.round(it.skill.last_score_pct) }) }}
                </span>
                <span
                  v-if="it.skill.snoozed_until"
                  class="md-item-snoozed"
                >
                  {{ $t('ap2Trainer.moduleDetail.item.snoozed',
                        { time: formatTime(it.skill.snoozed_until) }) }}
                </span>
              </div>
            </div>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>

<style scoped>
.mod-detail { max-width: 980px; margin: 0 auto; padding: 1rem; }

.md-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}
.md-back {
  background: transparent; border: 0;
  color: #94a3b8; font-size: 0.85rem; cursor: pointer;
  padding: 0.3rem 0;
}
.md-back:hover { color: #cbd5e1; }

.btn {
  padding: 0.55rem 1rem; border: 0; border-radius: 6px;
  font-weight: 600; font-size: 0.88rem; cursor: pointer;
}
.btn-primary { background: #2563eb; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #1e40af; }

.md-loading, .md-error {
  padding: 1rem; border-radius: 8px;
  background: var(--color-surface, #1e293b);
  color: #cbd5e1;
}
.md-error { background: #7f1d1d33; border-left: 3px solid #dc2626; color: #fecaca; }

.md-title h2 { margin: 0; color: #f1f5f9; }
.md-desc { color: #94a3b8; margin: 0.3rem 0 1.2rem 0; line-height: 1.5; font-size: 0.9rem; }

.md-overview, .md-items {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1.2rem;
  margin-bottom: 1rem;
}
.md-overview h3, .md-items h3 { margin: 0 0 0.8rem 0; color: #f1f5f9; font-size: 1rem; }

.md-progress-bar {
  height: 10px; background: rgba(255,255,255,0.06);
  border-radius: 5px; overflow: hidden;
  margin-bottom: 0.3rem;
}
.md-progress-fill { height: 100%; background: #16a34a; transition: width 0.3s; }
.md-progress-label { margin: 0 0 1rem 0; color: #cbd5e1; font-size: 0.82rem; }

.md-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 0.6rem;
}
.md-stat {
  background: rgba(0,0,0,0.2);
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 0.6rem 0.5rem;
  text-align: center;
}
.md-stat-mastered { border-color: rgba(22,163,74,0.5); }
.md-stat-progress { border-color: rgba(245,158,11,0.5); }
.md-stat-recovery { border-color: rgba(220,38,38,0.5); }
.md-stat-value { font-size: 1.3rem; font-weight: 700; color: #f1f5f9; }
.md-stat-label { font-size: 0.72rem; color: #94a3b8; margin-top: 0.2rem; }

.md-subarea-chip {
  margin-left: 0.5rem;
  padding: 0.15rem 0.5rem;
  background: rgba(139,92,246,0.2);
  border: 1px solid #8b5cf6;
  border-radius: 999px;
  color: #c4b5fd;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
}
.md-subarea-chip:hover { background: rgba(139,92,246,0.3); }

.md-items-head {
  display: flex; justify-content: space-between;
  align-items: center; flex-wrap: wrap; gap: 0.5rem;
  margin-bottom: 0.8rem;
}
.md-filters { display: flex; gap: 0.3rem; flex-wrap: wrap; }
.md-filter {
  padding: 0.3rem 0.7rem;
  background: rgba(0,0,0,0.2);
  border: 1px solid #334155;
  color: #94a3b8;
  border-radius: 999px;
  font-size: 0.78rem;
  cursor: pointer;
}
.md-filter:hover { border-color: #475569; color: #cbd5e1; }
.md-filter--active {
  background: rgba(59,130,246,0.2);
  border-color: #3b82f6;
  color: #e0e7ff;
}

.md-item-list { list-style: none; padding: 0; margin: 0; }
.md-item {
  padding: 0.7rem 0.8rem;
  border: 1px solid #334155;
  border-left: 3px solid #475569;
  border-radius: 6px;
  margin-bottom: 0.4rem;
  background: rgba(0,0,0,0.15);
}
.md-item--mastered { border-left-color: #16a34a; }
.md-item--in_progress { border-left-color: #f59e0b; }
.md-item--recovery { border-left-color: #dc2626; }
.md-item--fresh { border-left-color: #64748b; }

.md-item-prompt {
  color: #f1f5f9;
  font-size: 0.88rem;
  line-height: 1.4;
  margin-bottom: 0.3rem;
}
.md-item-meta {
  display: flex; flex-wrap: wrap; gap: 0.8rem;
  font-size: 0.75rem; color: #94a3b8;
}
.md-item-skill { color: #cbd5e1; font-weight: 500; }
.md-item-stuetzrad { color: #93c5fd; }
.md-item-last { color: #fbbf24; }
.md-item-snoozed { color: #d8b4fe; }
</style>
