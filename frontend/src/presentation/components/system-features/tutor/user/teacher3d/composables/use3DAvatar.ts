/**
 * use3DAvatar Composable
 * =======================
 * Three.js Scene Setup & Animation Loop Management
 * for 3D Teacher Avatar (VRM, Human, Robot)
 */
import { ref, readonly, type Ref } from 'vue'
import * as THREE from 'three'
import { VRM } from '@pixiv/three-vrm'

// ============================================================================
// Types
// ============================================================================

export type AnimationType = 'idle' | 'talking' | 'pointing' | 'thinking' | 'celebrating' | 'explaining' | 'walking' | 'writing'
export type ExpressionType = 'happy' | 'sad' | 'surprised' | 'angry' | 'thinking' | 'neutral'

export interface PointTarget {
  x: number  // 0-1, relative to whiteboard
  y: number  // 0-1, relative to whiteboard
}

export interface AvatarOptions {
  width?: number
  height?: number
  showInClassroom?: boolean
}

// ============================================================================
// Composable
// ============================================================================

export function use3DAvatar(
  containerRef: Ref<HTMLDivElement | null>,
  options: AvatarOptions = {}
) {
  // ==========================================================================
  // State
  // ==========================================================================

  const isLoading = ref(true)
  const loadError = ref<string | null>(null)
  const currentExpression = ref<ExpressionType>('neutral')

  // Three.js objects (mutable, not reactive)
  let renderer: THREE.WebGLRenderer | null = null
  let scene: THREE.Scene | null = null
  let camera: THREE.PerspectiveCamera | null = null
  let clock: THREE.Clock | null = null
  let animationId: number | null = null

  // Avatar objects (set by external loaders)
  let vrm: VRM | null = null
  let robotAvatar: THREE.Group | null = null
  let humanModel: THREE.Group | null = null
  let mixer: THREE.AnimationMixer | null = null

  // ==========================================================================
  // Scene Initialization
  // ==========================================================================

  async function initScene(): Promise<THREE.Scene | null> {
    if (!containerRef.value) return null

    isLoading.value = true
    loadError.value = null

    try {
      // Create scene with TRANSPARENT background
      scene = new THREE.Scene()

      // Create camera - Show avatar from waist up, larger
      camera = new THREE.PerspectiveCamera(
        30,  // Narrow FOV for larger avatar
        (options.width || 400) / (options.height || 500),
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
      renderer.setSize(options.width || 400, options.height || 500)
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
      renderer.outputColorSpace = THREE.SRGBColorSpace
      renderer.toneMapping = THREE.ACESFilmicToneMapping
      renderer.toneMappingExposure = 1.2

      containerRef.value.appendChild(renderer.domElement)

      // Add lights
      setupLighting()

      // Start animation loop
      clock = new THREE.Clock()
      animate()

      isLoading.value = false
      return scene

    } catch (error) {
      console.error('Failed to initialize 3D scene:', error)
      loadError.value = 'error_loading_scene'
      isLoading.value = false
      return null
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

  // ==========================================================================
  // Animation Loop
  // ==========================================================================

  function animate() {
    animationId = requestAnimationFrame(animate)

    if (!renderer || !scene || !camera || !clock) return

    const delta = clock.getDelta()

    // Update mixer for loaded animations
    if (mixer) {
      mixer.update(delta)
    }

    renderer.render(scene, camera)
  }

  // ==========================================================================
  // Avatar Management
  // ==========================================================================

  function setVRM(vrmInstance: VRM | null) {
    vrm = vrmInstance
    if (vrmInstance && scene) {
      mixer = new THREE.AnimationMixer(vrmInstance.scene)
    }
  }

  function setRobotAvatar(robot: THREE.Group | null) {
    robotAvatar = robot
  }

  function setHumanModel(human: THREE.Group | null) {
    humanModel = human
  }

  function getScene(): THREE.Scene | null {
    return scene
  }

  function getVRM(): VRM | null {
    return vrm
  }

  function getRobotAvatar(): THREE.Group | null {
    return robotAvatar
  }

  function getHumanModel(): THREE.Group | null {
    return humanModel
  }

  function getClock(): THREE.Clock | null {
    return clock
  }

  // ==========================================================================
  // Cleanup
  // ==========================================================================

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
    mixer = null
    clock = null
  }

  // ==========================================================================
  // Return
  // ==========================================================================

  return {
    // State
    isLoading: readonly(isLoading),
    loadError: readonly(loadError),
    currentExpression: readonly(currentExpression),

    // Methods - Scene
    initScene,
    getScene,
    cleanup,

    // Methods - Avatar Management
    setVRM,
    setRobotAvatar,
    setHumanModel,
    getVRM,
    getRobotAvatar,
    getHumanModel,
    getClock,

    // Methods - Animation
    animate
  }
}
