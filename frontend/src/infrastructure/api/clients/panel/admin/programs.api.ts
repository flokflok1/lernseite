/**
 * Admin Programs API client.
 * Program CRUD, program types management.
 */
import http from '@/infrastructure/api/http'

export interface ExamType {
  exam_type: string
  display_name: Record<string, string>
  passing_score: number
  applies_to: string[]
  sort_order: number
  program_id: number | null
  archive_folder_id: string | null
  exam_count?: number
  question_count?: number
}

export interface AdminProgram {
  program_id: number
  program_key: string
  display_name: Record<string, string>
  program_type: string
  provider: string | null
  icon: string | null
  sort_order: number
  parts: ExamType[]
}

export interface ProgramType {
  type_key: string
  display_name: Record<string, string>
  icon: string | null
  sort_order: number
}

export async function getAdminPrograms(): Promise<AdminProgram[]> {
  const { data } = await http.get<{ success: boolean; programs: AdminProgram[] }>(
    '/admin/programs',
  )
  return data.programs
}

export async function createProgram(payload: Record<string, unknown>): Promise<AdminProgram> {
  const { data } = await http.post<{ success: boolean; program: AdminProgram }>(
    '/admin/programs', payload,
  )
  return data.program
}

export async function updateProgram(id: number, payload: Record<string, unknown>): Promise<AdminProgram> {
  const { data } = await http.put<{ success: boolean; program: AdminProgram }>(
    `/admin/programs/${id}`, payload,
  )
  return data.program
}

export async function deleteProgram(id: number): Promise<void> {
  await http.delete(`/admin/programs/${id}`)
}

export async function getProgramTypes(): Promise<ProgramType[]> {
  const { data } = await http.get<{ success: boolean; types: ProgramType[] }>(
    '/admin/program-types',
  )
  return data.types
}

export async function createProgramType(payload: Record<string, unknown>): Promise<ProgramType> {
  const { data } = await http.post<{ success: boolean; type: ProgramType }>(
    '/admin/program-types', payload,
  )
  return data.type
}

export async function updateProgramType(key: string, payload: Record<string, unknown>): Promise<ProgramType> {
  const { data } = await http.put<{ success: boolean; type: ProgramType }>(
    `/admin/program-types/${key}`, payload,
  )
  return data.type
}

export async function deleteProgramType(key: string): Promise<void> {
  await http.delete(`/admin/program-types/${key}`)
}

export async function getExamTypes(programId: number): Promise<ExamType[]> {
  const { data } = await http.get<{ success: boolean; exam_types: ExamType[] }>(
    '/admin/exam-types', { params: { program_id: programId } },
  )
  return data.exam_types
}

export async function createExamType(payload: Record<string, unknown>): Promise<ExamType> {
  const { data } = await http.post<{ success: boolean; exam_type: ExamType }>(
    '/admin/exam-types', payload,
  )
  return data.exam_type
}

export async function updateExamType(key: string, payload: Record<string, unknown>): Promise<ExamType> {
  const { data } = await http.put<{ success: boolean; exam_type: ExamType }>(
    `/admin/exam-types/${key}`, payload,
  )
  return data.exam_type
}

export async function deleteExamType(key: string): Promise<void> {
  await http.delete(`/admin/exam-types/${key}`)
}
