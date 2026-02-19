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
 *
 * Uses composables: useAvatar3DScene, useRobotAvatar, useClassroomScene
 */

import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { VRMLoaderPlugin, VRM, VRMExpressionPresetName } from '@pixiv/three-vrm'
import { useAvatarStore } from '@/application/stores/modules/ui/avatar.store'
import { useTutorStore } from '@/application/stores/modules/learning/tutor.store'
import { useAvatar3DScene } from './composables/useAvatar3DScene'
import { useRobotAvatar } from './composables/useRobotAvatar'
import { useClassroomScene } from './composables/useClassroomScene'

const props = defineProps<{
  mode?: 'floating' | 'classroom' | 'whiteboard' | 'fullscreen'
  showWhiteboard?: boolean
  whiteboardContent?: string
}>()

const avatarStore = useAvatarStore()
const tutorStore = useTutorStore()

const container = ref<HTMLDivElement | null>(null)

const {
  scene,
  initScene,
  startAnimationLoop,
  handleResize,
  dispose
} = useAvatar3DScene()

const { createRobotAvatar, animateRobot } = useRobotAvatar()
const { createClassroomScene, updateWhiteboard } = useClassroomScene()

let robotAvatar: THREE.Group | null = null
let vrmAvatar: VRM | null = null
let mixer: THREE.AnimationMixer | null = null

const isClassroom = (): boolean =>
  props.mode === 'classroom' || props.mode === 'whiteboard'

function initAvatar(): void {
  if (!container.value) return

  initScene(container.value, { mode: props.mode })

  if (!scene.value) return

  if (isClassroom() || props.showWhiteboard) {
    createClassroomScene(scene.value, !!props.showWhiteboard)
  }

  if (avatarStore.isRobotStyle) {
    robotAvatar = createRobotAvatar(scene.value, {
      mode: props.mode,
      showWhiteboard: props.showWhiteboard
    })
  } else if (avatarStore.hasVRM) {
    loadVRMAvatar(avatarStore.settings.appearance.vrmUrl!)
  } else {
    robotAvatar = createRobotAvatar(scene.value, {
      mode: props.mode,
      showWhiteboard: props.showWhiteboard
    })
  }

  startAnimationLoop(onFrame)
}

async function loadVRMAvatar(url: string): Promise<void> {
  if (!scene.value) return

  avatarStore.isLoading = true
  avatarStore.loadError = null

  const loader = new GLTFLoader()
  loader.register((parser) => new VRMLoaderPlugin(parser))

  try {
    const gltf = await loader.loadAsync(url)
    vrmAvatar = gltf.userData.vrm as VRM

    vrmAvatar.scene.rotation.y = Math.PI
    vrmAvatar.scene.position.y = isClassroom() ? 0 : -0.5

    if (props.showWhiteboard) {
      vrmAvatar.scene.position.x = -1.2
    }

    scene.value.add(vrmAvatar.scene)

    mixer = new THREE.AnimationMixer(vrmAvatar.scene)

    if (gltf.animations.length > 0) {
      const idleAction = mixer.clipAction(gltf.animations[0])
      idleAction.play()
    }

    avatarStore.isLoaded = true
  } catch (error) {
    console.error('Failed to load VRM:', error)
    avatarStore.loadError = 'VRM konnte nicht geladen werden'
    robotAvatar = createRobotAvatar(scene.value!, {
      mode: props.mode,
      showWhiteboard: props.showWhiteboard
    })
  } finally {
    avatarStore.isLoading = false
  }
}

function onFrame(delta: number, time: number): void {
  if (mixer) {
    mixer.update(delta)
  }

  updateVRMExpressions(delta)

  if (robotAvatar) {
    const lipSync = getLipSyncState()
    animateRobot(robotAvatar, time, {
      isSpeaking: tutorStore.isSpeaking,
      isTyping: tutorStore.isTyping,
      isLoading: tutorStore.isLoading,
      mouthOpen: lipSync.mouthOpen,
      mouthWide: lipSync.mouthWide
    }, isClassroom())
  }
}

function updateVRMExpressions(delta: number): void {
  if (!vrmAvatar) return

  if (tutorStore.isSpeaking) {
    avatarStore.updateLipSync()
    const lipSync = avatarStore.lipSyncData

    vrmAvatar.expressionManager?.setValue(VRMExpressionPresetName.Aa, lipSync.mouthOpen)
    vrmAvatar.expressionManager?.setValue(VRMExpressionPresetName.Ih, lipSync.mouthWide * 0.5)
  } else {
    vrmAvatar.expressionManager?.setValue(VRMExpressionPresetName.Aa, 0)
    vrmAvatar.expressionManager?.setValue(VRMExpressionPresetName.Ih, 0)
  }

  vrmAvatar.update(delta)
}

function getLipSyncState(): { mouthOpen: number; mouthWide: number } {
  if (tutorStore.isSpeaking) {
    avatarStore.updateLipSync()
    return avatarStore.lipSyncData
  }
  return { mouthOpen: 0, mouthWide: 0 }
}

function removeCurrentAvatar(): void {
  if (!scene.value) return

  if (vrmAvatar) {
    scene.value.remove(vrmAvatar.scene)
    vrmAvatar = null
  }
  if (robotAvatar) {
    scene.value.remove(robotAvatar)
    robotAvatar = null
  }
}

function onResize(): void {
  if (container.value) {
    handleResize(container.value)
  }
}

onMounted(() => {
  avatarStore.loadSettings()
  nextTick(() => initAvatar())
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  dispose()
  window.removeEventListener('resize', onResize)
})

watch(() => props.whiteboardContent, (newContent) => {
  if (newContent) {
    updateWhiteboard(newContent)
  }
})

watch(() => avatarStore.settings.appearance.vrmUrl, (newUrl) => {
  if (newUrl && scene.value) {
    removeCurrentAvatar()
    loadVRMAvatar(newUrl)
  }
})

watch(() => avatarStore.settings.appearance.style, (newStyle) => {
  if (scene.value) {
    removeCurrentAvatar()

    if (newStyle === 'robot') {
      robotAvatar = createRobotAvatar(scene.value!, {
        mode: props.mode,
        showWhiteboard: props.showWhiteboard
      })
    } else if (avatarStore.hasVRM) {
      loadVRMAvatar(avatarStore.settings.appearance.vrmUrl!)
    }
  }
})

defineExpose({
  updateWhiteboard
})
</script>

<template>
  <div ref="container" class="w-full h-full"></div>
</template>
