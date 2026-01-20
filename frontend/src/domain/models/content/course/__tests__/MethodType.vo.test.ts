import { describe, it, expect } from 'vitest'
import { MethodType } from '../MethodType.vo'

describe('MethodType Value Object', () => {
  describe('Creation & Validation', () => {
    it('should create all 12 valid method types (0-11)', () => {
      for (let i = 0; i <= 11; i++) {
        const method = MethodType.create(i)
        expect(method).toBeDefined()
        expect(method.toNumber()).toBe(i)
      }
    })

    it('should reject negative method types', () => {
      expect(() => MethodType.create(-1)).toThrow('Invalid method type: -1. Must be 0-11 (LM00-LM11)')
      expect(() => MethodType.create(-10)).toThrow()
      expect(() => MethodType.create(-100)).toThrow()
    })

    it('should reject method types > 11 (LM12+ are system features, not content LMs)', () => {
      expect(() => MethodType.create(12)).toThrow('Invalid method type: 12. Must be 0-11 (LM00-LM11)')
      expect(() => MethodType.create(15)).toThrow()
      expect(() => MethodType.create(32)).toThrow()
      expect(() => MethodType.create(100)).toThrow()
    })

    it('should validate boundary cases (0 and 11 are valid)', () => {
      const min = MethodType.create(0)
      const max = MethodType.create(11)

      expect(min.toNumber()).toBe(0)
      expect(max.toNumber()).toBe(11)
    })
  })

  describe('Group Classification - getGroup()', () => {
    it('should classify into 3 groups: A (0-4), B (5-8), C (9-11)', () => {
      // Group A: Erklärend (0-4)
      for (let i = 0; i <= 4; i++) {
        expect(MethodType.create(i).getGroup()).toBe('A')
      }

      // Group B: Praxis (5-8)
      for (let i = 5; i <= 8; i++) {
        expect(MethodType.create(i).getGroup()).toBe('B')
      }

      // Group C: Prüfung (9-11)
      for (let i = 9; i <= 11; i++) {
        expect(MethodType.create(i).getGroup()).toBe('C')
      }
    })

    it('should handle group boundaries correctly', () => {
      // Boundary between A and B (4 → 5)
      expect(MethodType.create(4).getGroup()).toBe('A')
      expect(MethodType.create(5).getGroup()).toBe('B')

      // Boundary between B and C (8 → 9)
      expect(MethodType.create(8).getGroup()).toBe('B')
      expect(MethodType.create(9).getGroup()).toBe('C')
    })

    it('should return correct group letter for all members', () => {
      const testCases = [
        { id: 0, expected: 'A' },  // LM00
        { id: 2, expected: 'A' },  // LM02
        { id: 4, expected: 'A' },  // LM04
        { id: 5, expected: 'B' },  // LM05
        { id: 6, expected: 'B' },  // LM06
        { id: 8, expected: 'B' },  // LM08
        { id: 9, expected: 'C' },  // LM09
        { id: 10, expected: 'C' }, // LM10
        { id: 11, expected: 'C' }  // LM11
      ]

      testCases.forEach(({ id, expected }) => {
        expect(MethodType.create(id).getGroup()).toBe(expected)
      })
    })
  })

  describe('Group Display Names - getGroupName()', () => {
    it('should return correct German group names', () => {
      // Group A: Erklärend (Explanation/Theory)
      expect(MethodType.create(0).getGroupName()).toBe('Erklärend')
      expect(MethodType.create(2).getGroupName()).toBe('Erklärend')
      expect(MethodType.create(4).getGroupName()).toBe('Erklärend')

      // Group B: Praxis (Practice/Exercises)
      expect(MethodType.create(5).getGroupName()).toBe('Praxis')
      expect(MethodType.create(6).getGroupName()).toBe('Praxis')
      expect(MethodType.create(8).getGroupName()).toBe('Praxis')

      // Group C: Prüfung (Assessment/Exams)
      expect(MethodType.create(9).getGroupName()).toBe('Prüfung')
      expect(MethodType.create(10).getGroupName()).toBe('Prüfung')
      expect(MethodType.create(11).getGroupName()).toBe('Prüfung')
    })

    it('should return consistent names for all group members', () => {
      // All Group A members return 'Erklärend'
      for (let i = 0; i <= 4; i++) {
        expect(MethodType.create(i).getGroupName()).toBe('Erklärend')
      }

      // All Group B members return 'Praxis'
      for (let i = 5; i <= 8; i++) {
        expect(MethodType.create(i).getGroupName()).toBe('Praxis')
      }

      // All Group C members return 'Prüfung'
      for (let i = 9; i <= 11; i++) {
        expect(MethodType.create(i).getGroupName()).toBe('Prüfung')
      }
    })

    it('should translate to correct learning modalities', () => {
      const testCases = [
        { id: 0, expected: 'Erklärend' }, // Explanation
        { id: 5, expected: 'Praxis' },    // Practice
        { id: 11, expected: 'Prüfung' }   // Assessment
      ]

      testCases.forEach(({ id, expected }) => {
        const method = MethodType.create(id)
        expect(method.getGroupName()).toBe(expected)
      })
    })
  })

  describe('String Representation - toString()', () => {
    it('should return zero-padded LM format (LM00-LM11)', () => {
      expect(MethodType.create(0).toString()).toBe('LM00')
      expect(MethodType.create(1).toString()).toBe('LM01')
      expect(MethodType.create(5).toString()).toBe('LM05')
      expect(MethodType.create(10).toString()).toBe('LM10')
      expect(MethodType.create(11).toString()).toBe('LM11')
    })

    it('should format all 12 methods correctly with leading zeros', () => {
      for (let i = 0; i <= 11; i++) {
        const expected = `LM${i.toString().padStart(2, '0')}`
        expect(MethodType.create(i).toString()).toBe(expected)
      }
    })

    it('should handle single-digit methods with leading zero', () => {
      // 0-9 should have leading zero
      expect(MethodType.create(0).toString()).toMatch(/^LM0\d$/)
      expect(MethodType.create(9).toString()).toBe('LM09')

      // 10-11 should not have extra padding
      expect(MethodType.create(10).toString()).toBe('LM10')
      expect(MethodType.create(11).toString()).toBe('LM11')
    })
  })

  describe('Numeric Value - toNumber()', () => {
    it('should return original numeric value for all method types', () => {
      expect(MethodType.create(0).toNumber()).toBe(0)
      expect(MethodType.create(1).toNumber()).toBe(1)
      expect(MethodType.create(5).toNumber()).toBe(5)
      expect(MethodType.create(10).toNumber()).toBe(10)
      expect(MethodType.create(11).toNumber()).toBe(11)
    })

    it('should maintain numeric accuracy across all method types', () => {
      for (let i = 0; i <= 11; i++) {
        expect(MethodType.create(i).toNumber()).toBe(i)
      }
    })
  })

  describe('Value Object Equality - equals()', () => {
    it('should identify equal method types', () => {
      expect(MethodType.create(0).equals(MethodType.create(0))).toBe(true)
      expect(MethodType.create(5).equals(MethodType.create(5))).toBe(true)
      expect(MethodType.create(11).equals(MethodType.create(11))).toBe(true)
    })

    it('should identify different method types', () => {
      expect(MethodType.create(0).equals(MethodType.create(1))).toBe(false)
      expect(MethodType.create(5).equals(MethodType.create(6))).toBe(false)
      expect(MethodType.create(0).equals(MethodType.create(11))).toBe(false)
    })

    it('should correctly compare cross-group method types', () => {
      // Group A vs Group B
      expect(MethodType.create(4).equals(MethodType.create(5))).toBe(false)

      // Group B vs Group C
      expect(MethodType.create(8).equals(MethodType.create(9))).toBe(false)

      // Group A vs Group C
      expect(MethodType.create(0).equals(MethodType.create(11))).toBe(false)
    })
  })

  describe('Integration - Complete Usage Patterns', () => {
    it('should demonstrate complete MethodType usage for Erklärend (Group A)', () => {
      const method = MethodType.create(2) // LM02

      expect(method.toNumber()).toBe(2)
      expect(method.toString()).toBe('LM02')
      expect(method.getGroup()).toBe('A')
      expect(method.getGroupName()).toBe('Erklärend')
      expect(method.equals(MethodType.create(2))).toBe(true)
      expect(method.equals(MethodType.create(3))).toBe(false)
    })

    it('should demonstrate complete MethodType usage for Praxis (Group B)', () => {
      const method = MethodType.create(6) // LM06

      expect(method.toNumber()).toBe(6)
      expect(method.toString()).toBe('LM06')
      expect(method.getGroup()).toBe('B')
      expect(method.getGroupName()).toBe('Praxis')
      expect(method.equals(MethodType.create(6))).toBe(true)
      expect(method.equals(MethodType.create(5))).toBe(false)
    })

    it('should demonstrate complete MethodType usage for Prüfung (Group C)', () => {
      const method = MethodType.create(10) // LM10

      expect(method.toNumber()).toBe(10)
      expect(method.toString()).toBe('LM10')
      expect(method.getGroup()).toBe('C')
      expect(method.getGroupName()).toBe('Prüfung')
      expect(method.equals(MethodType.create(10))).toBe(true)
      expect(method.equals(MethodType.create(11))).toBe(false)
    })

    it('should support method chaining patterns', () => {
      // Create → Group → GroupName chain
      const groupName = MethodType.create(7).getGroupName()
      expect(groupName).toBe('Praxis')

      // Create → toString → validate format
      const stringFormat = MethodType.create(3).toString()
      expect(stringFormat).toMatch(/^LM\d{2}$/)
    })
  })

  describe('Constraint Validation - Business Rules', () => {
    it('should enforce 0-11 constraint strictly (CRITICAL)', () => {
      // Valid range
      expect(() => MethodType.create(0)).not.toThrow()
      expect(() => MethodType.create(11)).not.toThrow()

      // Invalid: negative
      expect(() => MethodType.create(-1)).toThrow()

      // Invalid: > 11 (LM12-LM32 are system features, not content LMs)
      expect(() => MethodType.create(12)).toThrow()
      expect(() => MethodType.create(32)).toThrow()
    })

    it('should provide clear error messages for constraint violations', () => {
      const negativeError = () => MethodType.create(-5)
      expect(negativeError).toThrow('Invalid method type: -5. Must be 0-11 (LM00-LM11)')

      const tooLargeError = () => MethodType.create(20)
      expect(tooLargeError).toThrow('Invalid method type: 20. Must be 0-11 (LM00-LM11)')
    })

    it('should correctly distinguish Group sizes', () => {
      // Group A: 5 methods (0-4)
      const groupAMethods = [0, 1, 2, 3, 4]
      expect(groupAMethods.every(i => MethodType.create(i).getGroup() === 'A')).toBe(true)

      // Group B: 4 methods (5-8)
      const groupBMethods = [5, 6, 7, 8]
      expect(groupBMethods.every(i => MethodType.create(i).getGroup() === 'B')).toBe(true)

      // Group C: 3 methods (9-11)
      const groupCMethods = [9, 10, 11]
      expect(groupCMethods.every(i => MethodType.create(i).getGroup() === 'C')).toBe(true)
    })
  })

  describe('Regression Tests - Ensure Consistency', () => {
    it('should maintain immutability (cannot modify after creation)', () => {
      const method = MethodType.create(5)

      // Calling methods multiple times should return consistent results
      expect(method.getGroup()).toBe('B')
      expect(method.getGroup()).toBe('B')

      expect(method.getGroupName()).toBe('Praxis')
      expect(method.getGroupName()).toBe('Praxis')

      expect(method.toString()).toBe('LM05')
      expect(method.toString()).toBe('LM05')

      expect(method.toNumber()).toBe(5)
      expect(method.toNumber()).toBe(5)
    })

    it('should be usable as value object in collections', () => {
      const methods = [
        MethodType.create(0),
        MethodType.create(5),
        MethodType.create(11)
      ]

      expect(methods).toHaveLength(3)
      expect(methods[0].getGroup()).toBe('A')
      expect(methods[1].getGroup()).toBe('B')
      expect(methods[2].getGroup()).toBe('C')
    })

    it('should support comparison operations correctly', () => {
      const method1 = MethodType.create(5)
      const method2 = MethodType.create(5)
      const method3 = MethodType.create(6)

      // Equality should work
      expect(method1.equals(method2)).toBe(true)
      expect(method1.equals(method3)).toBe(false)

      // Can be used in filtering
      const methods = [method1, method3]
      const filterResult = methods.filter(m => m.equals(method1))
      expect(filterResult).toHaveLength(1)
    })
  })
})
