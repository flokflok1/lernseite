<template>
  <div class="fb">
    <!-- Category tabs -->
    <div class="fb-cats">
      <button v-for="cat in categories" :key="cat.id" class="fb-cat-btn"
        :class="activeCat === cat.id ? 'fb-cat-on' : ''"
        @click="activeCat = cat.id; resetDeck()">
        {{ cat.icon }} {{ cat.label }}
        <span class="fb-cat-count">{{ catProgress(cat.id) }}</span>
      </button>
    </div>

    <!-- Browse / Select toggle -->
    <div class="fb-browse-row">
      <button class="fb-btn fb-btn-browse" @click="browseMode = !browseMode">
        {{ browseMode ? '▲ Auswahl ausblenden' : '📋 Karten auswählen' }}
      </button>
      <span class="fb-selected-info" v-if="selectedCards.size > 0 && !browseMode">
        {{ selectedCards.size }} Karten ausgewählt
      </span>
    </div>

    <!-- Browse panel -->
    <div v-if="browseMode" class="fb-browse-panel">
      <div class="fb-browse-actions">
        <button class="fb-quick-btn" @click="selectAll">Alle</button>
        <button class="fb-quick-btn" @click="selectNone">Keine</button>
        <button class="fb-quick-btn" @click="selectRandom(5)">5 zufällig</button>
        <button class="fb-quick-btn" @click="selectRandom(10)">10 zufällig</button>
        <button class="fb-quick-btn" v-if="weakSet.size > 0" @click="selectWeakOnly">Nur schwache</button>
      </div>
      <!-- Tag filter -->
      <div class="fb-tag-filter" v-if="availableTags.length > 1">
        <button v-for="t in availableTags" :key="t" class="fb-tag-pill"
          :class="{ 'fb-tag-on': !tagFilter || tagFilter === t }"
          @click="tagFilter = tagFilter === t ? null : t">
          {{ t }}
        </button>
      </div>
      <div class="fb-browse-list">
        <label v-for="(card, i) in browsableCards" :key="i" class="fb-browse-item"
          :class="{ 'fb-browse-selected': selectedCards.has(card.idx) }">
          <input type="checkbox" :checked="selectedCards.has(card.idx)" @change="toggleCard(card.idx)" />
          <span class="fb-browse-tag">{{ card.tag }}</span>
          <span class="fb-browse-q">{{ card.q }}</span>
        </label>
      </div>
      <button class="fb-btn fb-btn-start" @click="startSelected()" :disabled="selectedCards.size === 0">
        ▶ {{ selectedCards.size }} Karten üben
      </button>
    </div>

    <!-- Progress bar + shuffle toggle -->
    <div class="fb-progress-row" v-if="!browseMode">
      <div class="fb-progress">
        <div class="fb-progress-bar" :style="{width: progressPct + '%'}"></div>
        <span class="fb-progress-txt">Karte {{ cardIdx + 1 }}/{{ deck.length }} · Runde {{ roundCount + 1 }}</span>
      </div>
      <button class="fb-shuffle-btn" :class="{ 'fb-shuffle-on': shuffleOn }" @click="toggleShuffle" title="Mischen an/aus">
        🔀
      </button>
    </div>

    <!-- Stats bar -->
    <div class="fb-stats-row" v-if="statsTotal > 0 && !browseMode">
      <span class="fb-stat fb-stat-green">🟢 {{ statsGreen }}</span>
      <span class="fb-stat fb-stat-yellow">🟡 {{ statsYellow }}</span>
      <span class="fb-stat fb-stat-red">🔴 {{ statsRed }}</span>
      <span class="fb-stat fb-stat-total">· {{ statsTotal }} beantwortet</span>
    </div>

    <!-- Card -->
    <div v-if="currentCard && !browseMode" class="fb-card">
      <div class="fb-card-cat">{{ currentCatLabel }} <span v-if="currentCard.tag" class="fb-card-tag">· {{ currentCard.tag }}</span></div>
      <div class="fb-card-q">{{ currentCard.q }} <span v-if="currentCard.pts" class="fb-card-pts">{{ currentCard.pts }} Pkt</span></div>

      <!-- Write answer BEFORE seeing solution -->
      <div v-if="!revealed" class="fb-write-area">
        <textarea
          ref="answerInput"
          v-model="userAnswer"
          class="fb-textarea"
          placeholder="Schreib deine Antwort hier..."
          rows="3"
          @keydown.ctrl.enter="reveal()"
        ></textarea>
        <div class="fb-write-btns">
          <button class="fb-btn fb-btn-reveal" @click="reveal()" :disabled="!userAnswer.trim()">
            🔍 Lösung vergleichen
          </button>
          <button class="fb-btn fb-btn-skip" @click="skipCard">⏭ Skip</button>
        </div>
      </div>

      <!-- After reveal: show comparison with AI feedback -->
      <div v-else class="fb-compare">
        <!-- AI Verdict banner -->
        <div v-if="aiGrading" class="fb-verdict fb-verdict-loading">
          <span class="fb-verdict-icon">🤖</span>
          <span class="fb-verdict-txt">Lumi bewertet...</span>
        </div>
        <div v-else-if="aiResult" class="fb-verdict" :class="aiVerdictClass">
          <span class="fb-verdict-icon">{{ aiResult.pct >= 80 ? '🟢' : aiResult.pct >= 50 ? '🟡' : aiResult.pct >= 25 ? '🟠' : '🔴' }}</span>
          <span class="fb-verdict-txt">{{ aiResult.pct >= 80 ? 'Sehr gut!' : aiResult.pct >= 50 ? 'Fast richtig!' : aiResult.pct >= 25 ? 'Ansatz da...' : 'Nochmal lernen!' }}</span>
          <span class="fb-verdict-pts" v-if="currentCard.pts">~{{ Math.round(currentCard.pts * aiResult.pct / 100) }}/{{ currentCard.pts }} Pkt</span>
          <span class="fb-verdict-pct">{{ aiResult.pct }}%</span>
        </div>
        <!-- AI Feedback -->
        <div v-if="aiResult && aiResult.feedback" class="fb-ai-feedback">
          🤖 {{ aiResult.feedback }}
        </div>
        <div class="fb-your-answer">
          <div class="fb-compare-label">Deine Antwort:</div>
          <div class="fb-compare-text fb-compare-user">{{ userAnswer }}</div>
        </div>
        <div class="fb-correct-answer">
          <div class="fb-compare-label">Musterlösung:</div>
          <div class="fb-compare-text fb-compare-correct">{{ currentCard.a }}</div>
        </div>
        <div v-if="currentCard.detail" class="fb-card-detail">💡 {{ currentCard.detail }}</div>
        <div class="fb-card-btns">
          <button class="fb-btn fb-btn-next" @click="nextCardAuto">→ Nächste Karte</button>
          <button class="fb-btn fb-btn-stop" @click="stopLoop" v-if="roundPos > 0">⏹ Stopp</button>
        </div>
      </div>
    </div>

    <!-- Done state -->
    <div v-else-if="deckDone && !browseMode" class="fb-done">
      <div class="fb-done-icon">🎉</div>
      <div class="fb-done-txt">{{ deck.length }} Karten durch!</div>
      <div class="fb-done-pts" v-if="totalMaxPts > 0">
        ~{{ totalEarnedPts }}/{{ totalMaxPts }} Punkte ({{ Math.round(totalEarnedPts / totalMaxPts * 100) }}%)
      </div>
      <div class="fb-done-weak" v-if="weakCards.length">{{ weakCards.length }} Karten waren unter 50% — kommen nochmal</div>
      <button class="fb-btn fb-btn-restart" @click="resetDeck()">🔁 Nochmal üben</button>
      <button class="fb-btn fb-btn-weak" @click="browseMode = true; deckDone = false">📋 Neue Auswahl</button>
      <button v-if="weakCards.length" class="fb-btn fb-btn-weak" @click="resetWeak()">🎯 Nur schwache Karten</button>
    </div>

    <!-- Lumi Tutor -->
    <div class="fb-tutor-wrap">
      <button class="fb-tutor-toggle" @click="showTutor = !showTutor">
        🤖 {{ showTutor ? 'Lumi ausblenden ▲' : 'Lumi fragen ▼' }}
      </button>
      <div v-if="showTutor" class="fb-tutor-panel">
        <div ref="tutorContainer" class="fb-tutor-msgs">
          <div v-if="tutorMessages.length === 0" class="fb-tutor-empty">
            Frag mich zu jedem Fachbegriff — ich erklär dir das! 🤖
          </div>
          <div v-for="(m, i) in tutorMessages" :key="i" class="fb-tutor-msg" :class="m.role === 'user' ? 'fb-tm-user' : 'fb-tm-bot'">{{ m.content }}</div>
          <div v-if="tutorLoading" class="fb-tutor-msg fb-tm-bot">Lumi denkt nach…</div>
        </div>
        <div class="fb-tutor-input-row">
          <button class="fb-tutor-ctx" @click="askAboutCard" :disabled="tutorLoading || !currentCard">❓ Zur Karte</button>
          <input v-model="tutorInput" class="fb-tutor-inp" placeholder="Frag Lumi..." @keydown.enter="askTutor()" :disabled="tutorLoading" />
          <button class="fb-tutor-send" @click="askTutor()" :disabled="tutorLoading || !tutorInput.trim()">→</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { tutorChat } from '@/infrastructure/api/clients/public/learning/tutor/tutor.api'

