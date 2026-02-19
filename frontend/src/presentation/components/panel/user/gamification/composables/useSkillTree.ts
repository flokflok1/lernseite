/**
 * useSkillTree - Skill tree interaction logic
 *
 * Manages skill node states, unlock checks, and requirement resolution
 * for the RPG skill tree component.
 */

import { ref, computed } from 'vue'
import { useGamificationStore } from '@/application/stores/modules/system/gamification.store'
import type { SkillNode } from '@/application/stores/modules/system/gamification.store'

interface UseSkillTreeReturn {
  selectedSkill: ReturnType<typeof ref<SkillNode | null>>
  skillTree: ReturnType<typeof computed<SkillNode[]>>
  skillPoints: ReturnType<typeof computed<number>>
  isSkillUnlocked: (skillId: string) => boolean
  isSkillAvailable: (skillId: string) => boolean
  getSkillCost: (skillId: string) => number
  getNodeClass: (skillId: string) => Record<string, boolean>
  handleSkillClick: (skillId: string) => void
  canUnlock: (skillId: string) => boolean
  getLockedReason: (skillId: string) => string
  getRequirementNames: (requireIds: string[]) => string
  handleUnlock: (skillId: string) => void
}

export function useSkillTree(): UseSkillTreeReturn {
  const gamificationStore = useGamificationStore()

  const selectedSkill = ref<SkillNode | null>(null)

  const skillTree = computed(() => gamificationStore.skillTree)
  const skillPoints = computed(() => gamificationStore.stats.skillPoints)
  const availableSkills = computed(() => gamificationStore.availableSkills)

  function isSkillUnlocked(skillId: string): boolean {
    const skill = skillTree.value.find(s => s.id === skillId)
    return skill?.unlocked || false
  }

  function isSkillAvailable(skillId: string): boolean {
    return availableSkills.value.some(s => s.id === skillId)
  }

  function getSkillCost(skillId: string): number {
    const skill = skillTree.value.find(s => s.id === skillId)
    return skill?.cost || 0
  }

  function getNodeClass(skillId: string): Record<string, boolean> {
    const skill = skillTree.value.find(s => s.id === skillId)
    if (!skill) return { locked: true }

    return {
      unlocked: skill.unlocked,
      available: !skill.unlocked && isSkillAvailable(skillId),
      locked: !skill.unlocked && !isSkillAvailable(skillId),
      selected: selectedSkill.value?.id === skillId
    }
  }

  function handleSkillClick(skillId: string): void {
    const skill = skillTree.value.find(s => s.id === skillId)
    if (skill) {
      selectedSkill.value = selectedSkill.value?.id === skillId ? null : skill
    }
  }

  function canUnlock(skillId: string): boolean {
    const skill = skillTree.value.find(s => s.id === skillId)
    if (!skill || skill.unlocked) return false

    if (skillPoints.value < skill.cost) return false

    if (skill.requires && skill.requires.length > 0) {
      return skill.requires.every(reqId => isSkillUnlocked(reqId))
    }

    return true
  }

  function getRequirementNames(requireIds: string[]): string {
    return requireIds
      .map(id => skillTree.value.find(s => s.id === id)?.name || id)
      .join(', ')
  }

  function getLockedReason(skillId: string): string {
    const skill = skillTree.value.find(s => s.id === skillId)
    if (!skill) return 'Skill nicht gefunden'

    if (skillPoints.value < skill.cost) {
      return `Benoetigt ${skill.cost} Skillpunkte (${skillPoints.value} vorhanden)`
    }

    if (skill.requires && skill.requires.length > 0) {
      const missing = skill.requires.filter(reqId => !isSkillUnlocked(reqId))
      if (missing.length > 0) {
        return `Benoetigt: ${getRequirementNames(missing)}`
      }
    }

    return 'Nicht verfuegbar'
  }

  function handleUnlock(skillId: string): void {
    const result = gamificationStore.unlockSkill(skillId)

    if (result.success) {
      const skill = skillTree.value.find(s => s.id === skillId)
      if (skill) {
        selectedSkill.value = { ...skill }
      }
    }
  }

  return {
    selectedSkill,
    skillTree,
    skillPoints,
    isSkillUnlocked,
    isSkillAvailable,
    getSkillCost,
    getNodeClass,
    handleSkillClick,
    canUnlock,
    getLockedReason,
    getRequirementNames,
    handleUnlock
  }
}
