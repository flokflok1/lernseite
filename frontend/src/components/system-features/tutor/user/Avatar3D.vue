<script setup lang="ts">
/**
 * Avatar3D - Advanced 3D Avatar with VRM Support & Lip-Sync
 *
 * Features:
 * - Robot avatar (default, built-in)
 * - VRM avatar support (Ready Player Me, VRoid)
 * - Real-time lip-sync with audio analysis
 * - Multiple animations (idle, talking, thinking, waving)
 * - Whiteboard/Classroom scene mode
 */

import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { VRMLoaderPlugin, VRM, VRMExpressionPresetName } from '@pixiv/three-vrm'
import { useAvatarStore } from '@/store/avatar.store'
import { useTutorStore } from '@/store/tutor.store'

// Props
const props = defineProps<{
  mode?: 'floating' | 'classroom' | 'whiteboard' | 'fullscreen'
  showWhiteboard?: boolean
  whiteboardContent?: string
}>()

// Stores
const avatarStore = useAvatarStore()
const tutorStore = useTutorStore()

// Refs
const container = ref<HTMLDivElement | null>(null)

// Three.js state
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let clock: THREE.Clock
let animationId: number

// Avatar state
let robotAvatar: THREE.Group | null = null
let vrmAvatar: VRM | null = null
let mixer: THREE.AnimationMixer | null = null

// Whiteboard
let whiteboardMesh: THREE.Mesh | null = null
let whiteboardTexture: THREE.CanvasTexture | null = null

// =====================================
// INITIALIZATION
// =====================================

const initScene = () => {
  if (!container.value) return

  const width = container.value.clientWidth
  const height = container.value.clientHeight

  // Scene
  scene = new THREE.Scene()
  scene.background = null // Transparent

  // Camera setup based on mode
  const isClassroom = props.mode === 'classroom' || props.mode === 'whiteboard'
  const fov = isClassroom ? 35 : 45
  camera = new THREE.PerspectiveCamera(fov, width / height, 0.1, 1000)

  if (isClassroom) {
    camera.position.set(0, 1.2, 3)
    camera.lookAt(0, 1, 0)
  } else {
    camera.position.set(0, 0.3, 2)
    camera.lookAt(0, 0.2, 0)
  }

  // Renderer
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.outputColorSpace = THREE.SRGBColorSpace
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1
  container.value.appendChild(renderer.domElement)

  // Lighting
  setupLighting()

  // Create scene based on mode
  if (isClassroom || props.showWhiteboard) {
    createClassroomScene()
  }

  // Create avatar based on style
  if (avatarStore.isRobotStyle) {
    createRobotAvatar()
  } else if (avatarStore.hasVRM) {
    loadVRMAvatar(avatarStore.settings.appearance.vrmUrl!)
  } else {
    createRobotAvatar() // Fallback
  }

  // Clock
  clock = new THREE.Clock()

  // Start animation
  animate()
}

const setupLighting = () => {
  // Ambient light
  const ambient = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambient)

  // Key light
  const keyLight = new THREE.DirectionalLight(0xffffff, 0.8)
  keyLight.position.set(2, 3, 2)
  keyLight.castShadow = true
  scene.add(keyLight)

  // Fill light (blue tint)
  const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3)
  fillLight.position.set(-2, 1, -1)
  scene.add(fillLight)

  // Rim light
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.4)
  rimLight.position.set(0, 2, -3)
  scene.add(rimLight)
}

// =====================================
// ROBOT AVATAR
// =====================================

