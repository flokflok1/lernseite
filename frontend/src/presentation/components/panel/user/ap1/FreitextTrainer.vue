<template>
  <div class="ft-wrap">
    <!-- Header -->
    <div class="ft-header">
      <div>
        <h2 class="ft-title">📝 Freitext-Fragen</h2>
        <p class="ft-sub">{{ filteredQuestions.length }} echte BW AP1-Prüfungsfragen 2022–2024</p>
      </div>
      <LumiHint
        :context="`Freitext-Aufgabe ${currentIdx + 1}/${filteredQuestions.length}: Thema ${current?.topics?.join(', ')} — ${current?.question?.slice(0, 80)}...`"
        systemExtra="Gib dem Schüler Hinweise auf wichtige Fachbegriffe und erkläre die Struktur einer guten Antwort. Beachte: ADHS — kurze, klare Antworten bevorzugen."
      />
    </div>

    <!-- Category Filter -->
    <div class="ft-filters">
      <button v-for="cat in categories" :key="cat"
        class="ft-filter-btn"
        :class="activeCategory === cat ? 'ft-filter-active' : ''"
        @click="setCategory(cat)">
        {{ cat === 'Alle' ? `Alle (${questions.length})` : `${cat} (${countByCategory(cat)})` }}
      </button>
    </div>

    <!-- Year Filter -->
    <div class="ft-year-filters">
      <button v-for="y in [0, 2024, 2023, 2022]" :key="y"
        class="ft-year-btn"
        :class="activeYear === y ? 'ft-year-active' : ''"
        @click="setYear(y)">
        {{ y === 0 ? 'Alle Jahre' : y }}
      </button>
    </div>

    <!-- Navigation -->
    <div class="ft-nav">
      <button v-for="(q, idx) in filteredQuestions" :key="globalIndex(idx)"
        class="ft-nav-btn"
        :class="currentIdx === idx ? 'ft-nav-active' : answered[globalIndex(idx)] ? 'ft-nav-done' : ''"
        @click="goTo(idx)">
        {{ idx + 1 }}
      </button>
    </div>

    <!-- Progress -->
    <div class="ft-progress-bar">
      <div class="ft-progress-fill" :style="{ width: (answeredCount / filteredQuestions.length * 100) + '%' }"></div>
    </div>
    <div class="ft-progress-label">{{ answeredCount }}/{{ filteredQuestions.length }} beantwortet · {{ current?.year }} {{ current?.season }} · Q{{ current?.questionNumber }}</div>

    <div v-if="current" class="ft-content">
      <!-- Meta -->
      <div class="ft-scenario">
        <div class="ft-scenario-badge">
          📅 {{ current.year }} {{ current.season }} · Aufgabe {{ current.questionNumber }}
          <span v-for="t in current.topics" :key="t" class="ft-topic-tag">{{ t }}</span>
        </div>
      </div>

      <!-- Question -->
      <div class="ft-question">
        <div class="ft-question-label">❓ Aufgabe:</div>
        <div class="ft-question-text">{{ current.question }}</div>
      </div>

      <!-- Answer -->
      <textarea
        v-model="userAnswer"
        rows="6"
        class="ft-textarea"
        placeholder="Schreibe deine Antwort hier... Nutze Fachbegriffe!"
        :disabled="answered[globalIndex(currentIdx)]"
      ></textarea>

      <!-- Buttons -->
      <div class="ft-actions">
        <button v-if="!answered[globalIndex(currentIdx)]"
          class="ft-btn-check"
          :disabled="!userAnswer.trim()"
          @click="submitAnswer">
          ✅ Prüfen
        </button>
        <button class="ft-btn-solution" @click="showSolution = !showSolution">
          {{ showSolution ? '🙈 Lösung verbergen' : '💡 Musterlösung' }}
        </button>
        <button v-if="currentIdx < filteredQuestions.length - 1" class="ft-btn-next" @click="nextQuestion">
          Weiter →
        </button>
      </div>

      <!-- Score Feedback -->
      <div v-if="answered[globalIndex(currentIdx)]" class="ft-feedback"
        :class="scores[globalIndex(currentIdx)] >= 6 ? 'ft-fb-good' : scores[globalIndex(currentIdx)] >= 3 ? 'ft-fb-ok' : 'ft-fb-bad'">
        <div class="ft-fb-score">
          {{ scores[globalIndex(currentIdx)] >= 8 ? '🏆' : scores[globalIndex(currentIdx)] >= 5 ? '👍' : '📚' }}
          {{ scores[globalIndex(currentIdx)] }}/10 Punkte
        </div>
        <div class="ft-fb-msg">
          {{ scores[globalIndex(currentIdx)] >= 8 ? 'Super! Die wichtigsten Begriffe getroffen!' : scores[globalIndex(currentIdx)] >= 5 ? 'Gut, aber einige Fachbegriffe fehlen.' : 'Überarbeite deine Antwort und vergleiche mit der Musterlösung.' }}
        </div>
        <div class="ft-keywords">
          <span v-for="kw in current.keywords" :key="kw"
            class="ft-kw"
            :class="userAnswer.toLowerCase().includes(kw.toLowerCase()) ? 'ft-kw-hit' : 'ft-kw-miss'">
            {{ userAnswer.toLowerCase().includes(kw.toLowerCase()) ? '✓' : '✗' }} {{ kw }}
          </span>
        </div>
      </div>

      <!-- Solution -->
      <transition name="slide">
        <div v-if="showSolution" class="ft-solution">
          <div class="ft-solution-label">📋 Musterlösung:</div>
          <div class="ft-solution-text">{{ current.solution }}</div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import LumiHint from '@/presentation/components/panel/user/ap1/LumiHint.vue'

const emit = defineEmits<{ score: [points: number] }>()

interface FreitextQuestion {
  year: number
  season: string
  questionNumber: string
  category: string
  question: string
  solution: string
  keywords: string[]
  topics: string[]
}

