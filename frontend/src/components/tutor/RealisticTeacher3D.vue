<!--
  RealisticTeacher3D - VRM-basierter 3D-Lehrer mit Animationen

  Features:
  - VRM Avatar-Support (Ready Player Me, VRoid)
  - Animationen: idle, talking, pointing, thinking, celebrating
  - Lip-Sync mit TTS
  - Dynamisches Zeigen auf Whiteboard-Positionen
  - Expression-System (happy, thinking, neutral)
  - Fallback zu Robot-Avatar wenn VRM nicht verfügbar

  Usage:
  <RealisticTeacher3D
    ref="teacher"
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
      <span class="loading-text">Lade Lehrer...</span>
    </div>

    <!-- Error State -->
    <div v-if="loadError" class="error-overlay">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ loadError }}</span>
      <button @click="retryLoad" class="retry-btn">Erneut versuchen</button>
    </div>

    <!-- Canvas will be inserted here by Three.js -->
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { VRMLoaderPlugin, VRM, VRMExpressionPresetName } from '@pixiv/three-vrm'
import { useAvatarStore } from '@/store/avatar.store'

// ============================================================================
// Types
// ============================================================================
type AnimationType = 'idle' | 'talking' | 'pointing' | 'thinking' | 'celebrating' | 'explaining' | 'walking' | 'writing'
type ExpressionType = 'happy' | 'sad' | 'surprised' | 'angry' | 'thinking' | 'neutral'

interface PointTarget {
  x: number  // 0-1, relative to whiteboard
  y: number  // 0-1, relative to whiteboard
}

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
  useRealisticHuman?: boolean  // NEW: Try to load realistic human avatar
}>(), {
  vrmUrl: '',
  animation: 'idle',
  isSpeaking: false,
  pointAt: null,
  expression: 'neutral',
  showInClassroom: true,
  width: 400,
  height: 500,
  useRealisticHuman: true  // Default: try realistic human first
})

const emit = defineEmits<{
  (e: 'loaded'): void
  (e: 'error', error: string): void
  (e: 'animation-complete', animation: AnimationType): void
}>()

// ============================================================================
// State
// ============================================================================
const containerRef = ref<HTMLDivElement | null>(null)
const isLoading = ref(true)
const loadError = ref<string | null>(null)

const avatarStore = useAvatarStore()

// Three.js objects
let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let vrm: VRM | null = null
let robotAvatar: THREE.Group | null = null
let mixer: THREE.AnimationMixer | null = null
let clock: THREE.Clock | null = null
let animationId: number | null = null

// Animation state
const currentExpression = ref<ExpressionType>('neutral')
const targetArmRotation = ref({ x: 0, y: 0, z: 0 })
const mouthOpenValue = ref(0)

// Robot parts (for fallback)
let robotHead: THREE.Mesh | null = null
let robotMouth: THREE.Mesh | null = null
let robotRightArm: THREE.Mesh | null = null
let robotBody: THREE.Mesh | null = null

// ============================================================================
// Initialization
// ============================================================================
async function initScene() {
  if (!containerRef.value) return

  isLoading.value = true
  loadError.value = null

  try {
    // Create scene with TRANSPARENT background
    scene = new THREE.Scene()
    // No background color - let it be transparent

    // Create camera - Show avatar from waist up, larger
    camera = new THREE.PerspectiveCamera(
      30,  // Narrow FOV for larger avatar
      props.width / props.height,
      0.1,
      100
    )
    // Camera closer, focused on upper body
    camera.position.set(0, 1.3, 1.8)
    camera.lookAt(0, 1.2, 0)

    // Create renderer with transparency
    renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,  // Enable transparency
      powerPreference: 'high-performance'
    })
    renderer.setClearColor(0x000000, 0)  // Transparent background
    renderer.setSize(props.width, props.height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.2

    containerRef.value.appendChild(renderer.domElement)

    // Add lights (no floor/stage - avatar floats on transparent background)
    setupLighting()

    // NO setupStage() - we want transparent background without floor/walls

    // Load avatar - Priority: 1. Custom VRM, 2. Ready Player Me, 3. Robot fallback
    if (props.vrmUrl) {
      await loadVRMAvatar(props.vrmUrl)
    } else if (props.useRealisticHuman) {
      // Try to load a Ready Player Me avatar (GLB format)
      await loadReadyPlayerMeAvatar()
    } else {
      createRobotAvatar()
    }

    // Start animation loop
    clock = new THREE.Clock()
    animate()

    isLoading.value = false
    emit('loaded')
  } catch (error) {
    console.error('Failed to initialize 3D scene:', error)
    loadError.value = 'Fehler beim Laden der 3D-Szene'
    isLoading.value = false
    emit('error', loadError.value)
  }
}

