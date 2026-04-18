<template>
  <div class="ap2-anl">
    <header class="ap2-anl-header">
      <div>
        <h2>{{ t('ap2Trainer.anlagen.title') }}</h2>
        <p class="ap2-anl-sub">{{ t('ap2Trainer.anlagen.subtitle') }}</p>
      </div>
    </header>

    <div v-if="loading" class="ap2-anl-loading">
      {{ t('ap2Trainer.review.loading') }}
    </div>

    <div v-else-if="anlagen.length === 0" class="ap2-anl-empty">
      <div class="ap2-anl-empty-icon">📎</div>
      <h3>{{ t('ap2Trainer.anlagen.emptyTitle') }}</h3>
      <p>{{ t('ap2Trainer.anlagen.emptySubtitle') }}</p>
      <div class="ap2-anl-hint">
        <strong>{{ t('ap2Trainer.anlagen.emptyHintTitle') }}</strong>
        <ul>
          <li>{{ t('ap2Trainer.anlagen.emptyHint1') }}</li>
          <li>{{ t('ap2Trainer.anlagen.emptyHint2') }}</li>
          <li>{{ t('ap2Trainer.anlagen.emptyHint3') }}</li>
        </ul>
      </div>
    </div>

    <div v-else class="ap2-anl-grid">
      <article
        v-for="a in anlagen"
        :key="a.anlage_id"
        class="ap2-anl-card"
        @click="selectedAnlage = a.anlage_id === selectedAnlage ? null : a.anlage_id"
      >
        <div class="ap2-anl-card-header">
          <span class="ap2-anl-type">{{ anlageTypeLabel(a.anlage_type) }}</span>
          <span v-if="a.source_exam" class="ap2-anl-source">{{ a.source_exam }}</span>
        </div>
        <h4 class="ap2-anl-card-title">{{ a.title }}</h4>
        <p v-if="a.anlage_number" class="ap2-anl-meta">
          {{ t('ap2Trainer.anlagen.anlageNr', { n: a.anlage_number }) }}
          <span v-if="a.has_hotspots" class="ap2-anl-hotspots">
            · {{ t('ap2Trainer.anlagen.withHotspots') }}
          </span>
        </p>
        <img
          v-if="selectedAnlage === a.anlage_id && a.image_url"
          :src="a.image_url"
          :alt="a.title"
          class="ap2-anl-preview"
        />
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { listAp2Anlagen, type Ap2Anlage } from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

const anlagen = ref<Ap2Anlage[]>([])
const loading = ref(false)
const selectedAnlage = ref<string | null>(null)

const anlageTypeLabels: Record<string, string> = {
  'network-topology': 'Netzplan',
  'datasheet': 'Datenblatt',
  'table': 'Tabelle',
  'er-diagram': 'ER-Modell',
  'rack-layout': 'Rack',
  'process-diagram': 'Prozess',
  'epk-diagram': 'EPK',
  'state-diagram': 'Zustand',
  'sequence-diagram': 'Sequenz',
  'image': 'Bild',
}
function anlageTypeLabel(type: string) {
  return anlageTypeLabels[type] ?? type
}

async function load() {
  loading.value = true
  try {
    const res = await listAp2Anlagen()
    anlagen.value = res.anlagen
  } catch (e) {
    console.warn('[AP2] load anlagen failed:', e)
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<style scoped>
.ap2-anl { display: flex; flex-direction: column; gap: 16px; }
.ap2-anl-header h2 { color: var(--color-text-primary, #fff); margin: 0 0 4px; font-size: 22px; }
.ap2-anl-sub { color: #94a3b8; margin: 0; font-size: 13px; }
.ap2-anl-loading { padding: 48px; text-align: center; color: #94a3b8; }
.ap2-anl-empty { text-align: center; padding: 48px 24px; background: var(--color-surface, #1e293b); border: 1px dashed var(--color-border, #334155); border-radius: 14px; }
.ap2-anl-empty-icon { font-size: 48px; margin-bottom: 12px; }
.ap2-anl-empty h3 { color: var(--color-text-primary, #fff); margin: 0 0 8px; }
.ap2-anl-empty p { color: #94a3b8; margin: 0 0 20px; }
.ap2-anl-hint { max-width: 500px; margin: 0 auto; padding: 16px; background: rgba(99, 102, 241, 0.08); border-left: 3px solid #4338ca; border-radius: 6px; text-align: left; }
.ap2-anl-hint strong { display: block; color: #a5b4fc; margin-bottom: 8px; font-size: 13px; }
.ap2-anl-hint ul { margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 12px; line-height: 1.6; }
.ap2-anl-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.ap2-anl-card { padding: 14px; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 12px; cursor: pointer; transition: all .15s; }
.ap2-anl-card:hover { border-color: #4338ca; transform: translateY(-1px); }
.ap2-anl-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.ap2-anl-type { font-size: 10px; font-weight: 700; text-transform: uppercase; color: #a5b4fc; padding: 2px 6px; background: rgba(99, 102, 241, 0.15); border-radius: 4px; }
.ap2-anl-source { font-size: 10px; font-family: ui-monospace, monospace; color: #94a3b8; }
.ap2-anl-card-title { color: #fff; font-size: 14px; font-weight: 600; margin: 0 0 6px; line-height: 1.3; }
.ap2-anl-meta { font-size: 11px; color: #94a3b8; margin: 0; }
.ap2-anl-hotspots { color: #fbbf24; font-weight: 600; }
.ap2-anl-preview { width: 100%; margin-top: 12px; border-radius: 6px; border: 1px solid var(--color-border, #334155); }
</style>
