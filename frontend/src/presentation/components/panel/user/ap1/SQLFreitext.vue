<template>
  <div class="sql-wrap">
    <!-- Header -->
    <div class="sql-header">
      <div>
        <h2 class="sql-title">🗄️ SQL Freitext-Übungen</h2>
        <p class="sql-sub">Schreibe SQL-Befehle selbst – wie in der BW AP1-Prüfung!</p>
      </div>
      <LumiHint
        :context="`SQL-Übung ${currentIdx + 1}/${exercises.length}: ${current?.question?.slice(0, 80)}... Schema: ${current?.schema?.split('\n')[0]}`"
        systemExtra="Erkläre die SQL-Syntax die für diese Aufgabe gebraucht wird. Gib einen Hinweis auf die Schlüsselwörter ohne die komplette Lösung zu verraten."
      />
    </div>

    <!-- Exercise Navigation -->
    <div class="sql-nav">
      <button v-for="(q, idx) in exercises" :key="idx"
        class="sql-nav-btn"
        :class="[
          currentIdx === idx ? 'sql-nav-active' : '',
          answered[idx] ? 'sql-nav-done' : '',
          q.difficulty === 'schwer' ? 'sql-nav-hard' : q.difficulty === 'mittel' ? 'sql-nav-mid' : ''
        ]"
        @click="goTo(idx)">
        {{ idx + 1 }}
      </button>
    </div>

    <div v-if="current" class="sql-content">
      <!-- Schema -->
      <div class="sql-schema">
        <div class="sql-schema-label">📋 Tabellen-Schema:</div>
        <pre class="sql-schema-code">{{ current.schema }}</pre>
      </div>

      <!-- Task -->
      <div class="sql-task">
        <div class="sql-task-header">
          <span class="sql-diff-badge" :class="`sql-diff-${current.difficulty}`">{{ current.difficulty }}</span>
          <span class="sql-task-num">Aufgabe {{ currentIdx + 1 }}/{{ exercises.length }}</span>
        </div>
        <div class="sql-task-text">{{ current.question }}</div>
      </div>

      <!-- SQL Editor -->
      <div class="sql-editor-wrap">
        <div class="sql-editor-bar">
          <span class="sql-editor-lang">SQL</span>
          <span v-if="answered[currentIdx]" class="sql-editor-score">
            {{ scores[currentIdx] >= 7 ? '✅' : scores[currentIdx] >= 4 ? '⚠️' : '❌' }}
            {{ scores[currentIdx] }}/10 Punkte
          </span>
        </div>
        <textarea
          v-model="userSQL"
          rows="5"
          class="sql-editor"
          placeholder="SELECT ..."
          :disabled="answered[currentIdx]"
          spellcheck="false"
        ></textarea>
      </div>

      <!-- Actions -->
      <div class="sql-actions">
        <button v-if="!answered[currentIdx]"
          class="sql-btn-check"
          :disabled="!userSQL.trim()"
          @click="checkSQL">
          ▶ Ausführen & Prüfen
        </button>
        <button class="sql-btn-solution" @click="showSolution = !showSolution">
          {{ showSolution ? '🙈 Lösung verbergen' : '💡 Musterlösung' }}
        </button>
        <button v-if="currentIdx < exercises.length - 1" class="sql-btn-next" @click="goTo(currentIdx + 1)">
          Weiter →
        </button>
      </div>

      <!-- Feedback Keywords -->
      <div v-if="answered[currentIdx]" class="sql-feedback"
        :class="scores[currentIdx] >= 7 ? 'sql-fb-good' : scores[currentIdx] >= 4 ? 'sql-fb-ok' : 'sql-fb-bad'">
        <div class="sql-fb-score">
          {{ scores[currentIdx] >= 8 ? '🏆 Sehr gut!' : scores[currentIdx] >= 5 ? '👍 Gut!' : '📚 Noch üben!' }}
          &nbsp;{{ scores[currentIdx] }}/10 Punkten
        </div>
        <div class="sql-kw-list">
          <span v-for="kw in current.keywords" :key="kw"
            class="sql-kw"
            :class="userSQL.toUpperCase().includes(kw.toUpperCase()) ? 'sql-kw-hit' : 'sql-kw-miss'">
            {{ userSQL.toUpperCase().includes(kw.toUpperCase()) ? '✓' : '✗' }} {{ kw }}
          </span>
        </div>
      </div>

      <!-- Solution -->
      <transition name="slide">
        <div v-if="showSolution" class="sql-solution">
          <div class="sql-solution-label">📋 Musterlösung:</div>
          <pre class="sql-solution-code">{{ current.solution }}</pre>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import LumiHint from '@/presentation/components/panel/user/ap1/LumiHint.vue'

