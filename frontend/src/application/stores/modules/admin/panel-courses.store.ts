/**
 * LernsystemX - Panel Courses Sub-Store (Pinia)
 *
 * Manages admin course management:
 * - Course listing with pagination and filters
 * - Course CRUD, publish/unpublish, archive/unarchive
 * - Chapter management (CRUD, reorder)
 * - Category management (tree, flat list, CRUD)
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as adminApi from '@/application/services/api/panel-admin'
import type {
  AdminCourse,
  CoursesFilterParams,
  PaginatedResponse,
  AdminChapter,
  AdminChapterCreateRequest,
  AdminChapterUpdateRequest,
  Category,
  CategoryTreeNode
} from '@/application/services/api/panel-admin'

export const usePanelCoursesStore = defineStore('panel-courses', () => {
  // State - Courses
  const courses = ref<AdminCourse[]>([])
  const coursesTotal = ref(0)
  const coursesPage = ref(1)
  const coursesLimit = ref(20)
  const coursesTotalPages = ref(0)
  const courseFilters = ref<CoursesFilterParams>({})
  // State - Chapters
  const courseChapters = ref<Map<number, AdminChapter[]>>(new Map())
  const currentChapters = ref<AdminChapter[]>([])
  // State - Categories
  const categoryTree = ref<CategoryTreeNode[]>([])
  const categoriesFlat = ref<Category[]>([])
  const categoriesLoaded = ref(false)
  // State - UI
  const loading = ref(false)
  const error = ref<string | null>(null)

  /**
   * Load courses with filters
   */
  const loadCourses = async (params: CoursesFilterParams = {}): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response: PaginatedResponse<AdminCourse> = await adminApi.adminGetCourses(params)

      courses.value = response.items
      coursesTotal.value = response.total
      coursesPage.value = response.page
      coursesLimit.value = response.limit
      coursesTotalPages.value = response.total_pages
      courseFilters.value = params
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kurse'
      console.error('Failed to load courses:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Publish course
   */
  const publishCourse = async (courseId: number): Promise<void> => {
    try {
      await adminApi.adminPublishCourse(courseId)

      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.is_published = true
        course.status = 'published'
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Veröffentlichen des Kurses'
      console.error('Failed to publish course:', err)
      throw err
    }
  }

  /**
   * Unpublish course
   */
  const unpublishCourse = async (courseId: number): Promise<void> => {
    try {
      await adminApi.adminUnpublishCourse(courseId)

      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.is_published = false
        course.status = 'draft'
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Zurückziehen des Kurses'
      console.error('Failed to unpublish course:', err)
      throw err
    }
  }

  /**
   * Archive course
   */
  const archiveCourse = async (courseId: number): Promise<void> => {
    try {
      await adminApi.adminArchiveCourse(courseId)

      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.status = 'archived'
        course.is_published = false
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Archivieren des Kurses'
      console.error('Failed to archive course:', err)
      throw err
    }
  }

  /**
   * Delete course (soft delete / archive)
   */
  const deleteCourse = async (courseId: number, reason?: string): Promise<void> => {
    try {
      await adminApi.adminDeleteCourse(courseId, reason)

      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.status = 'archived'
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Löschen des Kurses'
      console.error('Failed to delete course:', err)
      throw err
    }
  }

  /**
   * Unarchive course
   */
  const unarchiveCourse = async (courseId: number, reason?: string): Promise<void> => {
    try {
      await adminApi.adminUnarchiveCourse(courseId, reason)

      const course = courses.value.find(c => c.course_id === courseId)
      if (course) {
        course.status = 'draft'
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Wiederherstellen des Kurses'
      console.error('Failed to unarchive course:', err)
      throw err
    }
  }

  /**
   * Permanently delete course (hard delete)
   */
  const permanentDeleteCourse = async (courseId: number, reason?: string): Promise<void> => {
    try {
      await adminApi.adminPermanentDeleteCourse(courseId, reason)

      courses.value = courses.value.filter(c => c.course_id !== courseId)
      coursesTotal.value -= 1
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim permanenten Löschen des Kurses'
      console.error('Failed to permanently delete course:', err)
      throw err
    }
  }

  /**
   * Get course detail
   */
  const getCourseDetail = async (courseId: number): Promise<adminApi.AdminCourseDetail> => {
    try {
      const course = await adminApi.adminGetCourseDetail(courseId)
      return course
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kursdetails'
      console.error('Failed to load course detail:', err)
      throw err
    }
  }

  /**
   * Create course
   */
  const createCourse = async (data: adminApi.AdminCourseCreateRequest): Promise<adminApi.AdminCourseDetail> => {
    try {
      const course = await adminApi.adminCreateCourse(data)

      courses.value.unshift(course as any)
      coursesTotal.value += 1

      return course
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Erstellen des Kurses'
      console.error('Failed to create course:', err)
      throw err
    }
  }

  /**
   * Update course
   */
  const updateCourse = async (
    courseId: number,
    data: adminApi.AdminCourseUpdateRequest
  ): Promise<adminApi.AdminCourseDetail> => {
    try {
      const updatedCourse = await adminApi.adminUpdateCourse(courseId, data)

      const index = courses.value.findIndex(c => c.course_id === courseId)
      if (index !== -1) {
        courses.value[index] = { ...courses.value[index], ...updatedCourse }
      }

      return updatedCourse
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Aktualisieren des Kurses'
      console.error('Failed to update course:', err)
      throw err
    }
  }

  /**
   * Load chapters for a specific course
   */
  const loadCourseChapters = async (courseId: number): Promise<AdminChapter[]> => {
    loading.value = true
    error.value = null

    try {
      const chapters = await adminApi.adminGetCourseChapters(courseId)

      courseChapters.value.set(courseId, chapters)
      currentChapters.value = chapters

      return chapters
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kapitel'
      console.error('Failed to load course chapters:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Create new chapter for a course
   */
  const createChapter = async (
    courseId: number,
    data: AdminChapterCreateRequest
  ): Promise<AdminChapter> => {
    try {
      const chapter = await adminApi.adminCreateChapter(courseId, data)

      const chapters = courseChapters.value.get(courseId) || []
      chapters.push(chapter)
      courseChapters.value.set(courseId, chapters)
      currentChapters.value = chapters

      return chapter
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Erstellen des Kapitels'
      console.error('Failed to create chapter:', err)
      throw err
    }
  }

  /**
   * Update chapter metadata
   */
  const updateChapter = async (
    chapterId: string,
    data: AdminChapterUpdateRequest
  ): Promise<AdminChapter> => {
    try {
      const updatedChapter = await adminApi.adminUpdateChapter(chapterId, data)

      for (const [courseId, chapters] of courseChapters.value.entries()) {
        const index = chapters.findIndex(c => c.chapter_id === chapterId)
        if (index !== -1) {
          chapters[index] = { ...chapters[index], ...updatedChapter }
          courseChapters.value.set(courseId, chapters)
          if (currentChapters.value === chapters) {
            currentChapters.value = [...chapters]
          }
          break
        }
      }

      return updatedChapter
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Aktualisieren des Kapitels'
      console.error('Failed to update chapter:', err)
      throw err
    }
  }

  /**
   * Delete chapter (cascades to lessons)
   */
  const deleteChapter = async (chapterId: string, reason?: string): Promise<void> => {
    try {
      await adminApi.adminDeleteChapter(chapterId, reason)

      for (const [courseId, chapters] of courseChapters.value.entries()) {
        const filtered = chapters.filter(c => c.chapter_id !== chapterId)
        if (filtered.length !== chapters.length) {
          courseChapters.value.set(courseId, filtered)
          if (currentChapters.value === chapters) {
            currentChapters.value = filtered
          }
          break
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Löschen des Kapitels'
      console.error('Failed to delete chapter:', err)
      throw err
    }
  }

  /**
   * Reorder chapters in a course
   */
  const reorderChapters = async (courseId: number, chapterIds: string[]): Promise<void> => {
    try {
      await adminApi.adminReorderChapters(courseId, chapterIds)

      const chapters = courseChapters.value.get(courseId)
      if (chapters) {
        const reordered = chapterIds
          .map(id => chapters.find(c => c.chapter_id === id))
          .filter(c => c !== undefined) as AdminChapter[]

        courseChapters.value.set(courseId, reordered)
        currentChapters.value = reordered
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Neu-Sortieren der Kapitel'
      console.error('Failed to reorder chapters:', err)
      throw err
    }
  }

  /**
   * Load category tree
   */
  const loadCategoryTree = async (activeOnly: boolean = true, forceReload: boolean = false): Promise<void> => {
    if (categoriesLoaded.value && !forceReload) return

    loading.value = true
    error.value = null

    try {
      const result = await adminApi.adminGetCategoriesTree(activeOnly)
      categoryTree.value = result.tree?.categories || result.tree || []
      categoriesLoaded.value = true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kategorien'
      console.error('Failed to load category tree:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Load flat list of categories
   */
  const loadCategories = async (params?: adminApi.CategoryFilterParams): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const categories = await adminApi.adminGetCategories(params)
      categoriesFlat.value = categories
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Laden der Kategorien'
      console.error('Failed to load categories:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Find category by ID (from tree or flat list)
   */
  const findCategoryById = (categoryId: number): Category | CategoryTreeNode | null => {
    const flatCategory = categoriesFlat.value.find(c => c.category_id === categoryId)
    if (flatCategory) return flatCategory

    function searchTree(nodes: CategoryTreeNode[]): CategoryTreeNode | null {
      for (const node of nodes) {
        if (node.category_id === categoryId) return node
        if (node.children.length > 0) {
          const found = searchTree(node.children)
          if (found) return found
        }
      }
      return null
    }

    return searchTree(categoryTree.value)
  }

  /**
   * Create a new category
   */
  const createCategory = async (categoryData: any): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await adminApi.adminCreateCategory(categoryData)
      categoriesLoaded.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Erstellen der Kategorie'
      console.error('Failed to create category:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Update an existing category
   */
  const updateCategory = async (categoryId: number, categoryData: any): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await adminApi.adminUpdateCategory(categoryId, categoryData)
      categoriesLoaded.value = false
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Fehler beim Aktualisieren der Kategorie'
      console.error('Failed to update category:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete a category
   */
  const deleteCategory = async (categoryId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await adminApi.adminDeleteCategory(categoryId)
      categoriesLoaded.value = false
    } catch (err: any) {
      const errorMessage = err.response?.data?.message ||
                          err.response?.data?.error ||
                          'Fehler beim Löschen der Kategorie'
      error.value = errorMessage
      console.error('Failed to delete category:', err)
      const customError = new Error(errorMessage)
      throw customError
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    courses, coursesTotal, coursesPage, coursesLimit, coursesTotalPages, courseFilters,
    courseChapters, currentChapters,
    categoryTree, categoriesFlat, categoriesLoaded,
    loading, error,

    // Actions - Courses
    loadCourses, getCourseDetail, createCourse, updateCourse,
    publishCourse, unpublishCourse, archiveCourse, unarchiveCourse,
    deleteCourse, permanentDeleteCourse,

    // Actions - Chapters
    loadCourseChapters, createChapter, updateChapter, deleteChapter, reorderChapters,

    // Actions - Categories
    loadCategoryTree, loadCategories, findCategoryById,
    createCategory, updateCategory, deleteCategory
  }
})
