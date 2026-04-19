<script setup lang="ts">
import { ref, computed } from 'vue'

type DeviceType = 'router' | 'switch' | 'firewall' | 'server' | 'client' | 'wlan' | 'modem' | 'printer' | 'cloud' | 'subnet'

interface NetDevice {
  id: string
  type: DeviceType
  label: string
  ipAddress?: string
  x: number
  y: number
}

interface NetLink {
  id: string
  from: string
  to: string
  label?: string
  type: 'ethernet' | 'wan' | 'wlan' | 'vlan'
}

interface Props {
  submitted?: boolean
  width?: number
  height?: number
  initialDevices?: NetDevice[]
  initialLinks?: NetLink[]
}

const props = withDefaults(defineProps<Props>(), {
  submitted: false,
  width: 1100,
  height: 700,
  initialDevices: () => [],
  initialLinks: () => [],
})

const emit = defineEmits<{
  change: [payload: { devices: NetDevice[]; links: NetLink[] }]
}>()

const devices = ref<NetDevice[]>([...props.initialDevices])
const links = ref<NetLink[]>([...props.initialLinks])
const selectedId = ref<string | null>(null)
const linkStartId = ref<string | null>(null)
const linkType = ref<NetLink['type']>('ethernet')

const svgEl = ref<SVGSVGElement | null>(null)
const draggingId = ref<string | null>(null)
const dragOffset = ref({ x: 0, y: 0 })

let idCounter = 1
function nextId(p: string) { return `${p}-${idCounter++}-${Date.now()}` }

const DEVICE_META: Record<DeviceType, { label: string; icon: string; color: string; size: number }> = {
  router:   { label: 'Router',    icon: '⟷', color: '#2563eb', size: 60 },
  switch:   { label: 'Switch',    icon: '≣', color: '#16a34a', size: 60 },
  firewall: { label: 'Firewall',  icon: '▮',  color: '#dc2626', size: 60 },
  server:   { label: 'Server',    icon: '🗄', color: '#7c3aed', size: 60 },
  client:   { label: 'PC/Client', icon: '🖥', color: '#6b7280', size: 55 },
  wlan:     { label: 'AP (WLAN)', icon: '📶', color: '#0ea5e9', size: 55 },
  modem:    { label: 'Modem',     icon: '□',  color: '#64748b', size: 55 },
  printer:  { label: 'Drucker',   icon: '🖨', color: '#854d0e', size: 55 },
  cloud:    { label: 'Internet',  icon: '☁', color: '#06b6d4', size: 80 },
  subnet:   { label: 'Subnetz',   icon: '▢',  color: '#f59e0b', size: 200 },
}

function addDevice(type: DeviceType) {
  if (props.submitted) return
  const baseLabel = DEVICE_META[type].label
  const label = window.prompt(`${baseLabel}-Name (z.B. „R1" oder „Switch-Zentrale"):`, baseLabel) || baseLabel
  let ip: string | undefined = undefined
  if (type === 'router' || type === 'server' || type === 'client' || type === 'firewall' || type === 'wlan' || type === 'printer') {
    ip = window.prompt(`IP-Adresse für ${label} (optional):`) || undefined
  }
  const offset = devices.value.length * 40
  devices.value.push({
    id: nextId(type),
    type,
    label,
    ipAddress: ip,
    x: 120 + (offset % 500),
    y: 100 + (Math.floor(offset / 500) * 120) + (offset % 100),
  })
  emitChange()
}

function startLink(id: string) {
  if (props.submitted) return
  if (linkStartId.value === id) {
    linkStartId.value = null
    return
  }
  if (linkStartId.value) {
    const from = linkStartId.value
    const to = id
    if (from !== to) {
      const label = window.prompt('Link-Label (z.B. VLAN-ID, Bandbreite, optional):') || ''
      links.value.push({ id: nextId('link'), from, to, label, type: linkType.value })
      emitChange()
    }
    linkStartId.value = null
  } else {
    linkStartId.value = id
  }
}

function deleteDevice(id: string) {
  if (props.submitted) return
  devices.value = devices.value.filter(d => d.id !== id)
  links.value = links.value.filter(l => l.from !== id && l.to !== id)
  selectedId.value = null
  emitChange()
}

function editDevice(id: string) {
  if (props.submitted) return
  const dev = devices.value.find(d => d.id === id)
  if (!dev) return
  const label = window.prompt('Name:', dev.label)
  if (label !== null) dev.label = label
  const ip = window.prompt('IP-Adresse (leer = keine):', dev.ipAddress || '')
  if (ip !== null) dev.ipAddress = ip || undefined
  emitChange()
}

function svgPoint(evt: PointerEvent) {
  if (!svgEl.value) return { x: 0, y: 0 }
  const rect = svgEl.value.getBoundingClientRect()
  return {
    x: (evt.clientX - rect.left) * (props.width / rect.width),
    y: (evt.clientY - rect.top) * (props.height / rect.height),
  }
}

