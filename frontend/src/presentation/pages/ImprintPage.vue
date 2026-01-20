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
          {{ $t('legal.imprint.title') }}
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          {{ $t('legal.imprint.subtitle') }}
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
              <strong>{{ $t('legal.placeholderNotice') }}</strong> {{ $t('legal.imprint.placeholderText') }}
            </p>
          </div>
        </div>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.provider') }}</h2>
          <p>
            LernsystemX GmbH<br />
            Musterstraße 123<br />
            12345 Musterstadt<br />
            Deutschland
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.representedBy') }}</h2>
          <p>{{ $t('legal.imprint.managingDirector', { name: 'Max Mustermann' }) }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.contact') }}</h2>
          <p>
            {{ $t('legal.imprint.phone', { phone: '+49 (0) 123 456789' }) }}<br />
            {{ $t('legal.imprint.email', { email: 'info@lernsystemx.de' }) }}<br />
            {{ $t('legal.imprint.website', { website: 'www.lernsystemx.de' }) }}
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.registry') }}</h2>
          <p>
            {{ $t('legal.imprint.registryEntry') }}<br />
            {{ $t('legal.imprint.registryCourt', { court: 'Amtsgericht Musterstadt' }) }}<br />
            {{ $t('legal.imprint.registryNumber', { number: 'HRB 12345' }) }}
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.vatId') }}</h2>
          <p>
            {{ $t('legal.imprint.vatIdText') }}<br />
            DE 123456789
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.responsible') }}</h2>
          <p>
            Max Mustermann<br />
            Musterstraße 123<br />
            12345 Musterstadt
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.euDispute') }}</h2>
          <p>
            {{ $t('legal.imprint.euDisputeText') }}
            <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer" class="text-[var(--color-accent)] hover:underline">
              https://ec.europa.eu/consumers/odr/
            </a>
          </p>
          <p>{{ $t('legal.imprint.euDisputeEmail') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.consumerDispute') }}</h2>
          <p>{{ $t('legal.imprint.consumerDisputeText') }}</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.liability') }}</h2>
          <p>{{ $t('legal.imprint.liabilityText') }}</p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mb-4">{{ $t('legal.imprint.links') }}</h2>
          <p>{{ $t('legal.imprint.linksText') }}</p>
        </section>
      </div>
    </main>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Footer } from '@/presentation/components/base/layout'

useI18n()
</script>
