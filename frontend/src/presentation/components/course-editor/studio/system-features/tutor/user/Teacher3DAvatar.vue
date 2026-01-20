<script setup lang="ts">
/**
 * Teacher3DAvatar - Real-time 3D Avatar for Whiteboard Tutor
 *
 * Features:
 * - VRM model with realistic animations
 * - Real-time lip-sync while speaking
 * - Pointing gestures toward whiteboard
 * - Idle breathing and blinking animations
 * - Smooth transitions between states
 */

import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { VRMLoaderPlugin, VRM, VRMExpressionPresetName, VRMHumanBoneName } from '@pixiv/three-vrm'

// Props
const props = defineProps<{
  isSpeaking?: boolean
  isPointing?: boolean
  modelUrl?: string
}>()

// Emits
const emit = defineEmits<{
  (e: 'loaded'): void
  (e: 'error', error: string): void
}>()

// Refs
const container = ref<HTMLDivElement | null>(null)
const isLoaded = ref(false)
const loadProgress = ref(0)

// Three.js objects
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let clock: THREE.Clock
let animationId: number
let vrm: VRM | null = null

// Animation state
let blinkTimer = 0
let breathTimer = 0
let talkTimer = 0
let currentMouthOpen = 0
let targetMouthOpen = 0

// Default VRM model - Seed-san (more professional looking)
const defaultModelUrl = '/avatars/teacher/teacher2.vrm'

// =====================================
// INITIALIZATION
// =====================================

const initScene = async () => {
  if (!container.value) return

  const width = container.value.clientWidth
  const height = container.value.clientHeight

  // Scene with transparent background
  scene = new THREE.Scene()
  scene.background = null

  // Camera - positioned to show upper body
  camera = new THREE.PerspectiveCamera(30, width / height, 0.1, 100)
  camera.position.set(0, 1.3, 2.5)
  camera.lookAt(0, 1.2, 0)

  // Renderer with transparency
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  container.value.appendChild(renderer.domElement)

  // Lighting setup for character
  setupLighting()

  // Clock for animations
  clock = new THREE.Clock()

  // Load VRM model
  await loadVRM(props.modelUrl || defaultModelUrl)

  // Start render loop
  animate()
}

const setupLighting = () => {
  // Soft ambient light
  const ambient = new THREE.AmbientLight(0xffffff, 0.7)
  scene.add(ambient)

  // Main key light (front-top-right)
  const keyLight = new THREE.DirectionalLight(0xffffff, 1.0)
  keyLight.position.set(2, 3, 3)
  scene.add(keyLight)

  // Fill light (front-left, softer)
  const fillLight = new THREE.DirectionalLight(0xaaccff, 0.4)
  fillLight.position.set(-2, 2, 2)
  scene.add(fillLight)

  // Rim light from behind
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.3)
  rimLight.position.set(0, 2, -2)
  scene.add(rimLight)

  // Bottom fill to reduce harsh shadows
  const bottomLight = new THREE.DirectionalLight(0xffeedd, 0.2)
  bottomLight.position.set(0, -1, 1)
  scene.add(bottomLight)
}

// =====================================
// VRM LOADING
// =====================================

const loadVRM = async (url: string) => {
  const loader = new GLTFLoader()

  // Register VRM plugin
  loader.register((parser) => new VRMLoaderPlugin(parser))

  try {
    const gltf = await new Promise<any>((resolve, reject) => {
      loader.load(
        url,
        (gltf) => resolve(gltf),
        (progress) => {
          if (progress.total > 0) {
            loadProgress.value = Math.round((progress.loaded / progress.total) * 100)
          }
        },
        (error) => reject(error)
      )
    })

    vrm = gltf.userData.vrm as VRM

    // VRM is loaded facing -Z, rotate to face camera
    vrm.scene.rotation.y = Math.PI

    // Position the avatar
    vrm.scene.position.set(0, 0, 0)

    scene.add(vrm.scene)

    // Initialize expressions
    if (vrm.expressionManager) {
      vrm.expressionManager.setValue(VRMExpressionPresetName.Neutral, 1)
    }

    isLoaded.value = true
    emit('loaded')

  } catch (error) {
    console.error('Failed to load VRM:', error)
    emit('error', 'VRM konnte nicht geladen werden')
  }
}

// =====================================
// ANIMATION LOOP
// =====================================

const animate = () => {
  animationId = requestAnimationFrame(animate)

  const delta = clock.getDelta()
  const time = clock.getElapsedTime()

  if (vrm) {
    // Update timers
    blinkTimer += delta
    breathTimer += delta
    talkTimer += delta

    // Blink animation (every 3-5 seconds)
    updateBlink()

    // Breathing animation
    updateBreathing(time)

    // Lip-sync when speaking
    updateLipSync(delta)

    // Pointing gesture
    updatePointing()

    // Update VRM
    vrm.update(delta)
  }

  renderer.render(scene, camera)
}

// =====================================
// ANIMATIONS
// =====================================

const updateBlink = () => {
  if (!vrm?.expressionManager) return

  // Random blink interval (2-5 seconds)
  const blinkInterval = 3 + Math.random() * 2

  if (blinkTimer > blinkInterval) {
    // Quick blink
    vrm.expressionManager.setValue(VRMExpressionPresetName.Blink, 1)
    setTimeout(() => {
      if (vrm?.expressionManager) {
        vrm.expressionManager.setValue(VRMExpressionPresetName.Blink, 0)
      }
    }, 100)
    blinkTimer = 0
  }
}

