<!--
  PHASE G1: RPG Dashboard - Vollwertiges Gamification Dashboard

  Analysis Summary:
  - Original dashboard displayed: Welcome, Profile Summary, Plan/Tokens, Enrolled Courses, Progress, Org Overview
  - All original data (profile, tokens, subscription, courses) is preserved and passed to RPG components
  - Widget system is replaced with RPG-styled components
  - Gamification layer (XP, Level, Quests, Skills) added on top of existing functionality

  Components:
  - RpgCharacterCard: Shows user stats, level, XP, base stats
  - RpgQuestList: Shows quests generated from enrolled courses
  - RpgSkillTree: Shows unlockable skills that affect XP/Gold gain
  - RpgInventorySummary: Shows subscription, tokens, and premium features as items

  Data Flow:
  - Profile data -> Character name, role, avatar
  - Enrolled courses -> Quests generation
  - Subscription -> Membership tier in inventory
  - Token balance -> Resources in inventory
-->

<template>
  <div class="rpg-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="header-title">
          Willkommen zurueck, {{ authStore.user?.first_name }}!
        </h1>
        <p class="header-subtitle">Deine Lern-Abenteuer warten auf dich.</p>
      </div>

      <!-- Quick Stats Bar -->
      <div class="quick-stats-bar">
        <div class="quick-stat">
          <span class="quick-stat-icon">📈</span>
          <span class="quick-stat-value">Level {{ gamificationStore.stats.level }}</span>
        </div>
        <div class="quick-stat">
          <span class="quick-stat-icon">📚</span>
          <span class="quick-stat-value">{{ enrolledCourses.length }} Kurse</span>
        </div>
        <div class="quick-stat">
          <span class="quick-stat-icon">🎯</span>
          <span class="quick-stat-value">{{ gamificationStore.activeQuests.length }} Quests</span>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <span class="loading-text">Lade dein Abenteuer...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ error }}</span>
      <button class="retry-btn" @click="loadDashboardData">Erneut versuchen</button>
    </div>

    <!-- Main Dashboard Grid -->
    <div v-else class="dashboard-grid">
      <!-- Left Column: Character Card -->
      <aside class="dashboard-sidebar">
        <RpgCharacterCard
          :name="fullName"
          :role="authStore.userRole"
          :avatar-url="authStore.profile?.avatar_url"
        />
      </aside>

      <!-- Center Column: Main Content -->
      <main class="dashboard-main">
        <!-- Tab Navigation -->
        <div class="tab-navigation">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="tab-btn"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <span class="tab-icon">{{ tab.icon }}</span>
            <span class="tab-label">{{ tab.label }}</span>
          </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content">
          <!-- Quests Tab -->
          <Transition name="fade" mode="out-in">
            <RpgQuestList v-if="activeTab === 'quests'" key="quests" />
          </Transition>

          <!-- Skillbaum Tab -->
          <Transition name="fade" mode="out-in">
            <RpgSkillTree v-if="activeTab === 'skills'" key="skills" />
          </Transition>

          <!-- Kurse Tab (Legacy Progress View) -->
          <Transition name="fade" mode="out-in">
            <div v-if="activeTab === 'courses'" key="courses" class="courses-section">
              <div class="section-header">
                <h3 class="section-title">
                  <span class="section-icon">📚</span>
                  Meine Kurse
                </h3>
                <span class="course-count">{{ enrolledCourses.length }} eingeschrieben</span>
              </div>

              <div v-if="enrolledCourses.length === 0" class="empty-courses">
                <span class="empty-icon">📭</span>
                <p class="empty-text">Du hast noch keine Kurse.</p>
                <p class="empty-hint">Schreibe dich in Kurse ein, um Quests freizuschalten!</p>
              </div>

              <div v-else class="courses-list">
                <div
                  v-for="course in enrolledCourses"
                  :key="course.course_id"
                  class="course-card"
                >
                  <div class="course-icon">
                    {{ getCourseIcon(course) }}
                  </div>
                  <div class="course-info">
                    <h4 class="course-title">{{ course.title || course.name }}</h4>
                    <p class="course-description">{{ course.description?.substring(0, 80) }}...</p>
                    <div class="course-progress">
                      <div class="progress-bar">
                        <div
                          class="progress-fill"
                          :style="{ width: `${course.progress || 0}%` }"
                        ></div>
                      </div>
                      <span class="progress-text">{{ course.progress || 0 }}%</span>
                    </div>
                  </div>
                  <div class="course-xp">
                    <span class="xp-badge">+{{ getQuestXp(course) }} XP</span>
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </main>

      <!-- Right Column: Inventory -->
      <aside class="dashboard-inventory">
        <RpgInventorySummary
          :subscription="subscription"
          :token-balance="tokenBalance"
          :courses-count="enrolledCourses.length"
          :completed-lessons="completedLessonsCount"
        />

        <!-- Learning Progress Widget (legacy data) -->
        <div class="progress-widget">
          <h4 class="widget-title">
            <span class="widget-icon">📊</span>
            Lernfortschritt
          </h4>
          <div class="progress-stats">
            <div class="progress-stat">
              <span class="stat-value">{{ totalProgress }}%</span>
              <span class="stat-label">Gesamt</span>
            </div>
            <div class="progress-stat">
              <span class="stat-value">{{ completedLessonsCount }}</span>
              <span class="stat-label">Lektionen</span>
            </div>
          </div>
          <div class="overall-progress-bar">
            <div
              class="overall-progress-fill"
              :style="{ width: `${totalProgress}%` }"
            ></div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/store/auth.store'
