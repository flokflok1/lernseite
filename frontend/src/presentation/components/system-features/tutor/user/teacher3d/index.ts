/**
 * Teacher3D Module Exports
 * ========================
 * Barrel export for all Teacher3D components and utilities
 */

// Composables
export { use3DAvatar } from './composables/use3DAvatar.ts'
export type { AnimationType, ExpressionType, PointTarget, AvatarOptions } from './composables/use3DAvatar.ts'

// Avatar Builders
export { VRMAvatarLoader } from './avatars/VRMAvatarLoader.ts'
export type { LoadedAvatar } from './avatars/VRMAvatarLoader.ts'

export { HumanAvatarBuilder } from './avatars/HumanAvatarBuilder.ts'
export type { HumanAvatarParts } from './avatars/HumanAvatarBuilder.ts'

export { RobotAvatarBuilder } from './avatars/RobotAvatarBuilder.ts'
export type { RobotAvatarParts } from './avatars/RobotAvatarBuilder.ts'

export { AnimationController } from './avatars/AnimationController.ts'
export type { AvatarParts } from './avatars/AnimationController.ts'
