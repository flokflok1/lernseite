import http from '@/infrastructure/api/http'

export interface ChapterPreview {
  topic: string
  question_count: number
  lm_types: number[]
  point_weight: number
  parent_label?: Record<string, string> | null
  child_topics?: string[] | null
}

export interface CoursePlan {
  title: string
  exam_type: string
  region: string
  total_questions: number
  total_points: number
  chapters: ChapterPreview[]
  simulation_exam_ids: string[]
}

export interface GenerateResult {
  course_id: string
  chapters_count: number
  lm_count: number
  tokens_used: number
  status?: 'generating' | 'ready'
}

export interface GenerationProgress {
  total: number
  completed: number
  failed: number
  status: 'generating' | 'ready' | 'partial' | 'failed' | 'unknown'
}

export async function previewExamCourse(
  examType: string,
  region: string = 'alle'
): Promise<CoursePlan> {
  const response = await http.post<{ success: boolean; plan: CoursePlan }>(
    '/admin/exam-courses/preview',
    { exam_type: examType, region }
  )
  return response.data.plan
}

export async function generateExamCourse(
  examType: string,
  region: string = 'alle',
  options?: { provider?: string; model?: string }
): Promise<GenerateResult> {
  const response = await http.post<{ success: boolean } & GenerateResult>(
    '/admin/exam-courses/generate',
    { exam_type: examType, region, options }
  )
  return {
    course_id: response.data.course_id,
    chapters_count: response.data.chapters_count,
    lm_count: response.data.lm_count,
    tokens_used: response.data.tokens_used,
    status: response.data.status,
  }
}

export async function getGenerationProgress(
  courseId: string
): Promise<GenerationProgress> {
  const response = await http.get<{ success: boolean; data: GenerationProgress }>(
    `/admin/exam-courses/courses/${courseId}/generation-progress`
  )
  return response.data.data
}
