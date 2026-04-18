<template>
  <div class="ap1-page">
    <!-- Hero Header -->
    <div class="ap1-hero">
      <div class="ap1-hero-left">
        <div class="ap1-hero-badge">🎓 FISI · IHK Ulm · Baden-Württemberg</div>
        <h1 class="ap1-hero-title">AP1 Praxis-Training</h1>
        <p class="ap1-hero-sub">Echte BW-Prüfungsfragen · Interaktiv · KI-gestützt</p>
      </div>
      <div class="ap1-countdown" :class="daysLeft <= 7 ? 'ap1-countdown-urgent' : ''">
        <div class="ap1-countdown-num">{{ daysLeft }}</div>
        <div class="ap1-countdown-label">Tage bis AP1</div>
        <div class="ap1-countdown-date">14.04.2026</div>
      </div>
    </div>

    <!-- Stats Bar -->
    <div class="ap1-stats">
      <div class="ap1-stat ap1-stat-gold">
        <span class="ap1-stat-icon">🏆</span>
        <span class="ap1-stat-val">{{ totalScore }}</span>
        <span class="ap1-stat-label">Punkte</span>
      </div>
      <div class="ap1-stat ap1-stat-fire">
        <span class="ap1-stat-icon">🔥</span>
        <span class="ap1-stat-val">{{ streak }}</span>
        <span class="ap1-stat-label">Streak</span>
      </div>
      <div class="ap1-stat ap1-stat-green">
        <span class="ap1-stat-icon">✅</span>
        <span class="ap1-stat-val">{{ solvedCount }}</span>
        <span class="ap1-stat-label">Gelöst</span>
      </div>
      <div class="ap1-stat ap1-stat-blue">
        <span class="ap1-stat-icon">📚</span>
        <span class="ap1-stat-val">{{ Math.round(totalScore / 10) || 0 }}</span>
        <span class="ap1-stat-label">Level</span>
      </div>
    </div>

    <!-- Module Grid Navigation -->
    <div class="ap1-modules">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="ap1-module-btn"
        :class="activeTab === tab.id ? 'ap1-module-active' : ''"
      >
        <span class="ap1-module-icon">{{ tab.icon }}</span>
        <span class="ap1-module-label">{{ tab.label }}</span>
      </button>
    </div>

    <!-- Module Content -->
    <div class="ap1-content">
      <OSIDragDrop    v-if="activeTab === 'osi'"      @score="onScore" />
      <FreitextTrainer v-if="activeTab === 'freitext'" @score="onScore" />
      <SubnettingDrill v-if="activeTab === 'subnet'"  @score="onScore" />
      <SQLFreitext    v-if="activeTab === 'sql'"      @score="onScore" />
      <SecurityTrainer v-if="activeTab === 'security'" @score="onScore" />
      <CalcTrainer    v-if="activeTab === 'calc'"     @score="onScore" />
      <Formelsammlung  v-if="activeTab === 'formulas'" />
      <AP1TutorChat   v-if="activeTab === 'tutor'" />
      <CasioTrainer   v-if="activeTab === 'casio'"   @score="onScore" />
      <IPv6Trainer    v-if="activeTab === 'ipv6'"     @score="onScore" />
      <FachbegriffeTrainer v-if="activeTab === 'begriffe'" @score="onScore" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import OSIDragDrop from '@/presentation/components/panel/user/ap1/OSIDragDrop.vue'
import FreitextTrainer from '@/presentation/components/panel/user/ap1/FreitextTrainer.vue'
import SubnettingDrill from '@/presentation/components/panel/user/ap1/SubnettingDrill.vue'
import SQLFreitext from '@/presentation/components/panel/user/ap1/SQLFreitext.vue'
import SecurityTrainer from '@/presentation/components/panel/user/ap1/SecurityTrainer.vue'
import CalcTrainer from '@/presentation/components/panel/user/ap1/CalcTrainer.vue'
import Formelsammlung from '@/presentation/components/panel/user/ap1/Formelsammlung.vue'
import AP1TutorChat from '@/presentation/components/panel/user/ap1/AP1TutorChat.vue'
import CasioTrainer from '@/presentation/components/panel/user/ap1/CasioTrainer.vue'
import IPv6Trainer from '@/presentation/components/panel/user/ap1/IPv6Trainer.vue'
import FachbegriffeTrainer from '@/presentation/components/panel/user/ap1/FachbegriffeTrainer.vue'

const activeTab = ref('osi')
const totalScore = ref(0)
const streak = ref(0)
const solvedCount = ref(0)

