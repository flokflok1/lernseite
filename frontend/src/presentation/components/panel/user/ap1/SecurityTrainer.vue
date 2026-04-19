<template>
  <div>
    <h2 class="text-xl font-bold text-[var(--color-text-primary)] mb-2">IT-Sicherheit Training</h2>
    <p class="text-[var(--color-text-secondary)] mb-6">CIA-Triade, Verschluesselung, DSGVO, Firewall - alles was du fuer die AP1 brauchst</p>

    <div class="space-y-6">
      <div v-for="(q, idx) in questions" :key="idx"
        class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5">
        <div class="flex items-center gap-2 mb-3">
          <span class="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-bold">{{ q.topic }}</span>
        </div>
        <div class="text-[var(--color-text-primary)] font-semibold mb-4">{{ q.question }}</div>

        <div v-if="q.type === 'mc'" class="space-y-2">
          <button v-for="(opt, oi) in q.options" :key="oi"
            class="w-full text-left p-3 border-2 rounded-lg transition-colors font-medium text-sm"
            :class="selected[idx] === oi
              ? (oi === q.correct ? 'border-green-500 bg-green-50 text-green-700' : 'border-red-500 bg-red-50 text-red-700')
              : 'border-[var(--color-border)] hover:border-primary-400 text-[var(--color-text-primary)]'"
            :disabled="selected[idx] !== undefined"
            @click="selectAnswer(idx, oi, q.correct)">
            {{ opt }}
          </button>
        </div>

        <div v-else>
          <textarea v-model="textAnswers[idx]" rows="3"
            class="w-full p-3 border-2 border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:border-primary-500 focus:outline-none text-sm"
            placeholder="Deine Antwort..."
            :disabled="textChecked[idx]"></textarea>
          <button v-if="!textChecked[idx]"
            class="mt-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700"
            @click="checkText(idx)">Pruefen</button>
        </div>

        <!-- Show solution after answering -->
        <div v-if="selected[idx] !== undefined || textChecked[idx]"
          class="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800">
          <span class="font-bold">Erklaerung: </span>{{ q.explanation }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const emit = defineEmits<{ score: [points: number] }>()

const questions = [
  {
    type: 'mc', topic: 'RAID',
    question: 'Welches RAID bietet Schutz bei Ausfall EINES Laufwerks, mind. 3 Platten, Parität verteilt?',
    options: ['RAID 0 – Striping, kein Schutz', 'RAID 1 – Mirroring, 2 Platten', 'RAID 5 – Striping + verteilte Parität', 'RAID 6 – 2 Paritätsblöcke'],
    correct: 2,
    explanation: 'RAID 5: mind. 3 Platten, 1 darf ausfallen. Nettospeicher = (n−1) × Plattengröße. RAID 0: kein Schutz. RAID 1: Spiegelung, 50% Kapazität. RAID 6: 2 Platten dürfen ausfallen. AP1-Tipp: „bei Ausfall eines Laufwerks kein Totalverlust" → RAID 1, 5 oder 10.',
  },
  {
    type: 'mc', topic: 'RAID',
    question: 'Du hast 4 × 2 TB in RAID 5. Wie viel Nettokapazität steht zur Verfügung?',
    options: ['8 TB (alle Platten)', '6 TB (n−1 Platten)', '4 TB (Hälfte)', '2 TB (1 Platte)'],
    correct: 1,
    explanation: 'RAID 5: Nettokapazität = (Anzahl − 1) × Plattengröße → (4−1) × 2 TB = 6 TB. Eine Platte "opfert" sich für die Parität – dafür kannst du bei einem Ausfall alles rekonstruieren.',
  },
  {
    type: 'mc', topic: 'Firewall',
    question: 'Was unterscheidet einstufiges von zweistufigem Firewall-Konzept?',
    options: [
      'Einstufig: 1 Firewall (intern/extern). Zweistufig: 2 Firewalls + DMZ dazwischen.',
      'Einstufig: Hardware-Firewall. Zweistufig: Software-Firewall.',
      'Kein Unterschied, nur andere Bezeichnung.'
    ],
    correct: 0,
    explanation: 'Einstufig: eine Firewall = eine Sicherheitsgrenze. Zweistufig: zwei Firewalls bilden eine DMZ (Demilitarisierte Zone). Server die von außen erreichbar sein müssen (Webserver, Mailserver) stehen in der DMZ – das interne Netz bleibt trotzdem geschützt.',
  },
  {
    type: 'mc', topic: 'VPN',
    question: 'Welcher VPN-Typ verbindet zwei Firmenstandorte dauerhaft (Filiale ↔ Zentrale)?',
    options: ['Remote-Access-VPN (Einzelperson wählt sich ein)', 'Site-to-Site-VPN (Netz zu Netz)', 'SSL-VPN (nur Browser-basiert)'],
    correct: 1,
    explanation: 'Site-to-Site-VPN: verbindet zwei komplette Netze dauerhaft. Remote-Access: Einzelne Nutzer wählen sich ein (z.B. Homeoffice). AP1-Tipp: Standortvernetzung = immer Site-to-Site.',
  },

  {
    type: 'mc', topic: 'CIA-Triade',
    question: 'Welche drei Schutzziele bilden die CIA-Triade?',
    options: ['Confidentiality, Integrity, Availability', 'Control, Identity, Access', 'Compliance, Integration, Authentication'],
    correct: 0,
    explanation: 'CIA = Confidentiality (Vertraulichkeit), Integrity (Integritaet), Availability (Verfuegbarkeit). Diese drei Schutzziele sind die Grundlage der IT-Sicherheit.',
  },
  {
    type: 'mc', topic: 'Verschluesselung',
    question: 'Was ist der Unterschied zwischen symmetrischer und asymmetrischer Verschluesselung?',
    options: [
      'Symmetrisch: 1 Schluessel fuer beide, Asymmetrisch: 2 Schluessel (Public + Private)',
      'Symmetrisch: nur fuer Texte, Asymmetrisch: nur fuer Dateien',
      'Kein Unterschied, nur andere Namen'
    ],
    correct: 0,
    explanation: 'Symmetrisch: Ein Schluessel zum Ver- und Entschluesseln (z.B. AES). Asymmetrisch: Public Key zum Verschluesseln, Private Key zum Entschluesseln (z.B. RSA).',
  },
  {
    type: 'text', topic: 'Firewall',
    question: 'Erklaere 3 Sicherheitsfunktionen einer Firewall.',
    keywords: ['Paketfilter', 'Deep Packet Inspection', 'NAT', 'Zugriffskontrolle', 'Protokollierung', 'VPN', 'Stateful'],
    explanation: 'Wichtige Firewall-Funktionen: Paketfilterung (IP/Port), Deep Packet Inspection (DPI), Stateful Inspection, NAT, VPN-Terminierung, Protokollierung/Logging, Zugriffskontrolle (ACL), Application Layer Gateway.',
  },
  {
    type: 'mc', topic: 'DSGVO',
    question: 'Welches Recht hat eine betroffene Person NICHT nach der DSGVO?',
    options: ['Recht auf Auskunft', 'Recht auf Loeschung', 'Recht auf kostenlose Produkte', 'Recht auf Datenuebertragbarkeit'],
    correct: 2,
    explanation: 'DSGVO-Rechte: Auskunft (Art.15), Berichtigung (Art.16), Loeschung (Art.17), Einschraenkung (Art.18), Datenuebertragbarkeit (Art.20), Widerspruch (Art.21).',
  },
  {
    type: 'text', topic: 'Schutzbedarf',
    question: 'Ein Serverraum wurde bei allen 3 Schutzzielen als "sehr hoch" eingestuft. Begruende dies.',
    keywords: ['Vertraulichkeit', 'personenbezogen', 'Integritaet', 'Verfuegbarkeit', 'Ausfall', 'Daten'],
    explanation: 'Vertraulichkeit: Personenbezogene/kritische Daten auf dem Server. Integritaet: Manipulation von Daten/Verkabelung kann Systemausfall verursachen. Verfuegbarkeit: Bei Brand/Ausfall kein Zugriff auf Unternehmensdaten moeglich.',
  },
  {
    type: 'mc', topic: 'Backup',
    question: 'Welche Backup-Art sichert nur die seit dem letzten Vollbackup geaenderten Daten?',
    options: ['Vollbackup', 'Differentielles Backup', 'Inkrementelles Backup', 'Snapshot'],
    correct: 1,
    explanation: 'Differentiell: Alle Aenderungen seit dem letzten Vollbackup. Inkrementell: Nur Aenderungen seit dem LETZTEN Backup (egal welcher Art). Differentiell ist groesser aber schneller beim Restore.',
  },
]

const selected = reactive<Record<number, number>>({})
const textAnswers = reactive<Record<number, string>>({})
const textChecked = reactive<Record<number, boolean>>({})

function selectAnswer(qIdx: number, optIdx: number, correct: number) {
  selected[qIdx] = optIdx
  emit('score', optIdx === correct ? 5 : 0)
}

function checkText(idx: number) {
  const q = questions[idx] as any
  const answer = (textAnswers[idx] || '').toLowerCase()
  let found = 0
  q.keywords.forEach((kw: string) => { if (answer.includes(kw.toLowerCase())) found++ })
  textChecked[idx] = true
  emit('score', found >= 2 ? 5 : found >= 1 ? 3 : 0)
}
</script>
