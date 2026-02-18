<!--
  WhiteboardChalkboard - Classic green chalkboard sub-component
  Extracted from WhiteboardTutorLesson for quality gate G01 compliance.
-->

<template>
  <div class="chalkboard-container">
    <!-- Wooden frame -->
    <div class="chalkboard-frame">
      <!-- Green board surface -->
      <div class="chalkboard-surface">
        <!-- Title in chalk style -->
        <h2 class="chalk-title">{{ title || $t('lesson.whiteboard.defaultTitle') }}</h2>
        <!-- Content area -->
        <InteractiveWhiteboard
          ref="whiteboardRef"
          :width="580"
          :height="340"
          :title="''"
          :show-controls="false"
          :background-color="'transparent'"
          :text-color="'#f5f5dc'"
          class="chalk-content"
        />
      </div>
      <!-- Chalk tray -->
      <div class="chalk-tray">
        <div class="chalk white"></div>
        <div class="chalk yellow"></div>
        <div class="chalk red"></div>
        <div class="eraser"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { InteractiveWhiteboard } from '@/presentation/components/public/system-features/tutor/user'
import type { WhiteboardAction } from '@/application/composables/system/useTeachingTimeline'

defineProps<{
  title: string
}>()

const whiteboardRef = ref<InstanceType<typeof InteractiveWhiteboard> | null>(null)

async function executeAction(action: WhiteboardAction): Promise<void> {
  if (whiteboardRef.value) {
    await whiteboardRef.value.executeAction(action)
  }
}

defineExpose({ executeAction })
</script>

<style scoped>
.chalkboard-container {
  flex: 1;
  max-width: 750px;
  min-width: 550px;
}

.chalkboard-frame {
  background: linear-gradient(180deg, #8B4513 0%, #654321 50%, #4a3520 100%);
  padding: 20px;
  border-radius: 8px;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    inset 0 2px 4px rgba(255, 255, 255, 0.1),
    inset 0 -2px 4px rgba(0, 0, 0, 0.2);
  position: relative;
}

/* Wood grain texture */
.chalkboard-frame::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.05) 2px,
    rgba(0, 0, 0, 0.05) 4px
  );
  border-radius: 8px;
  pointer-events: none;
}

.chalkboard-surface {
  background: linear-gradient(170deg, #2d5a3d 0%, #1e4a2e 50%, #1a3d26 100%);
  border-radius: 4px;
  padding: 1.5rem;
  min-height: 380px;
  position: relative;
  box-shadow:
    inset 0 2px 8px rgba(0, 0, 0, 0.3),
    inset 0 0 20px rgba(0, 0, 0, 0.1);
}

/* Chalk dust texture */
.chalkboard-surface::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 30%, rgba(255,255,255,0.03) 1px, transparent 1px),
    radial-gradient(circle at 60% 70%, rgba(255,255,255,0.02) 1px, transparent 1px),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
}

.chalk-title {
  font-family: 'Segoe UI', sans-serif;
  font-size: 1.75rem;
  font-weight: 600;
  color: #f5f5dc;
  text-shadow:
    1px 1px 2px rgba(0, 0, 0, 0.3),
    0 0 10px rgba(245, 245, 220, 0.1);
  margin: 0 0 1rem 0;
  text-align: center;
  letter-spacing: 1px;
}

.chalk-content {
  background: transparent !important;
  color: #f5f5dc !important;
}

/* Make InteractiveWhiteboard use chalk colors */
.chalk-content :deep(canvas) {
  background: transparent !important;
}

.chalk-content :deep(.whiteboard-text) {
  color: #f5f5dc !important;
  text-shadow: 1px 1px 1px rgba(0, 0, 0, 0.3);
}

/* Chalk tray at bottom */
.chalk-tray {
  background: linear-gradient(180deg, #654321 0%, #4a3520 100%);
  height: 25px;
  margin-top: 8px;
  border-radius: 0 0 4px 4px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
}

.chalk {
  width: 40px;
  height: 10px;
  border-radius: 2px;
  box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.chalk.white {
  background: linear-gradient(180deg, #f5f5f5 0%, #e0e0e0 100%);
}

.chalk.yellow {
  background: linear-gradient(180deg, #ffd54f 0%, #ffca28 100%);
}

.chalk.red {
  background: linear-gradient(180deg, #ef5350 0%, #e53935 100%);
}

.eraser {
  width: 50px;
  height: 16px;
  background: linear-gradient(180deg, #8d6e63 0%, #6d4c41 100%);
  border-radius: 2px;
  margin-left: auto;
  box-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}
</style>
