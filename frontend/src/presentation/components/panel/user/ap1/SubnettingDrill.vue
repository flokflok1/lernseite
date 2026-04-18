<template>
  <div class="sn-wrap">
    <!-- Header -->
    <div class="sn-header">
      <div>
        <h2 class="sn-title">📡 Subnetting Drill</h2>
        <p class="sn-sub">Berechne Netzadresse, Broadcast, Hosts und Subnetzmaske</p>
      </div>
      <LumiHint
        :context="`Subnetting-Aufgabe: IP ${task.ip}/${task.prefix}. Schwierigkeit: ${difficulty}. Aufgabe: Subnetzmaske, Netzwerkadresse, Broadcast und Anzahl nutzbarer Hosts berechnen.`"
        systemExtra="Erkläre Schritt für Schritt wie man aus dem Prefix die Subnetzmaske, Netzadresse und Broadcast berechnet. Nutze konkrete Zahlen aus der aktuellen Aufgabe."
      />
    </div>

    <!-- Difficulty -->
    <div class="sn-diff-bar">
      <button v-for="d in ['Leicht', 'Mittel', 'Schwer']" :key="d"
        class="sn-diff-btn"
        :class="difficulty === d ? 'sn-diff-active' : ''"
        @click="difficulty = d; generate()">
        {{ d }}
      </button>
    </div>

    <!-- Task Card -->
    <div class="sn-task-card">
      <div class="sn-task-ip">
        🖥️ {{ task.ip }}<span class="sn-task-prefix">/{{ task.prefix }}</span>
      </div>
      <div class="sn-task-hint">Berechne alle Angaben für dieses Netzwerk:</div>
    </div>

    <!-- 5-Schritte Guide -->
    <div class="sn-steps-toggle" @click="showSteps = !showSteps">
      {{ showSteps ? '▼' : '▶' }} 5-Schritte Rechenmethode
      <span class="sn-steps-toggle-hint">{{ showSteps ? 'zuklappen' : 'aufklappen' }}</span>
    </div>
    <div v-if="showSteps" class="sn-steps-box">
      <div class="sn-step">
        <div class="sn-step-num">1</div>
        <div class="sn-step-body">
          <div class="sn-step-title">Host-Bits = 32 − Präfix</div>
       2  <div class="sn-step-calc">32 − /{{ steps.prefix }} = <strong>{{ steps.hostBits }} Host-Bits</strong></div>
        </div>
      </div>
      <div class="sn-step">
        <div class="sn-step-num">2</div>
        <div class="sn-step-body">
          <div class="sn-step-title">Blockgröße = 2 ^ Host-Bits</div>
          <div class="sn-step-calc">2 ^ {{ steps.hostBits }} = <strong>{{ steps.blockSize }}</strong> &nbsp;<span class="sn-casio">Casio: 2 [x□] {{ steps.hostBits }} [=]</span></div>
        </div>
      </div>
      <div class="sn-step">
        <div class="sn-step-num">3</div>
  2    <div class="sn-step-body">
          <div class="sn-step-title">Subnetzmaske: {{ steps.activeOctetNum }}. Oktet → 256 − 2^{{ steps.activeOctetBits }}</div>
          <div class="sn-step-calc">256 − {{ steps.activeOctetBlock }} = {{ steps.activeOctetMaskVal }} → <strong>{{ steps.maskStr }}</strong></div>
        </div>
      </div>
      <div class="sn-step">
        <div class="sn-step-num">4</div>
        <div class="sn-step-body">
          <div class="sn-step-title">Nutzbare Hosts = Blockgröße − 2</div>
          <div class="sn-step-calc">{{ steps.blockSize }} − 2 = <strong>{{ steps.hosts }}</strong></div>
        </div>
   2   </div>
      <div class="sn-step">
        <div class="sn-step-num">5</div>
        <div class="sn-step-body">
          <div class="sn-step-title">Broadcast = Netzadresse + Blockgröße − 1</div>
          <div class="sn-step-calc">{{ steps.netAddr }} + {{ steps.blockSize }} − 1 = <strong>{{ steps.bcAddr }}</strong></div>
        </div>
      </div>
    </div>

    <!-- Quick Reference -->
    <div class="sn-reference">
      <div class="sn-ref-title">⚡ Schnell-Referenz:</div>
      <div class="sn-ref-table">
        <span v-for="r in prefixRef" :key="r.prefix" class="sn-ref-item" :class="r.prefix === task.prefix ? 'sn-ref-active' : ''">
          /{{ r.prefix }} = {{ r.hosts }}H
        </span>
      </div>
    </div>

    <!-- Input Grid -->
    <div class="sn-inputs">
      <div class="sn-input-group">
        <label class="sn-label">Subnetzmaske:</label>
        <input v-model="answers.mask" type="text" placeholder="z.B. 255.255.255.0"
          class="sn-input"
          :class="checked ? (results.mask ? 'sn-input-ok' : 'sn-input-err') : ''"
          :disabled="checked" />
        <div v-if="checked" class="sn-result-hint" :class="results.mask ? 'sn-ok' : 'sn-err'">
          {{ results.mask ? '✓ Richtig!' : `✗ Richtig: ${correctAnswers.mask}` }}
        </div>
      </div>
      <div class="sn-input-group">
        <label class="sn-label">Netzwerkadresse:</label>
        <input v-model="answers.network" type="text" placeholder="z.B. 192.168.1.0"
          class="sn-input"
          :class="checked ? (results.network ? 'sn-input-ok' : 'sn-input-err') : ''"
          :disabled="checked" />
        <div v-if="checked" class="sn-result-hint" :class="results.network ? 'sn-ok' : 'sn-err'">
          {{ results.network ? '✓ Richtig!' : `✗ Richtig: ${correctAnswers.network}` }}
        </div>
      </div>
      <div class="sn-input-group">
        <label class="sn-label">Broadcast-Adresse:</label>
        <input v-model="answers.broadcast" type="text" placeholder="z.B. 192.168.1.255"
          class="sn-input"
          :class="checked ? (results.broadcast ? 'sn-input-ok' : 'sn-input-err') : ''"
          :disabled="checked" />
        <div v-if="checked" class="sn-result-hint" :class="results.broadcast ? 'sn-ok' : 'sn-err'">
          {{ results.broadcast ? '✓ Richtig!' : `✗ Richtig: ${correctAnswers.broadcast}` }}
        </div>
      </div>
      <div class="sn-input-group">
        <label class="sn-label">Nutzbare Hosts:</label>
        <input v-model="answers.hosts" type="number" placeholder="z.B. 254"
          class="sn-input"
          :class="checked ? (results.hosts ? 'sn-input-ok' : 'sn-input-err') : ''"
          :disabled="checked" />
        <div v-if="checked" class="sn-result-hint" :class="results.hosts ? 'sn-ok' : 'sn-err'">
          {{ results.hosts ? '✓ Richtig!' : `✗ Richtig: ${correctAnswers.hosts}` }}
        </div>
      </div>
    </div>

    <!-- Score Bar -->
    <div v-if="checked" class="sn-score-bar">
      <div class="sn-score-fill" :style="{ width: (correctCount / 4 * 100) + '%', background: correctCount === 4 ? '#22c55e' : correctCount >= 2 ? '#f59e0b' : '#ef4444' }"></div>
    </div>
    <div v-if="checked" class="sn-score-label">
      {{ correctCount === 4 ? '🏆' : correctCount >= 2 ? '👍' : '📚' }}
      {{ correctCount }}/4 richtig
    </div>

    <!-- Actions -->
    <div class="sn-actions">
      <button v-if="!checked" class="sn-btn-check" @click="check">✅ Prüfen</button>
      <button class="sn-btn-next" @click="generate">🔄 Neue Aufgabe</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import LumiHint from '@/presentation/components/panel/user/ap1/LumiHint.vue'