const emit = defineEmits(['score'])

// ─── FLASHCARD DATA (extracted from real AP1 exams 2022-2026) ───

const cards = [
  // ══════ IT-SICHERHEIT (94 Punkte in Prüfungen) ══════
  { cat: 'sec', tag: 'Schutzziele', pts: 6, q: 'Nenne die 3 Schutzziele der Informationssicherheit (CIA) und erkläre sie jeweils in einem Satz', a: 'Vertraulichkeit: Daten sind nur für befugte Personen zugänglich. Integrität: Daten sind vollständig, korrekt und unverändert. Verfügbarkeit: Systeme und Daten sind für Berechtigte nutzbar, wenn benötigt.', detail: 'Kommt in JEDER Prüfung. Immer alle 3 nennen + kurz erklären können.' },
  { cat: 'sec', tag: 'Schutzbedarf', pts: 3, q: 'Nenne die 3 Schutzbedarfskategorien', a: 'Normal, Hoch, Sehr hoch', detail: 'Je nach möglichem Schaden für das Unternehmen' },
  { cat: 'sec', tag: 'Schutzbedarf', pts: 5, q: 'Was ist das Maximumprinzip (Schutzbedarfsanalyse)?', a: 'Der höchste Schutzbedarf aller Anwendungen bestimmt den Gesamtschutzbedarf des IT-Systems', detail: 'Kam in FISI Sommer 2023 dran!' },
  { cat: 'sec', tag: 'Schutzbedarf', pts: 5, q: 'Was ist der Kumulationseffekt?', a: 'Schutzbedarf ist höher als einzelne Apps, wenn viele normal-eingestufte Apps auf einem System laufen', detail: 'Viele "kleine" Apps zusammen = hohes Risiko bei Ausfall' },
  { cat: 'sec', tag: 'Firewall', pts: 4, q: 'Was ist Paketfilterung (Firewall)?', a: 'Prüft Pakete anhand von IP-Adresse, Port und Protokoll (Layer 3+4 im OSI-Modell)', detail: 'Einfachste Firewall-Funktion — nur Header werden geprüft' },
  { cat: 'sec', tag: 'Firewall', pts: 4, q: 'Was ist Stateful Packet Inspection (SPI)?', a: 'Verfolgt Verbindungszustände — lässt nur Antworten auf selbst initiierte Verbindungen durch', detail: 'Führt eine State Table mit aktiven Verbindungen' },
  { cat: 'sec', tag: 'Firewall', pts: 4, q: 'Was ist ein Application Layer Gateway / Deep Packet Inspection?', a: 'Proxy auf Layer 7 — prüft den Inhalt des Datenstroms, nicht nur Header', detail: 'Kann Schadcode, Protokollverletzungen und unerwünschte Inhalte erkennen' },
  { cat: 'sec', tag: 'Firewall', pts: 6, q: 'Einstufiges vs. zweistufiges Firewall-Konzept?', a: 'Einstufig: EINE Firewall zwischen Internet und LAN. Zweistufig: ZWEI Firewalls mit DMZ dazwischen', detail: 'Zweistufig = Defense in Depth. Kam in Winter 2023 dran!' },
  { cat: 'sec', tag: 'Firewall', pts: 4, q: 'Was ist eine DMZ?', a: 'Demilitarisierte Zone — Netzwerksegment zwischen Internet und internem Netz für öffentlich erreichbare Server', detail: 'Z.B. Webserver, Mailserver stehen in der DMZ' },
  { cat: 'sec', tag: 'VPN', pts: 6, q: 'Was ist ein VPN? Nenne 3 Sicherheitsaspekte', a: 'Virtual Private Network — verschlüsselter Tunnel über öffentliches Netz. Aspekte: Authentizität, Integrität, Vertraulichkeit', detail: 'Authentizität=Identitätsprüfung, Integrität=Daten unverändert, Vertraulichkeit=verschlüsselt' },
  { cat: 'sec', tag: 'VPN', pts: 4, q: 'Client-to-Site VPN vs. Site-to-Site VPN?', a: 'Client-to-Site: einzelner User → Firmennetz (Homeoffice). Site-to-Site: zwei Standorte dauerhaft verbunden', detail: 'Kam in Winter 2023 dran: "Nennen Sie die VPN-Art"' },
  { cat: 'sec', tag: 'Angriffe', pts: 6, q: 'Nenne 5 Maßnahmen gegen Ransomware', a: '1. E-Mail-Anhänge prüfen 2. Updates installieren 3. MFA nutzen 4. Backups (offline!) 5. Verdacht sofort melden', detail: 'Kam in FISI Winter 2022 als 6-Punkte-Frage!' },
  { cat: 'sec', tag: 'WLAN', pts: 8, q: '4 WLAN-Sicherheitsmaßnahmen?', a: '1. WPA3 nutzen 2. Starkes Passwort/RADIUS 3. VLAN-Segmentierung 4. Standard-Admin-Passwort ändern', detail: 'Kam in FISI Winter 2022 als 8-Punkte-Frage!' },
  { cat: 'sec', tag: 'TOM', pts: 6, q: 'Was sind technische vs. organisatorische Maßnahmen (TOM)?', a: 'Technisch: Firewall, Verschlüsselung, Backup. Organisatorisch: Schulungen, Richtlinien, Zugangskontrollen', detail: 'DSGVO verlangt TOMs zum Schutz personenbezogener Daten' },

  // ══════ DATENBANKEN (68 Punkte in Prüfungen) ══════
  { cat: 'db', tag: 'ERM', pts: 6, q: 'Was ist ein ERM?', a: 'Entity-Relationship-Modell — grafische Darstellung von Entitäten (Rechtecke), Beziehungen (Rauten) und Attributen (Ovale)', detail: 'Chen-Notation in der Prüfung! Kam fast jede Prüfung ab 2022' },
  { cat: 'db', tag: 'ERM', pts: 3, q: 'Was sind Kardinalitäten? Nenne die 3 Typen', a: '1:1 (eins-zu-eins), 1:n (eins-zu-viele), m:n (viele-zu-viele)', detail: 'Beschreiben wieviele Entitäten einer Beziehung zugeordnet werden' },
  { cat: 'db', tag: 'Relationen', pts: 4, q: 'Wie wird eine 1:n Beziehung im Relationenmodell abgebildet?', a: 'Primärschlüssel der 1-Seite wird als Fremdschlüssel in die n-Seite aufgenommen', detail: 'Z.B. KundenID → in Tabelle Bestellung als FK' },
  { cat: 'db', tag: 'Relationen', pts: 4, q: 'Wie wird eine m:n Beziehung abgebildet?', a: 'Eigene Verknüpfungstabelle mit den Primärschlüsseln beider Seiten als Fremdschlüssel', detail: 'Z.B. Mitarbeiter_Projekt(Mitarbeiter_ID, Projekt_ID)' },
  { cat: 'db', tag: 'Schlüssel', pts: 3, q: 'Was ist ein Primärschlüssel?', a: 'Eindeutiger Identifikator eines Datensatzes — UNIQUE + NOT NULL', detail: 'Kann natürlich (z.B. ISBN) oder künstlich/Surrogat (z.B. Auto-ID) sein' },
  { cat: 'db', tag: 'Schlüssel', pts: 4, q: 'Was ist ein Fremdschlüssel?', a: 'Attribut das auf den Primärschlüssel einer anderen Tabelle verweist — stellt referenzielle Integrität sicher', detail: 'FK-Constraint verhindert Waisendatensätze' },
  { cat: 'db', tag: 'Normalformen', pts: 3, q: '1. Normalform (1NF)?', a: 'Alle Attribute sind atomar — keine mehrfachen Werte in einer Zelle', detail: 'Falsch: "Meier, Müller" in einem Feld. Richtig: Eigene Zeilen!' },
  { cat: 'db', tag: 'Normalformen', pts: 4, q: '2. Normalform (2NF)?', a: '1NF + jedes Nicht-Schlüsselattribut ist voll funktional abhängig vom GESAMTEN Primärschlüssel', detail: 'Nur relevant bei zusammengesetztem PK! Partielle Abhängigkeit auflösen' },
  { cat: 'db', tag: 'Normalformen', pts: 5, q: '3. Normalform (3NF)?', a: '2NF + keine transitiven Abhängigkeiten — kein Nicht-Schlüssel hängt von anderem Nicht-Schlüssel ab', detail: 'Z.B. PLZ→Ort ist transitiv! Eigene Tabelle machen' },
  { cat: 'db', tag: 'Anomalien', pts: 3, q: 'Einfüge-Anomalie?', a: 'Daten können nicht eingefügt werden, weil ein Teil des Schlüssels fehlt', detail: 'Z.B. Neuer Hersteller ohne Produkt nicht eintragbar' },
  { cat: 'db', tag: 'Anomalien', pts: 3, q: 'Änderungs-Anomalie?', a: 'Redundante Daten werden nicht überall geändert → Inkonsistenz', detail: 'Z.B. Adresse an 50 Stellen gespeichert, nur 49 aktualisiert' },
  { cat: 'db', tag: 'Anomalien', pts: 3, q: 'Lösch-Anomalie?', a: 'Beim Löschen eines Datensatzes gehen ungewollt andere Informationen verloren', detail: 'Z.B. Letzter Auftrag gelöscht → Technikerdaten auch weg' },
  { cat: 'db', tag: 'DBMS', pts: 4, q: '2 Vorteile DBMS gegenüber CSV?', a: '1. Effiziente Abfragen durch Indizes 2. ACID-Prinzip + Mehrbenutzerfähigkeit', detail: 'Kam in Winter 2023! CSV hat kein Locking, keine Constraints' },
  { cat: 'db', tag: 'DBMS', pts: 4, q: 'Wofür steht ACID?', a: 'Atomicity (ganz oder gar nicht), Consistency (konsistenter Zustand), Isolation (Transaktionen unabhängig), Durability (dauerhaft gespeichert)', detail: 'Garantiert Datenkonsistenz bei Mehrbenutzerzugriff' },
  { cat: 'db', tag: 'SQL', pts: 5, q: 'Was passiert bei INSERT mit bereits vorhandenem Primärschlüssel?', a: 'Fehler! Verletzung des Primary-Key-Constraints — PK muss UNIQUE sein', detail: 'Kam in FISI Winter 2022 als 5-Punkte-Frage!' },
  { cat: 'db', tag: 'Relationen', pts: 4, q: 'Relationenschreibweise — wie kennzeichnet man PK und FK?', a: 'Primärschlüssel: unterstrichen. Fremdschlüssel: mit Pfeil ↑ oder kursiv/gestrichelt', detail: 'Mitarbeiter(M_ID, Name, Abt_ID↑). Notation aus Aufgabe beachten!' },

  // ══════ WIRTSCHAFT & ORGA (77 Punkte in Prüfungen) ══════
  { cat: 'wirt', tag: 'Beschaffung', pts: 4, q: 'Nenne je 2 interne und externe Bezugsquellen', a: 'Intern: Lieferantenkartei, Bestandslisten. Extern: Internet, Messen, Fachzeitschriften, Branchenverzeichnisse', detail: 'Kam in FISI Sommer 2024! Genau 4 nennen' },
  { cat: 'wirt', tag: 'Beschaffung', pts: 8, q: '4 Schritte der Wareneingangsprüfung?', a: '1. Lieferschein prüfen 2. Menge kontrollieren (quantitativ) 3. Qualität prüfen (qualitativ) 4. Mängel dokumentieren', detail: 'Kam als 8-Punkte-Frage in FISI Sommer 2024!' },
  { cat: 'wirt', tag: 'Organisation', pts: 4, q: 'Was ist eine Einlinienorganisation?', a: 'Jeder Mitarbeiter hat genau EINEN Vorgesetzten — klare Hierarchie, aber langer Dienstweg', detail: 'Vorteil: Klare Zuständigkeit. Nachteil: Langsame Kommunikation' },
  { cat: 'wirt', tag: 'Organisation', pts: 4, q: 'Was ist eine Mehrlinienorganisation?', a: 'Mitarbeiter hat mehrere fachliche Vorgesetzte — kurze Wege, aber mögliche Kompetenzkonfikte', detail: 'Vorteil: Spezialisierung. Nachteil: Widersprüchliche Anweisungen' },
  { cat: 'wirt', tag: 'Organisation', pts: 4, q: 'Was ist eine Stablinienorganisation?', a: 'Einlinienorganisation + Stabsstellen die beraten, aber KEINE Weisungsbefugnis haben', detail: 'Stäbe: z.B. Rechtsabteilung, IT-Security-Berater' },
  { cat: 'wirt', tag: 'Organisation', pts: 5, q: 'Was ist eine Matrixorganisation?', a: 'Kombination aus Funktions- und Spartenorganisation — flexibel aber komplex, Mitarbeiter hat 2 Vorgesetzte', detail: 'Kam in FISI Sommer 2023 — "Benennen und beschreiben Sie"' },
  { cat: 'wirt', tag: 'Angebotsvergleich', pts: 6, q: 'Quantitative vs. qualitative Angebotsvergleich?', a: 'Quantitativ: nur Preis/Kosten vergleichen. Qualitativ: auch Lieferzeit, Service, Qualität bewerten (Nutzwertanalyse)', detail: 'Bei Nutzwertanalyse: Kriterien gewichten, Punkte vergeben, multiplizieren' },
  { cat: 'wirt', tag: 'SLA', pts: 4, q: 'Was ist ein SLA?', a: 'Service Level Agreement — vertragliche Vereinbarung über Qualität und Umfang einer Dienstleistung', detail: 'Definiert z.B. Verfügbarkeit (99,9%), Reaktionszeiten, Penalties' },

  // ══════ NETZWERK EXTRAS (wichtige Fachbegriffe) ══════
  { cat: 'netz', tag: 'OSI', pts: 7, q: 'Nenne die 7 OSI-Schichten (von unten nach oben)', a: '1.Physical 2.Data Link 3.Network 4.Transport 5.Session 6.Presentation 7.Application', detail: 'Merkhilfe: "Please Do Not Throw Sausage Pizza Away"' },
  { cat: 'netz', tag: 'Protokolle', pts: 4, q: 'Was ist NAT?', a: 'Network Address Translation — übersetzt private IP-Adressen in öffentliche für Internetzugang', detail: 'Router ersetzt interne IP durch seine öffentliche IP' },
  { cat: 'netz', tag: 'Protokolle', pts: 3, q: 'Was ist DNS?', a: 'Domain Name System — löst Domainnamen (z.B. google.de) in IP-Adressen auf', detail: 'Wie ein "Telefonbuch" des Internets' },
  { cat: 'netz', tag: 'Protokolle', pts: 4, q: 'Was ist DHCP?', a: 'Dynamic Host Configuration Protocol — vergibt automatisch IP-Adressen an Geräte im Netzwerk', detail: 'Vergibt: IP, Subnetzmaske, Gateway, DNS-Server' },
  { cat: 'netz', tag: 'Segmentierung', pts: 4, q: 'Was ist ein VLAN?', a: 'Virtual Local Area Network — logische Trennung eines physischen Netzwerks in mehrere Segmente', detail: 'Trennt z.B. Gast-WLAN vom Firmennetz auf demselben Switch' },
  { cat: 'netz', tag: 'Adressierung', pts: 3, q: 'Private IPv4-Bereiche?', a: '10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16', detail: 'Werden im Internet NICHT geroutet!' },
  { cat: 'netz', tag: 'Adressierung', pts: 4, q: 'Was ist eine MAC-Adresse?', a: '48-Bit Hardware-Adresse der Netzwerkkarte — weltweit eindeutig, Layer 2', detail: 'Format: AA:BB:CC:DD:EE:FF. Erste 3 Bytes = Hersteller (OUI)' },
  { cat: 'netz', tag: 'Geräte', pts: 4, q: 'Was macht ein Switch vs. Router?', a: 'Switch: verbindet Geräte im LAN (Layer 2, MAC). Router: verbindet Netzwerke (Layer 3, IP)', detail: 'Switch = lokal, Router = zwischen Netzen' },

  // ══════ PROJEKTMANAGEMENT & EXTRAS ══════
  { cat: 'wirt', tag: 'Projektmanagement', pts: 5, q: 'Wofür steht SMART bei Projektzielen?', a: 'Spezifisch, Messbar, Attraktiv, Realistisch, Terminiert', detail: 'Jedes Projektziel muss alle 5 Kriterien erfüllen' },
  { cat: 'wirt', tag: 'Projektmanagement', pts: 4, q: 'Was ist der Unterschied zwischen Lastenheft und Pflichtenheft?', a: 'Lastenheft: WAS will der Kunde (Anforderungen). Pflichtenheft: WIE setzt der Auftragnehmer es um (Lösung)', detail: 'Lastenheft = Kunde erstellt. Pflichtenheft = Auftragnehmer erstellt' },
  { cat: 'wirt', tag: 'Projektmanagement', pts: 4, q: 'Wasserfall vs. agiles Projektmodell (Scrum)?', a: 'Wasserfall: feste Phasen nacheinander (Planung→Analyse→Entwurf→Umsetzung→Test→Einführung). Scrum: iterativ in kurzen Sprints mit Feedback', detail: 'Wasserfall = starr aber planbar. Scrum = flexibel, reagiert auf Änderungen' },
  { cat: 'sec', tag: 'Verschlüsselung', pts: 4, q: 'Symmetrische vs. asymmetrische Verschlüsselung?', a: 'Symmetrisch: EIN Schlüssel für Ver- und Entschlüsselung (z.B. AES). Asymmetrisch: Public Key + Private Key (z.B. RSA)', detail: 'Symmetrisch = schnell. Asymmetrisch = sicher für Schlüsseltausch' },
  { cat: 'wirt', tag: 'Qualitätsmanagement', pts: 4, q: 'Wofür steht PDCA?', a: 'Plan: planen, Do: durchführen, Check: prüfen, Act: verbessern — kontinuierlicher Verbesserungsprozess', detail: 'Auch Deming-Kreis genannt. Zyklus wiederholt sich immer wieder' },
  { cat: 'wirt', tag: 'Cloud', pts: 4, q: 'Was ist IaaS, PaaS und SaaS?', a: 'IaaS: Infrastruktur mieten (Server, Speicher). PaaS: Plattform zum Entwickeln (z.B. Heroku). SaaS: fertige Software nutzen (z.B. Office 365)', detail: 'Von unten nach oben: IaaS = Fundament, PaaS = Werkbank, SaaS = fertiges Produkt' },

  // ══════ FORMELN & RECHNEN ══════
  { cat: 'formel', tag: 'Bezugspreis', pts: 6, q: 'Wie berechnet man den Bezugspreis? Nenne die Schritte', a: 'Listenpreis − Rabatt = Zieleinkaufspreis − Skonto = Bareinkaufspreis + Bezugskosten (Lieferung, Verpackung) = Bezugspreis', detail: 'Kommt fast jede Prüfung beim Angebotsvergleich! Immer alle Schritte zeigen' },
  { cat: 'formel', tag: 'Bezugspreis', pts: 4, q: 'Wie berechnet man Rabatt und Skonto?', a: 'Rabatt: Listenpreis × Rabatt% = Rabattbetrag. Skonto: Zieleinkaufspreis × Skonto% = Skontobetrag. ACHTUNG: Skonto wird vom Zieleinkaufspreis berechnet, nicht vom Listenpreis!', detail: 'Häufiger Fehler: Skonto vom Listenpreis berechnen' },
  { cat: 'formel', tag: 'Stromkosten', pts: 4, q: 'Wie berechnet man die jährlichen Stromkosten eines Geräts?', a: 'Leistung (kW) × Betriebsstunden pro Tag × 365 Tage × Strompreis (€/kWh) = Jahreskosten', detail: 'Einheiten beachten: Watt → kW (÷1000). Beispiel: 500W Server, 24/7, 0.30€/kWh = 0.5 × 24 × 365 × 0.30 = 1.314€' },
  { cat: 'formel', tag: 'Zahlensysteme', pts: 4, q: 'Wie rechnet man Dezimal → Binär um?', a: 'Stellenwerte 128-64-32-16-8-4-2-1 durchgehen: Passt die Zahl rein? → 1, sonst → 0. Rest weiterrechnen. Beispiel: 42 = 32+8+2 = 00101010', detail: 'Oder: Zahl immer durch 2 teilen, Reste von unten nach oben lesen' },
  { cat: 'formel', tag: 'Zahlensysteme', pts: 4, q: 'Wie rechnet man Binär → Dezimal um?', a: 'Jede 1 mit ihrem Stellenwert multiplizieren und addieren. Stellenwerte von rechts: 1,2,4,8,16,32,64,128. Beispiel: 1010 = 8+0+2+0 = 10', detail: 'Merke die Reihe: 128, 64, 32, 16, 8, 4, 2, 1' },
  { cat: 'formel', tag: 'Zahlensysteme', pts: 4, q: 'Wie rechnet man Hexadezimal ↔ Binär um?', a: 'Jede Hex-Ziffer = 4 Bit. A=1010, B=1011, C=1100, D=1101, E=1110, F=1111. Beispiel: 0x2F = 0010 1111', detail: 'Hex → Binär: Jede Stelle einzeln in 4 Bit umwandeln. Binär → Hex: Von rechts in 4er-Gruppen teilen' },
  { cat: 'formel', tag: 'Speicher', pts: 3, q: 'Speichergrößen umrechnen: Bit, Byte, KB, MB, GB, TB', a: '8 Bit = 1 Byte. 1024 Byte = 1 KB. 1024 KB = 1 MB. 1024 MB = 1 GB. 1024 GB = 1 TB', detail: 'Faktor ist immer 1024 (= 2^10). Bei Festplattenherstellern oft 1000 statt 1024!' },
  { cat: 'formel', tag: 'Nutzwertanalyse', pts: 5, q: 'Wie führt man eine Nutzwertanalyse durch?', a: '1. Kriterien festlegen (z.B. Preis, Lieferzeit, Service) 2. Gewichtung vergeben (Summe = 100%) 3. Angebote bewerten (Punkte 1-10) 4. Gewichtung × Bewertung = Teilnutzwert 5. Summe aller Teilnutzwerte = Gesamtnutzwert → höchster gewinnt', detail: 'Wird oft als Tabelle in der Prüfung verlangt' },
  { cat: 'formel', tag: 'Netzwerk', pts: 4, q: 'Wie viele Hosts passen in ein Subnetz?', a: '2^Hostbits − 2 = nutzbare Hosts. Die 2 Abzüge sind: Netzadresse und Broadcast. Beispiel: /24 = 8 Hostbits → 2^8 − 2 = 254 Hosts', detail: '/25=126, /26=62, /27=30, /28=14, /29=6, /30=2' },
  { cat: 'formel', tag: 'Verfügbarkeit', pts: 3, q: 'Wie berechnet man die Verfügbarkeit in Prozent?', a: 'Verfügbarkeit = (Gesamtzeit − Ausfallzeit) ÷ Gesamtzeit × 100%. Beispiel: 8760h Jahr − 8.76h Ausfall = 99,9%', detail: '99,9% = max 8,76h Ausfall/Jahr. 99,99% = max 52 Min/Jahr' },
]