const emit = defineEmits<{ score: [points: number] }>()

interface SQLExercise {
  schema: string
  question: string
  solution: string
  keywords: string[]
  difficulty: string
}

const exercises: SQLExercise[] = [
  {
    schema: 'mitarbeiter(m_id INT, vorname VARCHAR, nachname VARCHAR, abteilung_id INT)\nabteilung(abt_id INT, bezeichnung VARCHAR)',
    question: 'Zeige alle Mitarbeiter mit Vor- und Nachname, sortiert nach Nachname aufsteigend.',
    solution: 'SELECT vorname, nachname\nFROM mitarbeiter\nORDER BY nachname ASC;',
    keywords: ['SELECT', 'FROM', 'mitarbeiter', 'ORDER BY', 'nachname'],
    difficulty: 'leicht',
  },
  {
    schema: 'mitarbeiter(m_id INT, vorname VARCHAR, nachname VARCHAR, abteilung_id INT)\nabteilung(abt_id INT, bezeichnung VARCHAR)',
    question: 'Zeige die Anzahl der Mitarbeiter pro Abteilung (Abteilungsbezeichnung + Anzahl).',
    solution: 'SELECT a.bezeichnung, COUNT(*) AS anzahl\nFROM mitarbeiter m\nJOIN abteilung a ON m.abteilung_id = a.abt_id\nGROUP BY a.bezeichnung;',
    keywords: ['SELECT', 'COUNT', 'JOIN', 'abteilung', 'GROUP BY'],
    difficulty: 'mittel',
  },
  {
    schema: 'laptop(laptop_id INT, marke VARCHAR, modell VARCHAR, kaufjahr INT, m_id INT)\nmitarbeiter(m_id INT, vorname VARCHAR, nachname VARCHAR)',
    question: 'Füge einen neuen Laptop ein: ID 101, Marke "Lenovo", Modell "ThinkPad X1", Kaufjahr 2024, zugewiesen an Mitarbeiter 5.',
    solution: "INSERT INTO laptop (laptop_id, marke, modell, kaufjahr, m_id)\nVALUES (101, 'Lenovo', 'ThinkPad X1', 2024, 5);",
    keywords: ['INSERT', 'INTO', 'laptop', 'VALUES'],
    difficulty: 'leicht',
  },
  {
    schema: 'projekt(projekt_id INT, bezeichnung VARCHAR, dauer DOUBLE)\nmitarbeiter_projekt(m_id INT, projekt_id INT)',
    question: 'Lösche alle Projekte mit einer Dauer von mehr als 12 Monaten.',
    solution: 'DELETE FROM projekt\nWHERE dauer > 12;',
    keywords: ['DELETE', 'FROM', 'projekt', 'WHERE', 'dauer'],
    difficulty: 'leicht',
  },
  {
    schema: 'mitarbeiter(m_id INT, vorname VARCHAR, nachname VARCHAR, abteilung_id INT)\nlaptop(laptop_id INT, marke VARCHAR, modell VARCHAR, kaufjahr INT, m_id INT)',
    question: 'Zeige alle Mitarbeiter mit ihren Laptops (Vor-/Nachname, Marke, Modell). Auch Mitarbeiter OHNE Laptop sollen angezeigt werden.',
    solution: 'SELECT m.vorname, m.nachname, l.marke, l.modell\nFROM mitarbeiter m\nLEFT JOIN laptop l ON m.m_id = l.m_id;',
    keywords: ['SELECT', 'LEFT JOIN', 'laptop', 'mitarbeiter', 'ON'],
    difficulty: 'schwer',
  },
  {
    schema: 'mitarbeiter(m_id INT, vorname VARCHAR, nachname VARCHAR, gehalt DECIMAL)\nabteilung(abt_id INT, bezeichnung VARCHAR)',
    question: 'Ändere das Gehalt aller Mitarbeiter in Abteilung 3: Erhöhe es um 5%.',
    solution: 'UPDATE mitarbeiter\nSET gehalt = gehalt * 1.05\nWHERE abteilung_id = 3;',
    keywords: ['UPDATE', 'SET', 'gehalt', 'WHERE', 'abteilung_id'],
    difficulty: 'mittel',
  },
  {
    schema: 'laptop(laptop_id INT, marke VARCHAR, modell VARCHAR, kaufjahr INT, m_id INT)',
    question: 'Zeige die Anzahl der Laptops pro Marke, aber nur Marken mit mehr als 2 Laptops.',
    solution: 'SELECT marke, COUNT(*) AS anzahl\nFROM laptop\nGROUP BY marke\nHAVING COUNT(*) > 2;',
    keywords: ['SELECT', 'COUNT', 'GROUP BY', 'HAVING', 'marke'],
    difficulty: 'schwer',
  },
  {
    schema: '-- Theorie: Normalisierung',
    question: 'Nenne und erkläre die 3 Anomalien, die bei nicht normalisierter Datenbank entstehen können.',
    solution: '1. Einfügeanomalie: Neue Daten können nicht eingefügt werden, ohne andere (evtl. unbekannte) Daten anzugeben.\n2. Löschanomalie: Beim Löschen eines Datensatzes gehen ungewollt andere Informationen verloren.\n3. Änderungsanomalie: Beim Ändern eines Wertes müssen mehrere Datensätze geändert werden (Redundanz) → Inkonsistenz möglich.',
    keywords: ['Einfügeanomalie', 'Löschanomalie', 'Änderungsanomalie', 'Redundanz', 'Inkonsistenz'],
    difficulty: 'mittel',
  },
  {
    schema: '-- Theorie: Normalisierung\nBestellung(BestellNr, KundenNr, KundenName, KundenOrt, ArtikelNr, ArtikelName, Menge, Preis)',
    question: 'Die Tabelle Bestellung ist nicht in 1NF, 2NF und 3NF. Welche Normalform wird zuerst verletzt und warum?\nHinweis: BestellNr ist Primärschlüssel. KundenName hängt von KundenNr ab (nicht von BestellNr).',
    solution: '2NF wird verletzt: KundenName und KundenOrt hängen nur von KundenNr ab (Teilschlüsselabhängigkeit), nicht vom gesamten Primärschlüssel BestellNr.\nFix: Kunden-Tabelle auslagern → Kunden(KundenNr, KundenName, KundenOrt).\n\n3NF wäre auch verletzt wenn z.B. KundenOrt → Postleitzahl (transitive Abhängigkeit).\n\n1NF ist erfüllt wenn alle Felder atomar sind.',
    keywords: ['2NF', 'Teilschlüssel', 'KundenNr', 'KundenName', 'auslagern', 'Abhängigkeit'],
    difficulty: 'schwer',
  },
  {
    schema: '-- Theorie: Normalformen im Überblick',
    question: 'Erkläre kurz 1NF, 2NF und 3NF in je einem Satz.',
    solution: '1NF (Erste Normalform): Alle Attributwerte sind atomar (keine Wiederholungsgruppen, keine Listen in einer Zelle).\n2NF (Zweite Normalform): 1NF + jedes Nicht-Schlüsselattribut ist voll funktional abhängig vom gesamten Primärschlüssel (keine Teilabhängigkeiten).\n3NF (Dritte Normalform): 2NF + kein Nicht-Schlüsselattribut ist transitiv abhängig vom Primärschlüssel (A→B→C ist verboten wenn B kein Schlüssel ist).',
    keywords: ['atomar', 'voll funktional', 'Teilabhängigkeit', 'transitiv', 'Primärschlüssel'],
    difficulty: 'mittel',
  },
  {
    schema: 'wartung(wartung_id INT PK, geraet_id INT, geraet_name VARCHAR, techniker_id INT, techniker_name VARCHAR, datum DATE)',
    question: 'Prüfe die Tabelle "wartung" auf Normalisierungsverstöße bis 3NF. geraet_name hängt von geraet_id ab, techniker_name von techniker_id.',
    solution: '2NF-Verstoß: geraet_name hängt nur von geraet_id ab (nicht von wartung_id). techniker_name hängt nur von techniker_id ab.\n→ Fix: Auslagern in Geraet(geraet_id PK, geraet_name) und Techniker(techniker_id PK, techniker_name).\n\nErgebnis nach Normalisierung:\nwartung(wartung_id PK, geraet_id FK, techniker_id FK, datum)\ngeraet(geraet_id PK, geraet_name)\ntechniker(techniker_id PK, techniker_name)',
    keywords: ['geraet_id', 'techniker_id', 'auslagern', 'Fremdschlüssel', '2NF', 'Teilabhängigkeit'],
    difficulty: 'schwer',
  },

]

