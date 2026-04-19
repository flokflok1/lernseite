<template>
  <div class="ct">
    <!-- Category tabs -->
    <div class="ct-cats">
      <button v-for="cat in categories" :key="cat.id" class="ct-cat-btn"
        :class="activeCat === cat.id ? 'ct-cat-on' : ''"
        @click="activeCat = cat.id; newExercise()">
        {{ cat.icon }} {{ cat.label }}
      </button>
    </div>

    <!-- Stats -->
    <div class="ct-stats" v-if="statsTotal > 0">
      <span class="ct-stat">🟢 {{ statsGreen }}</span>
      <span class="ct-stat">🟡 {{ statsYellow }}</span>
      <span class="ct-stat">🔴 {{ statsRed }}</span>
      <span class="ct-stat ct-stat-total">· {{ statsTotal }} gerechnet</span>
    </div>

    <!-- Exercise card -->
    <div class="ct-card" v-if="currentExercise">
      <div class="ct-card-cat">{{ currentExercise.catLabel }} <span class="ct-card-pts">{{ currentExercise.pts }} Pkt</span></div>
      <div class="ct-card-q">{{ currentExercise.question }}</div>

      <!-- Casio hint -->
      <div class="ct-casio-hint" v-if="showHint">
        <div class="ct-hint-title">📱 Casio Tipp:</div>
        <div class="ct-hint-steps">{{ currentExercise.casioSteps }}</div>
      </div>
      <button v-if="!showHint && !revealed" class="ct-hint-btn" @click="showHint = true">📱 Casio-Tipp zeigen</button>

      <!-- Input -->
      <div v-if="!revealed" class="ct-input-area">
        <input
          ref="answerInput"
          v-model="userAnswer"
          class="ct-input"
          :placeholder="currentExercise.placeholder || 'Dein Ergebnis...'"
          @keydown.enter="checkAnswer()"
          autofocus
        />
        <div class="ct-input-btns">
          <button class="ct-btn ct-btn-check" @click="checkAnswer()" :disabled="!userAnswer.trim()">
            ✅ Prüfen
          </button>
          <button class="ct-btn ct-btn-skip" @click="skip()">
            ⏭ Skip
          </button>
        </div>
      </div>

      <!-- Result -->
      <div v-if="revealed" class="ct-result">
        <div class="ct-verdict" :class="verdictClass">
          <span>{{ verdictIcon }} {{ verdictText }}</span>
        </div>
        <div class="ct-compare">
          <div class="ct-compare-row">
            <span class="ct-compare-label">Deine Antwort:</span>
            <span class="ct-compare-val ct-user-answer">{{ userAnswer }}</span>
          </div>
          <div class="ct-compare-row">
            <span class="ct-compare-label">Richtig:</span>
            <span class="ct-compare-val ct-correct-answer">{{ currentExercise.answer }}</span>
          </div>
          <div v-if="currentExercise.explanation" class="ct-explanation">
            💡 {{ currentExercise.explanation }}
          </div>
        </div>
        <button class="ct-btn ct-btn-next" @click="newExercise()">→ Nächste Aufgabe</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'

const categories = [
  { id: 'zahlen', icon: '🔢', label: 'Zahlensysteme' },
  { id: 'kalk', icon: '💰', label: 'Kalkulation' },
  { id: 'strom', icon: '⚡', label: 'Stromkosten' },
  { id: 'speicher', icon: '💾', label: 'Speicher' },
  { id: 'netz', icon: '🌐', label: 'Subnetz & Hosts' },
  { id: 'all', icon: '🎲', label: 'Alles mischen' },
]

const activeCat = ref('zahlen')
const userAnswer = ref('')
const revealed = ref(false)
const showHint = ref(false)
const answerInput = ref<HTMLInputElement | null>(null)
const currentExercise = ref<any>(null)

// Stats
const statsGreen = ref(0)
const statsYellow = ref(0)
const statsRed = ref(0)
const statsTotal = computed(() => statsGreen.value + statsYellow.value + statsRed.value)

// ─── EXERCISE GENERATORS ───

