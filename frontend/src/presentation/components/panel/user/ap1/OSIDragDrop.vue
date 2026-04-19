<template>
  <div class="osi-wrap">
    <!-- Header -->
    <div class="osi-header">
      <div>
        <h2 class="osi-title">🌐 OSI-Modell Drag &amp; Drop</h2>
        <p class="osi-sub">Ziehe die Protokolle und Geräte auf die richtige OSI-Schicht!</p>
      </div>
      <LumiHint
        :context="`OSI-Modell Drag & Drop Übung, Schwierigkeit: ${difficulty}. Aktuell zu platzieren: ${shuffledItems.filter((_,i) => !placed[i]).map(i => i.text).slice(0,5).join(', ')}...`"
        systemExtra="Erkläre OSI-Schichten mit konkreten Protokollen als Eselsbrücken."
      />
    </div>

    <!-- Difficulty -->
    <div class="osi-diff-bar">
      <button v-for="d in difficulties" :key="d.key"
        class="osi-diff-btn"
        :class="difficulty === d.key ? 'osi-diff-active' : ''"
        @click="changeDifficulty(d.key)">
        {{ d.label }} <span class="osi-diff-count">{{ d.count }}</span>
      </button>
    </div>

    <!-- Items Pool -->
    <div class="osi-pool">
      <div class="osi-pool-label">📦 Noch zuzuordnen:</div>
      <div class="osi-pool-items">
        <div v-for="(item, idx) in shuffledItems" :key="idx"
          class="osi-chip"
          :class="placed[idx] ? 'osi-chip-done' : 'osi-chip-active'"
          :draggable="!placed[idx]"
          @dragstart="onDragStart($event, idx)">
          {{ item.text }}
        </div>
      </div>
    </div>

    <!-- OSI Layers -->
    <div class="osi-layers">
      <div v-for="layer in osiLayers" :key="layer.number"
        class="osi-layer"
        :class="dragOverLayer === layer.number ? 'osi-layer-over' : ''"
        :style="{ '--layer-color': layer.color, '--layer-bg': layer.bg }"
        @dragover.prevent="dragOverLayer = layer.number"
        @dragleave="dragOverLayer = null"
        @drop="onDrop($event, layer.number)">

        <div class="osi-layer-head">
          <span class="osi-layer-num" :style="{ background: layer.color }">{{ layer.number }}</span>
          <div class="osi-layer-names">
            <span class="osi-layer-de">{{ layer.name }}</span>
            <span class="osi-layer-en">{{ layer.english }}</span>
          </div>
          <div class="osi-layer-protocol-hint">{{ layer.hint }}</div>
        </div>

        <div class="osi-dropzone"
          :class="dragOverLayer === layer.number ? 'osi-dropzone-over' : ''"
          :style="dragOverLayer === layer.number ? { borderColor: layer.color, background: layer.bg + '33' } : {}">
          <span v-for="(item, i) in droppedItems[layer.number]" :key="i"
            class="osi-placed-chip"
            :style="{ background: layer.bg + '33', borderColor: layer.color, color: layer.color }">
            ✓ {{ item }}
          </span>
          <span v-if="!droppedItems[layer.number]?.length" class="osi-dropzone-hint">
            Hierher ziehen...
          </span>
        </div>
      </div>
    </div>

    <!-- Buttons -->
    <div class="osi-actions">
      <button class="btn-primary" @click="checkAll">🔍 Übersicht</button>
      <button class="btn-ghost" @click="reset">↺ Zurücksetzen</button>
    </div>

    <!-- Feedback Toast -->
    <transition name="toast">
      <div v-if="feedback" class="osi-toast"
        :class="feedback.type === 'success' ? 'osi-toast-ok' : feedback.type === 'error' ? 'osi-toast-err' : 'osi-toast-info'">
        {{ feedback.message }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import LumiHint from '@/presentation/components/panel/user/ap1/LumiHint.vue'

const emit = defineEmits<{ score: [points: number] }>()

interface OSIItem { text: string; layer: number }

const osiLayers = [
  { number: 7, name: 'Anwendungsschicht', english: 'Application', color: '#6366f1', bg: '#6366f1', hint: 'HTTP, FTP, SMTP, DNS' },
  { number: 6, name: 'Darstellungsschicht', english: 'Presentation', color: '#8b5cf6', bg: '#8b5cf6', hint: 'TLS/SSL, MIME' },
  { number: 5, name: 'Sitzungsschicht', english: 'Session', color: '#a855f7', bg: '#a855f7', hint: 'NetBIOS, PPTP' },
  { number: 4, name: 'Transportschicht', english: 'Transport', color: '#3b82f6', bg: '#3b82f6', hint: 'TCP, UDP' },
  { number: 3, name: 'Vermittlungsschicht', english: 'Network', color: '#0ea5e9', bg: '#0ea5e9', hint: 'IP, Router, ICMP' },
  { number: 2, name: 'Sicherungsschicht', english: 'Data Link', color: '#14b8a6', bg: '#14b8a6', hint: 'Switch, MAC, ARP' },
  { number: 1, name: 'Bitübertragungsschicht', english: 'Physical', color: '#22c55e', bg: '#22c55e', hint: 'Kabel, Hub, RJ-45' },
]

const allItems: Record<string, OSIItem[]> = {
  easy: [
    { text: 'HTTP', layer: 7 }, { text: 'FTP', layer: 7 }, { text: 'SMTP', layer: 7 }, { text: 'DNS', layer: 7 },
    { text: 'TCP', layer: 4 }, { text: 'UDP', layer: 4 },
    { text: 'IP', layer: 3 }, { text: 'Router', layer: 3 },
    { text: 'Switch', layer: 2 }, { text: 'MAC-Adresse', layer: 2 }, { text: 'Ethernet', layer: 2 },
    { text: 'Kabel', layer: 1 }, { text: 'Hub', layer: 1 }, { text: 'Repeater', layer: 1 },
  ],
  normal: [
    { text: 'HTTP', layer: 7 }, { text: 'FTP', layer: 7 }, { text: 'SMTP', layer: 7 }, { text: 'DNS', layer: 7 },
    { text: 'SSH', layer: 7 }, { text: 'SNMP', layer: 7 }, { text: 'LDAP', layer: 7 },
    { text: 'TLS/SSL', layer: 6 }, { text: 'Verschlüsselung', layer: 6 }, { text: 'Kompression', layer: 6 },
    { text: 'NetBIOS', layer: 5 }, { text: 'PPTP', layer: 5 },
    { text: 'TCP', layer: 4 }, { text: 'UDP', layer: 4 },
    { text: 'IP', layer: 3 }, { text: 'Router', layer: 3 }, { text: 'ICMP', layer: 3 },
    { text: 'Switch', layer: 2 }, { text: 'MAC-Adresse', layer: 2 }, { text: 'ARP', layer: 2 }, { text: 'PPP', layer: 2 },
    { text: 'Kabel', layer: 1 }, { text: 'Hub', layer: 1 }, { text: 'RJ-45', layer: 1 },
  ],
  hard: [
    { text: 'HTTP', layer: 7 }, { text: 'FTP', layer: 7 }, { text: 'SMTP', layer: 7 }, { text: 'DNS', layer: 7 },
    { text: 'SSH', layer: 7 }, { text: 'SNMP', layer: 7 }, { text: 'TFTP', layer: 7 }, { text: 'TELNET', layer: 7 },
    { text: 'TLS/SSL', layer: 6 }, { text: 'Verschlüsselung', layer: 6 }, { text: 'Kompression', layer: 6 }, { text: 'MIME', layer: 6 },
    { text: 'NetBIOS', layer: 5 }, { text: 'PPTP', layer: 5 }, { text: 'SCP', layer: 5 },
    { text: 'TCP', layer: 4 }, { text: 'UDP', layer: 4 }, { text: 'SCTP', layer: 4 },
    { text: 'IP', layer: 3 }, { text: 'Router', layer: 3 }, { text: 'ICMP', layer: 3 }, { text: 'OSPF', layer: 3 }, { text: 'Firewall (L3)', layer: 3 },
    { text: 'Switch', layer: 2 }, { text: 'MAC-Adresse', layer: 2 }, { text: 'ARP', layer: 2 }, { text: 'VLAN', layer: 2 }, { text: 'L2TP', layer: 2 },
    { text: 'Kabel', layer: 1 }, { text: 'Hub', layer: 1 }, { text: 'RJ-45', layer: 1 }, { text: 'Glasfaser', layer: 1 },
  ],
}

const difficulties = [
  { key: 'easy', label: 'Anfänger', count: 14 },
  { key: 'normal', label: 'Normal', count: 24 },
  { key: 'hard', label: 'Experte', count: 32 },
]

const difficulty = ref('easy')
const shuffledItems = ref<OSIItem[]>([])
const placed = reactive<Record<number, boolean>>({})
const droppedItems = reactive<Record<number, string[]>>({})
const dragOverLayer = ref<number | null>(null)
const dragItemIdx = ref<number | null>(null)
const feedback = ref<{ message: string; type: string } | null>(null)

function shuffle(arr: OSIItem[]) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function changeDifficulty(key: string) {
  difficulty.value = key
  reset()
}

function reset() {
  shuffledItems.value = shuffle(allItems[difficulty.value])
  Object.keys(placed).forEach(k => delete placed[Number(k)])
  osiLayers.forEach(l => { droppedItems[l.number] = [] })
  feedback.value = null
}

function onDragStart(e: DragEvent, idx: number) {
  dragItemIdx.value = idx
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}

function onDrop(e: DragEvent, layerNum: number) {
  e.preventDefault()
  dragOverLayer.value = null
  const idx = dragItemIdx.value
  if (idx === null || placed[idx]) return
  const item = shuffledItems.value[idx]
  if (item.layer === layerNum) {
    placed[idx] = true
    if (!droppedItems[layerNum]) droppedItems[layerNum] = []
    droppedItems[layerNum].push(item.text)
    feedback.value = { message: `✅ Richtig! ${item.text} gehört zu Schicht ${layerNum}`, type: 'success' }
    emit('score', 5)
  } else {
    const correctLayer = osiLayers.find(l => l.number === item.layer)
    feedback.value = { message: `❌ Falsch! ${item.text} gehört zu Schicht ${item.layer} (${correctLayer?.name})`, type: 'error' }
    emit('score', 0)
  }
  setTimeout(() => { feedback.value = null }, 3000)
}

function checkAll() {
  const total = shuffledItems.value.length
  const correct = Object.keys(placed).length
  if (correct === total) {
    feedback.value = { message: `🏆 Perfekt! Alle ${total} Elemente richtig zugeordnet!`, type: 'success' }
  } else {
    feedback.value = { message: `📊 ${correct}/${total} richtig platziert. Weiter so!`, type: 'info' }
  }
  setTimeout(() => { feedback.value = null }, 4000)
}

reset()
</script>

<style scoped>
.osi-wrap { max-width: 900px; }

.osi-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 16px; gap: 12px;
}
.osi-title { font-size: 20px; font-weight: 800; color: var(--color-text-primary); margin: 0 0 4px; }
.osi-sub { font-size: 13px; color: var(--color-text-secondary); margin: 0; }

