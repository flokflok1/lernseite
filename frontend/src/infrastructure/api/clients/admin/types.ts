/**
 * LernsystemX Admin API - Type Definitions
 */

// ============================================================================
// Core Types
// ============================================================================

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

// ============================================================================
// Filter & Pagination Types
// ============================================================================

export interface UsersFilterParams {
  page?: number
  limit?: number
  search?: string
  role?: string
  status?: 'active' | 'inactive'
  organisation_id?: number
}

export interface OrganisationsFilterParams {
  page?: number
  limit?: number
  search?: string
  type?: 'school' | 'company' | 'teacher_team' | 'creator_team'
  status?: 'active' | 'inactive'
}

export interface CoursesFilterParams {
  page?: number
  per_page?: number
  search?: string
  status?: 'all' | 'draft' | 'published' | 'archived'
  creator_id?: number
  organisation_id?: number
  category?: string
  category_id?: number
  level?: string
  language?: string
  sort?: 'created_at' | 'updated_at' | 'title' | 'enrollment_count'
  order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  total_pages: number
}

// ============================================================================
// User Management Types
// ============================================================================

export interface BanUserRequest {
  reason: string
  duration_days?: number
  permanent: boolean
  notify_user: boolean
}

export interface UnbanUserRequest {
  reason: string
}

export interface GrantTokensRequest {
  amount: number
  reason: string
}

export interface VerifyCreatorRequest {
  verified: boolean
  reason: string
}

export interface AuditLog {
  log_id: number
  user_id?: number | null
  user_email?: string | null
  user_role?: string | null
  action: string
  event_category?: string | null
  resource_type?: string | null
  resource_id?: number | null
  description?: string | null
  ip_address?: string | null
  user_agent?: string | null
  session_id?: string | null
  success: boolean
  error_message?: string | null
  created_at: string
  meta?: Record<string, unknown>
}

export interface AuditLogsFilterParams {
  page?: number
  limit?: number
  user_id?: number
  action?: string
  event_category?: string
  from?: string
  to?: string
  success?: boolean
}

// ============================================================================
// Course Management Types
// ============================================================================

export interface AdminCourseCreateRequest {
  title: string
  description?: string
  creator_id: string
  organisation_id?: string | null
  category_id?: number | null
  level?: string
  language?: string
  price?: number
  is_public?: boolean
  thumbnail_url?: string
  preview_video_url?: string
  tags?: string[]
}

