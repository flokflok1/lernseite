/**
 * Learning method definitions and group metadata.
 *
 * 19 Content-Lernmethoden in 3 Gruppen (A-C):
 * - A: Erklaerend (LM00, LM01, LM02, LM03, LM06) - 5 Methoden
 * - B: Praxis (LM08, LM12, LM13, LM14, LM15, LM17) - 6 Methoden
 * - C: Pruefung (LM18-LM25) - 8 Methoden
 *
 * System-Features (fruehere LMs, jetzt eigenstaendige Module):
 * - LM04: Sokratischer Dialog -> TutorAgent
 * - LM05: Mindmap-Generator -> CourseFeatures.mindmap
 * - LM07: NPC-Tutor -> TutorAgent
 * - LM09-LM11, LM16: IT-Sandboxes -> System-Feature IT-Umgebungen
 * - LM26-LM32: Kollaborativ -> System-Features Kollaboration
 *
 * Referenz: 02_Lernmethoden.md, 02a_System-Features.md
 *
 * Diese Konfiguration MUSS mit dem Backend uebereinstimmen!
 * Backend-Quelle: /api/v1/admin/learning-method-types
 */

import type { LearningMethod, LearningMethodGroup } from './learningMethods.types.js'

// ==========================================================================
// Full learning method registry (content + inactive system-features)
// ==========================================================================