.osi-diff-bar { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.osi-diff-btn {
  padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600;
  border: 1px solid var(--color-border); background: var(--color-surface);
  color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
}
.osi-diff-btn:hover { border-color: #6366f1; color: #a5b4fc; }
.osi-diff-active { background: rgba(99,102,241,0.2) !important; border-color: #6366f1 !important; color: #a5b4fc !important; }
.osi-diff-count {
  display: inline-block; background: rgba(99,102,241,0.3); border-radius: 10px;
  padding: 0 6px; font-size: 11px; margin-left: 4px;
}

.osi-pool {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 12px; padding: 14px; margin-bottom: 16px;
}
.osi-pool-label { font-size: 12px; font-weight: 700; color: var(--color-text-secondary); margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
.osi-pool-items { display: flex; flex-wrap: wrap; gap: 8px; }
.osi-chip {
  padding: 5px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;
  border: 1.5px solid; transition: all 0.15s; user-select: none;
}
.osi-chip-active {
  background: rgba(99,102,241,0.12); border-color: #6366f1; color: #a5b4fc;
  cursor: grab;
}
.osi-chip-active:hover { background: rgba(99,102,241,0.25); transform: scale(1.05); }
.osi-chip-done { background: rgba(34,197,94,0.08); border-color: #22c55e; color: #4ade80; opacity: 0.5; cursor: default; }

.osi-layers { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.osi-layer {
  border: 2px solid var(--color-border); border-radius: 12px;
  padding: 10px 14px; transition: all 0.15s;
  background: var(--color-surface);
}
.osi-layer-over {
  border-color: var(--layer-color) !important;
  background: color-mix(in srgb, var(--layer-bg) 8%, var(--color-surface)) !important;
  transform: scale(1.01);
}
.osi-layer-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.osi-layer-num {
  width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center;
  justify-content: center; color: white; font-weight: 800; font-size: 13px; flex-shrink: 0;
}
.osi-layer-names { flex: 1; }
.osi-layer-de { font-weight: 700; font-size: 14px; color: var(--color-text-primary); display: block; }
.osi-layer-en { font-size: 11px; color: var(--color-text-secondary); }
.osi-layer-protocol-hint {
  font-size: 11px; color: var(--color-text-secondary); font-style: italic;
  text-align: right; padding-right: 4px;
}

.osi-dropzone {
  min-height: 38px; border: 2px dashed var(--color-border);
  border-radius: 8px; padding: 6px 8px; display: flex; flex-wrap: wrap; gap: 6px;
  align-items: center; transition: all 0.15s;
}
.osi-dropzone-over { border-style: solid !important; }
.osi-dropzone-hint { font-size: 12px; color: var(--color-text-secondary); font-style: italic; }
.osi-placed-chip {
  padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;
  border: 1.5px solid; display: inline-flex; align-items: center; gap: 4px;
}

.osi-actions { display: flex; gap: 10px; margin-bottom: 12px; }
.btn-primary {
  padding: 8px 20px; background: #6366f1; color: white; border: none;
  border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.15s;
}
.btn-primary:hover { background: #4f46e5; }
.btn-ghost {
  padding: 8px 20px; background: var(--color-surface); color: var(--color-text-secondary);
  border: 1px solid var(--color-border); border-radius: 8px; font-weight: 600;
  font-size: 14px; cursor: pointer; transition: all 0.15s;
}
.btn-ghost:hover { border-color: #6366f1; color: #a5b4fc; }

.osi-toast {
  position: fixed; bottom: 24px; right: 24px; z-index: 999;
  padding: 12px 20px; border-radius: 10px; font-weight: 600; font-size: 14px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3); max-width: 360px;
}
.osi-toast-ok { background: #166534; color: #86efac; border: 1px solid #16a34a; }
.osi-toast-err { background: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }
.osi-toast-info { background: #1e3a5f; color: #93c5fd; border: 1px solid #3b82f6; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(16px); }
</style>
