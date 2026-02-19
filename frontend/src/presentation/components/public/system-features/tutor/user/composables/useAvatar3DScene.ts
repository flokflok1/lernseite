/**
 * useAvatar3DScene - Three.js scene initialization and lifecycle
 *
 * Manages the core Three.js scene setup including camera, renderer,
 * lighting, animation loop, and resize handling.
 */

import { ref, type Ref } from 'vue'
import * as THREE from 'three'

interface SceneConfig {
  mode?: 'floating' | 'classroom' | 'whiteboard' | 'fullscreen'
}

interface UseAvatar3DSceneReturn {
  scene: Ref<THREE.Scene | null>
  camera: Ref<THREE.PerspectiveCamera | null>
  renderer: Ref<THREE.WebGLRenderer | null>
  clock: Ref<THREE.Clock | null>
  animationId: Ref<number | null>
  initScene: (container: HTMLDivElement, config: SceneConfig) => void
  startAnimationLoop: (onFrame: (delta: number, time: number) => void) => void
  stopAnimationLoop: () => void
  handleResize: (container: HTMLDivElement) => void
  dispose: () => void
}

export function useAvatar3DScene(): UseAvatar3DSceneReturn {
  const scene = ref<THREE.Scene | null>(null) as Ref<THREE.Scene | null>
  const camera = ref<THREE.PerspectiveCamera | null>(null) as Ref<THREE.PerspectiveCamera | null>
  const renderer = ref<THREE.WebGLRenderer | null>(null) as Ref<THREE.WebGLRenderer | null>
  const clock = ref<THREE.Clock | null>(null) as Ref<THREE.Clock | null>
  const animationId = ref<number | null>(null)

  function initScene(container: HTMLDivElement, config: SceneConfig): void {
    const width = container.clientWidth
    const height = container.clientHeight

    const newScene = new THREE.Scene()
    newScene.background = null

    const isClassroom = config.mode === 'classroom' || config.mode === 'whiteboard'
    const fov = isClassroom ? 35 : 45
    const newCamera = new THREE.PerspectiveCamera(fov, width / height, 0.1, 1000)

    if (isClassroom) {
      newCamera.position.set(0, 1.2, 3)
      newCamera.lookAt(0, 1, 0)
    } else {
      newCamera.position.set(0, 0.3, 2)
      newCamera.lookAt(0, 0.2, 0)
    }

    const newRenderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    })
    newRenderer.setSize(width, height)
    newRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    newRenderer.outputColorSpace = THREE.SRGBColorSpace
    newRenderer.toneMapping = THREE.ACESFilmicToneMapping
    newRenderer.toneMappingExposure = 1
    container.appendChild(newRenderer.domElement)

    setupLighting(newScene)

    scene.value = newScene
    camera.value = newCamera
    renderer.value = newRenderer
    clock.value = new THREE.Clock()
  }

  function setupLighting(targetScene: THREE.Scene): void {
    const ambient = new THREE.AmbientLight(0xffffff, 0.6)
    targetScene.add(ambient)

    const keyLight = new THREE.DirectionalLight(0xffffff, 0.8)
    keyLight.position.set(2, 3, 2)
    keyLight.castShadow = true
    targetScene.add(keyLight)

    const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3)
    fillLight.position.set(-2, 1, -1)
    targetScene.add(fillLight)

    const rimLight = new THREE.DirectionalLight(0xffffff, 0.4)
    rimLight.position.set(0, 2, -3)
    targetScene.add(rimLight)
  }

  function startAnimationLoop(onFrame: (delta: number, time: number) => void): void {
    function animate(): void {
      animationId.value = requestAnimationFrame(animate)

      if (!clock.value || !renderer.value || !scene.value || !camera.value) return

      const delta = clock.value.getDelta()
      const time = clock.value.getElapsedTime()

      onFrame(delta, time)

      renderer.value.render(scene.value, camera.value)
    }

    animate()
  }

  function stopAnimationLoop(): void {
    if (animationId.value !== null) {
      cancelAnimationFrame(animationId.value)
      animationId.value = null
    }
  }

  function handleResize(container: HTMLDivElement): void {
    if (!renderer.value || !camera.value) return

    const width = container.clientWidth
    const height = container.clientHeight

    camera.value.aspect = width / height
    camera.value.updateProjectionMatrix()
    renderer.value.setSize(width, height)
  }

  function dispose(): void {
    stopAnimationLoop()
    if (renderer.value) {
      renderer.value.dispose()
    }
  }

  return {
    scene,
    camera,
    renderer,
    clock,
    animationId,
    initScene,
    startAnimationLoop,
    stopAnimationLoop,
    handleResize,
    dispose
  }
}
