<template>
  <footer class="bg-[var(--color-surface)] border-t border-[var(--color-border)] mt-auto">
    <!-- Main Footer Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Column 1: Legal Links -->
        <div>
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider mb-4">
            {{ $t('legal.footer.legalSection') }}
          </h3>
          <ul class="space-y-2">
            <li>
              <router-link
                to="/legal/imprint"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.imprint') }}
              </router-link>
            </li>
            <li>
              <router-link
                to="/legal/privacy"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.privacy') }}
              </router-link>
            </li>
            <li>
              <router-link
                to="/legal/terms"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.terms') }}
              </router-link>
            </li>
            <li>
              <router-link
                to="/legal/cookies"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.cookiePolicy') }}
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Column 2: Content Usage -->
        <div>
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider mb-4">
            {{ $t('legal.footer.usageSection') }}
          </h3>
          <ul class="space-y-2">
            <li>
              <router-link
                to="/legal/content-usage"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.contentUsage') }}
              </router-link>
            </li>
            <li>
              <router-link
                to="/legal/licensing"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.licenseRequests') }}
              </router-link>
            </li>
            <li>
              <a
                href="mailto:license@lernsystemx.de"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.commercialUse') }}
              </a>
            </li>
          </ul>
        </div>

        <!-- Column 3: Support & Social -->
        <div>
          <h3 class="text-sm font-semibold text-[var(--color-text-primary)] uppercase tracking-wider mb-4">
            {{ $t('legal.footer.supportSection') }}
          </h3>
          <ul class="space-y-2">
            <li>
              <router-link
                to="/support"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.contactSupport') }}
              </router-link>
            </li>
            <li>
              <router-link
                to="/help"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                {{ $t('legal.footer.helpCenter') }}
              </router-link>
            </li>
            <li>
              <a
                href="mailto:support@lernsystemx.de"
                class="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors"
              >
                support@lernsystemx.de
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- Security Notice -->
      <div class="mt-8 pt-6 border-t border-[var(--color-border)]">
        <div class="flex items-center justify-center gap-2 text-sm text-[var(--color-text-secondary)] bg-[var(--color-surface-secondary)] rounded-lg p-3">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 text-[var(--color-success)]"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fill-rule="evenodd"
              d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
              clip-rule="evenodd"
            />
          </svg>
          <span>
            <strong>{{ $t('legal.footer.securityNotice') }}</strong> –
            {{ $t('legal.footer.securityText') }}
          </span>
        </div>
      </div>
    </div>

    <!-- Copyright Bar -->
    <div class="bg-[var(--color-surface-secondary)] border-t border-[var(--color-border)]">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
          <p class="text-sm text-[var(--color-text-tertiary)]">
            {{ $t('legal.footer.copyright', { year: currentYear }) }}
          </p>
          <p class="text-xs text-[var(--color-text-tertiary)]">
            {{ $t('legal.footer.copyrightNotice') }}
          </p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>