// ─── CATEGORIES ───

const categories = [
  { id: 'sec', icon: '🔒', label: 'IT-Sicherheit' },
  { id: 'db', icon: '🗄️', label: 'Datenbanken' },
  { id: 'wirt', icon: '💼', label: 'Wirtschaft & Orga' },
  { id: 'netz', icon: '🌐', label: 'Netzwerk' },
  { id: 'formel', icon: '📐', label: 'Formeln' },
  { id: 'all', icon: '🎲', label: 'Alle mischen' },
]

// ─── STATE ───

const activeCat = ref('sec')
const revealed = ref(false)
const userAnswer = ref('')
const answerInput = ref<HTMLTextAreaElement | null>(null)
const cardIdx = ref(0)
const known = ref<number[]>([])
const again = ref<number[]>([])
const weakSet = ref(new Set<number>())
const deckDone = ref(false)
const deck = ref<number[]>([])
const browseMode = ref(false)
const selectedCards = ref(new Set<number>())
const tagFilter = ref<string | null>(null)
const isCustomSelection = ref(false)
const totalEarnedPts = ref(0)
const totalMaxPts = ref(0)
const roundCount = ref(0)
const roundPos = ref(0)
const shuffleOn = ref(false)
const aiGrading = ref(false)
const aiResult = ref<{pct: number, feedback: string} | null>(null)

