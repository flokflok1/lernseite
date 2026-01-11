// Base UI Components
export { default as Button } from './Button.vue'
export { default as Card } from './Card.vue'
export { default as Input } from './Input.vue'
export { default as Textarea } from './Textarea.vue'
export { default as Dropdown } from './Dropdown.vue'
export { default as Modal } from './Modal.vue'
export { default as Loader } from './Loader.vue'
export { default as Alert } from './Alert.vue'
export { default as ProgressBar } from './ProgressBar.vue'
export { default as Avatar } from './Avatar.vue'

// i18n Components
export { default as LanguageSelector } from './i18n/LanguageSelector.vue'

// Chart Components
export { BarChart, LineChart, AnalyticsKpiCard } from './charts'

// Layout Components
export { Footer, ProtectedContent } from './layout'

// Application Interface Components
export { Taskbar, MiniPreview, WindowComponent, DesktopLayer } from './application-interface'

// Audio Components
export { AudioRecorder } from './audio'

// Ads Components
export { AdSlot } from './ads'

// Dialog Components
export { DeleteConfirmModal, DialogManager, TaskManagerModal } from './dialogs'

// Widget Components
export {
  CoursesProgressWidget,
  EnrolledCoursesWidget,
  WelcomeWidget,
  PlanTokensWidget,
  OrgOverviewWidget,
  ProfileSummaryWidget
} from './widgets'