function onDeviceDown(evt: PointerEvent, id: string) {
  if (props.submitted) return
  evt.stopPropagation()
  selectedId.value = id
  const dev = devices.value.find(d => d.id === id)
  if (!dev) return
  const p = svgPoint(evt)
  draggingId.value = id
  dragOffset.value = { x: p.x - dev.x, y: p.y - dev.y }
}

function onSvgMove(evt: PointerEvent) {
  if (!draggingId.value) return
  const dev = devices.value.find(d => d.id === draggingId.value)
  if (!dev) return
  const p = svgPoint(evt)
  dev.x = Math.max(0, Math.min(props.width, p.x - dragOffset.value.x))
  dev.y = Math.max(0, Math.min(props.height, p.y - dragOffset.value.y))
}

function onSvgUp() {
  if (draggingId.value) {
    draggingId.value = null
    emitChange()
  }
}

function clearAll() {
  if (props.submitted) return
  if (!window.confirm('Alles löschen?')) return
  devices.value = []
  links.value = []
  emitChange()
}

function emitChange() {
  emit('change', {
    devices: JSON.parse(JSON.stringify(devices.value)),
    links: JSON.parse(JSON.stringify(links.value)),
  })
}

function linkPath(link: NetLink): string {
  const from = devices.value.find(d => d.id === link.from)
  const to = devices.value.find(d => d.id === link.to)
  if (!from || !to) return ''
  const sz1 = DEVICE_META[from.type].size
  const sz2 = DEVICE_META[to.type].size
  const x1 = from.x + sz1 / 2
  const y1 = from.y + sz1 / 2
  const x2 = to.x + sz2 / 2
  const y2 = to.y + sz2 / 2
  return `M ${x1} ${y1} L ${x2} ${y2}`
}

function linkMidpoint(link: NetLink) {
  const from = devices.value.find(d => d.id === link.from)
  const to = devices.value.find(d => d.id === link.to)
  if (!from || !to) return { x: 0, y: 0 }
  const sz1 = DEVICE_META[from.type].size
  const sz2 = DEVICE_META[to.type].size
  return {
    x: (from.x + sz1 / 2 + to.x + sz2 / 2) / 2,
    y: (from.y + sz1 / 2 + to.y + sz2 / 2) / 2 - 6,
  }
}

function linkStroke(type: NetLink['type']): string {
  return { ethernet: '#1f2937', wan: '#7c3aed', wlan: '#0ea5e9', vlan: '#f59e0b' }[type]
}

function linkDashArray(type: NetLink['type']): string {
  return { ethernet: 'none', wan: '6,4', wlan: '3,3', vlan: '8,2,2,2' }[type]
}

const viewBox = computed(() => `0 0 ${props.width} ${props.height}`)
</script>

