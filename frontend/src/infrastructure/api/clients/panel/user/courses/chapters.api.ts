/**
 * Chapter API Client
 * ==================
 * DDD-compliant API layer for chapter detail operations.
 * Composables import from here instead of raw http.
 */
import http from '@/infrastructure/api/http'

export async function getChapterDetail(courseId: string, chapterId: string) {
  const res = await http.get(`/courses/${courseId}/chapters/${chapterId}`)
  return res.data
}

export async function getChapterProgress(courseId: string, chapterId: string) {
  const res = await http.get(`/courses/${courseId}/chapters/${chapterId}/progress`)
  return res.data
}

export async function getChapterTheories(chapterId: string) {
  const res = await http.get(`/chapters/${chapterId}/theories`)
  return res.data?.data?.theories || []
}

export async function getChapterTheory(chapterId: string) {
  const res = await http.get(`/chapters/${chapterId}/theory`)
  return res.data?.data
}

export async function getTheoryById(theoryId: string) {
  const res = await http.get(`/chapter-theory/${theoryId}`)
  return res.data?.data
}
