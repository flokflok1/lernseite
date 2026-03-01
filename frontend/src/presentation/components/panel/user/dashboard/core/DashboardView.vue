<!--
  RPG Dashboard View - Orchestrator

  Delegates data loading to useDashboard composable,
  and renders extracted sub-components for each section:
  - DashboardSkeleton: loading state
  - DashboardCoursesTab: enrolled courses list
  - DashboardProgressWidget: learning progress sidebar widget
-->

<template>
  <div class="rpg-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="header-title">
          {{ $t('dashboard.welcome_name', { name: authStore.fullName || authStore.user?.email?.split('@')[0] || '' }) }}
        </h1>
        <p class="header-subtitle">{{ $t('dashboard.subtitle') }}</p>
      </div>

      <!-- Quick Stats Bar -->
      <div class="quick-stats-bar">
        <div class="quick-stat">
          <span class="quick-stat-icon">📈</span>
          <span class="quick-stat-value">{{ $t('dashboard.level', { level: gamificationStore.stats.level }) }}</span>
        </div>
        <div class="quick-stat">
          <span class="quick-stat-icon">📚</span>
          <span class="quick-stat-value">{{ $t('dashboard.courses_count', { count: enrolledCourses.length }) }}</span>
        </div>
        <div class="quick-stat">
          <span class="quick-stat-icon">🎯</span>
          <span class="quick-stat-value">{{ $t('dashboard.quests_count', { count: gamificationStore.activeQuests.length }) }}</span>
        </div>
      </div>
    </div>

    <!-- Loading Skeleton -->
    <DashboardSkeleton v-if="loading" />

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ error }}</span>
      <button class="retry-btn" @click="loadDashboardData">{{ $t('dashboard.retry') }}</button>
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
          <Transition name="fade" mode="out-in">
            <RpgQuestList v-if="activeTab === 'quests'" key="quests" />
          </Transition>

          <Transition name="fade" mode="out-in">
            <RpgSkillTree v-if="activeTab === 'skills'" key="skills" />
          </Transition>

          <Transition name="fade" mode="out-in">
            <DashboardCoursesTab
              v-if="activeTab === 'courses'"
              key="courses"
              :courses="enrolledCourses"
              :get-course-icon="getCourseIcon"
              :get-quest-xp="getQuestXp"
              @navigate-courses="router.push('/courses')"
            />
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

        <DashboardProgressWidget
          :total-progress="totalProgress"
          :completed-lessons="completedLessonsCount"
        />
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import RpgCharacterCard from '@/presentation/components/panel/user/gamification/character/RpgCharacterCard.vue'
import RpgQuestList from '@/presentation/components/panel/user/gamification/quests/RpgQuestList.vue'
import RpgSkillTree from '@/presentation/components/panel/user/gamification/character/RpgSkillTree.vue'
import RpgInventorySummary from '@/presentation/components/panel/user/gamification/inventory/RpgInventorySummary.vue'

import DashboardSkeleton from '@/presentation/components/panel/user/dashboard/core/DashboardSkeleton.vue'
import DashboardCoursesTab from '@/presentation/components/panel/user/dashboard/tabs/DashboardCoursesTab.vue'
import DashboardProgressWidget from '@/presentation/components/panel/user/dashboard/tabs/DashboardProgressWidget.vue'
import { useDashboard } from '@/presentation/components/panel/user/dashboard/composables'

const router = useRouter()

const {
  loading,
  error,
  activeTab,
  tokenBalance,
  subscription,
  enrolledCourses,
  tabs,
  fullName,
  totalProgress,
  completedLessonsCount,
  getCourseIcon,
  getQuestXp,
  loadDashboardData,
  authStore,
  gamificationStore
} = useDashboard()

onMounted(() => {
  loadDashboardData()
})
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

/* Inventory Sidebar */
.dashboard-inventory {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 24px;
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
}
</style>
