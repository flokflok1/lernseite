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

import type {
  BaseStats,
  GamificationStats,
  Quest,
  SkillNode
} from './gamification.types'

export type {
  BaseStats,
  GamificationStats,
  Quest,
  QuestDifficulty,
  QuestSourceType,
  SkillNode,
  GamificationState
} from './gamification.types'

import {
  STORAGE_KEY,
  createDefaultStats,
  createDefaultSkillTree,
  createDefaultQuests,
  generateQuestsFromCourses
} from './gamification.helpers'

// ============================================================================
// Store Definition
// ============================================================================

export const useGamificationStore = defineStore('gamification', () => {
  // ============================================================================
  // State
  // ============================================================================

  const stats = ref<GamificationStats>(createDefaultStats())
  const quests = ref<Quest[]>([])
  const skillTree = ref<SkillNode[]>(createDefaultSkillTree())

  // Track bonuses from skills
  const xpBonus = ref(0)
  const goldBonus = ref(0)

  // ============================================================================
  // Computed
  // ============================================================================

  const xpProgress = computed((): number => {
    return Math.min((stats.value.xp / stats.value.xpToNext) * 100, 100)
  })

  const activeQuests = computed((): Quest[] => {
    return quests.value.filter(q => !q.completed)
  })

  const completedQuests = computed((): Quest[] => {
    return quests.value.filter(q => q.completed)
  })

  const availableSkills = computed((): SkillNode[] => {
    return skillTree.value.filter(skill => {
      if (skill.unlocked) return false
      if (!skill.requires || skill.requires.length === 0) return true
      return skill.requires.every(reqId =>
        skillTree.value.find(s => s.id === reqId)?.unlocked
      )
    })
  })

  const unlockedSkills = computed((): SkillNode[] => {
    return skillTree.value.filter(skill => skill.unlocked)
  })

  const totalStats = computed((): number => {
    return stats.value.baseStats.strength +
           stats.value.baseStats.intelligence +
           stats.value.baseStats.stamina
  })

  const getCharacterClass = computed(() => {
    const { strength, intelligence, stamina } = stats.value.baseStats

    if (strength >= intelligence && strength >= stamina) {
      return { name: 'Code Warrior', icon: '⚔️' }
    }
    if (intelligence >= strength && intelligence >= stamina) {
      return { name: 'Logic Mage', icon: '🧙' }
    }
    return { name: 'Endurance Runner', icon: '🏃' }
  })

  // ============================================================================
  // Persistence
  // ============================================================================

  /**
   * Save state to localStorage
   */
  function saveState(): void {
    const state = {
      stats: stats.value,
      quests: quests.value,
      skillTree: skillTree.value,
      xpBonus: xpBonus.value,
      goldBonus: goldBonus.value
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  }

  // ============================================================================
  // Actions
  // ============================================================================

  /**
   * Load gamification state from API
   */
  async function loadFromProfile(data: {
    profile?: any
    courses?: any[]
    progress?: Record<string, number>
  }): Promise<void> {
    try {
      const { getMyGamificationData } = await import('@/application/services/api/panel-user')
      const apiData = await getMyGamificationData()

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
    }

    if (data.courses && data.courses.length > 0) {
      quests.value = generateQuestsFromCourses(data.courses, data.progress)
    }

    if (quests.value.length === 0) {
      quests.value = createDefaultQuests()
    }

    saveState()
  }

  /**
   * Apply a skill effect to bonuses or base stats
   */
  function applySkillEffect(effect: SkillNode['effect']): void {
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
   * Gain XP with bonus calculation
   */
  function gainXP(amount: number): { leveledUp: boolean; newLevel?: number } {
    const bonusAmount = Math.floor(amount * (1 + xpBonus.value))
    stats.value.xp += bonusAmount

    let leveledUp = false
    let newLevel = stats.value.level

    while (stats.value.xp >= stats.value.xpToNext) {
      stats.value.xp -= stats.value.xpToNext
      stats.value.level += 1
      stats.value.skillPoints += 1

      stats.value.baseStats.strength += 1
      stats.value.baseStats.intelligence += 1
      stats.value.baseStats.stamina += 1

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
  function gainGold(amount: number): number {
    const bonusAmount = Math.floor(amount * (1 + goldBonus.value))
    stats.value.gold += bonusAmount
    saveState()
    return bonusAmount
  }

  /**
   * Complete a quest
   */
  function completeQuest(questId: string): {
    success: boolean
    xpGained?: number
    goldGained?: number
    leveledUp?: boolean
    newLevel?: number
  } {
    const quest = quests.value.find(q => q.id === questId)

    if (!quest || quest.completed) {
      return { success: false }
    }

    quest.completed = true

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
  function unlockSkill(skillId: string): { success: boolean; message?: string } {
    const skill = skillTree.value.find(s => s.id === skillId)

    if (!skill) {
      return { success: false, message: 'Skill nicht gefunden' }
    }

    if (skill.unlocked) {
      return { success: false, message: 'Skill bereits freigeschaltet' }
    }

    if (skill.requires && skill.requires.length > 0) {
      const allRequirementsMet = skill.requires.every(reqId =>
        skillTree.value.find(s => s.id === reqId)?.unlocked
      )
      if (!allRequirementsMet) {
        return { success: false, message: 'Voraussetzungen nicht erfuellt' }
      }
    }

    if (stats.value.skillPoints < skill.cost) {
      return { success: false, message: 'Nicht genug Skillpunkte' }
    }

    stats.value.skillPoints -= skill.cost
    skill.unlocked = true

    if (skill.effect) {
      applySkillEffect(skill.effect)
    }

    saveState()
    return { success: true }
  }

  /**
   * Reset gamification state
   */
  function resetState(): void {
    stats.value = createDefaultStats()
    quests.value = []
    skillTree.value = createDefaultSkillTree()
    xpBonus.value = 0
    goldBonus.value = 0
    localStorage.removeItem(STORAGE_KEY)
  }

  /**
   * Add a custom quest
   */
  function addQuest(quest: Omit<Quest, 'id' | 'completed'>): void {
    const newQuest: Quest = {
      ...quest,
      id: `custom-${Date.now()}`,
      completed: false
    }
    quests.value.push(newQuest)
    saveState()
  }

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