// ─── STATS ───
const statsGreen = ref(0)  // >= 80%
const statsYellow = ref(0) // 50-79%
const statsRed = ref(0)    // < 50%
const statsTotal = computed(() => statsGreen.value + statsYellow.value + statsRed.value)

// ─── TUTOR ───
const showTutor = ref(false)
const tutorMessages = ref<{role: string, content: string}[]>([])
const tutorInput = ref('')
const tutorLoading = ref(false)
const tutorContainer = ref<HTMLDivElement | null>(null)

const LUMI_PROMPT = `Du bist Lumi, ein Sokrates-Tutor für AP1-Fachbegriffe (Pascal, FISI BW). WICHTIG: Gib NIEMALS direkt die Antwort! Stelle eine gezielte Frage die Pascal selbst draufkommen lässt. Max 2-3 Sätze. Deutsch. Nutze Eselsbrücken wenn möglich.`

// ─── COMPUTED ───

const currentDeck = computed(() => {
  if (activeCat.value === 'all') return cards.map((_, i) => i)
  return cards.map((c, i) => ({ c, i })).filter(x => x.c.cat === activeCat.value).map(x => x.i)
})

const currentCard = computed(() => {
  if (deck.value.length === 0) return null
  return cards[deck.value[cardIdx.value]] || null
})