import { useGamificationStore } from '@/store/gamification.store'
import * as tokensApi from '@/api/tokens.api'
import * as subscriptionsApi from '@/api/subscriptions.api'
import * as coursesApi from '@/api/courses.api'
import type { TokenBalanceResponse } from '@/api/tokens.api'
import type { SubscriptionResponse } from '@/api/subscriptions.api'
import type { EnrolledCourse } from '@/api/courses.api'

// Components
import RpgCharacterCard from '@/components/gamification/RpgCharacterCard.vue'
import RpgQuestList from '@/components/gamification/RpgQuestList.vue'
import RpgSkillTree from '@/components/gamification/RpgSkillTree.vue'
import RpgInventorySummary from '@/components/gamification/RpgInventorySummary.vue'

// ============================================================================
// Stores
// ============================================================================

const authStore = useAuthStore()
const gamificationStore = useGamificationStore()

// ============================================================================
// State
// ============================================================================

const loading = ref(true)
const error = ref('')
const activeTab = ref('quests')

const tokenBalance = ref<TokenBalanceResponse | null>(null)
const subscription = ref<SubscriptionResponse | null>(null)
const enrolledCourses = ref<EnrolledCourse[]>([])

// ============================================================================
// Tab Configuration
// ============================================================================

const tabs = [
  { id: 'quests', label: 'Lern-Quests', icon: '📜' },
  { id: 'skills', label: 'Skillbaum', icon: '🌟' },
  { id: 'courses', label: 'Meine Kurse', icon: '📚' }
]

// ============================================================================
// Computed
// ============================================================================

const fullName = computed(() => {
  const user = authStore.user
  if (user?.first_name && user?.last_name) {
    return `${user.first_name} ${user.last_name}`
  }
  return user?.first_name || 'Abenteurer'
})

const totalProgress = computed(() => {
  if (enrolledCourses.value.length === 0) return 0
  const sum = enrolledCourses.value.reduce((acc, course) => acc + (course.progress || 0), 0)
  return Math.round(sum / enrolledCourses.value.length)
})

const completedLessonsCount = computed(() => {
  // Estimate from progress - would be more accurate with actual lesson data
  return enrolledCourses.value.reduce((acc, course) => {
    const progress = course.progress || 0
    const estimatedLessons = Math.floor(progress / 10) // Rough estimate
    return acc + estimatedLessons
  }, 0)
})

// ============================================================================
// Methods
// ============================================================================

const getCourseIcon = (course: EnrolledCourse): string => {
  // Could be based on category or custom field
  const icons = ['📘', '📗', '📙', '📕', '📓']
  const index = course.course_id?.charCodeAt(0) % icons.length || 0
  return icons[index]
}

const getQuestXp = (course: EnrolledCourse): number => {
  // XP based on course complexity/progress
  const baseXp = 50
  const progress = course.progress || 0
  if (progress >= 80) return 150
  if (progress >= 50) return 100
  return baseXp
}

/**
 * Load all dashboard data from APIs
 */
const loadDashboardData = async () => {
  loading.value = true
  error.value = ''

  try {
    // Load profile if not cached
    if (!authStore.profile) {
      await authStore.loadProfile()
    }

    // Load all dashboard data in parallel
    const [tokensResponse, subscriptionResponse, coursesResponse] = await Promise.allSettled([
      tokensApi.getMyTokens(),
      subscriptionsApi.getMySubscription(),
      coursesApi.getMyEnrolledCourses({ per_page: 20 })
    ])

    // Handle tokens
    if (tokensResponse.status === 'fulfilled') {
      tokenBalance.value = tokensResponse.value
    } else {
      console.error('Failed to load tokens:', tokensResponse.reason)
    }

    // Handle subscription
    if (subscriptionResponse.status === 'fulfilled') {
      subscription.value = subscriptionResponse.value
    } else {
      console.error('Failed to load subscription:', subscriptionResponse.reason)
    }

    // Handle courses
    if (coursesResponse.status === 'fulfilled') {
      enrolledCourses.value = coursesResponse.value.items
    } else {
      console.error('Failed to load courses:', coursesResponse.reason)
    }

    // Initialize gamification from loaded data
    gamificationStore.loadFromProfile({
      profile: authStore.profile,
      courses: enrolledCourses.value,
      progress: buildProgressMap(enrolledCourses.value)
    })

  } catch (err: any) {
    error.value = err.response?.data?.message || 'Fehler beim Laden der Dashboard-Daten'
    console.error('Dashboard error:', err)
  } finally {
    loading.value = false
  }
}

