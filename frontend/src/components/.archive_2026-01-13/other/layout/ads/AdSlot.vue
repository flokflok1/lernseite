<!--
  AdSlot Component - Phase C2.4: Werbungsslots vorbereiten

  Placeholder-Komponente für Werbeeinblendungen.
  Zeigt nur einen Placeholder an - keine echte Werbung implementiert.

  Features:
  - Verschiedene Slot-Typen (banner, sidebar, inline, interstitial)
  - Feature-Flag basierte Anzeige
  - Placeholder-Design für Entwicklung
  - Keine externe Ad-Vendor-Logik (wird später hinzugefügt)
-->

<template>
  <div
    v-if="showAd"
    :class="['ad-slot', `ad-slot--${type}`, { 'ad-slot--development': isDevelopment }]"
    :style="slotStyle"
  >
    <!-- Development Placeholder -->
    <div class="ad-placeholder">
      <div class="ad-placeholder__icon">{{ getIcon }}</div>
      <div class="ad-placeholder__info">
        <p class="ad-placeholder__type">{{ getTypeLabel }}</p>
        <p class="ad-placeholder__size">{{ getSizeLabel }}</p>
      </div>
      <div v-if="isDevelopment" class="ad-placeholder__badge">
        DEV
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Types
type AdSlotType = 'banner' | 'sidebar' | 'inline' | 'interstitial' | 'leaderboard'

interface Props {
  type?: AdSlotType
  position?: string
  fallback?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'banner',
  position: '',
  fallback: true
})

// Feature flags (will be loaded from config/API in production)
const adsEnabled = true  // Feature flag - set to false to hide all ads
const isDevelopment = true  // Show development placeholders

// Computed
const showAd = computed(() => {
  return adsEnabled && (isDevelopment || props.fallback)
})

const getIcon = computed(() => {
  const icons: Record<AdSlotType, string> = {
    banner: '🎯',
    sidebar: '📢',
    inline: '📄',
    interstitial: '🖥️',
    leaderboard: '🏆'
  }
  return icons[props.type] || '📢'
})

const getTypeLabel = computed(() => {
  const labels: Record<AdSlotType, string> = {
    banner: t('common.ads.bannerAd'),
    sidebar: t('common.ads.sidebarAd'),
    inline: t('common.ads.inlineAd'),
    interstitial: t('common.ads.interstitialAd'),
    leaderboard: t('common.ads.leaderboardAd')
  }
  return labels[props.type] || t('common.ads.adSlot')
})

const getSizeLabel = computed(() => {
  const sizes: Record<AdSlotType, string> = {
    banner: '728x90',
    sidebar: '300x250',
    inline: '100%x100',
    interstitial: '640x480',
    leaderboard: '970x90'
  }
  return sizes[props.type] || 'Auto'
})

const slotStyle = computed(() => {
  const styles: Record<AdSlotType, Record<string, string>> = {
    banner: {
      width: '100%',
      maxWidth: '728px',
      height: '90px'
    },
    sidebar: {
      width: '300px',
      height: '250px'
    },
    inline: {
      width: '100%',
      height: '100px'
    },
    interstitial: {
      width: '100%',
      maxWidth: '640px',
      height: '480px'
    },
    leaderboard: {
      width: '100%',
      maxWidth: '970px',
      height: '90px'
    }
  }
  return styles[props.type] || {}
})
</script>

<style scoped>
.ad-slot {
  margin: 1rem auto;
  border-radius: 8px;
  overflow: hidden;
  background-color: var(--color-surface, #f3f4f6);
  border: 2px dashed var(--color-border, #e5e7eb);
}

.ad-slot--development {
  border-color: var(--color-warning, #f59e0b);
  background-color: var(--color-warning-bg, #fef3c7);
}

.ad-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  position: relative;
}

.ad-placeholder__icon {
  font-size: 2rem;
  opacity: 0.5;
}

.ad-placeholder__info {
  text-align: left;
}

.ad-placeholder__type {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  margin: 0;
}

.ad-placeholder__size {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  opacity: 0.7;
  margin: 0;
}

.ad-placeholder__badge {
  position: absolute;
  top: 4px;
  right: 4px;
  padding: 2px 6px;
  font-size: 0.625rem;
  font-weight: 700;
  background-color: var(--color-warning, #f59e0b);
  color: white;
  border-radius: 4px;
}

/* Type-specific styles */
.ad-slot--banner {
  margin: 1rem auto;
}

.ad-slot--sidebar {
  margin: 0;
}

.ad-slot--inline {
  margin: 1.5rem 0;
}

.ad-slot--interstitial {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.ad-slot--leaderboard {
  margin: 1rem auto;
}
</style>
