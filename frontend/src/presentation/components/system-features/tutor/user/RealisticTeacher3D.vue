<!--
  RealisticTeacher3D - 3D Teacher Avatar with VRM, Human, and Robot support

  Features:
  - VRM Avatar support (Ready Player Me, VRoid)
  - Realistic procedural human avatar
  - Robot fallback avatar
  - Animations: idle, talking, pointing, celebrating
  - Lip-sync with TTS
  - Dynamic whiteboard pointing
  - Expression system

  Usage:
  <RealisticTeacher3D
    :vrm-url="'/avatars/teacher.vrm'"
    :animation="'talking'"
    :is-speaking="true"
    :point-at="{x: 0.5, y: 0.3}"
    :expression="'happy'"
  />
-->

<template>
  <div ref="containerRef" class="teacher-container">
    <!-- Loading State -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span class="loading-text">{{ $t('tutor.avatar.loading') }}</span>
    </div>

    <!-- Error State -->
    <div v-if="loadError" class="error-overlay">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ $t(loadError) }}</span>
      <button @click="retryLoad" class="retry-btn">{{ $t('common.retry') }}</button>
    </div>

    <!-- Canvas will be inserted here by Three.js -->
  </div>
</template>

<script setup lang="ts">
/**
 * RealisticTeacher3D - 3D Teacher Avatar Component
 * =================================================
 * Orchestrates VRM, Human, and Robot avatars with animations
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAvatarStore } from '@/application/stores/avatar.store'
import {
  use3DAvatar,
  VRMAvatarLoader,
  HumanAvatarBuilder,
  RobotAvatarBuilder,
  AnimationController,
  type AnimationType,
  type ExpressionType,
  type PointTarget,
  type LoadedAvatar,
  type AvatarParts as _AvatarParts
} from './teacher3d'

// ============================================================================
// i18n
// ============================================================================
const { t } = useI18n()

// ============================================================================
// Props & Emits
// ============================================================================
const props = withDefaults(defineProps<{
  vrmUrl?: string
  animation?: AnimationType
  isSpeaking?: boolean
  pointAt?: PointTarget | null
  expression?: ExpressionType
  showInClassroom?: boolean
  width?: number
  height?: number
  useRealisticHuman?: boolean
}>(), {
  vrmUrl: '',
  animation: 'idle',
  isSpeaking: false,
  pointAt: null,
  expression: 'neutral',
  showInClassroom: true,
  width: 400,
  height: 500,
  useRealisticHuman: true
})

const emit = defineEmits<{
  (e: 'loaded'): void
  (e: 'error', error: string): void
  (e: 'animation-complete', animation: AnimationType): void
}>()

// ============================================================================
// Stores
// ============================================================================
const _avatarStore = useAvatarStore()

// ============================================================================
// State
// ============================================================================
const containerRef = ref<HTMLDivElement | null>(null)

// Animation controller
let animationController: AnimationController | null = null

// ============================================================================
// Composable - 3D Scene Setup
// ============================================================================
const {
  isLoading,
  loadError,
  currentExpression,
  initScene,
  getScene,
  cleanup,
  setVRM,
  setRobotAvatar,
  setHumanModel,
  getClock
} = use3DAvatar(containerRef, {
  width: props.width,
  height: props.height,
  showInClassroom: props.showInClassroom
})

// ============================================================================
// Avatar Loading
// ============================================================================

/**
 * Load avatar (VRM, Human, or Robot)
 */
async function loadAvatar(): Promise<void> {
  const scene = await initScene()
  if (!scene) return

  const clock = getClock()
  if (!clock) return

  // Try VRM first if URL provided
  if (props.vrmUrl) {
    const vrmLoader = new VRMAvatarLoader(
      scene,
      onVRMLoaded,
      onVRMError
    )
    await vrmLoader.loadWithFallback(props.vrmUrl)
    return
  }

  // Try realistic human avatar
  if (props.useRealisticHuman) {
    const vrmLoader = new VRMAvatarLoader(
      scene,
      onHumanLoaded,
      onHumanError
    )
    await vrmLoader.loadReadyPlayerMe()
    return
  }

  // Fallback to robot
  loadRobotAvatar()
}

/**
 * VRM avatar loaded successfully
 */
