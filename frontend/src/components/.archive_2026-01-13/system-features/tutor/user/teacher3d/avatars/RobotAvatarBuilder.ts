/**
 * RobotAvatarBuilder Class
 * ========================
 * Fallback robot teacher avatar with futuristic design
 * Used when VRM/GLB avatar loading fails
 */
import * as THREE from 'three'

// ============================================================================
// Types
// ============================================================================

export interface RobotAvatarParts {
  model: THREE.Group
  head: THREE.Mesh
  body: THREE.Mesh
  rightArm: THREE.Mesh
  mouth: THREE.Mesh
}

// ============================================================================
// RobotAvatarBuilder Class
// ============================================================================

export class RobotAvatarBuilder {
  private scene: THREE.Scene

  // Material definitions
  private bodyMaterial: THREE.MeshStandardMaterial
  private headMaterial: THREE.MeshStandardMaterial
  private eyeMaterial: THREE.MeshStandardMaterial
  private accentMaterial: THREE.MeshStandardMaterial

  constructor(scene: THREE.Scene) {
    this.scene = scene

    // Initialize materials - bright, visible colors
    this.bodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x6366f1,  // Indigo blue
      metalness: 0.4,
      roughness: 0.5
    })

    this.headMaterial = new THREE.MeshStandardMaterial({
      color: 0x818cf8,  // Light indigo
      metalness: 0.3,
      roughness: 0.4
    })

    this.eyeMaterial = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      emissive: 0x22d3ee,  // Cyan glow
      emissiveIntensity: 0.8
    })

    this.accentMaterial = new THREE.MeshStandardMaterial({
      color: 0x22d3ee,  // Cyan accents
      metalness: 0.5,
      roughness: 0.3,
      emissive: 0x22d3ee,
      emissiveIntensity: 0.2
    })
  }

  /**
   * Build complete robot avatar
   */
  build(): RobotAvatarParts {
    const model = new THREE.Group()

    // Build robot parts
    const body = this.buildBody()
    const bodyStripe = this.buildBodyStripe()
    const head = this.buildHead()
    const visor = this.buildVisor()
    const eyes = this.buildEyes()
    const mouth = this.buildMouth()
    const antenna = this.buildAntenna()
    const shoulders = this.buildShoulders()
    const { leftArm, rightArm } = this.buildArms()
    const legs = this.buildLegs()

    // Assemble robot
    model.add(body)
    model.add(bodyStripe)
    model.add(head)
    model.add(visor)
    eyes.forEach(eye => model.add(eye))
    model.add(mouth)
    antenna.forEach(part => model.add(part))
    shoulders.forEach(shoulder => model.add(shoulder))
    model.add(leftArm.arm)
    model.add(leftArm.hand)
    model.add(rightArm.arm)
    model.add(rightArm.hand)
    legs.forEach(leg => model.add(leg))

    // Position with angle toward whiteboard
    model.position.set(0, 0, 0)
    model.rotation.y = -0.25  // ~15° toward whiteboard

    this.scene.add(model)
    console.log('Robot avatar created - fallback mode')

    return {
      model,
      head,
      body,
      rightArm: rightArm.arm,
      mouth
    }
  }

  /**
   * Build robot body
   */
  private buildBody(): THREE.Mesh {
    const bodyGeometry = new THREE.CapsuleGeometry(0.35, 0.7, 12, 24)
    const body = new THREE.Mesh(bodyGeometry, this.bodyMaterial)
    body.position.y = 1.1
    body.name = 'body'
    return body
  }

  /**
   * Build body accent stripe
   */
  private buildBodyStripe(): THREE.Mesh {
    const stripeGeometry = new THREE.TorusGeometry(0.36, 0.02, 8, 32)
    const stripe = new THREE.Mesh(stripeGeometry, this.accentMaterial)
    stripe.position.y = 1.1
    stripe.rotation.x = Math.PI / 2
    return stripe
  }

  /**
   * Build robot head
   */
  private buildHead(): THREE.Mesh {
    const headGeometry = new THREE.SphereGeometry(0.32, 32, 32)
    const head = new THREE.Mesh(headGeometry, this.headMaterial)
    head.position.y = 1.95
    head.name = 'head'
    return head
  }

  /**
   * Build head visor/screen effect
   */
  private buildVisor(): THREE.Mesh {
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
    return visor
  }

  /**
   * Build eyes with pupils
   */
  private buildEyes(): THREE.Mesh[] {
    const eyes: THREE.Mesh[] = []

    // Eye geometry
    const eyeGeometry = new THREE.SphereGeometry(0.07, 16, 16)

    // Left eye
    const leftEye = new THREE.Mesh(eyeGeometry, this.eyeMaterial)
    leftEye.position.set(-0.1, 2.0, 0.25)
    eyes.push(leftEye)

    // Right eye
    const rightEye = new THREE.Mesh(eyeGeometry, this.eyeMaterial)
    rightEye.position.set(0.1, 2.0, 0.25)
    eyes.push(rightEye)

    // Pupils
    const pupilGeometry = new THREE.SphereGeometry(0.03, 8, 8)
    const pupilMaterial = new THREE.MeshStandardMaterial({ color: 0x1e293b })

    const leftPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
    leftPupil.position.set(-0.1, 2.0, 0.31)
    eyes.push(leftPupil)

    const rightPupil = new THREE.Mesh(pupilGeometry, pupilMaterial)
    rightPupil.position.set(0.1, 2.0, 0.31)
    eyes.push(rightPupil)

    return eyes
  }

  /**
   * Build animated mouth (bar style)
   */
  private buildMouth(): THREE.Mesh {
    const mouthGeometry = new THREE.BoxGeometry(0.15, 0.04, 0.02)
    const mouthMaterial = new THREE.MeshStandardMaterial({
      color: 0x22d3ee,
      emissive: 0x22d3ee,
      emissiveIntensity: 0.5
    })
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
    mouth.position.set(0, 1.85, 0.28)
    mouth.name = 'mouth'
    return mouth
  }

  /**
   * Build antenna with ball
   */
  private buildAntenna(): THREE.Mesh[] {
    const parts: THREE.Mesh[] = []

    // Antenna rod
    const antennaGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.15, 8)
    const antenna = new THREE.Mesh(antennaGeometry, this.bodyMaterial)
    antenna.position.set(0, 2.35, 0)
    parts.push(antenna)

    // Antenna ball
    const antennaBall = new THREE.Mesh(
      new THREE.SphereGeometry(0.04, 8, 8),
      this.accentMaterial
    )
    antennaBall.position.set(0, 2.45, 0)
    parts.push(antennaBall)

    return parts
  }

  /**
   * Build shoulders
   */
  private buildShoulders(): THREE.Mesh[] {
    const shoulderGeometry = new THREE.SphereGeometry(0.1, 16, 16)

    const leftShoulder = new THREE.Mesh(shoulderGeometry, this.bodyMaterial)
    leftShoulder.position.set(-0.45, 1.4, 0)

    const rightShoulder = new THREE.Mesh(shoulderGeometry, this.bodyMaterial)
    rightShoulder.position.set(0.45, 1.4, 0)

    return [leftShoulder, rightShoulder]
  }

  /**
   * Build arms with hands
   */
  private buildArms(): {
    leftArm: { arm: THREE.Mesh; hand: THREE.Mesh }
    rightArm: { arm: THREE.Mesh; hand: THREE.Mesh }
  } {
    const armGeometry = new THREE.CapsuleGeometry(0.07, 0.4, 8, 12)
    const handGeometry = new THREE.SphereGeometry(0.08, 16, 16)

    // Left arm
    const leftArm = new THREE.Mesh(armGeometry, this.bodyMaterial)
    leftArm.position.set(-0.5, 1.1, 0)
    leftArm.rotation.z = 0.2

    const leftHand = new THREE.Mesh(handGeometry, this.headMaterial)
    leftHand.position.set(-0.55, 0.75, 0)

    // Right arm (for pointing)
    const rightArm = new THREE.Mesh(armGeometry, this.bodyMaterial)
    rightArm.position.set(0.5, 1.1, 0)
    rightArm.rotation.z = -0.2
    rightArm.name = 'rightArm'

    const rightHand = new THREE.Mesh(handGeometry, this.headMaterial)
    rightHand.position.set(0.55, 0.75, 0)

    return {
      leftArm: { arm: leftArm, hand: leftHand },
      rightArm: { arm: rightArm, hand: rightHand }
    }
  }

  /**
   * Build legs with feet
   */
  private buildLegs(): THREE.Mesh[] {
    const parts: THREE.Mesh[] = []

    const legGeometry = new THREE.CapsuleGeometry(0.08, 0.35, 8, 12)

    // Left leg
    const leftLeg = new THREE.Mesh(legGeometry, this.bodyMaterial)
    leftLeg.position.set(-0.15, 0.4, 0)
    parts.push(leftLeg)

    // Right leg
    const rightLeg = new THREE.Mesh(legGeometry, this.bodyMaterial)
    rightLeg.position.set(0.15, 0.4, 0)
    parts.push(rightLeg)

    // Feet
    const footGeometry = new THREE.BoxGeometry(0.12, 0.05, 0.18)

    const leftFoot = new THREE.Mesh(footGeometry, this.bodyMaterial)
    leftFoot.position.set(-0.15, 0.05, 0.03)
    parts.push(leftFoot)

    const rightFoot = new THREE.Mesh(footGeometry, this.bodyMaterial)
    rightFoot.position.set(0.15, 0.05, 0.03)
    parts.push(rightFoot)

    return parts
  }
}
