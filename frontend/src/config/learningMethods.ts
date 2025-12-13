/**
 * Lernmethoden-Definitionen
 *
 * 31 aktive Lernmethoden in 6 Gruppen:
 * - A: Erklaerend (LM00-LM03, LM06) - 5 Methoden
 * - B: Praxis (LM08, LM12-LM15, LM17) - 6 Methoden
 * - C: Pruefung (LM18-LM25) - 8 Methoden
 * - D: Pro (LM04) - 1 Methode
 * - E: IT (LM09-LM11, LM16) - 4 Methoden
 * - F: Kollaborativ (LM26-LM32) - 7 Methoden
 *
 * Deaktiviert (jetzt CourseFeatures/TutorAgent):
 * - LM05: Mindmap-Generator -> course_features.auto_mindmap_enabled
 * - LM07: NPC-Tutor -> TutorAgent System
 *
 * Diese Konfiguration MUSS mit dem Backend uebereinstimmen!
 * Backend-Quelle: /api/v1/admin/learning-method-types
 */

export type LearningMethodGroup = 'A' | 'B' | 'C' | 'D' | 'E' | 'F'

export interface LearningMethod {
  id: string          // "00"-"32" (OHNE "LM")
  code: number        // 0-32
  name: string        // Deutscher Name
  group: LearningMethodGroup
  category: 'erklaerend' | 'praxis' | 'pruefung' | 'pro' | 'it' | 'kollaborativ'
  description: string
  icon: string        // Emoji
  promptKey: string   // Backend prompt_key
  active: boolean     // Aktiv oder deaktiviert
}

