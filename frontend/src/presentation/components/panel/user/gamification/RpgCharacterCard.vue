<!--
  RPG Character Card Component
  Phase G1: RPG Dashboard - Charakterkarte

  Features:
  - Avatar mit Initials/Placeholder
  - Name & Klasse
  - Level & XP-Balken
  - Gold & Skillpunkte
  - Base Stats (Staerke, Intelligenz, Ausdauer)
-->

<template>
  <div class="rpg-character-card">
    <!-- Character Header -->
    <div class="character-header">
      <!-- Avatar -->
      <div class="avatar-container">
        <div class="avatar" :style="avatarStyle">
          <span v-if="!hasAvatar" class="avatar-initials">{{ initials }}</span>
        </div>
        <div class="level-badge">{{ stats.level }}</div>
      </div>

      <!-- Name & Class -->
      <div class="character-info">
        <h3 class="character-name">{{ displayName }}</h3>
        <div class="character-class">
          <span class="class-icon">{{ characterClass.icon }}</span>
          <span class="class-name">{{ characterClass.name }}</span>
        </div>
        <div class="character-role">{{ roleLabel }}</div>
      </div>
    </div>

    <!-- XP Bar -->
    <div class="xp-section">
      <div class="xp-header">
        <span class="xp-label">{{ $t('dashboard.gamification.experience') }}</span>
        <span class="xp-value">{{ stats.xp }} / {{ stats.xpToNext }} XP</span>
      </div>
      <div class="xp-bar-container">
        <div class="xp-bar" :style="{ width: `${xpProgress}%` }">
          <div class="xp-bar-glow"></div>
        </div>
      </div>
    </div>

    <!-- Resources -->
    <div class="resources-row">
      <div class="resource gold">
        <span class="resource-icon">💰</span>
        <span class="resource-value">{{ stats.gold }}</span>
        <span class="resource-label">{{ $t('dashboard.gamification.gold') }}</span>
      </div>
      <div class="resource skill-points">
        <span class="resource-icon">⭐</span>
        <span class="resource-value">{{ stats.skillPoints }}</span>
        <span class="resource-label">{{ $t('dashboard.gamification.skillPoints') }}</span>
      </div>
    </div>

    <!-- Stats (extracted sub-component) -->
    <RpgCharacterStats
      :baseStats="stats.baseStats"
      :totalStats="totalStats"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useGamificationStore } from '@/application/stores/modules/system/gamification.store'
import type { GamificationStats } from '@/application/stores/modules/system/gamification.store'
import RpgCharacterStats from './RpgCharacterStats.vue'

const { t } = useI18n()

// ============================================================================
// Props
// ============================================================================

interface Props {
  name?: string
  role?: string
  avatarUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
  name: 'Abenteurer',
  role: 'user',
  avatarUrl: ''
})

// ============================================================================
// Store
// ============================================================================

const gamificationStore = useGamificationStore()

// ============================================================================
// Computed
// ============================================================================

const stats = computed<GamificationStats>(() => gamificationStore.stats)
const xpProgress = computed(() => gamificationStore.xpProgress)
const totalStats = computed(() => gamificationStore.totalStats)
const characterClass = computed(() => gamificationStore.getCharacterClass)

const displayName = computed(() => props.name || 'Abenteurer')

const initials = computed(() => {
  const nameParts = displayName.value.split(' ')
  if (nameParts.length >= 2) {
    return `${nameParts[0][0]}${nameParts[1][0]}`.toUpperCase()
  }
  return displayName.value.substring(0, 2).toUpperCase()
})

const hasAvatar = computed(() => !!props.avatarUrl)

const avatarStyle = computed(() => {
  if (props.avatarUrl) {
    return {
      backgroundImage: `url(${props.avatarUrl})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
    }
  }
  return {}
})

const roleLabel = computed(() => {
  const roleMap: Record<string, string> = {
    admin: 'roleAdmin',
    teacher: 'roleTeacher',
    creator: 'roleCreator',
    premium: 'rolePremium',
    user: 'roleUser',
    free: 'roleUser',
    school: 'roleSchool',
    company: 'roleCompany'
  }
  const key = roleMap[props.role] || 'roleUser'
  return t(`dashboard.gamification.${key}`)
})

</script>

<style scoped>
.rpg-character-card {
  background: linear-gradient(
    145deg,
    var(--color-surface) 0%,
    var(--color-background) 100%
  );
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* Character Header */
.character-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.avatar-container {
  position: relative;
  flex-shrink: 0;
}

.avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark, #4338ca) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid var(--color-primary);
  box-shadow: 0 0 20px var(--color-primary-light, rgba(99, 102, 241, 0.3));
}

.avatar-initials {
  font-size: 24px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.level-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #1f2937;
  border: 2px solid var(--color-surface);
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
}

.character-info {
  flex: 1;
  min-width: 0;
}

.character-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
  line-height: 1.2;
}

.character-class {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 2px;
}

.class-icon {
  font-size: 16px;
}

.class-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary);
}

.character-role {
  font-size: 12px;
  color: var(--color-text-muted);
}

/* XP Section */
.xp-section {
  margin-bottom: 16px;
}

.xp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.xp-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.xp-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.xp-bar-container {
  height: 12px;
  background: var(--color-background);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.xp-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary) 0%, #818cf8 100%);
  border-radius: 6px;
  position: relative;
  transition: width 0.5s ease;
}

.xp-bar-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.3) 0%, transparent 100%);
  border-radius: 6px 6px 0 0;
}

/* Resources */
.resources-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}

.resource {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: var(--color-background);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.resource-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.resource-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.resource-label {
  font-size: 11px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.resource.gold {
  background: linear-gradient(145deg, rgba(251, 191, 36, 0.1) 0%, var(--color-background) 100%);
  border-color: rgba(251, 191, 36, 0.3);
}

.resource.skill-points {
  background: linear-gradient(145deg, rgba(139, 92, 246, 0.1) 0%, var(--color-background) 100%);
  border-color: rgba(139, 92, 246, 0.3);
}

/* Responsive */
@media (max-width: 640px) {
  .rpg-character-card {
    padding: 16px;
  }

  .avatar {
    width: 60px;
    height: 60px;
  }

  .avatar-initials {
    font-size: 20px;
  }

  .level-badge {
    width: 24px;
    height: 24px;
    font-size: 11px;
  }

  .character-name {
    font-size: 16px;
  }
}
</style>
