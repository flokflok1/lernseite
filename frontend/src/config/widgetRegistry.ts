/**
 * LernsystemX - Widget Registry
 *
 * Central registry of all available dashboard widgets
 * Defines which widgets exist and their properties
 */

import type { WidgetDefinition } from '@/types/widgets'

// ============================================================================
// Widget Definitions
// ============================================================================

export const WIDGET_DEFINITIONS: WidgetDefinition[] = [
  // -------------------------------------------------------------------------
  // 1. Welcome Widget
  // -------------------------------------------------------------------------
  {
    id: 'welcome',
    type: 'welcome',
    title: 'Willkommen',
    description: 'Persönliche Begrüßung mit Benutzerinformationen',
    icon: '👋',
    defaultSize: 'large',
    minWidth: 1,
    minHeight: 1,
    configurable: false,
    defaultOrder: 1,
    defaultVisible: true
  },

  // -------------------------------------------------------------------------
  // 2. Profile Summary Widget
  // -------------------------------------------------------------------------
  {
    id: 'profile-summary',
    type: 'profile-summary',
    title: 'Mein Profil',
    description: 'Kompakte Profilübersicht mit wichtigen Informationen',
    icon: '👤',
    defaultSize: 'medium',
    minWidth: 1,
    minHeight: 1,
    configurable: false,
    defaultOrder: 2,
    defaultVisible: true
  },

  // -------------------------------------------------------------------------
  // 3. Plan & Tokens Widget
  // -------------------------------------------------------------------------
  {
    id: 'plan-tokens',
    type: 'plan-tokens',
    title: 'Abo & KI',
    description: 'Abonnement-Status und Token-Guthaben',
    icon: '💎',
    defaultSize: 'medium',
    minWidth: 1,
    minHeight: 1,
    premiumOnly: false, // Free users can see their plan status
    configurable: true,
    defaultOrder: 3,
    defaultVisible: true
  },

  // -------------------------------------------------------------------------
  // 4. Enrolled Courses Widget
  // -------------------------------------------------------------------------
  {
    id: 'enrolled-courses',
    type: 'enrolled-courses',
    title: 'Meine Kurse',
    description: 'Liste der eingeschriebenen Kurse mit Fortschritt',
    icon: '📚',
    defaultSize: 'large',
    minWidth: 2,
    minHeight: 2,
    configurable: true,
    defaultOrder: 4,
    defaultVisible: true
  },

  // -------------------------------------------------------------------------
  // 5. Courses Progress Widget
  // -------------------------------------------------------------------------
  {
    id: 'courses-progress',
    type: 'courses-progress',
    title: 'Lernfortschritt',
    description: 'Aggregierte Statistiken über deinen Lernfortschritt',
    icon: '📈',
    defaultSize: 'medium',
    minWidth: 1,
    minHeight: 1,
    configurable: true,
    defaultOrder: 5,
    defaultVisible: true
  },

  // -------------------------------------------------------------------------
  // 6. Organisation Overview Widget (Teacher/Admin Only)
  // -------------------------------------------------------------------------
  {
    id: 'org-overview',
    type: 'org-overview',
    title: 'Organisation',
    description: 'Übersicht über deine Organisation (nur für Lehrer/Admins)',
    icon: '🏢',
    defaultSize: 'medium',
    minWidth: 1,
    minHeight: 1,
    orgOnly: true, // Only for school_admin, company_admin
    teacherOnly: false, // Also allow teachers
    rolesAllowed: ['teacher', 'school_admin', 'company_admin', 'admin'],
    configurable: true,
    defaultOrder: 6,
    defaultVisible: true
  }
]

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get widget definition by ID
 */
export const getWidgetDefinition = (widgetId: string): WidgetDefinition | undefined => {
  return WIDGET_DEFINITIONS.find(w => w.id === widgetId)
}

/**
 * Get all widgets available for a specific role
 */
export const getWidgetsForRole = (
  role: string,
  isPremium: boolean = false
): WidgetDefinition[] => {
  return WIDGET_DEFINITIONS.filter(widget => {
    // Check premium requirement
    if (widget.premiumOnly && !isPremium) {
      return false
    }

    // Check role-specific requirements
    if (widget.rolesAllowed && widget.rolesAllowed.length > 0) {
      return widget.rolesAllowed.includes(role)
    }

    // Check org-only widgets
    if (widget.orgOnly) {
      const orgRoles = ['school_admin', 'company_admin', 'admin']
      return orgRoles.includes(role)
    }

    // Check teacher-only widgets
    if (widget.teacherOnly) {
      const teacherRoles = ['teacher', 'school_admin', 'company_admin', 'admin']
      return teacherRoles.includes(role)
    }

    // Check creator-only widgets
    if (widget.creatorOnly) {
      const creatorRoles = ['creator', 'teacher', 'school_admin', 'company_admin', 'admin']
      return creatorRoles.includes(role)
    }

    // Widget is available to all
    return true
  })
}

/**
 * Check if a specific widget is available for a role
 */
export const isWidgetAvailableForRole = (
  widgetId: string,
  role: string,
  isPremium: boolean = false
): boolean => {
  const widget = getWidgetDefinition(widgetId)
  if (!widget) return false

  const availableWidgets = getWidgetsForRole(role, isPremium)
  return availableWidgets.some(w => w.id === widgetId)
}