function setupLighting() {
  if (!scene) return

  // Ambient light
  const ambient = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambient)

  // Key light (main)
  const keyLight = new THREE.DirectionalLight(0xffffff, 0.8)
  keyLight.position.set(2, 3, 2)
  scene.add(keyLight)

  // Fill light (soft blue)
  const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3)
  fillLight.position.set(-2, 1, -1)
  scene.add(fillLight)

  // Rim light (back)
  const rimLight = new THREE.DirectionalLight(0xffffff, 0.4)
  rimLight.position.set(0, 2, -3)
  scene.add(rimLight)
}

function setupStage() {
  if (!scene) return

  // Floor
  const floorGeometry = new THREE.PlaneGeometry(10, 10)
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0x334155,
    roughness: 0.8
  })
  const floor = new THREE.Mesh(floorGeometry, floorMaterial)
  floor.rotation.x = -Math.PI / 2
  floor.position.y = 0
  scene.add(floor)

  // Back wall (subtle)
  const wallGeometry = new THREE.PlaneGeometry(10, 5)
  const wallMaterial = new THREE.MeshStandardMaterial({
    color: 0x475569,
    roughness: 0.9
  })
  const wall = new THREE.Mesh(wallGeometry, wallMaterial)
  wall.position.set(0, 2.5, -2)
  scene.add(wall)
}

// ============================================================================
// VRM Avatar Loading
// ============================================================================
async function loadVRMAvatar(url: string) {
  if (!scene) return

  const loader = new GLTFLoader()
  loader.register((parser) => new VRMLoaderPlugin(parser))

  try {
    const gltf = await loader.loadAsync(url)
    vrm = gltf.userData.vrm as VRM

    if (vrm) {
      // Slight angle toward whiteboard (right side)
      vrm.scene.rotation.y = -0.25

      // Position in scene
      vrm.scene.position.set(0, 0, 0)

      scene.add(vrm.scene)

      // Setup animation mixer
      mixer = new THREE.AnimationMixer(vrm.scene)

      console.log('VRM avatar loaded successfully')
    }
  } catch (error) {
    console.warn('Failed to load VRM, falling back to robot:', error)
    createRobotAvatar()
  }
}

// ============================================================================
// Stylized Human Avatar (Realistic-looking procedural human)
// ============================================================================
let humanModel: THREE.Group | null = null
let humanMixer: THREE.AnimationMixer | null = null
let humanHead: THREE.Object3D | null = null
let humanSpine: THREE.Object3D | null = null
let humanRightArm: THREE.Object3D | null = null
let humanLeftArm: THREE.Object3D | null = null
let humanMouth: THREE.Mesh | null = null

async function loadReadyPlayerMeAvatar() {
  if (!scene) return

  const loader = new GLTFLoader()

  // Try to load local avatar file first - include the uploaded Ready Player Me avatar
  const avatarUrls = [
    '/avatars/teacher-rpm.glb',           // Ready Player Me avatar (uploaded)
    '/avatars/teacher-professional.glb',
    '/avatars/teacher.glb'
  ]

  for (const url of avatarUrls) {
    try {
      console.log(`Trying to load avatar from: ${url}`)
      const gltf = await loader.loadAsync(url)

      humanModel = gltf.scene
      humanModel.scale.set(1.1, 1.1, 1.1)  // Slightly larger
      humanModel.position.set(0.15, 0, 0)   // Shift slightly right toward whiteboard
      // Slight angle toward whiteboard (which is on the right side)
      humanModel.rotation.y = -0.3  // ~17 degrees toward whiteboard

      // Ready Player Me avatars need special handling
      // They have morph targets (blend shapes) for expressions and visemes
      const morphMeshes: THREE.Mesh[] = []

      // Find bones and morph target meshes
      // Ready Player Me bone names: Head, Spine, RightArm, LeftArm, RightShoulder, LeftShoulder
      humanModel.traverse((child) => {
        const name = child.name

        // Log all bone names for debugging
        if (child.type === 'Bone') {
          console.log('Found bone:', name)
        }

        // Bones for animation - use EXACT names from Ready Player Me
        if (name === 'Head' && !humanHead) humanHead = child
        if (name === 'Spine' && !humanSpine) humanSpine = child
        // DON'T animate arms for now - the bone structure is complex
        // if (name === 'RightArm' && !humanRightArm) humanRightArm = child
        // if (name === 'LeftArm' && !humanLeftArm) humanLeftArm = child

        // Morph targets (for lip-sync and expressions)
        if (child instanceof THREE.Mesh && child.morphTargetInfluences && child.morphTargetDictionary) {
          morphMeshes.push(child)
          console.log(`Found morph targets in ${child.name}:`, Object.keys(child.morphTargetDictionary))
        }

        // Enable shadows
        if (child instanceof THREE.Mesh) {
          child.castShadow = true
          child.receiveShadow = true
        }
      })

      // Clear arm references for GLB avatars - don't animate them
      humanRightArm = null
      humanLeftArm = null

      // Store morph meshes for lip-sync
      if (morphMeshes.length > 0) {
        (humanModel as any)._morphMeshes = morphMeshes
        console.log(`Ready Player Me avatar has ${morphMeshes.length} morph target meshes`)
      }

      scene.add(humanModel)
      console.log('GLB avatar loaded successfully')
      return

    } catch (error) {
      console.warn(`Failed to load avatar from ${url}:`, error)
    }
  }

  // No GLB file available - create stylized human procedurally
  console.log('Creating stylized human avatar procedurally')
  createStylizedHumanAvatar()
}

