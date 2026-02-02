/**
 * HumanAvatarBuilder Class
 * ========================
 * Procedural generation of stylized human teacher avatar
 * with realistic proportions and professional appearance
 */
import * as THREE from 'three'

// ============================================================================
// Types
// ============================================================================

export interface HumanAvatarParts {
  model: THREE.Group
  head: THREE.Group
  spine: THREE.Group
  rightArm: THREE.Group
  leftArm: THREE.Group
  mouth: THREE.Mesh
}

// ============================================================================
// HumanAvatarBuilder Class
// ============================================================================

export class HumanAvatarBuilder {
  private scene: THREE.Scene

  // Material definitions
  private skinMaterial: THREE.MeshStandardMaterial
  private hairMaterial: THREE.MeshStandardMaterial
  private shirtMaterial: THREE.MeshStandardMaterial
  private pantsMaterial: THREE.MeshStandardMaterial
  private eyeMaterial: THREE.MeshStandardMaterial
  private irisMaterial: THREE.MeshStandardMaterial

  constructor(scene: THREE.Scene) {
    this.scene = scene

    // Initialize materials
    this.skinMaterial = new THREE.MeshStandardMaterial({
      color: 0xf5d0c5,  // Natural skin tone
      roughness: 0.6,
      metalness: 0.0
    })

    this.hairMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a3728,  // Dark brown hair
      roughness: 0.8,
      metalness: 0.0
    })

    this.shirtMaterial = new THREE.MeshStandardMaterial({
      color: 0x3b82f6,  // Blue shirt (professional)
      roughness: 0.7,
      metalness: 0.0
    })

    this.pantsMaterial = new THREE.MeshStandardMaterial({
      color: 0x374151,  // Dark gray pants
      roughness: 0.8,
      metalness: 0.0
    })

    this.eyeMaterial = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.2
    })

    this.irisMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a7c59,  // Green-brown eyes
      roughness: 0.3
    })
  }

  /**
   * Build complete stylized human avatar
   */
  build(): HumanAvatarParts {
    const model = new THREE.Group()

    // Build avatar parts
    const head = this.buildHead()
    const neck = this.buildNeck()
    const spine = this.buildTorso()
    const rightArm = this.buildRightArm()
    const leftArm = this.buildLeftArm()
    const legs = this.buildLegs()

    // Assemble avatar
    model.add(head)
    model.add(neck)
    model.add(spine)
    model.add(rightArm)
    model.add(leftArm)
    legs.forEach(leg => model.add(leg))

    // Position with angle toward whiteboard
    model.position.set(0, 0, 0)
    model.rotation.y = -0.25  // ~15° toward whiteboard

    this.scene.add(model)
    console.log('Stylized human avatar created - angled toward whiteboard')

    return {
      model,
      head,
      spine,
      rightArm,
      leftArm,
      mouth: this.findMouthMesh(head)
    }
  }

  /**
   * Build head with face features
   */
  private buildHead(): THREE.Group {
    const headGroup = new THREE.Group()

    // Head shape (slightly oval)
    const headGeometry = new THREE.SphereGeometry(0.14, 32, 32)
    headGeometry.scale(1, 1.15, 1)
    const head = new THREE.Mesh(headGeometry, this.skinMaterial)
    headGroup.add(head)

    // Hair
    this.addHair(headGroup)

    // Eyes
    this.addEyes(headGroup)

    // Eyebrows
    this.addEyebrows(headGroup)

    // Nose
    const noseGeometry = new THREE.ConeGeometry(0.015, 0.04, 8)
    const nose = new THREE.Mesh(noseGeometry, this.skinMaterial)
    nose.position.set(0, -0.01, 0.13)
    nose.rotation.x = -0.3
    headGroup.add(nose)

    // Mouth (animated, named for easy reference)
    const mouthGeometry = new THREE.BoxGeometry(0.04, 0.008, 0.01)
    const mouthMaterial = new THREE.MeshStandardMaterial({ color: 0xc4756e })
    const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial)
    mouth.position.set(0, -0.06, 0.12)
    mouth.name = 'mouth'  // Named for finding later
    headGroup.add(mouth)

    // Ears
    this.addEars(headGroup)

    headGroup.position.y = 1.55
    headGroup.name = 'head'
    return headGroup
  }

  /**
   * Add hair to head
   */
  private addHair(headGroup: THREE.Group): void {
    // Main hair (top)
    const hairGeometry = new THREE.SphereGeometry(0.15, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2)
    const hair = new THREE.Mesh(hairGeometry, this.hairMaterial)
    hair.position.y = 0.02
    hair.scale.set(1, 0.8, 1)
    headGroup.add(hair)

    // Side hair
    const sideHairGeometry = new THREE.BoxGeometry(0.32, 0.08, 0.2)
    sideHairGeometry.translate(0, 0.08, -0.02)
    const sideHair = new THREE.Mesh(sideHairGeometry, this.hairMaterial)
    headGroup.add(sideHair)
  }

  /**
   * Add eyes to head
   */
  private addEyes(headGroup: THREE.Group): void {
    const eyeGeometry = new THREE.SphereGeometry(0.025, 16, 16)

    // Left eye
    const leftEye = new THREE.Mesh(eyeGeometry, this.eyeMaterial)
    leftEye.position.set(-0.045, 0.02, 0.12)
    headGroup.add(leftEye)

    // Right eye
    const rightEye = new THREE.Mesh(eyeGeometry, this.eyeMaterial)
    rightEye.position.set(0.045, 0.02, 0.12)
    headGroup.add(rightEye)

    // Irises
    const irisGeometry = new THREE.SphereGeometry(0.012, 12, 12)

    const leftIris = new THREE.Mesh(irisGeometry, this.irisMaterial)
    leftIris.position.set(-0.045, 0.02, 0.14)
    headGroup.add(leftIris)

    const rightIris = new THREE.Mesh(irisGeometry, this.irisMaterial)
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
  }

  /**
   * Add eyebrows to head
   */
  private addEyebrows(headGroup: THREE.Group): void {
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
  }

  /**
   * Add ears to head
   */
  private addEars(headGroup: THREE.Group): void {
    const earGeometry = new THREE.SphereGeometry(0.025, 8, 8)
    earGeometry.scale(0.5, 1, 0.7)

    const leftEar = new THREE.Mesh(earGeometry, this.skinMaterial)
    leftEar.position.set(-0.14, 0, 0)
    headGroup.add(leftEar)

    const rightEar = new THREE.Mesh(earGeometry, this.skinMaterial)
    rightEar.position.set(0.14, 0, 0)
    headGroup.add(rightEar)
  }

  /**
   * Build neck
   */
  private buildNeck(): THREE.Mesh {
    const neckGeometry = new THREE.CylinderGeometry(0.05, 0.06, 0.1, 16)
    const neck = new THREE.Mesh(neckGeometry, this.skinMaterial)
    neck.position.y = 1.4
    return neck
  }

  /**
   * Build torso with shirt
   */
  private buildTorso(): THREE.Group {
    const torsoGroup = new THREE.Group()

    // Shirt/body
    const torsoGeometry = new THREE.CylinderGeometry(0.18, 0.15, 0.45, 16)
    const torso = new THREE.Mesh(torsoGeometry, this.shirtMaterial)
    torsoGroup.add(torso)

    // Collar
    const collarGeometry = new THREE.TorusGeometry(0.08, 0.02, 8, 16)
    const collarMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff })
    const collar = new THREE.Mesh(collarGeometry, collarMaterial)
    collar.position.y = 0.2
    collar.rotation.x = Math.PI / 2
    torsoGroup.add(collar)

    torsoGroup.position.y = 1.1
    torsoGroup.name = 'spine'
    return torsoGroup
  }

  /**
   * Build right arm (for pointing animations)
   */
  private buildRightArm(): THREE.Group {
    const armGroup = new THREE.Group()

    // Upper arm
    const upperArmGeometry = new THREE.CapsuleGeometry(0.04, 0.2, 8, 12)
    const upperArm = new THREE.Mesh(upperArmGeometry, this.shirtMaterial)
    upperArm.position.y = -0.1
    armGroup.add(upperArm)

    // Lower arm (skin)
    const lowerArmGeometry = new THREE.CapsuleGeometry(0.035, 0.18, 8, 12)
    const lowerArm = new THREE.Mesh(lowerArmGeometry, this.skinMaterial)
    lowerArm.position.y = -0.32
    armGroup.add(lowerArm)

    // Hand
    const handGeometry = new THREE.SphereGeometry(0.04, 12, 12)
    handGeometry.scale(0.8, 1, 0.6)
    const hand = new THREE.Mesh(handGeometry, this.skinMaterial)
    hand.position.y = -0.46
    armGroup.add(hand)

    armGroup.position.set(0.22, 1.25, 0)
    armGroup.rotation.z = -0.15
    armGroup.name = 'rightArm'
    return armGroup
  }

  /**
   * Build left arm
   */
  private buildLeftArm(): THREE.Group {
    const armGroup = new THREE.Group()

    // Upper arm
    const upperArmGeometry = new THREE.CapsuleGeometry(0.04, 0.2, 8, 12)
    const upperArm = new THREE.Mesh(upperArmGeometry, this.shirtMaterial)
    upperArm.position.y = -0.1
    armGroup.add(upperArm)

    // Lower arm (skin)
    const lowerArmGeometry = new THREE.CapsuleGeometry(0.035, 0.18, 8, 12)
    const lowerArm = new THREE.Mesh(lowerArmGeometry, this.skinMaterial)
    lowerArm.position.y = -0.32
    armGroup.add(lowerArm)

    // Hand
    const handGeometry = new THREE.SphereGeometry(0.04, 12, 12)
    handGeometry.scale(0.8, 1, 0.6)
    const hand = new THREE.Mesh(handGeometry, this.skinMaterial)
    hand.position.y = -0.46
    armGroup.add(hand)

    armGroup.position.set(-0.22, 1.25, 0)
    armGroup.rotation.z = 0.15
    armGroup.name = 'leftArm'
    return armGroup
  }

  /**
   * Build legs with pants and shoes
   */
  private buildLegs(): THREE.Object3D[] {
    const parts: THREE.Object3D[] = []

    // Hips/Belt area
    const hipsGeometry = new THREE.CylinderGeometry(0.15, 0.14, 0.1, 16)
    const hips = new THREE.Mesh(hipsGeometry, this.pantsMaterial)
    hips.position.y = 0.82
    parts.push(hips)

    // Left upper leg
    const legGeometry = new THREE.CapsuleGeometry(0.055, 0.35, 8, 12)
    const leftLeg = new THREE.Mesh(legGeometry, this.pantsMaterial)
    leftLeg.position.set(-0.08, 0.52, 0)
    parts.push(leftLeg)

    // Right upper leg
    const rightLeg = new THREE.Mesh(legGeometry, this.pantsMaterial)
    rightLeg.position.set(0.08, 0.52, 0)
    parts.push(rightLeg)

    // Left lower leg
    const lowerLegGeometry = new THREE.CapsuleGeometry(0.045, 0.25, 8, 12)
    const leftLowerLeg = new THREE.Mesh(lowerLegGeometry, this.pantsMaterial)
    leftLowerLeg.position.set(-0.08, 0.2, 0)
    parts.push(leftLowerLeg)

    // Right lower leg
    const rightLowerLeg = new THREE.Mesh(lowerLegGeometry, this.pantsMaterial)
    rightLowerLeg.position.set(0.08, 0.2, 0)
    parts.push(rightLowerLeg)

    // Shoes
    const shoeMaterial = new THREE.MeshStandardMaterial({ color: 0x1f2937 })
    const shoeGeometry = new THREE.BoxGeometry(0.08, 0.04, 0.14)

    const leftShoe = new THREE.Mesh(shoeGeometry, shoeMaterial)
    leftShoe.position.set(-0.08, 0.02, 0.02)
    parts.push(leftShoe)

    const rightShoe = new THREE.Mesh(shoeGeometry, shoeMaterial)
    rightShoe.position.set(0.08, 0.02, 0.02)
    parts.push(rightShoe)

    return parts
  }

  /**
   * Find mouth mesh in head group for animation
   */
  private findMouthMesh(headGroup: THREE.Group): THREE.Mesh {
    const mouth = headGroup.getObjectByName('mouth')
    if (mouth && mouth instanceof THREE.Mesh) {
      return mouth
    }
    throw new Error('Mouth mesh not found in head group')
  }
}