const emit = defineEmits<{ score: [points: number] }>()

const difficulty = ref('Leicht')
const task = ref({ ip: '192.168.1.100', prefix: 24 })
const answers = reactive({ mask: '', network: '', broadcast: '', hosts: '' })
const correctAnswers = reactive({ mask: '', network: '', broadcast: '', hosts: '' })
const results = reactive({ mask: false, network: false, broadcast: false, hosts: false })
const checked = ref(false)
const showSteps = ref(false)

const correctCount = computed(() => Object.values(results).filter(Boolean).length)

const steps = computed(() => {
  const prefix = task.value.prefix
  const hostBits = 32 - prefix
  const blockSize = Math.pow(2, hostBits)
  const lastOctet = 256 - blockSize
  const hosts = Math.max(0, blockSize - 2)
  const maskStr = prefix >= 24 ? `255.255.255.${lastOctet}` : prefix >= 16 ? `255.255.${256 - Math.pow(2, 24-prefix)}.0` : `255.${256 - Math.pow(2, 16-prefix)}.0.0`
  const activeOctetBits = prefix >= 24 ? hostBits : prefix >= 16 ? 24 - prefix : 16 - prefix
  const activeOctetBlock = Math.pow(2, activeOctetBits)
  const activeOctetMaskVal = 256 - activeOctetBlock
  const activeOctetNum = prefix >= 24 ? 4 : prefix >= 16 ? 3 : 2
  const netAddr = correctAnswers.network || '?'
  const bcAddr = correctAnswers.broadcast || '?'
  return { prefix, hostBits, blockSize, lastOctet, hosts, maskStr: correctAnswers.mask || maskStr, netAddr, bcAddr, activeOctetBits, activeOctetBlock, activeOctetMaskVal, activeOctetNum }
})