const currentCatLabel = computed(() => {
  return categories.find(c => c.id === activeCat.value)?.label || ''
})

const progressPct = computed(() => {
  if (deck.value.length === 0) return 0
  return Math.round((cardIdx.value + (revealed.value ? 1 : 0)) / deck.value.length * 100)
})

const weakCards = computed(() => [...weakSet.value])

// ─── KEYWORD MATCHING ───

function extractKeywords(answer: string): string[] {
  const stopwords = new Set(['der','die','das','ein','eine','und','oder','ist','sind','wird','werden','für','von','zu','auf','in','mit','an','des','dem','den','als','bei','nach','über','unter','aus','durch','um','vor','zur','zum','im','am','es','hat','kann','man','nur','auch','noch','wie','was','aber','nicht','kein','keine','einem','einer','eines','dass','diese','dieser','dieses','wenn','z.b.','bzw.','etc.','z.b','bzw','etc','alle','jeder','jede','jedes'])
  return answer
    .replace(/[()\/\-–—,;:!?.]+/g, ' ')
    .split(/\s+/)
    .map(w => w.toLowerCase().trim())
    .filter(w => w.length > 2 && !stopwords.has(w))
}

function fuzzyMatch(keyword: string, text: string): boolean {
  // Exact match
  if (text.includes(keyword)) return true
  // Umlaut alternatives
  const alt = keyword.replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue')
  if (alt !== keyword && text.includes(alt)) return true
  // Check if any word in text is similar (max 2 chars difference for words > 4 chars)
  const textWords = text.split(/\s+/)
  for (const tw of textWords) {
    if (tw.length < 3) continue
    // Starts-with match (handles plural/case endings like "anwendung" matching "anwendungen")
    if (keyword.length >= 4 && (tw.startsWith(keyword.slice(0, -1)) || keyword.startsWith(tw.slice(0, -1)))) return true
    // Contains match for compound words (e.g. "gesamtschutzbedarf" contains "schutzbedarf")
    if (tw.length > keyword.length && tw.includes(keyword)) return true
    if (keyword.length > tw.length && keyword.includes(tw) && tw.length >= 4) return true
    // Levenshtein for close typos
    if (Math.abs(tw.length - keyword.length) <= 2 && levenshtein(tw, keyword) <= 2) return true
  }
  return false
}

function levenshtein(a: string, b: string): number {
  const m = a.length, n = b.length
  const d: number[][] = Array.from({length: m + 1}, (_, i) => {
    const row = new Array(n + 1).fill(0)
    row[0] = i
    return row
  })
  for (let j = 1; j <= n; j++) d[0][j] = j
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      d[i][j] = Math.min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+(a[i-1]===b[j-1]?0:1))
  return d[m][n]
}

