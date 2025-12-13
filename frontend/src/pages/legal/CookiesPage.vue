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
          Zurück zur Startseite
        </router-link>
        <h1 class="text-3xl font-bold text-[var(--color-text-primary)]">
          Cookie-Richtlinie
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          Informationen über die Verwendung von Cookies auf unserer Plattform
        </p>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="prose prose-lg max-w-none text-[var(--color-text-primary)]">

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Was sind Cookies?</h2>
          <p>
            Cookies sind kleine Textdateien, die von Websites auf Ihrem Gerät gespeichert werden.
            Sie helfen dabei, Ihre Präferenzen zu speichern und die Website-Nutzung zu verbessern.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Welche Cookies verwenden wir?</h2>

          <!-- Notwendige Cookies -->
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-6 mb-4 border border-[var(--color-border)]">
            <div class="flex items-center gap-3 mb-3">
              <div class="w-8 h-8 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
              <h3 class="text-lg font-medium m-0">Notwendige Cookies</h3>
              <span class="ml-auto text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded">
                Immer aktiv
              </span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-3">
              Diese Cookies sind für die Grundfunktionen der Website erforderlich und können nicht deaktiviert werden.
            </p>
            <div class="bg-[var(--color-surface)] rounded p-3 text-sm">
              <table class="w-full">
                <thead>
                  <tr class="text-left text-[var(--color-text-tertiary)]">
                    <th class="pb-2">Cookie</th>
                    <th class="pb-2">Zweck</th>
                    <th class="pb-2">Dauer</th>
                  </tr>
                </thead>
                <tbody class="text-[var(--color-text-secondary)]">
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_session</td>
                    <td class="py-1">Sitzungsverwaltung</td>
                    <td class="py-1">Sitzung</td>
                  </tr>
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_auth</td>
                    <td class="py-1">Authentifizierung</td>
                    <td class="py-1">7 Tage</td>
                  </tr>
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_csrf</td>
                    <td class="py-1">Sicherheit (CSRF-Schutz)</td>
                    <td class="py-1">Sitzung</td>
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
              <h3 class="text-lg font-medium m-0">Funktionale Cookies</h3>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-3">
              Diese Cookies ermöglichen erweiterte Funktionen wie Personalisierung und das Speichern Ihrer Präferenzen.
            </p>
            <div class="bg-[var(--color-surface)] rounded p-3 text-sm">
              <table class="w-full">
                <thead>
                  <tr class="text-left text-[var(--color-text-tertiary)]">
                    <th class="pb-2">Cookie</th>
                    <th class="pb-2">Zweck</th>
                    <th class="pb-2">Dauer</th>
                  </tr>
                </thead>
                <tbody class="text-[var(--color-text-secondary)]">
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_theme</td>
                    <td class="py-1">Theme-Präferenz (Hell/Dunkel)</td>
                    <td class="py-1">1 Jahr</td>
                  </tr>
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_lang</td>
                    <td class="py-1">Spracheinstellung</td>
                    <td class="py-1">1 Jahr</td>
                  </tr>
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_sidebar</td>
                    <td class="py-1">Seitenleisten-Status</td>
                    <td class="py-1">30 Tage</td>
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
              <h3 class="text-lg font-medium m-0">Analytische Cookies</h3>
              <span class="ml-auto text-xs bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded">
                Optional
              </span>
            </div>
            <p class="text-sm text-[var(--color-text-secondary)] mb-3">
              Diese Cookies helfen uns zu verstehen, wie Besucher die Website nutzen. Alle Daten sind anonymisiert.
            </p>
            <div class="bg-[var(--color-surface)] rounded p-3 text-sm">
              <table class="w-full">
                <thead>
                  <tr class="text-left text-[var(--color-text-tertiary)]">
                    <th class="pb-2">Cookie</th>
                    <th class="pb-2">Zweck</th>
                    <th class="pb-2">Dauer</th>
                  </tr>
                </thead>
                <tbody class="text-[var(--color-text-secondary)]">
                  <tr>
                    <td class="py-1 font-mono text-xs">lsx_analytics</td>
                    <td class="py-1">Anonyme Nutzungsstatistiken</td>
                    <td class="py-1">90 Tage</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Wie können Sie Cookies verwalten?</h2>
          <p>
            Sie können Ihre Cookie-Einstellungen jederzeit in Ihrem Browser anpassen:
          </p>
          <ul>
            <li>
              <strong>Chrome:</strong> Einstellungen → Datenschutz und Sicherheit → Cookies
            </li>
            <li>
              <strong>Firefox:</strong> Einstellungen → Datenschutz & Sicherheit → Cookies
            </li>
            <li>
              <strong>Safari:</strong> Einstellungen → Datenschutz → Cookies und Websitedaten
            </li>
            <li>
              <strong>Edge:</strong> Einstellungen → Cookies und Websiteberechtigungen
            </li>
          </ul>
          <p class="mt-4">
            <strong>Hinweis:</strong> Das Deaktivieren notwendiger Cookies kann die Funktionalität
            der Website einschränken.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Cookie-Einstellungen anpassen</h2>
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-6 border border-[var(--color-border)]">
            <p class="text-[var(--color-text-secondary)] mb-4">
              Sie können Ihre Cookie-Präferenzen hier anpassen:
            </p>
            <button
              @click="openCookieSettings"
              class="btn btn-primary"
            >
              Cookie-Einstellungen öffnen
            </button>
          </div>
        </section>

        <section>
          <h2 class="text-xl font-semibold mb-4">Weitere Informationen</h2>
          <p>
            Weitere Informationen zum Datenschutz finden Sie in unserer
            <router-link to="/legal/privacy" class="text-[var(--color-accent)] hover:underline">
              Datenschutzerklärung
            </router-link>.
          </p>
          <p class="text-sm text-[var(--color-text-tertiary)] mt-4">
            Stand: {{ currentDate }}
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
import Footer from '@/components/layout/Footer.vue'

const currentDate = computed(() => {
  return new Date().toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
})

const openCookieSettings = () => {
  // TODO: Implement cookie consent modal
  alert('Cookie-Einstellungen werden in einer zukünftigen Version implementiert.')
}
</script>
