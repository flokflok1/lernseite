/**
 * LernsystemX - Gamification API Client
 *
 * Provides methods to interact with gamification endpoints:
 * - Get user gamification data (XP, Level, Skills, Achievements)
 * - Get stats, skills, achievements separately
 */

import http from './http'

export interface BaseStats {
  strength: number
  intelligence: number
  stamina: number
}

export interface GamificationData {
  level: number
  xp: number
  xpToNext: number
  gold: number
  skillPoints: number
  baseStats: BaseStats
  skills: any[]
  achievements: any[]
}

export interface GamificationApiResponse {
  success: boolean
  data?: GamificationData
  error?: string
  details?: string
}

/**
 * Get complete gamification data for current user
 */
export const getMyGamificationData = async (): Promise<GamificationData> => {
  const response = await http.get<GamificationApiResponse>('/gamification/me')

  if (!response.data.success || !response.data.data) {
    throw new Error(response.data.error || 'Failed to load gamification data')
  }

  return response.data.data
}

/**
 * Get basic stats (XP, Level) only
 */
export const getMyStats = async () => {
  const response = await http.get('/gamification/stats')
  return response.data
}

/**
 * Get skills (Strength, Intelligence, Stamina)
 */
export const getMySkills = async () => {
  const response = await http.get('/gamification/skills')
  return response.data
}

/**
 * Get achievements
 */
export const getMyAchievements = async () => {
  const response = await http.get('/gamification/achievements')
  return response.data
}
