/**
 * useAccessControl Composable
 *
 * Centralized access control for CourseEditor and content management.
 * Determines which operations a user can perform based on their role.
 *
 * Role Hierarchy:
 * - Owner (level 1000): Can access EVERYTHING
 * - Admin: Can access Academy courses only (if team member)
 * - Creator: Can create/edit/manage own courses (Community + Private)
 * - User: Can create own courses but limited functionality
 *
 * Course Types:
 * - Academy: Owner + Team only (exklusiv, no review)
 * - Community: User-submitted, requires Team review
 * - Private: User's own, not visible to anyone
 */

import { computed, type ComputedRef } from 'vue'
import { useUserStore } from '@/application/stores/modules/core/user.store'
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
 * Composable for access control
 *
 * Usage:
 * ```ts
 * const { isOwner, canEditCourse, canCreateCourse } = useAccessControl()
 *
 * if (canCreateCourse('academy')) {
 *   // Show academy course creation
 * }
 *
 * if (canEditCourse(course)) {
 *   // Show edit button
 * }
 * ```
 */
export function useAccessControl(): ComputedRef<AccessControl> {
  const userStore = useUserStore()

  return computed(() => {
    const user = userStore.currentUser
    if (!user) {
      return createGuestAccess()
    }

    const userRole = user.role || 'user'
    const userLevel = user.level || 100

    // Owner (level 1000) - full access
    if (userLevel >= 1000 || userRole === 'owner') {
      return createOwnerAccess()
    }

    // Admin - can access academy courses
    if (userRole === 'admin') {
      return createAdminAccess(user)
    }

    // Creator - can create and manage own courses
    if (userRole === 'creator') {
      return createCreatorAccess(user)
    }

    // Default User
    return createUserAccess(user)
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
 * Owner access (level 1000+)
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
 * Admin access
 */
function createAdminAccess(user: any): AccessControl {
  const isTeamMember = user.team_id !== null && user.team_id !== undefined
  const hasAcademyAccess = isTeamMember

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
    canAccessAdminPanel: true,
    canAccessTeamDashboard: hasAcademyAccess
  }
}

/**
 * Creator access
 */
function createCreatorAccess(user: any): AccessControl {
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
        course.creator_id === user.user_id &&
        (course.source === 'community' || course.source === 'private')
      )
    },
    canDeleteCourse: (course) => {
      return (
        course.creator_id === user.user_id &&
        (course.source === 'community' || course.source === 'private')
      )
    },
    canPublishCourse: (course) => {
      return (
        course.creator_id === user.user_id &&
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
 * User access (free/premium/pro subscription)
 */
function createUserAccess(user: any): AccessControl {
  const hasCreatorPlan = user.subscription_tier === 'creator' || user.subscription_tier === 'pro'

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
        course.creator_id === user.user_id &&
        (course.source === 'community' || course.source === 'private')
      )
    },
    canDeleteCourse: (course) => {
      if (!hasCreatorPlan) return false
      return (
        course.creator_id === user.user_id &&
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
