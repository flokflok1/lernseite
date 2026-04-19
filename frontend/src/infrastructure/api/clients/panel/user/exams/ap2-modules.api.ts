/**
 * AP2 Module API — Diagramm-Module mit Mastery-Loop.
 *
 * Endpoints unter /api/v1/user/exam-trainer/ap2/modules/*
 */

import http from '@/infrastructure/api/http'

const BASE = '/user/exam-trainer/ap2/modules'

export type ModuleStatus =
  | 'locked'
  | 'available'
  | 'learning'
  | 'pending_recall'
  | 'mastered'
  | 'review_failed'

export interface ModuleProgress {
  status: ModuleStatus
  streak_count: number
  total_attempts: number
  passed_attempts: number
  cooldown_until: string | null
  same_day_recall_due_at: string | null
  mastered_at: string | null
  spotcheck_stage: number
  next_spotcheck_at: string | null
}

export interface ItemStats {
  total: number
  mastered: number
  in_progress: number
  recovery: number
  total_attempts: number
  stuetzrad_uses: number
}

export interface ModuleCard {
  module_id: string
  slug: string
  name_de: string
  description: string | null
  estimated_min: number
  difficulty: number
  sort_order: number
  prerequisite_slugs: string[]
  progress: ModuleProgress | null
  item_stats?: ItemStats
}

export interface ItemSkillState {
  kopf_serie_count: number
  fail_count: number
  effective_target: number | null
  total_attempts: number
  stuetzrad_uses: number
  is_mastered: boolean
  mastered_at: string | null
  snoozed_until: string | null
  last_attempt_at: string | null
  last_score_pct: number | null
  is_in_recovery: boolean
  should_suggest_stuetzrad: boolean
  should_suggest_pause: boolean
}

export interface ModuleItem {
  item_id: string
  item_type: 'blurt' | 'cued' | 'application'
  prompt: string
  points: number
  difficulty: number
  estimated_time_sec: number
  calculator_hint: CalculatorHint | null
  sub_area?: string | null
  tags?: string[]
}

export interface CalculatorHintStep {
  label: string
  keys?: string          // "MODE 2" oder "SHIFT + log"
  display?: string       // Beispiel-Display-Output
  note?: string
}

export interface CalculatorHint {
  model?: string         // z.B. 'Casio FX-991DE X'
  mode?: string          // z.B. 'COMP (MODE 1)'
  summary?: string
  steps?: CalculatorHintStep[]
  formula?: string       // LaTeX oder Plain
  example?: string
}

export interface SubAreaStat {
  sub_area: string
  total: number
  mastered: number
  in_progress: number
  recovery: number
  fresh: number
  avg_score_pct: number
  meta?: {
    module_id: string
    sub_area: string
    label_de: string
    label_en?: string | null
    sort_order: number
    icon?: string | null
    color?: string | null
    description?: string | null
  } | null
}

export interface ModuleStartResponse {
  module: ModuleCard
  theory_markdown: string | null
  first_item: ModuleItem | null
}

export interface ModuleSubmitResponse {
  pct: number
  passed: boolean
  points_earned: number
  stuetzrad_used: boolean
  model_answer: string | null
  skill: {
    kopf_serie_count: number
    effective_target: number
    fail_count: number
    stuetzrad_uses: number
    is_mastered: boolean
    should_suggest_stuetzrad: boolean
    should_suggest_pause: boolean
  }
  feedback: {
    summary: string
    correct_aspects: string[]
    missing_aspects: string[]
    partial_aspects: string[]
    incorrect_aspects: string[]
    suggestions: string[]
  }
  progress: ModuleProgress
  next_item: ModuleItem | null
}

export interface ModuleDetailResponse {
  module: ModuleCard
  theory_markdown: string | null
  item_stats: ItemStats
  sub_areas: SubAreaStat[]
  items: Array<ModuleItem & { skill: ItemSkillState }>
}

export type RecoveryMode = 'plus_one' | 'plus_two' | 'multiply_1_5'
export type StuetzradDefault = 'off' | 'per_item' | 'first_two_on'
export type MasteryStrictness = 'express' | 'standard' | 'strict'

export interface UserPreferences {
  base_target: number
  max_target: number
  recovery_mode: RecoveryMode
  stuetzrad_default: StuetzradDefault
  mastery_strictness: MasteryStrictness
}

export interface PreferencesResponse {
  preferences: UserPreferences
  meta: {
    recovery_modes: RecoveryMode[]
    stuetzrad_defaults: StuetzradDefault[]
    mastery_strictness_levels: MasteryStrictness[]
    abs_min_target: number
    abs_max_target: number
  }
}

export async function listModules(): Promise<ModuleCard[]> {
  const res = await http.get<{ modules: ModuleCard[] }>(BASE)
  return res.data.modules
}

export async function startModule(moduleId: string): Promise<ModuleStartResponse> {
  const res = await http.post<ModuleStartResponse>(`${BASE}/${moduleId}/start`)
  return res.data
}

export async function submitModuleAnswer(
  moduleId: string,
  itemId: string,
  answer: string,
  stuetzrad = false,
): Promise<ModuleSubmitResponse> {
  const res = await http.post<ModuleSubmitResponse>(
    `${BASE}/${moduleId}/submit`,
    { item_id: itemId, answer, stuetzrad },
  )
  return res.data
}

export async function getModuleDetail(
  moduleId: string,
): Promise<ModuleDetailResponse> {
  const res = await http.get<ModuleDetailResponse>(`${BASE}/${moduleId}/detail`)
  return res.data
}

const PREFS_BASE = '/user/exam-trainer/ap2/preferences'

export async function getPreferences(): Promise<PreferencesResponse> {
  const res = await http.get<PreferencesResponse>(PREFS_BASE)
  return res.data
}

export async function updatePreferences(
  body: Partial<UserPreferences>,
): Promise<PreferencesResponse> {
  const res = await http.put<PreferencesResponse>(PREFS_BASE, body)
  return res.data
}

export async function getRecallItem(moduleId: string): Promise<ModuleItem | null> {
  const res = await http.get<{ item: ModuleItem | null }>(`${BASE}/${moduleId}/recall-item`)
  return res.data.item
}

export async function getSpotcheckItem(moduleId: string): Promise<ModuleItem | null> {
  const res = await http.get<{ item: ModuleItem | null }>(`${BASE}/${moduleId}/spotcheck-item`)
  return res.data.item
}
