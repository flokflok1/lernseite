/**
 * Admin Exam Archive Folders API - File Explorer operations
 */

import http from '@/infrastructure/api/http'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface ArchiveFolder {
  folder_id: string
  parent_folder_id: string | null
  program_id: string
  name: string
  icon: string
  position: number
  metadata: Record<string, unknown>
  created_at: string
  child_count?: number
  file_count?: number
  children?: ArchiveFolder[]
}

export interface ArchiveFile {
  exam_id: string
  title: string
  pdf_path: string
  analysis_status: 'pending' | 'analyzing' | 'ready' | 'failed'
  created_at: string
  year: number
  season: string
  part: string
  question_count: number
}

export interface FolderContents {
  folder: ArchiveFolder | null
  children: ArchiveFolder[]
  files: ArchiveFile[]
  breadcrumb: { folder_id: string; name: string }[]
}

export interface ExamProgram {
  program_id: string
  program_key: string
  display_name: Record<string, string>
  program_type: string
  provider: string
  icon: string
  sort_order: number
  root_folder_count?: number
  total_file_count?: number
}

// ---------------------------------------------------------------------------
// API Client
// ---------------------------------------------------------------------------

const BASE = '/admin/exam-archive/folders'

export function fetchPrograms() {
  return http.get<{ programs: ExamProgram[] }>(`${BASE}/programs`)
}

export function fetchSidebarTree(programId: string) {
  return http.get<{ tree: ArchiveFolder[] }>(`${BASE}/tree/${programId}`)
}

export function fetchFolderContents(folderId: string) {
  return http.get<FolderContents>(`${BASE}/contents/${folderId}`)
}

export function fetchProgramRoot(programId: string) {
  return http.get<FolderContents>(`${BASE}/contents/program/${programId}`)
}

export function createFolder(params: {
  parent_folder_id: string | null
  program_id: string
  name: string
  icon?: string
}) {
  return http.post<{ folder: ArchiveFolder }>(BASE, params)
}

export function updateFolder(
  folderId: string,
  params: { name?: string; icon?: string; position?: number }
) {
  return http.patch<{ folder: ArchiveFolder }>(`${BASE}/${folderId}`, params)
}

export function moveFolder(folderId: string, newParentId: string | null) {
  return http.post<{ folder: ArchiveFolder }>(`${BASE}/${folderId}/move`, {
    new_parent_id: newParentId
  })
}

export function deleteFolder(folderId: string) {
  return http.delete<{ success: boolean }>(`${BASE}/${folderId}`)
}

export function moveFileToFolder(examId: string, folderId: string) {
  return http.post<{ success: boolean }>(`${BASE}/move-file`, {
    exam_id: examId,
    folder_id: folderId
  })
}
