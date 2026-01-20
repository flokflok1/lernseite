import { describe, it, expect } from 'vitest'
import { UserRole, UserRoleEnum } from '../UserRole.vo'

describe('UserRole Value Object', () => {
  describe('Role Creation', () => {
    it('should create all 12 standard roles successfully', () => {
      const roles = [
        UserRoleEnum.FREE,
        UserRoleEnum.PREMIUM,
        UserRoleEnum.CREATOR,
        UserRoleEnum.TEACHER,
        UserRoleEnum.SCHOOL,
        UserRoleEnum.COMPANY,
        UserRoleEnum.SUPPORT,
        UserRoleEnum.MODERATOR,
        UserRoleEnum.ADMIN,
        UserRoleEnum.SCHOOL_ADMIN,
        UserRoleEnum.COMPANY_ADMIN,
        UserRoleEnum.OWNER
      ]

      roles.forEach(roleEnum => {
        const role = UserRole.create(roleEnum)
        expect(role).toBeDefined()
        expect(role.toString()).toBe(roleEnum)
      })
    })

    it('should create new organizational admin roles', () => {
      const schoolAdmin = UserRole.create(UserRoleEnum.SCHOOL_ADMIN)
      const companyAdmin = UserRole.create(UserRoleEnum.COMPANY_ADMIN)
      const owner = UserRole.create(UserRoleEnum.OWNER)

      expect(schoolAdmin.toString()).toBe('school_admin')
      expect(companyAdmin.toString()).toBe('company_admin')
      expect(owner.toString()).toBe('owner')
    })

    it('should reject invalid role values', () => {
      expect(() => UserRole.create('InvalidRole')).toThrow('Invalid user role: InvalidRole')
      expect(() => UserRole.create('SCHOOL_ADMIN')).toThrow() // Case-sensitive
      expect(() => UserRole.create('admin_school')).toThrow() // Wrong order
      expect(() => UserRole.create('')).toThrow('Invalid user role:')
    })
  })

  describe('isPremium() - Subscription Tier Identification', () => {
    it('should identify premium subscription roles', () => {
      const premiumRoles = [
        UserRoleEnum.PREMIUM,
        UserRoleEnum.CREATOR,
        UserRoleEnum.TEACHER,
        UserRoleEnum.SCHOOL,
        UserRoleEnum.COMPANY
      ]

      premiumRoles.forEach(roleEnum => {
        const role = UserRole.create(roleEnum)
        expect(role.isPremium()).toBe(true)
      })
    })

    it('should not identify free tier as premium', () => {
      const freeRole = UserRole.create(UserRoleEnum.FREE)
      expect(freeRole.isPremium()).toBe(false)
    })

    it('should not identify support staff as premium', () => {
      const supportRole = UserRole.create(UserRoleEnum.SUPPORT)
      const modRole = UserRole.create(UserRoleEnum.MODERATOR)

      expect(supportRole.isPremium()).toBe(false)
      expect(modRole.isPremium()).toBe(false)
    })

    it('should not identify system admin as premium (different permission model)', () => {
      const adminRole = UserRole.create(UserRoleEnum.ADMIN)
      expect(adminRole.isPremium()).toBe(false)
    })

    it('should not identify organizational admins as premium (orthogonal to subscription)', () => {
      const schoolAdmin = UserRole.create(UserRoleEnum.SCHOOL_ADMIN)
      const companyAdmin = UserRole.create(UserRoleEnum.COMPANY_ADMIN)
      const owner = UserRole.create(UserRoleEnum.OWNER)

      expect(schoolAdmin.isPremium()).toBe(false)
      expect(companyAdmin.isPremium()).toBe(false)
      expect(owner.isPremium()).toBe(false)
    })
  })

  describe('isSystemAdmin() - System Administration Check', () => {
    it('should only identify ADMIN as system admin', () => {
      const adminRole = UserRole.create(UserRoleEnum.ADMIN)
      expect(adminRole.isSystemAdmin()).toBe(true)
    })

    it('should not identify other roles as system admin', () => {
      const nonAdminRoles = [
        UserRoleEnum.FREE,
        UserRoleEnum.PREMIUM,
        UserRoleEnum.CREATOR,
        UserRoleEnum.TEACHER,
        UserRoleEnum.SCHOOL,
        UserRoleEnum.COMPANY,
        UserRoleEnum.SUPPORT,
        UserRoleEnum.MODERATOR,
        UserRoleEnum.SCHOOL_ADMIN,
        UserRoleEnum.COMPANY_ADMIN,
        UserRoleEnum.OWNER
      ]

      nonAdminRoles.forEach(roleEnum => {
        const role = UserRole.create(roleEnum)
        expect(role.isSystemAdmin()).toBe(false)
      })
    })
  })

  describe('isModerator() - Content Moderation Check', () => {
    it('should only identify MODERATOR as moderator', () => {
      const modRole = UserRole.create(UserRoleEnum.MODERATOR)
      expect(modRole.isModerator()).toBe(true)
    })

    it('should not identify other roles as moderator', () => {
      const nonModRoles = [
        UserRoleEnum.FREE,
        UserRoleEnum.PREMIUM,
        UserRoleEnum.CREATOR,
        UserRoleEnum.TEACHER,
        UserRoleEnum.SCHOOL,
        UserRoleEnum.COMPANY,
        UserRoleEnum.SUPPORT,
        UserRoleEnum.ADMIN,
        UserRoleEnum.SCHOOL_ADMIN,
        UserRoleEnum.COMPANY_ADMIN,
        UserRoleEnum.OWNER
      ]

      nonModRoles.forEach(roleEnum => {
        const role = UserRole.create(roleEnum)
        expect(role.isModerator()).toBe(false)
      })
    })
  })

  describe('hasElevatedPrivileges() - Administrative Privilege Check (COMPLETE HIERARCHY)', () => {
    it('should identify all 5 roles with elevated privileges', () => {
      const elevatedRoles = [
        UserRoleEnum.ADMIN,
        UserRoleEnum.MODERATOR,
        UserRoleEnum.SCHOOL_ADMIN,
        UserRoleEnum.COMPANY_ADMIN,
        UserRoleEnum.OWNER
      ]

      elevatedRoles.forEach(roleEnum => {
        const role = UserRole.create(roleEnum)
        expect(role.hasElevatedPrivileges()).toBe(true)
      })
    })

    it('should identify system admin (ADMIN) as having elevated privileges', () => {
      const adminRole = UserRole.create(UserRoleEnum.ADMIN)
      expect(adminRole.hasElevatedPrivileges()).toBe(true)
    })

    it('should identify moderator as having elevated privileges', () => {
      const modRole = UserRole.create(UserRoleEnum.MODERATOR)
      expect(modRole.hasElevatedPrivileges()).toBe(true)
    })

    it('should identify organizational admins as having elevated privileges', () => {
      const schoolAdmin = UserRole.create(UserRoleEnum.SCHOOL_ADMIN)
      const companyAdmin = UserRole.create(UserRoleEnum.COMPANY_ADMIN)
      const owner = UserRole.create(UserRoleEnum.OWNER)

      expect(schoolAdmin.hasElevatedPrivileges()).toBe(true)
      expect(companyAdmin.hasElevatedPrivileges()).toBe(true)
      expect(owner.hasElevatedPrivileges()).toBe(true)
    })

    it('should not identify regular subscription tiers as having elevated privileges', () => {
      const regularRoles = [
        UserRoleEnum.FREE,
        UserRoleEnum.PREMIUM,
        UserRoleEnum.CREATOR,
        UserRoleEnum.TEACHER,
        UserRoleEnum.SCHOOL,
        UserRoleEnum.COMPANY
      ]

      regularRoles.forEach(roleEnum => {
        const role = UserRole.create(roleEnum)
        expect(role.hasElevatedPrivileges()).toBe(false)
      })
    })

    it('should not identify support staff as having elevated privileges', () => {
      const supportRole = UserRole.create(UserRoleEnum.SUPPORT)
      expect(supportRole.hasElevatedPrivileges()).toBe(false)
    })
  })

  describe('Permission Orthogonality - Subscription vs Organizational Roles', () => {
    it('organizational admins are independent of subscription tier', () => {
      // org-admin roles should NOT return true for isPremium
      const schoolAdmin = UserRole.create(UserRoleEnum.SCHOOL_ADMIN)
      expect(schoolAdmin.isPremium()).toBe(false)
      expect(schoolAdmin.hasElevatedPrivileges()).toBe(true)

      // A school admin could be either free or premium in a real system
      // but the isPremium() method doesn't consider org-admin roles
    })

    it('system admin and moderator are independent of subscription tier', () => {
      const adminRole = UserRole.create(UserRoleEnum.ADMIN)
      const modRole = UserRole.create(UserRoleEnum.MODERATOR)

      expect(adminRole.isPremium()).toBe(false)
      expect(adminRole.hasElevatedPrivileges()).toBe(true)

      expect(modRole.isPremium()).toBe(false)
      expect(modRole.hasElevatedPrivileges()).toBe(true)
    })

    it('demonstrates business rule: ADMIN role has elevated privileges but NOT premium features', () => {
      const adminRole = UserRole.create(UserRoleEnum.ADMIN)

      // Admin has full system access (elevated privileges)
      expect(adminRole.hasElevatedPrivileges()).toBe(true)
      expect(adminRole.isSystemAdmin()).toBe(true)

      // But admin does NOT automatically have premium features
      // (Premium is subscription-based, not permission-based)
      expect(adminRole.isPremium()).toBe(false)
    })
  })

  describe('Role Equality', () => {
    it('should correctly compare equal roles', () => {
      const role1 = UserRole.create(UserRoleEnum.PREMIUM)
      const role2 = UserRole.create(UserRoleEnum.PREMIUM)

      expect(role1.equals(role2)).toBe(true)
    })

    it('should correctly compare different roles', () => {
      const premiumRole = UserRole.create(UserRoleEnum.PREMIUM)
      const freeRole = UserRole.create(UserRoleEnum.FREE)

      expect(premiumRole.equals(freeRole)).toBe(false)
    })

    it('should correctly compare new organizational roles', () => {
      const schoolAdmin1 = UserRole.create(UserRoleEnum.SCHOOL_ADMIN)
      const schoolAdmin2 = UserRole.create(UserRoleEnum.SCHOOL_ADMIN)
      const companyAdmin = UserRole.create(UserRoleEnum.COMPANY_ADMIN)

      expect(schoolAdmin1.equals(schoolAdmin2)).toBe(true)
      expect(schoolAdmin1.equals(companyAdmin)).toBe(false)
    })
  })

  describe('String Representation', () => {
    it('should return correct string values for all roles', () => {
      const roleMap = {
        FREE: 'Free',
        PREMIUM: 'Premium',
        CREATOR: 'Creator',
        TEACHER: 'Teacher',
        SCHOOL: 'School',
        COMPANY: 'Company',
        SUPPORT: 'Support',
        MODERATOR: 'Moderator',
        ADMIN: 'Admin',
        SCHOOL_ADMIN: 'school_admin',
        COMPANY_ADMIN: 'company_admin',
        OWNER: 'owner'
      }

      Object.entries(roleMap).forEach(([enumKey, expectedString]) => {
        const roleEnum = UserRoleEnum[enumKey as keyof typeof UserRoleEnum]
        const role = UserRole.create(roleEnum)
        expect(role.toString()).toBe(expectedString)
      })
    })
  })

  describe('Regression Tests - Existing Roles Unchanged', () => {
    it('should preserve existing free tier behavior', () => {
      const freeRole = UserRole.create(UserRoleEnum.FREE)

      expect(freeRole.isPremium()).toBe(false)
      expect(freeRole.isSystemAdmin()).toBe(false)
      expect(freeRole.isModerator()).toBe(false)
      expect(freeRole.hasElevatedPrivileges()).toBe(false)
    })

    it('should preserve existing premium tier behavior', () => {
      const premiumRole = UserRole.create(UserRoleEnum.PREMIUM)

      expect(premiumRole.isPremium()).toBe(true)
      expect(premiumRole.isSystemAdmin()).toBe(false)
      expect(premiumRole.isModerator()).toBe(false)
      expect(premiumRole.hasElevatedPrivileges()).toBe(false)
    })

    it('should preserve existing creator tier behavior', () => {
      const creatorRole = UserRole.create(UserRoleEnum.CREATOR)

      expect(creatorRole.isPremium()).toBe(true)
      expect(creatorRole.isSystemAdmin()).toBe(false)
      expect(creatorRole.isModerator()).toBe(false)
      expect(creatorRole.hasElevatedPrivileges()).toBe(false)
    })

    it('should preserve existing teacher tier behavior', () => {
      const teacherRole = UserRole.create(UserRoleEnum.TEACHER)

      expect(teacherRole.isPremium()).toBe(true)
      expect(teacherRole.isSystemAdmin()).toBe(false)
      expect(teacherRole.isModerator()).toBe(false)
      expect(teacherRole.hasElevatedPrivileges()).toBe(false)
    })

    it('should preserve existing system admin behavior', () => {
      const adminRole = UserRole.create(UserRoleEnum.ADMIN)

      expect(adminRole.isPremium()).toBe(false)
      expect(adminRole.isSystemAdmin()).toBe(true)
      expect(adminRole.isModerator()).toBe(false)
      expect(adminRole.hasElevatedPrivileges()).toBe(true)
    })

    it('should preserve existing moderator behavior', () => {
      const modRole = UserRole.create(UserRoleEnum.MODERATOR)

      expect(modRole.isPremium()).toBe(false)
      expect(modRole.isSystemAdmin()).toBe(false)
      expect(modRole.isModerator()).toBe(true)
      expect(modRole.hasElevatedPrivileges()).toBe(true)
    })
  })
})
