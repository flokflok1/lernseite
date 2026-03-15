/**
 * Admin Course Management API
 *
 * Routes map to backend: /api/v1/course-editor/manual/courses/*
 */

import http from '@/infrastructure/api/http'
import type {
  AdminCourse,
  AdminCourseDetail,
  AdminCourseCreateRequest,
  AdminCourseUpdateRequest,
  CoursesFilterParams,
  PaginatedResponse
} from '../types'

const PREFIX = '/course-editor/manual'

export const adminGetCourses = async (
  params: CoursesFilterParams = {}
): Promise<PaginatedResponse<AdminCourse>> => {
  const response = await http.get<{
    success: boolean
    courses: AdminCourse[]
    pagination: {
      total: number
      page: number
      per_page: number
      total_pages: number
    }
  }>(`${PREFIX}/courses`, { params })

  return {
    items: response.data.courses,
    total: response.data.pagination.total,
    page: response.data.pagination.page,
    limit: response.data.pagination.per_page,
    total_pages: response.data.pagination.total_pages
  }
}

export const adminGetCourseDetail = async (courseId: string): Promise<AdminCourseDetail> => {
  const response = await http.get<{
    success: boolean
    course: AdminCourseDetail
  }>(`${PREFIX}/courses/${courseId}`)

  return response.data.course
}

export const adminCreateCourse = async (
  data: AdminCourseCreateRequest
): Promise<AdminCourseDetail> => {
  const response = await http.post<{
    success: boolean
    course: AdminCourseDetail
  }>(`${PREFIX}/courses`, data)

  return response.data.course
}

export const adminUpdateCourse = async (
  courseId: string,
  data: AdminCourseUpdateRequest
): Promise<AdminCourseDetail> => {
  const response = await http.patch<{
    success: boolean
    course: AdminCourseDetail
  }>(`${PREFIX}/courses/${courseId}`, data)

  return response.data.course
}

export const adminChangeCourseStatus = async (
  courseId: string,
  action: 'publish' | 'unpublish' | 'archive' | 'unarchive',
  reason?: string
): Promise<string> => {
  const response = await http.post<{
    success: boolean
    status: string
  }>(`${PREFIX}/courses/${courseId}/status`, {
    action,
    reason
  })

  return response.data.status
}

export const adminPublishCourse = async (courseId: string, reason?: string): Promise<void> => {
  await adminChangeCourseStatus(courseId, 'publish', reason)
}

export const adminUnpublishCourse = async (courseId: string, reason?: string): Promise<void> => {
  await adminChangeCourseStatus(courseId, 'unpublish', reason)
}

export const adminArchiveCourse = async (courseId: string, reason?: string): Promise<void> => {
  await adminChangeCourseStatus(courseId, 'archive', reason)
}

export const adminUnarchiveCourse = async (courseId: string, reason?: string): Promise<void> => {
  await adminChangeCourseStatus(courseId, 'unarchive', reason)
}

export const adminDeleteCourse = async (courseId: string, reason?: string): Promise<void> => {
  await http.delete(`${PREFIX}/courses/${courseId}`, {
    data: { reason }
  })
}

export const adminPermanentDeleteCourse = async (courseId: string, reason?: string): Promise<void> => {
  await http.delete(`${PREFIX}/courses/${courseId}/permanent`, {
    data: { confirm: true, reason }
  })
}