export interface AdminCourseUpdateRequest {
  title?: string
  description?: string
  category_id?: number | null
  category?: string
  level?: string
  language?: string
  price?: number
  is_public?: boolean
  thumbnail_url?: string
  preview_video_url?: string
  tags?: string[]
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface UserStatsData {
  total_users: number
  active_users: number
  banned_users: number
  new_users_30d: number
}

export interface CourseStatsData {
  total_courses: number
  published: number
  pending_review: number
  rejected: number
}

export interface SystemStatsData {
  uptime: number
  db_latency: number
  request_count_24h: number
  error_rate: number
}

export interface TimeSeriesPoint {
  date: string
  value: number
}

export interface AdminAnalyticsCourse {
  course_id: number
  title: string
  events_count: number
  enrollments: number
  completions: number
  avg_completion_rate?: number
}

export interface AdminAnalyticsMethod {
  method_id: number
  name: string
  calls: number
  tokens_used?: number
  avg_tokens?: number
}

// ============================================================================
// Chapter Types
// ============================================================================

export interface AdminChapter {
  chapter_id: string
  course_id: string
  title: string
  description?: string | null
  order_index: number
  duration_minutes: number
  has_video: boolean
  has_quiz: boolean
  has_exam: boolean
  lesson_count?: number
  total_lesson_duration?: number
  created_at: string
  updated_at?: string | null
}

export interface AdminChapterCreateRequest {
  title: string
  description?: string
  order_index?: number
  duration_minutes?: number
  has_video?: boolean
  has_quiz?: boolean
  has_exam?: boolean
}

export interface AdminChapterUpdateRequest {
  title?: string
  description?: string
  order_index?: number
  duration_minutes?: number
  has_video?: boolean
  has_quiz?: boolean
  has_exam?: boolean
}

// ============================================================================
// Category Types
// ============================================================================

export interface Category {
  category_id: number
  name: string
  slug: string
  description?: string | null
  parent_id?: number | null
  level: number
  is_active: boolean
  created_at: string
  updated_at?: string | null
  path?: string | null
  root_id?: number | null
  path_ids?: number[] | null
  course_count?: number
  total_course_count?: number
  name_en?: string | null
  name_es?: string | null
  name_fr?: string | null
  children?: Category[]
  has_children?: boolean
  icon?: string | null
  color?: string | null
  order_index?: number
}

export interface CategoryTreeNode {
  category_id: number
  name: string
  slug: string
  description?: string | null
  level: number
  is_active: boolean
  children: CategoryTreeNode[]
  path?: string | null
  root_id?: number | null
  path_ids?: number[] | null
  course_count?: number
  total_course_count?: number
  has_children?: boolean
  icon?: string | null
  color?: string | null
  order_index?: number
  parent_id?: number | null
}

export interface CategoryTree {
  tree: CategoryTreeNode[]
  total_categories?: number
  max_level?: number
  active_categories?: number
}

export interface CategoryFilterParams {
  active_only?: boolean
  level?: number
  parent_id?: number
}

// ============================================================================
// Lesson Types
// ============================================================================

export type LessonType = 'text' | 'video' | 'quiz' | 'interactive' | 'assignment' | 'discussion'

export interface AdminLesson {
  lesson_id: string
  chapter_id: string
  title: string
  lesson_type: LessonType
  content?: Record<string, unknown> | null
  duration_minutes: number
  order_index: number
  published: boolean
  free_preview: boolean
  created_at: string
  updated_at?: string | null
}

export interface AdminLessonCreateRequest {
  title: string
  lesson_type?: LessonType
  content?: Record<string, unknown>
  duration_minutes?: number
  published?: boolean
  free_preview?: boolean
}

export interface AdminLessonUpdateRequest {
  title?: string
  lesson_type?: LessonType
  content?: Record<string, unknown>
  duration_minutes?: number
  order_index?: number
  published?: boolean
  free_preview?: boolean
}

// ============================================================================
// AI Job Types
// ============================================================================

export type AIJobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
export type AIJobType = 'course_from_pdf' | 'chapter_autogen' | 'lesson_autogen'

export interface AICourseDraft {
  course: {
    title: string
    description: string
    category: string
    level: string
    language: string
  }
  chapters: Array<{
    title: string
    description: string
    duration_minutes: number
    order_index: number
    lessons: Array<{
      title: string
      lesson_type: string
      duration_minutes: number
      order_index: number
    }>
  }>
}

export interface AIJob {
  id: string
  user_id: string
  course_id?: string | null
  type: AIJobType
  status: AIJobStatus
  progress: number
  input_file?: string | null
  input_prompt?: string | null
  output_data?: AICourseDraft | null
  error_message?: string | null
  created_at: string
  updated_at: string
}

export interface AIJobCreateRequest {
  type: AIJobType
  file_name?: string
  prompt?: string
  course_id?: string
}

export interface AIJobResponse {
  success: boolean
  job: AIJob
}

export interface AIJobFinalizeRequest {
  create_course?: boolean
  create_chapters?: boolean
  create_lessons?: boolean
}

export interface AIJobFinalizeResponse {
  success: boolean
  message: string
  course_id: number
  chapters_created: number
  lessons_created: number
}

// ============================================================================
// Exam Types
// ============================================================================

export type ExamType = 'practice' | 'ai_simulation' | 'final'
export type ExamStandard = 'IHK_FISI_AP1' | 'IHK_FIAE_AP1' | 'CompTIA_A+' | 'CompTIA_Network+' | 'Abitur_Informatik' | 'Custom'
export type QuestionType = 'mcq' | 'true_false' | 'fill_blanks' | 'matching' | 'short_answer' | 'math_problem' | 'case_question'

export interface ExamQuestion {
  question_id: string
  exam_id: string
  question_type: QuestionType
  question_text: string
  data: Record<string, unknown>
  solution: Record<string, unknown>
  points: number
  order_index: number
}

export interface Exam {
  exam_id: string
  course_id: string
  exam_type: ExamType
  title: string
  description?: string | null
  duration_minutes: number
  passing_score: number
  total_points: number
  settings?: Record<string, unknown>
  published: boolean
  generated_by_ai: boolean
  ai_model?: string | null
  question_count: number
  questions?: ExamQuestion[]
  created_at: string
  updated_at?: string | null
}

export interface ExamCreateRequest {
  title: string
  description?: string
  exam_type?: ExamType
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  settings?: Record<string, unknown>
  published?: boolean
}

export interface ExamUpdateRequest {
  title?: string
  description?: string
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  settings?: Record<string, unknown>
  published?: boolean
}

export interface ExamGenerateRequest {
  title: string
  description?: string
  exam_standard: ExamStandard
  difficulty?: string
  duration_minutes?: number
  passing_score?: number
  total_points?: number
  question_distribution: Record<string, number>
  topic_coverage?: Record<string, number>
  source_chapter_ids?: string[]
}

// ============================================================================
// Course Prompts Types
// ============================================================================

export type PromptScope =
  | 'course_generation'
  | 'module_generation'
  | 'exam_generation'
  | 'lesson_generation'
  | 'quiz_generation'

export interface CoursePrompt {
  course_prompt_id: string
  course_id: string
  scope: PromptScope
  language: string | null
  prompt_system: string | null
  prompt_user_template: string | null
  metadata: Record<string, unknown>
  is_active: boolean
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface CoursePromptUpdateRequest {
  language?: string | null
  prompt_system?: string | null
  prompt_user_template?: string | null
  metadata?: Record<string, unknown>
  is_active?: boolean
}

export interface CoursePromptResolveResponse {
  source: 'course_specific' | 'global' | 'hardcoded_fallback'
  scope: PromptScope
  language: string | null
  prompt_system: string | null
  prompt_user_template: string | null
  metadata: Record<string, unknown>
}

// ============================================================================
// Course Files Types
// ============================================================================

export type CourseFileType = 'pdf' | 'docx' | 'pptx' | 'xlsx' | 'txt' | 'image' | 'video' | 'audio' | 'archive' | 'other'
export type CourseFileCategory = 'script' | 'material' | 'exercise' | 'solution' | 'reference' | 'template' | 'other'

export interface CourseFile {
  course_file_id: string
  course_id: string
  file_id: string | null
  file_name: string
  file_type: CourseFileType
  file_size_bytes: number | null
  mime_type: string | null
  display_name: string | null
  description: string | null
  file_category: CourseFileCategory
  order_index: number
  is_public: boolean
  requires_enrollment: boolean
  download_count: number
  processed_for_ai: boolean
  ai_extracted_text: string | null
  ai_summary: string | null
  storage_path: string | null
  external_url: string | null
  uploaded_by: string | null
  uploader_name?: string | null
  public_url?: string | null
  cdn_url?: string | null
  media_status?: string | null
  created_at: string
  updated_at: string | null
}

export interface CourseFileCategorySummary {
  file_category: CourseFileCategory
  count: number
  total_size: number | null
}

export interface CourseFilesListResponse {
  files: CourseFile[]
  total: number
  categories_summary: CourseFileCategorySummary[]
}

export interface CourseFileUploadData {
  display_name?: string
  description?: string
  file_category?: CourseFileCategory
  is_public?: boolean
}

export interface CourseFileUpdateRequest {
  display_name?: string
  description?: string
  file_category?: CourseFileCategory
  is_public?: boolean
}

export interface CourseFileUploadResponse {
  file: CourseFile
  already_exists?: boolean
  message?: string
}

// ============================================================================
// AI Models Types
// ============================================================================

export type AIModelCategory =
  | 'reasoning'
  | 'chat'
  | 'realtime'
  | 'audio'
  | 'image'
  | 'video'
  | 'embedding'
  | 'moderation'

export type AIModelCostLevel = 'free' | 'low' | 'medium' | 'high' | 'very_high'
export type AIModelSpeed = 'very_fast' | 'fast' | 'medium' | 'slow'

export interface AIModel {
  model_id: number
  model_name: string
  display_name: string
  model_type?: string
  category: AIModelCategory
  description?: string | null
  cost_level: AIModelCostLevel
  speed: AIModelSpeed
  context_window?: number | null
  max_output_tokens?: number | null
  supports_vision?: boolean
  supports_functions?: boolean
  supports_streaming?: boolean
  is_default: boolean
  active: boolean
  provider_id?: number
  provider_name?: string
  provider_display_name?: string
  created_at?: string
  updated_at?: string
}

export interface AIModelsResponse {
  success: boolean
  data: AIModel[]
  categories: AIModelCategory[]
  total: number
  timestamp: string
}

export interface AIModelFilterParams {
  category?: AIModelCategory
  active_only?: boolean
  search?: string
  provider?: string
  configured_only?: boolean
}

export interface AIModelSyncResponse {
  success: boolean
  data: {
    added: number
    updated: number
    unchanged: number
    total_synced: number
    models: Array<{
      model_name: string
      category: string
      status: 'added' | 'updated'
    }>
  }
  timestamp: string
}

export interface AIModelRegistryCategory {
  id: string
  label: string
}

export interface AIModelRegistryItem extends AIModel {
  provider?: string
  input_price_per_1k?: number | null
  output_price_per_1k?: number | null
}

export interface AIModelUpdateRequest {
  display_name?: string
  description?: string
  cost_level?: AIModelCostLevel
  speed?: AIModelSpeed
  input_price_per_1k?: number | null
  output_price_per_1k?: number | null
  active?: boolean
}

export interface AIProviderInfo {
  provider_id: number
  name: string
  display_name: string
  has_api_key: boolean
}

export interface AIModelRegistryResponse {
  success: boolean
  data: AIModelRegistryItem[]
  categories: AIModelRegistryCategory[]
  providers: AIProviderInfo[]
  total: number
  timestamp: string
}

// ============================================================================
// AI Model Pricing Types
// ============================================================================

export interface AIModelPricing {
  model_id: number
  provider_id: number
  provider_name: string
  provider_display_name?: string
  model_name: string
  display_name: string
  category: string
  cost_per_1k_input: number | null    // Einkaufspreis (Provider-Kosten)
  cost_per_1k_output: number | null
  input_price_per_1k: number | null   // Verkaufspreis (Kundenpreis)
  output_price_per_1k: number | null
  margin_input: number | null         // Berechnete Marge %
  margin_output: number | null
  active: boolean
  is_default: boolean
  updated_at: string
}

export interface AIModelPricingResponse {
  success: boolean
  data: {
    models: AIModelPricing[]
    count: number
    categories: string[]
    providers: string[]
  }
}

export interface AIModelPricingUpdateRequest {
  cost_per_1k_input?: number | null
  cost_per_1k_output?: number | null
  input_price_per_1k?: number | null
  output_price_per_1k?: number | null
}

export interface AIModelBulkPricingRequest {
  model_ids: number[]
  updates: AIModelPricingUpdateRequest
}

export interface AIModelApplyMarginRequest {
  model_ids: number[] | 'all'
  margin_percent: number
  apply_to: 'input' | 'output' | 'both'
}

export interface AIModelBulkPricingResponse {
  success: boolean
  data: { updated_count: number }
  message: string
}

// ============================================================================
// Learning Methods Types
// ============================================================================

export type LearningMethodGroup = 'A' | 'B' | 'C' | 'D' | 'E' | 'F'

export interface LearningMethodType {
  lm_id: number
  name: string
  group: LearningMethodGroup
  method_type: 'explanatory' | 'practice' | 'exam' | 'meta' | 'it' | 'collaborative'
  ki_usage: 'intensive' | 'medium' | 'optional'
  prompt_key: string
  description: string
}

export interface LearningMethodTypesResponse {
  success: boolean
  types: LearningMethodType[]
  total: number
  groups: {
    A: { name: string; range: string; count: number }
    B: { name: string; range: string; count: number }
    C: { name: string; range: string; count: number }
    D: { name: string; range: string; count: number }
  }
}

export interface AdminLearningMethod {
  method_id: string
  chapter_id: string
  method_type: number
  title: string
  instructions?: string | null
  data: Record<string, unknown>
  solution?: Record<string, unknown> | null
  tier: 'basic' | 'premium' | 'pro'
  duration_minutes?: number | null
  difficulty: 'easy' | 'medium' | 'hard'
  order_index: number
  published: boolean
  created_at: string
  updated_at?: string | null
  method_name?: string
  method_group?: LearningMethodGroup
  method_type_name?: string
  ki_usage?: string
  prompt_key?: string
  method_description?: string
}

export interface AdminLearningMethodCreateRequest {
  method_type: number
  title: string
  instructions?: string
  data?: Record<string, unknown>
  solution?: Record<string, unknown>
  tier?: 'basic' | 'premium' | 'pro'
  duration_minutes?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  order_index?: number
  published?: boolean
}

export interface AdminLearningMethodUpdateRequest {
  method_type?: number
  title?: string
  instructions?: string
  data?: Record<string, unknown>
  solution?: Record<string, unknown>
  tier?: 'basic' | 'premium' | 'pro'
  duration_minutes?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  order_index?: number
  published?: boolean
}

export interface AdminLearningMethodsResponse {
  success: boolean
  learning_methods: AdminLearningMethod[]
  total: number
  chapter_id: string
  statistics?: {
    total_methods: number
    published_count: number
    unique_types: number
    total_duration: number
    easy_count: number
    medium_count: number
    hard_count: number
    basic_count: number
    premium_count: number
    pro_count: number
  }
}

// ============================================================================
// LM Routing Types
// ============================================================================

export interface LMModelAssignment {
  learning_method_id: number
  lm_code: string
  lm_name: string
  lm_group: 'A' | 'B' | 'C' | 'D' | null
  lm_type: 'explanatory' | 'practice' | 'exam' | 'meta' | null
  ki_usage: 'intensive' | 'medium' | 'optional' | null
  model_required: boolean
  recommended_categories: string[]
  requires_vision: boolean
  assignment_id: number | null
  model_id: number | null
  model_name: string | null
  model_display_name: string | null
  model_category: string | null
  provider_name: string | null
  provider_display_name: string | null
  is_configured: boolean
}

export interface LMRoutingOverview {
  assignments: LMModelAssignment[]
  stats: {
    total: number
    configured: number
    unconfigured_required: number
    unconfigured_optional: number
  }
}

export interface LMRequirement {
  learning_method_id: number
  lm_code: string
  lm_name: string
  required: boolean
  recommended_categories: string[]
  requires_vision: boolean
  requires_functions: boolean
  min_context_window: number | null
  description: string | null
}

export interface UnconfiguredLM {
  learning_method_id: number
  lm_code: string
  lm_name: string
  lm_group: string | null
  recommended_categories: string[]
  description: string | null
}

export interface RecommendedModel {
  model_id: number
  model_name: string
  display_name: string
  category: string
  provider_name: string
  provider_display_name: string
  score: number
  reasons: string[]
  cost_level: string
  supports_vision: boolean
  context_window: number | null
}

export interface AutoSetupOptions {
  only_required?: boolean
  prefer_cheap?: boolean
  overwrite_existing?: boolean
}

export interface AutoSetupResult {
  configured: number
  skipped: number
  failed: number
  assignments: Array<{
    lm_id: number
    lm_code: string
    lm_name: string
    model_name: string
    provider: string
    score: number
  }>
}

export interface AIAutoSetupOptions {
  model?: string
  overwrite_existing?: boolean
}

export interface AIAutoSetupAssignment {
  lm_id: number
  lm_code: string
  lm_name: string
  model_id: number
  model_name: string
  provider: string
  reasoning: string
}

export interface AIAutoSetupResult {
  configured: number
  failed: number
  assignments: AIAutoSetupAssignment[]
  ai_model_used: string
  total_cost_eur: number
}

// ============================================================================
// LM Capability Slots Types
// ============================================================================

export interface CapabilitySlot {
  slot_id: number
  slot_code: string
  display_name: string
  description: string
  required_category: string
  accepted_categories: string[]
  icon: string
  sort_order: number
}

export interface CompatibleModel {
  model_id: number
  model_name: string
  display_name: string
  category: string
  provider_name: string
  provider_display_name: string
  supports_vision: boolean
  supports_functions: boolean
  context_window: number | null
  cost_level: string
}

export interface LMSlotConfig {
  slot_code: string
  slot_display_name: string
  is_required: boolean
  is_primary: boolean
  is_configured: boolean
  model: {
    model_id: number
    model_name: string
    display_name: string
    provider: string
  } | null
  resolved_scope: string
  compatible_models?: CompatibleModel[]
}

export interface LMSlotOverview {
  learning_method_id: number
  name: string
  group: string
  ready: boolean
  required_count: number
  configured_count: number
  slots: LMSlotConfig[]
}

export interface SlotAssignmentRequest {
  model_id: number
  scope?: 'system' | 'course' | 'chapter'
  scope_reference_id?: string | null
}

export interface BulkSlotAssignment {
  slot_code: string
  model_id: number
  priority?: number
}

// ============================================================================
// Feature Flags & Configuration
// ============================================================================

export interface FeatureFlag {
  feature_id: string
  feature_name: string
  feature_code: string
  description?: string | null
  category: string
  is_enabled: boolean
  rollout_percentage: number
  tier_required?: string | null
  max_daily_quota?: number | null
  max_monthly_quota?: number | null
  disabled_reason?: string | null
  created_by?: string | null
  updated_by?: string | null
  created_at: string
  updated_at?: string | null
}

export interface FeatureFlagCreateRequest {
  feature_name: string
  feature_code: string
  description?: string
  category: string
  is_enabled?: boolean
  tier_required?: string
  max_daily_quota?: number
  max_monthly_quota?: number
}

export interface FeatureFlagUpdateRequest {
  feature_name?: string
  description?: string
  category?: string
  is_enabled?: boolean
  tier_required?: string
  max_daily_quota?: number
  max_monthly_quota?: number
}

export interface FeatureFlagFilters {
  limit?: number
  offset?: number
  enabled?: boolean
  category?: string
}

export interface RolloutPhase {
  phase: number
  percentage: number
  description: string
  started_at?: string
  completed_at?: string
}

export interface RolloutPlan {
  plan_id: string
  feature_name: string
  feature_id: string
  description?: string | null
  status: 'planned' | 'active' | 'paused' | 'completed' | 'rolled_back'
  current_percentage: number
  target_percentage: number
  phases: RolloutPhase[]
  paused_reason?: string | null
  started_at?: string | null
  estimated_end_date?: string | null
  completed_at?: string | null
  rolled_back_at?: string | null
  rolled_back_reason?: string | null
  created_by?: string | null
  updated_by?: string | null
  created_at: string
  updated_at?: string | null
}

// ============================================================================
// Pagination & Response Wrappers
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
  total_pages?: number
  current_page?: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  meta?: {
    timestamp: string
    [key: string]: any
  }
}
