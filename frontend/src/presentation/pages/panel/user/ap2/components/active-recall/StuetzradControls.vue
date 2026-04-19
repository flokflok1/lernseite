<script setup lang="ts">
import { computed } from 'vue'
import type { ItemSkillState, UserPreferences } from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'

interface Props {
  modelValue: boolean          // Stützrad ON?
  skill: ItemSkillState | null
  prefs: UserPreferences | null
  disabled?: boolean
}
const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [v: boolean]
}>()

const target = computed(() => {
  return props.skill?.effective_target
    ?? props.prefs?.base_target
    ?? 3
})

const progress = computed(() => {
  const done = props.skill?.kopf_serie_count ?? 0
  return { done, total: target.value }
})

const progressPct = computed(() => {
  if (!target.value) return 0
  return Math.min(100, Math.round((progress.value.done / target.value) * 100))
})

function toggle() {
  if (props.disabled) return
  emit('update:modelValue', !props.modelValue)
}
</script>

<template>
  <div class="stuetzrad-controls">
    <div class="sc-left">
      <button
        type="button"
        class="sc-toggle"
        :class="{ 'sc-toggle--on': modelValue, 'sc-toggle--disabled': disabled }"
        :aria-pressed="modelValue"
        @click="toggle"
      >
        <span class="sc-toggle-knob"></span>
        <span class="sc-toggle-label">
          🪄 Stützrad {{ modelValue ? 'AN' : 'aus' }}
        </span>
      </button>
      <span class="sc-hint">
        <template v-if="modelValue">
          Musterlösung wird nach dem Abschicken gezeigt — Kopf-Serie unberührt.
        </template>
        <template v-else>
          Ohne Stützrad — Treffer zählt für Kopf-Serie.
        </template>
      </span>
    </div>

    <div class="sc-right">
      <div class="sc-badge" :class="{ 'sc-badge--recovery': skill?.is_in_recovery }">
        <span class="sc-badge-title">Kopf-Serie</span>
        <span class="sc-badge-count">
          {{ progress.done }} / {{ progress.total }}
        </span>
        <div class="sc-badge-bar">
          <div class="sc-badge-fill" :style="{ width: progressPct + '%' }" />
        </div>
      </div>
      <div v-if="skill?.is_in_recovery" class="sc-recovery">
        ⚠️ Recovery — Ziel auf {{ target }} erhöht
      </div>
      <div v-else-if="skill?.is_mastered" class="sc-mastered">
        ✅ Item sitzt
      </div>
    </div>
  </div>
</template>

<style scoped>
.stuetzrad-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  padding: 0.7rem 0.9rem;
  background: rgba(0,0,0,0.2);
  border: 1px solid var(--color-border, #334155);
  border-radius: 8px;
  margin-bottom: 0.8rem;
  flex-wrap: wrap;
}

.sc-left { display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap; }

.sc-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.6rem 0.3rem 0.3rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid #475569;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  color: #cbd5e1;
  transition: all 0.15s;
}
.sc-toggle:hover:not(.sc-toggle--disabled) {
  border-color: #3b82f6;
}
.sc-toggle--on {
  background: rgba(59,130,246,0.2);
  border-color: #3b82f6;
  color: #e0e7ff;
}
.sc-toggle--disabled { opacity: 0.5; cursor: not-allowed; }

.sc-toggle-knob {
  width: 18px; height: 18px;
  border-radius: 50%;
  background: #64748b;
  transition: background 0.15s;
}
.sc-toggle--on .sc-toggle-knob { background: #60a5fa; }

.sc-hint {
  font-size: 0.78rem;
  color: #94a3b8;
  max-width: 320px;
  line-height: 1.3;
}

.sc-right { display: flex; flex-direction: column; gap: 0.3rem; align-items: flex-end; }

.sc-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.6rem;
  background: rgba(22,163,74,0.1);
  border: 1px solid rgba(22,163,74,0.4);
  border-radius: 6px;
  font-size: 0.8rem;
  color: #cbd5e1;
}
.sc-badge--recovery {
  background: rgba(245,158,11,0.1);
  border-color: rgba(245,158,11,0.4);
}

.sc-badge-title { color: #94a3b8; }
.sc-badge-count {
  font-weight: 700;
  color: #f1f5f9;
  min-width: 48px;
  text-align: center;
}

.sc-badge-bar {
  width: 80px;
  height: 6px;
  background: rgba(255,255,255,0.08);
  border-radius: 3px;
  overflow: hidden;
}
.sc-badge-fill {
  height: 100%;
  background: #16a34a;
  transition: width 0.3s;
}
.sc-badge--recovery .sc-badge-fill { background: #f59e0b; }

.sc-recovery { font-size: 0.72rem; color: #fbbf24; }
.sc-mastered { font-size: 0.72rem; color: #86efac; }
</style>
