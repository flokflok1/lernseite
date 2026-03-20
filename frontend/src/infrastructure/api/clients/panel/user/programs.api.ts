/**
 * User Programs API client.
 * Enrolled programs, enrollment management, catalog.
 */
import http from '@/infrastructure/api/http'

export interface UserProgram {
  program_id: number
  program_key: string
  display_name: Record<string, string>
  program_type: string
  type_display_name: Record<string, string> | null
  provider: string | null
  icon: string | null
  sort_order: number
  total_questions: number
  seen_questions: number
  mastered_questions: number
  exam_count: number
  course_id: string | null
}

export interface ProgramDetail {
  program: UserProgram
  topics: Array<{ topic: string; total: number; correct: number; mastery: number }>
}

export async function getUserPrograms(): Promise<UserProgram[]> {
  const { data } = await http.get<{ success: boolean; programs: UserProgram[] }>(
    '/user/programs',
  )
  return data.programs
}

export async function getProgramDetail(programId: number): Promise<ProgramDetail> {
  const { data } = await http.get<{ success: boolean } & ProgramDetail>(
    `/user/programs/${programId}`,
  )
  return data
}

export async function getAvailablePrograms(): Promise<UserProgram[]> {
  const { data } = await http.get<{ success: boolean; programs: UserProgram[] }>(
    '/user/programs/available',
  )
  return data.programs
}

export async function enrollInProgram(programId: number): Promise<void> {
  await http.post(`/user/programs/${programId}/enroll`)
}

export async function unenrollFromProgram(programId: number): Promise<void> {
  await http.delete(`/user/programs/${programId}/enroll`)
}