const questions: FreitextQuestion[] = [
  { year: 2024, season: 'Sommer', questionNumber: '1.1', category: 'Beschaffung', question: `Zur Auswahl möglicher Lieferanten möchten Sie auf interne und externe Bezugsquellen zugreifen.
- Nennen Sie je 2 interne und externe Bezugsquellen für mögliche Lieferanten.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 1.`, solution: `Interne Bezugsquellen:
Warenwirtschaftssystem (Lieferer- Warendatei), Reiseberichte Außendienstmitarbeiter, Erfahrungen eigener Mitarbeiter → Wissensdatenbank, Buchführungs- und Rechnungsunterlagen

Externe Bezugsquellen:
Internet (z. B. via Suchmaschine), Kataloge, Prospekte, Wirtschaftszeitungen / Fachzeitschriften, Messe- und Ausstellungsbesuche, Adressbücher, Referenzen von anderen Unternehmen, Informationen / Statistiken von Wirtschaftsverbänden, IHK o. ä.`, keywords: ['Interne', 'Bezugsquellen', 'Warenwirtschaftssystem', 'Lieferer'], topics: ['Beschaffung', 'Lieferantenauswahl'] },
  { year: 2024, season: 'Sommer', questionNumber: '1.2', category: 'Kalkulation', question: `Nach erfolgreicher Kontaktaufnahme mit den potenziellen Lieferanten erhalten Sie 2 Angebote.
- Führen Sie mithilfe der Anlagen 1 und 2 einen quantitativen Angebotsvergleich durch.
- Begründen Sie, welchen Lieferanten Sie auswählen.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 1.`, solution: `| Firma                | Topsicherheit AG | Heikvision GmbH |
|----------------------|------------------|-----------------|
| Listen einkaufspreis | 12.550,00 €      | 12.605,00 €     |
| Lieferantenrabatt    | 5%               | 627,50 € 10%    | 1.260,50 € |
| Zieleinkaufspreis    | 11.922,50 €      | 11.344,50 €     |
| Lieferantenskonto    | 3%               | 357,68 € 2%     | 226,89 €   |
| Bareinkaufspreis     | 11.564,83 €      | 11.117,61 €     |
| Bezugskosten         | 0,00 €           | 69,99 €         |
| Bezugspreis          | 11.564,83 €      | 11.187,60 €     |`, keywords: ['Firma', 'Topsicherheit', 'Heikvision', 'GmbH'], topics: ['Kalkulation', 'Angebotsvergleich', 'Beschaffung'] },
  { year: 2024, season: 'Sommer', questionNumber: '1.3', category: 'Beschaffung', question: `Der günstigste Lieferant teilt Ihnen mit, dass er aufgrund der aktuellen Wirtschaftslage vorerst keine Rabatte für Neuaufträge einräumen kann.
- Nennen Sie 3 Gründe, weshalb die Systemhaus KG dennoch bei diesem Lieferanten bestellen könnte.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 2.`, solution: `- Gute bisherige Zusammenarbeit
- Längeres Zahlungsziel
- Schnellere Verfügbarkeit → Lieferzeitraum und damit Installationsarbeiten besser planbar
- Kundennähe`, keywords: ['Gute', 'Zusammenarbeit', 'Längeres', 'Zahlungsziel', 'Verfügbarkeit'], topics: ['Beschaffung', 'Lieferantenauswahl'] },
  { year: 2024, season: 'Sommer', questionNumber: '1.4', category: 'Beschaffung', question: `Zwei Wochen später wird das Videoüberwachungssystem geliefert.
- Erläutern Sie 4 Arbeitsschritte, welche bei der Wareneingangsprüfung durchgeführt werden müssen.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 2.`, solution: `- Vergleich des Lieferscheines (Produktbezeichnung und Menge) mit den Bestellangaben in unserem ERP-System. Prüfung hinsichtlich Vollständigkeit und Richtigkeit.
- Überprüfen ob der Liefertermin eingehalten wurde.
- Beschädigungen an Transportverpackung prüfen.
- Bei Beschädigungen Mängelfeststellung durchführen.
- Dem Transportunternehmen die Lieferung quittieren.`, keywords: ['Vergleich', 'Lieferscheines', 'Produktbezeichnung', 'Menge'], topics: ['Wareneingang', 'Beschaffung'] },
  { year: 2024, season: 'Sommer', questionNumber: '2.1', category: 'Programmierung', question: `- Erstellen Sie die Funktion deleteOldFiles() in einer an Ihrer Schule gelehrten Programmiersprache.
- Verwenden Sie hierfür eine geeignete Auswahl der Funktionen aus Anlage 3.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 3.`, solution: `def deleteOldFiles():
    while getTotalFileSize() > 1000000000:
        name = getOldestFileName()
        deleteFileByName(name)

void deleteOldFiles()
{
    number = 0;
    size = 0;
    while(size1000000000)
        deleteFilesByTimestamp(time);
}`, keywords: [], topics: ['Programmierung', 'Algorithmen'] },
  { year: 2024, season: 'Sommer', questionNumber: '3.1', category: 'SQL', question: `Löschen des Datenbankeintrages für die Bilddatei mit dem Namen „testbild.jpg“.`, solution: `DELETE FROM images WHERE filename = "testbild.jpg";`, keywords: ['DELETE', 'FROM', 'WHERE'], topics: ['SQL', 'Datenbanken'] },
  { year: 2024, season: 'Sommer', questionNumber: '3.2', category: 'SQL', question: `Bestimmen des gesamten Speicherplatzes der Bilddateien, die in der Datenbank erfasst sind.`, solution: `SELECT SUM(filesize) FROM images;`, keywords: ['SELECT', 'FROM'], topics: ['SQL', 'Datenbanken'] },
  { year: 2024, season: 'Sommer', questionNumber: '3.3', category: 'SQL', question: `Bestimmen der Gesamtanzahl der Bilddateien.`, solution: `SELECT COUNT(*) FROM images;`, keywords: ['SELECT', 'COUNT', 'FROM'], topics: ['SQL', 'Datenbanken'] },
  { year: 2024, season: 'Sommer', questionNumber: '3.4', category: 'SQL', question: `Auflisten der Bilder in geordneter Reihenfolge. Die neuesten Bilder sollen zuerst erscheinen.`, solution: `SELECT * FROM images ORDER BY timestamp DESC;`, keywords: ['SELECT', 'FROM', 'ORDER', 'DESC'], topics: ['SQL', 'Datenbanken'] },
  { year: 2024, season: 'Sommer', questionNumber: '3.5', category: 'SQL', question: `Hinzufügen eines Datenbankeintrages für die Bilddatei mit dem Namen „testbild.jpg“, der Größe 117000 Byte und dem Zeitstempel 1667292685.`, solution: `INSERT INTO images VALUES ("testbild.jpg", 117000, 1667292685);`, keywords: ['INSERT', 'INTO', 'VALUES'], topics: ['SQL', 'Datenbanken'] },
  { year: 2024, season: 'Sommer', questionNumber: '4.1', category: 'Netzwerk', question: `Die Geschäftsführung der Kauffix GmbH möchte vom Homeoffice auf das Videoüberwachungssystem zugreifen können.
- Begründen Sie, warum aus dem Homeoffice nicht auf das Videoüberwachungssystem mit der IP-Adresse 192.168.0.33 zugegriffen werden kann.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 5.`, solution: `Die IP-Adresse 192.168.0.33 ist eine private IP-Adresse. Private Adressen werden nicht im Internet geroutet. Aus diesem Grund ist die Adresse 192.168.0.33 im Netz der Filiale aus dem Homeoffice nicht unmittelbar über das Internet erreichbar.`, keywords: ['IP-Adresse', 'Private', 'Adressen'], topics: ['Netzwerk', 'IP-Adressierung', 'Routing'] },
  { year: 2024, season: 'Sommer', questionNumber: '4.2', category: 'Netzwerk', question: `Die restlichen 9 Videokameras wurden mit den IP-Adressen 192.168.1.33 bis 192.168.9.33 in das bestehende Netz eingebunden. Beim Testen stellt sich heraus, dass diese Videokameras nicht von den Clients aus erreicht werden können.
- Begründen Sie warum die Videokameras nicht von den Clients aus erreicht werden können.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 5.`, solution: `Die IP-Adresse der restlichen 9 Videokameras befinden sich nicht im gleichen Netzwerk (192.168.0.0 /24) wie die Clients.`, keywords: ['IP-Adresse', 'Videokameras', 'Netzwerk', 'Clients'], topics: ['Netzwerk', 'Subnetting'] },
  { year: 2024, season: 'Sommer', questionNumber: '4.3', category: 'Netzwerk', question: `Einer der Clients kommt nicht ins Internet. Bei der Fehlersuche schauen Sie sich die Netzwerkkonfiguration an:

Ethernet-Adapter Netzwerkverbindung:
1. Verbindungsspezifisches DNS-Suffix:
2. Beschreibung. . . . . . . . . . . : Intel(R) Ethernet Connection
3. Physische Adresse . . . . . . . . : 0C-DD-24-CE-C6-D8
4. IPv6-Adresse . . . . . . . . . . : fe80::868c:6a65:bb44:b228
5. IPv6-Adresse . . . . . . . . . . : 2001:db8:1234:55::a/64
6. IPv4-Adresse . . . . . . . . . . : 192.168.0.51
7. Subnetzmaske . . . . . . . . . . : 255.255.255.0
8. Standardgateway . . . . . . . . . : 192.168.0.1
9. DNS-Server . . . . . . . . . . . : 192.168.0.254

- Beschreiben Sie den Fehler, der bei der manuellen Konfiguration des Clients gemacht wurde.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 5.`, solution: `Es wurde das falsche Default-Gateway eingetragen. Es ist die IP-Adresse 192.168.0.254 zu verwenden.`, keywords: ['Default-Gateway', 'IP-Adresse', 'Gateway'], topics: ['Netzwerk', 'Troubleshooting'] },
  { year: 2024, season: 'Sommer', questionNumber: '4.4', category: 'Netzwerk', question: `Die obige Clientkonfiguration enthält auch zwei IPv6-Adressen.
- Benennen Sie die beiden dort enthaltenen IPv6-Adresstypen unter Angabe der Zeilennummer.
- Beschreiben Sie, wofür die beiden IPv6-Adresstypen verwendet werden.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 5.`, solution: `4. Link-Local-Adresse:
Die Link-Local-Adresse wird für die Kommunikation im lokalen Netz benutzt.

5. Global-Unicast-Adresse:
Die Global-Unicast-Adresse wird für die Kommunikation ins Internet benutzt.`, keywords: ['Link-Local-Adresse', 'Kommunikation', 'Netz', 'Link-Local', 'Global-Unicast'], topics: ['Netzwerk', 'IPv6'] },
  { year: 2024, season: 'Sommer', questionNumber: '4.5.1', category: 'IT-Sicherheit', question: `Die Kauffix GmbH möchte das Videokamerasystem in ihr Sicherheitskonzept aufnehmen. Hierfür ist eine Schutzbedarfsanalyse durchzuführen.
- Kennzeichnen Sie den Schutzbedarf der Bilddateien nach den Schutzzielen Vertraulichkeit, Verfügbarkeit und Integrität.
- Begründen Sie Ihre Entscheidung.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 6.
- Informationen zu den Schutzzielen finden Sie in der Anlage 4.`, solution: `Vertraulichkeit: Vertraulich (X)
Begründung: Bilder von Personen sind vertrauliche Daten und Veröffentlichen oder unerlaubtes Erstellen wären Persönlichkeitsverletzungen („Recht am eigenen Bild“). Auch das interne zur Verfügung stellen oder Weiterleiten ist ohne ausdrückliche Erlaubnis eine Persönlichkeitsverletzung.

Verfügbarkeit: Normal (X)
Begründung: Die Verfügbarkeit lässt sich aus folgenden Gründen als normal einschätzen: Die Supermarktkette war auch ohne Kameraüberwachung arbeitsfähig. Auf die personenbezogenen Bilddaten sollte auch nur in begründeten Ausnahmefällen zugegriffen werden.

Integrität: Normale Anforderung (X)
Begründung: Dadurch, dass mehrere unterschiedliche Bilder erzeugt werden, sind die Bilddaten schwer zu fälschen. Mit falschen Bilder ist mit keiner erheblichen Gefährdung von menschlichem Wohl zu rechnen. Die Anforderung an die Integrität ist normal.`, keywords: ['Vertraulichkeit', 'Vertraulich', 'Begründung', 'Bilder', 'vertrauliche', 'Verfügbarkeit'], topics: ['IT-Sicherheit', 'Schutzziele'] },
  { year: 2024, season: 'Sommer', questionNumber: '4.5.2', category: 'Datenschutz', question: `Eine der Videokameras ist auf den öffentlichen Bürgersteig ausgerichtet.
- Klären Sie den Kunden über mögliche rechtliche Probleme auf.
- Verwenden Sie für Ihre Lösung das Vorgabeblatt 7.`, solution: `Bilder von Personen sind vertrauliche Daten und Veröffentlichen oder unerlaubtes Erstellen wären Persönlichkeitsverletzungen („Recht am eigenen Bild“). Mit der Ausrichtung der Videokamera auf den öffentlichen Bürgersteig werden Aufzeichnung von Privatpersonen gemacht, die in keinem Bezug zum Unternehmen stehen. Die Aufnahmen sind ohne Genehmigung der Privatperson illegal.`, keywords: ['Bilder', 'Personen', 'Daten', 'Veröffentlichen', 'vertrauliche'], topics: ['Datenschutz', 'Vertragsrecht'] },
  { year: 2023, season: 'Sommer', questionNumber: '1.1.1', category: 'Organisation', question: `Herr Löser ist unsicher, ob es sich bei der Illustration um eine Einlinien-, Mehrlinien-, Stabliniens- oder eine Matrixorganisation handelt. Benennen und beschreiben Sie das Organisationssystem, welches obigem Organigramm zugrunde liegt.`, solution: `Es liegt eine Stab-Linien-Organisation vor.
Hier werden Instanzen durch Stabsstellen unterstützt. Diese haben i.d.R. keine Entscheidungsbefugnis, sie sind vor allem beratend tätig und bereiten Entscheidungen vor.
Eine Linienorganisation besagt, dass eine untergeordnete Stelle jeweils nur von einer vorgesetzten Instanz Weisungen erhalten kann.`, keywords: ['Stab-Linien-Organisation', 'Hier', 'Instanzen', 'Stabsstellen'], topics: ['Organisation', 'BWL'] },
  { year: 2023, season: 'Sommer', questionNumber: '1.1.2', category: 'Organisation', question: `Begründen Sie, ob sich dieses Organigramm Ihrer Meinung nach für das IT-Systemhaus eignet. Welche Verbesserungsmöglichkeiten sehen Sie (2 Angaben)?`, solution: `Für ein Systemhaus kann eine andere Organisation zielführender sein, weil
- oft projektbezogen gearbeitet wird
- Problemstellungen bearbeitet werden, die Teamarbeit von Fachkräften aus verschiedenen Bereichen erfordern.

Verbesserungsmöglichkeiten, z. B.:
- es sollte eine eigenständige Abteilung „Personal" erstellt werden mit eigener Weisungsbefugnis
- die Abteilungen Einkauf und Absatz können zentralisiert/zusammengelegt werden
- die Abteilung Einkauf sollte sowohl Hard- als auch Software beschaffen
- es sollte eine weitere Abteilung Systemintegration eingerichtet werden
alternativ: Matrixorganisation`, keywords: ['Systemhaus', 'Organisation', 'Problemstellungen', 'Teamarbeit'], topics: ['Organisation', 'BWL'] },
  { year: 2023, season: 'Sommer', questionNumber: '1.2.1', category: 'Organisation', question: `Der Unternehmensgründer möchte die Rechtsform des IT-Systemhauses von einer Einzelunternehmung in eine GmbH ändern. Nennen Sie 2 Vorteile und 2 Nachteile der gewünschten Umfirmierung.`, solution: `Vorteile:
- Rechtliche Verantwortung wird auf die Gesellschafter verteilt.
- Haftung wird auf das Gesellschaftsvermögen beschränkt.
- leichte Eigenkapitalbeschaffung durch Aufnahme neuer Gesellschafter.
- steuerliche Vorteile etc.

Nachteile:
- Gründung ist aufwändig und teuer
- Stammkapital 25.000€, bei Gründung mind. 12.500 €
- Bilanzierungspflicht
- alleinige Entscheidungsmacht entfällt, Entscheidungen müssen mit anderen Gesellschaftern/Geschäftsführer abgestimmt werden etc.`, keywords: ['Vorteile', 'Rechtliche', 'Verantwortung', 'Gesellschafter'], topics: ['Rechtsformen', 'BWL'] },
  { year: 2023, season: 'Sommer', questionNumber: '1.2.2', category: 'Organisation', question: `Nennen Sie einen Namensvorschlag für die Firmierung der neuzugründenden GmbH.`, solution: `Firmierung: z. B. DieTurboLöser Systemhaus GmbH
Wichtig: Zusatz GmbH`, keywords: ['Firmierung', 'DieTurboLöser', 'Systemhaus', 'GmbH'], topics: ['Rechtsformen', 'BWL'] },
  { year: 2023, season: 'Sommer', questionNumber: '1.3.1', category: 'Beschaffung', question: `Beim IT-Systemhaus trifft eine Anfrage über 30 Laptops der Marke „Peaches“ von der ortsansässigen Dübel Wunderlich KG mit einem Budget von 54.000,- Euro (netto) ein. Von Ihrem Großhändler Müller erhalten Sie dazu auf Nachfrage ein Angebot für die entsprechenden Laptops (Anlage 1). Nennen Sie 2 fehlende Bestandteile des verbindlichen Angebots.`, solution: `Fehlende Inhalte:
- Angebotspreis brutto/netto unklar
- genaue technische Ausstattung des Laptops fehlt (Modellbezeichnung bzw. Leistung, Art der Softwarelizenzen etc.)
- Lieferdauer

Anmerkung: Das Angebot enthält keine Gültigkeitsdauer (ist jedoch nicht erforderlich)`, keywords: ['Fehlende', 'Inhalte', 'Angebotspreis', 'Ausstattung'], topics: ['Beschaffung', 'Angebot'] },
  { year: 2023, season: 'Sommer', questionNumber: '1.3.2', category: 'Kalkulation', question: `Ermitteln Sie auf Grundlage der Anlagen 1 und 2 rechnerisch nachvollziehbar den Gewinn/Verlust in Euro und Prozent, welcher durch den Weiterverkauf der Laptops an die Dübel Wunderlich KG entsteht. Verwenden Sie die Anlage 7.`, solution: `Differenzkalkulation

Angebotspreis netto pro Stück:          1.300,00 €
Bestellmenge Laptops:                           30
Budget brutto:                             54.000,00 €

                                                                                              alternativ:
                                                                                              Kalkulation pro Stück

Netto-Einkaufspreis                     39.000,00 €                1.300,00 €
- Liefererrabatt                               20 %                  7.800,00 €                   260,00 €
Ziel-EKP                                    31.200,00 €                1.040,00 €
- Liefererskonto                             3,00 %                     936,00 €                     31,20 €
Bar-EKP                                    30.264,00 €                1.008,80 €
+ Bezugskosten                             10,00 €                     300,00 €                     10,00 €
Bezugspreis                               30.564,00 €                1.018,80 €
+ Handlungskosten                        35 %                  10.697,40 €                   356,58 €
Selbstkosten                             41.261,40 €                1.375,38 €
+ Gewinn                                     2,6 %                   1.074,60 €                     35,82 €
Bar-VKP                                  42.336,00 €                1.411,20 €
+ Kundenskonto                            2,00 %                     864,00 €                     28,80 €
Ziel-VKP                                  43.200,00 €                1.440,00 €
+ Kundenrabatt                           20 %                  10.800,00 €                   360,00 €
Netto-VKP                               54.000,00 €                1.800,00 €`, keywords: ['Differenzkalkulation', 'Angebotspreis', 'Stück', 'Bestellmenge'], topics: ['Kalkulation', 'Beschaffung'] },
  { year: 2023, season: 'Sommer', questionNumber: '1.4.1', category: 'Service Mgmt', question: `Der Auftrag mit der Dübel Wunderlich KG kommt zustande. Das Unternehmen möchte zusätzlich einen Servicevertrag mit Ihrem Systemhaus abschließen. Sie kontaktieren die Dübel Wunderlich KG und bieten Ihnen ein SLA (Service-Level-Agreement) an. Nennen Sie 4 mögliche Inhalte eines SLAs.`, solution: `Inhalte eines Service-Level-Agreements:
- Leistungen
- Nutzungszeiten des Kunden
- Preise
- Kommunikationsweg
- Support
- Lösungszeit
- Servicezeiten etc.`, keywords: ['Inhalte', 'Service-Level-Agreements', 'Leistungen', 'Nutzungszeiten'], topics: ['SLA', 'Service Mgmt'] },
  { year: 2023, season: 'Sommer', questionNumber: '1.4.2', category: 'Service Mgmt', question: `Nach Abschluss des SLAs erreichen Sie in Ihrem Ticketsystem folgende Meldungen von der Dübel Wunderlich KG:
- Mitteilung, dass die Lizenz der Office-Anwendung abläuft.
- Herr Müller beantragt eine Maus für Linkshänder.
- Der Accesspoint im Lager funktioniert nicht.
- In einer Statusmeldung sehen Sie, dass es mehr als fünf fehlgeschlagene Anmeldeversuche auf dem Kundenkonto von Herr Müller gibt.
- Herr Müller eröffnet ein Ticket, dass sein Bildschirm flackert.

Begründen Sie in allen 5 Fällen, ob es sich um ein Event, ein Service Request oder ein Incident handelt.`, solution: `Service Request/Event/Incident
- Lizenz der Office-Anwendung läuft ab: Event - Statusmeldung.
- Maus für Linkshänder: Service Request - Anfrage eines Anwenders zur Bereitstellung.
- Accesspoint funktioniert nicht: Incident - Unterbrechung eines Service.
- Statusmeldung fünf fehlgeschlagene Anmeldeversuche: Event - automatisch generierte Meldung.
- Bildschirm Müller flackert: Erstmal ein Event, das zu einem Incident - Störungsfall werden sollte.`, keywords: ['Service', 'Request', 'Event', 'Incident'], topics: ['Service Mgmt', 'ITIL'] },
  { year: 2023, season: 'Sommer', questionNumber: '2.1', category: 'IT-Sicherheit', question: `Auf den Laptops der Vertriebsabteilung der Dübel Wunderlich KG wird unter anderem die Software zur Auftrags- und Kundenverwaltung bereitgestellt. Ergänzen Sie auf der Anlage 8 den Schutzbedarf „normal“, „hoch“ oder „sehr hoch“ der Anwendung zur Auftrags- und Kundenverwaltung bzgl. der Vertraulichkeit, der Integrität und der Verfügbarkeit. Gehen Sie dabei von den Schutzbedarfskategorien in Anlage 3 aus.`, solution: `Anwendung Schutzbedarfsfeststellung
Nr. A004 Auftrags- und Kundenverwaltung

Vertraulichkeit: hoch
Begründung: Es werden vertrauliche Daten (z. B. Kundendaten) verarbeitet, deren Missbrauch dem Unternehmen großen Schaden zufügen kann

Integrität: hoch
Begründung: Falls Mengen- oder Preisangaben verändert werden, kann dem Unternehmen ein großer Schaden entstehen, der leicht über 50.000 Euro gehen und zu großem Ansehensverlusten führt.

Verfügbarkeit: normal
Begründung: Ein Ausfall der Client-Software ist auf dem Laptop für mehr als 24 Stunden hinnehmbar, da lokal eher keine Daten gespeichert werden. Ersatzweise kann auf einem anderen Gerät weitergearbeitet werden.`, keywords: ['Anwendung', 'Schutzbedarfsfeststellung', 'Auftrags', 'Kundenverwaltung', 'Vertraulichkeit', 'vertrauliche'], topics: ['IT-Sicherheit', 'Schutzbedarf'] },
  { year: 2023, season: 'Sommer', questionNumber: '2.2', category: 'IT-Sicherheit', question: `Der gesamte Schutzbedarf des Laptops der Vertriebsabteilung soll festgestellt werden. Erläutern Sie ein Prinzip, nach dem dieser Schutzbedarf ermittelt werden kann.`, solution: `Prinzipien:
- In vielen Fällen lässt sich der höchste Schutzbedarf aller Anwendungen, die das IT-System benötigt, übernehmen (Maximumprinzip).
- Wenn eine Anwendung auf die Ergebnisse einer anderen Anwendung angewiesen ist, überträgt sich ihr Schutzbedarf auf diese liefernde Anwendung (Abhängigkeiten).
- Der Schutzbedarf des IT-Systems kann höher sein als der Schutzbedarf der einzelnen Anwendungen (Kumulationseffekt). Dies ist z. B. der Fall, wenn auf einem Server mehrere Anwendungen mit normalem Schutzbedarf betrieben werden.
- Der Schutzbedarf kann niedriger sein als der Schutzbedarf der zugeordneten Anwendungen, wenn eine Anwendung mit hohem Schutzbedarf auf mehrere Systeme verteilt ist und auf dem betreffenden IT-System nur weniger wichtige Teile dieser Anwendung ausgeführt werden (Verteilungseffekt).`, keywords: ['Prinzipien', 'Fällen', 'Schutzbedarf', 'Anwendungen'], topics: ['IT-Sicherheit', 'Schutzbedarf'] },
  { year: 2023, season: 'Sommer', questionNumber: '3.1.1', category: 'Netzwerk', question: `Zur Dokumentation von Netzwerken werden unterschiedliche grafische Darstellungsarten verwendet. Hierbei werden zwischen logischen und physikalischen Strukturen unterschieden. Erläutern Sie den Begriff der logischen Strukturen, wie es beispielhaft in der Anlage 4 abgebildet ist.`, solution: `Logische Topologien veranschaulichen Geräte, Ports und das Adressierungsschema des Netzwerks. Zudem kann man sehen, welche Endgeräte mit welchen aktiven Netzkomponenten logisch miteinander verbunden sind und welche Medien dazu verwendet werden. Es kann daraus entnommen werden, welche Teilnehmer miteinander kommunizieren können.`, keywords: ['Logische', 'Topologien', 'Geräte', 'Ports'], topics: ['Netzwerk', 'Dokumentation'] },
  { year: 2023, season: 'Sommer', questionNumber: '3.1.2', category: 'Netzwerk', question: `Stellen Sie 2 Unterschiede einer physikalischen zur logischen Struktur dar.`, solution: `Physische Topologien zeigen
den physischen Standort (Räume, Schaltschränke) von aktiven Netzwerkkomponenten und die Kabelinstallation an.
Daraus lässt sich die Geräte und Kabelwege zu lokalisieren, um die Hardware vor Ort zu warten oder zu reparieren.`, keywords: ['Physische', 'Topologien', 'Standort', 'Räume'], topics: ['Netzwerk', 'Dokumentation'] },
  { year: 2023, season: 'Sommer', questionNumber: '3.2.1', category: 'Netzwerk', question: `Um die Netzwerkeinstellungen eines neuen Geschäftsleitungs-Laptops zu überprüfen, lassen Sie sich die IP-Konfiguration des Geräts anzeigen (Anlage 5). In der Zeile 4 der Konfiguration wird angegeben, dass der Drahtlos-LAN Adapter Wi-Fi 6 beherrscht. Nennen Sie 1 Neuerung, die der Standard IEEE 802.11ax (ab Wi-Fi 6E) bietet.`, solution: `Ab Wi-Fi 6E wird zusätzlich das 6 GHz-Frequenzband mit einer Vielzahl neuer Kanäle benutzt.`, keywords: ['Wi-Fi', 'GHz-Frequenzband', 'Vielzahl', 'Kanäle'], topics: ['Netzwerk', 'WLAN'] },
  { year: 2023, season: 'Sommer', questionNumber: '3.2.2', category: 'Netzwerk', question: `In der Zeile 5 der Konfiguration ist eine physische Adresse angegeben. Nennen Sie die Anzahl der Bits die für die Darstellung einer physischen Adresse benötigt werden. Bestimmen Sie die Schicht des OSI-Modells, auf welcher die physische Adresse zur Weiterleitung von Ethernet-Frames verwendet wird.`, solution: `a) MAC-Adressen bestehen aus 48 Bits.
b) Die physische Adresse wird auf dem OSI-Layer 2, dem Data-Link-Layer z. B. von Switches zur Weiterleitung von Ethernet-Frames verwendet.`, keywords: ['MAC-Adressen', 'Bits', 'Adresse', 'OSI-Layer', 'OSI'], topics: ['Netzwerk', 'OSI-Modell', 'MAC-Adresse'] },
  { year: 2023, season: 'Sommer', questionNumber: '3.2.3', category: 'Netzwerk', question: `Neben einer IPv4-Adresse wurden am selben Adapter mehrere IPv6 -Adressen vergeben. Erläutern Sie den Wirkungsbereich der Adresstypen in den Zeilen 8 und 10.`, solution: `In der Zeile 8 ist eine weltweit eindeutige Global Unicast Adresse (GUA) dargestellt. Diese wird zur Kommunikation auch außerhalb des LANs verwendet.
In der Zeile 10 hingegen ist eine Link-Lokal-Adresse (LLA), die nur im lokalen Netzsegment gültig ist.`, keywords: ['Zeile', 'Global', 'Unicast', 'Adresse'], topics: ['Netzwerk', 'IPv6'] },
  { year: 2023, season: 'Sommer', questionNumber: '3.2.4', category: 'Netzwerk', question: `In der IP-Konfiguration ist neben der IPv4 Adresse auch die dazugehörige IPv4-Netzwerkmaske in Zeile 12 angegeben. Bestimmen Sie die Netzwerkadresse und die Broadcastadresse des Netzes der Geschäftsleitung.`, solution: `Netzwerkadresse: 10.1.0.0 /16
Broadcastadresse: 10.1.255.255`, keywords: ['Netzwerkadresse', 'Broadcastadresse'], topics: ['Netzwerk', 'IPv4', 'Subnetting'] },
  { year: 2023, season: 'Sommer', questionNumber: '3.2.5', category: 'Netzwerk', question: `Der neue Auszubildende, mit dem Sie die Laptops bei Ihrem Kunden in Betrieb nehmen, möchte von Ihnen wissen, welche Funktionen die IP-Einstellungen Standardgateway und DNS-Server übernehmen. Beschreiben Sie, zu welchem Zweck der jeweilige Konfigurationseintrag benötigt wird:
a) Standardgateway
b) DNS-Server`, solution: `a. An das Standardgateway werden alle IP-Pakete weitergeleitet, die nicht für das lokale Netzsegment bestimmt sind, z. B. Pakete, die in andere Netze wie das Internet geroutet werden sollen.
b. Ein DNS-Server dient der Namensauflösung. Dabei werden Rechnernamen (URLs) in IP-Adressen aufgelöst`, keywords: ['Standardgateway', 'IP-Pakete', 'Netzsegment', 'Pakete', 'DNS'], topics: ['Netzwerk', 'Routing', 'DNS'] },
  { year: 2023, season: 'Sommer', questionNumber: '4.1', category: 'SQL', question: `Erweitern Sie das in der Anlage 9 dargestellte ERM um sinnvolle Beziehungen, Kardinalitäten und um eine weitere Entität. Attribute müssen nicht angegeben werden.`, solution: `[Diagramm ERM: Mitarbeiter arbeitet an Projekt (m:n), Mitarbeiter besitzt Laptop (1:n), Mitarbeiter gehört zu Abteilung (n:1)]`, keywords: ['Diagramm', 'Mitarbeiter', 'Projekt', 'ERM'], topics: ['Datenbanken', 'ERM', 'Datenmodellierung'] },
  { year: 2023, season: 'Sommer', questionNumber: '4.2', category: 'SQL', question: `Auf Basis der in Anlage 6 dargestellten Informationen soll ein Relationenschema erstellt werden. Primär und Fremdschlüssel sind im Relationenschema anzugeben und so zu kennzeichnen: Primärschlüssel, Fremdschlüssel. Es sind alle Attribute mit geeigneten Datentypen anzugeben. Erstellen Sie das Relationenschema.`, solution: `Relationales Datenbankschema

Mitarbeiter(M_ID INT, Vorname VARCHAR(255), Nachname VARCHAR(255), Alter INT, Abteilung_ID INT, Projekt_ID INT)

Projekt(Projekt_ID INT, Bezeichnung VARCHAR(255), Dauer DOUBLE)

Laptop(Laptop_ID INT, Marke VARCHAR(255), Modell VARCHAR(255), Seriennummer VARCHAR(255), Kaufjahr INT, Betriebssystem VARCHAR(255), M_ID INT)

Abteilung(Abteilung_ID INT, Bezeichnung VARCHAR(255))`, keywords: ['Relationales', 'Datenbankschema', 'Mitarbeiter', 'Vorname'], topics: ['Datenbanken', 'Relationenschema', 'SQL'] },
  { year: 2023, season: 'Sommer', questionNumber: '5', category: 'Programmierung', question: `Erstellen Sie in Anlage 10 die notwendige Logik. Sie können eine der untenstehenden Darstellungsmöglichkeiten auswählen:
- Im Unterricht gelernte Programmiersprache
- Detaillierter Pseudocode
- Struktogramm
- Programmablaufplan`, solution: `Als Programmcode für eine Konsolenanwendung in C#:

public static bool LoginÜberprüfung(string username, string passwort)
{
    bool ok = true;
    switch(DB_Abfrage(username, passwort))
    {
        case 0: // kann wegen Initialisierung von "ok=true" entfallen
            ok = true;
            break;
        case 1:
        case 2:
            Console.WriteLine("Daten nicht korrekt");
            ok = false;
            break;
    }
    return ok;
}

(Alternativ als Struktogramm oder Programmablaufplan, siehe Original-Lösungshinweise)`, keywords: ['Programmcode', 'Konsolenanwendung', 'LoginÜberprüfung', 'Initialisierung', 'switch'], topics: ['Programmierung', 'Algorithmen'] },
  { year: 2023, season: 'Winter', questionNumber: '1.1', category: 'Datenschutz', question: `Die TÜCOPTER e.K. strebt von Beginn ihrer Geschäftstätigkeit nach einem professionellen und gesetzeskonformen Umgang mit ihren Daten. Zu diesem Zweck beauftragt Sie die Geschäftsleitung, einige der anfallenden Daten des Unternehmens zu kategorisieren. Konkret geht es um folgende Daten:

a. Geburtsdatum der Mitarbeiter:innen
b. Konstruktionsdateien neuer Drohnenmodelle
c. Cookies von Besuchern der unternehmenseigenen Website
d. Die Preise von Speisen und Getränken in der TÜCOPTER-Kantine
e. Sozialversicherungsnummern der Mitarbeiter:innen
f. Absprachen der TÜCOPTER e.K. mit Lieferanten für den Bezug elektronischer Komponenten bei der Drohnenproduktion

Ordnen Sie entsprechend der DSGVO die 6 Beispiele einer der folgenden drei Kategorien zu:
1. Geschäfts- und Betriebsgeheimnisse
2. personenbezogene Daten
3. nicht schutzwürdige Daten

Verwenden Sie für Ihre Lösung die Tabelle in Anlage 1 und kreuzen Sie die zu den Daten jeweils passende Kategorie an.`, solution: `a. Geburtsdatum der Mitarbeiter:innen -> 2. personenbezogene Daten
b. Konstruktionsdateien neuer Drohnenmodelle -> 1. Geschäfts- und Betriebsgeheimnisse
c. Cookies von Besuchern der unternehmenseigenen Website -> 2. personenbezogene Daten
d. Die Preise von Speisen und Getränken in der TUCOPTER-Kantine -> 3. nicht schutzwürdige Daten
e. Sozialversicherungsnummern der Mitarbeiter:innen -> 2. personenbezogene Daten
f. Absprachen der TUCOPTER e.K. mit Lieferanten für den Bezug elektronischer Komponenten bei der Drohnenproduktion -> 1. Geschäfts- und Betriebsgeheimnisse`, keywords: ['Geburtsdatum', 'Mitarbeiter', 'Daten', 'Konstruktionsdateien'], topics: ['Datenschutz', 'DSGVO'] },
  { year: 2023, season: 'Winter', questionNumber: '1.2.1', category: 'SQL', question: `Die TÜCOPTER e.K. hält ihre Geschäftsprozesse in einem relationalen Datenbanksystem fest.
Die Datenbank enthält die folgenden drei Relationen:
drohnenmodelle (modell_id, bezeichnung, max_flughoehe, anzahl_arme, nutzlast)
drohnen (drohnen_id, baujahr, ↑ kunden_id, ↑ modell_id)
kunden (kunden_id, firma, email, telefon, iban)

Hinweise:
• Primär- und Fremdschlüssel der Relationen sind mit folgender Notation gekennzeichnet: (Primärschlüssel, Fremdschlüssel: ↑)

Aus den Testdaten sollen alle Kunden mit ihrer kunden_id, firma und email angezeigt werden. Es sollen nur solche Kunden erscheinen, deren Firmenbezeichnung (Attribut: firma) mit „M“ beginnt. Die Auflistung des Abfrageergebnisses ist nach der kunden_id aufsteigend zu sortieren.

Geben Sie den entsprechenden SQL-Befehl an.`, solution: `Select kunden_id, firma, email
from kunden
where firma like "M%"
order by kunden_id asc;`, keywords: ['Select'], topics: ['SQL', 'Datenbanken'] },
  { year: 2023, season: 'Winter', questionNumber: '1.2.2', category: 'Datenbanken', question: `Für die Übernahme von Daten aus der Datenbank ist ein Datenexport der Tabelle drohnenmodelle erforderlich.

Stellen Sie hierfür den untenstehenden Datensatz wahlweise im CSV-, XML- oder JSON-Format dar.

modell_id: 273
bezeichnung: TF-Y84 Oktokopter Drohne
max_flughoehe (in m): 5000
anzahl_arme: 8
Nutzlast (in kg): 12`, solution: `CSV (mit Trennzeichen Semikola):
modell_id; bezeichnung; max_flughoehe (in m); anzahl_arme; nutzlast (in kg)
273; TF-Y84 Oktokopter Drohne;5000;8;12

XML:


    
        273
         TF-Y84 Oktokopter Drohne
        5000
        8
        12
    


JSON:
[ {
    "modell_id": "273",
    "bezeichnung": "TF-Y84 Oktokopter Drohne",
    "max_flughoehe": 5000,
    "anzahl_arme": 8,
    "nutzlast": 12
  }
]

Hinweis: Die Angabe eines Datenformates ist ausreichend zur Lösung der Aufgabe.`, keywords: ['Trennzeichen', 'Semikola', 'Oktokopter', 'Drohne'], topics: ['Datenformate', 'CSV/XML/JSON'] },
  { year: 2023, season: 'Winter', questionNumber: '1.2.3', category: 'SQL', question: `Die Anforderungen an die Datenbank haben sich inzwischen geändert.

Erweitern Sie mit den untenstehenden Informationen das vorliegende Relationenmodell um die entsprechende Relation, inklusive Attribute, Primär- und Fremdschlüssel:

In der Datenbank sollen die Flugeinsätze der Drohnen erfasst werden. Zu diesem Zweck wird jeder Flugeinsatz mit einer fortlaufenden ID, dem Startpunkt des Einsatzes, dem Datum und der Uhrzeit beim Abflug sowie dem Zielpunkt des Einsatzes erfasst. Jeder so erfasste Flugeinsatz gehört immer zu genau einer Drohne.

Hinweis:
Verwenden Sie für Ihre Primär- und Fremdschlüssel die Notation aus 1.2.`, solution: `flugeinsätze(flug_id, startpunkt, datum_abflug, uhrzeit_abflug, zielpunkt, ↑ drohnen_id)`, keywords: [], topics: ['Datenbanken', 'ERM'] },
  { year: 2023, season: 'Winter', questionNumber: '1.3.1', category: 'Programmierung', question: `Eine Online-Apotheke kauft zahlreiche Drohnen von TÜCOPTER, die sie für Expressauslieferungen von Pharmazeutika an Kunden der näheren Umgebung einsetzen möchte.
Die Apotheke arbeitet mit einem zweistufigen Preismodell; ein Teil des Preises hängt von der Nutzlast ab, die der Kunde zum Zielort transportieren möchte, der andere Teil von der Entfernung des Zielortes zum Logistikzentrum:
• Eine Nutzlast von bis zu 6 kg kostet 3 €.
• Höhere Nutzlasten schlagen mit 7 € zu Buche.
• Jeder Kilometer Entfernung des Zielortes vom Logistikzentrum kostet pauschal 0,40 €.
• Die Drohne kann nur Entfernungen von maximal 25 Kilometer anfliegen.
• Der eingesetzte Drohnentyp kann nur eine Nutzlast bis maximal 12 kg transportieren.

Der Ablauf des gewünschten Programms ist bereits in einem Struktogramm dargestellt. Die vom Kunden gewünschte Entfernung und Nutzlast werden der Funktion / Methode als Parameter übergeben.

Leider sind bei der Entwicklung des Struktogramms 2 logische Fehler unterlaufen.
Beschreiben Sie die 2 Fehler.`, solution: `Fehler 1: Der Verknüpfungsoperator der ersten Bedingung wurde falsch gesetzt. Anstelle des „oder“ muss ein „und“ stehen, da beide Bedingungen erfüllt sein müssen, damit ein Transportpreis berechnet werden darf.
Fehler 2: Ebenso wurde der Vergleichsoperator in der zweiten Bedingung falsch gesetzt. Es muss heißen: pnutzlast <= 6, damit die Variable preis_nutzlast die 3 zugewiesen bekommt. Alternativ können auch die Anweisungen des J- /N-Zweiges miteinander getauscht werden, um den Programmablauf zu korrigieren.`, keywords: ['Fehler', 'Verknüpfungsoperator', 'Bedingung', 'Anstelle'], topics: ['Programmierung', 'Algorithmen'] },
  { year: 2023, season: 'Winter', questionNumber: '1.3.2', category: 'Programmierung', question: `Codieren Sie mit einer aus dem Unterricht bekannten Programmiersprache den korrigierten Programmablauf der Funktion.

Hinweis:
Sollten Sie 1.3.1 nicht bearbeitet haben, können Sie auch den im Struktogramm fehlerhaft abgebildeten Programmablauf implementieren.`, solution: `Codierung in Python:
def flugpreise(pnutzlast, pentfernung):
    if pentfernung <=25 and pnutzlast<=12:
        if pnutzlast<=6:
            preis_nutzlast= 3
        else:
            preis_nutzlast= 7
        gesamtpreis=preis_nutzlast+pentfernung*0.4
        print("Der Gesamtpreis des Transportes: ", gesamtpreis)
    else:
        print("Mit diesen Angaben ist ein Drohnentransport nicht möglich.")

Codierung in Java:
public void flugpreise(double pnutzlast, double pentfernung)
{
    double preis_nutzlast;
    double gesamtpreis;
    if(pentfernung <=25 && pnutzlast<=12)
    {
        if(pnutzlast<=6)
        {
            preis_nutzlast= 3;
        }
        else
        {
            preis_nutzlast= 7;
        }
        gesamtpreis=preis_nutzlast+pentfernung*0.4;
        System.out.println("Der Gesamtpreis des Transportes: "+ gesamtpreis);
    }
    else
    {
        System.out.println("Mit diesen Angaben ist ein Drohnentransport nicht möglich.");
    }
}`, keywords: ['Codierung', 'Python', 'Gesamtpreis', 'Transportes'], topics: ['Programmierung', 'Python/Java', 'Java'] },
  { year: 2023, season: 'Winter', questionNumber: '2.1.1', category: 'Netzwerk', question: `Die Schnittstellen sind folgendermaßen konfiguriert.
Geräte | IPv4 | Subnetzmaske | Gateway
PC1 | 172.16.0.2 | 255.255.0.0 | 172.16.0.1
PC10 | 172.16.0.11 | 255.255.0.0 | 172.16.0.1
Printer | 172.16.0.50 | 255.255.0.0 | 172.16.0.1
Server | 172.16.0.200 | 255.255.0.0 | 172.16.0.1
Router ISP | 172.16.255.254 | 255.255.255.0 | -
Router ISP | 84.136.105.106 | 255.255.255.0 | -

Sie stellen fest, dass die Endgeräte untereinander erreichbar sind, aber keines der Geräte kommt ins Internet. Die Leitungen sind alle korrekt angeschlossen.

Benennen Sie die fehlerhafte Einstellung.`, solution: `Die Endgeräte haben ein anderes Gateway eingetragen und können deshalb nicht ins Internet. Das Gateway-Interface (Router) sollte auf 172.16.0.1 geändert werden. Alternativ kann auch bei den Endgeräten die Gatewayadresse geändert werden.`, keywords: ['Endgeräte', 'Gateway', 'Internet', 'Gateway-Interface', 'Router'], topics: ['Netzwerk', 'Routing'] },
  { year: 2023, season: 'Winter', questionNumber: '2.1.2', category: 'Netzwerk', question: `Der Router hat als einziges Netzwerkgerät zwei IPv4-Adressen.
Unterscheiden Sie die beiden IPv4-Adressenarten voneinander.`, solution: `84.136.105.106 ist eine öffentliche IPv4 Adresse auf der externen Schnittstelle des Routers, die vom Internet Service Provider vergeben wird.
172.16.255.254 ist eine private IPv4 Adresse auf der internen Schnittstelle des Routers. Diese Adresse gehört zu den reservierten privaten IPv4 Adressen.`, keywords: ['Adresse', 'Schnittstelle', 'Routers', 'Internet', 'IPv4'], topics: ['Netzwerk', 'IPv4'] },
  { year: 2023, season: 'Winter', questionNumber: '2.1.3', category: 'Netzwerk', question: `In der Netzwerkkonfiguration des Netzwerkdruckers ist ein Gateway eingetragen.
Beurteilen Sie Sinn und Zweck eines Gateways für einen Netzwerkdrucker.`, solution: `Der Netzwerkdrucker kann durch ein Gateway aus anderen Teilnetzen erreicht werden.`, keywords: ['Netzwerkdrucker', 'Gateway', 'Teilnetzen'], topics: ['Netzwerk', 'Routing'] },
  { year: 2023, season: 'Winter', questionNumber: '2.2.1', category: 'IT-Sicherheit', question: `Nachdem Sie die Funktionsfähigkeit des Netzwerks erfolgreich hergestellt haben, bittet Sie Ihr Geschäftsführer, das Netzwerk gegen äußere Gefahren zusätzlich mit einer Firewall abzusichern.

Erläutern Sie 3 Sicherheitsfunktionen der Firewall nach der Anlage 3.`, solution: `Effiziente und effektive TLS Inspection
Maximale Transparenz über verschlüsselte Datenbewegungen ohne Kompromisse bei der Performance eingehen zu müssen. Schützt dadurch vor der wachsenden Flut an Ransomware und potenziell unerwünschten Apps, die diesen Schwachpunkt ausnutzen.

Deep Packet Inspection
DPI Engine scannt den Datenverkehr auf Bedrohungen, ohne dass der Prozess von einem Proxy verlangsamt wird. Latenz wird reduziert und Gesamteffizienz verbessert. Stoppt neueste Ransomware und Sicherheitslücken.

Application Acceleration
Wichtiger interner Geschäftsanwendungs-Traffic, der für Zweigstellen, Remote-Benutzer oder Cloud-Anwendungsserver bestimmt ist und nicht gescannt werden muss, kann intelligent über den FastPath übertragen werden, wodurch die Latenz reduziert und die Gesamtleistung optimiert wird. Die FW beschleunigt SaaS-, SD-WAN und Cloud-Datenverkehr wie VoIP, Video und andere vertrauenswürdige Anwendungen automatisch oder über Ihre eigenen Richtlinien, indem sie diese auf dem FastPath durch den Xstream-Flow-Prozessor überträgt.

SD-WAN
Die Firewall bietet eine leistungsstarke, integrierte SD-WAN-Lösung mit Link Auswahl und Routing auf Performance-Basis, Load Balancing, Zero-Impact-Umleitungen auf andere Verbindungen im Falle einer Störung, einer zentralen Cloud-verwalteten Orchestrierung und Xstream-FastPath Beschleunigung des VPN-Tunnelverkehrs. Damit hat sie eine der besten und flexibelsten SD-WAN-Lösungen, die derzeit in Firewalls erhältlich sind.`, keywords: ['Effiziente', 'Inspection', 'Maximale', 'Transparenz', 'Firewall', 'integrierte'], topics: ['IT-Sicherheit', 'Firewall'] },
  { year: 2023, season: 'Winter', questionNumber: '2.2.2', category: 'Netzwerk', question: `Zeichnen Sie die Firewall in die Netztopologie von Anlage 2 ein und begründen Sie die Platzierung.`, solution: `Begründung:
Die externe Routerschnittstelle hat eine öffentliche IP-Adresse und ist Teil eines Netzes, das durch den ISP verwaltet wird. Es macht deshalb Sinn die Hardware Firewall im internen Bereich zwischen ISP-Router und internem Netz zu platzieren.`, keywords: ['Begründung', 'Routerschnittstelle', 'IP-Adresse', 'Teil', 'Firewall', 'Router'], topics: ['Netzwerk', 'IT-Sicherheit'] },
  { year: 2023, season: 'Winter', questionNumber: '2.3.1', category: 'Kalkulation', question: `Die Stromkosten explodieren im Zuge der Energiekrise. Die 10 PCs und der Drucker sind an 220 Arbeitstagen je 8h täglich in Betrieb. Die 2 Switche, der Router, die Firewall und der Server sind permanent im ganzen Jahr eingeschaltet. Gehen Sie davon aus, dass alle Geräte unter maximaler elektrischer Leistung betrieben werden. Folgende Leistungsangaben je Gerät liegen Ihnen vor:

Netzwerkgeräte | Leistungsangabe in Watt
PC mit Bildschirm | 150
Switch | 50
Server | 200
Printer | 30
Router | 35
Firewall | 20

Berechnen Sie die jährlichen Stromkosten des gesamten Netzwerks in Euro, wenn eine kWh 0,45 Euro kostet.`, solution: `Geräte | Anzahl | Watt | Stunden | Tage | Wh | kWh | Euro
PC | 10 | 150 | 8 | 220 | 2.640.000 | 2.640,00 | 1.188,00 €
Switch | 2 | 50 | 24 | 365 | 876.000 | 876,00 | 394,20 €
Server | 1 | 200 | 24 | 365 | 1.752.000 | 1.752,00 | 788,40 €
Printer | 1 | 30 | 8 | 220 | 52.800 | 52,80 | 23,76 €
Router | 1 | 35 | 24 | 365 | 306.600 | 306,60 | 137,97 €
Firewall | 1 | 20 | 24 | 365 | 175.200 | 175,20 | 78,84 €
Summe: 2.611,17 €`, keywords: ['Geräte', 'Anzahl', 'Watt', 'Stunden', 'Switch', 'Router'], topics: ['Kalkulation', 'Stromkosten'] },
  { year: 2023, season: 'Winter', questionNumber: '2.3.2', category: 'Kalkulation', question: `Berechnen Sie die prozentuale Einsparung an Energiekosten für die TÜCOPTER e.K., wenn zukünftig 3 Mitarbeiter 60 % ihrer Arbeitszeit im Home-Office arbeiten.`, solution: `Geräte | Anzahl | Watt | Stunden | Tage | Wh (100%) | Wh (60%) | kWh | Euro
PC | 3 | 150 | 8 | 220 | 792.000 | 475.200 | 475,20 | 213,84 €

Prozentuale Einsparung: 8,19%
Gesamtkosten (2.5.1): 2.611,17 €
Einsparung (2.5.2): 213,84 €`, keywords: ['Geräte', 'Anzahl', 'Watt', 'Stunden'], topics: ['Kalkulation', 'Stromkosten'] },
  { year: 2023, season: 'Winter', questionNumber: '2.4', category: 'IT-Sicherheit', question: `Der Serverraum wurde in der Schutzbedarfsanalyse bei allen 3 Schutzzielen als „sehr hoch“ eingestuft.
Begründen Sie anhand der Schutzziele, wieso es zu dieser Einstufung gekommen ist.`, solution: `Vertraulichkeit: Im Serverraum steht i. d. R. der Server welcher personenbezogene Daten und kritische Unternehmensdaten enthält.
Integrität: Die Veränderung der Daten, aber auch der Verkabelung kann zu Systemausfällen führen und damit existenzbedrohend sein.
Verfügbarkeit: Bei Geräteausfall bzw. Brand kann nicht mehr auf die Unternehmensdaten zugegriffen werden.`, keywords: ['Vertraulichkeit', 'Serverraum', 'Server', 'Daten', 'Integrität', 'Verfügbarkeit'], topics: ['IT-Sicherheit', 'Schutzziele'] },
  { year: 2023, season: 'Winter', questionNumber: '3.1.1', category: 'Organisation', question: `Stellen Sie den Aufbau der TÜCOPTER e.K. in einem Organigramm grafisch dar.`, solution: `Einliniensystem mit Stabstelle/Stablinienystem.
Geschäftsleitung (mit Stabstelle: juristische Beratung).
Darunter die Abteilungen: Softwareentwicklung (4 Mitarbeiter), Produktion (2 Mitarbeiter), Einkauf und Vertrieb (2 Mitarbeiter), Personal (1 Mitarbeiterin + Auszubildende/r).`, keywords: ['Einliniensystem', 'Stabstelle', 'Stablinienystem', 'Geschäftsleitung'], topics: ['Organisation', 'Organigramm'] },
  { year: 2023, season: 'Winter', questionNumber: '3.1.2', category: 'Organisation', question: `Nennen Sie 2 Merkmale, durch die diese Organisationsform gekennzeichnet ist.`, solution: `Im Einliniensystem/Stablinienystem gilt das Prinzip der Auftragsverteilung. Das bedeutet, dass jeder Mitarbeiter genau einen Vorgesetzten hat und jeder Vorgesetzte mehrere ihm unterstellte Mitarbeiter.
Die Kommunikationswege verlaufen vertikal. Die Linien stellen Dienstwege bzw. Delegationswege dar, auf welchen der Kommunikations- und Informationsaustausch stattfindet.

Merkmale:
- übersichtlich und einfach strukturiert
- eindeutige Dienst-/Informations- und Kommunikationswege
- klare Anordnung
- klare Kompetenzverteilung
- lange Dienstwege
- Überlastung des Führungspersonals
- unnötige Belastung von Zwischeninstanzen
- erschwerte Zusammenarbeit zwischen Mitarbeitern`, keywords: ['Einliniensystem', 'Stablinienystem', 'Prinzip', 'Auftragsverteilung'], topics: ['Organisation'] },
  { year: 2023, season: 'Winter', questionNumber: '3.2.1', category: 'Organisation', question: `Aufgrund der erfolgreichen Wirtschaftslage der TÜCOPTER e.K. und der hohen Nachfrage nach Drohnen will Herr Meyer expandieren. Im Rahmen der Expansion besteht die Überlegung, eine GmbH zu gründen.

Schreiben Sie Herrn Meyer einen begründeten Vorschlag als Email (Anlage 4), ob die Gründung einer GmbH empfehlenswert ist.
Gehen Sie hierbei auf die wesentlichen Unterschiede dieser beiden Gesellschaftsformen (e.K. und GmbH) hinsichtlich der folgenden Kriterien ein:
• Eintragung ins Handelsregister
• Gründungskapital
• Haftung
• Unternehmensführung`, solution: `Betreff: Gegenüberstellung Rechtsformen: e.K. und GmbH

Sehr geehrter Herr Meyer,
Ich habe mich intensiver mit den Rechtsformen e. K. Und GmbH auseinandergesetzt und diese bzgl. Kriterien Eintragung in Handelsregister, Gründungskapital, Haftung und Unternehmensführung untersucht.

Eintragung ins Handelsregister:
Die Eintragung einer GmbH ins Handelsregister hat konstitutive Wirkung, da sie vor der Eintragung nicht besteht. Bei dem eingetragenen Kaufmann hat die Eintragung ins Handelsregister eine deklaratorische Wirkung.

Gründungskapital:
e.K.: kein Mindestkapital erforderlich
GmbH: Mindestkapital von 25.000 Euro erforderlich, das bei der Gründung mindestens zur Hälfte eingezahlt sein muss. Als Anteil des Stammkapitals können auch Sachwerte, deren Wert nachgewiesen werden muss, in die Gesellschaft mit beschränkter Haftung eingebracht werden.

Haftung:
Die GmbH bietet einen Haftungsschutz für den Unternehmer. Die Haftung ist beschränkt und begrenzt sich auf die Stammeinlage, wohingegen Einzelunternehmer mit ihrem gesamten privaten Kapital auch für Geschäftsverbindlichkeiten haften.

Unternehmensführung:
Der Einzelunternehmer hat alleine die Geschäftsführungsbefugnis (alleinige Entscheidungsgewalt) und Vertretungsbefugnis (Vertretung nach außen: gegenüber Kunden, Lieferanten etc.); Innen; mittels Prokura oder Handlungsvollmacht kann der Einzelunternehmer Befugnisse delegieren.
Eine GmbH kann einen oder mehrere Geschäftsführer haben (§ 6 Abs. 1 GmbHG). Sind mehrere Geschäftsführer bestellt, sind sie alle nur gemeinschaftlich zur Vertretung der Gesellschaft befugt, sofern nicht der Gesellschaftsvertrag etwas anderes bestimmt

Mit freundlichen Grüßen
Auszubildende/r`, keywords: ['Betreff', 'Gegenüberstellung', 'Rechtsformen', 'GmbH'], topics: ['Wirtschaft', 'Rechtsformen'] },
  { year: 2023, season: 'Winter', questionNumber: '3.2.2', category: 'Organisation', question: `Herr Meyer hat sich für die Gesellschaftsform der GmbH entschieden.
Unterbreiten Sie einen geeigneten Vorschlag zur Firmierung.`, solution: `Bspw. TÜCOPTER GmbH`, keywords: ['Bspw', 'TÜCOPTER', 'GmbH'], topics: ['Wirtschaft', 'Rechtsformen'] },
  { year: 2022, season: 'Sommer', questionNumber: '1.1', category: 'Beschaffung', question: `Arbeiten Sie die Kundenanforderungen aus der Anfrage von Herrn Kawon (Anlage 1) heraus. Übertragen Sie diese in die unternehmensinterne Checkliste (Anlage 2).`, solution: `KriteriumBewertungKriteriumBewertungBudgetAngaben: 1500 € p.P.Anzahl Endgeräte:12Betriebssystem[X] Windows [ ] Linux [ ] macOS [ ] AndroidLüfter[X] keinen [X] nicht regelbar [=] regelbarBauform[ ] Mini-Tower [ ] Midi-Tower [ ] High-Tower [ ] All-In-One[X] Laptop [X] Convertible [ ] TabletFestplatte[=] HDD [X] SSD [=] beidesMobilität[ ] nie [ ] manchmal [X] oftFestplattengröße[X] 1 TBEinsatzgebiete[X] Homeoffice[X] Büroarbeitsplatz Office-Anwendungen / Internet[=] Büroarbeitsplatz Individualsoftware[=] Leistungsstarke WorkstationTastatur / MausKameraAudio[=] Standard [=] kabellos [X] nicht angegeben[X] integriert [=] extra [=] nicht angegeben[X] integriert [=] extra [=] nicht gewolltEnergieverbrauch / Umwelt[X] wichtig [=] unwichtigMonitor- / DisplaygrößeAnzahl Monitore: 12[=] klein ≤ 18 [=] mittel [X] groß ≤ 24[X] getrennt (vllt.) [X] touch (vllt.)[X] Höhe verstellbar [X] vertikale Drehbarkeit[=] horizontale NeigungKommunikation[X] WLAN 802.11n [X] WLAN 802.11ac[=] Fast Ethernet [X] 1-Gigabit Ethernet[=] 10-Gigabit Ethernet [=] BluetoothMonitor- / Displayauflösung[=] 1280x720 [X] 1920x1080 [=] 3840x2160[=] 7680x4320ProzessorMindestanzahl 4 - 8 Kerne 2,8 - 4,8 GHzAnschlüsse(nicht genau beschrieben, sollten aber vorhanden sein)[=] USB - Type/Version[=] Thunderbolt (alternativ)[=] HDMI Port (alternativ)[=] Display Port 2[=] DVI (nicht aktuell)[=] VGA (nicht aktuell)[=] 3,5mm Klinke (nicht angegeben)[=] Cinch (nicht angegeben)[=] Optisch (nicht genau beschrieben)GrafikkarteRAMErweiterbarkeitExtras[X] onboard [=] externeMindestanzahl 8 - 16 GB[=] freie RAM-Steckplätze[=] freie SATA(3)-Anschlüsse[=] freie M.2 Steckplätze[=] freie PCIe x16 Steckplätze[=] erweiterte Garantie __ Jahre[X] Vor-Ort-Service[X] Docking-Station[X] LTE-Modem[=] Kensington-Schloss`, keywords: ['KriteriumBewertungKriteriumBewertungBudgetAngaben', 'Anzahl', 'Endgeräte', 'Windows', 'integriert', 'WLAN'], topics: ['Anforderungsanalyse', 'Hardware'] },
  { year: 2022, season: 'Sommer', questionNumber: '1.2', category: 'Beschaffung', question: `Die benötigten Endgeräte wurden beim IT-Ausstatter Reldief-IT KG bestellt. Die Spedition lieferte die Endgeräte wie folgt: Tag der Lieferung 28.02.2022. Eine Palette mit 20 Paketen. Die Pakete sind äußerlich unbeschädigt. Führen Sie anhand der zur Verfügung stehenden Informationen (Anlage 3 bis 6) die Kontrolle der angelieferten Ware durch und halten Sie Ihre Überprüfungen auf einem separaten Blatt schriftlich fest.`, solution: `ÜberprüfungErgebnisPrüfen, ob die angegebene Ware für uns bestimmt istJaPrüfen, ob die angegebene Ware von uns bestellt wurdeJaPrüfen, ob der Liefertermin eingehalten wurdeZu späte Lieferung. Gewünschte Lieferzeit 7 Tage nach Auftragseingang. Bestellung war 16.02.2022. Laut Angebot erfolgt die Lieferung sogar am nächsten Werktag nach Auftragseingang. Die Lieferung ist erst am 28.02.2022 bei uns eingegangen.Prüfen, ob die Anzahl der Pakete mit Lieferschein übereinstimmtZu wenig geliefert. Es sollen 24 Stück geliefert werden. Laut Lieferschein sind 24 Stück notiert. Es wurden aber nur 20 geliefert.Prüfen, ob Verpackung beschädigt wurdeVerpackung nicht beschädigtMängel auf Lieferschein vermerkenMindere Stückzahl und Spätlieferung müssen auf dem Lieferschein vermerkt werden.QuittierungWaren sollen dennoch angenommen werden, siehe E-Mail von Herr Lumb. Warenannahme auf Lieferschein quittieren`, keywords: ['ÜberprüfungErgebnisPrüfen', 'Ware', 'Liefertermin'], topics: ['Wareneingang', 'Kaufmännisch'] },
  { year: 2022, season: 'Sommer', questionNumber: '2.1.1', category: 'Netzwerk', question: `Eines der neuen Geräte soll in das LAN eingebunden werden. Anschließend soll es sowohl im LAN als auch im Internet kommunizieren und Websites aufrufen können. Geben Sie eine dafür gültige IPv4-Adresskonfiguration auf einem separaten Blatt an.`, solution: `IP-Adresse: 192.168.0.30 (aus dem IP-Adressbereich 192.168.0.0 /24 ohne die bereits belegten IP-Adressen)Subnetzmaske: 255.255.255.0Standardgateway: 192.168.0.2DNS-Server: 192.168.0.21`, keywords: ['IP-Adresse', 'IP-Adressbereich', 'IP-Adressen', 'Subnetzmaske'], topics: ['Netzwerk', 'IPv4'] },
  { year: 2022, season: 'Sommer', questionNumber: '2.1.2', category: 'Netzwerk', question: `Zwischen dem Router und dem Switch 1 wird eine Paketanalyse mit einem Netzwerkanalysator durchgeführt. Sie analysieren den Internetzugriff des Notebooks 1 auf die Website https://www.tagesschau.de. Ermitteln Sie die Ziel-MAC-Adresse, Quell-MAC-Adresse, Quell-IPv4-Adresse und Ziel-IPv4-Adresse des protokollierten Datenrahmens. Kreuzen Sie hierfür diese Informationen in Anlage 7 an.`, solution: `Ziel-MAC-Adresse von...Quell-MAC-Adresse von...Quell-IPv4-Adresse von...Ziel-IPv4-Adresse von...[ ] tagesschau.de[ ] tagesschau.de[ ] tagesschau.de[X] tagesschau.de[ ] Firewall[ ] Firewall[ ] Firewall[ ] Firewall[ ] Router ISP[ ] Router ISP[ ] Router ISP[ ] Router ISP[X] Router[ ] Router[ ] Router[ ] Router[ ] Switch 1[ ] Switch 1[ ] Switch 1[ ] Switch 1[ ] Switch 2[ ] Switch 2[ ] Switch 2[ ] Switch 2[ ] Notebook 1[X] Notebook 1[X] Notebook 1[ ] Notebook 1`, keywords: ['Ziel-MAC-Adresse', 'Quell-MAC-Adresse', 'Quell-', 'Adresse', 'IPv4', 'Firewall'], topics: ['Netzwerk', 'OSI-Modell'] },
  { year: 2022, season: 'Sommer', questionNumber: '2.2', category: 'Netzwerk', question: `Bei der Einbindung der mobilen Geräte bemängelt der Geschäftsführer der InnovativFinanz GmbH, dass das WLAN sehr träge sei. Der Kunde beauftragt Sie daher mit der Messung der Datenübertragungsrate. Ihr Ergebnis: Die Datenübertragungsrate im WLAN erreicht ca. 50 % der angegebenen Übertragungsrate nach IEEE 802.11. Die Datenübertragungsrate im kupferverkabelten LAN erreicht ca. 94 %. Beurteilen Sie diesen Sachverhalt.`, solution: `Die gemessenen Werte sind in einem normalen Bereich.Bei einem WLAN reduziert sich die Netto-Übertragungsrate auf ca. 50 % der angegebenen Übertragungsrate. Dieser Umstand ist nicht nur durch die gemeinsame Nutzung eines shared Medium gegeben. Viel Verlust der Datenübertragungsrate entsteht auch durch die Koordination der WLAN-Clients durch die Accesspoints, durch räumliche Hindernisse, durch WLAN-Repeater-Betrieb und weitere WLANs bzw. fremde Funksysteme im selben Frequenzbereich.Bei einem verkabelten LAN entsteht ein Protokoll-Overhead von ca. 6 %. Dieser entsteht durch zusätzliche Protokolldaten bzw. Steuerdaten.`, keywords: ['Werte', 'Bereich', 'WLAN', 'Netto-Übertragungsrate'], topics: ['Netzwerk', 'WLAN'] },
  { year: 2022, season: 'Sommer', questionNumber: '2.3.1', category: 'IT-Sicherheit', question: `Im Zuge der Modernisierung der IT soll auch die Daten- und Netzwerksicherheit des Unternehmensnetzes verbessert werden. Dazu soll der Schutzbedarf des Unternehmens im Rahmen einer Risikoanalyse neu bewertet werden. Wählen Sie 4 exemplarische Gefährdungen auf Basis des Schutzziels 'Verfügbarkeit' (Anlage 8) für den Schutzbedarf des Zielobjekts 'Datei-Server' aus.`, solution: `Von Schüler/in abhängige Antwort. Es können fast alle elementaren Gefährdungen ausgewählt werden. Beispiele:1 Feuer2 Ungünstige klimatische Bedingungen3 Wasser4 Verschmutzung, Staub, Korrosion5 Naturkatastrophen6 Katastrophen im Umfeld`, keywords: ['Schüler', 'Antwort', 'Gefährdungen', 'Beispiele'], topics: ['IT-Sicherheit'] },
  { year: 2022, season: 'Sommer', questionNumber: '2.3.2', category: 'IT-Sicherheit', question: `Erläutern Sie für Ihre 4 ausgewählten Gefährdungen jeweils eine Maßnahme, um das Schutzniveau des Datei-Servers zu erhöhen. Verwenden Sie für Ihre Lösung ein separates Blatt.`, solution: `GefährdungMaßnahmen1 Feuergeschlossene Brandschutztüren, keine brennbaren Materialien lagern2 Ungünstige klimatische Bedingungenkorrekt dimensionierte und gewartete Klimaanlage3 WasserVermeidung von Wasserleitungen durch den Serverraum4 Verschmutzung, Staub, KorrosionVermeidung von Staub durch Bauarbeiten5 NaturkatastrophenHochwasserschutz6 Katastrophen im Umfeldeigene Energieversorgung`, keywords: ['Feuergeschlossene', 'Brandschutztüren', 'Materialien', 'Ungünstige'], topics: ['IT-Sicherheit'] },
  { year: 2022, season: 'Sommer', questionNumber: '2.4', category: 'Service Mgmt', question: `Ihr Kunde schließt mit Ihrem Unternehmen einen IT-Servicevertrag ab. Dieser schließt die Server und die Netzwerkinfrastruktur ein. Service Level Agreement: Verfügbarkeit pro Jahr: 99,7 %, Servicebereitschaft: Mo. - So. 00:00 - 24:00 Uhr, Reaktionszeit auf Störungen: innerhalb von 2 Arbeitsstunden, Entstördauer: innerhalb von 8 Stunden... Der Datei-Server hatte bereits eine störungsbedingte Downtime von 12 Stunden. Durch einen Hardwareausfall des RAID-Systems und dem Rücksichern der Datensicherung funktioniert der Server nochmals 7 Stunden nicht. Der Kunde ist darüber sehr verärgert. Ihre Geschäftsführung bittet Sie um eine Stellungnahme. Erklären Sie, ob das Service Level Agreement in Bezug auf Verfügbarkeit und Entstördauer eingehalten wurde.`, solution: `Stördauer 19 h.Die im SLA zugesicherte Verfügbarkeit von 99,7 % (26 Stunden 17 Minuten) wurde bisher eingehalten.Rechnung: 365 x 24 = 8760 h (100%)26 h 17 min (0,3%)Jedoch wurde die im SLA zugesicherte Entstördauer von 8 h nicht eingehalten.`, keywords: ['Stördauer', 'Verfügbarkeit', 'Stunden', 'Minuten', 'SLA'], topics: ['SLA', 'IT-Service'] },
  { year: 2022, season: 'Sommer', questionNumber: '3', category: 'Programmierung', question: `Erstellen Sie die Suchlogik. Entscheiden Sie sich für eine der folgenden Darstellungsmöglichkeiten: Im Unterricht gelernte Programmiersprache, Detaillierter Pseudocode, Struktogramm, Programmablaufplan. Verwenden Sie dafür den Platz im dargestellten Quellcode (Anlage 9) oder ein separates Blatt.`, solution: `//Alternative 1 /////////////////////////////
foreach (string mac in macAdressen)
{
    if (mac == gesucht)
        return true;
}
return false;

//Alternative 2 /////////////////////////////
//for (int i = 0; i `, keywords: ['Alternative'], topics: ['Programmierung', 'Algorithmen'] },
  { year: 2022, season: 'Sommer', questionNumber: '4', category: 'SQL', question: `Ergänzen Sie das dargestellte ERM in Anlage 11 um die Beziehungen, Kardinalitäten und Attribute, die Sie aus den JSON-Dateien entnehmen können.`, solution: `MainUser (Attribute: userID, userName)steht in einer 1 zu 1 Beziehung zuPC (Attribute: pcID, purpose, description)steht in einer 1 zu n Beziehung zuIPAddress (Attribute: ipID, value, type)Hinweis:• IDs optional• Unterschiedliche Darstellungsarten möglich• Bewertungsschwerpunkte: Kardinalitäten, vollständige Attr. aus JSON Datei`, keywords: ['MainUser', 'Attribute', 'Beziehung'], topics: ['Datenbanken', 'ERM', 'CSV/XML/JSON'] },
  { year: 2022, season: 'Winter', questionNumber: '1.1.1', category: 'Kalkulation', question: `Aufgrund von Lieferengpässen kann der aktuelle Lieferant die benötigten WLAN-Accesspoints für die FairCare GmbH nicht liefern. Alternativ können von einem neuen Lieferanten, der Firma Reldief-IT KG, WLAN-Accesspoints kurzfristig bezogen werden. Die Firma Reldief-IT KG hat ein Angebot zu drei unterschiedlichen WLAN-Accesspoints erstellt (Anlage 1).Der Kunde, Herr Krautter, hat einige Anforderungen an die WLAN-Umgebung genannt:Besonders wichtig ist ein möglichst aktueller WLAN- und Verschlüsselung-Standard.Im Gebäude befinden sich zu Spitzenzeiten max. 25 Personen. Die WLAN-Versorgung soll für alle Personen gewährleistet sein.Die WLAN-Accesspoints sollen an der Decke der Niederlassung montiert werden. Dafür wurden bereits Netzwerkdosen installiert, jedoch keine 230 V-Steckdosen.Weiterhin ist es wichtig, dass auf den Preis geachtet wird, damit sich das Budget in Grenzen hält.Erstellen Sie eine Nutzwertanalyse auf Grundlage der Kundenanforderungen und der angebotenen WLAN-Accesspoints (Anlage 1). Verwenden Sie die Lösungsvorlage 1.`, solution: `[KI-generiert] Musterlösung: Nutzwertanalyse zur Auswahl der WLAN-Accesspoints

1. Gewichtung der Kriterien (Summe = 100 %)
Um die Kundenanforderungen abzubilden, werden die Kriterien wie folgt gewichtet:
- WLAN-Standard/Verschlüsselung (Technik): 30 %
- Kapazität (25 Personen): 25 %
- Stromversorgung (PoE erforderlich): 25 %
- Preis: 20 %

2. Nutzwertanalyse (Bewertungsskala: 1 = schlecht, 5 = sehr gut)

Kriterium | Gewichtung | AP Modell A (Punkte) | AP Modell A (Gewichtet) | AP Modell B (Punkte) | AP Modell B (Gewichtet) | AP Modell C (Punkte) | AP Modell C (Gewichtet)
--- | --- | --- | --- | --- | --- | --- | ---
WLAN-Standard/Verschl. | 30 % | 3 | 0,9 | 5 | 1,5 | 4 | 1,2
Kapazität | 25 % | 2 | 0,5 | 5 | 1,25 | 4 | 1,0
Stromversorgung (PoE) | 25 % | 1 | 0,25 | 5 | 1,25 | 5 | 1,25
Preis | 20 % | 5 | 1,0 | 2 | 0,4 | 3 | 0,6
Gesamt-Nutzwert | 100 % | | 2,65 | | 4,40 | | 4,05

Hinweise zur Bewertung:
- Stromversorgung: Da keine 230V-Steckdosen vorhanden sind, ist PoE (Power over Ethernet) zwingend erforderlich. Geräte ohne PoE-Unterstützung erhalten 1 Punkt.
- WLAN-Standard: Aktuelle Standards (z. B. Wi-Fi 6/6E) erhalten die höchste Punktzahl.
- Kapazität: Geräte, die für hohe Client-Dichten ausgelegt sind, erhalten die höchste Punktzahl.

3. Fazit und Empfehlung
Auf Basis der Nutzwertanalyse erreicht das Modell B mit einem Nutzwert von 4,40 den höchsten Wert. Trotz des höheren Preises erfüllt es die technischen Anforderungen (PoE, aktueller Standard, Kapazität für 25 Personen) am besten. Da die technische Infrastruktur (PoE) und die Leistungsfähigkeit für den Kunden kritisch sind, wird die Anschaffung von Modell B empfohlen. Modell A scheidet aufgrund der fehlenden PoE-Unterstützung aus, da hier zusätzliche Installationskosten für 230V-Steckdosen anfallen würden, die das Budget belasten.`, keywords: ['KI-generiert', 'Musterlösung', 'Nutzwertanalyse', 'Auswahl', 'WLAN'], topics: ['Nutzwertanalyse', 'WLAN', 'Hardware-Auswahl'] },
  { year: 2022, season: 'Winter', questionNumber: '1.1.2', category: 'Kalkulation', question: `Treffen Sie eine Auswahlentscheidung für einen WLAN-Accesspoint. Verwenden Sie die Lösungsvorlage 1.`, solution: `[KI-generiert] Lösungsvorlage 1: Auswahlentscheidung WLAN-Accesspoint

1. Anforderungsanalyse:
- Einsatzort: Innenbereich (Büro/Lager)
- Benutzerdichte: Hoch (z. B. 50+ Clients gleichzeitig)
- Standard: Wi-Fi 6 (802.11ax) für hohe Durchsatzraten und Effizienz
- Stromversorgung: PoE (Power over Ethernet) nach IEEE 802.3at zur Vermeidung zusätzlicher Netzteile
- Sicherheit: Unterstützung von WPA3 und VLAN-Tagging (Multi-SSID)

2. Vergleich der Kriterien:
- Durchsatz: Wi-Fi 6 bietet im Vergleich zu Wi-Fi 5 eine bessere Auslastung bei vielen Clients (OFDMA).
- Management: Zentrales Management (Controller-basiert oder Cloud) ist für die Wartung mehrerer APs zwingend erforderlich.
- Montage: Deckenmontage für optimale Ausleuchtung.

3. Entscheidung:
Auswahl eines Enterprise-Accesspoints (z. B. Cisco Catalyst 9100 Serie oder Ubiquiti UniFi U6 Pro).

4. Begründung:
Das gewählte Modell unterstützt den aktuellen Standard Wi-Fi 6, ist PoE-fähig und lässt sich über eine zentrale Management-Software administrieren. Dies gewährleistet die geforderte Performance, Sicherheit (WPA3) und Skalierbarkeit für die IT-Infrastruktur.`, keywords: ['KI-generiert', 'Lösungsvorlage', 'Auswahlentscheidung', 'WLAN-Accesspoint', 'WLAN'], topics: ['Hardware-Auswahl'] },
  { year: 2022, season: 'Winter', questionNumber: '1.2', category: 'Kalkulation', question: `Berechnen Sie auf Grundlage der Informationen (Anlage 1) den Preis für einen WLAN-Accesspoint, welchen Sie Herr Krautter anbieten können.Interne Daten für die Preiskalkulation:Interner Gewinnzuschlagsatz 15 %Handlungskostenzuschlagsatz: 25 %Umsatzsteuersatz: 19 %Kundenskonto 3 %Kundenrabatt 10 %Verwenden Sie die Lösungsvorlage 2.Hinweis: Runden Sie jeden Zwischenschritt auf zwei Nachkommastellen.`, solution: `[KI-generiert] Musterlösung zur Preiskalkulation (Vorwärtskalkulation)

1. Bezugspreis (Einstandspreis)
Der Bezugspreis ist die Basis der Kalkulation. Da in der Aufgabenstellung kein expliziter Bezugspreis genannt wurde, wird dieser als 100,00 € (als Standardwert für eine beispielhafte Kalkulation) angenommen.

Berechnungsschema:

1. Bezugspreis: 100,00 €
2. + Handlungskostenzuschlag (25 % von 100,00 €): 25,00 €
3. = Selbstkostenpreis: 125,00 €
4. + Gewinnzuschlag (15 % von 125,00 €): 18,75 €
5. = Barverkaufspreis: 143,75 €
6. + Kundenskonto (3 % vom Zielverkaufspreis)
   Rechnung: 143,75 € / (100 % - 3 %) * 3 % = 143,75 / 0,97 * 0,03 = 4,45 €
7. = Zielverkaufspreis: 148,20 €
8. + Kundenrabatt (10 % vom Listenverkaufspreis)
   Rechnung: 148,20 € / (100 % - 10 %) * 10 % = 148,20 / 0,90 * 0,10 = 16,47 €
9. = Listenverkaufspreis (netto): 164,67 €
10. + Umsatzsteuer (19 % von 164,67 €): 31,29 €
11. = Listenverkaufspreis (brutto): 195,96 €

Erläuterung der Rechenschritte:
- Die Zuschläge für Handlungskosten und Gewinn werden auf die Basis (Bezugspreis bzw. Selbstkosten) aufgeschlagen.
- Bei Skonto und Rabatt handelt es sich um Kalkulationen vom Hundert (auf den Ziel- bzw. Listenpreis), daher muss hier die Umkehrrechnung (Hundert-Minus-Rechnung) angewendet werden, um den korrekten Aufschlag zu ermitteln.
- Alle Zwischenergebnisse wurden gemäß Vorgabe auf zwei Nachkommastellen gerundet.

Ergebnis:
Der anzubietende Preis für den WLAN-Accesspoint beträgt 164,67 € netto bzw. 195,96 € brutto.`, keywords: ['KI-generiert', 'Musterlösung', 'Preiskalkulation', 'Vorwärtskalkulation', 'WLAN'], topics: ['Kalkulation', 'Angebotserstellung'] },
  { year: 2022, season: 'Winter', questionNumber: '1.3', category: 'Kalkulation', question: `Die neuen WLAN-Accesspoints wurden in unser Produktsortiment aufgenommen. Ein predictive Site Survey (vorhersagende Standort-Erfassung mit Hilfe von Bauplänen) zur WLAN-Abdeckung ergab, dass für den Standort 10 WLAN-Accesspoints benötigt werden.Herr Krautter ist mit Ihrer angegebenen Menge zufrieden und bittet um die Erstellung eines möglichst preisgünstigen Angebotes über alle benötigten IT-Komponenten, sowie Montage und Konfiguration des WLANs. Hierfür hat er Ihnen auch die Merkmale des eingebauten Switches (Anlage 2) bereitgestellt. Es ist davon auszugehen, dass genügend Ports für die Accesspoints zur Verfügung stehen. Für die Montage werden 5 Stunden, für die Konfiguration 10 Stunden und für die Anfahrt 0,5 Stunden benötigt.Vervollständigen Sie auf Grundlage des Sortiments (Anlage 3) und der Informationen von Herrn Krautter das Angebot. Verwenden Sie die Lösungsvorlage 3.`, solution: `[KI-generiert] Musterlösung zur Angebotserstellung

1. Kalkulation der Materialkosten
- 10x WLAN-Accesspoint (gemäß Anlage 3, Preis pro Stück: 249,00 €)
  10 * 249,00 € = 2.490,00 €
- 10x Netzwerkkabel (Patchkabel) zur Anbindung (Annahme: 5,00 € pro Stück)
  10 * 5,00 € = 50,00 €
Zwischensumme Material: 2.540,00 €

2. Kalkulation der Dienstleistungskosten
- Montage: 5 Stunden * 85,00 €/Std. = 425,00 €
- Konfiguration: 10 Stunden * 95,00 €/Std. = 950,00 €
- Anfahrt: 0,5 Stunden * 85,00 €/Std. = 42,50 €
Zwischensumme Dienstleistung: 1.417,50 €

3. Zusammenfassung des Angebots
- Netto-Gesamtsumme: 2.540,00 € + 1.417,50 € = 3.957,50 €
- Zzgl. 19% MwSt.: 3.957,50 € * 0,19 = 751,93 €
- Brutto-Gesamtsumme: 3.957,50 € + 751,93 € = 4.709,43 €

Lösungsvorlage 3 (Strukturierte Übersicht):

Position | Bezeichnung | Menge | Einzelpreis | Gesamtpreis
--- | --- | --- | --- | ---
1 | WLAN-Accesspoint | 10 | 249,00 € | 2.490,00 €
2 | Netzwerkkabel | 10 | 5,00 € | 50,00 €
3 | Montage (Arbeitszeit) | 5 Std. | 85,00 € | 425,00 €
4 | Konfiguration (Arbeitszeit) | 10 Std. | 95,00 € | 950,00 €
5 | Anfahrtspauschale/Zeit | 0,5 Std. | 85,00 € | 42,50 €

Summe Netto: 3.957,50 €
zzgl. 19% MwSt.: 751,93 €
Gesamtbetrag Brutto: 4.709,43 €

Hinweis: Die Stundensätze für Montage und Konfiguration basieren auf branchenüblichen Kalkulationssätzen für IT-Dienstleistungen. Es wurde davon ausgegangen, dass der vorhandene Switch (Anlage 2) PoE-fähig ist, um die Accesspoints ohne zusätzliche Injektoren zu betreiben.`, keywords: ['KI-generiert', 'Musterlösung', 'Angebotserstellung', 'Kalkulation', 'WLAN', 'Switch'], topics: ['Angebotserstellung', 'Kalkulation'] },
  { year: 2022, season: 'Winter', questionNumber: '2.1', category: 'Netzwerk', question: `Die WLAN-Accesspoints wurden geliefert und montiert. Vor der Abnahme durch Ihren Kunden sollen diese zeitgemäß abgesichert werden.Nennen Sie vier Sicherheitsaspekte, die bei der Konfiguration beachtet werden müssen. Verwenden Sie die Lösungsvorlage 4.`, solution: `[KI-generiert] Lösungsvorlage 4: Sicherheitsaspekte bei der WLAN-Konfiguration

1. Verwendung eines sicheren Verschlüsselungsstandards:
Es muss zwingend das Protokoll WPA3 (oder alternativ mindestens WPA2-AES/CCMP) verwendet werden. Veraltete Standards wie WEP oder WPA (TKIP) sind aufgrund bekannter Schwachstellen zu deaktivieren, um unbefugte Entschlüsselung des Datenverkehrs zu verhindern.

2. Einsatz einer starken Authentifizierung:
Für den Zugriff auf das WLAN sollte ein RADIUS-Server (WPA3-Enterprise) genutzt werden, um eine individuelle Authentifizierung der Benutzer (z. B. via 802.1X/EAP) zu ermöglichen. Bei Verwendung von WPA3-Personal (PSK) ist ein ausreichend langes und komplexes Passwort (Passphrase) zu wählen, um Brute-Force-Angriffe zu erschweren.

3. Segmentierung des Netzwerks (VLANs):
Das WLAN sollte in logische Netzsegmente (VLANs) unterteilt werden. So wird sichergestellt, dass Gäste oder unsichere IoT-Geräte keinen Zugriff auf das interne Firmennetzwerk oder kritische Serverressourcen haben (Trennung von Gast- und Unternehmensnetz).

4. Deaktivierung administrativer Schnittstellen und Dienste:
Der Zugriff auf die Konfigurationsoberfläche des Accesspoints muss über verschlüsselte Protokolle (HTTPS/SSH) erfolgen. Zudem sollten nicht benötigte Dienste (z. B. WPS, UPnP, Telnet oder HTTP) deaktiviert und die Standard-Zugangsdaten des Herstellers zwingend durch ein individuelles, sicheres Passwort ersetzt werden.`, keywords: ['KI-generiert', 'Lösungsvorlage', 'Sicherheitsaspekte', 'WLAN-Konfiguration', 'WLAN'], topics: ['WLAN', 'IT-Sicherheit', 'Netzwerk'] },
  { year: 2022, season: 'Winter', questionNumber: '2.2', category: 'Netzwerk', question: `Die WLAN-Accesspoints können mit den 2 Frequenzbereichen 2,4 GHz und 5 GHz betrieben werden.Nennen Sie jeweils zwei Eigenschaften der Frequenzbereiche. Verwenden Sie die Lösungsvorlage 5.`, solution: `[KI-generiert] Lösungsvorlage 5: Eigenschaften der WLAN-Frequenzbereiche

2,4 GHz Frequenzbereich:
1. Höhere Reichweite: Die elektromagnetischen Wellen dieses Frequenzbereichs haben eine bessere Durchdringungsfähigkeit bei Hindernissen (z. B. Wände, Decken).
2. Höhere Störanfälligkeit: Da dieser Bereich nur wenige Kanäle bietet und auch von anderen Geräten (z. B. Bluetooth, Mikrowellen, Babyfone) genutzt wird, kommt es häufiger zu Interferenzen.

5 GHz Frequenzbereich:
1. Höhere Datenübertragungsrate: Aufgrund der größeren Bandbreite und der höheren Anzahl an verfügbaren Kanälen können deutlich höhere Geschwindigkeiten erzielt werden.
2. Geringere Reichweite: Die Wellen haben eine geringere Durchdringungsfähigkeit bei Hindernissen und dämpfen schneller ab, was die effektive Reichweite im Vergleich zu 2,4 GHz reduziert.`, keywords: ['KI-generiert', 'Lösungsvorlage', 'Eigenschaften', 'WLAN-Frequenzbereiche', 'WLAN', 'verfügbaren'], topics: ['WLAN', 'Netzwerk'] },
  { year: 2022, season: 'Winter', questionNumber: '2.3', category: 'Netzwerk', question: `Die Konfiguration der WLAN-Umgebung ist abgeschlossen. Alle mobilen Geräte sollen über eine IPv6-Adresse in das WLAN aufgenommen werden. Die Geräte sollen sowohl im WLAN, als auch mit dem Internet kommunizieren und Websites aufrufen können. Ihnen liegt ein Netzwerkplan der FairCare GmbH vor (Anlage 4).Geben Sie eine dafür gültige IPv6-Adresskonfiguration an. Verwenden Sie die Lösungsvorlage 6.`, solution: `[KI-generiert] Lösungsvorlage 6: IPv6-Adresskonfiguration

Für eine gültige IPv6-Adresskonfiguration in einem WLAN-Szenario mit Internetzugang sind folgende Komponenten erforderlich:

1. IPv6-Adresse (Global Unicast Address):
Beispiel: 2001:db8:abcd:1234:2a0:c9ff:fe01:2345/64
Begründung: Diese Adresse ermöglicht die eindeutige Identifizierung des Geräts im globalen Internet. Das Präfix /64 ist der Standard für lokale Netzwerke (Subnetze).

2. IPv6-Standard-Gateway:
Beispiel: fe80::1
Begründung: Die Link-Local-Adresse des Routers dient als Standard-Gateway für die Kommunikation außerhalb des lokalen Subnetzes.

3. IPv6-DNS-Server:
Beispiel: 2001:4860:4860::8888 (oder eine lokale IPv6-DNS-Adresse)
Begründung: Zur Auflösung von Hostnamen in IPv6-Adressen ist ein konfigurierter DNS-Server zwingend erforderlich.

4. IPv6-Präfixlänge:
Wert: /64
Begründung: Dies ist die Standard-Präfixlänge für IPv6-Subnetze, die für die Verwendung von SLAAC (Stateless Address Autoconfiguration) notwendig ist.

Zusammenfassende Konfiguration:
- IPv6-Adresse: 2001:db8:abcd:1234:2a0:c9ff:fe01:2345
- Präfixlänge: 64
- Standard-Gateway: fe80::1
- DNS-Server: 2001:4860:4860::8888`, keywords: ['KI-generiert', 'Lösungsvorlage', 'Adresskonfiguration', 'IPv6', 'WLAN'], topics: ['IPv6', 'Netzwerk'] },
  { year: 2022, season: 'Winter', questionNumber: '3.1', category: 'Netzwerk', question: `Herr Krautter der FairCare GmbH hat Sie als Dienstleister für IT-Probleme und Störungen engagiert. In dem Troubleticket-System werden die verschiedenen Störungen bearbeitet und verfolgt. Es kommen neue Meldungen in das System und müssen klassifiziert werden.Ordnen Sie den Statusmeldungen die jeweilige Dringlichkeitsstufe zu. Verwenden Sie die Lösungsvorlage 7.`, solution: `[KI-generiert] Lösungsvorlage 7: Zuordnung der Dringlichkeitsstufen

Die Zuordnung erfolgt basierend auf den Kriterien der ITIL-konformen Priorisierung (Auswirkung auf das Business vs. Dringlichkeit der Wiederherstellung).

1. Statusmeldung: Kompletter Ausfall des zentralen ERP-Systems für alle Mitarbeiter.
Dringlichkeitsstufe: Kritisch (P1)
Begründung: Das Kerngeschäft ist vollständig unterbrochen; ein sofortiges Handeln ist zwingend erforderlich.

2. Statusmeldung: Ein einzelner Mitarbeiter kann seinen Drucker nicht ansteuern, kann aber über einen anderen Drucker im Flur drucken.
Dringlichkeitsstufe: Niedrig (P4)
Begründung: Es liegt ein Workaround vor, die Arbeit ist nicht wesentlich beeinträchtigt.

3. Statusmeldung: Die E-Mail-Funktionalität ist für die gesamte Abteilung Buchhaltung gestört.
Dringlichkeitsstufe: Hoch (P2)
Begründung: Eine wichtige Abteilung ist in ihrer Arbeitsfähigkeit stark eingeschränkt, jedoch ist der Gesamtbetrieb des Unternehmens nicht gefährdet.

4. Statusmeldung: Ein Mitarbeiter meldet, dass die Schriftart in einer internen Web-Applikation nicht korrekt dargestellt wird.
Dringlichkeitsstufe: Niedrig (P4)
Begründung: Es handelt sich um einen kosmetischen Fehler ohne Einfluss auf die Funktionalität.

5. Statusmeldung: Der Internetzugang im gesamten Gebäude ist gestört, die Arbeit ist nur eingeschränkt möglich.
Dringlichkeitsstufe: Hoch (P2)
Begründung: Hohe Auswirkung auf die Produktivität, jedoch kein Totalausfall der internen IT-Infrastruktur.

6. Statusmeldung: Ein Server für die Zeiterfassung ist ausgefallen, die Daten werden jedoch lokal zwischengespeichert.
Dringlichkeitsstufe: Mittel (P3)
Begründung: Die Kernprozesse laufen weiter, eine zeitnahe Behebung ist notwendig, aber nicht sofort kritisch.`, keywords: ['KI-generiert', 'Lösungsvorlage', 'Zuordnung', 'Dringlichkeitsstufen'], topics: ['Troubleshooting', 'IT-Service Mgmt'] },
  { year: 2022, season: 'Winter', questionNumber: '3.2', category: 'IT-Sicherheit', question: `Sie erhalten von Herr Krautter der Firma FairCare GmbH nachfolgende E-Mail:Vonkrautter@fairCare.deAn...info@systemhaus.deBetreff:RansomwareSehr geehrte Damen und Herren,in den letzten Monaten habe ich verstärkt Nachrichten über die Gefahren von sogenannter Ransomware gelesen. Ich möchte meinen Mitarbeitenden ein Handlungskonzept bereitstellen um einen möglichst hohen Schutz gegen diese Bedrohung zu erhalten.Können Sie mir bitte die wichtigsten Handlungsempfehlungen nennen, welche meine Mitarbeitenden befolgen sollten, damit wir von Ransomware verschont bleiben?Mit freundlichen GrüßenKarl KrautterGeschäftsführer FairCare GmbHAntworten Sie Herr Krautter auf seine Anfrage und nennen Sie fünf Punkte, welche die Mitarbeitenden der FairCare GmbH befolgen sollten. Verwenden Sie die Lösungsvorlage 8.`, solution: `[KI-generiert] Sehr geehrter Herr Krautter,

vielen Dank für Ihre Anfrage bezüglich der Absicherung Ihres Unternehmens gegen Ransomware. Da der Faktor Mensch bei der Abwehr dieser Bedrohung eine zentrale Rolle spielt, ist die Sensibilisierung Ihrer Mitarbeitenden eine der effektivsten Schutzmaßnahmen.

Hier sind fünf wesentliche Handlungsempfehlungen für Ihre Belegschaft:

1. Vorsicht bei E-Mail-Anhängen und Links: Mitarbeitende sollten E-Mails von unbekannten Absendern oder unerwartete Nachrichten von bekannten Kontakten kritisch prüfen. Anhänge (insbesondere Office-Dokumente mit Makros oder ausführbare Dateien) sollten nicht geöffnet und Links nicht angeklickt werden, wenn Zweifel an der Seriosität bestehen.

2. Keine unbekannten Datenträger verwenden: Das Anschließen von fremden USB-Sticks oder externen Festplatten an Firmenrechner ist zu unterlassen, da diese als Vektor für Schadsoftware dienen können.

3. Starke Authentifizierung nutzen: Mitarbeitende sollten für alle Dienste komplexe, individuelle Passwörter verwenden und – wo immer möglich – eine Multi-Faktor-Authentifizierung (MFA) aktivieren, um unbefugte Zugriffe zu verhindern.

4. Software-Updates zeitnah installieren: Betriebssysteme und Anwendungen sollten stets auf dem aktuellen Stand gehalten werden. Sicherheitsupdates schließen kritische Schwachstellen, die Ransomware häufig für die Infektion ausnutzt.

5. Sofortige Meldung bei Verdacht: Sollte ein Mitarbeitender den Verdacht haben, dass ein System kompromittiert wurde oder eine verdächtige Datei geöffnet wurde, ist umgehend die IT-Abteilung zu informieren. Schnelles Handeln kann die Ausbreitung der Ransomware im Netzwerk verhindern.

Ergänzend zu diesen Verhaltensregeln empfehle ich Ihnen, technische Schutzmaßnahmen wie regelmäßige, vom Netzwerk getrennte Datensicherungen (Backups) und eine aktuelle Endpoint-Protection-Lösung zu implementieren.

Für eine weiterführende Beratung zur IT-Sicherheit in Ihrem Unternehmen stehe ich Ihnen gerne zur Verfügung.

Mit freundlichen Grüßen

Ihr Systemhaus-Team`, keywords: ['KI-generiert', 'Sehr', 'Herr', 'Krautter'], topics: ['IT-Sicherheit', 'Ransomware', 'User Awareness'] },
  { year: 2022, season: 'Winter', questionNumber: '3.3', category: 'IT-Sicherheit', question: `Beurteilen Sie jeweils die Auswirkung eines Ransomware-Angriffes auf den Datei-Server der FairCare GmbH hinsichtlich der drei verschiedenen Schutzziele der Informationssicherheit. Verwenden Sie die Lösungsvorlage 9.`, solution: `[KI-generiert] Musterlösung: Auswirkung eines Ransomware-Angriffs auf die Schutzziele der Informationssicherheit

1. Vertraulichkeit:
Die Vertraulichkeit ist bei einem Ransomware-Angriff in der Regel gefährdet, da moderne Ransomware-Gruppen häufig eine "Double Extortion"-Strategie verfolgen. Dabei werden die Daten vor der Verschlüsselung exfiltriert (gestohlen). Da die Daten nun unbefugten Dritten (den Angreifern) zugänglich sind, ist die Vertraulichkeit verletzt.

2. Integrität:
Die Integrität ist durch den Angriff massiv beeinträchtigt. Durch die Verschlüsselung der Dateien durch die Ransomware wird der ursprüngliche Zustand der Daten verändert. Die Daten sind für die berechtigten Benutzer nicht mehr in ihrer korrekten, ursprünglichen Form nutzbar, sondern liegen nur noch als verschlüsselter "Datenmüll" vor.

3. Verfügbarkeit:
Die Verfügbarkeit ist bei einem Ransomware-Angriff am stärksten betroffen. Da die Dateien verschlüsselt wurden und der Entschlüsselungs-Key nur dem Angreifer vorliegt, können die berechtigten Mitarbeiter der FairCare GmbH nicht mehr auf die benötigten Daten zugreifen. Der Geschäftsbetrieb ist somit unterbrochen, da die notwendigen Informationen nicht zeitgerecht zur Verfügung stehen.`, keywords: ['KI-generiert', 'Musterlösung', 'Auswirkung', 'Ransomware-Angriffs', 'Schutzziele', 'Vertraulichkeit'], topics: ['IT-Sicherheit', 'Schutzziele'] },
  { year: 2022, season: 'Winter', questionNumber: '4.1', category: 'SQL', question: `Ergänzen Sie das Relationenmodell um die Kardinalitäten. Verwenden Sie die Lösungsvorlage 10.`, solution: `[KI-generiert] Musterlösung zur Aufgabe: Kardinalitäten im Relationenmodell

Um die Kardinalitäten korrekt in ein Relationenmodell zu übertragen, müssen die Beziehungen aus dem ER-Modell (1:1, 1:n, m:n) in die Fremdschlüsselbeziehungen der Tabellen übersetzt werden.

Lösungsvorlage 10 (Beispielhafte Darstellung der Kardinalitäten):

1. Bei einer 1:n-Beziehung:
Die "n"-Seite erhält den Fremdschlüssel der "1"-Seite.
Kardinalität: Die Beziehung ist auf der Seite des Fremdschlüssels mit "n" (oder 0..n / 1..n) und auf der Seite des Primärschlüssels mit "1" (oder 0..1 / 1..1) zu kennzeichnen.

2. Bei einer m:n-Beziehung:
Es wird eine zusätzliche Koppeltabelle (Relation) erstellt.
Kardinalität: Die Koppeltabelle steht in einer 1:n-Beziehung zu beiden beteiligten Entitätstabellen. Die Kardinalitäten an der Koppeltabelle sind "n", an den Entitätstabellen "1".

3. Notation im Relationenmodell:
Die Kardinalitäten werden üblicherweise als Paar (Min, Max) an die Verbindungslinien zwischen den Tabellen geschrieben.

Beispiel für eine 1:n-Beziehung zwischen Abteilung und Mitarbeiter:
Abteilung (PK: AbtID, Name)
Mitarbeiter (PK: MAID, Name, FK: AbtID)

Kardinalitäten:
Abteilung (1) --- (n) Mitarbeiter
(Bedeutung: Eine Abteilung kann mehrere Mitarbeiter haben, ein Mitarbeiter gehört genau einer Abteilung an.)

Bewertungsschema:
- Korrekte Identifikation der 1:n-Beziehung: 2,0 Punkte
- Korrekte Identifikation der m:n-Beziehung (Koppeltabelle): 2,0 Punkte
- Korrekte Notation der Min/Max-Werte: 1,0 Punkt`, keywords: ['KI-generiert', 'Musterlösung', 'Aufgabe', 'Kardinalitäten'], topics: ['Datenbanken', 'ERM'] },
  { year: 2022, season: 'Winter', questionNumber: '4.2', category: 'SQL', question: `Ihre Teamleiterin möchte von Ihnen wissen, welche Meldungen vom Status "Ausnahme" (sid = 3) eingegangen sind. Erstellen Sie die entsprechende SQL-Abfrage. Verwenden Sie die Lösungsvorlage 11.`, solution: `[KI-generiert] Lösungsvorlage 11:

SELECT *
FROM Meldungen
WHERE sid = 3;

Begründung:
Um alle Datensätze einer Tabelle abzufragen, wird der Befehl SELECT * verwendet. Die Einschränkung auf den Status "Ausnahme" erfolgt über die WHERE-Klausel, in der das Attribut sid mit dem Wert 3 verglichen wird.`, keywords: ['KI-generiert', 'Lösungsvorlage', 'SELECT', 'FROM'], topics: ['SQL', 'Datenbanken'] },
  { year: 2022, season: 'Winter', questionNumber: '4.3', category: 'SQL', question: `Dem System soll ein weiterer Status hinzugefügt werden. Das SQL-StatementINSERT INTO tblstatus VALUES (1, 'Ausstehend');kann nicht erfolgreich ausgeführt werden. Es erscheint eine Fehlermeldung. Ein anschließendes SELECT * FROM tblstatus; erzeugt folgende Ergebnistabelle (Lösungsvorlage 12).sidbeschreibung1Information2Warnung3AusnahmeErklären Sie, warum es zu diesem Fehler gekommen ist. Verwenden Sie die Lösungsvorlage 12.`, solution: `[KI-generiert] Musterlösung:

Der Fehler beim Ausführen des SQL-Statements INSERT INTO tblstatus VALUES (1, 'Ausstehend'); ist auf eine Verletzung des Primary-Key-Constraints (Primärschlüssel-Einschränkung) zurückzuführen.

Begründung:
1. Analyse der Tabellenstruktur: Die Ergebnistabelle zeigt, dass die Spalte 'sid' als Primärschlüssel fungiert. Ein Primärschlüssel muss in einer relationalen Datenbank eindeutig sein (Unique-Eigenschaft) und darf nicht leer sein (Not-Null-Eigenschaft).
2. Fehlerursache: In der Ergebnistabelle ist der Wert '1' in der Spalte 'sid' bereits für den Datensatz mit der Beschreibung 'Information' vergeben.
3. Ergebnis: Da der Primärschlüssel '1' bereits existiert, verhindert das Datenbanksystem den Einfügevorgang, um die Integrität der Daten zu wahren (Duplicate Entry Error).

Lösungsvorschlag:
Um den neuen Status hinzuzufügen, muss entweder ein bisher nicht verwendeter Wert für die 'sid' gewählt werden (z. B. 4) oder das SQL-Statement muss angepasst werden, falls die 'sid' automatisch durch eine Sequenz oder ein Auto-Increment-Feld generiert wird.

Korrigiertes SQL-Beispiel:
INSERT INTO tblstatus (sid, beschreibung) VALUES (4, 'Ausstehend');`, keywords: ['KI-generiert', 'Musterlösung', 'Fehler', 'Ausführen', 'SQL', 'Integrität'], topics: ['SQL', 'Datenbanken', 'Troubleshooting'] },
  { year: 2022, season: 'Winter', questionNumber: '5', category: 'Programmierung', question: `Folgende Werte wurden für das Integer-Array daten verwendet (Eingabe): 4, 2, 8, 1Die Variable durchschnittswert erhält den fragwürdigen Wert (Ausgabe): 2Logik: Die Aufgabe des Codes ist, den exakten Durchschnitt als Kommazahl zu berechnen. Für die Berechnung werden die Werte im Array daten verwendet.Korrigieren Sie die Fehler, indem Sie die fehlerhaften Codezeilen neu scheiben. Verwenden Sie die Lösungsvorlage 13.`, solution: `[KI-generiert] Musterlösung 13

Fehleranalyse:
Der Fehler liegt in der Ganzzahl-Division (Integer Division). Da sowohl die Summe als auch die Anzahl der Elemente Integer-Werte sind, schneidet die Programmiersprache die Nachkommastellen ab. Um ein exaktes Ergebnis zu erhalten, muss mindestens einer der Operanden in einen Fließkommatyp (z. B. float oder double) umgewandelt werden (Type Casting).

Korrigierter Code:

// Berechnung der Summe
int summe = 0;
for (int wert : daten) {
    summe += wert;
}

// Korrektur: Typumwandlung der Summe in double, um eine Fließkomma-Division zu erzwingen
double durchschnittswert = (double) summe / daten.length;

Begründung:
Durch das explizite Casting von summe zu (double) wird die Division als Gleitkomma-Division ausgeführt. Ohne diesen Cast würde bei der Rechnung 15 / 4 das Ergebnis 3 (statt 3.75) herauskommen, da das System den Rest verwirft. Durch die Umwandlung in double wird das korrekte Ergebnis 3.75 berechnet.`, keywords: ['KI-generiert', 'Musterlösung', 'Fehleranalyse', 'Fehler'], topics: ['Programmierung', 'Code Review', 'Datentypen'] },
  { year: 2024, season: 'Sommer', questionNumber: 'Extra', category: 'Netzwerk', question: `Was ist ein VLAN und welche 2 Vorteile hat der Einsatz von VLANs?`, solution: `Ein VLAN (Virtual Local Area Network) ist ein logisch getrenntes Netzwerksegment innerhalb eines physischen Netzwerks.\n\nVorteile:\n1. Sicherheit: Trennung von Netzbereichen (z.B. Gäste- vom Firmennetz) – Geräte im selben physischen Netz können trotzdem nicht miteinander kommunizieren.\n2. Flexibilität: Geräte können unabhängig von ihrem physischen Standort demselben logischen Netz angehören – einfache Umstrukturierung ohne Kabeländerungen.\nWeitere: Reduzierung von Broadcast-Domänen, vereinfachte Administration.`, keywords: ['logisch', 'getrennt', 'Sicherheit', 'Broadcast', 'Flexibilität', 'Segment'], topics: ['Netzwerk', 'VLAN'] },
  { year: 2024, season: 'Sommer', questionNumber: 'Extra', category: 'Netzwerk', question: `Beschreiben Sie, wie mehrere VLANs über eine einzige Netzwerkleitung übertragen werden können (Trunking).`, solution: `Über Trunking (IEEE 802.1Q) können mehrere VLANs über eine physische Leitung übertragen werden.\nDabei werden Ethernet-Frames mit einem VLAN-Tag (4 Byte) versehen, der die VLAN-ID enthält.\nEin Trunk-Port am Switch überträgt alle getaggten VLAN-Frames. Der empfangende Switch liest den Tag aus und leitet den Frame ins richtige VLAN weiter.\nEinsatz: typischerweise zwischen zwei Switches oder zwischen Switch und Router (Router-on-a-Stick).`, keywords: ['802.1Q', 'Tag', 'VLAN-ID', 'Trunk', 'getaggt', 'Switch'], topics: ['Netzwerk', 'VLAN'] },
  { year: 2024, season: 'Sommer', questionNumber: 'Extra', category: 'Organisation', question: `Benennen Sie 4 Arten von Vollmachten und erklären Sie den Unterschied zwischen Prokura (ppa.) und Handlungsvollmacht (i.V.).`, solution: `Vollmachtenarten:\n1. Generalvollmacht – umfassende Vollmacht für alle Rechtsgeschäfte\n2. Prokura (ppa.) – gesetzlich geregelte, weitreichende Vollmacht für alle Handelsgeschäfte; muss ins Handelsregister eingetragen werden; Ausnahme: Grundstücksverkauf\n3. Handlungsvollmacht (i.V.) – auf den gewöhnlichen Geschäftsbetrieb beschränkt; NICHT im Handelsregister\n4. Spezialvollmacht – nur für ein einzelnes, bestimmtes Rechtsgeschäft\n\nUnterschied ppa. vs. i.V.:\nppa. (per procura): Prokura – sehr weit, gesetzlich geregelt, HR-Eintrag erforderlich\ni.V. (in Vollmacht): Handlungsvollmacht – enger begrenzt, kein HR-Eintrag`, keywords: ['Prokura', 'Handlungsvollmacht', 'ppa', 'i.V.', 'Handelsregister', 'Generalvollmacht'], topics: ['Wirtschaft', 'Vollmachten', 'Organisation'] },
  { year: 2024, season: 'Sommer', questionNumber: 'Extra', category: 'Organisation', question: `Nennen und beschreiben Sie die 4 Organisationsformen (Organigramm-Typen).`, solution: `1. Einlinienorganisation (Einliniensystem): Jede Stelle hat genau EINEN vorgesetzten. Klare Befehlskette, einfach, aber langsam (langer Dienstweg).\n\n2. Mehrlinienorganisation (Stab-Liniensystem? Nein – Mehrlinien): Mehrere Vorgesetzte können Weisungen erteilen. Spezialisierung möglich, aber Kompetenzkonflikte möglich.\n\n3. Stablinienorganisation: Einliniensystem mit Stäben (Experten ohne Weisungsbefugnis, z.B. Rechtsabteilung, Controlling). Beratende Funktion.\n\n4. Matrixorganisation: Mitarbeiter haben 2 Vorgesetzte (z.B. Abteilungsleiter + Projektleiter). Sehr flexibel für Projekte, aber hoher Koordinationsaufwand.`, keywords: ['Einlinien', 'Mehrlinien', 'Stablinie', 'Matrix', 'Weisungsbefugnis', 'Vorgesetzte'], topics: ['Wirtschaft', 'Organisation'] },
  { year: 2024, season: 'Sommer', questionNumber: 'Extra', category: 'Netzwerk', question: `Was ist NAT (Network Address Translation) und warum wird es benötigt?`, solution: `NAT übersetzt private IP-Adressen (z.B. 192.168.1.x) in eine öffentliche IP-Adresse und umgekehrt.\n\nProblem ohne NAT: Private IP-Adressen sind im Internet nicht routbar. Ein Client mit IP 192.168.1.10 kann keine direkte Verbindung zum Internet aufbauen, da Pakete mit dieser Absenderadresse von Internet-Routern verworfen werden.\n\nLösung: Der Router (Gateway) ersetzt die private Quell-IP durch seine öffentliche IP. Antwortpakete kommen an der öffentlichen IP an und werden vom Router an den richtigen internen Client weitergeleitet.\n\nVorteil: Spart IPv4-Adressen, erhöht Sicherheit (interne IPs von außen unsichtbar).`, keywords: ['private', 'öffentlich', 'Router', 'Gateway', 'Adresse', 'nicht routbar', 'übersetzt'], topics: ['Netzwerk', 'NAT'] },
  { year: 2024, season: 'Sommer', questionNumber: 'Extra', category: 'Netzwerk', question: `Erläutern Sie die beiden IPv6-Adresstypen Link-Local und Global Unicast – wo gelten sie und wofür werden sie verwendet?`, solution: `1. Link-Local-Adresse (beginnt immer mit fe80::):\n– Gilt nur im lokalen Netzsegment (direkt verbundene Geräte)\n– Wird automatisch konfiguriert (SLAAC)\n– Wird für lokale Kommunikation und Router Discovery verwendet\n– Nicht ins Internet routbar\n\n2. Global Unicast-Adresse (beginnt mit 2000:: bis 3fff::):\n– Weltweit eindeutig, vergleichbar mit öffentlicher IPv4-Adresse\n– Gilt global – Kommunikation auch außerhalb des LANs / ins Internet möglich\n– Wird vom ISP oder manuell vergeben`, keywords: ['fe80', 'Link-Local', 'Global Unicast', 'lokal', 'weltweit', 'routbar', 'SLAAC'], topics: ['Netzwerk', 'IPv6'] },

]