export const LEARNING_METHODS: LearningMethod[] = [
  // ============================================================================
  // Gruppe A: Erklaerend (LM00-LM03, LM06) - 5 aktive Methoden
  // ============================================================================
  {
    id: '00',
    code: 0,
    name: 'Tiefgehende Erklaerung',
    group: 'A',
    category: 'erklaerend',
    description: 'KI-generierte Erklaerung mit Beispielen & Analogien',
    icon: '🔍',
    promptKey: 'deep_explanation',
    active: true
  },
  {
    id: '01',
    code: 1,
    name: 'Schritt-fuer-Schritt',
    group: 'A',
    category: 'erklaerend',
    description: 'Sequenzielle Anleitung in nummerierten Schritten',
    icon: '📋',
    promptKey: 'step_by_step',
    active: true
  },
  {
    id: '02',
    code: 2,
    name: 'Interaktive Theorie',
    group: 'A',
    category: 'erklaerend',
    description: 'Theoriebloecke mit eingebetteten Kontrollfragen',
    icon: '📖',
    promptKey: 'interactive_theory',
    active: true
  },
  {
    id: '03',
    code: 3,
    name: 'Diagramm/Visualisierung',
    group: 'A',
    category: 'erklaerend',
    description: 'Visuelle Modelle (Netzwerk, OSI, ER, Flows)',
    icon: '📊',
    promptKey: 'visualization',
    active: true
  },
  // LM05 Mindmap-Generator -> deaktiviert (jetzt CourseFeature)
  {
    id: '06',
    code: 6,
    name: 'Beispiel-Szenario',
    group: 'A',
    category: 'erklaerend',
    description: 'Realitaetsnahe Case-Erklaerung eines Konzepts',
    icon: '💼',
    promptKey: 'scenario_explanation',
    active: true
  },
  // LM07 NPC-Tutor -> deaktiviert (jetzt TutorAgent)

  // ============================================================================
  // Gruppe B: Praxis (LM08, LM12-LM15, LM17) - 6 aktive Methoden
  // ============================================================================
  {
    id: '08',
    code: 8,
    name: 'Whiteboard-Aufgabe',
    group: 'B',
    category: 'praxis',
    description: 'Lernende zeichnen/verbinden Topologien, Skizzen',
    icon: '🎨',
    promptKey: 'whiteboard',
    active: true
  },
  // LM09-11, LM16 sind in Gruppe E (IT)
  {
    id: '12',
    code: 12,
    name: 'Mathe-Interaktiv',
    group: 'B',
    category: 'praxis',
    description: 'Rechenaufgaben mit Schritt-fuer-Schritt-Erklaerung',
    icon: '🔢',
    promptKey: 'math_interactive',
    active: true
  },
  {
    id: '13',
    code: 13,
    name: 'Flashcards',
    group: 'B',
    category: 'praxis',
    description: 'Karteikarten mit Spaced-Repetition',
    icon: '🗂️',
    promptKey: 'flashcards',
    active: true
  },
  {
    id: '14',
    code: 14,
    name: 'Drag & Drop',
    group: 'B',
    category: 'praxis',
    description: 'Zuordnungs-/Matching-Aufgaben',
    icon: '🎯',
    promptKey: 'drag_drop',
    active: true
  },
  {
    id: '15',
    code: 15,
    name: 'Lueckentext',
    group: 'B',
    category: 'praxis',
    description: 'Fill-in-the-blanks in Texten/Configs',
    icon: '✍️',
    promptKey: 'fill_blanks',
    active: true
  },
  {
    id: '17',
    code: 17,
    name: 'Hands-on Lab',
    group: 'B',
    category: 'praxis',
    description: 'Virtuelle Umgebung (Terminal/IDE) mit Aufgabe',
    icon: '🧪',
    promptKey: 'hands_on_lab',
    active: true
  },

  // ============================================================================
  // Gruppe C: Pruefungsorientiert (LM18-LM25) - 8 aktive Methoden
  // ============================================================================
  {
    id: '18',
    code: 18,
    name: 'Freitext-Langantwort',
    group: 'C',
    category: 'pruefung',
    description: 'Lange Antworten, KI bewertet mit Rubric',
    icon: '📝',
    promptKey: 'long_answer',
    active: true
  },
  {
    id: '19',
    code: 19,
    name: 'IHK-Stil Aufgaben',
    group: 'C',
    category: 'pruefung',
    description: 'Pruefungsnahe MC/Lueckentext/Szenario',
    icon: '🏛️',
    promptKey: 'ihk_style',
    active: true
  },
  {
    id: '20',
    code: 20,
    name: 'Multi-Step Praxispruefung',
    group: 'C',
    category: 'pruefung',
    description: 'Mehrstufige Pruefungsketten',
    icon: '📋',
    promptKey: 'multi_step_exam',
    active: true
  },
  {
    id: '21',
    code: 21,
    name: 'Zeitlimit-Training',
    group: 'C',
    category: 'pruefung',
    description: 'Aufgaben unter Zeitdruck (Countdown)',
    icon: '⏱️',
    promptKey: 'time_limit',
    active: true
  },
  {
    id: '22',
    code: 22,
    name: 'Pruefungs-Quiz',
    group: 'C',
    category: 'pruefung',
    description: 'Quiz mit sofortigem Feedback',
    icon: '☑️',
    promptKey: 'exam_quiz',
    active: true
  },
  {
    id: '23',
    code: 23,
    name: 'Verstaendnis-Checks',
    group: 'C',
    category: 'pruefung',
    description: 'Single-Item-Checks nach Lerneinheit',
    icon: '✅',
    promptKey: 'comprehension_check',
    active: true
  },
  {
    id: '24',
    code: 24,
    name: 'Muendliche Erklaerung',
    group: 'C',
    category: 'pruefung',
    description: 'User erklaert muendlich, KI bewertet',
    icon: '🎤',
    promptKey: 'oral_explanation',
    active: true
  },
  {
    id: '25',
    code: 25,
    name: 'Kapitel-Endpruefung',
    group: 'C',
    category: 'pruefung',
    description: 'Groessere Pruefung am Kapitelende',
    icon: '🎓',
    promptKey: 'chapter_exam',
    active: true
  },

  // ============================================================================
  // Gruppe D: Pro (LM04) - 1 aktive Methode
  // ============================================================================
  {
    id: '04',
    code: 4,
    name: 'Sokratischer Dialog',
    group: 'D',
    category: 'pro',
    description: 'KI fragt, User leitet Konzept selbst her',
    icon: '💬',
    promptKey: 'socratic_dialog',
    active: true
  },

  // ============================================================================
  // Gruppe E: IT-Spezifisch (LM09-LM11, LM16) - 4 aktive Methoden
  // ============================================================================
  {
    id: '09',
    code: 9,
    name: 'Code/IT-Config Sandbox',
    group: 'E',
    category: 'it',
    description: 'Code-/Config-Editor mit Tests & Output',
    icon: '💻',
    promptKey: 'code_sandbox',
    active: true
  },
  {
    id: '10',
    code: 10,
    name: 'Netzwerk-Simulation',
    group: 'E',
    category: 'it',
    description: 'Simulierte Netzumgebung (Router, Switch, Ping)',
    icon: '🌐',
    promptKey: 'network_sim',
    active: true
  },
  {
    id: '11',
    code: 11,
    name: 'IT-Szenario loesen',
    group: 'E',
    category: 'it',
    description: 'Troubleshooting mit Logs/Configs',
    icon: '🔧',
    promptKey: 'it_scenario',
    active: true
  },
  {
    id: '16',
    code: 16,
    name: 'Fehleranalyse',
    group: 'E',
    category: 'it',
    description: 'Defekter Code/Config, Fehler finden & erklaeren',
    icon: '🔍',
    promptKey: 'error_analysis',
    active: true
  },

  // ============================================================================
  // Gruppe F: Kollaborativ (LM26-LM32) - 7 aktive Methoden
  // ============================================================================
  {
    id: '26',
    code: 26,
    name: 'Peer Instruction',
    group: 'F',
    category: 'kollaborativ',
    description: 'Think-Pair-Share mit Erstantwort und Diskussion',
    icon: '👥',
    promptKey: 'peer_instruction',
    active: true
  },
  {
    id: '27',
    code: 27,
    name: 'Team-Case / Gruppenfallarbeit',
    group: 'F',
    category: 'kollaborativ',
    description: 'Teams loesen Fall mit Rollen',
    icon: '🤝',
    promptKey: 'team_case',
    active: true
  },
  {
    id: '28',
    code: 28,
    name: 'Peer Review (strukturiert)',
    group: 'F',
    category: 'kollaborativ',
    description: 'Rubric-basiertes Feedback zu Arbeiten anderer',
    icon: '📋',
    promptKey: 'peer_review',
    active: true
  },
  {
    id: '29',
    code: 29,
    name: 'Lerntagebuch / Learning Journal',
    group: 'F',
    category: 'kollaborativ',
    description: 'Regelmaessige Reflexionseintraege',
    icon: '📔',
    promptKey: 'learning_journal',
    active: true
  },
  {
    id: '30',
    code: 30,
    name: 'Projekt-Portfolio',
    group: 'F',
    category: 'kollaborativ',
    description: 'Artefakte-Sammlung mit Meta-Kommentar',
    icon: '📁',
    promptKey: 'portfolio',
    active: true
  },
  {
    id: '31',
    code: 31,
    name: 'Projektbasiertes Lernen',
    group: 'F',
    category: 'kollaborativ',
    description: 'Mehrwoechiges IT-Projekt',
    icon: '🏗️',
    promptKey: 'project_based',
    active: true
  },
  {
    id: '32',
    code: 32,
    name: 'Inverted Classroom',
    group: 'F',
    category: 'kollaborativ',
    description: 'Async Theorie + sync Praxis',
    icon: '🔄',
    promptKey: 'inverted_classroom',
    active: true
  }
]

