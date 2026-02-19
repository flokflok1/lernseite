/**
 * LernsystemX - Gamification Helpers
 * Default data, quest generation, and utility functions
 * for the Gamification Store.
 */

import type {
  GamificationStats,
  Quest,
  QuestDifficulty,
  SkillNode
} from './gamification.types'

// ============================================================================
// Constants
// ============================================================================

export const STORAGE_KEY = 'lsx_gamification_state'

// ============================================================================
// Default Stats
// ============================================================================

export function createDefaultStats(): GamificationStats {
  return {
    level: 1,
    xp: 0,
    xpToNext: 100,
    gold: 0,
    skillPoints: 0,
    baseStats: {
      strength: 0,
      intelligence: 0,
      stamina: 0
    }
  }
}

// ============================================================================
// Default Skill Tree
// ============================================================================

export function createDefaultSkillTree(): SkillNode[] {
  return [
    {
      id: 'focus',
      name: 'Hyper Focus',
      description: '+10% XP bei allen Quests',
      icon: '🎯',
      cost: 1,
      unlocked: false,
      effect: { type: 'xp_bonus', value: 0.1 }
    },
    {
      id: 'golddigger',
      name: 'Goldgraeber',
      description: '+20% Gold bei allen Quests',
      icon: '💰',
      cost: 1,
      unlocked: false,
      effect: { type: 'gold_bonus', value: 0.2 }
    },
    {
      id: 'logic',
      name: 'Logik-Meister',
      description: '+2 Intelligenz permanent',
      icon: '🧠',
      cost: 2,
      unlocked: false,
      requires: ['focus'],
      effect: { type: 'stat_bonus', value: 2, stat: 'intelligence' }
    },
    {
      id: 'endurance',
      name: 'Ausdauer-Training',
      description: '+2 Ausdauer permanent',
      icon: '💪',
      cost: 2,
      unlocked: false,
      requires: ['focus'],
      effect: { type: 'stat_bonus', value: 2, stat: 'stamina' }
    },
    {
      id: 'codemaster',
      name: 'Code-Meister',
      description: '+3 Staerke permanent',
      icon: '⚔️',
      cost: 3,
      unlocked: false,
      requires: ['logic', 'endurance'],
      effect: { type: 'stat_bonus', value: 3, stat: 'strength' }
    }
  ]
}

// ============================================================================
// Default Starter Quests
// ============================================================================

export function createDefaultQuests(): Quest[] {
  return [
    {
      id: 'starter-1',
      title: 'Erste Schritte',
      description: 'Erkunde das Dashboard und mache dich mit dem System vertraut',
      xpReward: 25,
      goldReward: 5,
      difficulty: 'easy',
      sourceType: 'custom',
      completed: false,
      icon: '🌟'
    },
    {
      id: 'starter-2',
      title: 'Profil vervollstaendigen',
      description: 'Fuege ein Profilbild hinzu und fuelle deine Informationen aus',
      xpReward: 50,
      goldReward: 10,
      difficulty: 'easy',
      sourceType: 'custom',
      completed: false,
      icon: '👤'
    },
    {
      id: 'starter-3',
      title: 'Erster Kurs',
      description: 'Schreibe dich in deinen ersten Kurs ein',
      xpReward: 75,
      goldReward: 15,
      difficulty: 'medium',
      sourceType: 'custom',
      completed: false,
      icon: '📚'
    }
  ]
}

// ============================================================================
// Quest Generation
// ============================================================================

/**
 * Get icon based on quest difficulty
 */
export function getDifficultyIcon(difficulty: QuestDifficulty): string {
  switch (difficulty) {
    case 'easy': return '🌱'
    case 'medium': return '⚡'
    case 'hard': return '🔥'
    default: return '📜'
  }
}

/**
 * Determine quest difficulty and rewards based on course index
 */
function getQuestParams(index: number): {
  difficulty: QuestDifficulty
  xpReward: number
  goldReward: number
} {
  if (index >= 3) {
    return { difficulty: 'hard', xpReward: 150, goldReward: 30 }
  }
  if (index >= 1) {
    return { difficulty: 'medium', xpReward: 100, goldReward: 20 }
  }
  return { difficulty: 'easy', xpReward: 50, goldReward: 10 }
}

/**
 * Generate quests from enrolled courses
 */
export function generateQuestsFromCourses(
  courses: any[],
  progress?: Record<string, number>
): Quest[] {
  return courses.map((course, index) => {
    const courseProgress = progress?.[course.course_id] || 0
    const isCompleted = courseProgress >= 100
    const { difficulty, xpReward, goldReward } = getQuestParams(index)

    return {
      id: `course-${course.course_id}`,
      title: `Meistere: ${course.title || course.name || 'Unbekannter Kurs'}`,
      description: course.description?.substring(0, 100) || 'Schliesse diesen Kurs ab',
      xpReward,
      goldReward,
      difficulty,
      sourceType: 'course' as const,
      sourceId: course.course_id,
      completed: isCompleted,
      icon: getDifficultyIcon(difficulty)
    }
  })
}