function createStylizedHumanAvatar() {
  if (!scene) return

  humanModel = new THREE.Group()

  // Skin tone and clothing colors
  const skinMaterial = new THREE.MeshStandardMaterial({
    color: 0xf5d0c5,  // Natural skin tone
    roughness: 0.6,
    metalness: 0.0
  })

  const hairMaterial = new THREE.MeshStandardMaterial({
    color: 0x4a3728,  // Dark brown hair
    roughness: 0.8,
    metalness: 0.0
  })

  const shirtMaterial = new THREE.MeshStandardMaterial({
    color: 0x3b82f6,  // Blue shirt (professional)
    roughness: 0.7,
    metalness: 0.0
  })

  const pantsMaterial = new THREE.MeshStandardMaterial({
    color: 0x374151,  // Dark gray pants
    roughness: 0.8,
    metalness: 0.0
  })

  const eyeMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    roughness: 0.2
  })

  const irisMaterial = new THREE.MeshStandardMaterial({
    color: 0x4a7c59,  // Green-brown eyes
    roughness: 0.3
  })

  // === HEAD ===
  const headGroup = new THREE.Group()

  // Head shape (slightly oval)
  const headGeometry = new THREE.SphereGeometry(0.14, 32, 32)
  headGeometry.scale(1, 1.15, 1)
  const head = new THREE.Mesh(headGeometry, skinMaterial)
  headGroup.add(head)

  // Hair (styled)
  const hairGeometry = new THREE.SphereGeometry(0.15, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2)
  const hair = new THREE.Mesh(hairGeometry, hairMaterial)
  hair.position.y = 0.02
  hair.scale.set(1, 0.8, 1)
  headGroup.add(hair)

  // Side hair
  const sideHairGeometry = new THREE.BoxGeometry(0.32, 0.08, 0.2)
  sideHairGeometry.translate(0, 0.08, -0.02)
  const sideHair = new THREE.Mesh(sideHairGeometry, hairMaterial)
  headGroup.add(sideHair)

  // Eyes
  const eyeGeometry = new THREE.SphereGeometry(0.025, 16, 16)
  const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
  leftEye.position.set(-0.045, 0.02, 0.12)
  headGroup.add(leftEye)

  const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
  rightEye.position.set(0.045, 0.02, 0.12)
  headGroup.add(rightEye)

  // Irises
  const irisGeometry = new THREE.SphereGeometry(0.012, 12, 12)
  const leftIris = new THREE.Mesh(irisGeometry, irisMaterial)
  leftIris.position.set(-0.045, 0.02, 0.14)
  headGroup.add(leftIris)

  const rightIris = new THREE.Mesh(irisGeometry, irisMaterial)
  rightIris.position.set(0.045, 0.02, 0.14)
  headGroup.add(rightIris)

  // Pupils
  const pupilMaterial = new THREE.MeshStandardMaterial({ color: 0x1a1a1a })
  const pupilGeometry = new THREE.SphereGeometry(0.005, 8, 8)
  const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
  leftPupil.position.set(-0.045, 0.02, 0.15)
  headGroup.add(leftPupil)

  const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
  rightPupil.position.set(0.045, 0.02, 0.15)
  headGroup.add(rightPupil)

  // Eyebrows
  const eyebrowMaterial = new THREE.MeshStandardMaterial({ color: 0x3d2b1f })
  const eyebrowGeometry = new THREE.BoxGeometry(0.04, 0.008, 0.01)
  const leftEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial)
  leftEyebrow.position.set(-0.045, 0.055, 0.12)
  leftEyebrow.rotation.z = 0.1
  headGroup.add(leftEyebrow)

  const rightEyebrow = new THREE.Mesh(eyebrowGeometry, eyebrowMaterial)
  rightEyebrow.position.set(0.045, 0.055, 0.12)
  rightEyebrow.rotation.z = -0.1
  headGroup.add(rightEyebrow)

  // Nose
  const noseGeometry = new THREE.ConeGeometry(0.015, 0.04, 8)
  const nose = new THREE.Mesh(noseGeometry, skinMaterial)
  nose.position.set(0, -0.01, 0.13)
  nose.rotation.x = -0.3
  headGroup.add(nose)

  // Mouth (animated)
  const mouthGeometry = new THREE.BoxGeometry(0.04, 0.008, 0.01)
  const mouthMaterial = new THREE.MeshStandardMaterial({ color: 0xc4756e })
  humanMouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
  humanMouth.position.set(0, -0.06, 0.12)
  headGroup.add(humanMouth)

  // Ears
  const earGeometry = new THREE.SphereGeometry(0.025, 8, 8)
  earGeometry.scale(0.5, 1, 0.7)
  const leftEar = new THREE.Mesh(earGeometry, skinMaterial)
  leftEar.position.set(-0.14, 0, 0)
  headGroup.add(leftEar)

  const rightEar = new THREE.Mesh(earGeometry, skinMaterial)
  rightEar.position.set(0.14, 0, 0)
  headGroup.add(rightEar)

  headGroup.position.y = 1.55
  humanHead = headGroup
  humanModel.add(headGroup)

  // === NECK ===
  const neckGeometry = new THREE.CylinderGeometry(0.05, 0.06, 0.1, 16)
  const neck = new THREE.Mesh(neckGeometry, skinMaterial)
  neck.position.y = 1.4
  humanModel.add(neck)

  // === TORSO ===
  const torsoGroup = new THREE.Group()

  // Shirt/body
  const torsoGeometry = new THREE.CylinderGeometry(0.18, 0.15, 0.45, 16)
  const torso = new THREE.Mesh(torsoGeometry, shirtMaterial)
  torsoGroup.add(torso)

  // Collar
  const collarGeometry = new THREE.TorusGeometry(0.08, 0.02, 8, 16)
  const collarMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff })
  const collar = new THREE.Mesh(collarGeometry, collarMaterial)
  collar.position.y = 0.2
  collar.rotation.x = Math.PI / 2
  torsoGroup.add(collar)

  torsoGroup.position.y = 1.1
  humanSpine = torsoGroup
  humanModel.add(torsoGroup)

  // === ARMS ===
  // Right Arm Group (for pointing)
  const rightArmGroup = new THREE.Group()

  // Upper arm
  const upperArmGeometry = new THREE.CapsuleGeometry(0.04, 0.2, 8, 12)
  const rightUpperArm = new THREE.Mesh(upperArmGeometry, shirtMaterial)
  rightUpperArm.position.y = -0.1
  rightArmGroup.add(rightUpperArm)

  // Lower arm (skin)
  const lowerArmGeometry = new THREE.CapsuleGeometry(0.035, 0.18, 8, 12)
  const rightLowerArm = new THREE.Mesh(lowerArmGeometry, skinMaterial)
  rightLowerArm.position.y = -0.32
  rightArmGroup.add(rightLowerArm)

  // Hand
  const handGeometry = new THREE.SphereGeometry(0.04, 12, 12)
  handGeometry.scale(0.8, 1, 0.6)
  const rightHand = new THREE.Mesh(handGeometry, skinMaterial)
  rightHand.position.y = -0.46
  rightArmGroup.add(rightHand)

  rightArmGroup.position.set(0.22, 1.25, 0)
  rightArmGroup.rotation.z = -0.15
  humanRightArm = rightArmGroup
  humanModel.add(rightArmGroup)

  // Left Arm Group
  const leftArmGroup = new THREE.Group()

  const leftUpperArm = new THREE.Mesh(upperArmGeometry, shirtMaterial)
  leftUpperArm.position.y = -0.1
  leftArmGroup.add(leftUpperArm)

  const leftLowerArm = new THREE.Mesh(lowerArmGeometry, skinMaterial)
  leftLowerArm.position.y = -0.32
  leftArmGroup.add(leftLowerArm)

  const leftHand = new THREE.Mesh(handGeometry, skinMaterial)
  leftHand.position.y = -0.46
  leftArmGroup.add(leftHand)

  leftArmGroup.position.set(-0.22, 1.25, 0)
  leftArmGroup.rotation.z = 0.15
  humanLeftArm = leftArmGroup
  humanModel.add(leftArmGroup)

  // === LEGS ===
  // Hips/Belt area
  const hipsGeometry = new THREE.CylinderGeometry(0.15, 0.14, 0.1, 16)
  const hips = new THREE.Mesh(hipsGeometry, pantsMaterial)
  hips.position.y = 0.82
  humanModel.add(hips)

  // Left leg
  const legGeometry = new THREE.CapsuleGeometry(0.055, 0.35, 8, 12)
  const leftLeg = new THREE.Mesh(legGeometry, pantsMaterial)
  leftLeg.position.set(-0.08, 0.52, 0)
  humanModel.add(leftLeg)

  // Right leg
  const rightLeg = new THREE.Mesh(legGeometry, pantsMaterial)
  rightLeg.position.set(0.08, 0.52, 0)
  humanModel.add(rightLeg)

  // Lower legs (visible below pants)
  const lowerLegGeometry = new THREE.CapsuleGeometry(0.045, 0.25, 8, 12)
  const leftLowerLeg = new THREE.Mesh(lowerLegGeometry, pantsMaterial)
  leftLowerLeg.position.set(-0.08, 0.2, 0)
  humanModel.add(leftLowerLeg)

  const rightLowerLeg = new THREE.Mesh(lowerLegGeometry, pantsMaterial)
  rightLowerLeg.position.set(0.08, 0.2, 0)
  humanModel.add(rightLowerLeg)

  // Shoes
  const shoeMaterial = new THREE.MeshStandardMaterial({ color: 0x1f2937 })
  const shoeGeometry = new THREE.BoxGeometry(0.08, 0.04, 0.14)
  const leftShoe = new THREE.Mesh(shoeGeometry, shoeMaterial)
  leftShoe.position.set(-0.08, 0.02, 0.02)
  humanModel.add(leftShoe)

  const rightShoe = new THREE.Mesh(shoeGeometry, shoeMaterial)
  rightShoe.position.set(0.08, 0.02, 0.02)
  humanModel.add(rightShoe)

  // Position model with slight angle toward whiteboard
  humanModel.position.set(0, 0, 0)
  humanModel.rotation.y = -0.25  // ~15 degrees toward whiteboard (right side)

  scene.add(humanModel)
  console.log('Stylized human avatar created - angled toward whiteboard')
}