const keywordResult = computed(() => {
  if (!currentCard.value || !revealed.value) return { keywords: [], hits: 0, total: 0 }
  const correctKws = extractKeywords(currentCard.value.a)
  const unique = [...new Set(correctKws)]
  const userLower = userAnswer.value.toLowerCase()
  const keywords = unique.map(w => ({
    word: w,
    hit: fuzzyMatch(w, userLower)
  }))
  return {
    keywords,
    hits: keywords.filter(k => k.hit).length,
    total: keywords.length
  }
})

const matchPct = computed(() => {
  if (keywordResult.value.total === 0) return 0
  return Math.round(keywordResult.value.hits / keywordResult.value.total * 100)
})

const verdictText = computed(() => {
  const p = matchPct.value
  if (p >= 80) return 'Sehr gut!'
  if (p >= 50) return 'Fast richtig!'
  if (p >= 25) return 'Ansatz da, aber...'
  return 'Nochmal lernen!'
})

const verdictIcon = computed(() => {
  const p = matchPct.value
  if (p >= 80) return '🟢'
  if (p >= 50) return '🟡'
  if (p >= 25) return '🟠'
  return '🔴'
})

const verdictClass = computed(() => {
  const p = matchPct.value
  if (p >= 80) return 'fb-verdict-green'
  if (p >= 50) return 'fb-verdict-yellow'
  if (p >= 25) return 'fb-verdict-orange'
  return 'fb-verdict-red'
})

const earnedPts = computed(() => {
  if (!currentCard.value?.pts) return 0
  if (aiResult.value) return Math.round(currentCard.value.pts * aiResult.value.pct / 100)
  return Math.round(currentCard.value.pts * matchPct.value / 100)
})

const aiVerdictClass = computed(() => {
  if (!aiResult.value) return ''
  const p = aiResult.value.pct
  if (p >= 80) return 'fb-verdict-green'
  if (p >= 50) return 'fb-verdict-yellow'
  if (p >= 25) return 'fb-verdict-orange'
  return 'fb-verdict-red'
})

const availableTags = computed(() => {
  const catCards = activeCat.value === 'all' ? cards : cards.filter(c => c.cat === activeCat.value)
  return [...new Set(catCards.map(c => c.tag).filter(Boolean))]
})

const browsableCards = computed(() => {
  const list = activeCat.value === 'all'
    ? cards.map((c, i) => ({ ...c, idx: i }))
    : cards.map((c, i) => ({ ...c, idx: i })).filter(x => x.cat === activeCat.value)
  if (tagFilter.value) return list.filter(c => c.tag === tagFilter.value)
  return list
})

// ─── METHODS ───

function shuffle(arr: number[]) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function resetDeck() {
  deck.value = shuffle(currentDeck.value)
  cardIdx.value = 0
  known.value = []
  again.value = []
  weakSet.value = new Set()
  revealed.value = false
  userAnswer.value = ''
  deckDone.value = false
  isCustomSelection.value = false
  totalEarnedPts.value = 0
  totalMaxPts.value = 0
  roundCount.value = 0
  roundPos.value = 0
  statsGreen.value = 0
  statsYellow.value = 0
  statsRed.value = 0
  nextTick(() => answerInput.value?.focus())
}

function resetWeak() {
  deck.value = shuffle([...weakSet.value])
  cardIdx.value = 0
  known.value = []
  again.value = []
  revealed.value = false
  userAnswer.value = ''
  deckDone.value = false
  nextTick(() => answerInput.value?.focus())
}

let gradeRequestId = 0

async function reveal() {
  if (!userAnswer.value.trim()) return
  revealed.value = true
  aiResult.value = null
  aiGrading.value = true
  const requestId = ++gradeRequestId
  const card = currentCard.value
  if (!card) { aiGrading.value = false; return }

  // Fire and forget — don't block the UI
  gradeAnswer(requestId, card, userAnswer.value)
}

async function gradeAnswer(requestId: number, card: any, answer: string, attempt = 1) {
  try {
    const gradePrompt = `Bewerte diese AP1-Prüfungsantwort. Antworte NUR mit JSON: {"pct": 0-100, "feedback": "kurzer Satz"}

Frage: ${card.q}
Musterlösung: ${card.a}
Schüler-Antwort: ${answer}
Max Punkte: ${card.pts || 5}

Bewerte inhaltlich — Tippfehler ignorieren! pct = Prozent der Punkte. feedback = was fehlt/gut war, 1 Satz Deutsch.`
    const res = await tutorChat({
      message: gradePrompt,
      systemPrompt: 'Du bist ein IHK-Prüfer für FISI AP1. Bewerte fair. Tippfehler ignorieren. Antworte IMMER exakt so: {"pct": ZAHL, "feedback": "TEXT"} — nichts anderes.',
      history: []
    })
    // Ignoriere Ergebnis wenn User schon weiter geklickt hat
    if (requestId !== gradeRequestId) return
    const raw = res.message.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim()
    const jsonMatch = raw.match(/\{[^}]*"pct"\s*:\s*\d+[^}]*\}/)
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0])
      aiResult.value = { pct: Math.min(100, Math.max(0, Number(parsed.pct) || 0)), feedback: String(parsed.feedback || '') }
    } else {
      const pctMatch = raw.match(/(\d{1,3})\s*%/)
      aiResult.value = {
        pct: pctMatch ? Math.min(100, Number(pctMatch[1])) : matchPct.value,
        feedback: raw.slice(0, 120)
      }
    }
  } catch (err) {
    if (requestId !== gradeRequestId) return
    // Retry once — Gemini API throws sporadic 500s
    if (attempt < 2) {
      return gradeAnswer(requestId, card, answer, attempt + 1)
    }
    console.error('AI grading error:', err)
    aiResult.value = { pct: matchPct.value, feedback: 'KI-Bewertung konnte nicht geladen werden.' }
  } finally {
    if (requestId === gradeRequestId) aiGrading.value = false
  }
}

function nextCard() {
  revealed.value = false
  userAnswer.value = ''
  if (deck.value.length > 0 && cardIdx.value < deck.value.length - 1) {
    cardIdx.value++
  } else if (again.value.length > 0) {
    deck.value = shuffle(again.value)
    again.value = []
    cardIdx.value = 0
  } else {
    deckDone.value = true
    emit('score', known.value.length)
    return
  }
  nextTick(() => answerInput.value?.focus())
}

function markKnown() {
  known.value.push(deck.value[cardIdx.value])
  nextCard()
}

function markAgain() {
  const idx = deck.value[cardIdx.value]
  again.value.push(idx)
  weakSet.value.add(idx)
  nextCard()
}

function catProgress(catId: string) {
  const total = catId === 'all' ? cards.length : cards.filter(c => c.cat === catId).length
  return total + ' Karten'
}

// ─── TUTOR FUNCTIONS ───

async function askTutor(msg?: string) {
  const question = (msg || tutorInput.value).trim()
  if (!question || tutorLoading.value) return
  tutorMessages.value.push({ role: 'user', content: question })
  tutorInput.value = ''
  tutorLoading.value = true
  await nextTick()
  if (tutorContainer.value) tutorContainer.value.scrollTop = tutorContainer.value.scrollHeight
  try {
    const history = tutorMessages.value.slice(0, -1).map(m => ({
      role: (m.role === 'tutor' ? 'assistant' : 'user') as 'assistant' | 'user',
      content: m.content
    }))
    const res = await tutorChat({ message: question, systemPrompt: LUMI_PROMPT, history })
    tutorMessages.value.push({ role: 'tutor', content: res.message })
  } catch {
    tutorMessages.value.push({ role: 'tutor', content: '⚠️ Fehler — bitte nochmal versuchen.' })
  } finally {
    tutorLoading.value = false
    await nextTick()
    if (tutorContainer.value) tutorContainer.value.scrollTop = tutorContainer.value.scrollHeight
  }
}