const createRobotAvatar = () => {
  robotAvatar = new THREE.Group()

  const isClassroom = props.mode === 'classroom' || props.mode === 'whiteboard'
  const scale = isClassroom ? 1.2 : 1

  // Body
  const bodyGeometry = new THREE.CapsuleGeometry(0.25 * scale, 0.4 * scale, 8, 16)
  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: 0x6366f1,
    metalness: 0.3,
    roughness: 0.7
  })
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
  body.position.y = isClassroom ? 0.8 : 0
  robotAvatar.add(body)

  // Head
  const headGeometry = new THREE.SphereGeometry(0.22 * scale, 32, 32)
  const headMaterial = new THREE.MeshStandardMaterial({
    color: 0x818cf8,
    metalness: 0.2,
    roughness: 0.6
  })
  const head = new THREE.Mesh(headGeometry, headMaterial)
  head.position.y = (isClassroom ? 0.8 : 0) + 0.55 * scale
  head.name = 'head'
  robotAvatar.add(head)

  // Eyes
  const eyeGeometry = new THREE.SphereGeometry(0.04 * scale, 16, 16)
  const eyeMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0x88ffff,
    emissiveIntensity: 0.5
  })

  const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
  leftEye.position.set(-0.08 * scale, (isClassroom ? 0.8 : 0) + 0.58 * scale, 0.18 * scale)
  robotAvatar.add(leftEye)

  const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
  rightEye.position.set(0.08 * scale, (isClassroom ? 0.8 : 0) + 0.58 * scale, 0.18 * scale)
  robotAvatar.add(rightEye)

  // Pupils
  const pupilGeometry = new THREE.SphereGeometry(0.02 * scale, 8, 8)
  const pupilMaterial = new THREE.MeshStandardMaterial({ color: 0x1e1b4b })

  const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
  leftPupil.position.set(-0.08 * scale, (isClassroom ? 0.8 : 0) + 0.58 * scale, 0.21 * scale)
  leftPupil.name = 'leftPupil'
  robotAvatar.add(leftPupil)

  const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
  rightPupil.position.set(0.08 * scale, (isClassroom ? 0.8 : 0) + 0.58 * scale, 0.21 * scale)
  rightPupil.name = 'rightPupil'
  robotAvatar.add(rightPupil)

  // Mouth
  const mouthGeometry = new THREE.TorusGeometry(0.06 * scale, 0.015 * scale, 8, 16, Math.PI)
  const mouthMaterial = new THREE.MeshStandardMaterial({ color: 0x312e81 })
  const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
  mouth.position.set(0, (isClassroom ? 0.8 : 0) + 0.48 * scale, 0.18 * scale)
  mouth.rotation.x = Math.PI
  mouth.rotation.z = Math.PI
  mouth.name = 'mouth'
  robotAvatar.add(mouth)

  // Antenna
  const antennaGeometry = new THREE.ConeGeometry(0.03 * scale, 0.15 * scale, 8)
  const antennaMaterial = new THREE.MeshStandardMaterial({
    color: 0xa5b4fc,
    emissive: 0x6366f1,
    emissiveIntensity: 0.3
  })
  const antenna = new THREE.Mesh(antennaGeometry, antennaMaterial)
  antenna.position.y = (isClassroom ? 0.8 : 0) + 0.82 * scale
  antenna.name = 'antenna'
  robotAvatar.add(antenna)

  // Glow ball
  const glowGeometry = new THREE.SphereGeometry(0.04 * scale, 16, 16)
  const glowMaterial = new THREE.MeshStandardMaterial({
    color: 0x22d3ee,
    emissive: 0x22d3ee,
    emissiveIntensity: 1
  })
  const glow = new THREE.Mesh(glowGeometry, glowMaterial)
  glow.position.y = (isClassroom ? 0.8 : 0) + 0.92 * scale
  glow.name = 'glow'
  robotAvatar.add(glow)

  // Arms for classroom mode
  if (isClassroom) {
    // Left arm
    const armGeometry = new THREE.CapsuleGeometry(0.06, 0.3, 4, 8)
    const armMaterial = new THREE.MeshStandardMaterial({ color: 0x6366f1 })

    const leftArm = new THREE.Mesh(armGeometry, armMaterial)
    leftArm.position.set(-0.35, 0.7, 0)
    leftArm.rotation.z = 0.3
    leftArm.name = 'leftArm'
    robotAvatar.add(leftArm)

    // Right arm (pointing at whiteboard)
    const rightArm = new THREE.Mesh(armGeometry, armMaterial)
    rightArm.position.set(0.35, 0.75, 0)
    rightArm.rotation.z = -0.8
    rightArm.name = 'rightArm'
    robotAvatar.add(rightArm)
  }

  // Position robot to side if whiteboard
  if (props.showWhiteboard) {
    robotAvatar.position.x = -1.2
  }

  scene.add(robotAvatar)
}

// =====================================
// VRM AVATAR
// =====================================

const loadVRMAvatar = async (url: string) => {
  avatarStore.isLoading = true
  avatarStore.loadError = null

  const loader = new GLTFLoader()
  loader.register((parser) => new VRMLoaderPlugin(parser))

  try {
    const gltf = await loader.loadAsync(url)
    vrmAvatar = gltf.userData.vrm as VRM

    // Setup VRM
    vrmAvatar.scene.rotation.y = Math.PI
    vrmAvatar.scene.position.y = props.mode === 'classroom' ? 0 : -0.5

    // Position to side if whiteboard
    if (props.showWhiteboard) {
      vrmAvatar.scene.position.x = -1.2
    }

    scene.add(vrmAvatar.scene)

    // Setup animation mixer
    mixer = new THREE.AnimationMixer(vrmAvatar.scene)

    // Load animations if available
    if (gltf.animations.length > 0) {
      const idleAction = mixer.clipAction(gltf.animations[0])
      idleAction.play()
    }

    avatarStore.isLoaded = true
  } catch (error) {
    console.error('Failed to load VRM:', error)
    avatarStore.loadError = 'VRM konnte nicht geladen werden'
    // Fallback to robot
    createRobotAvatar()
  } finally {
    avatarStore.isLoading = false
  }
}

