// Typed props for all 19 learning method renderers
// Based on actual DB JSONB structures from learning_method_instances

// ── Type 0: Deep Explanation ──────────────────────────
export interface DeepExplanationData {
  content?: string
  keyPoints?: string[]
}

export interface DeepExplanationSolution {
  summary?: string
}

// ── Type 1: Step by Step ──────────────────────────────
export interface StepByStepStep {
  step: number
  title: string
  content: string
}

export interface StepByStepData {
  steps?: StepByStepStep[]
}

export interface StepByStepSolution {
  expectedOutput?: string
  commonErrors?: string[]
}

// ── Type 2: Interactive Theory ────────────────────────
export interface TheoryExample {
  code: string
  explanation: string
}

export interface InteractiveTheoryData {
  concept?: string
  examples?: TheoryExample[]
  interactiveQuestion?: string
}

export interface InteractiveTheorySolution {
  answer?: string
  explanation?: string
}

// ── Type 3: Diagram ──────────────────────────────────
export interface DiagramData {
  diagram?: string
  description?: string
  questions?: string[]
}

export interface DiagramSolution {
  answers?: string[]
}

// ── Type 4: Scenario ─────────────────────────────────
export interface ScenarioData {
  scenario?: string
  requirements?: string[]
  hints?: string[]
}

export interface ScenarioSolution {
  code?: string
}

// ── Type 5: Math Interactive (4 sub-modes) ───────────
export interface MathProblem {
  question: string
  answer: string | number
  hint?: string
  points?: number
  scenario_title?: string
  scenario_text?: string
}

export interface MathEquation {
  equation: string
  solution: string
  hint?: string
}

export interface MathStep {
  step: number
  instruction: string
  expectedResult: string
}

export interface MathTestCase {
  input: string
  expected: string
}

export interface MathInteractiveData {
  // Mode detection: check which array exists
  problems?: MathProblem[]
  equations?: MathEquation[]
  steps?: MathStep[]
  task?: string
  testCases?: MathTestCase[]
  bonusTask?: string
}

export interface MathInteractiveSolution {
  code?: string
  explanation?: string
}

// ── Type 6: Flashcards ───────────────────────────────
export interface FlashcardItem {
  front: string
  back: string
}

export interface FlashcardsData {
  cards?: FlashcardItem[]
}

// ── Type 7: Drag & Drop ─────────────────────────────
export interface DragDropItem {
  label?: string
  term?: string
  correctCategory: string
}

export interface DragDropData {
  items?: DragDropItem[]
  categories?: string[]
}

// ── Type 8: Cloze Test ──────────────────────────────
export interface ClozeBlank {
  hint: string
  answer: string
  position: number
}

// Exam-generated sentence format (from LMContentMapper)
export interface ClozeSentence {
  text: string
  answers: string[]
  source_question_id?: string
}

export interface ClozeData {
  blanks?: ClozeBlank[]
  codeTemplate?: string
  // Exam-style sentences (alternative to blanks+codeTemplate)
  sentences?: ClozeSentence[]
}

export interface ClozeSolution {
  completedCode?: string
}

// ── Type 9: Free Text ───────────────────────────────
export interface FreeTextData {
  question?: string
  hints?: string[]
  wordLimit?: number
}

export interface FreeTextSolution {
  modelAnswer?: string
  keyPoints?: string[]
}

// ── Type 10: Multiple Choice ────────────────────────
export interface MCQuestion {
  question: string
  options: string[]
  correctAnswers: string[]
  explanation?: string
}

export interface MultipleChoiceData {
  questions?: MCQuestion[]
}

// ── Type 11 (core): Multi-Step Exam ─────────────────
export interface ExamStep {
  title: string
  description: string
  expectedAnswer?: string
  points?: number
  inputRows?: number
}

export interface MultiStepExamData {
  task?: string
  description?: string
  steps?: ExamStep[]
}

export interface MultiStepExamSolution {
  steps?: string[]
  explanation?: string
}

// ── Type 100: Whiteboard ────────────────────────────
export interface WhiteboardData {
  task?: string
  description?: string
  requirements?: string[]
  requireExplanation?: boolean
}

export interface WhiteboardSolution {
  description?: string
  diagram?: string
}

// ── Type 101: Hands-On Lab ──────────────────────────
export interface LabTask {
  title?: string
  hint?: string
}

export interface HandsOnLabData {
  task?: string
  description?: string
  tasks?: (LabTask | string)[]
  checklist?: (LabTask | string)[]
  language?: string
  editorRows?: number
  starterCode?: string
}

export interface HandsOnLabSolution {
  code?: string
  explanation?: string
}

// ── Type 102: Time Limit ────────────────────────────
export interface TimedQuestion {
  question: string
  answer: string
}

export interface TimeLimitData {
  task?: string
  description?: string
  questions?: TimedQuestion[]
  timeLimitMinutes?: number
}

export interface TimeLimitSolution {
  explanation?: string
}

// ── Type 103: True/False ────────────────────────────
export interface TFStatement {
  statement?: string
  text?: string
  correct?: boolean
  isTrue?: boolean
  explanation?: string
}

export interface TrueFalseData {
  statements?: TFStatement[]
}

// ── Type 104: Comprehension Check ───────────────────
export interface ComprehensionOption {
  text: string
  correct: boolean
}

export interface ComprehensionCheckData {
  question?: string
  options?: ComprehensionOption[]
  explanation?: string
  answer?: string
}

export interface ComprehensionCheckSolution {
  explanation?: string
  answer?: string
}

// ── Type 105: Oral Explanation ──────────────────────
export interface OralExplanationData {
  task?: string
  description?: string
  topic?: string
  question?: string
  keyPoints?: string[]
  minWords?: number
  criteria?: string[]
}

export interface OralExplanationSolution {
  explanation?: string
  modelAnswer?: string
}

// ── Type 106: Chapter Exam ──────────────────────────
export interface ChapterExamQuestion {
  question: string
  options?: ComprehensionOption[]
  answer?: string
  points?: number
}

export interface ChapterExamData {
  task?: string
  description?: string
  questions?: ChapterExamQuestion[]
  passingPercent?: number
}

export interface ChapterExamSolution {
  explanations?: string[]
}
