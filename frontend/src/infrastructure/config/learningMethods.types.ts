/**
 * Type definitions for learning methods configuration.
 *
 * Separated from data and helpers to keep each file under 500 LOC.
 */

/** Content groups: A (Erklaerend), B (Praxis), C (Pruefung) */
export type LearningMethodGroup = 'A' | 'B' | 'C'

/** Legacy groups D, E, F -- now System-Features */
export type LegacyGroup = 'D' | 'E' | 'F'

/** Union of all group identifiers */
export type AllGroups = LearningMethodGroup | LegacyGroup

export interface LearningMethod {
  id: string          // "00"-"25" (OHNE "LM")
  code: number        // 0-25 (Content-LMs)
  name: string        // Deutscher Name
  group: AllGroups    // A, B, C = Content; D, E, F = System-Features (inaktiv)
  category: 'erklaerend' | 'praxis' | 'pruefung' | 'system-feature'
  description: string
  icon: string        // Emoji
  promptKey: string   // Backend prompt_key
  active: boolean     // true = Content-LM, false = System-Feature
}