const prefixRef = [
  { prefix: 24, hosts: 254 }, { prefix: 25, hosts: 126 }, { prefix: 26, hosts: 62 },
  { prefix: 27, hosts: 30 }, { prefix: 28, hosts: 14 }, { prefix: 29, hosts: 6 },
  { prefix: 30, hosts: 2 }, { prefix: 22, hosts: 1022 }, { prefix: 20, hosts: 4094 },
]

function prefixToMask(prefix: number): string {
  const mask = (0xFFFFFFFF << (32 - prefix)) >>> 0
  return [(mask >>> 24) & 0xFF, (mask >>> 16) & 0xFF, (mask >>> 8) & 0xFF, mask & 0xFF].join('.')
}

function ipToNum(ip: string): number {
  const parts = ip.split('.').map(Number)
  return ((parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]) >>> 0
}

function numToIp(num: number): string {
  return [(num >>> 24) & 0xFF, (num >>> 16) & 0xFF, (num >>> 8) & 0xFF, num & 0xFF].join('.')
}

function generate() {
  checked.value = false
  Object.assign(answers, { mask: '', network: '', broadcast: '', hosts: '' })

  const prefixes: Record<string, number[]> = {
    'Leicht': [8, 16, 24],
    'Mittel': [20, 22, 25, 26],
    'Schwer': [19, 21, 23, 27, 28, 29, 30],
  }
  const pList = prefixes[difficulty.value]
  const prefix = pList[Math.floor(Math.random() * pList.length)]
  const o1 = [10, 172, 192][Math.floor(Math.random() * 3)]
  const o2 = Math.floor(Math.random() * 256)
  const o3 = Math.floor(Math.random() * 256)
  const o4 = Math.floor(Math.random() * 254) + 1
  task.value = { ip: `${o1}.${o2}.${o3}.${o4}`, prefix }

  const maskNum = (0xFFFFFFFF << (32 - prefix)) >>> 0
  const ipNum = ipToNum(task.value.ip)
  const netNum = (ipNum & maskNum) >>> 0
  const bcNum = (netNum | (~maskNum >>> 0)) >>> 0
  const hosts = Math.pow(2, 32 - prefix) - 2

  correctAnswers.mask = prefixToMask(prefix)
  correctAnswers.network = numToIp(netNum)
  correctAnswers.broadcast = numToIp(bcNum)
  correctAnswers.hosts = String(Math.max(0, hosts))
}

function check() {
  checked.value = true
  results.mask = answers.mask.trim() === correctAnswers.mask
  results.network = answers.network.trim() === correctAnswers.network
  results.broadcast = answers.broadcast.trim() === correctAnswers.broadcast
  results.hosts = String(answers.hosts).trim() === correctAnswers.hosts
  emit('score', correctCount.value > 0 ? correctCount.value * 3 : 0)
}

generate()
</script>

<style scoped>
.sn-wrap { max-width: 800px; }

.sn-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 16px; gap: 12px;
}
.sn-title { font-size: 20px; font-weight: 800; color: var(--color-text-primary); margin: 0 0 4px; }
.sn-sub { font-size: 13px; color: var(--color-text-secondary); margin: 0; }

