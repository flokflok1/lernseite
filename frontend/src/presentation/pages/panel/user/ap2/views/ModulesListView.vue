<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  listModules,
  type ModuleCard,
  type ModuleStatus,
} from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'

const router = useRouter()
const modules = ref<ModuleCard[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

const STATUS_META: Record<ModuleStatus, { label: string; color: string; icon: string }> = {
  locked:         { label: 'Gesperrt',          color: '#64748b', icon: '🔒' },
  available:      { label: 'Verfügbar',         color: '#3b82f6', icon: '▶️' },
  learning:       { label: 'In Arbeit',         color: '#f59e0b', icon: '📚' },
  pending_recall: { label: 'Same-Day-Recall',   color: '#a855f7', icon: '🟡' },
  mastered:       { label: 'Mastered',          color: '#16a34a', icon: '✅' },
  review_failed:  { label: 'Refresh nötig',     color: '#dc2626', icon: '🔄' },
}

async function refresh() {
  loading.value = true
  error.value = null
  try {
    modules.value = await listModules()
  } catch {
    error.value = 'Modul-Liste konnte nicht geladen werden.'
  } finally {
    loading.value = false
  }
}

function open(m: ModuleCard) {
  if (m.progress?.status === 'locked') return
  router.push(`/ap2-training/modules/${m.slug}`)
}

function statusOf(m: ModuleCard): ModuleStatus {
  return (m.progress?.status as ModuleStatus) || 'available'
}

function recallCountdown(p: ModuleCard['progress']): string | null {
  if (!p?.same_day_recall_due_at) return null
  const due = new Date(p.same_day_recall_due_at).getTime()
  const diff = due - Date.now()
  if (diff <= 0) return 'jetzt fällig'
  const mins = Math.round(diff / 60000)
  if (mins < 60) return `in ${mins} min`
  return `in ${Math.round(mins / 60)} h`
}

function nextSpotcheck(p: ModuleCard['progress']): string | null {
  if (!p?.next_spotcheck_at) return null
  const due = new Date(p.next_spotcheck_at).getTime()
  const diff = due - Date.now()
  if (diff <= 0) return 'jetzt fällig'
  const days = Math.round(diff / 86400000)
  if (days < 1) {
    const hrs = Math.round(diff / 3600000)
    return `in ${hrs} h`
  }
  return `in ${days} Tag${days > 1 ? 'en' : ''}`
}

const sortedModules = computed(() => {
  // Mastered ans Ende, dann learning oben, dann verfügbar
  const order: Record<ModuleStatus, number> = {
    learning: 0,
    pending_recall: 1,
    review_failed: 2,
    available: 3,
    locked: 4,
    mastered: 5,
  }
  return [...modules.value].sort((a, b) => {
    const sa = order[statusOf(a)]
    const sb = order[statusOf(b)]
    if (sa !== sb) return sa - sb
    return a.sort_order - b.sort_order
  })
})

onMounted(refresh)
</script>

<template>
  <div class="mods">
    <header class="mods-head">
      <div>
        <h2>📚 Diagramm-Module</h2>
        <p class="mods-sub">
          Strukturiert, mit Mastery-Gate (3× ≥80% + Same-Day-Recall) — nächste Module
          werden erst freigeschaltet wenn das aktuelle wirklich sitzt.
        </p>
      </div>
      <button class="mods-refresh" :disabled="loading" @click="refresh">
        ↻ Aktualisieren
      </button>
    </header>

    <div v-if="loading && !modules.length" class="mods-loading">Lade Module…</div>

    <div v-if="error" class="mods-error">⚠️ {{ error }}</div>

    <div v-if="!loading && !modules.length && !error" class="mods-empty">
      Noch keine Module verfügbar. Schau später wieder rein.
    </div>

    <div class="mods-grid">
      <article
        v-for="m in sortedModules"
        :key="m.module_id"
        class="mod-card"
        :class="`mod-status-${statusOf(m)}`"
        @click="open(m)"
        :role="statusOf(m) === 'locked' ? undefined : 'button'"
        :tabindex="statusOf(m) === 'locked' ? -1 : 0"
        @keydown.enter="open(m)"
      >
        <header class="mod-card-head">
          <span class="mod-status-badge" :style="{ background: STATUS_META[statusOf(m)].color }">
            {{ STATUS_META[statusOf(m)].icon }} {{ STATUS_META[statusOf(m)].label }}
          </span>
          <span class="mod-meta">⏱ {{ m.estimated_min }} min</span>
        </header>

        <h3 class="mod-name">{{ m.name_de }}</h3>
        <p v-if="m.description" class="mod-desc">{{ m.description }}</p>

        <footer class="mod-footer">
          <div v-if="statusOf(m) === 'learning' && m.progress" class="mod-streak">
            Streak: <strong>{{ m.progress.streak_count }}/3</strong>
          </div>
          <div v-else-if="statusOf(m) === 'pending_recall' && m.progress" class="mod-recall">
            🟡 Recall {{ recallCountdown(m.progress) }}
          </div>
          <div v-else-if="statusOf(m) === 'mastered' && m.progress" class="mod-spot">
            ✓ Nächster Check {{ nextSpotcheck(m.progress) || 'demnächst' }}
          </div>
          <div v-else-if="statusOf(m) === 'locked'" class="mod-locked-hint">
            <template v-if="m.prerequisite_slugs.length">
              Voraussetzung: {{ m.prerequisite_slugs.join(', ') }}
            </template>
            <template v-else>
              Bald verfügbar
            </template>
          </div>
          <div v-else class="mod-cta">▶ Starten</div>
        </footer>
      </article>
    </div>
  </div>
</template>

<style scoped>
.mods {
  max-width: 980px;
  margin: 0 auto;
  padding: 1rem;
}

.mods-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.mods-head h2 { margin: 0 0 0.2rem 0; color: #f1f5f9; }
.mods-sub { margin: 0; color: #94a3b8; font-size: 0.88rem; line-height: 1.4; }

.mods-refresh {
  padding: 0.4rem 0.8rem;
  background: transparent;
  color: #94a3b8;
  border: 1px solid #475569;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}
.mods-refresh:hover:not(:disabled) { background: rgba(255,255,255,0.04); color: #cbd5e1; }

.mods-loading,
.mods-empty {
  padding: 3rem;
  text-align: center;
  color: #94a3b8;
}

.mods-error {
  padding: 1rem;
  background: #7f1d1d33;
  border-left: 3px solid #dc2626;
  color: #fecaca;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.mods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.mod-card {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-left: 4px solid #475569;
  border-radius: 10px;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.15s, border-color 0.15s, background 0.15s;
  outline: none;
}

.mod-card:hover:not(.mod-status-locked),
.mod-card:focus-visible:not(.mod-status-locked) {
  transform: translateY(-2px);
  background: rgba(255,255,255,0.03);
}

.mod-status-locked {
  opacity: 0.55;
  cursor: not-allowed;
  border-left-color: #64748b;
}
.mod-status-available     { border-left-color: #3b82f6; }
.mod-status-learning      { border-left-color: #f59e0b; }
.mod-status-pending_recall { border-left-color: #a855f7; }
.mod-status-mastered      { border-left-color: #16a34a; }
.mod-status-review_failed { border-left-color: #dc2626; }

.mod-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.6rem;
}

.mod-status-badge {
  padding: 0.18rem 0.55rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: #fff;
  border-radius: 999px;
}

.mod-meta {
  font-size: 0.75rem;
  color: #94a3b8;
}

.mod-name {
  margin: 0 0 0.3rem 0;
  font-size: 1.02rem;
  color: #f1f5f9;
  line-height: 1.3;
}

.mod-desc {
  margin: 0 0 0.6rem 0;
  font-size: 0.82rem;
  color: #cbd5e1;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.mod-footer {
  margin-top: 0.6rem;
  padding-top: 0.6rem;
  border-top: 1px dashed #334155;
  font-size: 0.82rem;
  color: #cbd5e1;
}

.mod-streak strong { color: #fbbf24; }
.mod-recall { color: #d8b4fe; }
.mod-spot { color: #86efac; }
.mod-locked-hint { color: #94a3b8; font-size: 0.78rem; font-style: italic; }
.mod-cta { color: #60a5fa; font-weight: 600; }
</style>