function askAboutCard() {
  if (!currentCard.value) return
  showTutor.value = true
  askTutor(`Ich bin mir unsicher beim Begriff "${currentCard.value.q}". Gib mir NICHT die Antwort — stell mir eine Frage die mich selbst drauf bringt!`)
}

function skipCard() {
  revealed.value = false
  userAnswer.value = ''
  aiResult.value = null
  roundPos.value++
  if (cardIdx.value < deck.value.length - 1) {
    cardIdx.value++
  } else {
    if (shuffleOn.value) deck.value = shuffle(deck.value)
    cardIdx.value = 0
    roundCount.value++
  }
  nextTick(() => answerInput.value?.focus())
}

function toggleShuffle() {
  shuffleOn.value = !shuffleOn.value
}

function stopLoop() {
  deckDone.value = true
  emit('score', known.value.length)
}

// ─── BROWSE/SELECT FUNCTIONS ───

function toggleCard(idx: number) {
  const s = new Set(selectedCards.value)
  if (s.has(idx)) s.delete(idx); else s.add(idx)
  selectedCards.value = s
}

function selectAll() {
  selectedCards.value = new Set(browsableCards.value.map(c => c.idx))
}

function selectNone() {
  selectedCards.value = new Set()
}

function selectRandom(n: number) {
  const pool = browsableCards.value.map(c => c.idx)
  const shuffled = shuffle(pool)
  selectedCards.value = new Set(shuffled.slice(0, n))
}

function selectWeakOnly() {
  selectedCards.value = new Set([...weakSet.value].filter(i => {
    const c = cards[i]
    return activeCat.value === 'all' || c.cat === activeCat.value
  }))
}

function startSelected() {
  if (selectedCards.value.size === 0) return
  deck.value = shuffle([...selectedCards.value])
  cardIdx.value = 0
  known.value = []
  again.value = []
  weakSet.value = new Set()
  revealed.value = false
  userAnswer.value = ''
  deckDone.value = false
  browseMode.value = false
  isCustomSelection.value = true
  totalEarnedPts.value = 0
  totalMaxPts.value = 0
  roundCount.value = 0
  roundPos.value = 0
  statsGreen.value = 0
  statsYellow.value = 0
  statsRed.value = 0
  nextTick(() => answerInput.value?.focus())
}

function nextCardAuto() {
  // Track points
  if (currentCard.value?.pts) {
    totalEarnedPts.value += earnedPts.value
    totalMaxPts.value += currentCard.value.pts
  }
  const idx = deck.value[cardIdx.value]
  const pct = aiResult.value ? aiResult.value.pct : matchPct.value
  // Track stats
  if (pct >= 80) statsGreen.value++
  else if (pct >= 50) statsYellow.value++
  else statsRed.value++
  if (pct >= 50) {
    known.value.push(idx)
  } else {
    weakSet.value.add(idx)
  }
  revealed.value = false
  userAnswer.value = ''
  aiResult.value = null
  roundPos.value++
  if (cardIdx.value < deck.value.length - 1) {
    cardIdx.value++
  } else {
    // Loop — von vorne, optional mischen
    if (shuffleOn.value) deck.value = shuffle(deck.value)
    cardIdx.value = 0
    roundCount.value++
  }
  nextTick(() => answerInput.value?.focus())
}

// Init
resetDeck()
</script>

<style scoped>
.fb { display: flex; flex-direction: column; gap: 14px; }