// ============================================================================
// Robot Avatar (Fallback) - OPTIMIZED for better visibility
// ============================================================================
function createRobotAvatar() {
  if (!scene) return

  robotAvatar = new THREE.Group()

  // Materials - brighter, more visible colors
  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: 0x6366f1,
    metalness: 0.4,
    roughness: 0.5
  })

  const headMaterial = new THREE.MeshStandardMaterial({
    color: 0x818cf8,
    metalness: 0.3,
    roughness: 0.4
  })

  const eyeMaterial = new THREE.MeshStandardMaterial({
    color: 0xffffff,
    emissive: 0x22d3ee,
    emissiveIntensity: 0.8
  })

  const accentMaterial = new THREE.MeshStandardMaterial({
    color: 0x22d3ee,
    metalness: 0.5,
    roughness: 0.3,
    emissive: 0x22d3ee,
    emissiveIntensity: 0.2
  })

  // Body - LARGER
  const bodyGeometry = new THREE.CapsuleGeometry(0.35, 0.7, 12, 24)
  robotBody = new THREE.Mesh(bodyGeometry, bodyMaterial)
  robotBody.position.y = 1.1
  robotAvatar.add(robotBody)

  // Body accent stripe
  const stripeGeometry = new THREE.TorusGeometry(0.36, 0.02, 8, 32)
  const stripe = new THREE.Mesh(stripeGeometry, accentMaterial)
  stripe.position.y = 1.1
  stripe.rotation.x = Math.PI / 2
  robotAvatar.add(stripe)

  // Head - LARGER
  const headGeometry = new THREE.SphereGeometry(0.32, 32, 32)
  robotHead = new THREE.Mesh(headGeometry, headMaterial)
  robotHead.position.y = 1.95
  robotAvatar.add(robotHead)

  // Head visor/screen effect
  const visorGeometry = new THREE.SphereGeometry(0.28, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2)
  const visorMaterial = new THREE.MeshStandardMaterial({
    color: 0x1e293b,
    metalness: 0.8,
    roughness: 0.2,
    transparent: true,
    opacity: 0.7
  })
  const visor = new THREE.Mesh(visorGeometry, visorMaterial)
  visor.position.set(0, 1.92, 0.05)
  visor.rotation.x = Math.PI / 2
  robotAvatar.add(visor)

  // Eyes - LARGER, more expressive
  const eyeGeometry = new THREE.SphereGeometry(0.07, 16, 16)
  const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
  leftEye.position.set(-0.1, 2.0, 0.25)
  robotAvatar.add(leftEye)

  const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
  rightEye.position.set(0.1, 2.0, 0.25)
  robotAvatar.add(rightEye)

  // Eye pupils
  const pupilGeometry = new THREE.SphereGeometry(0.03, 8, 8)
  const pupilMaterial = new THREE.MeshStandardMaterial({ color: 0x1e293b })
  const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
  leftPupil.position.set(-0.1, 2.0, 0.31)
  robotAvatar.add(leftPupil)

  const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
  rightPupil.position.set(0.1, 2.0, 0.31)
  robotAvatar.add(rightPupil)

  // Mouth - animated bar style
  const mouthGeometry = new THREE.BoxGeometry(0.15, 0.04, 0.02)
  const mouthMaterial = new THREE.MeshStandardMaterial({
    color: 0x22d3ee,
    emissive: 0x22d3ee,
    emissiveIntensity: 0.5
  })
  robotMouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
  robotMouth.position.set(0, 1.85, 0.28)
  robotAvatar.add(robotMouth)

  // Antenna
  const antennaGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.15, 8)
  const antenna = new THREE.Mesh(antennaGeometry, bodyMaterial)
  antenna.position.set(0, 2.35, 0)
  robotAvatar.add(antenna)

  const antennaBall = new THREE.Mesh(new THREE.SphereGeometry(0.04, 8, 8), accentMaterial)
  antennaBall.position.set(0, 2.45, 0)
  robotAvatar.add(antennaBall)

  // Shoulders
  const shoulderGeometry = new THREE.SphereGeometry(0.1, 16, 16)
  const leftShoulder = new THREE.Mesh(shoulderGeometry, bodyMaterial)
  leftShoulder.position.set(-0.45, 1.4, 0)
  robotAvatar.add(leftShoulder)

  const rightShoulder = new THREE.Mesh(shoulderGeometry, bodyMaterial)
  rightShoulder.position.set(0.45, 1.4, 0)
  robotAvatar.add(rightShoulder)

  // Arms - LARGER
  const armGeometry = new THREE.CapsuleGeometry(0.07, 0.4, 8, 12)

  // Left arm
  const leftArm = new THREE.Mesh(armGeometry, bodyMaterial)
  leftArm.position.set(-0.5, 1.1, 0)
  leftArm.rotation.z = 0.2
  robotAvatar.add(leftArm)

  // Left hand
  const handGeometry = new THREE.SphereGeometry(0.08, 16, 16)
  const leftHand = new THREE.Mesh(handGeometry, headMaterial)
  leftHand.position.set(-0.55, 0.75, 0)
  robotAvatar.add(leftHand)

  // Right arm (for pointing)
  robotRightArm = new THREE.Mesh(armGeometry, bodyMaterial)
  robotRightArm.position.set(0.5, 1.1, 0)
  robotRightArm.rotation.z = -0.2
  robotAvatar.add(robotRightArm)

  // Right hand
  const rightHand = new THREE.Mesh(handGeometry, headMaterial)
  rightHand.position.set(0.55, 0.75, 0)
  robotAvatar.add(rightHand)

  // Legs - LARGER
  const legGeometry = new THREE.CapsuleGeometry(0.08, 0.35, 8, 12)

  const leftLeg = new THREE.Mesh(legGeometry, bodyMaterial)
  leftLeg.position.set(-0.15, 0.4, 0)
  robotAvatar.add(leftLeg)

  const rightLeg = new THREE.Mesh(legGeometry, bodyMaterial)
  rightLeg.position.set(0.15, 0.4, 0)
  robotAvatar.add(rightLeg)

  // Feet
  const footGeometry = new THREE.BoxGeometry(0.12, 0.05, 0.18)
  const leftFoot = new THREE.Mesh(footGeometry, bodyMaterial)
  leftFoot.position.set(-0.15, 0.05, 0.03)
  robotAvatar.add(leftFoot)

  const rightFoot = new THREE.Mesh(footGeometry, bodyMaterial)
  rightFoot.position.set(0.15, 0.05, 0.03)
  robotAvatar.add(rightFoot)

  // Position robot with slight angle toward whiteboard
  robotAvatar.position.set(0, 0, 0)
  robotAvatar.rotation.y = -0.25  // ~15 degrees toward whiteboard

  scene.add(robotAvatar)
}

