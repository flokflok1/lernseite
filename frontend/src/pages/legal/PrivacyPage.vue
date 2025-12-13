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
          Datenschutzerklärung
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          Informationen zum Datenschutz nach DSGVO
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
              <strong>Hinweis:</strong> Diese Datenschutzerklärung ist ein Platzhalter und muss vor dem Produktivbetrieb durch einen rechtlich geprüften Text ersetzt werden. Bitte konsultieren Sie einen Datenschutzbeauftragten oder Rechtsanwalt.
            </p>
          </div>
        </div>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">1. Datenschutz auf einen Blick</h2>
          <h3 class="text-lg font-medium mb-2">Allgemeine Hinweise</h3>
          <p>
            Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen
            Daten passiert, wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit
            denen Sie persönlich identifiziert werden können.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">2. Verantwortlicher</h2>
          <p>
            LernsystemX GmbH<br />
            Musterstraße 123<br />
            12345 Musterstadt<br />
            E-Mail: datenschutz@lernsystemx.de
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">3. Datenerfassung auf dieser Website</h2>

          <h3 class="text-lg font-medium mb-2">Wer ist verantwortlich für die Datenerfassung?</h3>
          <p>
            Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber.
            Dessen Kontaktdaten können Sie dem Abschnitt „Verantwortlicher" entnehmen.
          </p>

          <h3 class="text-lg font-medium mb-2 mt-4">Wie erfassen wir Ihre Daten?</h3>
          <p>
            Ihre Daten werden zum einen dadurch erhoben, dass Sie uns diese mitteilen.
            Hierbei kann es sich z.B. um Daten handeln, die Sie bei der Registrierung eingeben.
          </p>
          <p>
            Andere Daten werden automatisch oder nach Ihrer Einwilligung beim Besuch der Website
            durch unsere IT-Systeme erfasst. Das sind vor allem technische Daten (z.B. Internetbrowser,
            Betriebssystem oder Uhrzeit des Seitenaufrufs).
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">4. Nutzerkonto und Lerndaten</h2>
          <p>
            Bei der Nutzung unserer Lernplattform verarbeiten wir folgende personenbezogene Daten:
          </p>
          <ul>
            <li>Name, E-Mail-Adresse (Registrierungsdaten)</li>
            <li>Lernfortschritt und Kursabschlüsse</li>
            <li>Quiz- und Prüfungsergebnisse</li>
            <li>Nutzungszeiten und -statistiken</li>
            <li>Präferenzen und Einstellungen</li>
          </ul>
          <p>
            Diese Daten sind für die Bereitstellung unserer Lernservices erforderlich und werden
            auf Grundlage von Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung) verarbeitet.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">5. KI-gestützte Dienste</h2>
          <p>
            Unsere Plattform nutzt KI-Dienste von Drittanbietern (Anthropic, OpenAI, DeepL)
            zur Generierung und Übersetzung von Lerninhalten. Dabei werden:
          </p>
          <ul>
            <li>Keine personenbezogenen Daten an die KI-Anbieter übermittelt</li>
            <li>Nur anonymisierte Lerninhalte verarbeitet</li>
            <li>Alle Verarbeitungen DSGVO-konform durchgeführt</li>
          </ul>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">6. Cookies</h2>
          <p>
            Unsere Internetseiten verwenden Cookies. Cookies sind kleine Textdateien, die auf Ihrem
            Rechner abgelegt werden und die Ihr Browser speichert.
          </p>
          <p>
            Wir verwenden:
          </p>
          <ul>
            <li><strong>Notwendige Cookies</strong> - für die Grundfunktionen der Website</li>
            <li><strong>Funktionale Cookies</strong> - für Ihre Präferenzen</li>
            <li><strong>Analytische Cookies</strong> - zur Verbesserung unserer Dienste (nur mit Einwilligung)</li>
          </ul>
          <p>
            Weitere Informationen finden Sie in unserer
            <router-link to="/legal/cookies" class="text-[var(--color-accent)] hover:underline">
              Cookie-Richtlinie
            </router-link>.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">7. Ihre Rechte</h2>
          <p>Sie haben jederzeit das Recht:</p>
          <ul>
            <li>Auskunft über Ihre gespeicherten Daten zu erhalten</li>
            <li>Berichtigung unrichtiger Daten zu verlangen</li>
            <li>Löschung Ihrer Daten zu verlangen</li>
            <li>Die Verarbeitung einzuschränken</li>
            <li>Der Verarbeitung zu widersprechen</li>
            <li>Datenübertragbarkeit zu verlangen</li>
          </ul>
          <p>
            Für die Ausübung Ihrer Rechte wenden Sie sich bitte an:
            <a href="mailto:datenschutz@lernsystemx.de" class="text-[var(--color-accent)] hover:underline">
              datenschutz@lernsystemx.de
            </a>
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">8. Datensicherheit</h2>
          <p>
            Wir verwenden innerhalb des Website-Besuchs das verbreitete SSL-Verfahren
            (Secure Socket Layer) in Verbindung mit der jeweils höchsten Verschlüsselungsstufe,
            die von Ihrem Browser unterstützt wird.
          </p>
          <p>
            Darüber hinaus setzen wir geeignete technische und organisatorische Sicherheitsmaßnahmen ein,
            um Ihre Daten gegen zufällige oder vorsätzliche Manipulationen, Verlust, Zerstörung
            oder gegen den Zugriff unberechtigter Personen zu schützen.
          </p>
        </section>

        <section>
          <p class="text-sm text-[var(--color-text-tertiary)]">
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
</script>