.fb-cats { display: flex; gap: 6px; flex-wrap: wrap; }
.fb-cat-btn {
  padding: 8px 12px; border-radius: 10px; border: 1px solid var(--color-border);
  background: var(--color-surface); color: var(--color-text-secondary);
  cursor: pointer; font-size: 12px; font-weight: 600; transition: all 0.15s;
}
.fb-cat-btn:hover { border-color: #a78bfa; }
.fb-cat-on { border-color: #a78bfa !important; background: rgba(167,139,250,0.2) !important; color: #c4b5fd !important; }
.fb-cat-count { font-size: 10px; opacity: 0.6; margin-left: 4px; }

.fb-stats-row { display: flex; gap: 12px; align-items: center; font-size: 13px; padding: 4px 0; }
.fb-stat { font-weight: 500; }
.fb-stat-total { color: var(--color-text-secondary); }
.fb-progress-row { display: flex; gap: 8px; align-items: center; }
.fb-progress { position: relative; flex: 1; height: 24px; background: var(--color-surface); border-radius: 12px; border: 1px solid var(--color-border); overflow: hidden; }
.fb-shuffle-btn {
  width: 32px; height: 32px; border-radius: 8px; border: 1px solid var(--color-border);
  background: var(--color-surface); font-size: 14px; cursor: pointer; opacity: 0.4;
  display: flex; align-items: center; justify-content: center; transition: all 0.15s;
}
.fb-shuffle-btn:hover { opacity: 0.7; }
.fb-shuffle-on { opacity: 1 !important; border-color: #a78bfa; background: rgba(167,139,250,0.2); }
.fb-progress-bar { height: 100%; background: linear-gradient(90deg, #6366f1, #a78bfa); transition: width 0.3s; border-radius: 12px; }
.fb-progress-txt { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; color: var(--color-text); }

.fb-card {
  border-radius: 16px; padding: 24px; display: flex; flex-direction: column; gap: 12px;
  background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(167,139,250,0.08));
  border: 1px solid var(--color-border);
}
.fb-card-cat { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #a78bfa; }
.fb-card-q { font-size: 18px; font-weight: 700; color: var(--color-text); line-height: 1.4; }
.fb-card-pts { font-size: 11px; font-weight: 700; color: #facc15; background: rgba(250,204,21,0.15); padding: 2px 8px; border-radius: 6px; vertical-align: middle; }

.fb-write-area { display: flex; flex-direction: column; gap: 10px; }
.fb-textarea {
  width: 100%; padding: 14px; border-radius: 10px; border: 2px solid var(--color-border);
  background: var(--color-background); color: var(--color-text); font-size: 14px;
  font-family: inherit; resize: vertical; line-height: 1.5;
  transition: border-color 0.2s;
}
.fb-textarea:focus { outline: none; border-color: #a78bfa; }
.fb-textarea::placeholder { color: var(--color-text-secondary); opacity: 0.5; }

.fb-compare { display: flex; flex-direction: column; gap: 12px; }
.fb-compare-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.fb-compare-text { padding: 12px; border-radius: 10px; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
.fb-compare-user { background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); color: #c7d2fe; }
.fb-compare-user .fb-compare-label { color: #a5b4fc; }
.fb-your-answer .fb-compare-label { color: #a5b4fc; }
.fb-compare-correct { background: rgba(74,222,128,0.1); border: 1px solid rgba(74,222,128,0.3); color: #4ade80; font-weight: 700; }
.fb-correct-answer .fb-compare-label { color: #4ade80; }
.fb-verdict {
  display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-radius: 12px; font-weight: 700;
}
.fb-verdict-green { background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.4); color: #4ade80; }
.fb-verdict-yellow { background: rgba(250,204,21,0.15); border: 1px solid rgba(250,204,21,0.4); color: #facc15; }
.fb-verdict-orange { background: rgba(251,146,60,0.15); border: 1px solid rgba(251,146,60,0.4); color: #fb923c; }
.fb-verdict-red { background: rgba(248,113,113,0.15); border: 1px solid rgba(248,113,113,0.4); color: #f87171; }
.fb-verdict-icon { font-size: 20px; }
.fb-verdict-txt { flex: 1; font-size: 16px; }
.fb-verdict-pts { font-size: 14px; font-weight: 800; }
.fb-verdict-pct { font-size: 12px; opacity: 0.6; }
.fb-verdict-loading { background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); color: #a5b4fc; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
.fb-ai-feedback { font-size: 13px; padding: 10px 14px; border-radius: 10px; background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2); color: #c7d2fe; line-height: 1.5; }

.fb-keywords { display: flex; flex-direction: column; gap: 6px; }
.fb-kw-row { display: flex; flex-wrap: wrap; gap: 6px; }
.fb-kw {
  padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight: 600;
}
.fb-kw-hit { background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }
.fb-kw-miss { background: rgba(248,113,113,0.1); color: #f87171; border: 1px solid rgba(248,113,113,0.3); text-decoration: line-through; }
.fb-kw-summary { font-size: 11px; color: var(--color-text-secondary); font-weight: 600; }

.fb-card-detail { font-size: 13px; color: var(--color-text-secondary); line-height: 1.4; padding: 10px; background: rgba(0,0,0,0.15); border-radius: 8px; }
.fb-card-btns { display: flex; gap: 10px; padding-top: 8px; }

.fb-btn {
  flex: 1; padding: 12px; border-radius: 10px; border: none;
  font-weight: 700; font-size: 14px; cursor: pointer; transition: all 0.15s;
}
.fb-btn-again { background: rgba(251,146,60,0.2); color: #fb923c; }
.fb-btn-again:hover { background: rgba(251,146,60,0.3); }
.fb-write-btns { display: flex; gap: 8px; }
.fb-btn-reveal { background: rgba(167,139,250,0.2); color: #c4b5fd; }
.fb-btn-reveal:hover { background: rgba(167,139,250,0.3); }
.fb-btn-reveal:disabled { opacity: 0.3; cursor: not-allowed; }
.fb-btn-skip { background: rgba(148,163,184,0.15); color: #94a3b8; flex: 0 0 auto; }
.fb-btn-skip:hover { background: rgba(148,163,184,0.25); }
.fb-btn-ok { background: rgba(74,222,128,0.2); color: #4ade80; }
.fb-btn-ok:hover { background: rgba(74,222,128,0.3); }
.fb-btn-restart { background: rgba(99,102,241,0.2); color: #a5b4fc; }
.fb-btn-restart:hover { background: rgba(99,102,241,0.3); }
.fb-btn-weak { background: rgba(251,146,60,0.2); color: #fb923c; margin-top: 8px; }
.fb-btn-weak:hover { background: rgba(251,146,60,0.3); }

.fb-card-tag { font-weight: 400; opacity: 0.7; }

.fb-browse-row { display: flex; align-items: center; gap: 10px; }
.fb-btn-browse { flex: 0 0 auto; padding: 8px 14px; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); border-radius: 10px; color: #a5b4fc; font-size: 12px; font-weight: 600; cursor: pointer; }
.fb-btn-browse:hover { background: rgba(99,102,241,0.25); }
.fb-selected-info { font-size: 12px; color: #a78bfa; font-weight: 600; }

.fb-browse-panel {
  border: 1px solid var(--color-border); border-radius: 14px; padding: 14px;
  background: var(--color-surface); display: flex; flex-direction: column; gap: 10px;
}
.fb-browse-actions { display: flex; gap: 6px; flex-wrap: wrap; }
.fb-quick-btn {
  padding: 6px 12px; border-radius: 8px; border: 1px solid var(--color-border);
  background: var(--color-background); color: var(--color-text-secondary);
  font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.fb-quick-btn:hover { border-color: #a78bfa; color: #c4b5fd; }

.fb-tag-filter { display: flex; gap: 4px; flex-wrap: wrap; }
.fb-tag-pill {
  padding: 4px 10px; border-radius: 12px; border: 1px solid var(--color-border);
  background: var(--color-background); color: var(--color-text-secondary);
  font-size: 10px; font-weight: 600; cursor: pointer; transition: all 0.15s;
}
.fb-tag-pill:hover { border-color: #a78bfa; }
.fb-tag-on { border-color: #a78bfa; background: rgba(167,139,250,0.15); color: #c4b5fd; }

.fb-browse-list { max-height: 280px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
.fb-browse-item {
  display: flex; align-items: center; gap: 8px; padding: 8px 10px; border-radius: 8px;
  background: var(--color-background); border: 1px solid transparent; cursor: pointer;
  font-size: 13px; color: var(--color-text); transition: all 0.15s;
}
.fb-browse-item:hover { border-color: var(--color-border); }
.fb-browse-selected { border-color: rgba(167,139,250,0.4) !important; background: rgba(167,139,250,0.08); }
.fb-browse-item input[type="checkbox"] { accent-color: #a78bfa; }
.fb-browse-tag { font-size: 10px; font-weight: 700; color: #a78bfa; background: rgba(167,139,250,0.15); padding: 2px 6px; border-radius: 6px; white-space: nowrap; }
.fb-browse-q { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.fb-btn-start { padding: 12px; background: rgba(74,222,128,0.2); color: #4ade80; font-weight: 700; font-size: 14px; border: none; border-radius: 10px; cursor: pointer; }
.fb-btn-start:hover { background: rgba(74,222,128,0.3); }
.fb-btn-start:disabled { opacity: 0.3; cursor: not-allowed; }

.fb-done { text-align: center; padding: 40px 20px; background: var(--color-surface); border-radius: 16px; border: 1px solid var(--color-border); }
.fb-done-icon { font-size: 48px; margin-bottom: 12px; }
.fb-done-txt { font-size: 16px; font-weight: 700; color: var(--color-text); margin-bottom: 8px; }
.fb-done-pts { font-size: 18px; font-weight: 800; color: #a78bfa; margin-bottom: 12px; }
.fb-done-weak { font-size: 13px; color: #fb923c; margin-bottom: 16px; }
.fb-btn-next { background: rgba(99,102,241,0.2); color: #a5b4fc; }
.fb-btn-next:hover { background: rgba(99,102,241,0.3); }
.fb-btn-stop { background: rgba(248,113,113,0.15); color: #f87171; flex: 0 0 auto; }
.fb-btn-stop:hover { background: rgba(248,113,113,0.25); }

/* Tutor styles (same as IPv6Trainer) */
.fb-tutor-wrap { margin-top: 8px; }
.fb-tutor-toggle { width: 100%; padding: 10px; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3); border-radius: 10px; color: #a5b4fc; font-size: 13px; font-weight: 600; cursor: pointer; }
.fb-tutor-panel { margin-top: 8px; border: 1px solid var(--color-border); border-radius: 12px; background: var(--color-surface); overflow: hidden; }
.fb-tutor-msgs { max-height: 250px; overflow-y: auto; padding: 12px; display: flex; flex-direction: column; gap: 8px; }
.fb-tutor-empty { text-align: center; color: var(--color-text-secondary); font-size: 13px; padding: 16px; }
.fb-tutor-msg { padding: 8px 12px; border-radius: 10px; font-size: 13px; line-height: 1.5; max-width: 85%; }
.fb-tm-user { background: rgba(99,102,241,0.15); color: #c7d2fe; align-self: flex-end; }
.fb-tm-bot { background: rgba(74,222,128,0.1); color: var(--color-text); align-self: flex-start; }
.fb-tutor-input-row { display: flex; gap: 6px; padding: 8px; border-top: 1px solid var(--color-border); }
.fb-tutor-ctx { padding: 6px 10px; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); border-radius: 8px; color: #a5b4fc; font-size: 12px; cursor: pointer; white-space: nowrap; }
.fb-tutor-inp { flex: 1; padding: 6px 10px; background: var(--color-background); border: 1px solid var(--color-border); border-radius: 8px; color: var(--color-text); font-size: 13px; }
.fb-tutor-send { padding: 6px 12px; background: #6366f1; border: none; border-radius: 8px; color: white; cursor: pointer; font-weight: 700; }
.fb-tutor-send:disabled { opacity: 0.3; }
</style>