// ============================================================================
// Animation Loop
// ============================================================================
function animate() {
  animationId = requestAnimationFrame(animate)

  if (!renderer || !scene || !camera || !clock) return

  const delta = clock.getDelta()
  const time = clock.getElapsedTime()

  // Update VRM
  if (vrm) {
    vrm.update(delta)

    // Lip sync
    if (props.isSpeaking && vrm.expressionManager) {
      const mouthValue = 0.3 + Math.sin(time * 15) * 0.2
      vrm.expressionManager.setValue(VRMExpressionPresetName.Aa, mouthValue)
    } else if (vrm.expressionManager) {
      vrm.expressionManager.setValue(VRMExpressionPresetName.Aa, 0)
    }
  }

  // Update robot avatar
  if (robotAvatar) {
    // Idle animation (subtle floating)
    if (props.animation === 'idle') {
      robotAvatar.position.y = Math.sin(time * 1.5) * 0.02
    }

    // Head bob when talking
    if (robotHead && props.isSpeaking) {
      robotHead.rotation.z = Math.sin(time * 3) * 0.05
      robotHead.rotation.x = Math.sin(time * 2.5) * 0.03
    }

    // Mouth animation
    if (robotMouth && props.isSpeaking) {
      const mouthScale = 1 + Math.sin(time * 15) * 0.3
      robotMouth.scale.y = mouthScale
    } else if (robotMouth) {
      robotMouth.scale.y = 1
    }

    // Arm pointing
    if (robotRightArm && props.pointAt) {
      // Calculate target rotation based on point position
      const targetZ = -0.5 - props.pointAt.y * 0.8
      const targetX = props.pointAt.x * 0.3
      robotRightArm.rotation.z = THREE.MathUtils.lerp(robotRightArm.rotation.z, targetZ, 0.1)
      robotRightArm.rotation.x = THREE.MathUtils.lerp(robotRightArm.rotation.x, targetX, 0.1)
    } else if (robotRightArm) {
      robotRightArm.rotation.z = THREE.MathUtils.lerp(robotRightArm.rotation.z, -0.3, 0.1)
      robotRightArm.rotation.x = THREE.MathUtils.lerp(robotRightArm.rotation.x, 0, 0.1)
    }

    // Celebrating animation
    if (props.animation === 'celebrating' && robotAvatar) {
      robotAvatar.position.y = Math.abs(Math.sin(time * 5)) * 0.1
      if (robotRightArm) {
        robotRightArm.rotation.z = -1.5 + Math.sin(time * 8) * 0.2
      }
    }
  }

  // Update human model animations (including Ready Player Me GLB)
  if (humanModel) {
    // Subtle idle breathing animation
    if (humanSpine) {
      humanSpine.rotation.x = Math.sin(time * 1.2) * 0.015
    }

    // Head movement when speaking
    if (humanHead && props.isSpeaking) {
      humanHead.rotation.y = Math.sin(time * 2.5) * 0.06
      humanHead.rotation.x = Math.sin(time * 2) * 0.03
      humanHead.rotation.z = Math.sin(time * 1.8) * 0.02
    } else if (humanHead) {
      // Gentle head idle - looking at viewer
      humanHead.rotation.y = THREE.MathUtils.lerp(humanHead.rotation.y, Math.sin(time * 0.5) * 0.02, 0.03)
      humanHead.rotation.x = THREE.MathUtils.lerp(humanHead.rotation.x, 0, 0.05)
      humanHead.rotation.z = THREE.MathUtils.lerp(humanHead.rotation.z, 0, 0.05)
    }

    // Ready Player Me Lip-Sync via Morph Targets (Visemes)
    const morphMeshes = (humanModel as any)._morphMeshes as THREE.Mesh[] | undefined
    if (morphMeshes && props.isSpeaking) {
      // Animate visemes for lip-sync
      const mouthValue = 0.3 + Math.sin(time * 12) * 0.25
      const lipValue = Math.abs(Math.sin(time * 8)) * 0.3

      morphMeshes.forEach(mesh => {
        const dict = mesh.morphTargetDictionary
        const influences = mesh.morphTargetInfluences
        if (!dict || !influences) return

        // Ready Player Me viseme names
        // viseme_aa, viseme_E, viseme_I, viseme_O, viseme_U, viseme_CH, viseme_DD,
        // viseme_FF, viseme_kk, viseme_nn, viseme_PP, viseme_RR, viseme_sil, viseme_SS, viseme_TH
        if (dict['viseme_aa'] !== undefined) influences[dict['viseme_aa']] = mouthValue
        if (dict['viseme_O'] !== undefined) influences[dict['viseme_O']] = lipValue * 0.5
        if (dict['mouthOpen'] !== undefined) influences[dict['mouthOpen']] = mouthValue * 0.8

        // Expression: slight smile when speaking
        if (dict['mouthSmile'] !== undefined) influences[dict['mouthSmile']] = 0.15
      })
    } else if (morphMeshes) {
      // Reset morphs when not speaking
      morphMeshes.forEach(mesh => {
        const dict = mesh.morphTargetDictionary
        const influences = mesh.morphTargetInfluences
        if (!dict || !influences) return

        // Smoothly reset all visemes
        for (const key in dict) {
          if (key.startsWith('viseme_') || key === 'mouthOpen') {
            influences[dict[key]] *= 0.9
          }
        }
      })
    }

    // Fallback: Mouth animation for procedural avatar
    if (humanMouth && props.isSpeaking) {
      const mouthOpen = 0.008 + Math.abs(Math.sin(time * 12)) * 0.015
      humanMouth.scale.y = 1 + mouthOpen * 30
      humanMouth.scale.x = 1 - mouthOpen * 5
    } else if (humanMouth) {
      humanMouth.scale.y = THREE.MathUtils.lerp(humanMouth.scale.y, 1, 0.1)
      humanMouth.scale.x = THREE.MathUtils.lerp(humanMouth.scale.x, 1, 0.1)
    }

    // LEFT arm pointing towards whiteboard (whiteboard is on the RIGHT side of screen)
    // From avatar's perspective facing camera, LEFT arm points to HIS right = screen's right = whiteboard
    if (humanLeftArm && props.pointAt) {
      // Raise left arm to point at whiteboard (to avatar's right side)
      const targetZ = 0.8 + props.pointAt.y * 0.5   // Raise arm outward
      const targetX = -0.4 - props.pointAt.x * 0.3  // Extend toward whiteboard
      humanLeftArm.rotation.z = THREE.MathUtils.lerp(humanLeftArm.rotation.z, targetZ, 0.08)
      humanLeftArm.rotation.x = THREE.MathUtils.lerp(humanLeftArm.rotation.x, targetX, 0.08)
    } else if (humanLeftArm) {
      // Rest position - arm down
      humanLeftArm.rotation.z = THREE.MathUtils.lerp(humanLeftArm.rotation.z, 0.15, 0.05)
      humanLeftArm.rotation.x = THREE.MathUtils.lerp(humanLeftArm.rotation.x, 0, 0.05)
    }

    // Right arm - subtle gestures when speaking, otherwise relaxed
    if (humanRightArm && props.isSpeaking && !props.pointAt) {
      humanRightArm.rotation.z = -0.15 + Math.sin(time * 1.5) * 0.08
    } else if (humanRightArm) {
      humanRightArm.rotation.z = THREE.MathUtils.lerp(humanRightArm.rotation.z, -0.15, 0.05)
    }

    // Celebrating animation
    if (props.animation === 'celebrating') {
      if (humanRightArm) {
        humanRightArm.rotation.z = -1.2 + Math.sin(time * 6) * 0.15
      }
      if (humanLeftArm) {
        humanLeftArm.rotation.z = 1.2 + Math.sin(time * 6 + 0.5) * 0.15
      }
    }

    // Update human mixer
    if (humanMixer) {
      humanMixer.update(delta)
    }
  }

  // Update mixer for loaded animations
  if (mixer) {
    mixer.update(delta)
  }

  renderer.render(scene, camera)
}

