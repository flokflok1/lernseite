/**
 * LernsystemX - Widget System Types
 *
 * TypeScript types and interfaces for the configurable widget-dashboard system
 */

// ============================================================================
// Widget Types
// ============================================================================

export type WidgetType =
  | 'welcome'
  | 'profile-summary'
  | 'plan-tokens'
  | 'enrolled-courses'
  | 'courses-progress'
  | 'org-overview'
  | 'activity'

export type WidgetSize = 'small' | 'medium' | 'large' | 'full'

// ============================================================================
// Widget Definition
// ============================================================================

/**
 * Widget Definition - Static blueprint for a widget type
 */
export interface WidgetDefinition {
  /** Unique widget identifier */
  id: string

  /** Widget type */
  type: WidgetType

  /** Display title */
  title: string

  /** Widget description (for config panel) */
  description?: string

  /** Icon class (optional) */
  icon?: string

  /** Default size */
  defaultSize?: WidgetSize

  /** Minimum grid width (1-12) */
  minWidth?: number

  /** Minimum grid height */
  minHeight?: number

  /** Roles allowed to see this widget (empty = all) */
  rolesAllowed?: string[]

  /** Premium-only widget */
  premiumOnly?: boolean

  /** Creator-only widget */
  creatorOnly?: boolean

  /** Teacher-only widget */
  teacherOnly?: boolean

  /** Organisation admin only */
  orgOnly?: boolean

  /** Widget supports configuration */
  configurable?: boolean

  /** Default order in layout */
  defaultOrder?: number

  /** Default visibility */
  defaultVisible?: boolean
}

// ============================================================================
// Widget Instance
// ============================================================================

/**
 * Widget Instance - User-specific instance of a widget
 */
export interface DashboardWidgetInstance {
  /** Unique instance ID (userId-widgetId) */
  instanceId: string

  /** Reference to widget definition ID */
  widgetId: string

  /** Display order (lower = earlier) */
  order: number

  /** Visibility toggle */
  visible: boolean

  /** Widget-specific configuration */
  config?: Record<string, any>

  /** Grid position (for advanced layouts) */
  position?: {
    row?: number
    col?: number
    width?: number
    height?: number
  }
}

// ============================================================================
// Dashboard Layout
// ============================================================================

/**
 * Dashboard Layout - Complete user dashboard configuration
 */
export interface DashboardLayout {
  /** User ID this layout belongs to */
  userId: number

  /** User role (for filtering) */
  role: string

  /** List of widget instances */
  widgets: DashboardWidgetInstance[]

  /** Preset ID (if using a preset) */
  presetId?: string

  /** Last updated timestamp */
  updatedAt?: string

  /** Layout version (for migration) */
  version?: number
}

// ============================================================================
// Widget Props
// ============================================================================

/**
 * Base props for all widget components
 */
export interface BaseWidgetProps {
  /** Widget instance data */
  instance: DashboardWidgetInstance

  /** Widget definition */
  definition: WidgetDefinition

  /** Compact mode (for smaller viewports) */
  compact?: boolean
}

// ============================================================================
// Widget Data Context
// ============================================================================

/**
 * Data context passed to widgets
 * Contains all dashboard data to avoid duplicate API calls
 */
export interface WidgetDataContext {
  profile?: any
  tokenBalance?: any
  subscription?: any
  enrolledCourses?: any[]
  organisation?: any
  loading?: boolean
  error?: string | null
}
