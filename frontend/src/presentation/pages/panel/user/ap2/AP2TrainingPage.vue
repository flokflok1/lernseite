<template>
  <div class="ap2-shell">
    <header class="ap2-header">
      <div class="ap2-brand">
        <span class="ap2-brand-badge">{{ t('ap2Trainer.shell.badge') }}</span>
        <h1 class="ap2-brand-title">{{ t('ap2Trainer.shell.title') }}</h1>
      </div>

      <nav class="ap2-nav" :aria-label="t('ap2Trainer.shell.title')">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="ap2-nav-link"
          active-class="ap2-nav-link-active"
        >
          <span class="ap2-nav-icon">{{ link.icon }}</span>
          <span>{{ link.label }}</span>
          <span v-if="link.badge" class="ap2-nav-badge">{{ link.badge }}</span>
        </RouterLink>
      </nav>

      <div class="ap2-countdowns">
        <div class="ap2-cd" :class="{ 'ap2-cd-urgent': daysToWiso <= 7 }">
          <div class="ap2-cd-num">{{ daysToWiso }}</div>
          <div class="ap2-cd-label">{{ t('ap2Trainer.shell.countdown.wiso') }}</div>
        </div>
        <div class="ap2-cd" :class="{ 'ap2-cd-urgent': daysToAp2 <= 7 }">
          <div class="ap2-cd-num">{{ daysToAp2 }}</div>
          <div class="ap2-cd-label">{{ t('ap2Trainer.shell.countdown.ap2') }}</div>
        </div>
      </div>
    </header>

    <main class="ap2-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useExamCountdown, useAp2Stats } from './composables'

const { t } = useI18n()
const { daysToWiso, daysToAp2 } = useExamCountdown()
const { reviewQueueCount } = useAp2Stats()

const navLinks = computed(() => [
  { to: '/ap2-training/dashboard',  icon: '📊', label: t('ap2Trainer.shell.nav.dashboard'),  badge: '' },
  { to: '/ap2-training/modules',    icon: '📚', label: 'Module',                              badge: 'NEU' },
  { to: '/ap2-training/study',      icon: '🎯', label: t('ap2Trainer.shell.nav.study'),      badge: '' },
  { to: '/ap2-training/review',     icon: '🔁', label: t('ap2Trainer.shell.nav.review'),     badge: reviewQueueCount.value > 0 ? String(reviewQueueCount.value) : '' },
  { to: '/ap2-training/exam',       icon: '📝', label: t('ap2Trainer.shell.nav.exam'),       badge: '' },
  { to: '/ap2-training/cheatsheet', icon: '📋', label: t('ap2Trainer.shell.nav.cheatsheet'), badge: '' },
  { to: '/ap2-training/anlagen',    icon: '📎', label: t('ap2Trainer.shell.nav.anlagen'),    badge: '' },
  { to: '/ap2-training/preferences', icon: '🎛', label: t('ap2Trainer.shell.nav.prefs'),     badge: '' },
])
</script>

<style scoped>
.ap2-shell { max-width: 1280px; margin: 0 auto; padding: 16px; font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; }
.ap2-header { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 24px; background: linear-gradient(135deg, #1e3a5f 0%, #1e1b4b 50%, #2d1b69 100%); border: 1px solid #3730a3; border-radius: 14px; padding: 14px 20px; margin-bottom: 16px; }
.ap2-brand-badge { display: inline-block; padding: 3px 10px; border-radius: 999px; background: rgba(99, 102, 241, 0.2); color: #a5b4fc; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; margin-bottom: 4px; }
.ap2-brand-title { color: #fff; font-size: 22px; font-weight: 800; margin: 0; }
.ap2-nav { display: flex; gap: 4px; background: rgba(0, 0, 0, 0.2); padding: 4px; border-radius: 10px; flex-wrap: wrap; }
.ap2-nav-link { display: inline-flex; align-items: center; gap: 6px; padding: 7px 12px; border-radius: 8px; color: #cbd5e1; font-size: 13px; font-weight: 600; text-decoration: none; transition: all .15s; }
.ap2-nav-link:hover { background: rgba(255, 255, 255, 0.06); color: #fff; }
.ap2-nav-link-active { background: rgba(99, 102, 241, 0.3); color: #fff; box-shadow: 0 0 0 1px rgba(165, 180, 252, 0.4); }
.ap2-nav-icon { font-size: 15px; }
.ap2-nav-badge { background: #ef4444; color: #fff; border-radius: 999px; padding: 1px 6px; font-size: 10px; font-weight: 700; min-width: 16px; text-align: center; }
.ap2-countdowns { display: flex; gap: 8px; }
.ap2-cd { text-align: center; background: rgba(99, 102, 241, 0.15); border: 1px solid #4338ca; border-radius: 10px; padding: 6px 14px; min-width: 78px; }
.ap2-cd-urgent { background: rgba(239, 68, 68, 0.18); border-color: #dc2626; }
.ap2-cd-num { font-size: 26px; font-weight: 800; color: #818cf8; line-height: 1; }
.ap2-cd-urgent .ap2-cd-num { color: #f87171; }
.ap2-cd-label { font-size: 10px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
.ap2-content { min-height: 500px; }
</style>