// ============================================================================
// Public Methods
// ============================================================================
function setExpression(expression: ExpressionType) {
  currentExpression.value = expression

  if (vrm && vrm.expressionManager) {
    // Reset all expressions
    vrm.expressionManager.setValue(VRMExpressionPresetName.Happy, 0)
    vrm.expressionManager.setValue(VRMExpressionPresetName.Sad, 0)
    vrm.expressionManager.setValue(VRMExpressionPresetName.Surprised, 0)
    vrm.expressionManager.setValue(VRMExpressionPresetName.Angry, 0)

    // Set new expression
    switch (expression) {
      case 'happy':
        vrm.expressionManager.setValue(VRMExpressionPresetName.Happy, 1)
        break
      case 'sad':
        vrm.expressionManager.setValue(VRMExpressionPresetName.Sad, 1)
        break
      case 'surprised':
        vrm.expressionManager.setValue(VRMExpressionPresetName.Surprised, 1)
        break
      case 'angry':
        vrm.expressionManager.setValue(VRMExpressionPresetName.Angry, 1)
        break
    }
  }
}

function pointToPosition(target: PointTarget | null) {
  // Animation is handled in the animate loop
  // This is for external control
}

function retryLoad() {
  cleanup()
  initScene()
}

// ============================================================================
// Cleanup
// ============================================================================
function cleanup() {
  if (animationId) {
    cancelAnimationFrame(animationId)
    animationId = null
  }

  if (renderer && containerRef.value) {
    containerRef.value.removeChild(renderer.domElement)
    renderer.dispose()
    renderer = null
  }

  scene = null
  camera = null
  vrm = null
  robotAvatar = null
  humanModel = null
  humanMixer = null
  humanHead = null
  humanSpine = null
  humanRightArm = null
  humanLeftArm = null
  humanMouth = null
  mixer = null
  clock = null
}

