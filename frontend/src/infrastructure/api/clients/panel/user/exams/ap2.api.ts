/**
 * AP2 Trainer API Client — wraps /api/v1/user/exam-trainer/ap2/*
 * Backend: 12 Routes (siehe backend/app/api/v1/panel/user/exams/ap2/)
 */

import http from '@/infrastructure/api/http'

// ===================== TYPES =====================

export type Bereich = 'PB2' | 'PB3' | 'WISO' | 'both'
export type Priority = 'sehr-hoch' | 'hoch' | 'mittel' | 'niedrig'
export type ItemType = 'blurt' | 'cued' | 'application'
export type Phase = 'blurt' | 'cued' | 'application' | 'review'
export type SessionType = 'topic_study' | 'review_queue' | 'exam_simulation' | 'mixed_practice'

export interface Ap2Topic {
  topic_id: string
  slug: string
  name_de: string
  name_en: string | null
  bereich: Bereich
  priority: Priority
  expected_points: number
  exam_count: number
  description: string | null
  is_critical: boolean
}

export interface Ap2Item {
  item_id: string
  item_type: ItemType
  prompt: string
  points: number
  source_exam: string | null
  anlage_id: string | null
  difficulty: number
  estimated_time_sec: number
}

export interface Ap2BereichStat {
  topic_count: number
  avg_mastery: number
  points_earned: number
  points_possible: number
  pct: number
}

export interface Ap2TopicStat {
  topic_slug: string
  topic_name: string
  bereich: Bereich
  priority: Priority
  mastery_score: number
  attempts_count: number
  correct_count: number
  last_attempt_at: string | null
}

export interface Ap2Weakness {
  topic_slug: string
  topic_name: string
  bereich: Bereich
  priority: Priority
  mastery_score: number
  attempts_count: number
  gap: number
}

export interface Ap2Regression {
  item_id: string
  topic_slug: string
  topic_name: string
  item_type: ItemType
  item_prompt: string
  last_pct: number
  prev_pct: number
  regression_size: number
  last_attempt_at: string | null
}

export interface Ap2Stats {
  success: boolean
  overall: {
    attempts: number
    correct: number
    total_earned: number
    total_possible: number
    pct: number
    pass_prediction: 'bestanden' | 'gefaehrdet' | 'unvollstaendig'
  }
  bereich_stats: Record<string, Ap2BereichStat>
  bereich_pass: Record<string, boolean | null>
  topic_stats: Ap2TopicStat[]
  weaknesses: Ap2Weakness[]
  recent_regressions: Ap2Regression[]
  review_queue_count: number
}

export interface Ap2AnlageHotspot {
  hotspot_id: string
  x: number; y: number; width: number; height: number
  hotspot_type: 'text' | 'number' | 'ip-address' | 'subnet-mask' | 'ipv6-address' | 'dropdown' | 'draggable-label'
  placeholder: string | null
  hint: string | null
  dropdown_options: string[]
  points: number
}

export interface Ap2Anlage {
  anlage_id: string
  slug: string
  title: string
  anlage_type: string
  source_exam: string | null
  anlage_number: number | null
  image_url: string | null
  image_width: number | null
  image_height: number | null
  svg_markup: string | null
  description: string | null
  footnote: string | null
  hotspots: Ap2AnlageHotspot[]
  total_points: number
}

export interface Ap2AttemptFeedback {
  summary: string
  correct_aspects: string[]
  missing_aspects: string[]
  partial_aspects: string[]
  incorrect_aspects: string[]
  suggestions: string[]
}

export interface Ap2SubmitResponse {
  success: boolean
  attempt_id: string
  pct: number
  points_earned: number
  points_total: number
  feedback: Ap2AttemptFeedback
  model_answer: string
  mastery_score: number
  next_review_at: string
}

export interface Ap2ReviewQueueItem {
  item_id: string
  topic_id: string
  topic_name: string
  topic_bereich: Bereich
  item_type: ItemType
  prompt: string
  points: number
  difficulty: number
  estimated_time_sec: number
  next_review_at: string | null
  repetitions: number
}

export interface Ap2Cheatsheet {
  topic_slug: string
  topic_name: string
  markdown_content: string
  word_count: number
  updated_at: string | null
}

// ===================== STATS + TOPICS =====================

const BASE = '/user/exam-trainer/ap2'

export async function getAp2Stats(): Promise<Ap2Stats> {
  const res = await http.get(`${BASE}/stats`)
  return res.data
}

export async function listAp2Topics(): Promise<{ success: boolean; topics: Ap2Topic[] }> {
  const res = await http.get(`${BASE}/topics`)
  return res.data
}

export async function getAp2TopicDetail(slug: string): Promise<{
  success: boolean
  topic: Ap2Topic
  items: Record<ItemType, Ap2Item[]>
}> {
  const res = await http.get(`${BASE}/topics/${slug}`)
  return res.data
}

// ===================== STUDY FLOW =====================

export async function submitAp2Attempt(payload: {
  item_id: string
  phase: Phase
  answer_text: string
  answer_hotspots?: Record<string, string>
  time_spent_sec?: number
  user_quality_override?: number
  session_id?: string
}): Promise<Ap2SubmitResponse> {
  const res = await http.post(`${BASE}/attempts/submit`, payload)
  return res.data
}

export async function getAp2ReviewQueue(limit = 20): Promise<{
  success: boolean
  count_total_due: number
  items: Ap2ReviewQueueItem[]
}> {
  const res = await http.get(`${BASE}/review/queue`, { params: { limit } })
  return res.data
}

export async function startAp2Session(payload: {
  session_type: SessionType
  topic_id?: string
  metadata?: Record<string, unknown>
}): Promise<{ success: boolean; session_id: string; started_at: string }> {
  const res = await http.post(`${BASE}/sessions/start`, payload)
  return res.data
}

export async function endAp2Session(session_id: string): Promise<{ success: boolean }> {
  const res = await http.post(`${BASE}/sessions/${session_id}/end`)
  return res.data
}

// ===================== ANLAGEN =====================

export async function listAp2Anlagen(): Promise<{ success: boolean; anlagen: Ap2Anlage[] }> {
  const res = await http.get(`${BASE}/anlagen`)
  return res.data
}

export async function getAp2Anlage(anlage_id: string): Promise<{
  success: boolean
  anlage: Ap2Anlage
}> {
  const res = await http.get(`${BASE}/anlagen/${anlage_id}`)
  return res.data
}

// ===================== CHEATSHEETS =====================

export async function listAp2Cheatsheets(): Promise<{
  success: boolean
  cheatsheets: Ap2Cheatsheet[]
}> {
  const res = await http.get(`${BASE}/cheatsheets`)
  return res.data
}

export async function getAp2Cheatsheet(topic_slug: string): Promise<Ap2Cheatsheet & { success: boolean }> {
  const res = await http.get(`${BASE}/cheatsheets/${topic_slug}`)
  return res.data
}

export async function saveAp2Cheatsheet(
  topic_slug: string,
  markdown_content: string,
): Promise<{ success: boolean; word_count: number }> {
  const res = await http.put(`${BASE}/cheatsheets/${topic_slug}`, { markdown_content })
  return res.data
}
