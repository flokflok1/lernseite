/**
 * VRMAvatarLoader Class
 * =====================
 * Loads VRM and Ready Player Me GLB avatars
 * with fallback to procedural generation
 */
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { VRM, VRMLoaderPlugin } from '@pixiv/three-vrm'

// ============================================================================
// Types
// ============================================================================

export interface LoadedAvatar {
  type: 'vrm' | 'glb' | 'none'
  model: THREE.Group | null
  vrm: VRM | null
  mixer: THREE.AnimationMixer | null
  morphMeshes?: THREE.Mesh[]
  bones?: {
    head?: THREE.Object3D | null
    spine?: THREE.Object3D | null
    rightArm?: THREE.Object3D | null
    leftArm?: THREE.Object3D | null
    mouth?: THREE.Mesh | null
  }
}

// ============================================================================
// VRMAvatarLoader Class
// ============================================================================

export class VRMAvatarLoader {
  private scene: THREE.Scene
  private onSuccess: (avatar: LoadedAvatar) => void
  private onError: (errorKey: string) => void

  constructor(
    scene: THREE.Scene,
    onSuccess: (avatar: LoadedAvatar) => void,
    onError: (errorKey: string) => void
  ) {
    this.scene = scene
    this.onSuccess = onSuccess
    this.onError = onError
  }

  /**
   * Load VRM avatar from URL
   */
  async loadVRM(url: string): Promise<void> {
    const loader = new GLTFLoader()
    loader.register((parser) => new VRMLoaderPlugin(parser))

    try {
      const gltf = await loader.loadAsync(url)
      const vrm = gltf.userData.vrm as VRM

      if (!vrm) {
        console.warn('No VRM data found in GLTF')
        this.onError('tutor.avatar.error_no_vrm')
        return
      }

      // Position and rotation
      vrm.scene.rotation.y = -0.25  // ~15° toward whiteboard
      vrm.scene.position.set(0, 0, 0)

      this.scene.add(vrm.scene)

      // Setup animation mixer
      const mixer = new THREE.AnimationMixer(vrm.scene)

      console.log('VRM avatar loaded successfully')

      this.onSuccess({
        type: 'vrm',
        model: vrm.scene,
        vrm: vrm,
        mixer: mixer
      })

    } catch (error) {
      console.warn('Failed to load VRM:', error)
      this.onError('tutor.avatar.error_load_vrm')
    }
  }

  /**
   * Load Ready Player Me GLB avatar with fallback to local files
   */
  async loadReadyPlayerMe(): Promise<void> {
    const loader = new GLTFLoader()

    // Try multiple avatar URLs
    const avatarUrls = [
      '/avatars/teacher-rpm.glb',           // Ready Player Me avatar
      '/avatars/teacher-professional.glb',  // Professional avatar
      '/avatars/teacher.glb'                // Fallback avatar
    ]

    for (const url of avatarUrls) {
      try {
        console.log(`Trying to load avatar from: ${url}`)
        const gltf = await loader.loadAsync(url)

        const model = gltf.scene
        model.scale.set(1.1, 1.1, 1.1)  // Slightly larger
        model.position.set(0.15, 0, 0)   // Shift toward whiteboard
        model.rotation.y = -0.3          // ~17° toward whiteboard

        // Ready Player Me avatars have morph targets for expressions and lip-sync
        const morphMeshes: THREE.Mesh[] = []
        const bones: LoadedAvatar['bones'] = {}

        // Find bones and morph target meshes
        model.traverse((child) => {
          const name = child.name

          // Log bones for debugging
          if (child.type === 'Bone') {
            console.log('Found bone:', name)
          }

          // Store bones for animation (Ready Player Me bone names)
          if (name === 'Head' && !bones.head) {
            bones.head = child
          }
          if (name === 'Spine' && !bones.spine) {
            bones.spine = child
          }

          // Morph targets for lip-sync and expressions
          if (child instanceof THREE.Mesh &&
              child.morphTargetInfluences &&
              child.morphTargetDictionary) {
            morphMeshes.push(child)
            console.log(`Found morph targets in ${child.name}:`,
                       Object.keys(child.morphTargetDictionary))
          }

          // Enable shadows
          if (child instanceof THREE.Mesh) {
            child.castShadow = true
            child.receiveShadow = true
          }
        })

        this.scene.add(model)

        // Store morph meshes for animation
        if (morphMeshes.length > 0) {
          ;(model as any)._morphMeshes = morphMeshes
          console.log(`Ready Player Me avatar has ${morphMeshes.length} morph target meshes`)
        }

        console.log('GLB avatar loaded successfully')

        this.onSuccess({
          type: 'glb',
          model: model,
          vrm: null,
          mixer: null,
          morphMeshes: morphMeshes,
          bones: bones
        })

        return

      } catch (error) {
        console.warn(`Failed to load avatar from ${url}:`, error)
      }
    }

    // No GLB file available
    console.log('No GLB avatar available, requesting procedural fallback')
    this.onError('tutor.avatar.error_no_glb')
  }

  /**
   * Try to load VRM with fallback to Ready Player Me
   */
  async loadWithFallback(vrmUrl?: string): Promise<void> {
    if (vrmUrl) {
      try {
        await this.loadVRM(vrmUrl)
        return
      } catch (error) {
        console.warn('VRM failed, trying Ready Player Me', error)
      }
    }

    // Fallback to Ready Player Me
    await this.loadReadyPlayerMe()
  }
}