export const LEARNING_METHODS: LearningMethod[] = [
  // Gruppe A: Erklaerend (LM00, LM01, LM02, LM03, LM06)
  {
    id: '00', code: 0, name: 'Tiefgehende Erklaerung', group: 'A',
    category: 'erklaerend',
    description: 'KI-generierte Erklaerung mit Beispielen & Analogien',
    icon: '🔍', promptKey: 'deep_explanation', active: true
  },
  {
    id: '01', code: 1, name: 'Schritt-fuer-Schritt', group: 'A',
    category: 'erklaerend',
    description: 'Sequenzielle Anleitung in nummerierten Schritten',
    icon: '📋', promptKey: 'step_by_step', active: true
  },
  {
    id: '02', code: 2, name: 'Interaktive Theorie', group: 'A',
    category: 'erklaerend',
    description: 'Theoriebloecke mit eingebetteten Kontrollfragen',
    icon: '📖', promptKey: 'interactive_theory', active: true
  },
  {
    id: '03', code: 3, name: 'Diagramm/Visualisierung', group: 'A',
    category: 'erklaerend',
    description: 'Visuelle Modelle (Netzwerk, OSI, ER, Flows)',
    icon: '📊', promptKey: 'visualization', active: true
  },
  {
    id: '06', code: 6, name: 'Beispiel-Szenario', group: 'A',
    category: 'erklaerend',
    description: 'Realitaetsnahe Case-Erklaerung eines Konzepts',
    icon: '💼', promptKey: 'scenario_explanation', active: true
  },

  // Gruppe B: Praxis (LM08, LM12, LM13, LM14, LM15, LM17)
  {
    id: '08', code: 8, name: 'Whiteboard-Aufgabe', group: 'B',
    category: 'praxis',
    description: 'Lernende zeichnen/verbinden Topologien, Skizzen',
    icon: '🎨', promptKey: 'whiteboard', active: true
  },
  {
    id: '12', code: 12, name: 'Mathe-Interaktiv', group: 'B',
    category: 'praxis',
    description: 'Rechenaufgaben mit Schritt-fuer-Schritt-Erklaerung',
    icon: '🔢', promptKey: 'math_interactive', active: true
  },
  {
    id: '13', code: 13, name: 'Flashcards', group: 'B',
    category: 'praxis',
    description: 'Karteikarten mit Spaced-Repetition',
    icon: '🗂️', promptKey: 'flashcards', active: true
  },
  {
    id: '14', code: 14, name: 'Drag & Drop', group: 'B',
    category: 'praxis',
    description: 'Zuordnungs-/Matching-Aufgaben',
    icon: '🎯', promptKey: 'drag_drop', active: true
  },
  {
    id: '15', code: 15, name: 'Lueckentext', group: 'B',
    category: 'praxis',
    description: 'Fill-in-the-blanks in Texten/Configs',
    icon: '✍️', promptKey: 'fill_blanks', active: true
  },
  {
    id: '17', code: 17, name: 'Hands-on Lab', group: 'B',
    category: 'praxis',
    description: 'Virtuelle Umgebung (Terminal/IDE) mit Aufgabe',
    icon: '🧪', promptKey: 'hands_on_lab', active: true
  },

  // Gruppe C: Pruefung (LM18-LM25)
  {
    id: '18', code: 18, name: 'Freitext-Langantwort', group: 'C',
    category: 'pruefung',
    description: 'Lange Antworten, KI bewertet mit Rubric',
    icon: '📝', promptKey: 'long_answer', active: true
  },
  {
    id: '19', code: 19, name: 'IHK-Stil Aufgaben', group: 'C',
    category: 'pruefung',
    description: 'Pruefungsnahe MC/Lueckentext/Szenario',
    icon: '🏛️', promptKey: 'ihk_style', active: true
  },
  {
    id: '20', code: 20, name: 'Multi-Step Praxispruefung', group: 'C',
    category: 'pruefung',
    description: 'Mehrstufige Pruefungsketten',
    icon: '📋', promptKey: 'multi_step_exam', active: true
  },
  {
    id: '21', code: 21, name: 'Zeitlimit-Training', group: 'C',
    category: 'pruefung',
    description: 'Aufgaben unter Zeitdruck (Countdown)',
    icon: '⏱️', promptKey: 'time_limit', active: true
  },
  {
    id: '22', code: 22, name: 'Pruefungs-Quiz', group: 'C',
    category: 'pruefung',
    description: 'Quiz mit sofortigem Feedback',
    icon: '☑️', promptKey: 'exam_quiz', active: true
  },
  {
    id: '23', code: 23, name: 'Verstaendnis-Checks', group: 'C',
    category: 'pruefung',
    description: 'Single-Item-Checks nach Lerneinheit',
    icon: '✅', promptKey: 'comprehension_check', active: true
  },
  {
    id: '24', code: 24, name: 'Muendliche Erklaerung', group: 'C',
    category: 'pruefung',
    description: 'User erklaert muendlich, KI bewertet',
    icon: '🎤', promptKey: 'oral_explanation', active: true
  },
  {
    id: '25', code: 25, name: 'Kapitel-Endpruefung', group: 'C',
    category: 'pruefung',
    description: 'Groessere Pruefung am Kapitelende',
    icon: '🎓', promptKey: 'chapter_exam', active: true
  },

  // ==========================================================================
  // SYSTEM-FEATURES (fruehere LMs, jetzt eigenstaendige Module)
  // Diese sind NICHT als Content-LMs verfuegbar!
  // Siehe: 02a_System-Features.md
  // ==========================================================================

  // Gruppe D: TutorAgent (frueher Pro)
  {
    id: '04', code: 4, name: '[System-Feature] Sokratischer Dialog', group: 'D',
    category: 'system-feature',
    description: 'Jetzt: TutorAgent-Modul',
    icon: '💬', promptKey: 'socratic_dialog', active: false
  },
  {
    id: '05', code: 5, name: '[System-Feature] Mindmap-Generator', group: 'D',
    category: 'system-feature',
    description: 'Jetzt: CourseFeatures.mindmap',
    icon: '🗺️', promptKey: 'mindmap', active: false
  },
  {
    id: '07', code: 7, name: '[System-Feature] NPC-Tutor-Lecture', group: 'D',
    category: 'system-feature',
    description: 'Jetzt: TutorAgent-Modul',
    icon: '🤖', promptKey: 'npc_tutor', active: false
  },

  // Gruppe E: IT-Sandbox
  {
    id: '09', code: 9, name: '[System-Feature] Code/IT-Config Sandbox', group: 'E',
    category: 'system-feature',
    description: 'Jetzt: System-Feature IT-Umgebungen',
    icon: '💻', promptKey: 'code_sandbox', active: false
  },
  {
    id: '10', code: 10, name: '[System-Feature] Netzwerk-Simulation', group: 'E',
    category: 'system-feature',
    description: 'Jetzt: System-Feature IT-Umgebungen',
    icon: '🌐', promptKey: 'network_sim', active: false
  },
  {
    id: '11', code: 11, name: '[System-Feature] IT-Szenario loesen', group: 'E',
    category: 'system-feature',
    description: 'Jetzt: System-Feature IT-Umgebungen',
    icon: '🔧', promptKey: 'it_scenario', active: false
  },
  {
    id: '16', code: 16, name: '[System-Feature] Fehleranalyse', group: 'E',
    category: 'system-feature',
    description: 'Jetzt: System-Feature IT-Umgebungen',
    icon: '🔍', promptKey: 'error_analysis', active: false
  },

  // Gruppe F: Kollaboration
  {
    id: '26', code: 26, name: '[System-Feature] Peer Instruction', group: 'F',
    category: 'system-feature',
    description: 'Jetzt: System-Feature Kollaboration',
    icon: '👥', promptKey: 'peer_instruction', active: false
  },
  {
    id: '27', code: 27, name: '[System-Feature] Team-Case', group: 'F',
    category: 'system-feature',
    description: 'Jetzt: System-Feature Kollaboration',
    icon: '🤝', promptKey: 'team_case', active: false
  },
  {
    id: '28', code: 28, name: '[System-Feature] Peer Review', group: 'F',
    category: 'system-feature',
    description: 'Jetzt: System-Feature Kollaboration',
    icon: '📋', promptKey: 'peer_review', active: false
  },
  {
    id: '29', code: 29, name: '[System-Feature] Lerntagebuch', group: 'F',
    category: 'system-feature',
    description: 'Jetzt: System-Feature Kollaboration',
    icon: '📔', promptKey: 'learning_journal', active: false
  },
  {
    id: '30', code: 30, name: '[System-Feature] Projekt-Portfolio', group: 'F',
    category: 'system-feature',
    description: 'Jetzt: System-Feature Kollaboration',
    icon: '📁', promptKey: 'portfolio', active: false
  },
  {
    id: '31', code: 31, name: '[System-Feature] Projektbasiertes Lernen', group: 'F',
    category: 'system-feature',
    description: 'Jetzt: System-Feature Kollaboration',
    icon: '🏗️', promptKey: 'project_based', active: false
  }
]