// =====================================
// CLASSROOM SCENE
// =====================================

const createClassroomScene = () => {
  // Floor
  const floorGeometry = new THREE.PlaneGeometry(10, 10)
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0x4a5568,
    roughness: 0.8
  })
  const floor = new THREE.Mesh(floorGeometry, floorMaterial)
  floor.rotation.x = -Math.PI / 2
  floor.position.y = 0
  floor.receiveShadow = true
  scene.add(floor)

  // Back wall
  const wallGeometry = new THREE.PlaneGeometry(10, 5)
  const wallMaterial = new THREE.MeshStandardMaterial({
    color: 0x374151,
    roughness: 0.9
  })
  const wall = new THREE.Mesh(wallGeometry, wallMaterial)
  wall.position.set(0, 2.5, -2)
  scene.add(wall)

  // Whiteboard
  if (props.showWhiteboard) {
    createWhiteboard()
  }
}

const createWhiteboard = () => {
  // Whiteboard frame
  const frameGeometry = new THREE.BoxGeometry(3, 2, 0.1)
  const frameMaterial = new THREE.MeshStandardMaterial({
    color: 0x1f2937,
    roughness: 0.7
  })
  const frame = new THREE.Mesh(frameGeometry, frameMaterial)
  frame.position.set(0.5, 1.3, -1.9)
  scene.add(frame)

  // Whiteboard surface with dynamic texture
  const canvas = document.createElement('canvas')
  canvas.width = 1024
  canvas.height = 680
  const ctx = canvas.getContext('2d')!

  // Initial white background
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // Draw content if provided
  if (props.whiteboardContent) {
    ctx.fillStyle = '#1f2937'
    ctx.font = 'bold 48px Arial'
    ctx.textAlign = 'center'

    // Word wrap and draw
    const lines = wrapText(ctx, props.whiteboardContent, 900)
    lines.forEach((line, i) => {
      ctx.fillText(line, canvas.width / 2, 80 + i * 60)
    })
  }

  whiteboardTexture = new THREE.CanvasTexture(canvas)
  whiteboardTexture.needsUpdate = true

  const boardGeometry = new THREE.PlaneGeometry(2.8, 1.8)
  const boardMaterial = new THREE.MeshStandardMaterial({
    map: whiteboardTexture,
    roughness: 0.1
  })
  whiteboardMesh = new THREE.Mesh(boardGeometry, boardMaterial)
  whiteboardMesh.position.set(0.5, 1.3, -1.84)
  scene.add(whiteboardMesh)
}

const wrapText = (ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string[] => {
  const words = text.split(' ')
  const lines: string[] = []
  let currentLine = ''

  words.forEach(word => {
    const testLine = currentLine + (currentLine ? ' ' : '') + word
    const metrics = ctx.measureText(testLine)

    if (metrics.width > maxWidth && currentLine) {
      lines.push(currentLine)
      currentLine = word
    } else {
      currentLine = testLine
    }
  })

  if (currentLine) {
    lines.push(currentLine)
  }

  return lines
}

// Update whiteboard content
const updateWhiteboard = (content: string) => {
  if (!whiteboardTexture) return

  const canvas = whiteboardTexture.image as HTMLCanvasElement
  const ctx = canvas.getContext('2d')!

  // Clear
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, canvas.width, canvas.height)

  // Draw new content
  ctx.fillStyle = '#1f2937'
  ctx.font = 'bold 48px Arial'
  ctx.textAlign = 'center'

  const lines = wrapText(ctx, content, 900)
  lines.forEach((line, i) => {
    ctx.fillText(line, canvas.width / 2, 80 + i * 60)
  })

  whiteboardTexture.needsUpdate = true
}

// =====================================
// ANIMATION LOOP
// =====================================