<template>
  <div class="np-builder">
    <div class="np-toolbar">
      <div class="np-tool-group">
        <span class="np-tool-label">Geräte:</span>
        <button
          v-for="t in (['router','switch','firewall','server','client','wlan','printer','cloud','subnet'] as DeviceType[])"
          :key="t"
          class="np-btn"
          :disabled="submitted"
          @click="addDevice(t)"
        >
          {{ DEVICE_META[t].icon }} {{ DEVICE_META[t].label }}
        </button>
      </div>

      <div class="np-tool-group">
        <span class="np-tool-label">Link-Typ:</span>
        <button
          v-for="t in (['ethernet','wan','wlan','vlan'] as NetLink['type'][])"
          :key="t"
          class="np-btn np-btn-link"
          :class="{ 'np-btn-active': linkType === t }"
          :disabled="submitted"
          @click="linkType = t"
        >
          <span class="np-link-sample" :style="{ borderColor: linkStroke(t), borderStyle: t === 'ethernet' ? 'solid' : 'dashed' }"></span>
          {{ t.toUpperCase() }}
        </button>
      </div>

      <div class="np-tool-group">
        <button class="np-btn np-btn-danger" :disabled="submitted" @click="clearAll">🗑 Alles löschen</button>
      </div>
    </div>

    <p class="np-hint">
      <strong>Netzplan:</strong> Gerät hinzufügen → ziehen. Klick auf Gerät: Name/IP bearbeiten. „Verbinden"-Button
      zweimal (Quelle + Ziel), um Leitung zu ziehen. Link-Typ wählt Darstellung: Ethernet (durchgezogen),
      WAN (gestrichelt violett), WLAN (gepunktet blau), VLAN (strichpunktiert orange).
    </p>

    <div class="np-canvas-wrap">
      <svg
        ref="svgEl"
        class="np-svg"
        :viewBox="viewBox"
        @pointermove="onSvgMove"
        @pointerup="onSvgUp"
        @pointerleave="onSvgUp"
      >
        <defs>
          <pattern id="np-grid" width="25" height="25" patternUnits="userSpaceOnUse">
            <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#e5e7eb" stroke-width="0.5" />
          </pattern>
        </defs>

        <rect :width="width" :height="height" fill="url(#np-grid)" />

        <!-- Subnet containers (behind) -->
        <g v-for="d in devices.filter(x => x.type === 'subnet')" :key="d.id">
          <rect
            :x="d.x" :y="d.y"
            :width="DEVICE_META.subnet.size" :height="140"
            fill="rgba(245,158,11,0.08)"
            stroke="#f59e0b"
            stroke-width="2"
            stroke-dasharray="8,4"
            rx="8"
            @pointerdown="onDeviceDown($event, d.id)"
            style="cursor: move;"
          />
          <text
            :x="d.x + 10" :y="d.y + 22"
            font-size="14" font-weight="600" fill="#92400e"
            font-family="system-ui, sans-serif"
            style="pointer-events: none;"
          >
            {{ d.label }}
          </text>
        </g>

        <!-- Links -->
        <g>
          <g v-for="link in links" :key="link.id">
            <path
              :d="linkPath(link)"
              :stroke="linkStroke(link.type)"
              :stroke-dasharray="linkDashArray(link.type)"
              stroke-width="2.5"
              fill="none"
            />
            <text
              v-if="link.label"
              :x="linkMidpoint(link).x"
              :y="linkMidpoint(link).y"
              font-size="11"
              fill="#1f2937"
              text-anchor="middle"
              font-family="system-ui"
              font-weight="600"
            >
              {{ link.label }}
            </text>
          </g>
        </g>

        <!-- Devices (non-subnet) -->
        <g
          v-for="d in devices.filter(x => x.type !== 'subnet')"
          :key="d.id"
          :class="{
            'np-dev-selected': selectedId === d.id,
            'np-dev-link-start': linkStartId === d.id,
          }"
          @pointerdown="onDeviceDown($event, d.id)"
        >
          <rect
            :x="d.x" :y="d.y"
            :width="DEVICE_META[d.type].size"
            :height="DEVICE_META[d.type].size"
            rx="6"
            :fill="DEVICE_META[d.type].color + '22'"
            :stroke="DEVICE_META[d.type].color"
            stroke-width="2"
            style="cursor: move;"
          />
          <text
            :x="d.x + DEVICE_META[d.type].size / 2"
            :y="d.y + DEVICE_META[d.type].size / 2 + 8"
            text-anchor="middle"
            font-size="24"
            style="pointer-events: none;"
          >
            {{ DEVICE_META[d.type].icon }}
          </text>
          <text
            :x="d.x + DEVICE_META[d.type].size / 2"
            :y="d.y + DEVICE_META[d.type].size + 14"
            text-anchor="middle"
            font-size="12"
            font-weight="600"
            fill="#111827"
            font-family="system-ui"
            style="pointer-events: none;"
          >
            {{ d.label }}
          </text>
          <text
            v-if="d.ipAddress"
            :x="d.x + DEVICE_META[d.type].size / 2"
            :y="d.y + DEVICE_META[d.type].size + 28"
            text-anchor="middle"
            font-size="10"
            fill="#4b5563"
            font-family="monospace"
            style="pointer-events: none;"
          >
            {{ d.ipAddress }}
          </text>
        </g>
      </svg>
    </div>

    <div v-if="selectedId && !submitted" class="np-actions">
      <button class="np-btn" @click="editDevice(selectedId)">✎ Bearbeiten</button>
      <button class="np-btn" @click="startLink(selectedId)">
        {{ linkStartId === selectedId ? '✕ Verbindung abbrechen' : '→ Verbinden' }}
      </button>
      <button class="np-btn np-btn-danger" @click="deleteDevice(selectedId)">🗑 Löschen</button>
    </div>
  </div>
</template>

<style scoped>
.np-builder {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border: 1px solid #d1d5db;
  border-radius: 8px;
}

.np-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  padding: 0.5rem;
  background: #fff;
  border-radius: 6px;
}

.np-tool-group {
  display: flex;
  gap: 0.3rem;
  align-items: center;
  flex-wrap: wrap;
}

.np-tool-label {
  font-weight: 600;
  font-size: 0.85rem;
  color: #374151;
  margin-right: 0.3rem;
}

.np-btn {
  padding: 0.35rem 0.6rem;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 0.82rem;
  cursor: pointer;
}
.np-btn:hover:not(:disabled) { background: #f3f4f6; }
.np-btn-active { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.np-btn-danger:hover:not(:disabled) { background: #fee2e2; color: #dc2626; }
.np-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.np-btn-link { display: inline-flex; align-items: center; gap: 4px; }
.np-link-sample {
  display: inline-block;
  width: 16px;
  height: 0;
  border-top-width: 2px;
}

.np-hint {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
  padding: 0.4rem 0.6rem;
  background: #eff6ff;
  border-left: 3px solid #2563eb;
  border-radius: 3px;
}

.np-canvas-wrap {
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  overflow: hidden;
}

.np-svg { width: 100%; height: auto; display: block; touch-action: none; }

.np-dev-selected rect { stroke-width: 3 !important; filter: drop-shadow(0 0 4px rgba(59,130,246,0.6)); }
.np-dev-link-start rect { stroke: #dc2626 !important; stroke-dasharray: 4,2; }

.np-actions { display: flex; gap: 0.5rem; padding: 0.5rem; background: #fff; border-radius: 6px; }
</style>