// Aktive Methoden (fuer Katalog etc.)
export const ACTIVE_LEARNING_METHODS = LEARNING_METHODS.filter(m => m.active)

export const LEARNING_METHOD_GROUPS = {
  A: {
    id: 'A' as LearningMethodGroup,
    name: 'Erklaerend',
    range: 'LM00-LM03, LM06',
    icon: '📚',
    color: 'blue',
    count: 5
  },
  B: {
    id: 'B' as LearningMethodGroup,
    name: 'Praxis',
    range: 'LM08, LM12-LM15, LM17',
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
  },
  D: {
    id: 'D' as LearningMethodGroup,
    name: 'Pro',
    range: 'LM04',
    icon: '💬',
    color: 'purple',
    count: 1
  },
  E: {
    id: 'E' as LearningMethodGroup,
    name: 'IT',
    range: 'LM09-LM11, LM16',
    icon: '💻',
    color: 'cyan',
    count: 4
  },
  F: {
    id: 'F' as LearningMethodGroup,
    name: 'Kollaborativ',
    range: 'LM26-LM32',
    icon: '👥',
    color: 'pink',
    count: 7
  }
}

// Legacy-Kompatibilitaet fuer alte Kategorien
export const LEARNING_METHOD_CATEGORIES = {
  erklaerend: {
    name: 'Erklaerende Methoden',
    range: 'LM00-LM03, LM06',
    icon: '📚',
    color: 'blue'
  },
  praxis: {
    name: 'Praxis/Uebung',
    range: 'LM08, LM12-LM15, LM17',
    icon: '🎯',
    color: 'green'
  },
  pruefung: {
    name: 'Pruefungsorientiert',
    range: 'LM18-LM25',
    icon: '📝',
    color: 'orange'
  },
  pro: {
    name: 'Pro',
    range: 'LM04',
    icon: '💬',
    color: 'purple'
  },
  it: {
    name: 'IT-Spezifisch',
    range: 'LM09-LM11, LM16',
    icon: '💻',
    color: 'cyan'
  },
  kollaborativ: {
    name: 'Kollaborativ',
    range: 'LM26-LM32',
    icon: '👥',
    color: 'pink'
  }
}

