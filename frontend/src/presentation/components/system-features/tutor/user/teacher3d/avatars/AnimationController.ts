/**
 * AnimationController Class
 * =========================
 * Handles animations for VRM, Human, and Robot avatars
 * - Lip-sync (VRM expressions, morph targets, procedural)
 * - Arm pointing
 * - Idle animations
 * - Celebration animations
 */
import * as THREE from 'three'
import { VRM, VRMExpressionPresetName } from '@pixiv/three-vrm'

// ============================================================================
// Types
// ============================================================================

export type AnimationType = 'idle' | 'talking' | 'pointing' | 'thinking' | 'celebrating' | 'explaining'

export interface PointTarget {
  x: number  // 0-1, relative to whiteboard
  y: number  // 0-1, relative to whiteboard
}

export interface AvatarParts {
  type: 'vrm' | 'human' | 'robot'

  // Common
  model: THREE.Group

  // VRM-specific
  vrm?: VRM | null

  // Human-specific (including Ready Player Me)
  head?: THREE.Object3D | null
  spine?: THREE.Object3D | null
  rightArm?: THREE.Object3D | null
  leftArm?: THREE.Object3D | null
  mouth?: THREE.Mesh | null
  morphMeshes?: THREE.Mesh[]  // Ready Player Me morph targets

  // Robot-specific
  robotHead?: THREE.Mesh | null
  robotMouth?: THREE.Mesh | null
  robotRightArm?: THREE.Mesh | null
}

// ============================================================================
// AnimationController Class
// ============================================================================

export class AnimationController {
  private clock: THREE.Clock
  private parts: AvatarParts
  private isSpeaking: boolean = false
  private pointAt: PointTarget | null = null
  private animation: AnimationType = 'idle'

  constructor(clock: THREE.Clock, parts: AvatarParts) {
    this.clock = clock
    this.parts = parts
  }

  /**
   * Update isSpeaking state
   */
  setIsSpeaking(speaking: boolean): void {
    this.isSpeaking = speaking
  }

  /**
   * Update pointAt target
   */
  setPointAt(target: PointTarget | null): void {
    this.pointAt = target
  }

  /**
   * Update animation type
   */
  setAnimation(animation: AnimationType): void {
    this.animation = animation
  }

  /**
   * Update all animations (called in animation loop)
   */
  update(delta: number): void {
    const time = this.clock.getElapsedTime()

    switch (this.parts.type) {
      case 'vrm':
        this.updateVRM(delta, time)
        break
      case 'human':
        this.updateHuman(delta, time)
        break
      case 'robot':
        this.updateRobot(delta, time)
        break
    }
  }

  /**
   * Update VRM avatar animations
   */
  private updateVRM(delta: number, time: number): void {
    const vrm = this.parts.vrm
    if (!vrm) return

    vrm.update(delta)

    // Lip sync using VRM expressions
    if (this.isSpeaking && vrm.expressionManager) {
      const mouthValue = 0.3 + Math.sin(time * 15) * 0.2
      vrm.expressionManager.setValue(VRMExpressionPresetName.Aa, mouthValue)
    } else if (vrm.expressionManager) {
      vrm.expressionManager.setValue(VRMExpressionPresetName.Aa, 0)
    }
  }

