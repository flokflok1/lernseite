/**
 * useRobotAvatar - Robot avatar creation and animation
 *
 * Creates the built-in robot avatar with body, head, eyes, antenna,
 * and provides per-frame animation (floating, head bob, lip-sync, glow).
 */

import * as THREE from 'three'

interface RobotAvatarConfig {
  mode?: 'floating' | 'classroom' | 'whiteboard' | 'fullscreen'
  showWhiteboard?: boolean
}

interface RobotAnimationState {
  isSpeaking: boolean
  isTyping: boolean
  isLoading: boolean
  mouthOpen: number
  mouthWide: number
}

interface UseRobotAvatarReturn {
  createRobotAvatar: (scene: THREE.Scene, config: RobotAvatarConfig) => THREE.Group
  animateRobot: (robot: THREE.Group, time: number, state: RobotAnimationState, isClassroom: boolean) => void
}

export function useRobotAvatar(): UseRobotAvatarReturn {

  function createRobotAvatar(scene: THREE.Scene, config: RobotAvatarConfig): THREE.Group {
    const robotAvatar = new THREE.Group()

    const isClassroom = config.mode === 'classroom' || config.mode === 'whiteboard'
    const scale = isClassroom ? 1.2 : 1
    const baseY = isClassroom ? 0.8 : 0

    addBody(robotAvatar, scale, baseY)
    addHead(robotAvatar, scale, baseY)
    addEyes(robotAvatar, scale, baseY)
    addMouth(robotAvatar, scale, baseY)
    addAntenna(robotAvatar, scale, baseY)

    if (isClassroom) {
      addArms(robotAvatar, scale)
    }

    if (config.showWhiteboard) {
      robotAvatar.position.x = -1.2
    }

    scene.add(robotAvatar)
    return robotAvatar
  }

  function addBody(group: THREE.Group, scale: number, baseY: number): void {
    const bodyGeometry = new THREE.CapsuleGeometry(0.25 * scale, 0.4 * scale, 8, 16)
    const bodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      metalness: 0.3,
      roughness: 0.7
    })
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
    body.position.y = baseY
    group.add(body)
  }

  function addHead(group: THREE.Group, scale: number, baseY: number): void {
    const headGeometry = new THREE.SphereGeometry(0.22 * scale, 32, 32)
    const headMaterial = new THREE.MeshStandardMaterial({
      color: 0x818cf8,
      metalness: 0.2,
      roughness: 0.6
    })
    const head = new THREE.Mesh(headGeometry, headMaterial)
    head.position.y = baseY + 0.55 * scale
    head.name = 'head'
    group.add(head)
  }

  function addEyes(group: THREE.Group, scale: number, baseY: number): void {
    const eyeGeometry = new THREE.SphereGeometry(0.04 * scale, 16, 16)
    const eyeMaterial = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: 0x88ffff,
      emissiveIntensity: 0.5
    })

    const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
    leftEye.position.set(-0.08 * scale, baseY + 0.58 * scale, 0.18 * scale)
    group.add(leftEye)

    const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial)
    rightEye.position.set(0.08 * scale, baseY + 0.58 * scale, 0.18 * scale)
    group.add(rightEye)

    const pupilGeometry = new THREE.SphereGeometry(0.02 * scale, 8, 8)
    const pupilMaterial = new THREE.MeshStandardMaterial({ color: 0x1e1b4b })

    const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
    leftPupil.position.set(-0.08 * scale, baseY + 0.58 * scale, 0.21 * scale)
    leftPupil.name = 'leftPupil'
    group.add(leftPupil)

    const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
    rightPupil.position.set(0.08 * scale, baseY + 0.58 * scale, 0.21 * scale)
    rightPupil.name = 'rightPupil'
    group.add(rightPupil)
  }

  function addMouth(group: THREE.Group, scale: number, baseY: number): void {
    const mouthGeometry = new THREE.TorusGeometry(0.06 * scale, 0.015 * scale, 8, 16, Math.PI)
    const mouthMaterial = new THREE.MeshStandardMaterial({ color: 0x312e81 })
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
    mouth.position.set(0, baseY + 0.48 * scale, 0.18 * scale)
    mouth.rotation.x = Math.PI
    mouth.rotation.z = Math.PI
    mouth.name = 'mouth'
    group.add(mouth)
  }

  function addAntenna(group: THREE.Group, scale: number, baseY: number): void {
    const antennaGeometry = new THREE.ConeGeometry(0.03 * scale, 0.15 * scale, 8)
    const antennaMaterial = new THREE.MeshStandardMaterial({
      color: 0xa5b4fc,
      emissive: 0x6366f1,
      emissiveIntensity: 0.3
    })
    const antenna = new THREE.Mesh(antennaGeometry, antennaMaterial)
    antenna.position.y = baseY + 0.82 * scale
    antenna.name = 'antenna'
    group.add(antenna)

    const glowGeometry = new THREE.SphereGeometry(0.04 * scale, 16, 16)
    const glowMaterial = new THREE.MeshStandardMaterial({
      color: 0x22d3ee,
      emissive: 0x22d3ee,
      emissiveIntensity: 1
    })
    const glow = new THREE.Mesh(glowGeometry, glowMaterial)
    glow.position.y = baseY + 0.92 * scale
    glow.name = 'glow'
    group.add(glow)
  }

  function addArms(group: THREE.Group, _scale: number): void {
    const armGeometry = new THREE.CapsuleGeometry(0.06, 0.3, 4, 8)
    const armMaterial = new THREE.MeshStandardMaterial({ color: 0x6366f1 })

    const leftArm = new THREE.Mesh(armGeometry, armMaterial)
    leftArm.position.set(-0.35, 0.7, 0)
    leftArm.rotation.z = 0.3
    leftArm.name = 'leftArm'
    group.add(leftArm)

    const rightArm = new THREE.Mesh(armGeometry, armMaterial)
    rightArm.position.set(0.35, 0.75, 0)
    rightArm.rotation.z = -0.8
    rightArm.name = 'rightArm'
    group.add(rightArm)
  }

  function animateRobot(
    robot: THREE.Group,
    time: number,
    state: RobotAnimationState,
    isClassroom: boolean
  ): void {
    if (!isClassroom) {
      robot.position.y = Math.sin(time * 1.5) * 0.05
    }

    robot.rotation.y = Math.sin(time * 0.5) * 0.15

    const head = robot.getObjectByName('head') as THREE.Mesh
    const antenna = robot.getObjectByName('antenna') as THREE.Mesh
    const glow = robot.getObjectByName('glow') as THREE.Mesh
    const mouth = robot.getObjectByName('mouth') as THREE.Mesh
    const rightArm = robot.getObjectByName('rightArm') as THREE.Mesh

    if (head) {
      head.rotation.z = Math.sin(time * 1.5) * 0.08
      head.rotation.x = Math.sin(time * 1.2) * 0.03
    }

    if (antenna) {
      antenna.rotation.z = Math.sin(time * 3) * 0.15
    }

    if (glow) {
      const glowScale = 1 + Math.sin(time * 4) * 0.3
      glow.scale.set(glowScale, glowScale, glowScale)

      const mat = glow.material as THREE.MeshStandardMaterial
      if (state.isTyping || state.isLoading) {
        mat.emissive.setHex(0xfbbf24)
      } else if (state.isSpeaking) {
        mat.emissive.setHex(0x22c55e)
      } else {
        mat.emissive.setHex(0x22d3ee)
      }
    }

    if (mouth) {
      if (state.isSpeaking) {
        mouth.scale.y = 1 + state.mouthOpen * 1.5
        mouth.scale.x = 1 + state.mouthWide * 0.8
      } else {
        mouth.scale.y = 1
        mouth.scale.x = 1
      }
    }

    if (rightArm && isClassroom) {
      rightArm.rotation.z = -0.8 + Math.sin(time * 0.8) * 0.2
      rightArm.rotation.x = Math.sin(time * 0.5) * 0.1
    }
  }

  return {
    createRobotAvatar,
    animateRobot
  }
}
