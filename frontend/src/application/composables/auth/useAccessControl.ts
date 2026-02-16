/**
 * useAccessControl Composable
 *
 * Centralized access control for CourseEditor and content management.
 * Determines which operations a user can perform based on their role.
 *
 * Business logic for role determination is delegated to UserModel domain model.
 * Course-specific access logic stays here (application-layer concern).
 *
 * Role Hierarchy (GBA - Group-Based Authorization):
 * - Owner (level 1000+): Can access EVERYTHING
 * - OrgAdmin (level 500+): Can access Academy courses (if team member)
 * - Creator (level 250+): Can create/edit/manage own courses (Community + Private)
 * - User (default): Can create own courses but limited functionality
 *
 * Course Types:
 * - Academy: Owner + Team only (exklusiv, no review)
 * - Community: User-submitted, requires Team review
 * - Private: User's own, not visible to anyone
 */

import { computed, type ComputedRef } from 'vue'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
import { UserModel } from '@/domain/models/user/User.model'
import type { Course } from '@/infrastructure/api/clients/learning'

export interface AccessControl {
  // User role checks
  isOwner: boolean
  isAdmin: boolean
  isCreator: boolean
  isUser: boolean

  // Course type access
  canAccessAcademyCourses: boolean
  canAccessCommunityCourses: boolean
  canAccessPrivateCourses: boolean

  // Course operations
  canCreateCourse: (courseType: 'academy' | 'community' | 'private') => boolean
  canEditCourse: (course: Course) => boolean
  canDeleteCourse: (course: Course) => boolean
  canPublishCourse: (course: Course) => boolean
  canReviewCommunitySubmissions: boolean
  canApproveCommunitySubmission: boolean
  canRejectCommunitySubmission: boolean

  // Learning Method operations
  canEditLearningMethods: (courseType: 'academy' | 'community' | 'private') => boolean
  canAccessLMBrowser: boolean

  // Feature access based on role
  canAccessUserPanel: boolean
  canAccessAdminPanel: boolean
  canAccessTeamDashboard: boolean
}

/**
 * Composable for access control.
 * Role determination delegated to UserModel domain model.
 *
 * Usage:
 * ```ts
 * const access = useAccessControl()
 *
 * if (access.value.canCreateCourse('academy')) {
 *   // Show academy course creation
 * }
 *
 * if (access.value.canEditCourse(course)) {
 *   // Show edit button
 * }
 * ```
 */
export function useAccessControl(): ComputedRef<AccessControl> {
  const authStore = useAuthStore()

  return computed(() => {
    const rawUser = authStore.user
    if (!rawUser) {
      return createGuestAccess()
    }

    const userModel = UserModel.fromAPI(rawUser as Record<string, unknown>)

    if (userModel.isOwner) {
      return createOwnerAccess()
    }

    if (userModel.isOrgAdmin) {
      return createAdminAccess(userModel)
    }

    if (userModel.isCreator) {
      return createCreatorAccess(userModel)
    }

    return createUserAccess(userModel, rawUser)
  })
}

/**
 * Guest access (no user logged in)
 */
function createGuestAccess(): AccessControl {
  return {
    isOwner: false,
    isAdmin: false,
    isCreator: false,
    isUser: false,

    canAccessAcademyCourses: false,
    canAccessCommunityCourses: true,
    canAccessPrivateCourses: false,

    canCreateCourse: () => false,
    canEditCourse: () => false,
    canDeleteCourse: () => false,
    canPublishCourse: () => false,
    canReviewCommunitySubmissions: false,
    canApproveCommunitySubmission: false,
    canRejectCommunitySubmission: false,

    canEditLearningMethods: () => false,
    canAccessLMBrowser: true,

    canAccessUserPanel: false,
    canAccessAdminPanel: false,
    canAccessTeamDashboard: false
  }
}

/**
 * Owner access (hierarchy level 1000+)
 */
function createOwnerAccess(): AccessControl {
  return {
    isOwner: true,
    isAdmin: false,
    isCreator: false,
    isUser: false,

    canAccessAcademyCourses: true,
    canAccessCommunityCourses: true,
    canAccessPrivateCourses: true,

    canCreateCourse: () => true,
    canEditCourse: () => true,
    canDeleteCourse: () => true,
    canPublishCourse: () => true,
    canReviewCommunitySubmissions: true,
    canApproveCommunitySubmission: true,
    canRejectCommunitySubmission: true,

    canEditLearningMethods: () => true,
    canAccessLMBrowser: true,

    canAccessUserPanel: true,
    canAccessAdminPanel: true,
    canAccessTeamDashboard: true
  }
}

