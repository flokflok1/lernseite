import { describe, it, expect } from 'vitest'
import { UserModel } from '../User.model'

describe('UserModel', () => {
  const createUser = (overrides: Record<string, unknown> = {}, groups = [{ name: 'Users', hierarchy_level: 10 }]) =>
    UserModel.fromAPI({
      user_id: 'u1',
      email: 'test@test.de',
      full_name: 'Max Mustermann',
      organisation_id: null,
      is_active: true,
      email_verified: true,
      ...overrides
    }, groups as any)

  describe('fromAPI', () => {
    it('creates UserModel from snake_case API data', () => {
      const user = createUser()
      expect(user.id).toBe('u1')
      expect(user.email).toBe('test@test.de')
      expect(user.fullName).toBe('Max Mustermann')
      expect(user.isActive).toBe(true)
    })

    it('handles missing groups gracefully', () => {
      const user = UserModel.fromAPI({ user_id: 'u1', email: 'a@b.de', full_name: 'A' })
      expect(user.hierarchyLevel).toBe(0)
      expect(user.groups).toEqual([])
    })

    it('handles both user_id and id fields', () => {
      const u1 = UserModel.fromAPI({ user_id: 'uid1' })
      const u2 = UserModel.fromAPI({ id: 'uid2' })
      expect(u1.id).toBe('uid1')
      expect(u2.id).toBe('uid2')
    })
  })

  describe('hierarchyLevel', () => {
    it('returns 0 for user with no groups', () => {
      const user = createUser({}, [])
      expect(user.hierarchyLevel).toBe(0)
    })

    it('returns highest hierarchy level from all groups', () => {
      const user = createUser({}, [
        { name: 'Users', hierarchy_level: 10 },
        { name: 'Creator', hierarchy_level: 250 },
        { name: 'OrgAdmin', hierarchy_level: 500 }
      ] as any)
      expect(user.hierarchyLevel).toBe(500)
    })
  })

  describe('role checks', () => {
    it('isOwner is true for level >= 1000', () => {
      const user = createUser({}, [{ name: 'Owner', hierarchy_level: 1000 }] as any)
      expect(user.isOwner).toBe(true)
      expect(user.isSystemAdmin).toBe(true)
    })

    it('isSystemAdmin is true for level >= 900', () => {
      const user = createUser({}, [{ name: 'SysAdmin', hierarchy_level: 900 }] as any)
      expect(user.isSystemAdmin).toBe(true)
      expect(user.isOwner).toBe(false)
    })

    it('isModerator is true for level >= 750', () => {
      const user = createUser({}, [{ name: 'Mod', hierarchy_level: 750 }] as any)
      expect(user.isModerator).toBe(true)
      expect(user.isSystemAdmin).toBe(false)
    })

    it('isOrgAdmin is true for level >= 500', () => {
      const user = createUser({}, [{ name: 'OrgAdmin', hierarchy_level: 500 }] as any)
      expect(user.isOrgAdmin).toBe(true)
      expect(user.isModerator).toBe(false)
    })

    it('isCreator is true for level >= 250', () => {
      const user = createUser({}, [{ name: 'Creator', hierarchy_level: 250 }] as any)
      expect(user.isCreator).toBe(true)
      expect(user.isOrgAdmin).toBe(false)
    })

    it('isPremium is true for level >= 100', () => {
      const user = createUser({}, [{ name: 'Premium', hierarchy_level: 100 }] as any)
      expect(user.isPremium).toBe(true)
      expect(user.isCreator).toBe(false)
    })

    it('regular user at level 10 is not premium', () => {
      const user = createUser()
      expect(user.isPremium).toBe(false)
    })
  })

  describe('panel access', () => {
    it('canAccessAdminPanel requires level >= 500', () => {
      expect(createUser({}, [{ name: 'OrgAdmin', hierarchy_level: 500 }] as any).canAccessAdminPanel).toBe(true)
      expect(createUser({}, [{ name: 'Creator', hierarchy_level: 250 }] as any).canAccessAdminPanel).toBe(false)
    })

    it('canAccessUserPanel requires isActive', () => {
      expect(createUser({ is_active: true }).canAccessUserPanel).toBe(true)
      expect(createUser({ is_active: false }).canAccessUserPanel).toBe(false)
    })
  })

  describe('permissions', () => {
    it('hasPermission checks for specific permission', () => {
      const user = UserModel.fromAPI({ user_id: 'u1' }, [], ['users.read', 'courses.write'])
      expect(user.hasPermission('users.read')).toBe(true)
      expect(user.hasPermission('users.delete')).toBe(false)
    })

    it('hasAnyPermission checks for any matching permission', () => {
      const user = UserModel.fromAPI({ user_id: 'u1' }, [], ['users.read'])
      expect(user.hasAnyPermission('users.read', 'users.write')).toBe(true)
      expect(user.hasAnyPermission('courses.read', 'courses.write')).toBe(false)
    })
  })

  describe('canBeDeleted', () => {
    it('active non-owner can be deleted', () => {
      expect(createUser({ is_active: true }).canBeDeleted()).toBe(true)
    })

    it('owner cannot be deleted', () => {
      const owner = createUser({}, [{ name: 'Owner', hierarchy_level: 1000 }] as any)
      expect(owner.canBeDeleted()).toBe(false)
    })

    it('inactive user cannot be deleted', () => {
      expect(createUser({ is_active: false }).canBeDeleted()).toBe(false)
    })
  })

  describe('displayRole', () => {
    it('returns highest-level group name', () => {
      const user = createUser({}, [
        { name: 'Users', hierarchy_level: 10 },
        { name: 'Creator', hierarchy_level: 250 }
      ] as any)
      expect(user.displayRole).toBe('Creator')
    })

    it('returns User for no groups', () => {
      const user = createUser({}, [])
      expect(user.displayRole).toBe('User')
    })
  })

  describe('isTeamMember', () => {
    it('true when organisationId is set', () => {
      expect(createUser({ organisation_id: 'org-1' }).isTeamMember).toBe(true)
    })

    it('false when organisationId is null', () => {
      expect(createUser({ organisation_id: null }).isTeamMember).toBe(false)
    })
  })

  describe('toMinimal', () => {
    it('returns minimal interface for Course.model.ts', () => {
      const user = createUser({}, [{ name: 'SysAdmin', hierarchy_level: 900 }] as any)
      const minimal = user.toMinimal()
      expect(minimal).toEqual({ id: 'u1', isSystemAdmin: true })
    })
  })

  describe('toJSON', () => {
    it('serializes all relevant fields', () => {
      const user = createUser()
      const json = user.toJSON()
      expect(json.id).toBe('u1')
      expect(json.email).toBe('test@test.de')
      expect(json.fullName).toBe('Max Mustermann')
      expect(json.hierarchyLevel).toBe(10)
    })
  })
})
