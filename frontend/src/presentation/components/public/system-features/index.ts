// System Features Domain Components
// 25 System-Features organized by 10 DB categories
//
// These are infrastructure-level features (NOT content learning methods).
// Content LMs live in ../learning/methods/

// Interactive Tools (1 feature: whiteboard_engine)
export * from './interactive'

// Exam & Assessment (3 features: ihk_exam_system, practical_exam_engine, chapter_completion_system)
export * from './exam'

// Math Toolkit (4 features - implemented)
export * from './math'

// Gamification (3 features: adaptive_difficulty, xp_quest_system, daily_recall)
export * from './gamification'

// Collaboration (7 features: peer_instruction, team_case, peer_review, learning_journal, project_portfolio, project_based_learning, inverted_classroom)
export * from './collaboration'

// IT Environments (4 features: it_sandbox, code_sandbox, network_simulation, terminal_access)
export * from './it_environments'

// Meta Features (1 feature: timer_wrapper)
export * from './meta'

// Visualization (1 feature: mindmap_generator)
export * from './visualization'

// Learning Paths (1 feature: learning_path_generator)
export * from './learning_paths'

// Tutor & Coaching (3 features: npc_tutor, socratic_dialog, comprehension_checker)
export * from './tutor'