function onVRMLoaded(avatar: LoadedAvatar): void {
  if (!avatar.vrm) return

  setVRM(avatar.vrm)

  const clock = getClock()
  if (!clock) return

  animationController = new AnimationController(clock, {
    type: 'vrm',
    model: avatar.model!,
    vrm: avatar.vrm
  })

  isLoading.value = false
  emit('loaded')
}

/**
 * VRM loading failed - try human avatar
 */
function onVRMError(_errorKey: string): void {
  console.warn('VRM loading failed, trying human avatar')

  const scene = getScene()
  if (!scene) return

  const vrmLoader = new VRMAvatarLoader(
    scene,
    onHumanLoaded,
    onHumanError
  )
  vrmLoader.loadReadyPlayerMe()
}

/**
 * Human avatar loaded (GLB or procedural)
 */
function onHumanLoaded(avatar: LoadedAvatar): void {
  setHumanModel(avatar.model!)

  const clock = getClock()
  if (!clock) return

  animationController = new AnimationController(clock, {
    type: 'human',
    model: avatar.model!,
    head: avatar.bones?.head,
    spine: avatar.bones?.spine,
    rightArm: avatar.bones?.rightArm,
    leftArm: avatar.bones?.leftArm,
    mouth: avatar.bones?.mouth,
    morphMeshes: avatar.morphMeshes
  })

  isLoading.value = false
  emit('loaded')
}

/**
 * Human loading failed - use procedural or robot
 */
function onHumanError(_errorKey: string): void {
  console.warn('Human GLB loading failed, creating procedural avatar')

  const scene = getScene()
  if (!scene) return

  // Create procedural human
  const builder = new HumanAvatarBuilder(scene)
  const parts = builder.build()

  setHumanModel(parts.model)

  const clock = getClock()
  if (!clock) return

  animationController = new AnimationController(clock, {
    type: 'human',
    model: parts.model,
    head: parts.head,
    spine: parts.spine,
    rightArm: parts.rightArm,
    leftArm: parts.leftArm,
    mouth: parts.mouth
  })

  isLoading.value = false
  emit('loaded')
}

/**
 * Load robot fallback avatar
 */
function loadRobotAvatar(): void {
  const scene = getScene()
  if (!scene) return

  const builder = new RobotAvatarBuilder(scene)
  const parts = builder.build()

  setRobotAvatar(parts.model)

  const clock = getClock()
  if (!clock) return

  animationController = new AnimationController(clock, {
    type: 'robot',
    model: parts.model,
    robotHead: parts.head,
    robotMouth: parts.mouth,
    robotRightArm: parts.rightArm
  })

  isLoading.value = false
  emit('loaded')
}

/**
 * Retry loading avatar
 */
function retryLoad(): void {
  loadError.value = null
  loadAvatar()
}

// ============================================================================
// Animation Updates (Watchers)
// ============================================================================

watch(() => props.isSpeaking, (speaking) => {
  animationController?.setIsSpeaking(speaking)
})

watch(() => props.pointAt, (target) => {
  animationController?.setPointAt(target)
})

watch(() => props.animation, (animation) => {
  animationController?.setAnimation(animation)
})

watch(() => props.expression, (expression) => {
  currentExpression.value = expression
})

// ============================================================================
// Animation Loop
// ============================================================================

function _animate(): void {
  if (!animationController) return
  animationController.update(0)  // Delta handled by controller's clock
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadAvatar()
})

onUnmounted(() => {
  cleanup()
})

// ============================================================================
// Public Methods (exposed via ref)
// ============================================================================

defineExpose({
  setExpression: (expression: ExpressionType) => {
    currentExpression.value = expression
  },
  pointAt: (target: PointTarget | null) => {
    animationController?.setPointAt(target)
  },
  retryLoad
})
</script>

<style scoped>
.teacher-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: transparent;
  overflow: hidden;
}

/* Loading Overlay */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.9);
  color: #e2e8f0;
  z-index: 10;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(59, 130, 246, 0.3);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 0.95rem;
  font-weight: 500;
}

/* Error Overlay */
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 23, 42, 0.9);
  color: #e2e8f0;
  z-index: 10;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-text {
  font-size: 0.95rem;
  margin-bottom: 1rem;
  text-align: center;
  max-width: 80%;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #2563eb;
}
</style>
