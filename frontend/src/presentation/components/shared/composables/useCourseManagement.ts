/**
 * useCourseManagement Composable
 * ===============================
 * Course CRUD operations, categories, profiles, and AI analysis
 */
import { ref, readonly } from 'vue'
import { useI18n } from 'vue-i18n'
import http from '@/application/services/api/system'

// ============================================================================
// Types
// ============================================================================

export interface Category {
  category_id: number
  name: string
  parent_id?: number | null
}

export interface Profile {
  key: string
  name: string
  is_default: boolean
}

export interface NewCourseData {
  title: string
  description?: string
  language: string
  level: string
  categoryId: number | null
  profileKey: string
  files: File[]
}

export interface AIAnalysisResult {
  title: string
  description: string
  suggested_category_id: number | null
  suggested_profile_key: string
}

// ============================================================================
// Composable
// ============================================================================

export function useCourseManagement() {
  const { t } = useI18n()

  // ==========================================================================
  // State
  // ==========================================================================

  const availableCategories = ref<Category[]>([])
  const availableProfiles = ref<Profile[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // ==========================================================================
  // Methods - Loading
  // ==========================================================================

  async function loadCategories(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response = await http.get('/categories')

      if (response.data.success) {
        availableCategories.value = response.data.data || []
      } else {
        throw new Error('Failed to load categories')
      }
    } catch (err: any) {
      console.error('Load categories error:', err)
      error.value = err.message || 'Failed to load categories'
      availableCategories.value = []
    } finally {
      isLoading.value = false
    }
  }

  async function loadProfiles(): Promise<void> {
    try {
      isLoading.value = true
      error.value = null

      const response = await http.get('/admin/ai/profiles')

      if (response.data.success) {
        availableProfiles.value = response.data.data || []
      } else {
        throw new Error('Failed to load AI profiles')
      }
    } catch (err: any) {
      console.error('Load profiles error:', err)
      error.value = err.message || 'Failed to load AI profiles'
      availableProfiles.value = []
    } finally {
      isLoading.value = false
    }
  }

  // ==========================================================================
  // Methods - Course CRUD
  // ==========================================================================

  async function createCourse(courseData: NewCourseData): Promise<string | null> {
    try {
      isLoading.value = true
      error.value = null

      const formData = new FormData()
      formData.append('title', courseData.title)
      if (courseData.description) {
        formData.append('description', courseData.description)
      }
      formData.append('language', courseData.language)
      formData.append('level', courseData.level)
      if (courseData.categoryId) {
        formData.append('category_id', courseData.categoryId.toString())
      }
      formData.append('profile_key', courseData.profileKey)

      // Attach files
      courseData.files.forEach((file, index) => {
        formData.append(`files[${index}]`, file)
      })

      const response = await http.post('/admin/courses', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.success) {
        const newCourseId = response.data.data?.course_id
        return newCourseId || null
      } else {
        throw new Error(response.data.error?.message || 'Failed to create course')
      }
    } catch (err: any) {
      console.error('Create course error:', err)
      error.value =
        err.response?.data?.error?.message ||
        err.message ||
        'Failed to create course'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function createChapter(courseId: string, title?: string): Promise<string | null> {
    try {
      isLoading.value = true
      error.value = null

      const response = await http.post(`/admin/courses/${courseId}/chapters`, {
        title: title || t('panel.courses.newChapter'),
        order_index: 0 // Will be auto-calculated by backend
      })

      if (response.data.success) {
        return response.data.data?.chapter_id || null
      } else {
        throw new Error(response.data.error?.message || 'Failed to create chapter')
      }
    } catch (err: any) {
      console.error('Create chapter error:', err)
      error.value =
        err.response?.data?.error?.message ||
        err.message ||
        'Failed to create chapter'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function deleteCourse(courseId: string): Promise<boolean> {
    try {
      isLoading.value = true
      error.value = null

      const response = await http.delete(`/admin/courses/${courseId}`)

      return response.data.success || false
    } catch (err: any) {
      console.error('Delete course error:', err)
      error.value =
        err.response?.data?.error?.message ||
        err.message ||
        'Failed to delete course'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // ==========================================================================
  // Methods - AI Analysis
  // ==========================================================================

  async function analyzeFilesWithAI(files: File[]): Promise<AIAnalysisResult | null> {
    try {
      isLoading.value = true
      error.value = null

      const formData = new FormData()
      files.forEach((file, index) => {
        formData.append(`files[${index}]`, file)
      })

      const response = await http.post('/admin/ai/analyze-course-files', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      if (response.data.success) {
        const data = response.data.data
        return {
          title: data.title || '',
          description: data.description || '',
          suggested_category_id: data.suggested_category_id || null,
          suggested_profile_key: data.suggested_profile_key || 'standard'
        }
      } else {
        throw new Error(response.data.error?.message || 'AI analysis failed')
      }
    } catch (err: any) {
      console.error('AI analysis error:', err)
      error.value =
        err.response?.data?.error?.message ||
        err.message ||
        'AI analysis failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // ==========================================================================
  // Methods - Helpers
  // ==========================================================================

  function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  function getCategoryName(categoryId: number): string {
    const category = availableCategories.value.find(c => c.category_id === categoryId)
    return category?.name || ''
  }

  function getProfileName(profileKey: string): string {
    const profile = availableProfiles.value.find(p => p.key === profileKey)
    return profile?.name || profileKey
  }

  function getDefaultProfile(): Profile | null {
    return availableProfiles.value.find(p => p.is_default) || null
  }

  // ==========================================================================
  // Methods - Reset
  // ==========================================================================

  function clearError(): void {
    error.value = null
  }

  function reset(): void {
    availableCategories.value = []
    availableProfiles.value = []
    isLoading.value = false
    error.value = null
  }

  // ==========================================================================
  // Return
  // ==========================================================================

  return {
    // State (readonly)
    availableCategories: readonly(availableCategories),
    availableProfiles: readonly(availableProfiles),
    isLoading: readonly(isLoading),
    error: readonly(error),

    // Methods - Loading
    loadCategories,
    loadProfiles,

    // Methods - Course CRUD
    createCourse,
    createChapter,
    deleteCourse,

    // Methods - AI Analysis
    analyzeFilesWithAI,

    // Methods - Helpers
    formatFileSize,
    getCategoryName,
    getProfileName,
    getDefaultProfile,

    // Methods - Reset
    clearError,
    reset
  }
}