// ============================================================================
// Watchers
// ============================================================================
watch(() => props.expression, (newExp) => {
  setExpression(newExp)
})

watch(() => props.vrmUrl, async (newUrl) => {
  if (newUrl && scene) {
    // Remove old avatar
    if (vrm) {
      scene.remove(vrm.scene)
      vrm = null
    }
    if (robotAvatar) {
      scene.remove(robotAvatar)
      robotAvatar = null
    }

    // Load new avatar
    await loadVRMAvatar(newUrl)
  }
})

// ============================================================================
// Lifecycle
// ============================================================================
onMounted(() => {
  initScene()
})

onUnmounted(() => {
  cleanup()
})

// ============================================================================
// Expose
// ============================================================================
defineExpose({
  setExpression,
  pointToPosition,
  retryLoad,
  isLoading
})
</script>

<style scoped>
.teacher-container {
  position: relative;
  width: 100%;
  height: 100%;
  /* No border-radius, no background - seamless integration */
  overflow: visible;
  background: transparent;
}

.teacher-container :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
  background: transparent;
}

/* Loading */
.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(30, 41, 59, 0.9);
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(99, 102, 241, 0.3);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 1rem;
  color: #94a3b8;
  font-size: 0.875rem;
}

/* Error */
.error-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(30, 41, 59, 0.95);
  z-index: 10;
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.error-text {
  color: #f87171;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #4f46e5;
}
</style>