const updateBreathing = (time: number) => {
  if (!vrm?.humanoid) return

  // Subtle chest movement for breathing
  const chest = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.Chest)
  if (chest) {
    // Very subtle breathing motion
    const breathAmount = Math.sin(time * 1.5) * 0.01
    chest.rotation.x = breathAmount
  }

  // Subtle head movement
  const head = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.Head)
  if (head) {
    head.rotation.y = Math.sin(time * 0.5) * 0.05
    head.rotation.x = Math.sin(time * 0.3) * 0.02
  }
}

const updateLipSync = (delta: number) => {
  if (!vrm?.expressionManager) return

  if (props.isSpeaking) {
    // Generate natural-looking mouth movement
    talkTimer += delta * 15

    // Create varied mouth shapes
    const baseOpen = 0.3 + Math.sin(talkTimer * 1.5) * 0.2
    const variation = Math.sin(talkTimer * 3.7) * 0.15
    targetMouthOpen = Math.max(0, Math.min(1, baseOpen + variation))

    // Add some 'ih' and 'oh' shapes for variety
    const ihAmount = Math.max(0, Math.sin(talkTimer * 2.3) * 0.3)
    const ohAmount = Math.max(0, Math.sin(talkTimer * 1.8 + 1) * 0.3)

    vrm.expressionManager.setValue(VRMExpressionPresetName.Ih, ihAmount)
    vrm.expressionManager.setValue(VRMExpressionPresetName.Oh, ohAmount)

    // Slightly raised eyebrows while speaking
    vrm.expressionManager.setValue(VRMExpressionPresetName.Happy, 0.2)
  } else {
    targetMouthOpen = 0
    talkTimer = 0

    // Reset other expressions
    vrm.expressionManager.setValue(VRMExpressionPresetName.Ih, 0)
    vrm.expressionManager.setValue(VRMExpressionPresetName.Oh, 0)
    vrm.expressionManager.setValue(VRMExpressionPresetName.Happy, 0)
  }

  // Smooth interpolation for mouth
  currentMouthOpen += (targetMouthOpen - currentMouthOpen) * 0.3
  vrm.expressionManager.setValue(VRMExpressionPresetName.Aa, currentMouthOpen)
}

const updatePointing = () => {
  if (!vrm?.humanoid) return

  const rightUpperArm = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.RightUpperArm)
  const rightLowerArm = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.RightLowerArm)
  const rightHand = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.RightHand)

  if (props.isPointing) {
    // Raise arm to point at whiteboard (to the right)
    if (rightUpperArm) {
      // Smoothly transition to pointing pose
      rightUpperArm.rotation.z = THREE.MathUtils.lerp(rightUpperArm.rotation.z, -1.2, 0.1)
      rightUpperArm.rotation.x = THREE.MathUtils.lerp(rightUpperArm.rotation.x, 0.3, 0.1)
    }
    if (rightLowerArm) {
      rightLowerArm.rotation.y = THREE.MathUtils.lerp(rightLowerArm.rotation.y, 0.5, 0.1)
    }
    if (rightHand) {
      // Point finger
      rightHand.rotation.x = THREE.MathUtils.lerp(rightHand.rotation.x, -0.3, 0.1)
    }

    // Turn head slightly toward whiteboard
    const head = vrm.humanoid.getNormalizedBoneNode(VRMHumanBoneName.Head)
    if (head) {
      head.rotation.y = THREE.MathUtils.lerp(head.rotation.y, 0.3, 0.1)
    }
  } else {
    // Return to neutral pose
    if (rightUpperArm) {
      rightUpperArm.rotation.z = THREE.MathUtils.lerp(rightUpperArm.rotation.z, 0, 0.1)
      rightUpperArm.rotation.x = THREE.MathUtils.lerp(rightUpperArm.rotation.x, 0, 0.1)
    }
    if (rightLowerArm) {
      rightLowerArm.rotation.y = THREE.MathUtils.lerp(rightLowerArm.rotation.y, 0, 0.1)
    }
    if (rightHand) {
      rightHand.rotation.x = THREE.MathUtils.lerp(rightHand.rotation.x, 0, 0.1)
    }
  }
}

// =====================================
// RESIZE
// =====================================

const handleResize = () => {
  if (!container.value || !renderer || !camera) return

  const width = container.value.clientWidth
  const height = container.value.clientHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

// =====================================
// LIFECYCLE
// =====================================

onMounted(() => {
  initScene()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }

  // Cleanup Three.js resources
  if (renderer) {
    renderer.dispose()
  }
  if (vrm) {
    vrm.scene.traverse((obj) => {
      if (obj instanceof THREE.Mesh) {
        obj.geometry?.dispose()
        if (Array.isArray(obj.material)) {
          obj.material.forEach(m => m.dispose())
        } else {
          obj.material?.dispose()
        }
      }
    })
  }

  window.removeEventListener('resize', handleResize)
})

// Watch for model URL changes
watch(() => props.modelUrl, async (newUrl) => {
  if (newUrl && scene && vrm) {
    scene.remove(vrm.scene)
    vrm = null
    isLoaded.value = false
    await loadVRM(newUrl)
  }
})
</script>

<template>
  <div class="teacher-3d-container">
    <div ref="container" class="avatar-canvas"></div>

    <!-- Loading indicator -->
    <div v-if="!isLoaded" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="loading-text">Avatar lädt... {{ loadProgress }}%</p>
    </div>
  </div>
</template>

<style scoped>
.teacher-3d-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.avatar-canvas {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(4px);
  border-radius: inherit;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: #60a5fa;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 1rem;
  color: white;
  font-size: 0.875rem;
}
</style>
