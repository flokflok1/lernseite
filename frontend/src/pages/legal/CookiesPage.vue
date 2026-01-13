<template>
  <div class="min-h-screen bg-[var(--color-bg)]">
    <!-- Header -->
    <header class="bg-[var(--color-surface)] border-b border-[var(--color-border)]">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <router-link
          to="/"
          class="inline-flex items-center text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] mb-4"
        >
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          {{ $t('legal.backToHome') }}
        </router-link>
        <h1 class="text-3xl font-bold text-[var(--color-text-primary)]">
          {{ $t('legal.cookies.title') }}
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          {{ $t('legal.cookies.subtitle') }}
        </p>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="prose prose-lg max-w-none text-[var(--color-text-primary)]">

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.cookies.whatAreCookies') }}</h2>
          <p>{{ $t('legal.cookies.whatAreCookiesText') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.cookies.whichCookies') }}</h2>

          <!-- Notwendige Cookies -->
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-6 mb-4 border border-[var(--color-border)]">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
              <h3 class="text-lg font-medium m-0">{{ $t('legal.cookies.necessary.title') }}</h3>
              <span class="ml-auto text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded">
                {{ $t('legal.cookies.necessary.alwaysActive') }}
              </span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-3">
              {{ $t('legal.cookies.necessary.description') }}
            </p>
            <div class="bg-[var(--color-surface)] rounded p-3 text-sm">
              <table class="w-full">
                <thead>
                  <tr class="text-left text-[var(--color-text-tertiary)]">
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.cookie') }}</th>
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.purpose') }}</th>
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.duration') }}</th>
                  </tr>
                </thead>
                <tbody class="text-[var(--color-text-secondary)]">
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_session</td>
                    <td class="py-1">{{ $t('legal.cookies.necessary.session') }}</td>
                    <td class="py-1">{{ $t('legal.cookies.necessary.duration.session') }}</td>
                  </tr>
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_auth</td>
                    <td class="py-1">{{ $t('legal.cookies.necessary.auth') }}</td>
                    <td class="py-1">{{ $t('legal.cookies.necessary.duration.days7') }}</td>
                  </tr>
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_csrf</td>
                    <td class="py-1">{{ $t('legal.cookies.necessary.csrf') }}</td>
                    <td class="py-1">{{ $t('legal.cookies.necessary.duration.session') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Funktionale Cookies -->
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-6 mb-4 border border-[var(--color-border)]">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                <svg class="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                </svg>
              </div>
              <h3 class="text-lg font-medium m-0">{{ $t('legal.cookies.functional.title') }}</h3>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-3">
              {{ $t('legal.cookies.functional.description') }}
            </p>
            <div class="bg-[var(--color-surface)] rounded p-3 text-sm">
              <table class="w-full">
                <thead>
                  <tr class="text-left text-[var(--color-text-tertiary)]">
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.cookie') }}</th>
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.purpose') }}</th>
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.duration') }}</th>
                  </tr>
                </thead>
                <tbody class="text-[var(--color-text-secondary)]">
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_theme</td>
                    <td class="py-1">{{ $t('legal.cookies.functional.theme') }}</td>
                    <td class="py-1">{{ $t('legal.cookies.functional.duration.year1') }}</td>
                  </tr>
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_lang</td>
                    <td class="py-1">{{ $t('legal.cookies.functional.language') }}</td>
                    <td class="py-1">{{ $t('legal.cookies.functional.duration.year1') }}</td>
                  </tr>
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_sidebar</td>
                    <td class="py-1">{{ $t('legal.cookies.functional.sidebar') }}</td>
                    <td class="py-1">{{ $t('legal.cookies.functional.duration.days30') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Analytische Cookies -->
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-6 mb-4 border border-[var(--color-border)]">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <h3 class="text-lg font-medium m-0">{{ $t('legal.cookies.analytics.title') }}</h3>
              <span class="ml-auto text-xs bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded">
                {{ $t('legal.cookies.analytics.optional') }}
              </span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-3">
              {{ $t('legal.cookies.analytics.description') }}
            </p>
            <div class="bg-[var(--color-surface)] rounded p-3 text-sm">
              <table class="w-full">
                <thead>
                  <tr class="text-left text-[var(--color-text-tertiary)]">
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.cookie') }}</th>
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.purpose') }}</th>
                    <th class="pb-2">{{ $t('legal.cookies.tableHeaders.duration') }}</th>
                  </tr>
                </thead>
                <tbody class="text-[var(--color-text-secondary)]">
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_analytics</td>
                    <td class="py-1">{{ $t('legal.cookies.analytics.stats') }}</td>
                    <td class="py-1">{{ $t('legal.cookies.analytics.duration.days90') }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.cookies.manage') }}</h2>
          <p>{{ $t('legal.cookies.manageText') }}</p>
          <ul>
            <li><strong>Chrome:</strong> {{ $t('legal.cookies.browsers.chrome') }}</li>
            <li><strong>Firefox:</strong> {{ $t('legal.cookies.browsers.firefox') }}</li>
            <li><strong>Safari:</strong> {{ $t('legal.cookies.browsers.safari') }}</li>
            <li><strong>Edge:</strong> {{ $t('legal.cookies.browsers.edge') }}</li>
          </ul>
          <p class="mt-4">
            <strong>{{ $t('legal.placeholderNotice') }}</strong> {{ $t('legal.cookies.manageNote') }}
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.cookies.settings') }}</h2>
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-6 border border-[var(--color-border)]">
            <p class="text-[var(--color-text-secondary)] mb-4">
              {{ $t('legal.cookies.settingsText') }}
            </p>
            <button
              @click="openCookieSettings"
              class="btn btn-primary"
            >
              {{ $t('legal.cookies.openSettings') }}
            </button>
          </div>
        </section>

        <section>
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.cookies.moreInfo') }}</h2>
          <p>
            {{ $t('legal.cookies.moreInfoText') }}
            <router-link to="/legal/privacy" class="text-[var(--color-accent)] hover:underline">
              {{ $t('legal.privacy.title') }}
            </router-link>.
          </p>
          <p class="text-sm text-[var(--color-text-tertiary)] mt-4">
            {{ $t('legal.lastUpdated', { date: currentDate }) }}
          </p>
        </section>
      </div>
    </main>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Footer } from '@/components/base/layout'

const { t, locale } = useI18n()

const currentDate = computed(() => {
  const localeMap: Record<string, string> = {
    de: 'de-DE',
    en: 'en-US',
    pl: 'pl-PL'
  }
  return new Date().toLocaleDateString(localeMap[locale.value] || 'de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
})

const openCookieSettings = () => {
  // TODO: Implement cookie consent modal
  alert(t('common.loading'))
}
</script>
