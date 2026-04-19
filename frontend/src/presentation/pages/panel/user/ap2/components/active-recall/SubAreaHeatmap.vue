<script setup lang="ts">
import { computed } from 'vue'
import type { SubAreaStat } from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'

interface Props {
  subAreas: SubAreaStat[]
}
const props = defineProps<Props>()

const emit = defineEmits<{
  select: [subArea: string]
}>()

function heatClass(s: SubAreaStat): string {
  if (s.total === 0) return 'heat-empty'
  const masteredPct = s.mastered / s.total
  const recoveryPct = s.recovery / s.total
  if (recoveryPct >= 0.3) return 'heat-red'
  if (masteredPct >= 0.8) return 'heat-green'
  if (masteredPct >= 0.5) return 'heat-yellow-green'
  if (masteredPct >= 0.25) return 'heat-yellow'
  if (s.in_progress > 0) return 'heat-orange'
  return 'heat-cold'
}

function pctLabel(s: SubAreaStat): string {
  if (s.total === 0) return '0%'
  const pct = Math.round((s.mastered / s.total) * 100)
  return `${pct}%`
}

const sorted = computed(() =>
  [...props.subAreas].sort((a, b) => {
    const sa = a.meta?.sort_order ?? 999
    const sb = b.meta?.sort_order ?? 999
    if (sa !== sb) return sa - sb
    return a.sub_area.localeCompare(b.sub_area)
  })
)
</script>

<template>
  <section class="heatmap">
    <header class="heatmap-head">
      <h3>{{ $t('ap2Trainer.heatmap.title') }}</h3>
      <div class="heatmap-legend">
        <span class="legend-item"><span class="legend-swatch heat-green" />
          {{ $t('ap2Trainer.heatmap.legend.mastered') }}
        </span>
        <span class="legend-item"><span class="legend-swatch heat-yellow" />
          {{ $t('ap2Trainer.heatmap.legend.in_progress') }}
        </span>
        <span class="legend-item"><span class="legend-swatch heat-red" />
          {{ $t('ap2Trainer.heatmap.legend.recovery') }}
        </span>
        <span class="legend-item"><span class="legend-swatch heat-cold" />
          {{ $t('ap2Trainer.heatmap.legend.fresh') }}
        </span>
      </div>
    </header>

    <div v-if="!sorted.length" class="heatmap-empty">
      {{ $t('ap2Trainer.heatmap.empty') }}
    </div>

    <div v-else class="heatmap-grid">
      <button
        v-for="s in sorted"
        :key="s.sub_area"
        type="button"
        class="heat-cell"
        :class="heatClass(s)"
        @click="emit('select', s.sub_area)"
      >
        <span class="heat-icon">{{ s.meta?.icon || '•' }}</span>
        <span class="heat-label">{{ s.meta?.label_de || s.sub_area }}</span>
        <span class="heat-pct">{{ pctLabel(s) }}</span>
        <span class="heat-counts">
          <span class="heat-count c-m">{{ s.mastered }}</span>
          <span class="heat-sep">/</span>
          <span class="heat-count c-t">{{ s.total }}</span>
        </span>
        <span v-if="s.avg_score_pct > 0" class="heat-avg">
          {{ $t('ap2Trainer.heatmap.cell.avgScore',
                { pct: Math.round(s.avg_score_pct) }) }}
        </span>
      </button>
    </div>
  </section>
</template>

<style scoped>
.heatmap {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1.2rem;
  margin-bottom: 1rem;
}

.heatmap-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-bottom: 0.8rem;
}
.heatmap-head h3 { margin: 0; color: #f1f5f9; font-size: 1rem; }

.heatmap-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  font-size: 0.72rem;
  color: #94a3b8;
  align-items: center;
}
.legend-item { display: inline-flex; align-items: center; gap: 0.3rem; }
.legend-swatch {
  display: inline-block; width: 10px; height: 10px; border-radius: 2px;
}

.heatmap-empty {
  padding: 1rem;
  text-align: center;
  color: #94a3b8;
  font-size: 0.85rem;
}

.heatmap-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.4rem;
}

.heat-cell {
  display: grid;
  grid-template-columns: auto 1fr auto;
  grid-template-rows: auto auto;
  grid-template-areas:
    "icon label pct"
    "icon counts avg";
  gap: 0.1rem 0.4rem;
  align-items: center;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--color-border, #334155);
  border-left-width: 4px;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  background: rgba(0,0,0,0.2);
  transition: transform 0.12s, background 0.12s, border-color 0.12s;
}
.heat-cell:hover { transform: translateY(-1px); background: rgba(0,0,0,0.3); }

.heat-icon { grid-area: icon; font-size: 1.1rem; }
.heat-label {
  grid-area: label;
  color: #f1f5f9;
  font-size: 0.82rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.heat-pct {
  grid-area: pct;
  color: #fbbf24;
  font-weight: 700;
  font-size: 0.88rem;
}
.heat-counts {
  grid-area: counts;
  font-size: 0.72rem;
  color: #94a3b8;
}
.c-m { color: #86efac; font-weight: 600; }
.c-t { color: #cbd5e1; }
.heat-sep { margin: 0 0.1rem; }
.heat-avg {
  grid-area: avg;
  justify-self: end;
  font-size: 0.68rem;
  color: #64748b;
}

.heat-empty, .heat-cold { border-left-color: #475569; }
.heat-orange       { border-left-color: #f97316; background: rgba(249,115,22,0.08); }
.heat-yellow       { border-left-color: #eab308; background: rgba(234,179,8,0.08); }
.heat-yellow-green { border-left-color: #84cc16; background: rgba(132,204,22,0.08); }
.heat-green        { border-left-color: #16a34a; background: rgba(22,163,74,0.08); }
.heat-red          { border-left-color: #dc2626; background: rgba(220,38,38,0.08); }
</style>
