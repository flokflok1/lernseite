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
          Impressum
        </h1>
        <p class="mt-2 text-[var(--color-text-secondary)]">
          Angaben gemäß § 5 TMG
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
              <strong>Hinweis:</strong> Die folgenden Angaben sind Platzhalter und müssen vor dem Produktivbetrieb durch die korrekten Unternehmensdaten ersetzt werden. Bitte konsultieren Sie einen Rechtsanwalt.
            </p>
          </div>
        </div>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Anbieter</h2>
          <p>
            LernsystemX GmbH<br />
            Musterstraße 123<br />
            12345 Musterstadt<br />
            Deutschland
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Vertreten durch</h2>
          <p>Geschäftsführer: Max Mustermann</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Kontakt</h2>
          <p>
            Telefon: +49 (0) 123 456789<br />
            E-Mail: info@lernsystemx.de<br />
            Website: www.lernsystemx.de
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Registereintrag</h2>
          <p>
            Eintragung im Handelsregister<br />
            Registergericht: Amtsgericht Musterstadt<br />
            Registernummer: HRB 12345
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Umsatzsteuer-ID</h2>
          <p>
            Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br />
            DE 123456789
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
          <p>
            Max Mustermann<br />
            Musterstraße 123<br />
            12345 Musterstadt
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">EU-Streitschlichtung</h2>
          <p>
            Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:
            <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener noreferrer" class="text-[var(--color-accent)] hover:underline">
              https://ec.europa.eu/consumers/odr/
            </a>
          </p>
          <p>Unsere E-Mail-Adresse finden Sie oben im Impressum.</p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Verbraucherstreitbeilegung/Universalschlichtungsstelle</h2>
          <p>
            Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer
            Verbraucherschlichtungsstelle teilzunehmen.
          </p>
        </section>

        <section class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Haftung für Inhalte</h2>
          <p>
            Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach
            den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter
            jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen
            oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
          </p>
        </section>

        <section>
          <h2 class="text-xl font-semibold mb-4">Haftung für Links</h2>
          <p>
            Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen
            Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen.
            Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der
            Seiten verantwortlich.
          </p>
        </section>
      </div>
    </main>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup lang="ts">
import Footer from '@/components/layout/Footer.vue'
</script>
