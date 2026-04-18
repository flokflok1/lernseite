<template>
  <div class="ap-panel" :class="{ 'ap-expanded': isExpanded }">
    <!-- Toggle-Leiste -->
    <button class="ap-toggle" @click="isExpanded = !isExpanded" :aria-expanded="isExpanded">
      <span class="ap-toggle-icon">{{ isExpanded ? '&#9660;' : '&#9654;' }}</span>
      <span class="ap-toggle-label">
        <span class="ap-icon">&#128206;</span>
        Anlagen ({{ anlagen.length }})
      </span>
      <span v-if="!isExpanded" class="ap-toggle-hint">Klicken zum Öffnen</span>
    </button>

    <!-- Anlagen-Inhalt -->
    <transition name="ap-slide">
      <div v-if="isExpanded" class="ap-content">
        <!-- Tab-Navigation bei mehreren Anlagen -->
        <div v-if="anlagen.length > 1" class="ap-tabs">
          <button
            v-for="(anlage, idx) in anlagen"
            :key="anlage.id"
            class="ap-tab"
            :class="{ 'ap-tab-active': activeTab === idx }"
            @click="activeTab = idx"
          >
            <span class="ap-tab-icon">{{ getTypeIcon(anlage.type) }}</span>
            {{ anlage.title }}
          </button>
        </div>

        <!-- Aktive Anlage -->
        <div v-if="activeAnlage" class="ap-anlage">
          <!-- Titel (bei nur einer Anlage) -->
          <div v-if="anlagen.length === 1" class="ap-title">
            <span class="ap-title-icon">{{ getTypeIcon(activeAnlage.type) }}</span>
            {{ activeAnlage.title }}
          </div>

          <!-- SVG-Diagramm (Netzwerktopologie, ER, Rack etc.) -->
          <div
            v-if="activeAnlage.diagram"
            class="ap-diagram-wrap"
            :class="{ 'ap-diagram-zoomed': isZoomed }"
          >
            <div class="ap-diagram-toolbar">
              <button class="ap-btn-icon" @click="zoomIn" title="Vergrößern">&#43;</button>
              <button class="ap-btn-icon" @click="zoomOut" title="Verkleinern">&#8722;</button>
              <button class="ap-btn-icon" @click="resetZoom" title="Zurücksetzen">&#8634;</button>
              <span class="ap-zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
            </div>
            <div
              class="ap-diagram-container"
              ref="diagramContainer"
              @mousedown="startPan"
              @wheel.prevent="onWheel"
            >
              <div
                class="ap-diagram-svg"
                :style="diagramTransformStyle"
                v-html="activeAnlage.diagram.svg"
              ></div>
            </div>
            <p v-if="activeAnlage.diagram.description" class="ap-diagram-desc">
              {{ activeAnlage.diagram.description }}
            </p>
          </div>

          <!-- Tabelle (Datenblatt / Referenz-Tabelle) -->
          <div v-if="activeAnlage.table" class="ap-table-wrap">
            <table class="ap-table">
              <caption v-if="activeAnlage.table.caption" class="ap-table-caption">
                {{ activeAnlage.table.caption }}
              </caption>
              <thead>
                <tr>
                  <th
                    v-for="(header, hi) in activeAnlage.table.headers"
                    :key="hi"
                    class="ap-table-th"
                  >
                    {{ header }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, ri) in activeAnlage.table.rows"
                  :key="ri"
                  class="ap-table-row"
                  :class="{
                    'ap-table-row-highlight': activeAnlage.table.highlightRows?.includes(ri),
                    'ap-table-row-even': ri % 2 === 0
                  }"
                >
                  <td
                    v-for="(cell, ci) in row"
                    :key="ci"
                    class="ap-table-td"
                  >
                    {{ cell }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Bild (Screenshot, allgemeine Grafik) -->
          <div v-if="activeAnlage.imageUrl" class="ap-image-wrap">
            <img
              :src="activeAnlage.imageUrl"
              :alt="activeAnlage.title"
              class="ap-image"
              @click="isImageFullscreen = !isImageFullscreen"
              :class="{ 'ap-image-fullscreen': isImageFullscreen }"
            />
            <p class="ap-image-hint">Klicken zum Vergrößern</p>
          </div>

          <!-- Fußnote -->
          <p v-if="activeAnlage.footnote" class="ap-footnote">
            <span class="ap-footnote-icon">&#9432;</span>
            {{ activeAnlage.footnote }}
          </p>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Anlage } from '../types'

