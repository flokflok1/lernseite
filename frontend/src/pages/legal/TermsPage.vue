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
          Allgemeine Geschäftsbedingungen (AGB)
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          Nutzungsbedingungen für LernsystemX
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
              <strong>Hinweis:</strong> Diese AGB sind ein Platzhalter und müssen vor dem Produktivbetrieb durch rechtlich geprüfte Texte ersetzt werden. Bitte konsultieren Sie einen Rechtsanwalt.
            </p>
          </div>
        </div>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 1 Geltungsbereich</h2>
          <p>
            (1) Diese Allgemeinen Geschäftsbedingungen (AGB) gelten für alle Verträge zwischen der
            LernsystemX GmbH (nachfolgend „Anbieter") und dem Nutzer über die Nutzung der
            Lernplattform LernsystemX.
          </p>
          <p>
            (2) Abweichende, entgegenstehende oder ergänzende AGB des Nutzers werden nicht
            Vertragsbestandteil, es sei denn, ihrer Geltung wird ausdrücklich schriftlich zugestimmt.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 2 Vertragsgegenstand</h2>
          <p>
            (1) Der Anbieter betreibt eine KI-gestützte Online-Lernplattform mit verschiedenen
            Lernmethoden und Kursen.
          </p>
          <p>
            (2) Der konkrete Leistungsumfang richtet sich nach dem vom Nutzer gewählten
            Abonnement-Modell (Free, Premium, Creator, etc.).
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 3 Registrierung und Nutzerkonto</h2>
          <p>
            (1) Die Nutzung der Plattform erfordert eine Registrierung.
          </p>
          <p>
            (2) Der Nutzer verpflichtet sich, bei der Registrierung wahrheitsgemäße Angaben zu machen
            und seine Zugangsdaten geheim zu halten.
          </p>
          <p>
            (3) Jeder Nutzer darf nur ein Konto anlegen. Die Weitergabe von Zugangsdaten an Dritte
            ist untersagt.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 4 Preise und Zahlung</h2>
          <p>
            (1) Die aktuellen Preise und Leistungen der verschiedenen Abonnement-Modelle sind auf
            der Website ersichtlich.
          </p>
          <p>
            (2) Alle Preise verstehen sich inklusive der jeweils gültigen gesetzlichen Mehrwertsteuer.
          </p>
          <p>
            (3) Die Zahlung erfolgt per den auf der Plattform angebotenen Zahlungsmethoden.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 5 Token-System</h2>
          <p>
            (1) Bestimmte Funktionen der Plattform (insbesondere KI-gestützte Inhalte) werden über
            ein Token-System abgerechnet.
          </p>
          <p>
            (2) Premium-Nutzer erhalten ein monatliches Token-Kontingent gemäß ihrem Abonnement.
          </p>
          <p>
            (3) Nicht verbrauchte Tokens verfallen am Ende des Abrechnungszeitraums und werden nicht
            auf den Folgemonat übertragen.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 6 Urheberrecht und Nutzungsrechte</h2>
          <p>
            (1) Sämtliche Inhalte der Plattform sind urheberrechtlich geschützt.
          </p>
          <p>
            (2) Der Nutzer erhält ein einfaches, nicht übertragbares Nutzungsrecht für den
            persönlichen Gebrauch.
          </p>
          <p>
            (3) Die Vervielfältigung, Weitergabe oder kommerzielle Nutzung von Inhalten ist ohne
            ausdrückliche schriftliche Genehmigung untersagt.
          </p>
          <p>
            (4) Weitere Details finden Sie in unseren
            <router-link to="/legal/content-usage" class="text-[var(--color-accent)] hover:underline">
              Nutzungsbedingungen für Inhalte
            </router-link>.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 7 Kündigung</h2>
          <p>
            (1) Kostenfreie Konten können jederzeit ohne Angabe von Gründen gelöscht werden.
          </p>
          <p>
            (2) Premium-Abonnements können zum Ende der jeweiligen Vertragslaufzeit gekündigt werden.
          </p>
          <p>
            (3) Das Recht zur fristlosen Kündigung aus wichtigem Grund bleibt unberührt.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 8 Haftung</h2>
          <p>
            (1) Der Anbieter haftet unbeschränkt für Vorsatz und grobe Fahrlässigkeit.
          </p>
          <p>
            (2) Bei leichter Fahrlässigkeit haftet der Anbieter nur bei Verletzung wesentlicher
            Vertragspflichten.
          </p>
          <p>
            (3) Die Haftung für Schäden aus der Verletzung des Lebens, des Körpers oder der
            Gesundheit bleibt unberührt.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 9 Datenschutz</h2>
          <p>
            Informationen zur Verarbeitung personenbezogener Daten finden Sie in unserer
            <router-link to="/legal/privacy" class="text-[var(--color-accent)] hover:underline">
              Datenschutzerklärung
            </router-link>.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 10 Änderung der AGB</h2>
          <p>
            (1) Der Anbieter behält sich vor, diese AGB zu ändern.
          </p>
          <p>
            (2) Änderungen werden dem Nutzer mindestens 4 Wochen vor Inkrafttreten mitgeteilt.
          </p>
          <p>
            (3) Widerspricht der Nutzer nicht innerhalb von 4 Wochen, gelten die geänderten AGB
            als angenommen.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">§ 11 Schlussbestimmungen</h2>
          <p>
            (1) Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des
            UN-Kaufrechts.
          </p>
          <p>
            (2) Gerichtsstand ist, soweit gesetzlich zulässig, der Sitz des Anbieters.
          </p>
          <p>
            (3) Sollten einzelne Bestimmungen dieser AGB unwirksam sein, bleibt die Wirksamkeit
            der übrigen Bestimmungen unberührt.
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