const tabs = [
  { id: 'osi',      icon: '🌐', label: 'OSI-Modell' },
  { id: 'freitext', icon: '📝', label: 'Freitext BW' },
  { id: 'subnet',   icon: '📡', label: 'Subnetting' },
  { id: 'sql',      icon: '🗄️', label: 'SQL' },
  { id: 'security', icon: '🔒', label: 'IT-Sicherheit' },
  { id: 'calc',     icon: '💰', label: 'Kalkulation' },
  { id: 'formulas', icon: '📐', label: 'Formeln' },
  { id: 'tutor',    icon: '🤖', label: 'KI-Tutor' },
  { id: 'casio',    icon: '🔢', label: 'Casio Üben' },
  { id: 'ipv6',     icon: '🌐', label: 'IPv6' },
  { id: 'begriffe', icon: '🧠', label: 'Fachbegriffe' },
]

const daysLeft = computed(() => {
  const exam = new Date('2026-04-14')
  const now = new Date()
  return Math.max(0, Math.ceil((exam.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)))
})

const onScore = (points: number) => {
  totalScore.value += points
  if (points > 0) { streak.value++; solvedCount.value++ }
  else streak.value = 0
}
</script>

<style scoped>
.ap1-page { max-width: 1200px; }

/* Hero */
.ap1-hero {
  display: flex; justify-content: space-between; align-items: center;
  background: linear-gradient(135deg, #1e3a5f 0%, #1e1b4b 50%, #2d1b69 100%);
  border: 1px solid #3730a3; border-radius: 16px; padding: 20px 28px; margin-bottom: 16px;
}
.ap1-hero-badge {
  display: inline-block; padding: 3px 10px; border-radius: 20px;
  background: rgba(99,102,241,0.2); color: #a5b4fc; font-size: 11px;
  font-weight: 600; letter-spacing: 0.5px; margin-bottom: 8px;
}
.ap1-hero-title { font-size: 26px; font-weight: 800; color: white; margin: 0 0 4px; }
.ap1-hero-sub { color: #94a3b8; font-size: 13px; margin: 0; }
.ap1-countdown {
  text-align: center; background: rgba(99,102,241,0.15); border: 1px solid #4338ca;
  border-radius: 12px; padding: 12px 20px; min-width: 100px;
}
.ap1-countdown-urgent { background: rgba(239,68,68,0.15); border-color: #dc2626; }
.ap1-countdown-num { font-size: 40px; font-weight: 800; color: #818cf8; line-height: 1; }
.ap1-countdown-urgent .ap1-countdown-num { color: #f87171; }
.ap1-countdown-label { font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
.ap1-countdown-date { font-size: 11px; color: #64748b; margin-top: 2px; }

/* Stats */
.ap1-stats {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 16px;
}
.ap1-stat {
  display: flex; flex-direction: column; align-items: center; padding: 12px 8px;
  border-radius: 12px; border: 1px solid; gap: 2px;
}
.ap1-stat-icon { font-size: 22px; }
.ap1-stat-val { font-size: 24px; font-weight: 800; line-height: 1.2; }
.ap1-stat-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.ap1-stat-gold { background: rgba(251,191,36,0.1); border-color: #d97706; }
.ap1-stat-gold .ap1-stat-val { color: #fbbf24; }
.ap1-stat-gold .ap1-stat-label { color: #92400e; }
.ap1-stat-fire { background: rgba(249,115,22,0.1); border-color: #ea580c; }
.ap1-stat-fire .ap1-stat-val { color: #fb923c; }
.ap1-stat-fire .ap1-stat-label { color: #9a3412; }
.ap1-stat-green { background: rgba(34,197,94,0.1); border-color: #16a34a; }
.ap1-stat-green .ap1-stat-val { color: #4ade80; }
.ap1-stat-green .ap1-stat-label { color: #14532d; }
.ap1-stat-blue { background: rgba(59,130,246,0.1); border-color: #2563eb; }
.ap1-stat-blue .ap1-stat-val { color: #60a5fa; }
.ap1-stat-blue .ap1-stat-label { color: #1e3a5f; }

/* Module Grid */
.ap1-modules {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 20px;
}
@media (max-width: 900px) { .ap1-modules { grid-template-columns: repeat(3, 1fr); } }
.ap1-module-btn {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 10px 8px; border-radius: 10px; border: 1px solid var(--color-border);
  background: var(--color-surface); color: var(--color-text-secondary);
  cursor: pointer; transition: all 0.15s; font-size: 12px; font-weight: 600;
}
.ap1-module-btn:hover {
  border-color: #6366f1; background: rgba(99,102,241,0.1); color: #a5b4fc;
  transform: translateY(-1px);
}
.ap1-module-active {
  border-color: #6366f1 !important; background: rgba(99,102,241,0.2) !important;
  color: #a5b4fc !important; box-shadow: 0 0 0 2px rgba(99,102,241,0.3);
}
.ap1-module-icon { font-size: 22px; }
.ap1-module-label { line-height: 1.2; text-align: center; }

.ap1-content { min-height: 400px; }
</style>