function randInt(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

function decToBin(n: number): string {
  return n.toString(2)
}

function decToHex(n: number): string {
  return n.toString(16).toUpperCase()
}

function generateZahlen() {
  const types = [
    () => {
      const n = randInt(1, 255)
      return {
        catLabel: 'Zahlensysteme · Dezimal → Binär',
        question: `Rechne ${n} (dezimal) in Binär um.`,
        answer: decToBin(n),
        casioSteps: `MODE → 4 (BASE-N) → DEC → ${n} eingeben → = → dann BIN drücken`,
        explanation: `Stellenwerte: 128, 64, 32, 16, 8, 4, 2, 1 durchgehen`,
        placeholder: 'Binärzahl eingeben...',
        pts: 4
      }
    },
    () => {
      const n = randInt(1, 255)
      const bin = decToBin(n)
      return {
        catLabel: 'Zahlensysteme · Binär → Dezimal',
        question: `Rechne ${bin} (binär) in Dezimal um.`,
        answer: String(n),
        casioSteps: `MODE → 4 (BASE-N) → BIN → ${bin} eingeben → = → dann DEC drücken`,
        explanation: `Jede 1 mit Stellenwert multiplizieren und addieren`,
        placeholder: 'Dezimalzahl eingeben...',
        pts: 4
      }
    },
    () => {
      const n = randInt(1, 255)
      return {
        catLabel: 'Zahlensysteme · Dezimal → Hexadezimal',
        question: `Rechne ${n} (dezimal) in Hexadezimal um.`,
        answer: decToHex(n),
        casioSteps: `MODE → 4 (BASE-N) → DEC → ${n} eingeben → = → dann HEX drücken`,
        explanation: `Hex-Ziffern: A=10, B=11, C=12, D=13, E=14, F=15`,
        placeholder: 'Hex-Wert eingeben (z.B. 2F)...',
        pts: 4
      }
    },
    () => {
      const n = randInt(1, 255)
      const hex = decToHex(n)
      return {
        catLabel: 'Zahlensysteme · Hexadezimal → Dezimal',
        question: `Rechne ${hex} (hex) in Dezimal um.`,
        answer: String(n),
        casioSteps: `MODE → 4 (BASE-N) → HEX → ${hex} eingeben → = → dann DEC drücken`,
        explanation: `Jede Hex-Stelle × 16^Position, von rechts bei 0 anfangen`,
        placeholder: 'Dezimalzahl eingeben...',
        pts: 4
      }
    },
    () => {
      const n = randInt(1, 255)
      const bin = decToBin(n)
      const hex = decToHex(n)
      return {
        catLabel: 'Zahlensysteme · Binär → Hexadezimal',
        question: `Rechne ${bin} (binär) in Hexadezimal um.`,
        answer: hex,
        casioSteps: `MODE → 4 (BASE-N) → BIN → ${bin} eingeben → = → dann HEX drücken`,
        explanation: `Von rechts in 4er-Gruppen teilen, jede Gruppe = 1 Hex-Ziffer`,
        placeholder: 'Hex-Wert eingeben...',
        pts: 4
      }
    },
  ]
  return types[randInt(0, types.length - 1)]()
}

function generateKalk() {
  const types = [
    () => {
      const listenpreis = randInt(5, 50) * 100
      const rabattPct = randInt(5, 25)
      const skontoPct = randInt(1, 3)
      const lieferkosten = randInt(1, 10) * 10
      const ziel = listenpreis * (1 - rabattPct / 100)
      const bar = ziel * (1 - skontoPct / 100)
      const bezug = bar + lieferkosten
      return {
        catLabel: 'Kalkulation · Bezugspreis',
        question: `Listenpreis: ${listenpreis.toFixed(2)}€\nRabatt: ${rabattPct}%\nSkonto: ${skontoPct}%\nLieferkosten: ${lieferkosten.toFixed(2)}€\n\nBerechne den Bezugspreis.`,
        answer: bezug.toFixed(2),
        casioSteps: `${listenpreis} - ${listenpreis} × ${rabattPct} ÷ 100 = (Zieleinkauf)\nAns - Ans × ${skontoPct} ÷ 100 = (Bareinkauf)\nAns + ${lieferkosten} = (Bezugspreis)`,
        explanation: `Listenpreis ${listenpreis}€ − ${rabattPct}% Rabatt = ${ziel.toFixed(2)}€ − ${skontoPct}% Skonto = ${bar.toFixed(2)}€ + ${lieferkosten}€ Lieferung = ${bezug.toFixed(2)}€`,
        placeholder: 'Bezugspreis in € (z.B. 932.00)...',
        pts: 6
      }
    },
    () => {
      const listenpreis = randInt(5, 50) * 100
      const rabattPct = randInt(5, 25)
      const ziel = listenpreis * (1 - rabattPct / 100)
      return {
        catLabel: 'Kalkulation · Zieleinkaufspreis',
        question: `Listenpreis: ${listenpreis.toFixed(2)}€\nRabatt: ${rabattPct}%\n\nBerechne den Zieleinkaufspreis.`,
        answer: ziel.toFixed(2),
        casioSteps: `${listenpreis} - ${listenpreis} × ${rabattPct} ÷ 100 =\nODER: ${listenpreis} × (1 - ${rabattPct} ÷ 100) =`,
        explanation: `${listenpreis}€ − ${rabattPct}% = ${ziel.toFixed(2)}€`,
        placeholder: 'Zieleinkaufspreis in €...',
        pts: 4
      }
    },
    () => {
      const angebote = [
        { name: 'A', lp: randInt(10, 40) * 100, rabatt: randInt(5, 20), skonto: randInt(1, 3), lieferung: randInt(2, 8) * 10 },
        { name: 'B', lp: randInt(10, 40) * 100, rabatt: randInt(5, 20), skonto: randInt(1, 3), lieferung: randInt(2, 8) * 10 },
      ]
      const bezug = angebote.map(a => {
        const z = a.lp * (1 - a.rabatt / 100)
        const b = z * (1 - a.skonto / 100)
        return { ...a, bezug: b + a.lieferung }
      })
      const guenstig = bezug[0].bezug < bezug[1].bezug ? 'A' : 'B'
      return {
        catLabel: 'Kalkulation · Angebotsvergleich',
        question: `Angebot A: LP ${angebote[0].lp}€, Rabatt ${angebote[0].rabatt}%, Skonto ${angebote[0].skonto}%, Lieferung ${angebote[0].lieferung}€\nAngebot B: LP ${angebote[1].lp}€, Rabatt ${angebote[1].rabatt}%, Skonto ${angebote[1].skonto}%, Lieferung ${angebote[1].lieferung}€\n\nWelches Angebot ist günstiger? (A oder B)`,
        answer: guenstig,
        casioSteps: `Für jedes Angebot: LP - LP×Rabatt% = Ziel\nZiel - Ziel×Skonto% = Bar\nBar + Lieferung = Bezugspreis\nVergleiche beide Bezugspreise`,
        explanation: `Bezugspreis A: ${bezug[0].bezug.toFixed(2)}€ | Bezugspreis B: ${bezug[1].bezug.toFixed(2)}€ → ${guenstig} ist günstiger`,
        placeholder: 'A oder B...',
        pts: 6
      }
    },
  ]
  return types[randInt(0, types.length - 1)]()
}

function generateStrom() {
  const types = [
    () => {
      const watt = randInt(1, 10) * 100
      const stunden = [8, 10, 12, 16, 24][randInt(0, 4)]
      const tage = [220, 250, 300, 365][randInt(0, 3)]
      const preis = [0.25, 0.28, 0.30, 0.32, 0.35][randInt(0, 4)]
      const kw = watt / 1000
      const kosten = kw * stunden * tage * preis
      return {
        catLabel: 'Stromkosten · Jahreskosten',
        question: `Gerät: ${watt} Watt\nBetrieb: ${stunden} Stunden/Tag\nTage/Jahr: ${tage}\nStrompreis: ${preis.toFixed(2)} €/kWh\n\nBerechne die jährlichen Stromkosten.`,
        answer: kosten.toFixed(2),
        casioSteps: `${watt} ÷ 1000 × ${stunden} × ${tage} × ${preis} =\n(Watt→kW, dann × Stunden × Tage × Preis)`,
        explanation: `${kw} kW × ${stunden}h × ${tage} Tage × ${preis}€ = ${kosten.toFixed(2)}€`,
        placeholder: 'Jahreskosten in € (z.B. 1314.00)...',
        pts: 4
      }
    },
    () => {
      const geraete = [
        { name: 'Server', watt: randInt(3, 8) * 100 },
        { name: 'Switch', watt: randInt(1, 3) * 50 },
        { name: 'Monitor', watt: randInt(2, 5) * 10 },
      ]
      const g = geraete[randInt(0, geraete.length - 1)]
      const stunden = 24
      const preis = [0.25, 0.28, 0.30, 0.32][randInt(0, 3)]
      const kw = g.watt / 1000
      const monat = kw * stunden * 30 * preis
      return {
        catLabel: 'Stromkosten · Monatskosten',
        question: `${g.name}: ${g.watt} Watt\nBetrieb: 24/7\nStrompreis: ${preis.toFixed(2)} €/kWh\n\nBerechne die monatlichen Stromkosten (30 Tage).`,
        answer: monat.toFixed(2),
        casioSteps: `${g.watt} ÷ 1000 × 24 × 30 × ${preis} =`,
        explanation: `${kw} kW × 24h × 30 Tage × ${preis}€ = ${monat.toFixed(2)}€`,
        placeholder: 'Monatskosten in €...',
        pts: 4
      }
    },
  ]
  return types[randInt(0, types.length - 1)]()
}

function generateSpeicher() {
  const types = [
    () => {
      const exp = randInt(1, 4)
      const labels = ['KB', 'MB', 'GB', 'TB']
      const val = randInt(1, 16)
      const bytes = val * Math.pow(1024, exp)
      return {
        catLabel: 'Speicher · Umrechnung',
        question: `Wie viele Byte sind ${val} ${labels[exp - 1]}?`,
        answer: String(bytes),
        casioSteps: `${val} × 1024 x^ ${exp} =\n(1024^${exp} für ${labels[exp - 1]})`,
        explanation: `${val} × 1024^${exp} = ${bytes.toLocaleString('de-DE')} Byte`,
        placeholder: 'Anzahl Byte...',
        pts: 3
      }
    },
    () => {
      const bytes = randInt(1, 16) * 1024 * 1024
      const mb = bytes / (1024 * 1024)
      return {
        catLabel: 'Speicher · Umrechnung',
        question: `Wie viele MB sind ${bytes.toLocaleString('de-DE')} Byte?`,
        answer: String(mb),
        casioSteps: `${bytes} ÷ 1024 ÷ 1024 =\nODER: ${bytes} ÷ 1024 x^ 2 =`,
        explanation: `${bytes.toLocaleString('de-DE')} ÷ 1024 ÷ 1024 = ${mb} MB`,
        placeholder: 'Anzahl MB...',
        pts: 3
      }
    },
    () => {
      const bits = randInt(1, 64) * 8
      const bytes = bits / 8
      return {
        catLabel: 'Speicher · Bit & Byte',
        question: `Wie viele Byte sind ${bits} Bit?`,
        answer: String(bytes),
        casioSteps: `${bits} ÷ 8 =`,
        explanation: `8 Bit = 1 Byte → ${bits} ÷ 8 = ${bytes} Byte`,
        placeholder: 'Anzahl Byte...',
        pts: 3
      }
    },
    () => {
      const n = randInt(1, 12)
      const result = Math.pow(2, n)
      return {
        catLabel: 'Speicher · 2er-Potenzen',
        question: `Was ist 2^${n}?`,
        answer: String(result),
        casioSteps: `2 x^ ${n} =`,
        explanation: `2^${n} = ${result}`,
        placeholder: 'Ergebnis...',
        pts: 2
      }
    },
  ]
  return types[randInt(0, types.length - 1)]()
}

function generateNetz() {
  const types = [
    () => {
      const cidr = [24, 25, 26, 27, 28, 29, 30][randInt(0, 6)]
      const hostBits = 32 - cidr
      const hosts = Math.pow(2, hostBits) - 2
      return {
        catLabel: 'Subnetz · Hosts berechnen',
        question: `Wie viele nutzbare Hosts hat ein /${cidr} Subnetz?`,
        answer: String(hosts),
        casioSteps: `2 x^ ${hostBits} - 2 =\n(32 - ${cidr} = ${hostBits} Hostbits)`,
        explanation: `/${cidr} → ${hostBits} Hostbits → 2^${hostBits} - 2 = ${hosts} Hosts`,
        placeholder: 'Anzahl Hosts...',
        pts: 4
      }
    },
    () => {
      const cidr = [24, 25, 26, 27, 28][randInt(0, 4)]
      const hostBits = 32 - cidr
      const blockSize = Math.pow(2, hostBits)
      const masks: Record<number, string> = { 24: '255.255.255.0', 25: '255.255.255.128', 26: '255.255.255.192', 27: '255.255.255.224', 28: '255.255.255.240' }
      return {
        catLabel: 'Subnetz · Subnetzmaske',
        question: `Wie lautet die Subnetzmaske für /${cidr}?`,
        answer: masks[cidr],
        casioSteps: `/${cidr} → ${cidr} Bits auf 1 gesetzt\n256 - 2^${hostBits} = ${256 - blockSize} → letzes Oktett`,
        explanation: `/${cidr} = ${masks[cidr]} (Blockgröße: ${blockSize})`,
        placeholder: 'z.B. 255.255.255.0...',
        pts: 4
      }
    },
    () => {
      const gesamtH = [8760, 8760, 720, 720][randInt(0, 3)]
      const zeitLabel = gesamtH > 1000 ? 'Jahr (8760h)' : 'Monat (720h)'
      const ausfallH = [0.876, 4.38, 8.76, 43.8, 0.72, 3.6, 7.2][randInt(0, 6)]
      const actualAusfall = gesamtH > 1000 ? ausfallH : ausfallH
      const verf = ((gesamtH - actualAusfall) / gesamtH * 100)
      const verfStr = verf.toFixed(2)
      return {
        catLabel: 'Verfügbarkeit · Prozent',
        question: `Gesamtzeit: ${gesamtH}h (${zeitLabel})\nAusfallzeit: ${actualAusfall}h\n\nBerechne die Verfügbarkeit in %.`,
        answer: verfStr,
        casioSteps: `(${gesamtH} - ${actualAusfall}) ÷ ${gesamtH} × 100 =`,
        explanation: `(${gesamtH} - ${actualAusfall}) ÷ ${gesamtH} × 100 = ${verfStr}%`,
        placeholder: 'Verfügbarkeit in % (z.B. 99.90)...',
        pts: 3
      }
    },
  ]
  return types[randInt(0, types.length - 1)]()
}

function generateExercise() {
  const generators: Record<string, () => any> = {
    zahlen: generateZahlen,
    kalk: generateKalk,
    strom: generateStrom,
    speicher: generateSpeicher,
    netz: generateNetz,
  }
  if (activeCat.value === 'all') {
    const keys = Object.keys(generators)
    return generators[keys[randInt(0, keys.length - 1)]]()
  }
  return generators[activeCat.value]()
}

function newExercise() {
  currentExercise.value = generateExercise()
  userAnswer.value = ''
  revealed.value = false
  showHint.value = false
  nextTick(() => answerInput.value?.focus())
}

function normalize(s: string): string {
  return s.trim().toUpperCase().replace(/\s+/g, '').replace(/,/g, '.')
}

function checkAnswer() {
  if (!userAnswer.value.trim()) return
  revealed.value = true
  const user = normalize(userAnswer.value)
  const correct = normalize(currentExercise.value.answer)
  if (user === correct) {
    statsGreen.value++
  } else {
    // Allow small rounding differences for decimal answers
    const userNum = parseFloat(user)
    const correctNum = parseFloat(correct)
    if (!isNaN(userNum) && !isNaN(correctNum) && Math.abs(userNum - correctNum) < 0.1) {
      statsGreen.value++
    } else if (!isNaN(userNum) && !isNaN(correctNum) && Math.abs(userNum - correctNum) < correctNum * 0.05) {
      statsYellow.value++
    } else {
      statsRed.value++
    }
  }
}

function skip() {
  revealed.value = true
  statsRed.value++
}

const verdictClass = computed(() => {
  if (!revealed.value) return ''
  const user = normalize(userAnswer.value)
  const correct = normalize(currentExercise.value.answer)
  if (user === correct) return 'ct-verdict-green'
  const userNum = parseFloat(user)
  const correctNum = parseFloat(correct)
  if (!isNaN(userNum) && !isNaN(correctNum) && Math.abs(userNum - correctNum) < 0.1) return 'ct-verdict-green'
  if (!isNaN(userNum) && !isNaN(correctNum) && Math.abs(userNum - correctNum) < correctNum * 0.05) return 'ct-verdict-yellow'
  return 'ct-verdict-red'
})

const verdictIcon = computed(() => {
  if (verdictClass.value === 'ct-verdict-green') return '🟢'
  if (verdictClass.value === 'ct-verdict-yellow') return '🟡'
  return '🔴'
})

const verdictText = computed(() => {
  if (verdictClass.value === 'ct-verdict-green') return 'Richtig!'
  if (verdictClass.value === 'ct-verdict-yellow') return 'Fast richtig!'
  return 'Falsch'
})

// Init
newExercise()
</script>

<style scoped>
.ct { display: flex; flex-direction: column; gap: 14px; }

.ct-cats { display: flex; gap: 6px; flex-wrap: wrap; }
.ct-cat-btn {
  padding: 8px 12px; border-radius: 10px; border: 1px solid var(--color-border);
  background: var(--color-surface); color: var(--color-text-secondary);
  cursor: pointer; font-size: 12px; font-weight: 600; transition: all 0.15s;
}
.ct-cat-btn:hover { border-color: #a78bfa; }
.ct-cat-on { border-color: #a78bfa !important; background: rgba(167,139,250,0.2) !important; color: #c4b5fd !important; }

.ct-stats { display: flex; gap: 12px; align-items: center; font-size: 13px; padding: 4px 0; }
.ct-stat { font-weight: 500; }
.ct-stat-total { color: var(--color-text-secondary); }

.ct-card {
  border-radius: 16px; padding: 24px; display: flex; flex-direction: column; gap: 12px;
  background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(167,139,250,0.08));
  border: 1px solid var(--color-border);
}
.ct-card-cat { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #a78bfa; }
.ct-card-pts { font-size: 11px; font-weight: 700; color: #facc15; background: rgba(250,204,21,0.15); padding: 2px 8px; border-radius: 6px; }
.ct-card-q { font-size: 16px; font-weight: 700; color: var(--color-text); line-height: 1.6; white-space: pre-line; }

.ct-casio-hint {
  background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3);
  border-radius: 10px; padding: 12px;
}
.ct-hint-title { font-size: 12px; font-weight: 700; color: #22c55e; margin-bottom: 4px; }
.ct-hint-steps { font-size: 13px; color: var(--color-text); font-family: 'Courier New', monospace; white-space: pre-line; line-height: 1.6; }

.ct-hint-btn {
  padding: 8px 14px; border-radius: 8px; border: 1px solid rgba(34,197,94,0.3);
  background: rgba(34,197,94,0.1); color: #22c55e; cursor: pointer; font-size: 12px;
  font-weight: 600; align-self: flex-start; transition: all 0.15s;
}
.ct-hint-btn:hover { background: rgba(34,197,94,0.2); }

.ct-input-area { display: flex; flex-direction: column; gap: 10px; }
.ct-input {
  width: 100%; padding: 14px; border-radius: 10px; border: 2px solid var(--color-border);
  background: var(--color-background); color: var(--color-text); font-size: 16px;
  font-family: 'Courier New', monospace; font-weight: 700; transition: border-color 0.2s;
  box-sizing: border-box;
}
.ct-input:focus { outline: none; border-color: #a78bfa; }
.ct-input::placeholder { font-family: inherit; font-weight: 400; font-size: 13px; }

.ct-input-btns { display: flex; gap: 8px; }
.ct-btn {
  padding: 10px 18px; border-radius: 10px; border: none; cursor: pointer;
  font-weight: 700; font-size: 13px; transition: all 0.15s;
}
.ct-btn-check { background: linear-gradient(135deg, #6366f1, #a78bfa); color: white; flex: 1; }
.ct-btn-check:hover { opacity: 0.9; }
.ct-btn-check:disabled { opacity: 0.4; cursor: not-allowed; }
.ct-btn-skip { background: var(--color-surface); color: var(--color-text-secondary); border: 1px solid var(--color-border); }
.ct-btn-skip:hover { border-color: #a78bfa; }
.ct-btn-next { background: linear-gradient(135deg, #6366f1, #a78bfa); color: white; }
.ct-btn-next:hover { opacity: 0.9; }

.ct-result { display: flex; flex-direction: column; gap: 12px; }
.ct-verdict {
  padding: 10px 16px; border-radius: 10px; font-weight: 700; font-size: 15px;
}
.ct-verdict-green { background: rgba(34,197,94,0.15); color: #22c55e; }
.ct-verdict-yellow { background: rgba(250,204,21,0.15); color: #eab308; }
.ct-verdict-red { background: rgba(239,68,68,0.15); color: #ef4444; }

.ct-compare { display: flex; flex-direction: column; gap: 6px; }
.ct-compare-row { display: flex; gap: 8px; font-size: 14px; }
.ct-compare-label { color: var(--color-text-secondary); min-width: 120px; }
.ct-compare-val { font-weight: 700; font-family: 'Courier New', monospace; }
.ct-user-answer { color: var(--color-text); }
.ct-correct-answer { color: #22c55e; }
.ct-explanation {
  font-size: 12px; color: var(--color-text-secondary); margin-top: 4px;
  padding: 8px 12px; background: var(--color-surface); border-radius: 8px;
}
</style>