  /**
   * Update human avatar animations
   */
  private updateHuman(delta: number, time: number): void {
    const { model, head, spine, rightArm, leftArm, mouth, morphMeshes } = this.parts

    // Subtle breathing animation
    if (spine) {
      spine.rotation.x = Math.sin(time * 1.2) * 0.015
    }

    // Head movement when speaking
    if (head && this.isSpeaking) {
      head.rotation.y = Math.sin(time * 2.5) * 0.06
      head.rotation.x = Math.sin(time * 2) * 0.03
      head.rotation.z = Math.sin(time * 1.8) * 0.02
    } else if (head) {
      // Gentle idle - looking at viewer
      head.rotation.y = THREE.MathUtils.lerp(head.rotation.y, Math.sin(time * 0.5) * 0.02, 0.03)
      head.rotation.x = THREE.MathUtils.lerp(head.rotation.x, 0, 0.05)
      head.rotation.z = THREE.MathUtils.lerp(head.rotation.z, 0, 0.05)
    }

    // Ready Player Me lip-sync via morph targets (visemes)
    if (morphMeshes && this.isSpeaking) {
      const mouthValue = 0.3 + Math.sin(time * 12) * 0.25
      const lipValue = Math.abs(Math.sin(time * 8)) * 0.3

      morphMeshes.forEach(mesh => {
        const dict = mesh.morphTargetDictionary
        const influences = mesh.morphTargetInfluences
        if (!dict || !influences) return

        // Animate visemes
        if (dict['viseme_aa'] !== undefined) influences[dict['viseme_aa']] = mouthValue
        if (dict['viseme_O'] !== undefined) influences[dict['viseme_O']] = lipValue * 0.5
        if (dict['mouthOpen'] !== undefined) influences[dict['mouthOpen']] = mouthValue * 0.8

        // Slight smile when speaking
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

    // Fallback: Procedural mouth animation
    if (mouth && this.isSpeaking) {
      const mouthOpen = 0.008 + Math.abs(Math.sin(time * 12)) * 0.015
      mouth.scale.y = 1 + mouthOpen * 30
      mouth.scale.x = 1 - mouthOpen * 5
    } else if (mouth) {
      mouth.scale.y = THREE.MathUtils.lerp(mouth.scale.y, 1, 0.1)
      mouth.scale.x = THREE.MathUtils.lerp(mouth.scale.x, 1, 0.1)
    }

    // Left arm pointing (whiteboard is on avatar's right)
    if (leftArm && this.pointAt) {
      const targetZ = 0.8 + this.pointAt.y * 0.5
      const targetX = -0.4 - this.pointAt.x * 0.3
      leftArm.rotation.z = THREE.MathUtils.lerp(leftArm.rotation.z, targetZ, 0.08)
      leftArm.rotation.x = THREE.MathUtils.lerp(leftArm.rotation.x, targetX, 0.08)
    } else if (leftArm) {
      leftArm.rotation.z = THREE.MathUtils.lerp(leftArm.rotation.z, 0.15, 0.05)
      leftArm.rotation.x = THREE.MathUtils.lerp(leftArm.rotation.x, 0, 0.05)
    }

    // Right arm subtle gestures when speaking
    if (rightArm && this.isSpeaking && !this.pointAt) {
      rightArm.rotation.z = -0.15 + Math.sin(time * 1.5) * 0.08
    } else if (rightArm) {
      rightArm.rotation.z = THREE.MathUtils.lerp(rightArm.rotation.z, -0.15, 0.05)
    }

    // Celebrating animation
    if (this.animation === 'celebrating') {
      if (rightArm) {
        rightArm.rotation.z = -1.2 + Math.sin(time * 6) * 0.15
      }
      if (leftArm) {
        leftArm.rotation.z = 1.2 + Math.sin(time * 6 + 0.5) * 0.15
      }
    }
  }

  /**
   * Update robot avatar animations
   */
  private updateRobot(delta: number, time: number): void {
    const { model, robotHead, robotMouth, robotRightArm } = this.parts

    // Idle floating animation
    if (this.animation === 'idle' && model) {
      model.position.y = Math.sin(time * 1.5) * 0.02
    }

    // Head bob when talking
    if (robotHead && this.isSpeaking) {
      robotHead.rotation.z = Math.sin(time * 3) * 0.05
      robotHead.rotation.x = Math.sin(time * 2.5) * 0.03
    }

    // Mouth animation
    if (robotMouth && this.isSpeaking) {
      const mouthScale = 1 + Math.sin(time * 15) * 0.3
      robotMouth.scale.y = mouthScale
    } else if (robotMouth) {
      robotMouth.scale.y = 1
    }

    // Arm pointing
    if (robotRightArm && this.pointAt) {
      const targetZ = -0.5 - this.pointAt.y * 0.8
      const targetX = this.pointAt.x * 0.3
      robotRightArm.rotation.z = THREE.MathUtils.lerp(robotRightArm.rotation.z, targetZ, 0.1)
      robotRightArm.rotation.x = THREE.MathUtils.lerp(robotRightArm.rotation.x, targetX, 0.1)
    } else if (robotRightArm) {
      robotRightArm.rotation.z = THREE.MathUtils.lerp(robotRightArm.rotation.z, -0.3, 0.1)
      robotRightArm.rotation.x = THREE.MathUtils.lerp(robotRightArm.rotation.x, 0, 0.1)
    }

    // Celebrating animation
    if (this.animation === 'celebrating' && model) {
      model.position.y = Math.abs(Math.sin(time * 5)) * 0.1
      if (robotRightArm) {
        robotRightArm.rotation.z = -1.5 + Math.sin(time * 8) * 0.2
      }
    }
  }
}
