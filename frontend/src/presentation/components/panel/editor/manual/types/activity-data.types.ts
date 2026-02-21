/**
 * Type definitions for all 12 Learning Method data structures.
 * Each LM stores its specific content in the JSONB `data` field.
 */

// LM00 - Deep Explanation
export interface LM00Data {
  content: string
  key_concepts: string[]
  summary: string
}

// LM01 - Step by Step
export interface LM01Step {
  title: string
  content: string
  hint?: string
}
export interface LM01Data {
  steps: LM01Step[]
}

// LM02 - Interactive Theory
export interface LM02Section {
  title: string
  content: string
  question?: string
  answer?: string
}
export interface LM02Data {
  sections: LM02Section[]
}

// LM03 - Diagram Visualization
export interface LM03Element {
  label: string
  description?: string
}
export interface LM03Data {
  diagram_type: string
  description: string
  diagram_code: string
  elements: LM03Element[]
}

// LM04 - Example Scenario
export interface LM04Scenario {
  title: string
  situation: string
  solution: string
  takeaway?: string
}
export interface LM04Data {
  scenarios: LM04Scenario[]
}

// LM05 - Math Interactive
export interface LM05Step {
  description: string
}
export interface LM05Problem {
  text: string
  formula?: string
  solution: string
  steps?: LM05Step[]
}
export interface LM05Data {
  problems: LM05Problem[]
}

// LM06 - Flashcards
export interface LM06Card {
  front: string
  back: string
  hint?: string
}
export interface LM06Data {
  cards: LM06Card[]
}

// LM07 - Drag and Drop
export interface LM07Item {
  id: string
  text: string
}
export interface LM07Group {
  label: string
  correct_items: string[]
}
export interface LM07Data {
  items: LM07Item[]
  groups: LM07Group[]
}

// LM08 - Cloze Test
export interface LM08Blank {
  answer: string
  alternatives: string[]
}
export interface LM08Data {
  text: string
  blanks: LM08Blank[]
}

// LM09 - Free Text Long Answer
export interface LM09Data {
  question: string
  min_words: number
  max_words?: number
  rubric: string
  sample_answer: string
}

// LM10 - IHK Style Tasks
export interface LM10Criterion {
  text: string
  points?: number
}
export interface LM10Data {
  question_type: string
  question_text: string
  context: string
  criteria: LM10Criterion[]
}

// LM11 - Multi Step Practical
export interface LM11Step {
  title: string
  description: string
  points?: number
  rubric?: string
}
export interface LM11Data {
  steps: LM11Step[]
}

// Union type for all LM data
export type ActivityData =
  | LM00Data | LM01Data | LM02Data | LM03Data
  | LM04Data | LM05Data | LM06Data | LM07Data
  | LM08Data | LM09Data | LM10Data | LM11Data

// Default data factory
export function getDefaultData(methodType: number): Record<string, unknown> {
  const defaults: Record<number, () => Record<string, unknown>> = {
    0: () => ({ content: '', key_concepts: [], summary: '' }),
    1: () => ({ steps: [] }),
    2: () => ({ sections: [] }),
    3: () => ({ diagram_type: 'flowchart', description: '', diagram_code: '', elements: [] }),
    4: () => ({ scenarios: [] }),
    5: () => ({ problems: [] }),
    6: () => ({ cards: [] }),
    7: () => ({ items: [], groups: [] }),
    8: () => ({ text: '', blanks: [] }),
    9: () => ({ question: '', min_words: 50, max_words: 500, rubric: '', sample_answer: '' }),
    10: () => ({ question_type: 'situational', question_text: '', context: '', criteria: [] }),
    11: () => ({ steps: [] }),
  }
  return defaults[methodType]?.() ?? {}
}
