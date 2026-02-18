/**
 * Admin API - Core Entity Types
 *
 * Primary entity interfaces used across the admin panel:
 * users, organisations, courses, tokens, and system stats.
 */

export interface AdminUser {
  user_id: number
  email: string
  first_name: string
  last_name: string
  role: string
  organisation_id?: number | null
  organisation_name?: string | null
  is_active: boolean
  created_at: string
  last_login?: string | null
  token_balance?: number
}

export interface AdminOrganisation {
  organisation_id: number
  name: string
  type: 'school' | 'company' | 'teacher_team' | 'creator_team'
  plan_id?: string | null
  plan_name?: string
  active_users: number
  total_users: number
  token_pool: number
  token_used: number
  created_at: string
  is_active: boolean
  domain?: string | null
}

export interface AdminCourse {
  course_id: string
  title: string
  description?: string | null
  long_description?: string | null
  creator_id: string
  creator_name?: string
  creator_email?: string
  organisation_id?: string | null
  organisation_name?: string | null
  category?: string | null
  level?: string
  language: string
  price?: number
  is_public: boolean
  status: 'draft' | 'published' | 'archived'
  thumbnail_url?: string | null
  preview_video_url?: string | null
  tags?: string[]
  chapter_count: number
  enrollment_count: number
  ad_enabled?: boolean
  learning_goals?: string[]
  target_audience?: string | null
  created_at: string
  updated_at?: string | null
  published_at?: string | null
  archived_at?: string | null
}

export interface AdminCourseDetail extends AdminCourse {
  category_id?: number | null
  category_name?: string | null
}

export interface AdminTokenStats {
  total_tokens_purchased: number
  total_tokens_used: number
  total_tokens_available: number
  tokens_used_today: number
  tokens_used_7_days: number
  tokens_used_30_days: number
  top_consumers?: Array<{
    user_id: number
    user_name: string
    tokens_used: number
  }>
}

export interface AdminSystemStats {
  total_users: number
  active_users_7_days: number
  active_users_30_days: number
  new_users_7_days: number
  total_organisations: number
  total_courses: number
  published_courses: number
  total_lessons: number
  total_enrollments: number
  premium_subscriptions: number
  revenue_30_days?: number
  token_stats: AdminTokenStats
}

export interface AdminPlanOverview {
  plan_id: string
  plan_name: string
  price: number
  currency: string
  features: string[]
  subscriber_count: number
}