/**
 * Admin/OrgAdmin access (hierarchy level 500+)
 */
function createAdminAccess(user: UserModel): AccessControl {
  const hasAcademyAccess = user.isTeamMember

  return {
    isOwner: false,
    isAdmin: true,
    isCreator: false,
    isUser: false,

    canAccessAcademyCourses: hasAcademyAccess,
    canAccessCommunityCourses: true,
    canAccessPrivateCourses: false,

    canCreateCourse: (type) => type === 'academy' && hasAcademyAccess,
    canEditCourse: (course) => {
      if (!hasAcademyAccess) return false
      return course.source === 'academy'
    },
    canDeleteCourse: (course) => {
      if (!hasAcademyAccess) return false
      return course.source === 'academy'
    },
    canPublishCourse: (course) => {
      if (!hasAcademyAccess) return false
      return course.source === 'academy'
    },
    canReviewCommunitySubmissions: true,
    canApproveCommunitySubmission: true,
    canRejectCommunitySubmission: true,

    canEditLearningMethods: (type) => type === 'academy' && hasAcademyAccess,
    canAccessLMBrowser: true,

    canAccessUserPanel: true,
    canAccessAdminPanel: user.canAccessAdminPanel,
    canAccessTeamDashboard: hasAcademyAccess
  }
}

/**
 * Creator access (hierarchy level 250+)
 */
function createCreatorAccess(user: UserModel): AccessControl {
  return {
    isOwner: false,
    isAdmin: false,
    isCreator: true,
    isUser: false,

    canAccessAcademyCourses: false,
    canAccessCommunityCourses: true,
    canAccessPrivateCourses: true,

    canCreateCourse: (type) => type === 'community' || type === 'private',
    canEditCourse: (course) => {
      return (
        course.creator_id === user.id &&
        (course.source === 'community' || course.source === 'private')
      )
    },
    canDeleteCourse: (course) => {
      return (
        course.creator_id === user.id &&
        (course.source === 'community' || course.source === 'private')
      )
    },
    canPublishCourse: (course) => {
      return (
        course.creator_id === user.id &&
        course.source === 'community' &&
        course.status === 'approved'
      )
    },
    canReviewCommunitySubmissions: false,
    canApproveCommunitySubmission: false,
    canRejectCommunitySubmission: false,

    canEditLearningMethods: (type) => type === 'community' || type === 'private',
    canAccessLMBrowser: true,

    canAccessUserPanel: true,
    canAccessAdminPanel: false,
    canAccessTeamDashboard: false
  }
}

/**
 * Default user access (free/premium/pro subscription)
 * Uses raw user data for subscription_tier (application-layer concern, not domain).
 */
function createUserAccess(user: UserModel, rawUser: any): AccessControl {
  const subscriptionTier = rawUser.subscription_tier || ''
  const hasCreatorPlan = subscriptionTier === 'creator' || subscriptionTier === 'pro'

  return {
    isOwner: false,
    isAdmin: false,
    isCreator: false,
    isUser: true,

    canAccessAcademyCourses: false,
    canAccessCommunityCourses: true,
    canAccessPrivateCourses: hasCreatorPlan,

    canCreateCourse: (type) => {
      if (type === 'private' && hasCreatorPlan) return true
      if (type === 'community' && hasCreatorPlan) return true
      return false
    },
    canEditCourse: (course) => {
      if (!hasCreatorPlan) return false
      return (
        course.creator_id === user.id &&
        (course.source === 'community' || course.source === 'private')
      )
    },
    canDeleteCourse: (course) => {
      if (!hasCreatorPlan) return false
      return (
        course.creator_id === user.id &&
        (course.source === 'community' || course.source === 'private')
      )
    },
    canPublishCourse: () => false,
    canReviewCommunitySubmissions: false,
    canApproveCommunitySubmission: false,
    canRejectCommunitySubmission: false,

    canEditLearningMethods: (type) => hasCreatorPlan && (type === 'community' || type === 'private'),
    canAccessLMBrowser: true,

    canAccessUserPanel: true,
    canAccessAdminPanel: false,
    canAccessTeamDashboard: false
  }
}