/**
 * Build progress map from enrolled courses
 */
const buildProgressMap = (courses: EnrolledCourse[]): Record<string, number> => {
  const map: Record<string, number> = {}
  courses.forEach(course => {
    if (course.course_id) {
      map[course.course_id] = course.progress || 0
    }
  })
  return map
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadDashboardData()
})

// PHASE G1 - RPG Dashboard implemented
// All original dashboard data preserved (profile, tokens, subscription, courses)
// Added gamification layer with XP, Level, Quests, Skills, and Inventory
</script>

<style scoped>
.rpg-dashboard {
  min-height: 100%;
  padding: 24px;
}

/* Header */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-content {
  flex: 1;
  min-width: 200px;
}

.header-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.header-subtitle {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin: 0;
}

.quick-stats-bar {
  display: flex;
  gap: 12px;
}

.quick-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
}

.quick-stat-icon {
  font-size: 16px;
}

.quick-stat-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  gap: 16px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 15px;
  color: var(--color-text-secondary);
}

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
}

.error-icon {
  font-size: 40px;
}

.error-text {
  font-size: 15px;
  color: var(--color-text-secondary);
}

.retry-btn {
  padding: 8px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  opacity: 0.9;
}

/* Dashboard Grid */
.dashboard-grid {
  display: grid;
  grid-template-columns: 280px 1fr 300px;
  gap: 24px;
  align-items: start;
}

/* Sidebar */
.dashboard-sidebar {
  position: sticky;
  top: 24px;
}

/* Main Content */
.dashboard-main {
  min-height: 400px;
}

/* Tab Navigation */
.tab-navigation {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  padding: 4px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: var(--color-text-primary);
  background: var(--color-background);
}

.tab-btn.active {
  color: white;
  background: var(--color-primary);
}

.tab-icon {
  font-size: 16px;
}

/* Tab Content */
.tab-content {
  min-height: 300px;
}

/* Courses Section */
.courses-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(
    145deg,
    var(--color-background) 0%,
    var(--color-surface) 100%
  );
  border-bottom: 1px solid var(--color-border);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.section-icon {
  font-size: 18px;
}

.course-count {
  font-size: 13px;
  color: var(--color-text-muted);
}

.empty-courses {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: var(--color-text-muted);
  margin: 0;
}

.courses-list {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.course-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.course-card:hover {
  border-color: var(--color-primary);
  transform: translateX(4px);
}

.course-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  border-radius: 10px;
  font-size: 24px;
  flex-shrink: 0;
}

.course-info {
  flex: 1;
  min-width: 0;
}

.course-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.course-description {
  font-size: 12px;
  color: var(--color-text-muted);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.course-progress {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: var(--color-surface);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary) 0%, #818cf8 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  min-width: 36px;
}

.course-xp {
  flex-shrink: 0;
}

.xp-badge {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, var(--color-background) 100%);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #8b5cf6;
}

/* Inventory Sidebar */
.dashboard-inventory {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 24px;
}

/* Progress Widget */
.progress-widget {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 16px;
}

.widget-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 12px 0;
}

.widget-icon {
  font-size: 16px;
}

.progress-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.progress-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.stat-label {
  font-size: 11px;
  color: var(--color-text-muted);
}

.overall-progress-bar {
  height: 8px;
  background: var(--color-background);
  border-radius: 4px;
  overflow: hidden;
}

.overall-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e 0%, #4ade80 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr 280px;
  }

  .dashboard-sidebar {
    grid-row: 1;
    grid-column: 1 / -1;
    position: static;
  }

  .dashboard-main {
    grid-column: 1;
  }

  .dashboard-inventory {
    position: static;
  }
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-sidebar,
  .dashboard-main,
  .dashboard-inventory {
    grid-column: 1;
  }
}

@media (max-width: 640px) {
  .rpg-dashboard {
    padding: 16px;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .quick-stats-bar {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .header-title {
    font-size: 22px;
  }

  .tab-navigation {
    overflow-x: auto;
    gap: 4px;
  }

  .tab-btn {
    padding: 10px 12px;
    font-size: 13px;
    white-space: nowrap;
  }

  .tab-label {
    display: none;
  }

  .course-card {
    flex-wrap: wrap;
  }

  .course-xp {
    width: 100%;
    margin-top: 8px;
  }
}
</style>
