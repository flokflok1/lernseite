/**
 * LernsystemX - Gamification Store (Pinia)
 * Phase G1: RPG Dashboard Gamification System
 *
 * Manages:
 * - Player stats (level, XP, gold, skill points)
 * - Base stats (strength, intelligence, stamina)
 * - Quest system (from courses/chapters/lessons)
 * - Skill tree with unlockable nodes
 * - Level-up mechanics
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// ============================================================================
// Types
// ============================================================================

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

// ============================================================================
// Storage Key
// ============================================================================

const STORAGE_KEY = 'lsx_gamification_state'

// ============================================================================
// Default Skill Tree
// ============================================================================

const DEFAULT_SKILL_TREE: SkillNode[] = [
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

// ============================================================================
// Store Definition
// ============================================================================

export const useGamificationStore = defineStore('gamification', () => {
  // ============================================================================
  // State
  // ============================================================================

  const stats = ref<GamificationStats>({
    level: 1,
    xp: 0,
    xpToNext: 100,
    gold: 0,
    skillPoints: 0,
    baseStats: {
      strength: 0,  // Load from API instead of default
      intelligence: 0,  // Load from API instead of default
      stamina: 0  // Load from API instead of default
    }
  })

  const quests = ref<Quest[]>([])
  const skillTree = ref<SkillNode[]>([...DEFAULT_SKILL_TREE])

  // Track bonuses from skills
  const xpBonus = ref(0)
  const goldBonus = ref(0)

  // ============================================================================
  // Computed
  // ============================================================================

  const xpProgress = computed(() => {
    return Math.min((stats.value.xp / stats.value.xpToNext) * 100, 100)
  })

  const activeQuests = computed(() => {
    return quests.value.filter(q => !q.completed)
  })

  const completedQuests = computed(() => {
    return quests.value.filter(q => q.completed)
  })

  const availableSkills = computed(() => {
    return skillTree.value.filter(skill => {
      if (skill.unlocked) return false
      if (!skill.requires || skill.requires.length === 0) return true
      return skill.requires.every(reqId =>
        skillTree.value.find(s => s.id === reqId)?.unlocked
      )
    })
  })

  const unlockedSkills = computed(() => {
    return skillTree.value.filter(skill => skill.unlocked)
  })

  const totalStats = computed(() => {
    return stats.value.baseStats.strength +
           stats.value.baseStats.intelligence +
           stats.value.baseStats.stamina
  })

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Load gamification state from API
   */
  const loadFromProfile = async (data: {
    profile?: any
    courses?: any[]
    progress?: Record<string, number>
  }) => {
    try {
      // Load from API instead of localStorage
      const { getMyGamificationData } = await import('@/infrastructure/api/clients/system/gamification.api')
      const apiData = await getMyGamificationData()

      // Update stats from API
      stats.value = {
        level: apiData.level,
        xp: apiData.xp,
        xpToNext: apiData.xpToNext,
        gold: apiData.gold,
        skillPoints: apiData.skillPoints,
        baseStats: apiData.baseStats
      }

      console.log('[Gamification] Loaded from API:', stats.value)
    } catch (error) {
      console.error('[Gamification] Failed to load from API:', error)
      // Fallback: Keep default values (0, 0, 0)
    }

    // Generate quests from courses
    if (data.courses && data.courses.length > 0) {
      generateQuestsFromCourses(data.courses, data.progress)
    }

    // If no quests, add default starter quests
    if (quests.value.length === 0) {
      addDefaultQuests()
    }

    // Save state to localStorage for caching
    saveState()
  }

  /**
   * Generate quests from enrolled courses
   */
  const generateQuestsFromCourses = (
    courses: any[],
    progress?: Record<string, number>
  ) => {
    const newQuests: Quest[] = []

    courses.forEach((course, index) => {
      const courseProgress = progress?.[course.course_id] || 0
      const isCompleted = courseProgress >= 100

      // Quest difficulty based on index/complexity
      let difficulty: QuestDifficulty = 'easy'
      let xpReward = 50
      let goldReward = 10

      if (index >= 3) {
        difficulty = 'hard'
        xpReward = 150
        goldReward = 30
      } else if (index >= 1) {
        difficulty = 'medium'
        xpReward = 100
        goldReward = 20
      }

      newQuests.push({
        id: `course-${course.course_id}`,
        title: `Meistere: ${course.title || course.name || 'Unbekannter Kurs'}`,
        description: course.description?.substring(0, 100) || 'Schliesse diesen Kurs ab',
        xpReward,
        goldReward,
        difficulty,
        sourceType: 'course',
        sourceId: course.course_id,
        completed: isCompleted,
        icon: getDifficultyIcon(difficulty)
      })
    })

    quests.value = newQuests
  }

  /**
   * Add default starter quests
   */
  const addDefaultQuests = () => {
    quests.value = [
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

  /**
   * Get icon based on quest difficulty
   */
  const getDifficultyIcon = (difficulty: QuestDifficulty): string => {
    switch (difficulty) {
      case 'easy': return '🌱'
      case 'medium': return '⚡'
      case 'hard': return '🔥'
      default: return '📜'
    }
  }

  /**
   * Gain XP with bonus calculation
   */
  const gainXP = (amount: number): { leveledUp: boolean; newLevel?: number } => {
    const bonusAmount = Math.floor(amount * (1 + xpBonus.value))
    stats.value.xp += bonusAmount

    let leveledUp = false
    let newLevel = stats.value.level

    // Level up logic
    while (stats.value.xp >= stats.value.xpToNext) {
      stats.value.xp -= stats.value.xpToNext
      stats.value.level += 1
      stats.value.skillPoints += 1

      // Increase base stats on level up
      stats.value.baseStats.strength += 1
      stats.value.baseStats.intelligence += 1
      stats.value.baseStats.stamina += 1

      // Calculate new XP threshold (1.5x increase)
      stats.value.xpToNext = Math.floor(stats.value.xpToNext * 1.5)

      leveledUp = true
      newLevel = stats.value.level
    }

    saveState()
    return { leveledUp, newLevel: leveledUp ? newLevel : undefined }
  }

  /**
   * Gain gold with bonus calculation
   */
  const gainGold = (amount: number): number => {
    const bonusAmount = Math.floor(amount * (1 + goldBonus.value))
    stats.value.gold += bonusAmount
    saveState()
    return bonusAmount
  }

  /**
   * Complete a quest
   */
  const completeQuest = (questId: string): {
    success: boolean
    xpGained?: number
    goldGained?: number
    leveledUp?: boolean
    newLevel?: number
  } => {
    const quest = quests.value.find(q => q.id === questId)

    if (!quest || quest.completed) {
      return { success: false }
    }

    quest.completed = true

    // Award rewards
    const goldGained = gainGold(quest.goldReward)
    const { leveledUp, newLevel } = gainXP(quest.xpReward)

    saveState()

    return {
      success: true,
      xpGained: Math.floor(quest.xpReward * (1 + xpBonus.value)),
      goldGained,
      leveledUp,
      newLevel
    }
  }

  /**
   * Unlock a skill from the skill tree
   */
  const unlockSkill = (skillId: string): { success: boolean; message?: string } => {
    const skill = skillTree.value.find(s => s.id === skillId)

    if (!skill) {
      return { success: false, message: 'Skill nicht gefunden' }
    }

    if (skill.unlocked) {
      return { success: false, message: 'Skill bereits freigeschaltet' }
    }

    // Check prerequisites
    if (skill.requires && skill.requires.length > 0) {
      const allRequirementsMet = skill.requires.every(reqId =>
        skillTree.value.find(s => s.id === reqId)?.unlocked
      )
      if (!allRequirementsMet) {
        return { success: false, message: 'Voraussetzungen nicht erfuellt' }
      }
    }

    // Check skill points
    if (stats.value.skillPoints < skill.cost) {
      return { success: false, message: 'Nicht genug Skillpunkte' }
    }

    // Deduct skill points and unlock
    stats.value.skillPoints -= skill.cost
    skill.unlocked = true

    // Apply skill effect
    if (skill.effect) {
      applySkillEffect(skill.effect)
    }

    saveState()
    return { success: true }
  }

  /**
   * Apply skill effect
   */
  const applySkillEffect = (effect: SkillNode['effect']) => {
    if (!effect) return

    switch (effect.type) {
      case 'xp_bonus':
        xpBonus.value += effect.value
        break
      case 'gold_bonus':
        goldBonus.value += effect.value
        break
      case 'stat_bonus':
        if (effect.stat) {
          stats.value.baseStats[effect.stat] += effect.value
        }
        break
    }
  }

  /**
   * Save state to localStorage
   */
  const saveState = () => {
    const state = {
      stats: stats.value,
      quests: quests.value,
      skillTree: skillTree.value,
      xpBonus: xpBonus.value,
      goldBonus: goldBonus.value
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  }

  /**
   * Reset gamification state
   */
  const resetState = () => {
    stats.value = {
      level: 1,
      xp: 0,
      xpToNext: 100,
      gold: 0,
      skillPoints: 0,
      baseStats: {
        strength: 0,  // Start with 0, will be loaded from API
        intelligence: 0,
        stamina: 0
      }
    }
    quests.value = []
    skillTree.value = [...DEFAULT_SKILL_TREE]
    xpBonus.value = 0
    goldBonus.value = 0
    localStorage.removeItem(STORAGE_KEY)
  }

  /**
   * Add a custom quest
   */
  const addQuest = (quest: Omit<Quest, 'id' | 'completed'>) => {
    const newQuest: Quest = {
      ...quest,
      id: `custom-${Date.now()}`,
      completed: false
    }
    quests.value.push(newQuest)
    saveState()
  }

  /**
   * Get character class based on stats
   */
  const getCharacterClass = computed(() => {
    const { strength, intelligence, stamina } = stats.value.baseStats

    if (strength >= intelligence && strength >= stamina) {
      return { name: 'Code Warrior', icon: '⚔️' }
    } else if (intelligence >= strength && intelligence >= stamina) {
      return { name: 'Logic Mage', icon: '🧙' }
    } else {
      return { name: 'Endurance Runner', icon: '🏃' }
    }
  })

  // ============================================================================
  // Return
  // ============================================================================

  return {
    // State
    stats,
    quests,
    skillTree,
    xpBonus,
    goldBonus,

    // Computed
    xpProgress,
    activeQuests,
    completedQuests,
    availableSkills,
    unlockedSkills,
    totalStats,
    getCharacterClass,

    // Actions
    loadFromProfile,
    gainXP,
    gainGold,
    completeQuest,
    unlockSkill,
    resetState,
    addQuest,
    saveState
  }
})
