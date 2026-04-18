<template>
  <div class="ap2-phase-nav">
    <div
      v-for="(phase, idx) in phases"
      :key="phase.key"
      class="ap2-phase-step"
      :class="{
        'ap2-phase-active': phase.key === current,
        'ap2-phase-done': isDoneIdx(idx),
      }"
    >
      <div class="ap2-phase-num">{{ idx + 1 }}</div>
      <div class="ap2-phase-label">{{ t(phase.labelKey) }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { StudyPhase } from '../../composables'

interface Props { current: StudyPhase }
const props = defineProps<Props>()
const { t } = useI18n()

const phases: { key: StudyPhase; labelKey: string }[] = [
  { key: 'blurt',       labelKey: 'ap2Trainer.study.phases.blurt' },
  { key: 'cued',        labelKey: 'ap2Trainer.study.phases.cued' },
  { key: 'application', labelKey: 'ap2Trainer.study.phases.application' },
  { key: 'done',        labelKey: 'ap2Trainer.study.phases.done' },
]

const currentIdx = computed(() => phases.findIndex(p => p.key === props.current))
function isDoneIdx(idx: number) { return idx < currentIdx.value }
</script>

<style scoped>
.ap2-phase-nav { display: flex; gap: 8px; padding: 12px 16px; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 12px; margin-bottom: 16px; }
.ap2-phase-step { flex: 1; display: flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 8px; background: rgba(255, 255, 255, 0.03); color: #64748b; font-size: 12px; font-weight: 600; }
.ap2-phase-active { background: rgba(99, 102, 241, 0.18); color: #a5b4fc; box-shadow: inset 0 0 0 1px #4338ca; }
.ap2-phase-done { background: rgba(34, 197, 94, 0.12); color: #4ade80; }
.ap2-phase-num { width: 22px; height: 22px; border-radius: 50%; background: rgba(255, 255, 255, 0.08); display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }
.ap2-phase-active .ap2-phase-num { background: #4338ca; color: #fff; }
.ap2-phase-done .ap2-phase-num { background: #16a34a; color: #fff; }
</style>
