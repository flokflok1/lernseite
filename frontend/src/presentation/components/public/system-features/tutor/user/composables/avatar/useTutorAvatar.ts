/**
 * useTutorAvatar - Three.js 3D Avatar Composable
 *
 * Manages the Three.js scene, camera, renderer, and avatar animation
 * for the floating tutor companion widget.
 */

import { onMounted, onUnmounted, nextTick, type Ref } from 'vue'
import * as THREE from 'three'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'

interface UseTutorAvatarOptions {
  avatarContainer: Ref<HTMLDivElement | null>
}

export function useTutorAvatar({ avatarContainer }: UseTutorAvatarOptions): void {
  const tutorStore = useTutorStore()

  let scene: THREE.Scene
  let camera: THREE.PerspectiveCamera
  let renderer: THREE.WebGLRenderer
  let avatar: THREE.Group
  let animationId: number
  let clock: THREE.Clock

  function createPlaceholderAvatar(): void {
    avatar = new THREE.Group()

    // Body
    const bodyGeometry = new THREE.CapsuleGeometry(0.25, 0.4, 8, 16)
    const bodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      metalness: 0.3,
      roughness: 0.7
    })
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
    body.position.y = 0
    avatar.add(body)

    // Head
    const headGeometry = new THREE.SphereGeometry(0.22, 32, 32)
    const headMaterial = new THREE.MeshStandardMaterial({
      color: 0x818cf8,
      metalness: 0.2,
      roughness: 0.6
    })
    const head = new THREE.Mesh(headGeometry, headMaterial)
    head.position.y = 0.55
    head.name = 'head'
    avatar.add(head)

    // Eyes
    const eyeGeometry = new THREE.SphereGeometry(0.04, 16, 16)
    const eyeMaterial = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: 0x88ffff,
      emissiveIntensity: 0.5
    })

    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
    leftEye.position.set(-0.08, 0.58, 0.18)
    avatar.add(leftEye)

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
    rightEye.position.set(0.08, 0.58, 0.18)
    avatar.add(rightEye)

    // Pupils
    const pupilGeometry = new THREE.SphereGeometry(0.02, 8, 8)
    const pupilMaterial = new THREE.MeshStandardMaterial({ color: 0x1e1b4b })

    const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
    leftPupil.position.set(-0.08, 0.58, 0.21)
    leftPupil.name = 'leftPupil'
    avatar.add(leftPupil)

    const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
    rightPupil.position.set(0.08, 0.58, 0.21)
    rightPupil.name = 'rightPupil'
    avatar.add(rightPupil)

    // Mouth
    const mouthGeometry = new THREE.TorusGeometry(0.06, 0.015, 8, 16, Math.PI)
    const mouthMaterial = new THREE.MeshStandardMaterial({ color: 0x312e81 })
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
    mouth.position.set(0, 0.48, 0.18)
    mouth.rotation.x = Math.PI
    mouth.rotation.z = Math.PI
    mouth.name = 'mouth'
    avatar.add(mouth)

    // Antenna
    const antennaGeometry = new THREE.ConeGeometry(0.03, 0.15, 8)
    const antennaMaterial = new THREE.MeshStandardMaterial({
      color: 0xa5b4fc,
      emissive: 0x6366f1,
      emissiveIntensity: 0.3
    })
    const antenna = new THREE.Mesh(antennaGeometry, antennaMaterial)
    antenna.position.y = 0.82
    antenna.name = 'antenna'
    avatar.add(antenna)

    // Glow ball on antenna
    const glowGeometry = new THREE.SphereGeometry(0.04, 16, 16)
    const glowMaterial = new THREE.MeshStandardMaterial({
      color: 0x22d3ee,
      emissive: 0x22d3ee,
      emissiveIntensity: 1
    })
    const glow = new THREE.Mesh(glowGeometry, glowMaterial)
    glow.position.y = 0.92
    glow.name = 'glow'
    avatar.add(glow)

    scene.add(avatar)
  }

  function animate(): void {
    animationId = requestAnimationFrame(animate)

    const time = clock.getElapsedTime()

    if (avatar) {
      avatar.position.y = Math.sin(time * 1.5) * 0.05
      avatar.rotation.y = Math.sin(time * 0.5) * 0.15

      const head = avatar.getObjectByName('head') as THREE.Mesh
      const antenna = avatar.getObjectByName('antenna') as THREE.Mesh
      const glow = avatar.getObjectByName('glow') as THREE.Mesh
      const mouth = avatar.getObjectByName('mouth') as THREE.Mesh

      if (head) {
        head.rotation.z = Math.sin(time * 1.5) * 0.08
        head.rotation.x = Math.sin(time * 1.2) * 0.03
      }

      if (antenna) {
        antenna.rotation.z = Math.sin(time * 3) * 0.15
      }

      if (glow) {
        const scale = 1 + Math.sin(time * 4) * 0.3
        glow.scale.set(scale, scale, scale)

        const mat = glow.material as THREE.MeshStandardMaterial
        if (tutorStore.isTyping || tutorStore.isLoading) {
          mat.emissive.setHex(0xfbbf24)
        } else if (tutorStore.isSpeaking) {
          mat.emissive.setHex(0x22c55e)
        } else {
          mat.emissive.setHex(0x22d3ee)
        }
      }

      if (mouth) {
        if (tutorStore.isSpeaking) {
          mouth.scale.y = 1 + Math.sin(time * 20) * 0.6
          mouth.scale.x = 1 + Math.sin(time * 15) * 0.3
        } else {
          mouth.scale.y = 1
          mouth.scale.x = 1
        }
      }
    }

    renderer.render(scene, camera)
  }

  function initThreeJS(): void {
    if (!avatarContainer.value) return

    const container = avatarContainer.value
    const width = container.clientWidth
    const height = container.clientHeight

    scene = new THREE.Scene()
    scene.background = null

    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
    camera.position.set(0, 0.3, 2)
    camera.lookAt(0, 0.2, 0)

    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: 'default',
        failIfMajorPerformanceCaveat: false
      })
    } catch {
      console.warn('WebGL not available, using fallback')
      container.innerHTML = '<div class="w-full h-full flex items-center justify-center text-4xl">&#x1F916;</div>'
      return
    }
    renderer.setSize(width, height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.setClearColor(0x000000, 0)
    container.appendChild(renderer.domElement)

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(2, 3, 2)
    scene.add(directionalLight)

    const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3)
    fillLight.position.set(-2, 1, -1)
    scene.add(fillLight)

    createPlaceholderAvatar()
    clock = new THREE.Clock()
    animate()
  }

  function handleResize(): void {
    if (!avatarContainer.value || !renderer || !camera) return

    const width = avatarContainer.value.clientWidth
    const height = avatarContainer.value.clientHeight

    camera.aspect = width / height
    camera.updateProjectionMatrix()
    renderer.setSize(width, height)
  }

  onMounted(() => {
    nextTick(() => initThreeJS())
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
}
