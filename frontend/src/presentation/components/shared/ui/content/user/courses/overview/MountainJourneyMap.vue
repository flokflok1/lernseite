<template>
  <div class="map-section relative">
    <h2 class="map-title text-xl font-bold text-center mb-4">
      {{ $t('courses.your_journey') }}
    </h2>

    <div class="mountain-journey-container">
      <!-- SVG Mountain Path -->
      <svg
        class="mountain-svg"
        :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <!-- Path gradient for completed -->
          <linearGradient id="pathGradientComplete" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#34d399;stop-opacity:1" />
          </linearGradient>
          <!-- Glow filter -->
          <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
          <!-- Drop shadow for nodes -->
          <filter id="nodeShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="0" dy="4" stdDeviation="6" flood-opacity="0.4"/>
          </filter>
        </defs>

        <!-- Background path (dashed gray) -->
        <path
          :d="mountainPathD"
          stroke="rgba(255,255,255,0.2)"
          stroke-width="4"
          fill="none"
          stroke-linecap="round"
          stroke-dasharray="12 8"
        />

        <!-- Completed progress path (green glow) -->
        <path
          v-if="completedChapters > 0"
          :d="mountainPathD"
          stroke="url(#pathGradientComplete)"
          stroke-width="4"
          fill="none"
          stroke-linecap="round"
          class="progress-path"
          :stroke-dasharray="totalPathLength"
          :stroke-dashoffset="remainingPathOffset"
          filter="url(#glow)"
        />

        <!-- Summit Flag -->
        <g :transform="`translate(${summitPosition.x + 20}, ${summitPosition.y - 50})`">
          <!-- Flag pole -->
          <rect x="0" y="0" width="4" height="50" fill="#d97706" rx="1"/>
          <!-- Flag -->
          <path d="M 4 2 L 30 12 L 4 22 Z" fill="#ef4444">
            <animate attributeName="d"
              values="M 4 2 L 30 12 L 4 22 Z;M 4 2 L 28 10 L 4 20 Z;M 4 2 L 30 12 L 4 22 Z"
              dur="2s"
              repeatCount="indefinite"/>
          </path>
          <!-- Flag highlight -->
          <path d="M 4 2 L 18 8 L 4 14 Z" fill="#f87171" opacity="0.6"/>
        </g>
      </svg>

      <!-- Journey Nodes -->
      <div class="journey-nodes">
        <!-- Animated Character -->
        <div
          v-if="totalChapters > 0"
          class="character-container"
          :style="characterPositionStyle"
        >
          <!-- Hiker Character SVG -->
          <svg viewBox="0 0 80 100" class="hiker-character">
            <!-- Shadow -->
            <ellipse cx="40" cy="95" rx="18" ry="5" fill="rgba(0,0,0,0.3)"/>

            <!-- Legs (animated) -->
            <g class="legs">
              <path d="M35 65 L30 85 L25 88" stroke="#374151" stroke-width="6" stroke-linecap="round" fill="none" class="leg-left"/>
              <path d="M45 65 L52 82 L58 85" stroke="#1f2937" stroke-width="6" stroke-linecap="round" fill="none" class="leg-right"/>
              <!-- Shoes -->
              <ellipse cx="24" cy="89" rx="6" ry="3" fill="#92400e"/>
              <ellipse cx="59" cy="86" rx="6" ry="3" fill="#78350f"/>
            </g>

            <!-- Body -->
            <path d="M40 35 L40 68" stroke="#f59e0b" stroke-width="16" stroke-linecap="round"/>

            <!-- Backpack -->
            <rect x="22" y="38" width="14" height="22" rx="4" fill="#3b82f6"/>
            <rect x="24" y="40" width="10" height="4" rx="1" fill="#60a5fa"/>

            <!-- Arms (animated) -->
            <g class="arms">
              <path d="M40 42 L25 55" stroke="#fbbf24" stroke-width="5" stroke-linecap="round" fill="none" class="arm-left"/>
              <path d="M40 42 L58 48" stroke="#f59e0b" stroke-width="5" stroke-linecap="round" fill="none" class="arm-right"/>
            </g>

            <!-- Walking stick -->
            <line x1="60" y1="45" x2="68" y2="85" stroke="#92400e" stroke-width="3" stroke-linecap="round" class="walking-stick"/>

            <!-- Head -->
            <circle cx="40" cy="22" r="16" fill="#fcd34d"/>

            <!-- Hair -->
            <path d="M26 18 Q30 8 42 10 Q54 8 52 20" fill="#78350f"/>

            <!-- Face (looking right) -->
            <circle cx="47" cy="19" r="3" fill="#1f2937"/> <!-- Eye -->
            <circle cx="48" cy="18" r="1" fill="white"/> <!-- Eye highlight -->
            <path d="M50 26 Q54 28 52 30" stroke="#1f2937" stroke-width="2" fill="none"/> <!-- Smile -->

            <!-- Cap -->
            <ellipse cx="40" cy="10" rx="14" ry="5" fill="#dc2626"/>
            <rect x="26" y="8" width="28" height="6" fill="#dc2626"/>
          </svg>
        </div>

        <!-- Chapter Nodes -->
        <div
          v-for="(position, index) in nodePositions"
          :key="index"
          class="mountain-node"
          :class="getNodeStatusClass(index)"
          :style="getNodePositionStyle(index)"
          @click="$emit('node-click', index)"
        >
          <div class="node-outer">
            <div class="node-inner">
              <!-- Completed checkmark -->
              <svg v-if="isCompleted(index)" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
              <!-- Current play -->
              <svg v-else-if="isCurrent(index)" viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <!-- Locked -->
              <svg v-else viewBox="0 0 24 24" fill="currentColor" class="node-icon">
                <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
              </svg>
            </div>
          </div>
          <span class="node-label">{{ index + 1 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * MountainJourneyMap Component
 * ============================
 * Interactive SVG mountain journey visualization with animated character
 */
import { computed } from 'vue'

interface Props {
  totalChapters: number
  completedChapters: number
  currentChapterIndex: number
}

const props = defineProps<Props>()

defineEmits<{
  'node-click': [index: number]
}>()

// ============================================================================
// SVG Configuration
// ============================================================================

const svgWidth = 900
const svgHeight = 250

// ============================================================================
// Node Positions - Mountain climb from bottom-left to top-right
// ============================================================================

const nodePositions = computed(() => {
  const total = Math.max(props.totalChapters, 1)
  const positions: { x: number; y: number }[] = []

  const startX = 60
  const endX = svgWidth - 100
  const startY = svgHeight - 40
  const endY = 50

  for (let i = 0; i < total; i++) {
    const progress = total === 1 ? 0 : i / (total - 1)
    const x = startX + progress * (endX - startX)

    // Smooth curve up with slight wave
    const baseY = startY - progress * (startY - endY)
    const wave = Math.sin(progress * Math.PI * 2) * 20
    const y = baseY + (progress > 0 && progress < 1 ? wave : 0)

    positions.push({ x, y })
  }

  return positions
})

const summitPosition = computed(() => {
  const positions = nodePositions.value
  if (positions.length === 0) return { x: svgWidth - 100, y: 50 }
  return positions[positions.length - 1]
})

// ============================================================================
// SVG Path Calculation
// ============================================================================

const mountainPathD = computed(() => {
  const positions = nodePositions.value
  if (positions.length === 0) return ''
  if (positions.length === 1) return `M ${positions[0].x} ${positions[0].y}`

  let d = `M ${positions[0].x} ${positions[0].y}`

  for (let i = 1; i < positions.length; i++) {
    const prev = positions[i - 1]
    const curr = positions[i]
    const cpX = (prev.x + curr.x) / 2
    d += ` Q ${cpX} ${prev.y}, ${cpX} ${(prev.y + curr.y) / 2}`
    d += ` Q ${cpX} ${curr.y}, ${curr.x} ${curr.y}`
  }

  return d
})

const totalPathLength = 1400

const remainingPathOffset = computed(() => {
  if (props.totalChapters === 0) return totalPathLength
  const progress = props.completedChapters / props.totalChapters
  return totalPathLength * (1 - progress)
})

// ============================================================================
// Node & Character Positioning
// ============================================================================

const getNodePositionStyle = (index: number) => {
  const positions = nodePositions.value
  if (index >= positions.length) return {}
  const pos = positions[index]
  return {
    left: `${(pos.x / svgWidth) * 100}%`,
    top: `${(pos.y / svgHeight) * 100}%`
  }
}

const characterPositionStyle = computed(() => {
  const positions = nodePositions.value
  const charIndex = props.currentChapterIndex
  if (charIndex >= positions.length || positions.length === 0) return { display: 'none' }

  const pos = positions[charIndex]
  return {
    left: `${(pos.x / svgWidth) * 100}%`,
    top: `${((pos.y - 55) / svgHeight) * 100}%`
  }
})

// ============================================================================
// Node Status
// ============================================================================

const isCompleted = (index: number): boolean => {
  return index < props.completedChapters
}

const isCurrent = (index: number): boolean => {
  return index === props.currentChapterIndex
}

const getNodeStatusClass = (index: number): string => {
  if (isCompleted(index)) return 'completed'
  if (isCurrent(index)) return 'current'
  return 'locked'
}
</script>

<style scoped>
/* Map Section */
.map-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  padding: 1.5rem;
}

.map-title {
  color: var(--color-text-primary);
}

/* Mountain Container */
.mountain-journey-container {
  position: relative;
  width: 100%;
  height: 300px;
  margin-top: 1rem;
}

.mountain-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.progress-path {
  transition: stroke-dashoffset 1s ease-out;
}

/* Journey Nodes Container */
.journey-nodes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* Mountain Node */
.mountain-node {
  position: absolute;
  transform: translate(-50%, -50%);
  pointer-events: all;
  cursor: pointer;
  z-index: 10;
}

.node-outer {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.mountain-node:hover .node-outer {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.node-inner {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid;
  transition: all 0.3s ease;
}

.node-icon {
  width: 24px;
  height: 24px;
}

.node-label {
  position: absolute;
  bottom: -24px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  font-weight: bold;
  color: var(--color-text-secondary);
}

/* Node States */
.mountain-node.completed .node-inner {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
  border-color: #10b981;
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.mountain-node.current .node-inner {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
  border-color: #3b82f6;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

.mountain-node.locked .node-inner {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.3);
  cursor: not-allowed;
}

/* Character Container */
.character-container {
  position: absolute;
  width: 80px;
  height: 100px;
  transform: translate(-50%, -50%);
  transition: all 1s ease-out;
  z-index: 20;
  pointer-events: none;
}

.hiker-character {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
}

/* Character Animations */
.legs {
  animation: walk 0.6s ease-in-out infinite;
}

.arms {
  animation: swing 0.6s ease-in-out infinite;
}

@keyframes walk {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

@keyframes swing {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(5deg); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}
</style>
