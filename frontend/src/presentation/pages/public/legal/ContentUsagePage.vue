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
          {{ $t('legal.contentUsage.title') }}
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          {{ $t('legal.contentUsage.subtitle') }}
        </p>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="prose prose-lg max-w-none">

        <!-- Erlaubte Nutzung -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-[var(--color-text-primary)] m-0">
              {{ $t('legal.contentUsage.allowedTitle') }}
            </h2>
          </div>

          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <ul class="space-y-4 text-[var(--color-text-primary)]">
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.allowed.personalLearning') }}</strong> – {{ $t('legal.contentUsage.allowed.personalLearningDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.allowed.teaching') }}</strong> – {{ $t('legal.contentUsage.allowed.teachingDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.allowed.quotes') }}</strong> – {{ $t('legal.contentUsage.allowed.quotesDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.allowed.screenshots') }}</strong> – {{ $t('legal.contentUsage.allowed.screenshotsDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.allowed.offline') }}</strong> – {{ $t('legal.contentUsage.allowed.offlineDesc') }}</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- Verbotene Nutzung -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-full bg-red-100 dark:bg-red-900 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-[var(--color-text-primary)] m-0">
              {{ $t('legal.contentUsage.forbiddenTitle') }}
            </h2>
          </div>

          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <ul class="space-y-4 text-[var(--color-text-primary)]">
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.forbidden.commercial') }}</strong> – {{ $t('legal.contentUsage.forbidden.commercialDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.forbidden.duplication') }}</strong> – {{ $t('legal.contentUsage.forbidden.duplicationDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.forbidden.protection') }}</strong> – {{ $t('legal.contentUsage.forbidden.protectionDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.forbidden.scraping') }}</strong> – {{ $t('legal.contentUsage.forbidden.scrapingDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.forbidden.sharing') }}</strong> – {{ $t('legal.contentUsage.forbidden.sharingDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>{{ $t('legal.contentUsage.forbidden.upload') }}</strong> – {{ $t('legal.contentUsage.forbidden.uploadDesc') }}</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- Rechtliche Folgen -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-full bg-amber-100 dark:bg-amber-900 flex items-center justify-center">
              <svg class="w-6 h-6 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-[var(--color-text-primary)] m-0">
              {{ $t('legal.contentUsage.consequencesTitle') }}
            </h2>
          </div>

          <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-6">
            <p class="text-[var(--color-text-primary)] mb-4">
              {{ $t('legal.contentUsage.consequencesIntro') }}
            </p>
            <ul class="space-y-3 text-[var(--color-text-primary)]">
              <li class="flex items-start gap-3">
                <span class="text-amber-600 font-bold">1.</span>
                <span><strong>{{ $t('legal.contentUsage.consequences.ban') }}</strong> – {{ $t('legal.contentUsage.consequences.banDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-amber-600 font-bold">2.</span>
                <span><strong>{{ $t('legal.contentUsage.consequences.civil') }}</strong> – {{ $t('legal.contentUsage.consequences.civilDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-amber-600 font-bold">3.</span>
                <span><strong>{{ $t('legal.contentUsage.consequences.criminal') }}</strong> – {{ $t('legal.contentUsage.consequences.criminalDesc') }}</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-amber-600 font-bold">4.</span>
                <span><strong>{{ $t('legal.contentUsage.consequences.costs') }}</strong> – {{ $t('legal.contentUsage.consequences.costsDesc') }}</span>
              </li>
            </ul>
          </div>
        </section>

        <!-- Lizenzanfragen -->
        <section class="mb-12">
          <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 class="text-2xl font-bold text-[var(--color-text-primary)] m-0">
              {{ $t('legal.contentUsage.licenseTitle') }}
            </h2>
          </div>

          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <p class="text-[var(--color-text-primary)] mb-4">
              {{ $t('legal.contentUsage.licenseIntro') }}
            </p>
            <ul class="space-y-2 text-[var(--color-text-primary)] mb-6">
              <li>• <strong>{{ $t('legal.contentUsage.licenses.education') }}</strong> – {{ $t('legal.contentUsage.licenses.educationDesc') }}</li>
              <li>• <strong>{{ $t('legal.contentUsage.licenses.enterprise') }}</strong> – {{ $t('legal.contentUsage.licenses.enterpriseDesc') }}</li>
              <li>• <strong>{{ $t('legal.contentUsage.licenses.reseller') }}</strong> – {{ $t('legal.contentUsage.licenses.resellerDesc') }}</li>
              <li>• <strong>{{ $t('legal.contentUsage.licenses.whiteLabel') }}</strong> – {{ $t('legal.contentUsage.licenses.whiteLabelDesc') }}</li>
            </ul>

            <div class="flex flex-col sm:flex-row gap-4">
              <a
                href="mailto:license@lernsystemx.de"
                class="btn btn-primary inline-flex items-center justify-center"
              >
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                license@lernsystemx.de
              </a>
              <router-link
                to="/contact?subject=license"
                class="btn btn-outline inline-flex items-center justify-center"
              >
                {{ $t('legal.contentUsage.requestLicense') }}
              </router-link>
            </div>
          </div>
        </section>

        <!-- Stand der Information -->
        <section class="text-sm text-[var(--color-text-tertiary)] border-t border-[var(--color-border)] pt-6">
          <p>{{ $t('legal.lastUpdated', { date: currentDate }) }}</p>
          <p>{{ $t('legal.version', { version: '1.0' }) }}</p>
          <p class="mt-2">
            {{ $t('legal.partOfTerms') }}
            <router-link to="/legal/terms" class="text-[var(--color-accent)] hover:underline">
              {{ $t('legal.generalTerms') }}
            </router-link>.
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
