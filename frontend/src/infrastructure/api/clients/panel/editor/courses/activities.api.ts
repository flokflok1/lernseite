import http from '@/infrastructure/api/http'

const EDITOR_PREFIX = '/course-editor/manual'

// ============================================================================
// Lesson Activities (Learning Method Instances per Lesson)
// ============================================================================

export interface LessonActivity {
  method_id: string
  chapter_id: string
  lesson_id: string
  method_type: number
  title: string
  instructions?: string
  data: Record<string, unknown>
  tier: string
  duration_minutes?: number
  difficulty: string
  order_index: number
  published: boolean
  created_at: string
  updated_at: string
}

export const getLessonActivities = async (lessonId: string): Promise<LessonActivity[]> => {
  const response = await http.get<{
    success: boolean
    activities: LessonActivity[]
  }>(`${EDITOR_PREFIX}/lessons/${lessonId}/activities`)

  return response.data.activities || []
}

export const createLessonActivity = async (
  lessonId: string,
  methodType: number,
  title: string
): Promise<LessonActivity> => {
  const response = await http.post<{
    success: boolean
    activity: LessonActivity
  }>(`${EDITOR_PREFIX}/lessons/${lessonId}/activities`, {
    method_type: methodType,
    title
  })

  return response.data.activity
}

export const updateLessonActivity = async (
  activityId: string,
  payload: Partial<Pick<LessonActivity, 'title' | 'instructions' | 'data' | 'difficulty' | 'duration_minutes' | 'published'>>
): Promise<LessonActivity> => {
  const response = await http.patch<{
    success: boolean
    activity: LessonActivity
  }>(`${EDITOR_PREFIX}/activities/${activityId}`, payload)

  return response.data.activity
}

export const deleteLessonActivity = async (activityId: string): Promise<void> => {
  await http.delete(`${EDITOR_PREFIX}/activities/${activityId}`)
}

export const reorderLessonActivities = async (
  lessonId: string,
  methodIds: string[]
): Promise<void> => {
  await http.post(`${EDITOR_PREFIX}/lessons/${lessonId}/activities/reorder`, {
    method_ids: methodIds
  })
}
