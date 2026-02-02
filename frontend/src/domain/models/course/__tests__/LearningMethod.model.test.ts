import { describe, it, expect } from 'vitest'
import { LearningMethod } from '../LearningMethod.model'
import { MethodType } from '../MethodType.vo'

describe('LearningMethod Domain Model', () => {
  // Helper function to create test instances
  const createTestMethod = (methodType: number = 5, name: string = 'Test Method') => {
    return LearningMethod.fromMethodType(
      MethodType.create(methodType),
      `lm-${methodType.toString().padStart(2, '0')}`,
      name,
      'Test description',
      'test-icon'
    )
  }

  describe('Creation & Validation', () => {
    it('should create LearningMethod with valid MethodType', () => {
      const method = createTestMethod(5)

      expect(method).toBeDefined()
      expect(method.id).toBe('lm-05')
      expect(method.name).toBe('Test Method')
      expect(method.description).toBe('Test description')
      expect(method.icon).toBe('test-icon')
    })

    it('should create from all method types 0-11', () => {
      for (let i = 0; i <= 11; i++) {
        const method = createTestMethod(i)

        expect(method).toBeDefined()
        expect(method.methodType.toNumber()).toBe(i)
      }
    })

    it('should enforce immutability (cannot modify fields)', () => {
      const method = createTestMethod(5)

      // Attempting to modify readonly fields should fail at TypeScript compilation
      // This test verifies the fields are actually readonly
      expect(Object.getOwnPropertyDescriptor(method, 'id')).toBeDefined()
      expect(Object.getOwnPropertyDescriptor(method, 'name')).toBeDefined()

      // Runtime verification: verify no setters exist
      const descriptor = Object.getOwnPropertyDescriptor(method, 'methodType')
      expect(descriptor?.writable).toBe(false)
    })
  })

  describe('Group Classification - isExplanation()', () => {
    it('should return true for Group A methods (0-4)', () => {
      // Group A: LM00-LM04
      for (let i = 0; i <= 4; i++) {
        const method = createTestMethod(i)
        expect(method.isExplanation()).toBe(true)
      }
    })

    it('should return false for Group B methods (5-8)', () => {
      // Group B: LM05-LM08
      for (let i = 5; i <= 8; i++) {
        const method = createTestMethod(i)
        expect(method.isExplanation()).toBe(false)
      }
    })

    it('should return false for Group C methods (9-11)', () => {
      // Group C: LM09-LM11
      for (let i = 9; i <= 11; i++) {
        const method = createTestMethod(i)
        expect(method.isExplanation()).toBe(false)
      }
    })

    it('should be consistent across multiple calls', () => {
      const method = createTestMethod(2)

      expect(method.isExplanation()).toBe(true)
      expect(method.isExplanation()).toBe(true)
      expect(method.isExplanation()).toBe(true)
    })
  })

  describe('Group Classification - isPractice()', () => {
    it('should return true for Group B methods (5-8)', () => {
      // Group B: LM05-LM08
      for (let i = 5; i <= 8; i++) {
        const method = createTestMethod(i)
        expect(method.isPractice()).toBe(true)
      }
    })

    it('should return false for Group A methods (0-4)', () => {
      // Group A: LM00-LM04
      for (let i = 0; i <= 4; i++) {
        const method = createTestMethod(i)
        expect(method.isPractice()).toBe(false)
      }
    })

    it('should return false for Group C methods (9-11)', () => {
      // Group C: LM09-LM11
      for (let i = 9; i <= 11; i++) {
        const method = createTestMethod(i)
        expect(method.isPractice()).toBe(false)
      }
    })

    it('should be consistent across multiple calls', () => {
      const method = createTestMethod(6)

      expect(method.isPractice()).toBe(true)
      expect(method.isPractice()).toBe(true)
      expect(method.isPractice()).toBe(true)
    })
  })

  describe('Group Classification - isAssessment()', () => {
    it('should return true for Group C methods (9-11)', () => {
      // Group C: LM09-LM11
      for (let i = 9; i <= 11; i++) {
        const method = createTestMethod(i)
        expect(method.isAssessment()).toBe(true)
      }
    })

    it('should return false for Group A methods (0-4)', () => {
      // Group A: LM00-LM04
      for (let i = 0; i <= 4; i++) {
        const method = createTestMethod(i)
        expect(method.isAssessment()).toBe(false)
      }
    })

    it('should return false for Group B methods (5-8)', () => {
      // Group B: LM05-LM08
      for (let i = 5; i <= 8; i++) {
        const method = createTestMethod(i)
        expect(method.isAssessment()).toBe(false)
      }
    })

    it('should be consistent across multiple calls', () => {
      const method = createTestMethod(10)

      expect(method.isAssessment()).toBe(true)
      expect(method.isAssessment()).toBe(true)
      expect(method.isAssessment()).toBe(true)
    })
  })

  describe('Classification Mutual Exclusivity', () => {
    it('should have exactly one classification true for Group A', () => {
      const method = createTestMethod(2)

      const trueCount = [
        method.isExplanation(),
        method.isPractice(),
        method.isAssessment()
      ].filter(v => v === true).length

      expect(trueCount).toBe(1)
    })

    it('should have exactly one classification true for Group B', () => {
      const method = createTestMethod(6)

      const trueCount = [
        method.isExplanation(),
        method.isPractice(),
        method.isAssessment()
      ].filter(v => v === true).length

      expect(trueCount).toBe(1)
    })

    it('should have exactly one classification true for Group C', () => {
      const method = createTestMethod(10)

      const trueCount = [
        method.isExplanation(),
        method.isPractice(),
        method.isAssessment()
      ].filter(v => v === true).length

      expect(trueCount).toBe(1)
    })
  })

  describe('Display Name Formatting', () => {
    it('should format displayName as "LM##: Name"', () => {
      const method = LearningMethod.fromMethodType(
        MethodType.create(5),
        'lm-05',
        'Interactive Math'
      )

      expect(method.displayName).toBe('LM05: Interactive Math')
    })

    it('should format with zero-padding', () => {
      const testCases = [
        { methodType: 0, name: 'Method 0', expected: 'LM00: Method 0' },
        { methodType: 1, name: 'Method 1', expected: 'LM01: Method 1' },
        { methodType: 5, name: 'Method 5', expected: 'LM05: Method 5' },
        { methodType: 10, name: 'Method 10', expected: 'LM10: Method 10' },
        { methodType: 11, name: 'Method 11', expected: 'LM11: Method 11' }
      ]

      testCases.forEach(({ methodType, name, expected }) => {
        const method = LearningMethod.fromMethodType(MethodType.create(methodType), undefined, name)
        expect(method.displayName).toBe(expected)
      })
    })

    it('should handle names with special characters', () => {
      const method = LearningMethod.fromMethodType(
        MethodType.create(3),
        'lm-03',
        'Diagramm/Visualisierung'
      )

      expect(method.displayName).toBe('LM03: Diagramm/Visualisierung')
    })
  })

  describe('Group Delegation - Getters', () => {
    it('should delegate group() to MethodType.getGroup()', () => {
      const testCases = [
        { methodType: 0, expected: 'A' },
        { methodType: 4, expected: 'A' },
        { methodType: 5, expected: 'B' },
        { methodType: 8, expected: 'B' },
        { methodType: 9, expected: 'C' },
        { methodType: 11, expected: 'C' }
      ]

      testCases.forEach(({ methodType, expected }) => {
        const method = createTestMethod(methodType)
        expect(method.group).toBe(expected)
      })
    })

    it('should delegate groupName() to MethodType.getGroupName()', () => {
      const testCases = [
        { methodType: 0, expected: 'Erklärend' },
        { methodType: 4, expected: 'Erklärend' },
        { methodType: 5, expected: 'Praxis' },
        { methodType: 8, expected: 'Praxis' },
        { methodType: 9, expected: 'Prüfung' },
        { methodType: 11, expected: 'Prüfung' }
      ]

      testCases.forEach(({ methodType, expected }) => {
        const method = createTestMethod(methodType)
        expect(method.groupName).toBe(expected)
      })
    })
  })

  describe('API Transformation - fromAPI()', () => {
    it('should transform snake_case API data to domain model', () => {
      const apiData = {
        id: 'lm-05',
        method_type: 5,
        name: 'Interactive Math',
        description: 'Math exercises with interactive feedback',
        icon: 'calculate'
      }

      const method = LearningMethod.fromAPI(apiData)

      expect(method.id).toBe('lm-05')
      expect(method.methodType.toNumber()).toBe(5)
      expect(method.name).toBe('Interactive Math')
      expect(method.description).toBe('Math exercises with interactive feedback')
      expect(method.icon).toBe('calculate')
    })

    it('should handle camelCase methodType field', () => {
      const apiData = {
        id: 'lm-06',
        methodType: 6,  // camelCase instead of snake_case
        name: 'Flashcards',
        description: 'Flash card learning system',
        icon: 'style'
      }

      const method = LearningMethod.fromAPI(apiData)

      expect(method.methodType.toNumber()).toBe(6)
    })

    it('should prefer snake_case method_type over methodType', () => {
      const apiData = {
        id: 'lm-07',
        method_type: 7,    // snake_case should be used
        methodType: 99,    // This should be ignored
        name: 'Drag & Drop',
        description: 'Drag and drop exercises',
        icon: 'drag'
      }

      const method = LearningMethod.fromAPI(apiData)

      expect(method.methodType.toNumber()).toBe(7)  // snake_case wins
    })

    it('should throw error for invalid method_type (negative)', () => {
      const apiData = {
        id: 'invalid',
        method_type: -1,
        name: 'Invalid',
        description: 'Invalid method',
        icon: 'invalid'
      }

      expect(() => LearningMethod.fromAPI(apiData)).toThrow('Invalid method type: -1')
    })

    it('should throw error for invalid method_type (>11)', () => {
      const apiData = {
        id: 'invalid',
        method_type: 12,  // LM12+ are system features, not content LMs
        name: 'Invalid',
        description: 'Invalid method',
        icon: 'invalid'
      }

      expect(() => LearningMethod.fromAPI(apiData)).toThrow('Invalid method type: 12')
    })

    it('should handle all valid method types (0-11)', () => {
      for (let i = 0; i <= 11; i++) {
        const apiData = {
          id: `lm-${i.toString().padStart(2, '0')}`,
          method_type: i,
          name: `Method ${i}`,
          description: `Description for method ${i}`,
          icon: 'test'
        }

        const method = LearningMethod.fromAPI(apiData)

        expect(method.methodType.toNumber()).toBe(i)
        expect(method.id).toBe(`lm-${i.toString().padStart(2, '0')}`)
      }
    })

    it('should be a single transformation point for API DTOs', () => {
      // This test verifies that fromAPI is the canonical transformation
      const apiData = {
        id: 'lm-03',
        method_type: 3,
        name: 'Diagramm/Visualisierung',
        description: 'Visual diagrams',
        icon: 'diagram'
      }

      const method1 = LearningMethod.fromAPI(apiData)
      const method2 = LearningMethod.fromAPI(apiData)

      // Same input should produce consistent results
      expect(method1.id).toBe(method2.id)
      expect(method1.methodType.toNumber()).toBe(method2.methodType.toNumber())
      expect(method1.displayName).toBe(method2.displayName)
    })
  })

  describe('Factory Methods - fromMethodType()', () => {
    it('should create from MethodType with all parameters', () => {
      const methodType = MethodType.create(5)
      const method = LearningMethod.fromMethodType(
        methodType,
        'custom-id',
        'Custom Name',
        'Custom description',
        'custom-icon'
      )

      expect(method.id).toBe('custom-id')
      expect(method.name).toBe('Custom Name')
      expect(method.description).toBe('Custom description')
      expect(method.icon).toBe('custom-icon')
      expect(method.methodType.toNumber()).toBe(5)
    })

    it('should auto-generate ID if not provided', () => {
      const methodType = MethodType.create(7)
      const method = LearningMethod.fromMethodType(methodType)

      expect(method.id).toBe('lm-07')
    })

    it('should use MethodType string representation as default name', () => {
      const methodType = MethodType.create(8)
      const method = LearningMethod.fromMethodType(methodType)

      expect(method.name).toBe('LM08')
    })

    it('should provide sensible defaults for optional fields', () => {
      const methodType = MethodType.create(4)
      const method = LearningMethod.fromMethodType(methodType)

      expect(method.description).toBe('Learning method LM04')
      expect(method.icon).toBe('school')
    })

    it('should accept partial parameters', () => {
      const methodType = MethodType.create(2)
      const method = LearningMethod.fromMethodType(
        methodType,
        'lm-02-custom',
        'Custom Theory Method'
      )

      expect(method.id).toBe('lm-02-custom')
      expect(method.name).toBe('Custom Theory Method')
      expect(method.description).toBe('Learning method LM02')
      expect(method.icon).toBe('school')
    })
  })

  describe('Serialization - toJSON()', () => {
    it('should include all data fields', () => {
      const method = createTestMethod(5, 'Interactive Math')
      const json = method.toJSON()

      expect(json.id).toBe('lm-05')
      expect(json.methodType).toBe(5)
      expect(json.name).toBe('Interactive Math')
      expect(json.description).toBe('Test description')
      expect(json.icon).toBe('test-icon')
    })

    it('should include all computed properties', () => {
      const method = createTestMethod(5)
      const json = method.toJSON()

      expect(json.displayName).toBe('LM05: Test Method')
      expect(json.group).toBe('B')
      expect(json.groupName).toBe('Praxis')
      expect(json.isExplanation).toBe(false)
      expect(json.isPractice).toBe(true)
      expect(json.isAssessment).toBe(false)
    })

    it('should have all properties of valid toJSON output', () => {
      const method = createTestMethod(10)
      const json = method.toJSON()

      // Check complete structure
      expect(Object.keys(json).sort()).toEqual([
        'description',
        'displayName',
        'group',
        'groupName',
        'icon',
        'id',
        'isAssessment',
        'isExplanation',
        'isPractice',
        'methodType',
        'name'
      ].sort())
    })

    it('should serialize correctly for all method types', () => {
      const testCases = [
        { methodType: 0, group: 'A', isExplanation: true, isPractice: false, isAssessment: false },
        { methodType: 5, group: 'B', isExplanation: false, isPractice: true, isAssessment: false },
        { methodType: 11, group: 'C', isExplanation: false, isPractice: false, isAssessment: true }
      ]

      testCases.forEach(({ methodType, group, isExplanation, isPractice, isAssessment }) => {
        const method = createTestMethod(methodType)
        const json = method.toJSON()

        expect(json.methodType).toBe(methodType)
        expect(json.group).toBe(group)
        expect(json.isExplanation).toBe(isExplanation)
        expect(json.isPractice).toBe(isPractice)
        expect(json.isAssessment).toBe(isAssessment)
      })
    })
  })

  describe('Integration with MethodType - Constraint Enforcement', () => {
    it('should propagate MethodType constraint violation in fromAPI', () => {
      expect(() => {
        LearningMethod.fromAPI({
          id: 'invalid',
          method_type: -1,
          name: 'Invalid',
          description: 'Invalid',
          icon: 'invalid'
        })
      }).toThrow('Invalid method type: -1. Must be 0-11 (LM00-LM11)')
    })

    it('should enforce 0-11 range for valid construction', () => {
      // Valid: All 0-11 should work
      for (let i = 0; i <= 11; i++) {
        expect(() => {
          LearningMethod.fromMethodType(MethodType.create(i))
        }).not.toThrow()
      }
    })

    it('should reject invalid method types via fromAPI', () => {
      const invalidTypes = [-1, -10, 12, 13, 100]

      invalidTypes.forEach(invalid => {
        expect(() => {
          LearningMethod.fromAPI({
            id: 'test',
            method_type: invalid,
            name: 'Test',
            description: 'Test',
            icon: 'test'
          })
        }).toThrow()
      })
    })

    it('should validate through MethodType chain', () => {
      // fromAPI -> MethodType.create -> constraint validation
      const method = LearningMethod.fromAPI({
        id: 'lm-05',
        method_type: 5,
        name: 'Valid Method',
        description: 'Valid',
        icon: 'valid'
      })

      // Verify constraint was enforced at MethodType level
      expect(method.methodType.toNumber()).toBe(5)
      expect(() => method.methodType.equals(MethodType.create(5))).not.toThrow()
    })
  })

  describe('Complete Usage Patterns', () => {
    it('should demonstrate complete Group A (Explanation) workflow', () => {
      const method = LearningMethod.fromAPI({
        id: 'lm-02',
        method_type: 2,
        name: 'Schritt-für-Schritt',
        description: 'Step-by-Step explanation',
        icon: 'steps'
      })

      // Verify all properties and classifications
      expect(method.displayName).toBe('LM02: Schritt-für-Schritt')
      expect(method.group).toBe('A')
      expect(method.groupName).toBe('Erklärend')
      expect(method.isExplanation()).toBe(true)
      expect(method.isPractice()).toBe(false)
      expect(method.isAssessment()).toBe(false)

      const json = method.toJSON()
      expect(json.displayName).toBe('LM02: Schritt-für-Schritt')
      expect(json.isExplanation).toBe(true)
    })

    it('should demonstrate complete Group B (Practice) workflow', () => {
      const method = LearningMethod.fromAPI({
        id: 'lm-06',
        method_type: 6,
        name: 'Flashcards',
        description: 'Flash card learning system',
        icon: 'style'
      })

      // Verify all properties and classifications
      expect(method.displayName).toBe('LM06: Flashcards')
      expect(method.group).toBe('B')
      expect(method.groupName).toBe('Praxis')
      expect(method.isExplanation()).toBe(false)
      expect(method.isPractice()).toBe(true)
      expect(method.isAssessment()).toBe(false)

      const json = method.toJSON()
      expect(json.isPractice).toBe(true)
    })

    it('should demonstrate complete Group C (Assessment) workflow', () => {
      const method = LearningMethod.fromAPI({
        id: 'lm-10',
        method_type: 10,
        name: 'Multiple-Choice Quiz',
        description: 'Multiple choice quiz format',
        icon: 'quiz'
      })

      // Verify all properties and classifications
      expect(method.displayName).toBe('LM10: Multiple-Choice Quiz')
      expect(method.group).toBe('C')
      expect(method.groupName).toBe('Prüfung')
      expect(method.isExplanation()).toBe(false)
      expect(method.isPractice()).toBe(false)
      expect(method.isAssessment()).toBe(true)

      const json = method.toJSON()
      expect(json.isAssessment).toBe(true)
    })
  })
})
