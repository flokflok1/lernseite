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
          {{ $t('legal.privacy.title') }}
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          {{ $t('legal.privacy.subtitle') }}
        </p>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="prose prose-lg max-w-none text-[var(--color-text-primary)]">

        <!-- Hinweis: Platzhalter -->
        <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4 mb-8">
          <div class="flex items-start gap-3">
            <svg class="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <p class="text-sm text-amber-800 dark:text-amber-200 m-0">
              <strong>{{ $t('legal.placeholderNotice') }}</strong> {{ $t('legal.privacy.placeholderText') }}
            </p>
          </div>
        </div>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.privacy.overview') }}</h2>
          <h3 class="text-lg font-medium mb-2">{{ $t('legal.privacy.generalNotices') }}</h3>
          <p>{{ $t('legal.privacy.generalNoticesText') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.privacy.responsible') }}</h2>
          <p>
            LernsystemX GmbH<br />
            Musterstraße 123<br />
            12345 Musterstadt<br />
            E-Mail: datenschutz@lernsystemx.de
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.privacy.dataCollection') }}</h2>

          <h3 class="text-lg font-medium mb-2">{{ $t('legal.privacy.whoResponsible') }}</h3>
          <p>{{ $t('legal.privacy.whoResponsibleText') }}</p>

          <h3 class="text-lg font-medium mb-2 mt-4">{{ $t('legal.privacy.howCollect') }}</h3>
          <p>{{ $t('legal.privacy.howCollectText1') }}</p>
          <p>{{ $t('legal.privacy.howCollectText2') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.privacy.userAccount') }}</h2>
          <p>{{ $t('legal.privacy.userAccountIntro') }}</p>
          <ul>
            <li>{{ $t('legal.privacy.userData.registration') }}</li>
            <li>{{ $t('legal.privacy.userData.progress') }}</li>
            <li>{{ $t('legal.privacy.userData.results') }}</li>
            <li>{{ $t('legal.privacy.userData.usage') }}</li>
            <li>{{ $t('legal.privacy.userData.preferences') }}</li>
          </ul>
          <p>{{ $t('legal.privacy.userAccountLegal') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.privacy.aiServices') }}</h2>
          <p>{{ $t('legal.privacy.aiServicesIntro') }}</p>
          <ul>
            <li>{{ $t('legal.privacy.aiData.noPersonal') }}</li>
            <li>{{ $t('legal.privacy.aiData.anonymous') }}</li>
            <li>{{ $t('legal.privacy.aiData.gdpr') }}</li>
          </ul>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.privacy.cookies') }}</h2>
          <p>{{ $t('legal.privacy.cookiesText') }}</p>
          <p>{{ $t('legal.privacy.cookiesUsage') }}</p>
          <ul>
            <li><strong>{{ $t('legal.privacy.cookieTypes.necessary') }}</strong> – {{ $t('legal.privacy.cookieTypes.necessaryDesc') }}</li>
            <li><strong>{{ $t('legal.privacy.cookieTypes.functional') }}</strong> – {{ $t('legal.privacy.cookieTypes.functionalDesc') }}</li>
            <li><strong>{{ $t('legal.privacy.cookieTypes.analytics') }}</strong> – {{ $t('legal.privacy.cookieTypes.analyticsDesc') }}</li>
          </ul>
          <p>
            {{ $t('legal.privacy.cookiesMore') }}
            <router-link to="/legal/cookies" class="text-[var(--color-accent)] hover:underline">
              {{ $t('legal.privacy.cookiePolicy') }}
            </router-link>.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.privacy.rights') }}</h2>
          <p>{{ $t('legal.privacy.rightsIntro') }}</p>
          <ul>
            <li>{{ $t('legal.privacy.rightsList.access') }}</li>
            <li>{{ $t('legal.privacy.rightsList.rectification') }}</li>
            <li>{{ $t('legal.privacy.rightsList.erasure') }}</li>
            <li>{{ $t('legal.privacy.rightsList.restriction') }}</li>
            <li>{{ $t('legal.privacy.rightsList.objection') }}</li>
            <li>{{ $t('legal.privacy.rightsList.portability') }}</li>
          </ul>
          <p>
            {{ $t('legal.privacy.rightsContact') }}
            <a href="mailto:datenschutz@lernsystemx.de" class="text-[var(--color-accent)] hover:underline">
              datenschutz@lernsystemx.de
            </a>
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.privacy.security') }}</h2>
          <p>{{ $t('legal.privacy.securityText1') }}</p>
          <p>{{ $t('legal.privacy.securityText2') }}</p>
        </section>

        <section>
          <p class="text-sm text-[var(--color-text-tertiary)]">
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
import { Footer } from '@/presentation/components/shared/layout'

const { locale } = useI18n()

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
</script>