const props = defineProps<{
  anlagen: Anlage[]
  /** Automatisch aufklappen (z.B. wenn Aufgabe aktiv) */
  autoExpand?: boolean
}>()

// State
const isExpanded = ref(props.autoExpand ?? false)
const activeTab = ref(0)
const isZoomed = ref(false)
const isImageFullscreen = ref(false)
const zoomLevel = ref(1)
const panX = ref(0)
const panY = ref(0)
const isPanning = ref(false)
const panStartX = ref(0)
const panStartY = ref(0)
const diagramContainer = ref<HTMLElement | null>(null)

// Aktive Anlage
const activeAnlage = computed(() => props.anlagen[activeTab.value] || null)

// Zoom + Pan Transform
const diagramTransformStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoomLevel.value})`,
  transformOrigin: 'center center',
  cursor: isPanning.value ? 'grabbing' : 'grab',
}))

// Icon nach Anlage-Typ
function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    'network-topology': '\u{1F5A7}',   // 🖧
    'datasheet': '\u{1F4CB}',           // 📋
    'table': '\u{1F4CA}',               // 📊
    'er-diagram': '\u{1F5C3}',          // 🗃
    'rack-layout': '\u{1F5B3}',         // 🖳
    'process-diagram': '\u{1F504}',     // 🔄
    'image': '\u{1F5BC}',               // 🖼
  }
  return icons[type] || '\u{1F4C4}'     // 📄
}

// Zoom Controls
function zoomIn() {
  zoomLevel.value = Math.min(zoomLevel.value + 0.25, 3)
  isZoomed.value = zoomLevel.value > 1
}

function zoomOut() {
  zoomLevel.value = Math.max(zoomLevel.value - 0.25, 0.25)
  isZoomed.value = zoomLevel.value > 1
}

function resetZoom() {
  zoomLevel.value = 1
  panX.value = 0
  panY.value = 0
  isZoomed.value = false
}

function onWheel(e: WheelEvent) {
  if (e.deltaY < 0) zoomIn()
  else zoomOut()
}

// Pan Controls
function startPan(e: MouseEvent) {
  isPanning.value = true
  panStartX.value = e.clientX - panX.value
  panStartY.value = e.clientY - panY.value

  const onMove = (ev: MouseEvent) => {
    panX.value = ev.clientX - panStartX.value
    panY.value = ev.clientY - panStartY.value
  }

  const onUp = () => {
    isPanning.value = false
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

// Tab-Wechsel → Zoom zurücksetzen
watch(activeTab, () => {
  resetZoom()
  isImageFullscreen.value = false
})

// Auto-Expand wenn Prop sich ändert
watch(() => props.autoExpand, (val) => {
  if (val) isExpanded.value = true
})
</script>

<style scoped>
/* ─── Panel Container ─── */
.ap-panel {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  overflow: hidden;
  margin: 12px 0;
  background: rgba(0, 0, 0, 0.15);
  transition: border-color 0.3s ease;
}
.ap-panel:hover {
  border-color: rgba(255, 255, 255, 0.12);
}
.ap-expanded {
  border-color: rgba(26, 115, 232, 0.3);
}

/* ─── Toggle Button ─── */
.ap-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(13, 71, 161, 0.12);
  border: none;
  color: #b0bec5;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}
.ap-toggle:hover {
  background: rgba(13, 71, 161, 0.2);
  color: #e3f2fd;
}
.ap-toggle-icon {
  font-size: 0.7rem;
  transition: transform 0.2s ease;
  width: 14px;
  text-align: center;
}
.ap-icon {
  margin-right: 2px;
}
.ap-toggle-label {
  flex: 1;
}
.ap-toggle-hint {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.25);
  font-weight: 400;
}

/* ─── Slide Transition ─── */
.ap-slide-enter-active,
.ap-slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.ap-slide-enter-from,
.ap-slide-leave-to {
  max-height: 0;
  opacity: 0;
}
.ap-slide-enter-to,
.ap-slide-leave-from {
  max-height: 2000px;
  opacity: 1;
}

/* ─── Content ─── */
.ap-content {
  padding: 0;
}

/* ─── Tabs ─── */
.ap-tabs {
  display: flex;
  gap: 2px;
  padding: 8px 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  overflow-x: auto;
}
.ap-tab {
  padding: 8px 14px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #78909c;
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  border-radius: 6px 6px 0 0;
}
.ap-tab:hover {
  color: #b0bec5;
  background: rgba(255, 255, 255, 0.03);
}
.ap-tab-active {
  color: #e3f2fd;
  border-bottom-color: #1a73e8;
  background: rgba(26, 115, 232, 0.08);
}
.ap-tab-icon {
  margin-right: 4px;
}

/* ─── Anlage ─── */
.ap-anlage {
  padding: 14px;
}

.ap-title {
  font-size: 0.92rem;
  font-weight: 600;
  color: #e3f2fd;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.ap-title-icon {
  font-size: 1.05rem;
}

/* ─── SVG Diagramm ─── */
.ap-diagram-wrap {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
}
.ap-diagram-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.ap-btn-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  color: #b0bec5;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.15s ease;
}
.ap-btn-icon:hover {
  background: rgba(26, 115, 232, 0.15);
  border-color: rgba(26, 115, 232, 0.3);
  color: #e3f2fd;
}
.ap-zoom-level {
  font-size: 0.75rem;
  color: #78909c;
  margin-left: 6px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
}
.ap-diagram-container {
  overflow: hidden;
  min-height: 200px;
  max-height: 600px;
  position: relative;
  user-select: none;
}
.ap-diagram-svg {
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.1s ease;
}
.ap-diagram-svg :deep(svg) {
  max-width: 100%;
  height: auto;
}
/* SVG in Dark-Theme: Texte hell, Linien sichtbar */
.ap-diagram-svg :deep(svg text) {
  fill: #e0e0e0;
}
.ap-diagram-svg :deep(svg line),
.ap-diagram-svg :deep(svg path),
.ap-diagram-svg :deep(svg polyline),
.ap-diagram-svg :deep(svg polygon) {
  stroke: #78909c;
}
.ap-diagram-svg :deep(svg rect),
.ap-diagram-svg :deep(svg circle),
.ap-diagram-svg :deep(svg ellipse) {
  stroke: #546e7a;
  fill: rgba(38, 50, 56, 0.6);
}
.ap-diagram-desc {
  padding: 8px 12px;
  font-size: 0.8rem;
  color: #78909c;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  font-style: italic;
}

/* ─── Tabelle ─── */
.ap-table-wrap {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
.ap-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.ap-table-caption {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.84rem;
  color: #90a4ae;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  caption-side: top;
}
.ap-table-th {
  background: rgba(13, 71, 161, 0.25);
  color: #e3f2fd;
  padding: 9px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  border-bottom: 2px solid rgba(26, 115, 232, 0.25);
  white-space: nowrap;
}
.ap-table-td {
  padding: 8px 12px;
  color: #b0bec5;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  vertical-align: top;
  line-height: 1.45;
}
.ap-table-row-even {
  background: rgba(255, 255, 255, 0.012);
}
.ap-table-row-highlight {
  background: rgba(26, 115, 232, 0.08) !important;
  border-left: 3px solid #1a73e8;
}
.ap-table-row-highlight .ap-table-td {
  color: #e3f2fd;
  font-weight: 500;
}

/* ─── Bild ─── */
.ap-image-wrap {
  text-align: center;
}
.ap-image {
  max-width: 100%;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
}
.ap-image:hover {
  border-color: rgba(26, 115, 232, 0.3);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.ap-image-fullscreen {
  position: fixed;
  top: 5vh;
  left: 5vw;
  width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  z-index: 1000;
  border-radius: 12px;
  border: 2px solid rgba(26, 115, 232, 0.4);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
  background: rgba(0, 0, 0, 0.95);
}
.ap-image-hint {
  font-size: 0.75rem;
  color: #546e7a;
  margin-top: 4px;
}

/* ─── Fußnote ─── */
.ap-footnote {
  margin-top: 10px;
  padding: 8px 12px;
  background: rgba(255, 193, 7, 0.06);
  border-left: 3px solid rgba(255, 193, 7, 0.4);
  border-radius: 0 6px 6px 0;
  font-size: 0.8rem;
  color: #b0bec5;
  line-height: 1.45;
}
.ap-footnote-icon {
  margin-right: 4px;
  color: #ffc107;
}
</style>
