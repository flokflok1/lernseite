<template>
  <div class="casio-guide">
    <!-- Header -->
    <div class="bg-gradient-to-r from-slate-700 to-slate-900 rounded-xl p-5 mb-5 text-white">
      <div class="flex items-center gap-4">
        <div class="text-5xl">🔢</div>
        <div>
          <h2 class="text-xl font-bold">Casio FX-991DEX Guide</h2>
          <p class="text-slate-300 text-sm">Alle wichtigen Funktionen für die AP1-Prüfung</p>
        </div>
      </div>
    </div>

    <!-- Category Tabs -->
    <div class="flex gap-2 overflow-x-auto pb-2 mb-5">
      <button
        v-for="cat in categories"
        :key="cat.id"
        @click="activeCategory = cat.id"
        class="px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-colors flex-shrink-0"
        :class="activeCategory === cat.id
          ? 'bg-slate-700 text-white'
          : 'bg-[var(--color-surface)] border border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-slate-400'"
      >
        {{ cat.icon }} {{ cat.label }}
      </button>
    </div>

    <!-- Content -->
    <div class="space-y-4">

      <!-- GRUNDLAGEN -->
      <template v-if="activeCategory === 'basics'">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
            <h3 class="font-bold text-[var(--color-text-primary)] mb-3">📱 Modi starten</h3>
            <div class="space-y-2">
              <div v-for="m in modes" :key="m.key" class="flex items-start gap-3">
                <div class="flex gap-1 flex-shrink-0">
                  <kbd v-for="k in m.keys" :key="k" class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">{{ k }}</kbd>
                </div>
                <div>
                  <span class="text-sm font-medium text-[var(--color-text-primary)]">{{ m.name }}</span>
                  <span class="text-xs text-[var(--color-text-secondary)] ml-2">{{ m.desc }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-4">
            <h3 class="font-bold text-[var(--color-text-primary)] mb-3">⌨️ Wichtige Tasten</h3>
            <div class="space-y-2">
              <div v-for="k in importantKeys" :key="k.key" class="flex items-center gap-3">
                <kbd class="px-2 py-0.5 bg-blue-600 text-white rounded text-xs font-mono min-w-[60px] text-center">{{ k.key }}</kbd>
                <span class="text-sm text-[var(--color-text-primary)]">{{ k.desc }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-4">
          <h3 class="font-bold text-blue-800 dark:text-blue-300 mb-2">💡 Tipp: Speicher nutzen</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-blue-700 dark:text-blue-400">
            <div>
              <strong>Speichern:</strong> Ergebnis berechnen → <kbd class="px-1.5 py-0.5 bg-blue-600 text-white rounded text-xs">SHIFT</kbd> <kbd class="px-1.5 py-0.5 bg-blue-600 text-white rounded text-xs">STO</kbd> → Buchstabe (A–F, x, y, z)
            </div>
            <div>
              <strong>Abrufen:</strong> <kbd class="px-1.5 py-0.5 bg-blue-600 text-white rounded text-xs">RCL</kbd> → Buchstabe
            </div>
            <div>
              <strong>Ans nutzen:</strong> <kbd class="px-1.5 py-0.5 bg-blue-600 text-white rounded text-xs">Ans</kbd> = letztes Ergebnis. Praktisch für mehrstufige Rechnungen!
            </div>
            <div>
              <strong>AC ≠ löscht Speicher:</strong> <kbd class="px-1.5 py-0.5 bg-blue-600 text-white rounded text-xs">AC</kbd> löscht nur die Eingabe, nicht den Speicher.
            </div>
          </div>
        </div>
      </template>

      <!-- PROZENT & KALKULATION -->
      <template v-if="activeCategory === 'kalkulation'">
        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
          <h3 class="font-bold text-[var(--color-text-primary)] mb-4">💰 Bezugskalkulation – Schritt für Schritt</h3>

          <div class="space-y-3">
            <div v-for="(step, i) in kalkulationSteps" :key="i" class="flex items-start gap-4 p-3 rounded-lg" :class="step.highlight ? 'bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-700' : 'bg-[var(--color-surface-secondary)]'">
              <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold text-sm"
                :class="step.highlight ? 'bg-indigo-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'">
                {{ i + 1 }}
              </div>
              <div class="flex-1">
                <div class="font-medium text-[var(--color-text-primary)] text-sm">{{ step.name }}</div>
                <div class="text-xs text-[var(--color-text-secondary)] mt-0.5">{{ step.formula }}</div>
                <div v-if="step.casio" class="mt-1.5 flex items-center gap-2">
                  <span class="text-xs text-gray-500">Casio:</span>
                  <code class="px-2 py-0.5 bg-slate-700 text-green-300 rounded text-xs font-mono">{{ step.casio }}</code>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
          <h3 class="font-bold text-[var(--color-text-primary)] mb-3">% Prozentrechnung – Casio Tricks</h3>
          <div class="space-y-3">
            <div v-for="trick in procentTricks" :key="trick.label" class="flex items-start gap-3 p-3 bg-[var(--color-surface-secondary)] rounded-lg">
              <div>
                <div class="font-medium text-sm text-[var(--color-text-primary)]">{{ trick.label }}</div>
                <div class="text-xs text-[var(--color-text-secondary)] mb-1">{{ trick.desc }}</div>
                <code class="px-2 py-1 bg-slate-800 text-green-300 rounded text-xs font-mono block">{{ trick.casio }}</code>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- STROMKOSTEN -->
      <template v-if="activeCategory === 'strom'">
        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
          <h3 class="font-bold text-[var(--color-text-primary)] mb-4">⚡ Stromkosten berechnen</h3>

          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4 mb-5">
            <div class="font-bold text-yellow-800 dark:text-yellow-300 mb-2 text-sm">🧮 Die Formel:</div>
            <div class="font-mono text-lg text-yellow-900 dark:text-yellow-200 text-center py-2">
              Kosten = (Leistung [W] ÷ 1000) × Zeit [h] × Preis [€/kWh]
            </div>
          </div>

          <h4 class="font-semibold text-[var(--color-text-primary)] mb-3 text-sm">📝 Beispiel-Aufgabe (typisch AP1 BW):</h4>
          <div class="bg-[var(--color-surface-secondary)] rounded-lg p-4 mb-4 text-sm text-[var(--color-text-secondary)]">
            Ein Server läuft 24h/Tag mit 350W. Der Strompreis beträgt 0,32 €/kWh. Wie hoch sind die monatlichen Stromkosten (30 Tage)?
          </div>

          <div class="space-y-3">
            <div v-for="(step, i) in stromSteps" :key="i" class="flex items-start gap-4 p-3 rounded-lg bg-[var(--color-surface-secondary)]">
              <div class="w-7 h-7 rounded-full bg-yellow-500 text-white flex items-center justify-center flex-shrink-0 font-bold text-xs">{{ i + 1 }}</div>
              <div>
                <div class="text-sm font-medium text-[var(--color-text-primary)]">{{ step.step }}</div>
                <div class="text-xs text-[var(--color-text-secondary)]">{{ step.calc }}</div>
                <code v-if="step.casio" class="mt-1 px-2 py-0.5 bg-slate-800 text-green-300 rounded text-xs font-mono block w-fit">{{ step.casio }}</code>
              </div>
            </div>
          </div>

          <div class="mt-4 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-lg">
            <div class="font-bold text-green-700 dark:text-green-400 text-sm">✅ Ergebnis: 80,64 €/Monat</div>
            <div class="text-xs text-green-600 dark:text-green-500 mt-1">Casio direkt: <code class="px-1.5 py-0.5 bg-slate-800 text-green-300 rounded font-mono">350 ÷ 1000 × 24 × 30 × 0.32 =</code> → 80,64</div>
          </div>
        </div>

        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
          <h3 class="font-bold text-[var(--color-text-primary)] mb-3">🔄 Einheiten-Umrechnung</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="conv in conversions" :key="conv.from" class="p-3 bg-[var(--color-surface-secondary)] rounded-lg text-sm">
              <div class="font-medium text-[var(--color-text-primary)]">{{ conv.from }} → {{ conv.to }}</div>
              <code class="text-xs text-indigo-600 dark:text-indigo-400">{{ conv.formula }}</code>
            </div>
          </div>
        </div>
      </template>

      <!-- BINÄR / HEX (BASE-N) -->
      <template v-if="activeCategory === 'basen'">
        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
          <h3 class="font-bold text-[var(--color-text-primary)] mb-4">💻 BASE-N Modus (Binär, Hex, Oktal)</h3>

          <div class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700 rounded-lg p-4 mb-4">
            <div class="font-semibold text-orange-800 dark:text-orange-300 text-sm mb-2">🔑 Modus aktivieren:</div>
            <div class="flex items-center gap-2">
              <kbd class="px-2 py-1 bg-slate-700 text-white rounded text-sm font-mono">MODE</kbd>
              <span class="text-orange-700 dark:text-orange-400">→</span>
              <kbd class="px-2 py-1 bg-slate-700 text-white rounded text-sm font-mono">3</kbd>
              <span class="text-xs text-orange-600 dark:text-orange-500 ml-2">(BASE-N Modus)</span>
            </div>
          </div>

          <div class="space-y-3 mb-5">
            <div v-for="base in baseConversions" :key="base.mode" class="flex items-start gap-4 p-3 bg-[var(--color-surface-secondary)] rounded-lg">
              <kbd class="px-3 py-1.5 bg-slate-700 text-white rounded font-mono text-sm flex-shrink-0">{{ base.key }}</kbd>
              <div>
                <div class="font-medium text-sm text-[var(--color-text-primary)]">{{ base.mode }}</div>
                <div class="text-xs text-[var(--color-text-secondary)]">{{ base.desc }}</div>
              </div>
            </div>
          </div>

          <h4 class="font-semibold text-[var(--color-text-primary)] mb-3 text-sm">📝 Beispiel: Dezimal 192 → Binär</h4>
          <div class="space-y-2">
            <div v-for="(step, i) in binSteps" :key="i" class="flex items-center gap-3 p-2 rounded bg-[var(--color-surface-secondary)] text-sm">
              <span class="w-6 h-6 rounded-full bg-orange-500 text-white flex items-center justify-center text-xs font-bold flex-shrink-0">{{ i + 1 }}</span>
              <span class="text-[var(--color-text-primary)]">{{ step }}</span>
            </div>
          </div>
        </div>

        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
          <h3 class="font-bold text-[var(--color-text-primary)] mb-3">📊 Schnell-Referenz: Binär ↔ Dezimal</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-slate-700 text-white">
                  <th class="px-3 py-2 text-left rounded-tl-lg">Dezimal</th>
                  <th class="px-3 py-2 text-left">Binär</th>
                  <th class="px-3 py-2 text-left">Hex</th>
                  <th class="px-3 py-2 text-left rounded-tr-lg">Bedeutung</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in binTable" :key="row.dec" class="border-b border-[var(--color-border)] hover:bg-[var(--color-surface-secondary)]">
                  <td class="px-3 py-1.5 font-mono font-bold text-[var(--color-text-primary)]">{{ row.dec }}</td>
                  <td class="px-3 py-1.5 font-mono text-orange-600 dark:text-orange-400">{{ row.bin }}</td>
                  <td class="px-3 py-1.5 font-mono text-blue-600 dark:text-blue-400">{{ row.hex }}</td>
                  <td class="px-3 py-1.5 text-[var(--color-text-secondary)] text-xs">{{ row.note }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- POTENZEN & WISSENSCHAFT -->
      <template v-if="activeCategory === 'math'">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
            <h3 class="font-bold text-[var(--color-text-primary)] mb-3">🔢 Potenzen & Wurzeln</h3>
            <div class="space-y-3">
              <div v-for="op in mathOps" :key="op.label" class="p-3 bg-[var(--color-surface-secondary)] rounded-lg">
                <div class="font-medium text-sm text-[var(--color-text-primary)] mb-1">{{ op.label }}</div>
                <code class="px-2 py-1 bg-slate-800 text-green-300 rounded text-xs font-mono block">{{ op.casio }}</code>
                <div class="text-xs text-[var(--color-text-secondary)] mt-1">{{ op.example }}</div>
              </div>
            </div>
          </div>

          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
            <h3 class="font-bold text-[var(--color-text-primary)] mb-3">📏 Klammern & Vorrang</h3>
            <div class="space-y-3">
              <div class="p-3 bg-[var(--color-surface-secondary)] rounded-lg text-sm">
                <div class="font-medium text-[var(--color-text-primary)] mb-2">⚠️ Wichtig: Klammern setzen!</div>
                <div class="text-[var(--color-text-secondary)] text-xs space-y-1">
                  <div><span class="text-red-500">❌ Falsch:</span> <code class="bg-slate-800 text-red-300 px-1 rounded font-mono text-xs">350 / 1000 * 24</code></div>
                  <div class="text-xs text-gray-400 ml-4">→ Rechnet 350 ÷ 1000 = 0,35; dann × 24</div>
                  <div class="mt-2"><span class="text-green-500">✅ Richtig:</span> <code class="bg-slate-800 text-green-300 px-1 rounded font-mono text-xs">(350 / 1000) * 24</code></div>
                  <div class="text-xs text-gray-400 ml-4">→ Gleich, aber sicherer mit Klammern!</div>
                </div>
              </div>
              <div class="p-3 bg-[var(--color-surface-secondary)] rounded-lg text-sm">
                <div class="font-medium text-[var(--color-text-primary)] mb-2">🔁 Zwischenergebnis speichern</div>
                <div class="text-xs text-[var(--color-text-secondary)] space-y-1">
                  <div>Schritt 1 ausrechnen → <kbd class="px-1 py-0.5 bg-slate-700 text-white rounded text-xs">SHIFT</kbd> <kbd class="px-1 py-0.5 bg-slate-700 text-white rounded text-xs">STO</kbd> <kbd class="px-1 py-0.5 bg-slate-700 text-white rounded text-xs">A</kbd></div>
                  <div>Später: <kbd class="px-1 py-0.5 bg-slate-700 text-white rounded text-xs">RCL</kbd> <kbd class="px-1 py-0.5 bg-slate-700 text-white rounded text-xs">A</kbd> aufrufen</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
          <h3 class="font-bold text-[var(--color-text-primary)] mb-3">🔬 Wissenschaftliche Notation (EE-Taste)</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
            <div class="p-3 bg-[var(--color-surface-secondary)] rounded-lg">
              <div class="font-medium text-[var(--color-text-primary)]">Eingabe: 1,5 × 10⁶</div>
              <code class="text-xs bg-slate-800 text-green-300 px-2 py-0.5 rounded font-mono mt-1 block">1.5 × 10^6 =</code>
              <div class="text-xs text-[var(--color-text-secondary)] mt-1">oder: <code class="bg-slate-800 text-green-300 px-1 rounded font-mono">1.5 EXP 6</code></div>
            </div>
            <div class="p-3 bg-[var(--color-surface-secondary)] rounded-lg">
              <div class="font-medium text-[var(--color-text-primary)]">Ergebnis anzeigen</div>
              <div class="text-xs text-[var(--color-text-secondary)] mt-1">
                <kbd class="px-1.5 py-0.5 bg-slate-700 text-white rounded text-xs">SHIFT</kbd> + <kbd class="px-1.5 py-0.5 bg-slate-700 text-white rounded text-xs">=</kbd> wechselt zwischen Dezimal und Bruch
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- PRÜFUNGSTIPPS -->
      <template v-if="activeCategory === 'tipps'">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl p-5">
            <h3 class="font-bold text-green-800 dark:text-green-300 mb-3">✅ Do's in der Prüfung</h3>
            <ul class="space-y-2">
              <li v-for="tip in doTips" :key="tip" class="flex items-start gap-2 text-sm text-green-700 dark:text-green-400">
                <span class="text-green-500 flex-shrink-0">✓</span>{{ tip }}
              </li>
            </ul>
          </div>
          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-xl p-5">
            <h3 class="font-bold text-red-800 dark:text-red-300 mb-3">❌ Don'ts in der Prüfung</h3>
            <ul class="space-y-2">
              <li v-for="tip in dontTips" :key="tip" class="flex items-start gap-2 text-sm text-red-700 dark:text-red-400">
                <span class="text-red-500 flex-shrink-0">✗</span>{{ tip }}
              </li>
            </ul>
          </div>
        </div>

        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
          <h3 class="font-bold text-[var(--color-text-primary)] mb-3">🏁 Casio Reset – wenn alles hängt</h3>
          <div class="space-y-2 text-sm">
            <div class="p-3 bg-[var(--color-surface-secondary)] rounded-lg">
              <div class="font-medium text-[var(--color-text-primary)]">Nur Einstellungen zurücksetzen (Speicher bleibt):</div>
              <div class="flex items-center gap-1 mt-1">
                <kbd class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">SHIFT</kbd>
                <kbd class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">9</kbd>
                <span class="text-[var(--color-text-secondary)]">→</span>
                <kbd class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">1</kbd>
                <span class="text-[var(--color-text-secondary)]">→</span>
                <kbd class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">=</kbd>
              </div>
            </div>
            <div class="p-3 bg-[var(--color-surface-secondary)] rounded-lg">
              <div class="font-medium text-[var(--color-text-primary)]">Alles zurücksetzen:</div>
              <div class="flex items-center gap-1 mt-1">
                <kbd class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">SHIFT</kbd>
                <kbd class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">9</kbd>
                <span class="text-[var(--color-text-secondary)]">→</span>
                <kbd class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">3</kbd>
                <span class="text-[var(--color-text-secondary)]">→</span>
                <kbd class="px-2 py-0.5 bg-slate-700 text-white rounded text-xs font-mono">=</kbd>
              </div>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeCategory = ref('basics')

const categories = [
  { id: 'basics', icon: '📱', label: 'Grundlagen' },
  { id: 'kalkulation', icon: '💰', label: 'Kalkulation' },
  { id: 'strom', icon: '⚡', label: 'Stromkosten' },
  { id: 'basen', icon: '💻', label: 'Binär/Hex' },
  { id: 'math', icon: '🔢', label: 'Potenzen & Klammern' },
  { id: 'tipps', icon: '🏁', label: 'Prüfungstipps' },
]

const modes = [
  { keys: ['MODE', '1'], name: 'COMP', desc: 'Normaler Rechenmodus (Standard)' },
  { keys: ['MODE', '2'], name: 'CMPLX', desc: 'Komplexe Zahlen' },
  { keys: ['MODE', '3'], name: 'STAT', desc: 'Statistik' },
  { keys: ['MODE', '4'], name: 'BASE-N', desc: 'Binär, Oktal, Dezimal, Hex' },
  { keys: ['MODE', '5'], name: 'EQN', desc: 'Gleichungen lösen' },
  { keys: ['MODE', '6'], name: 'MATRIX', desc: 'Matrizenrechnung' },
]

const importantKeys = [
  { key: 'AC', desc: 'Eingabe löschen (Speicher bleibt!)' },
  { key: 'DEL', desc: 'Letztes Zeichen löschen' },
  { key: 'SHIFT', desc: 'Orange Funktionen aktivieren' },
  { key: 'ALPHA', desc: 'Grüne Funktionen / Buchstaben' },
  { key: 'Ans', desc: 'Letztes Ergebnis verwenden' },
  { key: '=', desc: 'Berechnen / Bestätigen' },
  { key: '←→', desc: 'Im Ausdruck navigieren' },
]

const kalkulationSteps = [
  { name: 'Listenpreis (LP)', formula: 'Gegeben', casio: null, highlight: false },
  { name: '- Rabatt', formula: 'LP × Rabatt%', casio: '1000 × 20 ÷ 100 =', highlight: false },
  { name: '= Zieleinkaufspreis (ZEP)', formula: 'LP - Rabatt', casio: '1000 - Ans =', highlight: true },
  { name: '- Skonto', formula: 'ZEP × Skonto%', casio: 'Ans × 2 ÷ 100 =', highlight: false },
  { name: '= Bareinkaufspreis (BEP)', formula: 'ZEP - Skonto', casio: 'Ans - Skonto =', highlight: true },
  { name: '+ Bezugskosten', formula: 'Fracht, Lieferung', casio: 'Ans + 50 =', highlight: false },
  { name: '= Bezugspreis (Einstandspreis)', formula: 'BEP + Bezugskosten', casio: null, highlight: true },
]

const procentTricks = [
  { label: '20% von 1.000 berechnen', desc: 'Rabatt berechnen', casio: '1000 × 20 ÷ 100 =' },
  { label: '1.000 − 20% berechnen', desc: 'Preis nach Rabatt', casio: '1000 - (1000 × 20 ÷ 100) =' },
  { label: 'Prozentsatz berechnen', desc: '200 ist wie viel % von 1000?', casio: '200 ÷ 1000 × 100 =' },
  { label: 'Mehrwertsteuer (19%)', desc: 'Netto-Preis + 19% MwSt', casio: '1000 × 1.19 =' },
  { label: 'Netto aus Brutto', desc: 'Brutto ÷ 1,19', casio: '1190 ÷ 1.19 =' },
]

const stromSteps = [
  { step: 'Leistung in kW umrechnen', calc: '350 W ÷ 1000 = 0,35 kW', casio: '350 ÷ 1000 =' },
  { step: 'Stunden pro Monat berechnen', calc: '24 h × 30 Tage = 720 h', casio: '24 × 30 =' },
  { step: 'Verbrauch in kWh', calc: '0,35 kW × 720 h = 252 kWh', casio: '0.35 × 720 =' },
  { step: 'Kosten berechnen', calc: '252 kWh × 0,32 €/kWh = 80,64 €', casio: '252 × 0.32 =' },
]

const conversions = [
  { from: 'Watt → Kilowatt', to: '', formula: 'W ÷ 1000 = kW' },
  { from: 'kWh (Energie)', to: '', formula: 'kW × Stunden = kWh' },
  { from: 'Cent → Euro', to: '', formula: 'ct ÷ 100 = €' },
  { from: 'Stunden/Monat', to: '', formula: '24h × 30 Tage = 720 h' },
  { from: 'Stunden/Jahr', to: '', formula: '24h × 365 Tage = 8760 h' },
  { from: 'MB → GB', to: '', formula: 'MB ÷ 1024 = GB' },
]

const baseConversions = [
  { key: 'DEC', mode: 'Dezimal (Basis 10)', desc: 'Normale Zahlen. Taste nach MODE 3 drücken' },
  { key: 'BIN', mode: 'Binär (Basis 2)', desc: 'Nur 0 und 1. In der Eingabe nur 0/1 erlaubt' },
  { key: 'OCT', mode: 'Oktal (Basis 8)', desc: 'Zahlen 0-7. Selten in AP1' },
  { key: 'HEX', mode: 'Hexadezimal (Basis 16)', desc: 'Zahlen + A-F. Für IP/MAC-Adressen' },
]

const binSteps = [
  'MODE drücken → 4 (BASE-N Modus)',
  'Dezimalmodus: DEC-Taste drücken',
  '192 eingeben → = drücken',
  'BIN-Taste drücken → zeigt 11000000',
  'Zurück: DEC drücken → wieder 192',
]

const binTable = [
  { dec: '0', bin: '0000', hex: '0', note: 'Null' },
  { dec: '1', bin: '0001', hex: '1', note: 'Eins' },
  { dec: '10', bin: '00001010', hex: 'A', note: '' },
  { dec: '15', bin: '00001111', hex: 'F', note: 'Max 1 Nibble' },
  { dec: '16', bin: '00010000', hex: '10', note: 'Hex-Stelle +1' },
  { dec: '128', bin: '10000000', hex: '80', note: '2⁷' },
  { dec: '192', bin: '11000000', hex: 'C0', note: 'Häufig in Subnetting' },
  { dec: '224', bin: '11100000', hex: 'E0', note: '/27 Subnetzmaske' },
  { dec: '240', bin: '11110000', hex: 'F0', note: '/28 Subnetzmaske' },
  { dec: '248', bin: '11111000', hex: 'F8', note: '/29 Subnetzmaske' },
  { dec: '252', bin: '11111100', hex: 'FC', note: '/30 Subnetzmaske' },
  { dec: '255', bin: '11111111', hex: 'FF', note: 'Alle Bits gesetzt' },
]

const mathOps = [
  { label: 'Quadrat (x²)', casio: '5 x² =', example: '5² = 25' },
  { label: 'Beliebige Potenz (xⁿ)', casio: '2 ^ 10 =', example: '2¹⁰ = 1024' },
  { label: 'Quadratwurzel (√)', casio: 'SHIFT x² 25 =', example: '√25 = 5' },
  { label: 'Kubikwurzel (³√)', casio: 'SHIFT ^ 8 =', example: '³√8 = 2' },
  { label: 'Kehrwert (1/x)', casio: '4 SHIFT x² =', example: '1/4 = 0,25' },
  { label: 'Betrag (|x|)', casio: 'SHIFT ÷ (-5) =', example: '|-5| = 5' },
]

const doTips = [
  'Immer zuerst prüfen ob Rechner im COMP-Modus (MODE 1)',
  'Zwischenergebnisse auf Papier notieren!',
  'Einheiten vor der Rechnung angleichen (W→kW, ct→€)',
  'Probe: Ergebnis grob im Kopf überschlagen',
  'Klammern großzügig setzen für korrekte Reihenfolge',
  'Ans-Taste für verkettete Rechnungen nutzen',
  'Ergebnis auf sinnvolle Nachkommastellen runden',
]

const dontTips = [
  'Nicht den Taschenrechner für alles verwenden — einige Formeln im Kopf!',
  'Nie vergessen W÷1000 bei Stromaufgaben',
  'Kein MODE wechseln während einer Rechnung',
  'Nicht verwirren: DEL löscht nur letztes Zeichen, AC alles',
  'Keine Kommas verwenden — nur Punkte (0.32, nicht 0,32)',
  'Nicht vergessen: Ans bezieht sich auf das letzte Ergebnis',
]
</script>