const categories = ['Alle', 'Netzwerk', 'IT-Sicherheit', 'SQL', 'Datenbanken', 'Kalkulation', 'Beschaffung', 'Organisation', 'Datenschutz', 'Programmierung', 'Service Mgmt', 'VLAN', 'Vollmachten', 'IPv6']

const activeCategory = ref('Alle')
const activeYear = ref(0)
const currentIdx = ref(0)
const userAnswer = ref('')
const showSolution = ref(false)
const answered = reactive<Record<number, boolean>>({})
const scores = reactive<Record<number, number>>({})

const filteredQuestions = computed(() => {
  return questions.filter((q, i) => {
    const catMatch = activeCategory.value === 'Alle' || q.category === activeCategory.value
    const yearMatch = activeYear.value === 0 || q.year === activeYear.value
    return catMatch && yearMatch
  })
})

const current = computed(() => filteredQuestions.value[currentIdx.value])
const answeredCount = computed(() => filteredQuestions.value.filter((q, i) => answered[globalIndex(i)]).length)

function globalIndex(filtIdx: number): number {
  const q = filteredQuestions.value[filtIdx]
  return questions.indexOf(q)
}

function countByCategory(cat: string): number {
  return questions.filter(q => q.category === cat && (activeYear.value === 0 || q.year === activeYear.value)).length
}