// ==========================================================================
// Derived constants
// ==========================================================================

/** Only active Content-LMs (19 Methoden) */
export const ACTIVE_LEARNING_METHODS: LearningMethod[] = LEARNING_METHODS.filter(m => m.active)

/** Content-Gruppen (A, B, C) */
export const LEARNING_METHOD_GROUPS = {
  A: {
    id: 'A' as LearningMethodGroup,
    name: 'Erklaerend',
    range: 'LM00, LM01, LM02, LM03, LM06',
    icon: '📚',
    color: 'blue',
    count: 5
  },
  B: {
    id: 'B' as LearningMethodGroup,
    name: 'Praxis',
    range: 'LM08, LM12, LM13, LM14, LM15, LM17',
    icon: '🎯',
    color: 'green',
    count: 6
  },
  C: {
    id: 'C' as LearningMethodGroup,
    name: 'Pruefung',
    range: 'LM18-LM25',
    icon: '📝',
    color: 'orange',
    count: 8
  }
} as const

/** System-Features (frueher D, E, F - jetzt separate Module) */
export const SYSTEM_FEATURE_GROUPS = {
  D: {
    id: 'D',
    name: 'TutorAgent',
    module: 'TutorAgent',
    range: 'LM04, LM05, LM07',
    icon: '💬',
    color: 'purple'
  },
  E: {
    id: 'E',
    name: 'IT-Umgebungen',
    module: 'IT-Sandbox',
    range: 'LM09, LM10, LM11, LM16',
    icon: '💻',
    color: 'cyan'
  },
  F: {
    id: 'F',
    name: 'Kollaboration',
    module: 'Collaboration',
    range: 'LM26-LM31',
    icon: '👥',
    color: 'pink'
  }
} as const

/** Legacy-Kompatibilitaet fuer alte Kategorien */
export const LEARNING_METHOD_CATEGORIES = {
  erklaerend: {
    name: 'Erklaerende Methoden',
    range: 'LM00, LM01, LM02, LM03, LM06',
    icon: '📚',
    color: 'blue'
  },
  praxis: {
    name: 'Praxis/Uebung',
    range: 'LM08, LM12, LM13, LM14, LM15, LM17',
    icon: '🎯',
    color: 'green'
  },
  pruefung: {
    name: 'Pruefungsorientiert',
    range: 'LM18-LM25',
    icon: '📝',
    color: 'orange'
  }
} as const

/** Gueltige Content-LM Codes */
export const VALID_CONTENT_LM_CODES: readonly number[] = [0, 1, 2, 3, 6, 8, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25]

/** System-Feature Codes (fuer Referenz) */
export const SYSTEM_FEATURE_CODES: readonly number[] = [4, 5, 7, 9, 10, 11, 16, 26, 27, 28, 29, 30, 31]
