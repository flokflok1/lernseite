/**
 * useCourseSelector Composable
 * ============================
 * Encapsulates filtering, categorization, and click-outside logic
 * for the CourseSelector dropdown.
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Course } from '../../composables/useAiStudioState'

interface UseCourseSelector {
  selectorRef: ReturnType<typeof ref<HTMLElement | null>>
  dropdownOpen: ReturnType<typeof ref<boolean>>
  categoryPopupOpen: ReturnType<typeof ref<boolean>>
  searchQuery: ReturnType<typeof ref<string>>
  selectedCategoryFilter: ReturnType<typeof ref<string | null>>
  selectedCourseTitle: ReturnType<typeof computed<string>>
  filteredCourses: ReturnType<typeof computed<Course[]>>
  coursesByCategory: ReturnType<typeof computed<{
    groups: Record<string, Course[]>
    uncategorized: Course[]
    sortedCategories: string[]
  }>>
  allCategories: ReturnType<typeof computed<string[]>>
  recentCourses: ReturnType<typeof computed<Course[]>>
  categoryFilterLabel: ReturnType<typeof computed<string>>
  handleSelectCourse: (courseId: string, emit: (e: 'select', courseId: string) => void) => void
  getCategoryCount: (categoryName: string) => number
  getUncategorizedCount: () => number
}

export function useCourseSelector(
  courses: () => Course[],
  selectedCourseId: () => string | null
): UseCourseSelector {
  const { t } = useI18n()

  const selectorRef = ref<HTMLElement | null>(null)
  const dropdownOpen = ref(false)
  const categoryPopupOpen = ref(false)
  const searchQuery = ref('')
  const selectedCategoryFilter = ref<string | null>(null)

  const selectedCourseTitle = computed((): string => {
    const id = selectedCourseId()
    if (!id) return ''
    const course = courses().find(c => c.course_id === id)
    return course?.title || ''
  })

  const filteredCourses = computed((): Course[] => {
    let filtered = courses()

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(course =>
        course.title.toLowerCase().includes(query) ||
        course.description?.toLowerCase().includes(query)
      )
    }

    if (selectedCategoryFilter.value) {
      if (selectedCategoryFilter.value === '__uncategorized__') {
        filtered = filtered.filter(course => !course.category_name)
      } else {
        filtered = filtered.filter(course =>
          course.category_name === selectedCategoryFilter.value
        )
      }
    }

    return filtered
  })

  const coursesByCategory = computed(() => {
    const groups: Record<string, Course[]> = {}
    const uncategorized: Course[] = []

    for (const course of filteredCourses.value) {
      if (!course.category_name) {
        uncategorized.push(course)
      } else {
        if (!groups[course.category_name]) {
          groups[course.category_name] = []
        }
        groups[course.category_name].push(course)
      }
    }

    const sortedCategories = Object.keys(groups).sort()

    return { groups, uncategorized, sortedCategories }
  })

  const allCategories = computed((): string[] => {
    const categories = new Set<string>()
    for (const course of courses()) {
      if (course.category_name) {
        categories.add(course.category_name)
      }
    }
    return Array.from(categories).sort()
  })

  const recentCourses = computed((): Course[] => {
    // TODO: Implement recent courses logic (last 5 edited)
    return []
  })

  const categoryFilterLabel = computed((): string => {
    if (!selectedCategoryFilter.value) {
      return t('panel.aiStudio.allCategories')
    }
    if (selectedCategoryFilter.value === '__uncategorized__') {
      return t('panel.aiStudio.noCategory')
    }
    return selectedCategoryFilter.value
  })

  function handleSelectCourse(courseId: string, emit: (e: 'select', courseId: string) => void): void {
    emit('select', courseId)
    dropdownOpen.value = false
    categoryPopupOpen.value = false
    searchQuery.value = ''
  }

  function getCategoryCount(categoryName: string): number {
    return courses().filter(c => c.category_name === categoryName).length
  }

  function getUncategorizedCount(): number {
    return courses().filter(c => !c.category_name).length
  }

  function handleClickOutside(event: MouseEvent): void {
    if (selectorRef.value && !selectorRef.value.contains(event.target as Node)) {
      dropdownOpen.value = false
      categoryPopupOpen.value = false
    }
  }

  onMounted(() => {
    document.addEventListener('click', handleClickOutside)
  })

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })

  return {
    selectorRef,
    dropdownOpen,
    categoryPopupOpen,
    searchQuery,
    selectedCategoryFilter,
    selectedCourseTitle,
    filteredCourses,
    coursesByCategory,
    allCategories,
    recentCourses,
    categoryFilterLabel,
    handleSelectCourse,
    getCategoryCount,
    getUncategorizedCount
  }
}