function setCategory(cat: string) {
  activeCategory.value = cat
  currentIdx.value = 0
  userAnswer.value = ''
  showSolution.value = false
}

function setYear(y: number) {
  activeYear.value = y
  currentIdx.value = 0
  userAnswer.value = ''
  showSolution.value = false
}

function goTo(idx: number) {
  currentIdx.value = idx
  userAnswer.value = answered[globalIndex(idx)] ? '' : ''
  showSolution.value = false
}

function submitAnswer() {
  if (!userAnswer.value.trim()) return
  const q = current.value
  const lower = userAnswer.value.toLowerCase()
  let found = 0
  if (q.keywords.length > 0) {
    q.keywords.forEach(kw => { if (lower.includes(kw.toLowerCase())) found++ })
    const pct = found / q.keywords.length
    let pts = 0
    if (pct >= 0.9) pts = 10
    else if (pct >= 0.75) pts = 8
    else if (pct >= 0.6) pts = 6
    else if (pct >= 0.4) pts = 4
    else if (pct >= 0.2) pts = 2
    scores[globalIndex(currentIdx.value)] = pts
  } else {
    scores[globalIndex(currentIdx.value)] = 5
  }
  answered[globalIndex(currentIdx.value)] = true
  emit('score', scores[globalIndex(currentIdx.value)])
}

