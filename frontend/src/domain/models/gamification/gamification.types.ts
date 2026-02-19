/**
 * LernsystemX - Gamification Types
 * Type definitions for the RPG Dashboard Gamification System.
 */

export interface BaseStats {
  strength: number    // Staerke (Code-Verstaendnis)
  intelligence: number // Intelligenz (Logik)
  stamina: number     // Ausdauer (Fokus)
}

export interface GamificationStats {
  level: number
  xp: number
  xpToNext: number
  gold: number
  skillPoints: number
  baseStats: BaseStats
}

export type QuestDifficulty = 'easy' | 'medium' | 'hard'
export type QuestSourceType = 'course' | 'module' | 'lesson' | 'custom'

export interface Quest {
  id: string
  title: string
  description: string
  xpReward: number
  goldReward: number
  difficulty: QuestDifficulty
  sourceType: QuestSourceType
  sourceId?: string
  completed: boolean
  icon?: string
}

export interface SkillNode {
  id: string
  name: string
  description: string
  icon: string
  requires?: string[]
  cost: number
  unlocked: boolean
  effect?: {
    type: 'xp_bonus' | 'gold_bonus' | 'stat_bonus'
    value: number
    stat?: keyof BaseStats
  }
}

export interface GamificationState {
  stats: GamificationStats
  quests: Quest[]
  skillTree: SkillNode[]
}
