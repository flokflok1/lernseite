// Core
export { useAuthStore } from './modules/core/auth.store'
export { useAppStore } from './modules/core/app.store'

// Admin
export { usePanelStore, useAdminPanelStore } from './modules/admin/panel.store'
export { usePanelUsersStore } from './modules/admin/panel-users.store'
export { usePanelOrganisationsStore } from './modules/admin/panel-organisations.store'
export { usePanelCoursesStore } from './modules/admin/panel-courses.store'
export { usePanelAnalyticsStore } from './modules/admin/panel-analytics.store'
export { usePanelAIJobsStore } from './modules/admin/panel-ai-jobs.store'
export { useAdminStore } from './modules/admin/admin.store'

// Content
export { useCourseEditorStore } from './modules/content/courseEditor.store'
export { usePlayerStore } from './modules/content/player.store'

// Workspace
export { usePanelStore as useWorkspacePanelStore } from './modules/workspace/panel.store'

// Feature Flags
export { useFeatureFlagsStore } from './modules/feature-flags/feature-flags.store'

// Learning
export { useDashboardStore } from './modules/learning/dashboard.store'
export { useTutorStore } from './modules/learning/tutor.store'

// System
export { useGamificationStore } from './modules/system/gamification.store'

// UI
export { useAvatarStore } from './modules/ui/avatar.store'
export { useThemeStore } from './modules/ui/theme.store'
export { useWindowStore } from './modules/ui/window.store'
