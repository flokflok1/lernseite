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
          {{ $t('legal.terms.title') }}
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          {{ $t('legal.terms.subtitle') }}
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
              <strong>{{ $t('legal.placeholderNotice') }}</strong> {{ $t('legal.terms.placeholderText') }}
            </p>
          </div>
        </div>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.scope') }}</h2>
          <p>{{ $t('legal.terms.scopeText1') }}</p>
          <p>{{ $t('legal.terms.scopeText2') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.subject') }}</h2>
          <p>{{ $t('legal.terms.subjectText1') }}</p>
          <p>{{ $t('legal.terms.subjectText2') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.registration') }}</h2>
          <p>{{ $t('legal.terms.registrationText1') }}</p>
          <p>{{ $t('legal.terms.registrationText2') }}</p>
          <p>{{ $t('legal.terms.registrationText3') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.prices') }}</h2>
          <p>{{ $t('legal.terms.pricesText1') }}</p>
          <p>{{ $t('legal.terms.pricesText2') }}</p>
          <p>{{ $t('legal.terms.pricesText3') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.tokens') }}</h2>
          <p>{{ $t('legal.terms.tokensText1') }}</p>
          <p>{{ $t('legal.terms.tokensText2') }}</p>
          <p>{{ $t('legal.terms.tokensText3') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.copyright') }}</h2>
          <p>{{ $t('legal.terms.copyrightText1') }}</p>
          <p>{{ $t('legal.terms.copyrightText2') }}</p>
          <p>{{ $t('legal.terms.copyrightText3') }}</p>
          <p>
            {{ $t('legal.terms.copyrightText4') }}
            <router-link to="/legal/content-usage" class="text-[var(--color-accent)] hover:underline">
              {{ $t('legal.terms.contentUsageTerms') }}
            </router-link>.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.termination') }}</h2>
          <p>{{ $t('legal.terms.terminationText1') }}</p>
          <p>{{ $t('legal.terms.terminationText2') }}</p>
          <p>{{ $t('legal.terms.terminationText3') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.liability') }}</h2>
          <p>{{ $t('legal.terms.liabilityText1') }}</p>
          <p>{{ $t('legal.terms.liabilityText2') }}</p>
          <p>{{ $t('legal.terms.liabilityText3') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.dataProtection') }}</h2>
          <p>
            {{ $t('legal.terms.dataProtectionText') }}
            <router-link to="/legal/privacy" class="text-[var(--color-accent)] hover:underline">
              {{ $t('legal.terms.privacyPolicy') }}
            </router-link>.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.changes') }}</h2>
          <p>{{ $t('legal.terms.changesText1') }}</p>
          <p>{{ $t('legal.terms.changesText2') }}</p>
          <p>{{ $t('legal.terms.changesText3') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.terms.finalProvisions') }}</h2>
          <p>{{ $t('legal.terms.finalProvisionsText1') }}</p>
          <p>{{ $t('legal.terms.finalProvisionsText2') }}</p>
          <p>{{ $t('legal.terms.finalProvisionsText3') }}</p>
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