const animate = () => {
  animationId = requestAnimationFrame(animate)

  const delta = clock.getDelta()
  const time = clock.getElapsedTime()

  // Update mixer for VRM animations
  if (mixer) {
    mixer.update(delta)
  }

  // Update VRM expressions for lip-sync
  if (vrmAvatar && tutorStore.isSpeaking) {
    avatarStore.updateLipSync()
    const lipSync = avatarStore.lipSyncData

    // Apply to VRM blend shapes
    vrmAvatar.expressionManager?.setValue(VRMExpressionPresetName.Aa, lipSync.mouthOpen)
    vrmAvatar.expressionManager?.setValue(VRMExpressionPresetName.Ih, lipSync.mouthWide * 0.5)
    vrmAvatar.update(delta)
  } else if (vrmAvatar) {
    // Reset expressions
    vrmAvatar.expressionManager?.setValue(VRMExpressionPresetName.Aa, 0)
    vrmAvatar.expressionManager?.setValue(VRMExpressionPresetName.Ih, 0)
    vrmAvatar.update(delta)
  }

  // Robot avatar animations
  if (robotAvatar) {
    animateRobot(time)
  }

  renderer.render(scene, camera)
}

const animateRobot = (time: number) => {
  if (!robotAvatar) return

  const isClassroom = props.mode === 'classroom' || props.mode === 'whiteboard'

  // Floating animation
  if (!isClassroom) {
    robotAvatar.position.y = Math.sin(time * 1.5) * 0.05
  }

  // Gentle rotation
  robotAvatar.rotation.y = Math.sin(time * 0.5) * 0.15

  // Get components
  const head = robotAvatar.getObjectByName('head') as THREE.Mesh
  const antenna = robotAvatar.getObjectByName('antenna') as THREE.Mesh
  const glow = robotAvatar.getObjectByName('glow') as THREE.Mesh
  const mouth = robotAvatar.getObjectByName('mouth') as THREE.Mesh
  const rightArm = robotAvatar.getObjectByName('rightArm') as THREE.Mesh

  // Head bob
  if (head) {
    head.rotation.z = Math.sin(time * 1.5) * 0.08
    head.rotation.x = Math.sin(time * 1.2) * 0.03
  }

  // Antenna sway
  if (antenna) {
    antenna.rotation.z = Math.sin(time * 3) * 0.15
  }

  // Glow effect
  if (glow) {
    const scale = 1 + Math.sin(time * 4) * 0.3
    glow.scale.set(scale, scale, scale)

    const mat = glow.material as THREE.MeshStandardMaterial
    if (tutorStore.isTyping || tutorStore.isLoading) {
      mat.emissive.setHex(0xfbbf24) // Yellow
    } else if (tutorStore.isSpeaking) {
      mat.emissive.setHex(0x22c55e) // Green
    } else {
      mat.emissive.setHex(0x22d3ee) // Cyan
    }
  }

  // Mouth animation (lip-sync)
  if (mouth) {
    if (tutorStore.isSpeaking) {
      avatarStore.updateLipSync()
      const lipSync = avatarStore.lipSyncData
      mouth.scale.y = 1 + lipSync.mouthOpen * 1.5
      mouth.scale.x = 1 + lipSync.mouthWide * 0.8
    } else {
      mouth.scale.y = 1
      mouth.scale.x = 1
    }
  }

  // Arm pointing animation in classroom mode
  if (rightArm && isClassroom) {
    rightArm.rotation.z = -0.8 + Math.sin(time * 0.8) * 0.2
    rightArm.rotation.x = Math.sin(time * 0.5) * 0.1
  }
}

// =====================================
// RESIZE HANDLING
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
  avatarStore.loadSettings()
  nextTick(() => initScene())
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (renderer) {
    renderer.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

// Watch for whiteboard content changes
watch(() => props.whiteboardContent, (newContent) => {
  if (newContent) {
    updateWhiteboard(newContent)
  }
})

// Watch for VRM changes
watch(() => avatarStore.settings.appearance.vrmUrl, (newUrl) => {
  if (newUrl && scene) {
    // Remove old avatar
    if (vrmAvatar) {
      scene.remove(vrmAvatar.scene)
      vrmAvatar = null
    }
    if (robotAvatar) {
      scene.remove(robotAvatar)
      robotAvatar = null
    }
    // Load new VRM
    loadVRMAvatar(newUrl)
  }
})

// Watch for style changes
watch(() => avatarStore.settings.appearance.style, (newStyle) => {
  if (scene) {
    // Remove old avatar
    if (vrmAvatar) {
      scene.remove(vrmAvatar.scene)
      vrmAvatar = null
    }
    if (robotAvatar) {
      scene.remove(robotAvatar)
      robotAvatar = null
    }

    // Create new avatar
    if (newStyle === 'robot') {
      createRobotAvatar()
    } else if (avatarStore.hasVRM) {
      loadVRMAvatar(avatarStore.settings.appearance.vrmUrl!)
    }
  }
})

// Expose for parent
defineExpose({
  updateWhiteboard
})
</script>

<template>
  <div ref="container" class="w-full h-full"></div>
</template>