const currentIdx = ref(0)
const userSQL = ref('')
const showSolution = ref(false)
const answered = reactive<Record<number, boolean>>({})
const scores = reactive<Record<number, number>>({})

const current = computed(() => exercises[currentIdx.value])

function goTo(idx: number) {
  currentIdx.value = idx
  userSQL.value = ''
  showSolution.value = false
}

function checkSQL() {
  if (!userSQL.value.trim()) return
  const q = current.value
  const upper = userSQL.value.toUpperCase()
  let found = 0
  q.keywords.forEach(kw => { if (upper.includes(kw.toUpperCase())) found++ })
  const pct = found / q.keywords.length
  let pts = Math.round(pct * 10)
  scores[currentIdx.value] = pts
  answered[currentIdx.value] = true
  emit('score', pts)
}
</script>

<style scoped>
.sql-wrap { max-width: 860px; }

.sql-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 16px; gap: 12px;
}
.sql-title { font-size: 20px; font-weight: 800; color: var(--color-text-primary); margin: 0 0 4px; }
.sql-sub { font-size: 13px; color: var(--color-text-secondary); margin: 0; }

/* Navigation */
.sql-nav { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.sql-nav-btn {
  width: 34px; height: 34px; border-radius: 8px; font-size: 13px; font-weight: 700;
  border: 1.5px solid var(--color-border); background: var(--color-surface);
  color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; justify-content: center;
}
.sql-nav-btn:hover { border-color: #a78bfa; color: #c4b5fd; }
.sql-nav-active { background: #6d28d9 !important; border-color: #7c3aed !important; color: white !important; }
.sql-nav-done { background: rgba(34,197,94,0.1) !important; border-color: #22c55e !important; color: #4ade80 !important; }
.sql-nav-hard { border-color: #ef4444; color: #f87171; }
.sql-nav-mid { border-color: #f59e0b; color: #fcd34d; }

/* Schema */
.sql-schema {
  background: #0f172a; border: 1px solid #334155;
  border-radius: 10px; padding: 14px; margin-bottom: 12px;
}
.sql-schema-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.sql-schema-code {
  font-family: 'Consolas', 'Monaco', monospace; font-size: 13px;
  color: #7dd3fc; margin: 0; white-space: pre-wrap;
}

/* Task */
.sql-task {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 10px; padding: 14px; margin-bottom: 12px;
}
.sql-task-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.sql-diff-badge {
  padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase;
}
.sql-diff-leicht { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid #22c55e; }
.sql-diff-mittel { background: rgba(245,158,11,0.15); color: #fcd34d; border: 1px solid #f59e0b; }
.sql-diff-schwer { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid #ef4444; }
.sql-task-num { font-size: 12px; color: var(--color-text-secondary); margin-left: auto; }
.sql-task-text { font-size: 14px; color: var(--color-text-primary); line-height: 1.6; font-weight: 500; }

/* Editor */
.sql-editor-wrap {
  border: 2px solid var(--color-border); border-radius: 10px; overflow: hidden;
  margin-bottom: 12px; background: #0f172a;
}
.sql-editor-bar {
  background: #1e293b; padding: 6px 14px; display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid #334155;
}
.sql-editor-lang { font-size: 11px; font-weight: 700; color: #7dd3fc; text-transform: uppercase; letter-spacing: 1px; }
.sql-editor-score { font-size: 12px; font-weight: 700; color: #a5b4fc; }
.sql-editor {
  width: 100%; padding: 14px; background: #0f172a; color: #e2e8f0;
  font-family: 'Consolas', 'Monaco', monospace; font-size: 14px; border: none;
  outline: none; resize: vertical; box-sizing: border-box; line-height: 1.6;
}
.sql-editor:disabled { opacity: 0.7; cursor: default; }

/* Actions */
.sql-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.sql-btn-check {
  padding: 9px 20px; background: #7c3aed; color: white; border: none;
  border-radius: 8px; font-weight: 700; font-size: 14px; cursor: pointer; transition: all 0.15s;
}
.sql-btn-check:hover:not(:disabled) { background: #6d28d9; }
.sql-btn-check:disabled { opacity: 0.4; cursor: not-allowed; }
.sql-btn-solution {
  padding: 9px 18px; background: rgba(139,92,246,0.1); color: #c4b5fd;
  border: 1px solid rgba(139,92,246,0.4); border-radius: 8px; font-weight: 600;
  font-size: 14px; cursor: pointer; transition: all 0.15s;
}
.sql-btn-solution:hover { background: rgba(139,92,246,0.2); }
.sql-btn-next {
  padding: 9px 18px; background: var(--color-surface); color: var(--color-text-secondary);
  border: 1px solid var(--color-border); border-radius: 8px; font-weight: 600;
  font-size: 14px; cursor: pointer; transition: all 0.15s; margin-left: auto;
}
.sql-btn-next:hover { border-color: #7c3aed; color: #c4b5fd; }

/* Feedback */
.sql-feedback {
  border-radius: 10px; padding: 14px; margin-bottom: 12px; border: 1.5px solid;
}
.sql-fb-good { background: rgba(34,197,94,0.08); border-color: #22c55e; }
.sql-fb-ok { background: rgba(245,158,11,0.08); border-color: #f59e0b; }
.sql-fb-bad { background: rgba(239,68,68,0.08); border-color: #ef4444; }
.sql-fb-score { font-size: 15px; font-weight: 800; color: var(--color-text-primary); margin-bottom: 10px; }
.sql-kw-list { display: flex; flex-wrap: wrap; gap: 6px; }
.sql-kw {
  padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;
  font-family: monospace; border: 1px solid;
}
.sql-kw-hit { background: rgba(34,197,94,0.12); border-color: #22c55e; color: #4ade80; }
.sql-kw-miss { background: rgba(239,68,68,0.1); border-color: #ef4444; color: #f87171; }

/* Solution */
.sql-solution {
  background: #0f172a; border: 1.5px solid #22c55e; border-radius: 10px; padding: 14px;
}
.sql-solution-label { font-size: 11px; font-weight: 700; color: #4ade80; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.sql-solution-code {
  font-family: 'Consolas', 'Monaco', monospace; font-size: 14px;
  color: #86efac; margin: 0; white-space: pre-wrap; line-height: 1.6;
}

.slide-enter-active, .slide-leave-active { transition: all 0.25s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
