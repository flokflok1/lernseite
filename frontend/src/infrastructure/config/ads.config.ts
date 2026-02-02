/**
 * Ads Configuration - Phase C2.4: Werbungsslots vorbereiten
 *
 * Zentrale Konfiguration für Werbeeinblendungen.
 * Feature-Flags und Slot-Definitionen ohne Vendor-spezifische Logik.
 */

// Feature Flags
export const ADS_CONFIG = {
  // Master-Schalter für alle Werbung
  enabled: false,

  // Zeige Development-Placeholders
  showDevPlaceholders: true,

  // Globale Einstellungen
  settings: {
    // Mindestabstand zwischen Ads (in Sekunden)
    minIntervalSeconds: 30,

    // Maximale Anzahl Ads pro Seite
    maxAdsPerPage: 3,

    // Werbung für Premium-User deaktivieren
    disableForPremium: true,

    // Werbung deaktivieren wenn Kurs kostenpflichtig
    disableForPaidCourses: true
  }
}

// Slot-Definitionen
export type AdSlotType = 'banner' | 'sidebar' | 'inline' | 'interstitial' | 'leaderboard'

export interface AdSlotConfig {
  id: string
  type: AdSlotType
  name: string
  description: string
  dimensions: {
    width: number | string
    height: number
  }
  positions: string[]  // Erlaubte Positionen im Layout
  priority: number     // Höhere Priorität = wichtiger
  enabled: boolean
}

// Vordefinierte Slot-Konfigurationen
export const AD_SLOTS: Record<string, AdSlotConfig> = {
  // Header Banner
  headerBanner: {
    id: 'header-banner',
    type: 'leaderboard',
    name: 'Header Leaderboard',
    description: 'Großes Banner am Seitenanfang',
    dimensions: { width: 970, height: 90 },
    positions: ['header', 'top'],
    priority: 1,
    enabled: false
  },

  // Sidebar Ads
  sidebarTop: {
    id: 'sidebar-top',
    type: 'sidebar',
    name: 'Sidebar Top',
    description: 'Rechteckige Werbung oben in der Sidebar',
    dimensions: { width: 300, height: 250 },
    positions: ['sidebar'],
    priority: 2,
    enabled: false
  },

  sidebarBottom: {
    id: 'sidebar-bottom',
    type: 'sidebar',
    name: 'Sidebar Bottom',
    description: 'Rechteckige Werbung unten in der Sidebar',
    dimensions: { width: 300, height: 250 },
    positions: ['sidebar'],
    priority: 4,
    enabled: false
  },

  // Inline Content Ads
  inlineContent: {
    id: 'inline-content',
    type: 'inline',
    name: 'Inline Content',
    description: 'Werbung zwischen Content-Blöcken',
    dimensions: { width: '100%', height: 100 },
    positions: ['content'],
    priority: 3,
    enabled: false
  },

  // Lesson Ads (zwischen Lektionen)
  lessonInterstitial: {
    id: 'lesson-interstitial',
    type: 'inline',
    name: 'Lesson Interstitial',
    description: 'Werbung zwischen Lektionen in kostenlosen Kursen',
    dimensions: { width: '100%', height: 120 },
    positions: ['lesson'],
    priority: 2,
    enabled: false
  },

  // Footer Banner
  footerBanner: {
    id: 'footer-banner',
    type: 'banner',
    name: 'Footer Banner',
    description: 'Banner am Seitenende',
    dimensions: { width: 728, height: 90 },
    positions: ['footer', 'bottom'],
    priority: 5,
    enabled: false
  }
}

/**
 * Prüft ob Werbung für einen User angezeigt werden soll
 */
export function shouldShowAds(user: {
  isPremium?: boolean
  hasActiveSubscription?: boolean
} | null): boolean {
  // Wenn Ads global deaktiviert
  if (!ADS_CONFIG.enabled) {
    return ADS_CONFIG.showDevPlaceholders
  }

  // Kein User = zeige Werbung
  if (!user) {
    return true
  }

  // Premium-User sehen keine Werbung
  if (ADS_CONFIG.settings.disableForPremium && (user.isPremium || user.hasActiveSubscription)) {
    return false
  }

  return true
}

/**
 * Prüft ob Werbung für einen Kurs angezeigt werden soll
 */
export function shouldShowAdsForCourse(course: {
  price?: number
  ad_enabled?: boolean
} | null): boolean {
  if (!course) return true

  // Kostenpflichtige Kurse ohne Werbung
  if (ADS_CONFIG.settings.disableForPaidCourses && (course.price || 0) > 0) {
    return false
  }

  // Kurs-spezifische Einstellung
  if (course.ad_enabled === false) {
    return false
  }

  return true
}

/**
 * Holt die Konfiguration für einen Slot
 */
export function getSlotConfig(slotId: string): AdSlotConfig | null {
  return AD_SLOTS[slotId] || null
}

/**
 * Holt alle aktiven Slots für eine Position
 */
export function getActiveSlotsForPosition(position: string): AdSlotConfig[] {
  return Object.values(AD_SLOTS)
    .filter(slot => slot.enabled && slot.positions.includes(position))
    .sort((a, b) => a.priority - b.priority)
}