export type LearningMethodCategory = keyof typeof LEARNING_METHOD_CATEGORIES

// Helper Funktionen
export function getLearningMethodsByCategory(category: LearningMethodCategory): LearningMethod[] {
  return ACTIVE_LEARNING_METHODS.filter(m => m.category === category)
}

export function getLearningMethodsByGroup(group: LearningMethodGroup): LearningMethod[] {
  return ACTIVE_LEARNING_METHODS.filter(m => m.group === group)
}

export function getLearningMethodByCode(code: number): LearningMethod | undefined {
  return LEARNING_METHODS.find(m => m.code === code)
}

export function getActiveLearningMethodByCode(code: number): LearningMethod | undefined {
  return ACTIVE_LEARNING_METHODS.find(m => m.code === code)
}

export function getLearningMethodById(id: string): LearningMethod | undefined {
  return LEARNING_METHODS.find(m => m.id === id)
}

export function getLearningMethodByPromptKey(promptKey: string): LearningMethod | undefined {
  return LEARNING_METHODS.find(m => m.promptKey === promptKey)
}

// Tier-Berechnung basierend auf Gruppe
export function getTierFromGroup(group: LearningMethodGroup): 'basic' | 'premium' | 'pro' {
  if (group === 'A' || group === 'B') return 'basic'
  if (group === 'C' || group === 'E') return 'premium'
  return 'pro' // D, F
}

export function getTierFromCode(code: number): 'basic' | 'premium' | 'pro' {
  const method = getLearningMethodByCode(code)
  if (!method) return 'basic'
  return getTierFromGroup(method.group)
}

// Fuer Legacy-Kompatibilitaet
export function getTierFromCategory(category: LearningMethodCategory): 'basic' | 'premium' | 'pro' {
  if (category === 'erklaerend' || category === 'praxis') return 'basic'
  if (category === 'pruefung' || category === 'it') return 'premium'
  return 'pro' // pro, kollaborativ
}
