/**
 * Teacher3D Module Exports
 * ========================
 * Barrel export for all Teacher3D components and utilities
 */

// Composables
export { use3DAvatar } from './composables/use3DAvatar'
export type { AnimationType, ExpressionType, PointTarget, AvatarOptions } from './composables/use3DAvatar'

// Avatar Builders
export { VRMAvatarLoader } from './avatars/VRMAvatarLoader'
export type { LoadedAvatar } from './avatars/VRMAvatarLoader'

export { HumanAvatarBuilder } from './avatars/HumanAvatarBuilder'
export type { HumanAvatarParts } from './avatars/HumanAvatarBuilder'

export { RobotAvatarBuilder } from './avatars/RobotAvatarBuilder'
export type { RobotAvatarParts } from './avatars/RobotAvatarBuilder'

export { AnimationController } from './avatars/AnimationController'
export type { AvatarParts } from './avatars/AnimationController'