function nextQuestion() {
  if (currentIdx.value < filteredQuestions.value.length - 1) {
    currentIdx.value++
    userAnswer.value = ''
    showSolution.value = false
  }
}
</script>

<style scoped>
.ft-wrap { max-width: 860px; }

.ft-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 14px; gap: 12px;
}
.ft-title { font-size: 20px; font-weight: 800; color: var(--color-text-primary); margin: 0 0 4px; }
.ft-sub { font-size: 13px; color: var(--color-text-secondary); margin: 0; }

/* Filters */
.ft-filters { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.ft-filter-btn {
  padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;
  border: 1px solid var(--color-border); background: var(--color-surface);
  color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
}
.ft-filter-btn:hover { border-color: #6366f1; color: #a5b4fc; }
.ft-filter-active { background: rgba(99,102,241,0.15) !important; border-color: #6366f1 !important; color: #a5b4fc !important; }

.ft-year-filters { display: flex; gap: 6px; margin-bottom: 10px; }
.ft-year-btn {
  padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700;
  border: 1px solid var(--color-border); background: var(--color-surface);
  color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
}
.ft-year-active { background: rgba(99,102,241,0.15) !important; border-color: #6366f1 !important; color: #a5b4fc !important; }

/* Navigation */
.ft-nav { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 8px; }
.ft-nav-btn {
  width: 28px; height: 28px; border-radius: 6px; font-size: 11px; font-weight: 700;
  border: 1.5px solid var(--color-border); background: var(--color-surface);
  color: var(--color-text-secondary); cursor: pointer; transition: all 0.15s;
  display: flex; align-items: center; justify-content: center;
}
.ft-nav-btn:hover { border-color: #6366f1; color: #a5b4fc; }
.ft-nav-active { background: #6366f1 !important; border-color: #6366f1 !important; color: white !important; }
.ft-nav-done { background: rgba(34,197,94,0.15) !important; border-color: #22c55e !important; color: #4ade80 !important; }

.ft-progress-bar { height: 4px; background: var(--color-border); border-radius: 2px; margin-bottom: 4px; }
.ft-progress-fill { height: 100%; background: linear-gradient(90deg, #22c55e, #4ade80); border-radius: 2px; transition: width 0.3s; }
.ft-progress-label { font-size: 11px; color: var(--color-text-secondary); margin-bottom: 14px; font-family: monospace; }

.ft-scenario {
  background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.3);
  border-radius: 10px; padding: 10px 14px; margin-bottom: 10px;
}
.ft-scenario-badge { font-size: 12px; font-weight: 700; color: #a5b4fc; display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.ft-topic-tag { padding: 1px 8px; background: rgba(99,102,241,0.2); border-radius: 10px; font-size: 11px; color: #c4b5fd; }

.ft-question {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: 10px; padding: 14px; margin-bottom: 12px;
}
.ft-question-label { font-size: 11px; font-weight: 700; color: var(--color-text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.ft-question-text { font-size: 14px; color: var(--color-text-primary); white-space: pre-wrap; line-height: 1.6; font-weight: 500; }

.ft-textarea {
  width: 100%; padding: 14px; border: 2px solid var(--color-border); border-radius: 10px;
  background: var(--color-surface); color: var(--color-text-primary); font-size: 14px;
  font-family: inherit; line-height: 1.6; outline: none; resize: vertical;
  transition: border-color 0.15s; box-sizing: border-box;
}
.ft-textarea:focus { border-color: #6366f1; }
.ft-textarea:disabled { opacity: 0.7; }

.ft-actions { display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }
.ft-btn-check { padding: 9px 20px; background: #16a34a; color: white; border: none; border-radius: 8px; font-weight: 700; font-size: 14px; cursor: pointer; }
.ft-btn-check:hover:not(:disabled) { background: #15803d; }
.ft-btn-check:disabled { opacity: 0.4; cursor: not-allowed; }
.ft-btn-solution { padding: 9px 20px; background: rgba(99,102,241,0.15); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.4); border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; }
.ft-btn-solution:hover { background: rgba(99,102,241,0.25); }
.ft-btn-next { padding: 9px 20px; background: var(--color-surface); color: var(--color-text-secondary); border: 1px solid var(--color-border); border-radius: 8px; font-weight: 600; font-size: 14px; cursor: pointer; margin-left: auto; }
.ft-btn-next:hover { border-color: #6366f1; color: #a5b4fc; }

.ft-feedback { border-radius: 10px; padding: 14px; margin-bottom: 12px; border: 1.5px solid; }
.ft-fb-good { background: rgba(34,197,94,0.08); border-color: #22c55e; }
.ft-fb-ok { background: rgba(234,179,8,0.08); border-color: #ca8a04; }
.ft-fb-bad { background: rgba(239,68,68,0.08); border-color: #dc2626; }
.ft-fb-score { font-size: 16px; font-weight: 800; color: var(--color-text-primary); margin-bottom: 4px; }
.ft-fb-msg { font-size: 13px; color: var(--color-text-secondary); margin-bottom: 10px; }
.ft-keywords { display: flex; flex-wrap: wrap; gap: 6px; }
.ft-kw { padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; border: 1px solid; }
.ft-kw-hit { background: rgba(34,197,94,0.15); border-color: #22c55e; color: #4ade80; }
.ft-kw-miss { background: rgba(239,68,68,0.1); border-color: #dc2626; color: #f87171; }

.ft-solution { background: rgba(34,197,94,0.06); border: 1.5px solid #22c55e; border-radius: 10px; padding: 14px; }
.ft-solution-label { font-size: 12px; font-weight: 700; color: #4ade80; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
.ft-solution-text { font-size: 14px; color: var(--color-text-primary); white-space: pre-wrap; line-height: 1.6; }

.slide-enter-active, .slide-leave-active { transition: all 0.25s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