.sn-diff-bar { display: flex; gap: 8px; margin-bottom: 16px; }
.sn-diff-btn {
  padding: 6px 18px; border-radius: 20px; font-size: 13px; font-weight: 600;
  border: 1px solid var(--color-border); background: var(--color-surface);
  color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
}
.sn-diff-btn:hover { border-color: #0ea5e9; color: #38bdf8; }
.sn-diff-active { background: rgba(14,165,233,0.15) !important; border-color: #0ea5e9 !important; color: #38bdf8 !important; }

.sn-task-card {
  background: linear-gradient(135deg, rgba(14,165,233,0.12), rgba(59,130,246,0.08));
  border: 2px solid rgba(14,165,233,0.4); border-radius: 14px;
  padding: 20px 24px; margin-bottom: 14px; text-align: center;
}
.sn-task-ip { font-size: 32px; font-weight: 900; color: #38bdf8; font-family: monospace; margin-bottom: 6px; }
.sn-task-prefix { color: #93c5fd; }
.sn-task-hint { font-size: 13px; color: var(--color-text-secondary); }

.sn-reference {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 10px; padding: 12px 14px; margin-bottom: 16px;
}
.sn-ref-title { font-size: 11px; font-weight: 700; color: var(--color-text-secondary); text-transform: uppercase; margin-bottom: 8px; }
.sn-ref-table { display: flex; flex-wrap: wrap; gap: 6px; }
.sn-ref-item {
  padding: 3px 10px; border-radius: 20px; font-size: 12px; font-family: monospace; font-weight: 600;
  background: var(--color-surface-secondary, rgba(255,255,255,0.05));
  border: 1px solid var(--color-border); color: var(--color-text-secondary);
  transition: all 0.15s;
}
.sn-ref-active { background: rgba(14,165,233,0.2) !important; border-color: #0ea5e9 !important; color: #38bdf8 !important; transform: scale(1.1); }

.sn-inputs { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
@media (max-width: 600px) { .sn-inputs { grid-template-columns: 1fr; } }

.sn-input-group { display: flex; flex-direction: column; gap: 4px; }
.sn-label { font-size: 12px; font-weight: 700; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.4px; }
.sn-input {
  padding: 11px 14px; border: 2px solid var(--color-border); border-radius: 8px;
  background: var(--color-surface); color: var(--color-text-primary); font-size: 14px;
  font-family: monospace; outline: none; transition: border-color 0.15s;
}
.sn-input:focus { border-color: #0ea5e9; }
.sn-input:disabled { opacity: 0.7; }
.sn-input-ok { border-color: #22c55e !important; background: rgba(34,197,94,0.05) !important; }
.sn-input-err { border-color: #ef4444 !important; background: rgba(239,68,68,0.05) !important; }
.sn-result-hint { font-size: 12px; font-weight: 600; font-family: monospace; }
.sn-ok { color: #4ade80; }
.sn-err { color: #f87171; }

.sn-score-bar { height: 6px; background: var(--color-border); border-radius: 3px; margin-bottom: 4px; }
.sn-score-fill { height: 100%; border-radius: 3px; transition: width 0.4s; }
.sn-score-label { font-size: 14px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 14px; }

.sn-actions { display: flex; gap: 10px; }
.sn-btn-check {
  padding: 9px 22px; background: #16a34a; color: white; border: none;
  border-radius: 8px; font-weight: 700; font-size: 14px; cursor: pointer; transition: all 0.15s;
}
.sn-btn-check:hover { background: #15803d; }
.sn-btn-next {
  padding: 9px 22px; background: rgba(14,165,233,0.15); color: #38bdf8;
  border: 1px solid rgba(14,165,233,0.4); border-radius: 8px; font-weight: 600;
  font-size: 14px; cursor: pointer; transition: all 0.15s;
}
.sn-btn-next:hover { background: rgba(14,165,233,0.25); }

.sn-steps-toggle {
  cursor: pointer; padding: 10px 14px; margin-bottom: 10px;
  background: rgba(14,165,233,0.08); border: 1px solid rgba(14,165,233,0.3);
  border-radius: 10px; font-size: 13px; font-weight: 700; color: #38bdf8;
  user-select: none; transition: background 0.15s;
}
.sn-steps-toggle:hover { background: rgba(14,165,233,0.15); }
.sn-steps-toggle-hint { font-size: 11px; font-weight: 400; color: var(--color-text-secondary); margin-left: 8px; }

.sn-steps-box {
  background: var(--color-surface); border: 1px solid rgba(14,165,233,0.3);
  border-radius: 10px; padding: 14px 16px; margin-bottom: 14px;
  display: flex; flex-direction: column; gap: 12px;
}
.sn-step { display: flex; align-items: flex-start; gap: 12px; }
.sn-step-num {
  width: 28px; height: 28px; border-radius: 50%; background: rgba(14,165,233,0.2);
  border: 2px solid #0ea5e9; color: #38bdf8; font-weight: 900; font-size: 13px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.sn-step-body { flex: 1; }
.sn-step-title { font-size: 12px; color: var(--color-text-secondary); margin-bottom: 3px; }
.sn-step-calc { font-size: 14px; font-family: monospace; color: var(--color-text-primary); }
.sn-step-calc strong { color: #4ade80; font-size: 15px; }
.sn-casio {
  font-size: 11px; background: rgba(251,191,36,0.15); border: 1px solid rgba(251,191,36,0.4);
  color: #fbbf24; padding: 1px 7px; border-radius: 6px; font-family: sans-serif; font-weight: 600;
}
</style>
