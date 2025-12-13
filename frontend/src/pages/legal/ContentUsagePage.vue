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
          Nutzungsbedingungen für Inhalte
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          Informationen zur erlaubten und unerlaubten Nutzung unserer Lerninhalte
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
              Erlaubte Nutzung
            </h2>
          </div>

          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
            <ul class="space-y-4 text-[var(--color-text-primary)]">
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>Persönliches Lernen</strong> – Nutzung der Inhalte im Rahmen Ihrer gebuchten Kurse für Ihre persönliche Weiterbildung.</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>Lehren (mit Lizenz)</strong> – Nutzung als Lehrer/Dozent im Rahmen einer gültigen Schul- oder Unternehmenslizenz.</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>Zitate mit Quellenangabe</strong> – Kurze Zitate (max. 10% eines Textes) für wissenschaftliche oder journalistische Zwecke mit vollständiger Quellenangabe: "Quelle: LernsystemX (www.lernsystemx.de)"</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>Screenshots für Support</strong> – Screenshots von Fehlermeldungen oder Problemen zur Einreichung von Support-Anfragen.</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <span><strong>Offline-Nutzung</strong> – Speichern von Inhalten für die Offline-Nutzung auf Ihren persönlichen Geräten (sofern durch Ihre Lizenz gedeckt).</span>
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
              Verbotene Nutzung
            </h2>
          </div>

          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <ul class="space-y-4 text-[var(--color-text-primary)]">
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>Kommerzielle Weitergabe</strong> – Verkauf, Vermietung oder sonstige kommerzielle Weitergabe von Kursinhalten an Dritte.</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>Vollständige Vervielfältigung</strong> – Kopieren, Downloaden oder Verbreiten ganzer Kurse, Kapitel oder wesentlicher Teile davon.</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>Entfernung von Schutzmaßnahmen</strong> – Entfernen, Umgehen oder Manipulieren von Wasserzeichen, Copyright-Hinweisen oder technischen Schutzmaßnahmen.</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>Automatisiertes Scraping</strong> – Einsatz von Bots, Crawlern oder anderen automatisierten Tools zum Extrahieren von Inhalten.</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>Account-Sharing</strong> – Weitergabe Ihrer Zugangsdaten an Dritte oder gemeinsame Nutzung eines Accounts durch mehrere Personen.</span>
              </li>
              <li class="flex items-start gap-3">
                <svg class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
                <span><strong>Upload auf fremde Plattformen</strong> – Hochladen unserer Inhalte auf YouTube, andere Lernplattformen, Filesharing-Dienste oder soziale Medien.</span>
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
              Rechtliche Folgen bei Verstößen
            </h2>
          </div>

          <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-6">
            <p class="text-[var(--color-text-primary)] mb-4">
              Bei Verstößen gegen diese Nutzungsbedingungen behalten wir uns folgende Maßnahmen vor:
            </p>
            <ul class="space-y-3 text-[var(--color-text-primary)]">
              <li class="flex items-start gap-3">
                <span class="text-amber-600 font-bold">1.</span>
                <span><strong>Sofortige Accountsperrung</strong> – Ohne Vorwarnung und ohne Erstattung bereits gezahlter Gebühren.</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-amber-600 font-bold">2.</span>
                <span><strong>Zivilrechtliche Ansprüche</strong> – Schadensersatzforderungen für entstandene wirtschaftliche Schäden, einschließlich entgangener Lizenzgebühren.</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-amber-600 font-bold">3.</span>
                <span><strong>Strafrechtliche Verfolgung</strong> – Bei schwerem oder gewerbsmäßigem Urheberrechtsverstoß erstatten wir Strafanzeige (§ 106 ff. UrhG).</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="text-amber-600 font-bold">4.</span>
                <span><strong>Abmahnkosten</strong> – Übernahme sämtlicher Anwalts- und Gerichtskosten durch den Verursacher.</span>
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
              Kontakt für Lizenzanfragen
            </h2>
          </div>

          <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <p class="text-[var(--color-text-primary)] mb-4">
              Sie möchten unsere Inhalte kommerziell nutzen oder benötigen eine Sonderlizenz?
              Wir bieten verschiedene Lizenzmodelle an:
            </p>
            <ul class="space-y-2 text-[var(--color-text-primary)] mb-6">
              <li>• <strong>Bildungslizenz</strong> – Für Schulen, Universitäten und Bildungseinrichtungen</li>
              <li>• <strong>Unternehmenslizenz</strong> – Für interne Mitarbeiterschulungen</li>
              <li>• <strong>Weiterverkaufslizenz</strong> – Für Wiederverkäufer und Partner</li>
              <li>• <strong>White-Label-Lizenz</strong> – Für die Integration in eigene Produkte</li>
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
                Lizenzanfrage stellen
              </router-link>
            </div>
          </div>
        </section>

        <!-- Stand der Information -->
        <section class="text-sm text-[var(--color-text-tertiary)] border-t border-[var(--color-border)] pt-6">
          <p>Stand: {{ currentDate }}</p>
          <p>Version: 1.0</p>
          <p class="mt-2">
            Diese Nutzungsbedingungen sind Teil unserer
            <router-link to="/legal/terms" class="text-[var(--color-accent)] hover:underline">
              Allgemeinen Geschäftsbedingungen
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
import Footer from '@/components/layout/Footer.vue'

const currentDate = computed(() => {
  return new Date().toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
})
</script>
