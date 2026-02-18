import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/modules/core/auth.store'
import { useGamificationStore } from '@/application/stores/modules/system/gamification.store'
import * as tokensApi from '@/application/services/api/panel-user'
import * as subscriptionsApi from '@/application/services/api/panel-user'
import * as coursesApi from '@/application/services/api/panel-editor'
import type { TokenBalanceResponse } from '@/application/services/api/panel-user'
import type { SubscriptionResponse } from '@/application/services/api/panel-user'
import type { EnrolledCourse } from '@/application/services/api/panel-editor'

export interface DashboardTab {
  id: string
  label: string
  icon: string
}

/**
 * Composable for managing dashboard state, data loading, and computed values.
 *
 * Encapsulates all API calls (tokens, subscription, courses), gamification
 * initialization, and derived values like progress and course helpers.
 */
export function useDashboard() {
  const { t, locale } = useI18n()
  const authStore = useAuthStore()
  const gamificationStore = useGamificationStore()

  // State
  const loading = ref(true)
  const error = ref('')
  const activeTab = ref('quests')
  const tokenBalance = ref<TokenBalanceResponse | null>(null)
  const subscription = ref<SubscriptionResponse | null>(null)
  const enrolledCourses = ref<EnrolledCourse[]>([])

  // Tab Configuration
  const tabs = computed<DashboardTab[]>(() => {
    void locale.value // Trigger reactivity on language change
    return [
      { id: 'quests', label: t('dashboard.tab_quests'), icon: '\uD83D\uDCDC' },
      { id: 'skills', label: t('dashboard.tab_skills'), icon: '\uD83C\uDF1F' },
      { id: 'courses', label: t('dashboard.tab_courses'), icon: '\uD83D\uDCDA' }
    ]
  })

  // Computed
  const fullName = computed<string>(() => {
    const user = authStore.user
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`
    }
    return user?.first_name || t('dashboard.adventurer')
  })

  const totalProgress = computed<number>(() => {
    if (enrolledCourses.value.length === 0) return 0
    const sum = enrolledCourses.value.reduce((acc, course) => acc + (course.progress || 0), 0)
    return Math.round(sum / enrolledCourses.value.length)
  })

  const completedLessonsCount = computed<number>(() => {
    return enrolledCourses.value.reduce((acc, course) => {
      const progress = course.progress || 0
      const estimatedLessons = Math.floor(progress / 10)
      return acc + estimatedLessons
    }, 0)
  })

  // Methods
  function getCourseIcon(course: EnrolledCourse): string {
    const icons = ['\uD83D\uDCD8', '\uD83D\uDCD7', '\uD83D\uDCD9', '\uD83D\uDCD5', '\uD83D\uDCD3']
    const index = course.course_id?.charCodeAt(0) % icons.length || 0
    return icons[index]
  }

  function getQuestXp(course: EnrolledCourse): number {
    const baseXp = 50
    const progress = course.progress || 0
    if (progress >= 80) return 150
    if (progress >= 50) return 100
    return baseXp
  }

  function buildProgressMap(courses: EnrolledCourse[]): Record<string, number> {
    const map: Record<string, number> = {}
    courses.forEach(course => {
      if (course.course_id) {
        map[course.course_id] = course.progress || 0
      }
    })
    return map
  }

  /**
   * Load all dashboard data from APIs in parallel.
   * Handles partial failures gracefully -- individual API errors
   * do not prevent the rest of the dashboard from rendering.
   */
  async function loadDashboardData(): Promise<void> {
    loading.value = true
    error.value = ''

    try {
      if (!authStore.profile) {
        await authStore.loadProfile()
      }

      const [tokensResponse, subscriptionResponse, coursesResponse] = await Promise.allSettled([
        tokensApi.getMyTokens(),
        subscriptionsApi.getMySubscription(),
        coursesApi.getMyEnrolledCourses({ per_page: 20 })
      ])

      if (tokensResponse.status === 'fulfilled') {
        tokenBalance.value = tokensResponse.value
      } else {
        console.error('Failed to load tokens:', tokensResponse.reason)
      }

      if (subscriptionResponse.status === 'fulfilled') {
        subscription.value = subscriptionResponse.value
      } else {
        console.error('Failed to load subscription:', subscriptionResponse.reason)
      }

      if (coursesResponse.status === 'fulfilled') {
        enrolledCourses.value = coursesResponse.value.items
      } else {
        console.error('Failed to load courses:', coursesResponse.reason)
      }

      gamificationStore.loadFromProfile({
        profile: authStore.profile,
        courses: enrolledCourses.value,
        progress: buildProgressMap(enrolledCourses.value)
      })
    } catch (err: any) {
      error.value = err.response?.data?.message || t('dashboard.load_error')
      console.error('Dashboard error:', err)
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    loading,
    error,
    activeTab,
    tokenBalance,
    subscription,
    enrolledCourses,

    // Computed
    tabs,
    fullName,
    totalProgress,
    completedLessonsCount,

    // Methods
    getCourseIcon,
    getQuestXp,
    loadDashboardData,

    // Stores (exposed for template access)
    authStore,
    gamificationStore
  }
}
