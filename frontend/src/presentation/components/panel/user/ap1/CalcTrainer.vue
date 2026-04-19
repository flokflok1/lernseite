<template>
  <div class="ct-wrap">
    <!-- Header -->
    <div class="ct-header">
      <div>
        <h2 class="ct-title">💰 Kalkulation mit Casio</h2>
        <p class="ct-sub">Echte BW-Aufgaben · Casio FX-991DEX Anleitung bei jeder Aufgabe</p>
      </div>
      <LumiHint
        :context="`Kalkulation BW AP1 – Aufgabentyp: ${activeType}. ${lumiCtx}`"
        systemExtra="Pascal hat ADHS, 10 Tage bis AP1 BW. Erkläre Kalkulation mit Casio FX-991DEX Tasten. Kurz, Stichpunkte, max 4 Sätze. Konkrete Zahlen aus der Aufgabe nutzen."
      />
    </div>

    <!-- Typ-Auswahl -->
    <div class="ct-tabs">
      <button v-for="t in TYPES" :key="t.key"
        class="ct-tab" :class="activeType === t.key ? 'ct-tab-on' : ''"
        @click="switchType(t.key)">
        {{ t.icon }} {{ t.label }}
        <span class="ct-pts">{{ t.pts }}P</span>
      </button>
    </div>

    <!-- ===== BEZUGSKALKULATION ===== -->
    <div v-if="activeType === 'bezug'" class="ct-card">
      <div class="ct-scenario">
        <div class="ct-badge">📦 Beschaffung – Bezugskalkulation</div>
        <p class="ct-scenario-text">
          Sie beschaffen <strong>{{ bk.qty }}× {{ bk.product }}</strong>.
          Ihr Lieferant macht folgendes Angebot:
        </p>
        <div class="ct-data-grid">
          <div class="ct-row"><span>Listenpreis (netto)</span><strong>{{ fmt(bk.list) }} €</strong></div>
          <div class="ct-row"><span>Lieferantenrabatt</span><strong>{{ bk.rabatt }} %</strong></div>
          <div class="ct-row"><span>Liefererskonto</span><strong>{{ bk.skonto }} %</strong></div>
          <div class="ct-row"><span>Bezugskosten (Fracht)</span><strong>{{ fmt(bk.fracht) }} €</strong></div>
        </div>
        <p class="ct-question">Berechnen Sie den <strong>Bezugspreis</strong> Schritt für Schritt!</p>
      </div>
      <div class="ct-formula-hint">
        📋 Listenpreis → <em>−Rabatt</em> → Zieleinkaufspreis → <em>−Skonto</em> → Bareinkaufspreis → <em>+Fracht</em> → Bezugspreis
      </div>
      <div class="ct-inputs">
        <div v-for="(step, i) in bkSteps" :key="i" class="ct-input-row"
          :class="bkState[i]==='ok'?'row-ok':bkState[i]==='err'?'row-err':''">
          <label class="ct-label">{{ step.label }}:</label>
          <div class="ct-input-wrap">
            <input v-model="bkAns[i]" type="number" step="0.01" :placeholder="step.ph"
              class="ct-input" :disabled="bkState[i]==='ok'" @keyup.enter="checkBk(i)" />
            <span class="ct-unit">€</span>
          </div>
          <button v-if="bkState[i]!=='ok'" class="ct-btn-ok" @click="checkBk(i)">✓</button>
          <span v-if="bkState[i]==='ok'" class="ct-tick">✅</span>
          <div v-if="bkState[i]==='err'" class="ct-err-hint">✗ Richtig: <strong>{{ bkCorrect[i] }} €</strong></div>
        </div>
      </div>
      <div class="ct-casio-box">
        <button class="ct-casio-toggle" @click="showCasio=!showCasio">
          🔢 Casio FX-991DEX – Schritt-für-Schritt {{ showCasio ? '▲' : '▼' }}
        </button>
        <div v-if="showCasio" class="ct-casio-panel">
          <div class="ct-casio-intro">Tippe genau diese Tasten — Zwischenergebnisse bleiben im <kbd class="ans">Ans</kbd> Speicher!</div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">①</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Zieleinkaufspreis (Rabatt abziehen)</div>
              <div class="ct-cs-keys">
                <kbd>{{ bk.list }}</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd>
                <kbd class="op">−</kbd><kbd>{{ bk.rabatt }}</kbd><kbd class="op">÷</kbd>
                <kbd>100</kbd><kbd>)</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ bkCorrect[0] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">②</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Bareinkaufspreis (Skonto abziehen)</div>
              <div class="ct-cs-keys">
                <kbd class="ans">Ans</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd>
                <kbd class="op">−</kbd><kbd>{{ bk.skonto }}</kbd><kbd class="op">÷</kbd>
                <kbd>100</kbd><kbd>)</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ bkCorrect[1] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">③</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Bezugspreis (Frachtkosten addieren)</div>
              <div class="ct-cs-keys">
                <kbd class="ans">Ans</kbd><kbd class="op">+</kbd><kbd>{{ bk.fracht }}</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ bkCorrect[2] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-tipp">
            💡 <strong>Alles in einem:</strong>
            <kbd>{{ bk.list }}</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd><kbd class="op">−</kbd><kbd>{{ bk.rabatt }}</kbd><kbd class="op">÷</kbd><kbd>100</kbd><kbd>)</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd><kbd class="op">−</kbd><kbd>{{ bk.skonto }}</kbd><kbd class="op">÷</kbd><kbd>100</kbd><kbd>)</kbd><kbd class="op">+</kbd><kbd>{{ bk.fracht }}</kbd><kbd class="op">=</kbd>
          </div>
          <button @click="showResults=!showResults" class="ct-reveal-btn">{{ showResults ? "🙈 Ergebnisse ausblenden" : "👁 Ergebnisse einblenden" }}</button>
        </div>
      </div>
      <div class="ct-actions">
        <div v-if="bkDone" class="ct-done">🎉 Alle Schritte richtig! <strong>+{{ bkScore }}P</strong></div>
        <button class="ct-btn-next" @click="genBk">🔄 Neue Aufgabe</button>
      </div>
    </div>

    <!-- ===== ANGEBOTSVERGLEICH ===== -->
    <div v-if="activeType === 'angebot'" class="ct-card">
      <div class="ct-scenario">
        <div class="ct-badge">🤝 Angebotsvergleich (15P in Sommer 2024!)</div>
        <p class="ct-scenario-text">
          Sie möchten <strong>{{ av.product }}</strong> beschaffen und erhalten zwei Angebote:
        </p>
        <div v-if="avStufe < 3" class="ct-two-offers">
          <div class="ct-offer">
            <div class="ct-offer-name">Angebot A: {{ av.a.name }}</div>
            <div class="ct-row"><span>Listenpreis</span><strong>{{ fmt(av.a.list) }} €</strong></div>
            <div class="ct-row"><span>Rabatt</span><strong>{{ av.a.rabatt }} %</strong></div>
            <div class="ct-row"><span>Skonto</span><strong>{{ av.a.skonto }} %</strong></div>
            <div class="ct-row"><span>Versandkosten</span><strong>{{ fmt(av.a.fracht) }} €</strong></div>
          </div>
          <div class="ct-offer">
            <div class="ct-offer-name">Angebot B: {{ av.b.name }}</div>
            <div class="ct-row"><span>Listenpreis</span><strong>{{ fmt(av.b.list) }} €</strong></div>
            <div class="ct-row"><span>Rabatt</span><strong>{{ av.b.rabatt }} %</strong></div>
            <div class="ct-row"><span>Skonto</span><strong>{{ av.b.skonto }} %</strong></div>
            <div class="ct-row"><span>Versandkosten</span><strong>{{ fmt(av.b.fracht) }} €</strong></div>
          </div>
        </div>
        <p class="ct-question">Berechnen Sie den <strong>Bezugspreis beider Angebote</strong> und wählen Sie das günstigere!</p>
      </div>
      <div class="ct-formula-hint">
        📋 Für jedes Angebot: Liste → −Rabatt% → Ziel → −Skonto% → Bar → +Versand → <strong>Bezugspreis</strong>
      </div>
      <div class="av-stufe-row">
        <button v-for="s in avStufen" :key="s.n" class="av-stufe-btn" :class="avStufe===s.n?'av-stufe-on':''" @click="avStufe=s.n">{{ s.l }}</button>
      </div>
      <div v-if="avStufe===3" class="av-stufe3-hint">
        📝 Angebot A (<em>{{ av.a.name }}</em>): LP {{ fmt(av.a.list) }} €, {{ av.a.rabatt }}% Rabatt, {{ av.a.skonto }}% Skonto, {{ fmt(av.a.fracht) }} € Versand &nbsp;|&nbsp;
        Angebot B (<em>{{ av.b.name }}</em>): LP {{ fmt(av.b.list) }} €, {{ av.b.rabatt }}% Rabatt, {{ av.b.skonto }}% Skonto, {{ fmt(av.b.fracht) }} € Versand
      </div>
      <div class="av-table">
        <div class="av-head">
          <div class="av-col-lbl"></div>
          <div class="av-col-a">{{ av.a.name }}</div>
          <div class="av-col-b">{{ av.b.name }}</div>
        </div>
        <div v-for="(row,i) in avRowDefs" :key="i" class="av-row" :class="i===3?'av-row-final':''">
          <div class="av-col-lbl">
            <span v-if="avStufe===1">{{ row.label }}</span>
            <template v-else>
              <input v-model="avLabelInputs[i]" class="av-lbl-inp" :class="avLabelOk[i]?'av-lbl-ok':''" :placeholder="'Feldname ' + (i+1)" />
              <span v-if="avLabelOk[i]" class="ct-tick">✅</span>
            </template>
          </div>
          <div class="av-col-a">
            <div v-if="i===0 && avStufe===1" class="av-given">{{ fmt(av.a.list) }} €</div>
            <template v-else>
              <div class="av-val-row" :class="avStateA[i]==='ok'?'row-ok':avStateA[i]==='err'?'row-err':''">
                <input v-model="avAnsA[i]" type="number" step="0.01" class="ct-input"
                  :disabled="avStateA[i]==='ok'" @keyup.enter="checkAv('A',i)" />
                <button v-if="avStateA[i]!=='ok'" class="ct-btn-ok" @click="checkAv('A',i)">✓</button>
                <span v-if="avStateA[i]==='ok'" class="ct-tick">✅</span>
              </div>
              <div v-if="avStateA[i]==='err'" class="ct-err-hint">✗ {{ avCorrectA[i] }} €</div>
            </template>
          </div>
          <div class="av-col-b">
            <div v-if="i===0 && avStufe===1" class="av-given">{{ fmt(av.b.list) }} €</div>
            <template v-else>
              <div class="av-val-row" :class="avStateB[i]==='ok'?'row-ok':avStateB[i]==='err'?'row-err':''">
                <input v-model="avAnsB[i]" type="number" step="0.01" class="ct-input"
                  :disabled="avStateB[i]==='ok'" @keyup.enter="checkAv('B',i)" />
                <button v-if="avStateB[i]!=='ok'" class="ct-btn-ok" @click="checkAv('B',i)">✓</button>
                <span v-if="avStateB[i]==='ok'" class="ct-tick">✅</span>
              </div>
              <div v-if="avStateB[i]==='err'" class="ct-err-hint">✗ {{ avCorrectB[i] }} €</div>
            </template>
          </div>
        </div>
      </div>

      <div v-if="avBothDone" class="ct-winner-choice">
        <p class="ct-question" style="margin:0 0 10px">Welchen Lieferanten wählen Sie?</p>
        <div class="ct-choice-btns">
          <button class="ct-choice-btn" :class="avChoice==='A'?'ct-choice-on':''" @click="avChoice='A'">
            Angebot A – {{ av.a.name }}
          </button>
          <button class="ct-choice-btn" :class="avChoice==='B'?'ct-choice-on':''" @click="avChoice='B'">
            Angebot B – {{ av.b.name }}
          </button>
        </div>
        <button v-if="avChoice && !avChoiceChecked" class="ct-btn-ok"
          style="width:auto;padding:8px 24px;margin-top:10px;" @click="checkAvChoice">
          Auswahl prüfen
        </button>
        <div v-if="avChoiceChecked" class="ct-done" :class="avChoiceCorrect?'':'ct-done-err'" style="margin-top:10px">
          {{ avChoiceCorrect
            ? '🎉 Richtig! ' + avWinnerName + ' ist günstiger (' + avWinnerPrice + ' €)'
            : '✗ Falsch! Günstiger: ' + avWinnerName + ' mit ' + avWinnerPrice + ' €' }}
        </div>
      </div>
      <div class="ct-casio-box">
        <button class="ct-casio-toggle" @click="showCasio=!showCasio">
          🔢 Casio FX-991DEX – Schritt-für-Schritt {{ showCasio ? '▲' : '▼' }}
        </button>
        <div v-if="showCasio" class="ct-casio-panel">
          <div class="ct-casio-intro">Berechne jeden Bezugspreis separat — gleiche Schritte für A und B!</div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">①</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Angebot A – Bezugspreis komplett in einem Ausdruck</div>
              <div class="ct-cs-keys">
                <kbd>{{ av.a.list }}</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd><kbd class="op">−</kbd>
                <kbd>{{ av.a.rabatt }}</kbd><kbd class="op">÷</kbd><kbd>100</kbd><kbd>)</kbd>
                <kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd><kbd class="op">−</kbd>
                <kbd>{{ av.a.skonto }}</kbd><kbd class="op">÷</kbd><kbd>100</kbd><kbd>)</kbd>
                <kbd class="op">+</kbd><kbd>{{ av.a.fracht }}</kbd><kbd class="op">=</kbd>
                <span class="ct-cs-save"><kbd class="shift">SHIFT</kbd><kbd>STO</kbd><kbd class="ans">A</kbd></span>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ avCorrectA[3] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">②</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Angebot B – gleicher Ausdruck</div>
              <div class="ct-cs-keys">
                <kbd>{{ av.b.list }}</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd><kbd class="op">−</kbd>
                <kbd>{{ av.b.rabatt }}</kbd><kbd class="op">÷</kbd><kbd>100</kbd><kbd>)</kbd>
                <kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd><kbd class="op">−</kbd>
                <kbd>{{ av.b.skonto }}</kbd><kbd class="op">÷</kbd><kbd>100</kbd><kbd>)</kbd>
                <kbd class="op">+</kbd><kbd>{{ av.b.fracht }}</kbd><kbd class="op">=</kbd>
                <span class="ct-cs-save"><kbd class="shift">SHIFT</kbd><kbd>STO</kbd><kbd class="ans">B</kbd></span>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ avCorrectB[3] }} €</strong> → Günstiger: <strong>{{ avWinnerName }}</strong></div>
            </div>
          </div>
          <div class="ct-casio-tipp">
            💡 <strong>Vergleich:</strong> <kbd class="ans">RCL</kbd><kbd class="ans">A</kbd> und <kbd class="ans">RCL</kbd><kbd class="ans">B</kbd> aufrufen — kleinerer Wert gewinnt!
          </div>
          <button @click="showResults=!showResults" class="ct-reveal-btn">{{ showResults ? "🙈 Ergebnisse ausblenden" : "👁 Ergebnisse einblenden" }}</button>
        </div>
      </div>
      <div class="ct-actions">
        <button class="ct-btn-next" @click="genAv">🔄 Neue Aufgabe</button>
      </div>
    </div>

    <!-- ===== STROMKOSTEN ===== -->
    <div v-if="activeType === 'strom'" class="ct-card">
      <div class="ct-scenario">
        <div class="ct-badge">⚡ Stromkostenberechnung</div>
        <p class="ct-scenario-text">
          Berechnen Sie die <strong>jährlichen Stromkosten</strong>. Strompreis: <strong>{{ sk.preis }} €/kWh</strong>
        </p>
        <div class="ct-strom-table">
          <div class="ct-strom-header">
            <span>Gerät</span><span>Watt</span><span>h/Tag</span><span>Tage/Jahr</span>
          </div>
          <div v-for="(g, i) in sk.geraete" :key="i" class="ct-strom-row">
            <span>{{ g.name }}</span><span>{{ g.watt }} W</span>
            <span>{{ g.stunden }} h</span><span>{{ g.tage }}</span>
          </div>
        </div>
      </div>
      <div class="ct-formula-hint">
        📋 kWh/Jahr = Watt × h/Tag × Tage ÷ 1000 · Kosten = kWh × {{ sk.preis }} €
      </div>
      <div class="ct-inputs">
        <template v-for="(g, i) in sk.geraete" :key="i">
          <div class="ct-strom-label">{{ g.name }}:</div>
          <div class="ct-input-row" :class="skState[i*2]==='ok'?'row-ok':skState[i*2]==='err'?'row-err':''">
            <label class="ct-label">kWh/Jahr:</label>
            <div class="ct-input-wrap">
              <input v-model="skAns[i*2]" type="number" step="0.01" placeholder="0.00"
                class="ct-input" :disabled="skState[i*2]==='ok'" @keyup.enter="checkSk(i*2)" />
              <span class="ct-unit">kWh</span>
            </div>
            <button v-if="skState[i*2]!=='ok'" class="ct-btn-ok" @click="checkSk(i*2)">✓</button>
            <span v-if="skState[i*2]==='ok'" class="ct-tick">✅</span>
            <div v-if="skState[i*2]==='err'" class="ct-err-hint">✗ {{ skCorrect[i*2] }} kWh</div>
          </div>
          <div class="ct-input-row" :class="skState[i*2+1]==='ok'?'row-ok':skState[i*2+1]==='err'?'row-err':''">
            <label class="ct-label">Kosten/Jahr:</label>
            <div class="ct-input-wrap">
              <input v-model="skAns[i*2+1]" type="number" step="0.01" placeholder="0.00"
                class="ct-input" :disabled="skState[i*2+1]==='ok'" @keyup.enter="checkSk(i*2+1)" />
              <span class="ct-unit">€</span>
            </div>
            <button v-if="skState[i*2+1]!=='ok'" class="ct-btn-ok" @click="checkSk(i*2+1)">✓</button>
            <span v-if="skState[i*2+1]==='ok'" class="ct-tick">✅</span>
            <div v-if="skState[i*2+1]==='err'" class="ct-err-hint">✗ {{ skCorrect[i*2+1] }} €</div>
          </div>
        </template>
        <div class="ct-input-row ct-total-row"
          :class="skState[sk.geraete.length*2]==='ok'?'row-ok':skState[sk.geraete.length*2]==='err'?'row-err':''">
          <label class="ct-label" style="font-weight:800">Gesamtkosten/Jahr:</label>
          <div class="ct-input-wrap">
            <input v-model="skAns[sk.geraete.length*2]" type="number" step="0.01" placeholder="0.00"
              class="ct-input" :disabled="skState[sk.geraete.length*2]==='ok'" @keyup.enter="checkSkTotal" />
            <span class="ct-unit">€</span>
          </div>
          <button v-if="skState[sk.geraete.length*2]!=='ok'" class="ct-btn-ok" @click="checkSkTotal">✓</button>
          <span v-if="skState[sk.geraete.length*2]==='ok'" class="ct-tick">✅</span>
          <div v-if="skState[sk.geraete.length*2]==='err'" class="ct-err-hint">✗ {{ skCorrect[sk.geraete.length*2] }} €</div>
        </div>
      </div>
      <div class="ct-casio-box">
        <button class="ct-casio-toggle" @click="showCasio=!showCasio">
          🔢 Casio FX-991DEX – Schritt-für-Schritt {{ showCasio ? '▲' : '▼' }}
        </button>
        <div v-if="showCasio" class="ct-casio-panel">
          <div class="ct-casio-intro">Für jedes Gerät: <em>Watt × Stunden × Tage ÷ 1000 = kWh, dann × Preis = €</em></div>
          <div v-for="(g, i) in sk.geraete" :key="i" class="ct-casio-step">
            <div class="ct-cs-num">{{ ['①','②','③','④'][i] }}</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">{{ g.name }}</div>
              <div class="ct-cs-keys">
                <kbd>{{ g.watt }}</kbd><kbd class="op">×</kbd><kbd>{{ g.stunden }}</kbd>
                <kbd class="op">×</kbd><kbd>{{ g.tage }}</kbd><kbd class="op">÷</kbd>
                <kbd>1000</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ kWh: <strong>{{ skCorrect[i*2] }}</strong>
                &nbsp;dann&nbsp;
                <kbd class="ans">Ans</kbd><kbd class="op">×</kbd><kbd>{{ sk.preis }}</kbd><kbd class="op">=</kbd>
                → <strong>{{ skCorrect[i*2+1] }} €</strong>
              </div>
            </div>
          </div>
          <div class="ct-casio-tipp">
            💡 Gesamtsumme: Zwischenergebnisse mit <kbd class="shift">SHIFT</kbd><kbd>STO</kbd><kbd class="ans">A</kbd>, <kbd class="ans">B</kbd>, <kbd class="ans">C</kbd> speichern, dann <kbd class="ans">RCL</kbd><kbd class="ans">A</kbd><kbd class="op">+</kbd><kbd class="ans">RCL</kbd><kbd class="ans">B</kbd><kbd class="op">+</kbd>... addieren!
          </div>
          <button @click="showResults=!showResults" class="ct-reveal-btn">{{ showResults ? "🙈 Ergebnisse ausblenden" : "👁 Ergebnisse einblenden" }}</button>
        </div>
      </div>
      <div class="ct-actions">
        <div v-if="skDone" class="ct-done">🎉 Alle Geräte berechnet! <strong>+{{ skScore }}P</strong></div>
        <button class="ct-btn-next" @click="genSk">🔄 Neue Aufgabe</button>
      </div>
    </div>

    <!-- ===== VORWÄRTSKALKULATION ===== -->
    <div v-if="activeType === 'vorwaerts'" class="ct-card">
      <div class="ct-scenario">
        <div class="ct-badge">🏷️ Vorwärtskalkulation (Verkaufspreis ermitteln)</div>
        <p class="ct-scenario-text">
          Berechnen Sie den <strong>Brutto-Listenverkaufspreis</strong> für <strong>{{ vk.product }}</strong>:
        </p>
        <div class="ct-data-grid">
          <div class="ct-row"><span>Bezugspreis (Einstandspreis)</span><strong>{{ fmt(vk.bezug) }} €</strong></div>
          <div class="ct-row"><span>Handlungskostenzuschlag (HKZ)</span><strong>{{ vk.hkz }} %</strong></div>
          <div class="ct-row"><span>Gewinnzuschlag</span><strong>{{ vk.gewinn }} %</strong></div>
          <div class="ct-row"><span>Kundenskonto</span><strong>{{ vk.skonto }} %</strong></div>
          <div class="ct-row"><span>Kundenrabatt</span><strong>{{ vk.rabatt }} %</strong></div>
          <div class="ct-row"><span>Umsatzsteuer</span><strong>{{ vk.mwst }} %</strong></div>
        </div>
      </div>
      <div class="ct-formula-hint">
        📋 Bezugspreis → +HKZ → Selbstkosten → +Gewinn → Bar-VKP → ÷(1−Skonto%) → Ziel-VKP → ÷(1−Rabatt%) → Liste netto → ×(1+MwSt%) → Liste brutto
      </div>
      <div class="ct-inputs">
        <div v-for="(step, i) in vkSteps" :key="i" class="ct-input-row"
          :class="vkState[i]==='ok'?'row-ok':vkState[i]==='err'?'row-err':''">
          <label class="ct-label">{{ step.label }}:</label>
          <div class="ct-input-wrap">
            <input v-model="vkAns[i]" type="number" step="0.01" :placeholder="step.ph"
              class="ct-input" :disabled="vkState[i]==='ok'" @keyup.enter="checkVk(i)" />
            <span class="ct-unit">€</span>
          </div>
          <button v-if="vkState[i]!=='ok'" class="ct-btn-ok" @click="checkVk(i)">✓</button>
          <span v-if="vkState[i]==='ok'" class="ct-tick">✅</span>
          <div v-if="vkState[i]==='err'" class="ct-err-hint">✗ Richtig: <strong>{{ vkCorrect[i] }} €</strong></div>
        </div>
      </div>
      <div class="ct-casio-box">
        <button class="ct-casio-toggle" @click="showCasio=!showCasio">
          🔢 Casio FX-991DEX – Schritt-für-Schritt {{ showCasio ? '▲' : '▼' }}
        </button>
        <div v-if="showCasio" class="ct-casio-panel">
          <div class="ct-casio-intro">⚠️ <strong>Wichtig:</strong> Skonto/Rabatt beim Verkauf = <em>dividieren</em> durch (1 − %) — nicht multiplizieren!</div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">①</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Selbstkostenpreis (Bezugspreis + HKZ)</div>
              <div class="ct-cs-keys">
                <kbd>{{ vk.bezug }}</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd>
                <kbd class="op">+</kbd><kbd>{{ vk.hkz }}</kbd><kbd class="op">÷</kbd>
                <kbd>100</kbd><kbd>)</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ vkCorrect[0] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">②</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Barverkaufspreis (+ Gewinn)</div>
              <div class="ct-cs-keys">
                <kbd class="ans">Ans</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd>
                <kbd class="op">+</kbd><kbd>{{ vk.gewinn }}</kbd><kbd class="op">÷</kbd>
                <kbd>100</kbd><kbd>)</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ vkCorrect[1] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">③</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Zielverkaufspreis (÷ Skonto — DIVIDIEREN!)</div>
              <div class="ct-cs-keys">
                <kbd class="ans">Ans</kbd><kbd class="op">÷</kbd><kbd>(</kbd><kbd>1</kbd>
                <kbd class="op">−</kbd><kbd>{{ vk.skonto }}</kbd><kbd class="op">÷</kbd>
                <kbd>100</kbd><kbd>)</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ vkCorrect[2] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">④</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Listenverkaufspreis netto (÷ Rabatt — DIVIDIEREN!)</div>
              <div class="ct-cs-keys">
                <kbd class="ans">Ans</kbd><kbd class="op">÷</kbd><kbd>(</kbd><kbd>1</kbd>
                <kbd class="op">−</kbd><kbd>{{ vk.rabatt }}</kbd><kbd class="op">÷</kbd>
                <kbd>100</kbd><kbd>)</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ vkCorrect[3] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-step">
            <div class="ct-cs-num">⑤</div>
            <div class="ct-cs-body">
              <div class="ct-cs-label">Listenverkaufspreis brutto (+ MwSt)</div>
              <div class="ct-cs-keys">
                <kbd class="ans">Ans</kbd><kbd class="op">×</kbd><kbd>(</kbd><kbd>1</kbd>
                <kbd class="op">+</kbd><kbd>{{ vk.mwst }}</kbd><kbd class="op">÷</kbd>
                <kbd>100</kbd><kbd>)</kbd><kbd class="op">=</kbd>
              </div>
              <div v-if="showResults" class="ct-cs-result">→ <strong>{{ vkCorrect[4] }} €</strong></div>
            </div>
          </div>
          <div class="ct-casio-tipp">
            💡 <strong>Merke:</strong> Aufschläge (+) = <kbd>×(1+%÷100)</kbd> · Abzüge Einkauf (−) = <kbd>×(1−%÷100)</kbd> · Abzüge Verkauf (÷) = <kbd>÷(1−%÷100)</kbd>
          </div>
          <button @click="showResults=!showResults" class="ct-reveal-btn">{{ showResults ? "🙈 Ergebnisse ausblenden" : "👁 Ergebnisse einblenden" }}</button>
        </div>
      </div>
      <div class="ct-actions">
        <div v-if="vkDone" class="ct-done">🎉 Kalkulation komplett! <strong>+{{ vkScore }}P</strong></div>
        <button class="ct-btn-next" @click="genVk">🔄 Neue Aufgabe</button>
      </div>
    </div>

    <!-- ===== FORMEL-QUIZ ===== -->
    <div v-if="activeType === 'formel'" class="ct-card">
      <div class="fq-header">
        <div>
          <div class="ct-badge">🧠 Aktives Erinnern – Formeln tippen</div>
          <p class="ct-sub">Tippe den fehlenden Teil — so lernst du es wirklich!</p>
        </div>
        <div class="fq-progress">{{ fqMode===4 ? (hgIdx+1)+"/"+hgAllCards.length : (fqIdx+1)+"/"+fqCards.length }}</div>
      </div>
      <div class="fq-modes">
        <button v-for="m in fqModes" :key="m.n" class="fq-mode-btn" :class="fqMode===m.n?'fq-mode-on':''" @click="fqMode=m.n">{{ m.l }}</button>
        <span v-if="fqStreak>=2" class="fq-streak">🔥 {{ fqStreak }}er-Serie!</span>
      </div>
      <div v-if="fqMode !== 4" class="fq-card">
        <div class="fq-cat">{{ fqCards[fqIdx].cat }}</div>
        <div class="fq-step">{{ fqCards[fqIdx].step }}</div>
        <div class="fq-prompt">{{ fqCards[fqIdx].prefix }} <span class="fq-blank">???</span> = {{ fqCards[fqIdx].result }}</div>
        <div class="fq-input-row">
          <input v-model="fqInput" class="ct-input fq-input" placeholder="z.B. ×(1-3÷100)" @keyup.enter="fqCheck" :disabled="fqChecked" />
          <button v-if="!fqChecked" class="ct-btn-ok" @click="fqCheck">✓</button>
        </div>
        <button v-if="fqMode===2 && !fqChecked && !fqHintVisible" class="fq-hint-btn" @click="fqHintVisible=true">💡 Tipp anzeigen</button>
        <div v-if="fqShouldShowHint" class="fq-hint">💡 {{ fqCards[fqIdx].hint }}</div>
        <div v-if="fqChecked" class="fq-result-box" :class="fqCorrect ? 'fq-ok' : 'fq-err'">
          <div>{{ fqCorrect ? '✅ Richtig!' : '❌ Nicht ganz.' }}</div>
          <div class="fq-formula">
            <span class="fq-label">Formel: </span>
            <template v-for="(k,i) in fqCards[fqIdx].keys" :key="i">
              <kbd v-if="k.type==='key'">{{ k.v }}</kbd>
              <span v-else class="fq-op"> {{ k.v }} </span>
            </template>
          </div>
          <div v-if="fqCards[fqIdx].warn" class="fq-warn">⚠️ {{ fqCards[fqIdx].warn }}</div>
        </div>
        <div class="fq-btns">
          <button v-if="fqChecked && !fqCorrect" class="ct-btn-ok" @click="fqRetry">↩ Nochmal</button>
          <button v-if="fqChecked" class="ct-btn-next" @click="fqNext">{{ fqIdx+1 < fqCards.length ? '▶ Nächste' : '🔁 Von vorne' }}</button>
        </div>
      </div>
      <div v-if="fqMode === 4" class="hg-layout">
        <div class="hg-figure">
          <svg viewBox="0 0 100 130" class="hg-svg">
            <line x1="10" y1="125" x2="90" y2="125"/>
            <line x1="25" y1="125" x2="25" y2="5"/>
            <line x1="25" y1="5" x2="65" y2="5"/>
            <line x1="65" y1="5" x2="65" y2="22"/>
            <circle v-if="hgWrong>=1" cx="65" cy="32" r="10"/>
            <line v-if="hgWrong>=2" x1="65" y1="42" x2="65" y2="78"/>
            <line v-if="hgWrong>=3" x1="65" y1="52" x2="45" y2="68"/>
            <line v-if="hgWrong>=4" x1="65" y1="52" x2="85" y2="68"/>
            <line v-if="hgWrong>=5" x1="65" y1="78" x2="45" y2="100"/>
            <line v-if="hgWrong>=6" x1="65" y1="78" x2="85" y2="100"/>
            <line v-if="hgWrong>=7" x1="45" y1="68" x2="35" y2="55"/>
            <line v-if="hgWrong>=8" x1="85" y1="68" x2="95" y2="55"/>
          </svg>
          <div class="hg-lives" :class="hgWrong>=6?'hg-danger':''">
            ❤️ {{ 8-hgWrong }} / 8
          </div>
        </div>
        <div class="hg-game">
          <div class="fq-cat">{{ hgCard.cat }}</div>
          <div class="fq-step">{{ hgCard.name }}</div>
          <div v-if="hgCard.desc" class="hg-desc">{{ hgCard.desc }}</div>
          <div class="hg-formula">
            <template v-for="(p,pi) in hgPartsDisplay" :key="pi">
              <span v-if="p.state==='fixed'" class="hg-fixed">{{ p.display }}</span>
              <span v-else class="hg-blank" :class="'hg-'+p.state">{{ p.display }}</span>
            </template>
          </div>
          <div v-if="hgCard.vars" class="hg-vars">
            <span v-for="va in hgCard.vars" :key="va.k" class="hg-var-item"><b>{{ va.k }}</b> = {{ va.v }}</span>
          </div>
          <div v-if="hgWon" class="fq-result-box fq-ok">🎉 Alle Operatoren richtig!</div>
          <div v-if="hgGameOver&&!hgWon" class="fq-result-box fq-err">💀 Verloren!</div>
          <div class="hg-palette">
            <button v-for="btn in hgBtnDefs" :key="btn.sym"
              class="hg-sym-btn" :class="hgLastWrong===btn.sym?'hg-sym-err':''"
              :disabled="hgGameOver" @click="hgGuess(btn.sym)">
              <span class="hg-btn-sym">{{ btn.sym }}</span>
              <span class="hg-btn-key">{{ btn.key }}</span>
            </button>
          </div>
          <div class="hg-kb-hint">⌨️ */x=× &nbsp; /=÷ &nbsp; +=+ &nbsp; -=− &nbsp; (=( &nbsp; )=)</div>
          <div class="fq-btns">
            <button v-if="hgGameOver" class="ct-btn-ok" @click="hgReset">↩ Nochmal</button>
            <button v-if="hgGameOver" class="ct-btn-next" @click="hgNext">{{ hgIdx+1 < hgAllCards.length ? '▶ Nächste' : '🔁 Von vorne' }}</button>
          </div>
        </div>
      </div>
    </div>

  </div>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import LumiHint from '@/presentation/components/panel/user/ap1/LumiHint.vue'

const emit = defineEmits<{ score: [points: number] }>()

const TYPES = [
  { key: 'bezug',     icon: '📦', label: 'Bezugskalkulation',   pts: '8-13' },
  { key: 'angebot',   icon: '🤝', label: 'Angebotsvergleich',   pts: '15' },
  { key: 'strom',     icon: '⚡', label: 'Stromkosten',          pts: '7-10' },
  { key: 'vorwaerts', icon: '🏷️', label: 'Vorwärtskalkulation', pts: '8-10' },
  { key: 'formel',    icon: '🧠', label: 'Formel-Quiz',           pts: '?' },
]

const activeType = ref<'bezug'|'angebot'|'strom'|'vorwaerts'|'formel'>('bezug')
const showCasio = ref(false)
const showResults = ref(false)

// ============================================================
// FORMEL-QUIZ
// ============================================================
function k(v: string) { return { type: 'key', v } }
function op(v: string) { return { type: 'op', v } }

const fqCards = [
  { cat:'📦 BK', step:'Zieleinkaufspreis', prefix:'LP', result:'Ziel-EKP',
    keys:[k('LP'),op('×'),k('('),k('1'),op('−'),k('R'),op('÷'),k('100'),k(')')],
    accepted:['×(1-','*(1-'],
    hint:'Einkaufsabzug → × (1 − R÷100). Beim Einkauf bleibst du immer bei ×.',
    warn:'' },
  { cat:'📦 BK', step:'Bareinkaufspreis', prefix:'Ziel-EKP', result:'Bar-EKP',
    keys:[k('Ziel'),op('×'),k('('),k('1'),op('−'),k('S'),op('÷'),k('100'),k(')')],
    accepted:['×(1-','*(1-'],
    hint:'Skonto beim Einkauf: ebenfalls × (1 − S÷100).',
    warn:'' },
  { cat:'📦 BK', step:'Bezugspreis', prefix:'Bar-EKP', result:'Bezugspreis',
    keys:[k('Bar'),op('+'),k('Fracht')],
    accepted:['+fracht','+f'],
    hint:'Frachtkosten einfach addieren: Bar-EKP + Fracht.',
    warn:'' },
  { cat:'🏷️ VK', step:'Selbstkostenpreis', prefix:'Bezugspreis', result:'Selbstkosten',
    keys:[k('Bez'),op('×'),k('('),k('1'),op('+'),k('HKZ'),op('÷'),k('100'),k(')')],
    accepted:['×(1+','*(1+'],
    hint:'HKZ ist Aufschlag → × (1+HKZ÷100).',
    warn:'' },
  { cat:'🏷️ VK', step:'Nettoverkaufspreis', prefix:'Selbstkosten', result:'Netto-VKP',
    keys:[k('Selbst'),op('÷'),k('('),k('1'),op('−'),k('G'),op('÷'),k('100'),k(')')],
    accepted:['÷(1-','/(1-'],
    hint:'VK-Abzüge immer ÷. Gewinn/Skonto/Rabatt → ÷ (1−%÷100).',
    warn:'Gewinn: ÷, nicht ×!' },
  { cat:'🏷️ VK', step:'Zielverkaufspreis', prefix:'Netto-VKP', result:'Ziel-VKP',
    keys:[k('Netto'),op('÷'),k('('),k('1'),op('−'),k('S'),op('÷'),k('100'),k(')')],
    accepted:['÷(1-','/(1-'],
    hint:'Skonto im VK: ÷ (1−S÷100). Merke: alle VK-Abzüge sind ÷.',
    warn:'Skonto VK: ÷, nicht ×!' },
  { cat:'🏷️ VK', step:'Bruttoverkaufspreis', prefix:'Ziel-VKP', result:'Brutto-VKP',
    keys:[k('Ziel'),op('÷'),k('('),k('1'),op('−'),k('R'),op('÷'),k('100'),k(')')],
    accepted:['÷(1-','/(1-'],
    hint:'Rabatt im VK: ÷ (1−R÷100). VK-Abzüge sind immer ÷.',
    warn:'Rabatt VK: ÷, nicht ×!' },
  { cat:'🏷️ VK', step:'Bruttopreis (MwSt)', prefix:'Brutto-VKP', result:'Bruttopreis',
    keys:[k('Brutto'),op('×'),k('('),k('1'),op('+'),k('MwSt'),op('÷'),k('100'),k(')')],
    accepted:['×(1+','*(1+'],
    hint:'MwSt ist Aufschlag → × (1+MwSt÷100).',
    warn:'' },
  { cat:'⚡ Strom', step:'Stromkosten berechnen', prefix:'Watt × Stunden', result:'Kosten',
    keys:[k('W'),op('×'),k('h'),op('÷'),k('1000'),op('×'),k('Preis/kWh')],
    accepted:['÷1000','/1000'],
    hint:'Watt ÷ 1000 = kWh. Dann × Stunden × Preis/kWh.',
    warn:'Watt ÷ 1000 = kWh!' },
]

const fqIdx = ref(0)
const fqInput = ref('')
const fqChecked = ref(false)
const fqCorrect = ref(false)
const fqMode = ref(1)
const fqModes = [{n:1,l:'🔰 Einsteiger'},{n:2,l:'📚 Lernend'},{n:3,l:'🎯 Profi'},{n:4,l:'🎯 Operator-Rätsel'}]
const fqHintVisible = ref(false)
const fqStreak = ref(0)
const fqShouldShowHint = computed(() =>
  (fqMode.value === 1 && fqChecked.value && !fqCorrect.value) ||
  (fqMode.value === 2 && fqHintVisible.value)
)

function fqCheck() {
  if (!fqInput.value.trim()) return
  const norm = fqInput.value.replace(/\s/g,'').toLowerCase()
  fqCorrect.value = fqCards[fqIdx.value].accepted.some((a: string) => norm.includes(a.toLowerCase()))
  fqChecked.value = true
  if (fqCorrect.value) fqStreak.value++; else fqStreak.value = 0
}
function fqRetry() { fqInput.value = ''; fqChecked.value = false; fqHintVisible.value = false }
function fqNext() { fqIdx.value = (fqIdx.value + 1) % fqCards.length; fqInput.value = ''; fqChecked.value = false; fqHintVisible.value = false }

// ============ GALGEN-QUIZ ============
function hf(v: string) { return { type: 'fixed' as const, v } }
function hb(v: string) { return { type: 'blank' as const, v } }
const hgAllCards = [
  { cat:'📦 BK', name:'Zieleinkaufspreis', desc:'Listenpreis abzgl. Rabatt → was du angestrebt zahlen sollst', vars:[{k:'LP',v:'Listenpreis'},{k:'R',v:'Rabatt %'}],
    parts:[hf('LP'),hb('×'),hb('('),hf('1'),hb('−'),hf('R'),hb('÷'),hf('100'),hb(')'),hf('= Ziel-EKP')] },
  { cat:'📦 BK', name:'Bareinkaufspreis', desc:'Zieleinkaufspreis abzgl. Skonto → Preis bei Barzahlung', vars:[{k:'S',v:'Skonto %'}],
    parts:[hf('Ziel-EKP'),hb('×'),hb('('),hf('1'),hb('−'),hf('S'),hb('÷'),hf('100'),hb(')'),hf('= Bar-EKP')] },
  { cat:'📦 BK', name:'Bezugspreis', desc:'Bar-EKP plus Frachtkosten → was dich die Ware wirklich kostet', vars:[{k:'Fracht',v:'Bezugskosten'}],
    parts:[hf('Bar-EKP'),hb('+'),hf('Fracht = Bezugspreis')] },
  { cat:'🏷️ VK', name:'Selbstkostenpreis', desc:'Bezugspreis plus Handlungskosten (Miete, Löhne etc.) → deine gesamten Kosten', vars:[{k:'HKZ',v:'Handlungskostenzuschl. %'}],
    parts:[hf('Bezugspreis'),hb('×'),hb('('),hf('1'),hb('+'),hf('HKZ'),hb('÷'),hf('100'),hb(')'),hf('= Selbstkosten')] },
  { cat:'🏷️ VK', name:'Netto-VKP', desc:'Selbstkosten plus Gewinn → Mindestpreis um Gewinn zu machen', vars:[{k:'G',v:'Gewinn %'}],
    parts:[hf('Selbstkosten'),hb('÷'),hb('('),hf('1'),hb('−'),hf('G'),hb('÷'),hf('100'),hb(')'),hf('= Netto-VKP')] },
  { cat:'🏷️ VK', name:'Ziel-VKP', desc:'Netto-VKP aufgeschlagen für Skonto → Preis bei Zahlungsziel', vars:[{k:'S',v:'Skonto %'}],
    parts:[hf('Netto-VKP'),hb('÷'),hb('('),hf('1'),hb('−'),hf('S'),hb('÷'),hf('100'),hb(')'),hf('= Ziel-VKP')] },
  { cat:'🏷️ VK', name:'Brutto-VKP', desc:'Ziel-VKP aufgeschlagen für Rabatt → ausgezeichneter Preis im Laden', vars:[{k:'R',v:'Rabatt %'}],
    parts:[hf('Ziel-VKP'),hb('÷'),hb('('),hf('1'),hb('−'),hf('R'),hb('÷'),hf('100'),hb(')'),hf('= Brutto-VKP')] },
  { cat:'🏷️ VK', name:'Bruttopreis (MwSt)', desc:'Brutto-VKP plus Mehrwertsteuer → Endpreis den der Kunde zahlt', vars:[{k:'MwSt',v:'Mehrwertsteuer %'}],
    parts:[hf('Brutto-VKP'),hb('×'),hb('('),hf('1'),hb('+'),hf('MwSt'),hb('÷'),hf('100'),hb(')'),hf('= Bruttopreis')] },
]
const hgIdx = ref(0)
const hgWrong = ref(0)
const hgFilled = ref<string[]>([])
const hgLastWrong = ref('')
const hgCard = computed(() => hgAllCards[hgIdx.value])
const hgBlanks = computed(() =>
  hgCard.value.parts.filter(p => p.type === 'blank').map(p => p.v))
const hgWon = computed(() => hgFilled.value.length === hgBlanks.value.length)
const hgGameOver = computed(() => hgWon.value || hgWrong.value >= 8)
const hgPartsDisplay = computed(() => {
  let bi = 0
  return hgCard.value.parts.map(p => {
    if (p.type === 'fixed') return { state: 'fixed', display: p.v }
    const idx = bi++
    if (idx < hgFilled.value.length) return { state: 'ok', display: p.v }
    if (idx === hgFilled.value.length)
      return { state: 'active', display: hgGameOver.value ? p.v : '?' }
    return { state: 'future', display: hgGameOver.value ? p.v : '_' }
  })
})
function hgGuess(sym: string) {
  if (hgGameOver.value) return
  if (sym === hgBlanks.value[hgFilled.value.length]) {
    hgFilled.value = [...hgFilled.value, sym]; hgLastWrong.value = ''
  } else {
    hgWrong.value++; hgLastWrong.value = sym
    setTimeout(() => { hgLastWrong.value = '' }, 500)
  }
}
const hgBtnDefs = [
  { sym: '×', key: '*' },
  { sym: '÷', key: '/' },
  { sym: '+', key: '+' },
  { sym: '−', key: '-' },
  { sym: '(', key: '(' },
  { sym: ')', key: ')' },
]
const hgKeyMap = { x:'×', X:'×', '*':'×', '/':'÷', '+':'+', '-':'−', '(':'(', ')':')' }
function hgKeyDown(e) {
  if (hgGameOver.value) return
  const sym = hgKeyMap[e.key]
  if (sym) { e.preventDefault(); hgGuess(sym) }
}
onMounted(() => window.addEventListener('keydown', hgKeyDown))
onUnmounted(() => window.removeEventListener('keydown', hgKeyDown))

function hgReset() { hgWrong.value=0; hgFilled.value=[]; hgLastWrong.value='' }
function hgNext() { hgIdx.value=(hgIdx.value+1)%hgAllCards.length; hgReset() }



const lumiCtx = computed(() => {
  if (activeType.value === 'bezug')
    return `Bezugskalkulation: Listenpreis ${bk.value.list}€, Rabatt ${bk.value.rabatt}%, Skonto ${bk.value.skonto}%, Fracht ${bk.value.fracht}€`
  if (activeType.value === 'angebot')
    return `Angebotsvergleich A: ${av.value.a.list}€ (${av.value.a.rabatt}%/${av.value.a.skonto}%/+${av.value.a.fracht}€) vs B: ${av.value.b.list}€ (${av.value.b.rabatt}%/${av.value.b.skonto}%/+${av.value.b.fracht}€)`
  if (activeType.value === 'strom')
    return `Stromkosten: ${sk.value.geraete.map(g=>g.name+' '+g.watt+'W').join(', ')}, Preis ${sk.value.preis}€/kWh`
  return `Vorwärtskalkulation: Bezugspreis ${vk.value.bezug}€, HKZ ${vk.value.hkz}%, Gewinn ${vk.value.gewinn}%, Skonto ${vk.value.skonto}%, Rabatt ${vk.value.rabatt}%, MwSt ${vk.value.mwst}%`
})

function switchType(k: typeof activeType.value) {
  activeType.value = k
  showCasio.value = false
}

function fmt(n: number) { return n.toFixed(2) }
function r2(n: number) { return Math.round(n * 100) / 100 }

// ============================================================
// BEZUGSKALKULATION
// ============================================================
const PRODUCTS = ['Laptop Dell Latitude','Switch Cisco C2960','Server HPE ProLiant','USV APC Smart',
  'Drucker HP LaserJet','AP Cisco Aironet','Rack Netzwerkschrank','Firewall Fortinet']

const bk = ref({ product:'', qty:1, list:1000, rabatt:10, skonto:3, fracht:15 })
const bkAns = ref<(number|null)[]>([null,null,null,null])
const bkState = ref<('idle'|'ok'|'err')[]>(['idle','idle','idle','idle'])

const bkCorrect = computed(() => {
  const ziel = r2(bk.value.list * (1 - bk.value.rabatt/100))
  const bar  = r2(ziel * (1 - bk.value.skonto/100))
  const bez  = r2(bar + bk.value.fracht)
  return [ziel.toFixed(2), bar.toFixed(2), bez.toFixed(2)]
})
const bkSteps = [
  { label:'Zieleinkaufspreis (nach Rabatt)',  ph:'0.00' },
  { label:'Bareinkaufspreis (nach Skonto)',   ph:'0.00' },
  { label:'Bezugspreis (inkl. Frachtkosten)', ph:'0.00' },
]
const bkDone  = computed(() => bkState.value.every(s => s === 'ok'))
const bkScore = computed(() => bkState.value.filter(s => s === 'ok').length * 4)

function checkBk(i: number) {
  const val = bkAns.value[i]
  if (val === null) return
  bkState.value[i] = Math.abs(Number(val) - Number(bkCorrect.value[i])) < 0.06 ? 'ok' : 'err'
  if (bkState.value[i] === 'ok') emit('score', 4)
}
function genBk() {
  bk.value = {
    product: PRODUCTS[Math.floor(Math.random()*PRODUCTS.length)],
    qty:    [1,2,3,5,10][Math.floor(Math.random()*5)],
    list:   [800,1000,1200,1500,2000,2500,3000][Math.floor(Math.random()*7)],
    rabatt: [5,8,10,12,15,20][Math.floor(Math.random()*6)],
    skonto: [2,3,5][Math.floor(Math.random()*3)],
    fracht: [0,10,15,20,25,30,50][Math.floor(Math.random()*7)],
  }
  bkAns.value = [null,null,null]
  bkState.value = ['idle','idle','idle']
  showCasio.value = false
  showResults.value = false
}
genBk()

// ============================================================
// ANGEBOTSVERGLEICH
// ============================================================
const SUP_A = ['Topsicherheit AG','ComTec GmbH','DataNet KG','TechWorld AG']
const SUP_B = ['Heikvision GmbH','Alpha IT GmbH','NetVision KG','CyberSupply AG']
const AV_PROD = ['Videoüberwachungssystem','WLAN-Infrastruktur (10 APs)','Server-Bundle','Netzwerk-Switches (5×)']

const av = ref({ product:'', a:{ name:'',list:0,rabatt:0,skonto:0,fracht:0 }, b:{ name:'',list:0,rabatt:0,skonto:0,fracht:0 } })
const avAnsA = ref<(number|null)[]>([null,null,null,null])
const avAnsB = ref<(number|null)[]>([null,null,null,null])
const avStateA = ref<('idle'|'ok'|'err')[]>(['idle','idle','idle','idle'])
const avStateB = ref<('idle'|'ok'|'err')[]>(['idle','idle','idle','idle'])
const avChoice = ref<'A'|'B'|null>(null)
const avChoiceChecked = ref(false)
const avStufe = ref(1)
const avStufen = [
  {n:1,l:'🥉 Stufe 1 – Felder sichtbar'},
  {n:2,l:'🥈 Stufe 2 – Felder benennen'},
  {n:3,l:'🥇 Stufe 3 – Alles auswendig'},
]
const avRowDefs = [
  { label:'Listenpreis',        acc:['listenpreis','lp'] },
  { label:'Zieleinkaufspreis',  acc:['zieleinkaufspreis','ziel-ekp','zielekp','ziel'] },
  { label:'Bareinkaufspreis',   acc:['bareinkaufspreis','bar-ekp','barekp','bar'] },
  { label:'Bezugspreis',        acc:['bezugspreis','bezug'] },
]
const avLabelInputs = ref(['','','',''])
const avLabelOk = computed(() =>
  avRowDefs.map((r,i) => avStufe.value===1 ||
    r.acc.some(a => avLabelInputs.value[i].trim().toLowerCase().includes(a))))


const avCorrectA = computed(() => {
  const a = av.value.a
  const ziel = r2(a.list*(1-a.rabatt/100))
  const bar  = r2(ziel*(1-a.skonto/100))
  const bez  = r2(bar+a.fracht)
  return [a.list.toFixed(2), ziel.toFixed(2), bar.toFixed(2), bez.toFixed(2)]
})
const avCorrectB = computed(() => {
  const b = av.value.b
  const ziel = r2(b.list*(1-b.rabatt/100))
  const bar  = r2(ziel*(1-b.skonto/100))
  const bez  = r2(bar+b.fracht)
  return [b.list.toFixed(2), ziel.toFixed(2), bar.toFixed(2), bez.toFixed(2)]
})
const avWinner      = computed(() => Number(avCorrectA.value[2]) <= Number(avCorrectB.value[2]) ? 'A' : 'B')
const avWinnerName  = computed(() => avWinner.value === 'A' ? av.value.a.name : av.value.b.name)
const avWinnerPrice = computed(() => avWinner.value === 'A' ? avCorrectA.value[3] : avCorrectB.value[3])
const avBothDone    = computed(() => avStateA.value[3] !== 'idle' && avStateB.value[3] !== 'idle')
const avChoiceCorrect = computed(() => avChoice.value === avWinner.value)

function checkAv(offer: 'A'|'B', i: number) {
  const ans = offer==='A' ? avAnsA : avAnsB
  const st  = offer==='A' ? avStateA : avStateB
  const cor = offer==='A' ? avCorrectA : avCorrectB
  const val = ans.value[i]; if (val===null) return
  st.value[i] = Math.abs(Number(val)-Number(cor.value[i]))<0.06?'ok':'err'
  if (st.value[i]==='ok') emit('score',3)
}

function checkAvChoice() {
  avChoiceChecked.value = true
  if (avChoiceCorrect.value) emit('score',5)
}
function genAv() {
  const base = [5000,8000,10000,12000,15000][Math.floor(Math.random()*5)]
  av.value = {
    product: AV_PROD[Math.floor(Math.random()*AV_PROD.length)],
    a:{ name:SUP_A[Math.floor(Math.random()*SUP_A.length)], list:base+Math.floor(Math.random()*500), rabatt:[3,5,8,10][Math.floor(Math.random()*4)], skonto:[2,3][Math.floor(Math.random()*2)], fracht:[0,0,50,100][Math.floor(Math.random()*4)] },
    b:{ name:SUP_B[Math.floor(Math.random()*SUP_B.length)], list:base+Math.floor(Math.random()*500), rabatt:[5,8,10,12][Math.floor(Math.random()*4)], skonto:[2,3,5][Math.floor(Math.random()*3)], fracht:[0,50,70,100][Math.floor(Math.random()*4)] },
  }
  avAnsA.value=[null,null,null,null]; avAnsB.value=[null,null,null,null]
  avStateA.value=['idle','idle','idle','idle']; avStateB.value=['idle','idle','idle','idle']
  avLabelInputs.value=['','','','']; avStufe.value=avStufe.value
  avChoice.value=null; avChoiceChecked.value=false; showCasio.value=false
  showResults.value=false
}
genAv()

// ============================================================
// STROMKOSTEN
// ============================================================
const SK_ALL = [
  { name:'PC mit Bildschirm', watt:150, stunden:8,  tage:220 },
  { name:'Laptop',            watt:65,  stunden:8,  tage:220 },
  { name:'Server',            watt:200, stunden:24, tage:365 },
  { name:'Switch',            watt:30,  stunden:24, tage:365 },
  { name:'Router',            watt:20,  stunden:24, tage:365 },
  { name:'Firewall',          watt:25,  stunden:24, tage:365 },
  { name:'Drucker',           watt:40,  stunden:8,  tage:220 },
  { name:'NAS-Server',        watt:80,  stunden:24, tage:365 },
]
const SK_PREISE = [0.28,0.32,0.35,0.40,0.45]

const sk = ref({ geraete: SK_ALL.slice(0,2), preis:0.35 })
const skAns   = ref<(number|null)[]>([null,null,null,null,null])
const skState = ref<('idle'|'ok'|'err')[]>(['idle','idle','idle','idle','idle','idle'])

const skCorrect = computed(() => {
  const res: string[] = []; let total = 0
  for (const g of sk.value.geraete) {
    const kwh  = r2(g.watt * g.stunden * g.tage / 1000)
    const cost = r2(kwh * sk.value.preis)
    res.push(kwh.toFixed(2), cost.toFixed(2))
    total += cost
  }
  res.push(r2(total).toFixed(2))
  return res
})
const skDone  = computed(() => skState.value.slice(0, sk.value.geraete.length*2+1).every(s=>s==='ok'))
const skScore = computed(() => skState.value.filter(s=>s==='ok').length * 3)

function checkSk(idx: number) {
  const val = skAns.value[idx]; if (val===null) return
  skState.value[idx] = Math.abs(Number(val)-Number(skCorrect.value[idx]))<1?'ok':'err'
  if (skState.value[idx]==='ok') emit('score',3)
}
function checkSkTotal() {
  const ti = sk.value.geraete.length*2
  const val = skAns.value[ti]; if (val===null) return
  skState.value[ti] = Math.abs(Number(val)-Number(skCorrect.value[ti]))<2?'ok':'err'
  if (skState.value[ti]==='ok') emit('score',5)
}
function genSk() {
  const n = [2,3][Math.floor(Math.random()*2)]
  const shuffled = [...SK_ALL].sort(()=>Math.random()-0.5)
  sk.value = {
    geraete: shuffled.slice(0,n).map(g=>({ ...g, watt:g.watt+(Math.floor(Math.random()*5)-2)*10 })),
    preis: SK_PREISE[Math.floor(Math.random()*SK_PREISE.length)],
  }
  const len = sk.value.geraete.length*2+1
  skAns.value   = new Array(len).fill(null)
  skState.value = new Array(len).fill('idle')
  showCasio.value = false
  showResults.value = false
}
genSk()

// ============================================================
// VORWÄRTSKALKULATION
// ============================================================
const VK_PRODS = ['WLAN-Accesspoint','Managed Switch','USV-Anlage','NAS-System','Firewall-Appliance']
const vk = ref({ product:'', bezug:100, hkz:25, gewinn:15, skonto:3, rabatt:10, mwst:19 })

const vkSteps = [
  { label:'Selbstkostenpreis (+HKZ)',             ph:'0.00' },
  { label:'Barverkaufspreis (+Gewinn)',            ph:'0.00' },
  { label:'Zielverkaufspreis (÷ Skonto)',          ph:'0.00' },
  { label:'Listenverkaufspreis netto (÷ Rabatt)', ph:'0.00' },
  { label:'Listenverkaufspreis brutto (+MwSt)',   ph:'0.00' },
]
const vkAns   = ref<(number|null)[]>([null,null,null,null,null])
const vkState = ref<('idle'|'ok'|'err')[]>(['idle','idle','idle','idle','idle','idle'])

const vkCorrect = computed(() => {
  const v = vk.value
  const sk_ = r2(v.bezug  * (1 + v.hkz   /100))
  const bvk = r2(sk_      * (1 + v.gewinn /100))
  const zvk = r2(bvk      / (1 - v.skonto /100))
  const lvn = r2(zvk      / (1 - v.rabatt /100))
  const lvb = r2(lvn      * (1 + v.mwst   /100))
  return [sk_.toFixed(2), bvk.toFixed(2), zvk.toFixed(2), lvn.toFixed(2), lvb.toFixed(2)]
})
const vkDone  = computed(() => vkState.value.every(s=>s==='ok'))
const vkScore = computed(() => vkState.value.filter(s=>s==='ok').length*3)

function checkVk(i: number) {
  const val = vkAns.value[i]; if (val===null) return
  vkState.value[i] = Math.abs(Number(val)-Number(vkCorrect.value[i]))<0.06?'ok':'err'
  if (vkState.value[i]==='ok') emit('score',3)
}
function genVk() {
  vk.value = {
    product: VK_PRODS[Math.floor(Math.random()*VK_PRODS.length)],
    bezug:  [80,100,120,150,200,250,300][Math.floor(Math.random()*7)],
    hkz:    [20,25,30,35][Math.floor(Math.random()*4)],
    gewinn: [10,12,15,20][Math.floor(Math.random()*4)],
    skonto: [2,3,5][Math.floor(Math.random()*3)],
    rabatt: [10,15,20][Math.floor(Math.random()*3)],
    mwst:   19,
  }
  vkAns.value=['null','null','null','null','null'].map(()=>null) as (number|null)[]
  vkState.value=['idle','idle','idle','idle','idle']
  showCasio.value=false
  showResults.value=false
}
genVk()
</script>

<style scoped>
.ct-wrap{max-width:880px}
.ct-header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px;gap:12px}
.ct-title{font-size:22px;font-weight:900;color:var(--color-text-primary);margin:0 0 4px;letter-spacing:-0.3px}
.ct-sub{font-size:13px;color:var(--color-text-secondary);margin:0}
.ct-tabs{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}
.ct-tab{padding:8px 18px;border-radius:22px;font-size:13px;font-weight:700;border:1.5px solid var(--color-border);background:var(--color-surface);color:var(--color-text-secondary);cursor:pointer;transition:all 0.18s;display:flex;align-items:center;gap:7px}
.ct-tab:hover{border-color:#f59e0b;color:#fbbf24;background:rgba(245,158,11,0.07);transform:translateY(-1px)}
.ct-tab-on{background:linear-gradient(135deg,rgba(245,158,11,0.18),rgba(251,191,36,0.08))!important;border-color:#f59e0b!important;color:#fbbf24!important;box-shadow:0 0 0 3px rgba(245,158,11,0.12),0 2px 8px rgba(245,158,11,0.15)!important}
.ct-pts{font-size:11px;background:rgba(255,255,255,0.12);padding:2px 7px;border-radius:10px;font-weight:800}
.ct-card{background:var(--color-surface);border:1px solid var(--color-border);border-radius:18px;padding:22px;display:flex;flex-direction:column;gap:18px;box-shadow:0 4px 24px rgba(0,0,0,0.15)}
.ct-badge{display:inline-block;padding:4px 14px;border-radius:20px;font-size:12px;font-weight:800;background:linear-gradient(90deg,rgba(245,158,11,0.2),rgba(251,191,36,0.1));color:#fbbf24;border:1px solid rgba(245,158,11,0.3);margin-bottom:10px;letter-spacing:0.3px}
.ct-scenario{display:flex;flex-direction:column}
.ct-scenario-text{color:var(--color-text-primary);margin:0 0 12px;line-height:1.7}
.ct-question{font-size:15px;font-weight:800;color:#fbbf24;margin:12px 0 0}
.ct-data-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px 20px}
.ct-row{display:flex;justify-content:space-between;align-items:center;padding:6px 12px;background:rgba(255,255,255,0.04);border-radius:8px;font-size:13px;border:1px solid transparent;transition:border-color 0.15s}
.ct-row:hover{border-color:rgba(99,102,241,0.2)}
.ct-row span{color:var(--color-text-secondary)}
.ct-row strong{color:var(--color-text-primary);font-weight:700}
.ct-formula-hint{padding:11px 15px;background:rgba(14,165,233,0.07);border:1px solid rgba(14,165,233,0.2);border-radius:10px;font-size:13px;color:#7dd3fc;font-style:italic;border-left:3px solid rgba(14,165,233,0.5)}
.ct-inputs{display:flex;flex-direction:column;gap:10px}
.ct-input-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 14px;border-radius:12px;border:1.5px solid rgba(255,255,255,0.06);transition:all 0.22s;background:rgba(255,255,255,0.025)}
.ct-input-row:focus-within{border-color:rgba(245,158,11,0.35);background:rgba(245,158,11,0.03)}
.row-ok{border-color:rgba(34,197,94,0.45)!important;background:rgba(34,197,94,0.06)!important;box-shadow:0 0 0 2px rgba(34,197,94,0.1)!important}
.row-err{border-color:rgba(239,68,68,0.45)!important;background:rgba(239,68,68,0.06)!important;box-shadow:0 0 0 2px rgba(239,68,68,0.1)!important}
.ct-label{font-size:13px;font-weight:600;color:var(--color-text-secondary);min-width:220px}
.ct-input-wrap{display:flex;align-items:center;gap:4px;flex:1;min-width:120px;max-width:200px}
.ct-input{width:100%;padding:9px 11px;border:2px solid var(--color-border);border-radius:9px;background:var(--color-surface);color:var(--color-text-primary);font-size:14px;font-family:monospace;font-weight:700;outline:none;transition:all 0.18s}
.ct-input:focus{border-color:#f59e0b;background:rgba(245,158,11,0.04);box-shadow:0 0 0 3px rgba(245,158,11,0.1)}
.ct-input:disabled{opacity:0.6;cursor:not-allowed}
.ct-unit{font-size:13px;font-weight:800;color:var(--color-text-secondary);flex-shrink:0}
.ct-btn-ok{padding:7px 14px;background:linear-gradient(135deg,#16a34a,#15803d);color:white;border:none;border-radius:8px;font-size:13px;font-weight:800;cursor:pointer;flex-shrink:0;transition:all 0.15s;box-shadow:0 2px 8px rgba(22,163,74,0.3)}
.ct-btn-ok:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(22,163,74,0.4)}
.ct-tick{font-size:20px;flex-shrink:0}
.ct-err-hint{font-size:12px;font-weight:700;color:#f87171;width:100%;padding-left:4px}
.ct-two-offers{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:4px}
.ct-offer{padding:14px;background:rgba(255,255,255,0.03);border:1px solid var(--color-border);border-radius:12px;transition:border-color 0.15s}
.ct-offer:hover{border-color:rgba(125,211,252,0.3)}
.ct-offer-name{font-size:13px;font-weight:800;color:#7dd3fc;margin-bottom:10px}
.ct-two-inputs{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.ct-offer-calc{display:flex;flex-direction:column;gap:8px;padding:14px;background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid var(--color-border)}
.ct-offer-calc-title{font-size:14px;font-weight:800;color:#7dd3fc;margin-bottom:4px}
.ct-winner-choice{padding:16px;background:rgba(245,158,11,0.07);border-radius:12px;border:1px solid rgba(245,158,11,0.25)}
.ct-choice-btns{display:flex;gap:10px;margin-top:10px;flex-wrap:wrap}
.ct-choice-btn{padding:9px 22px;border-radius:10px;border:2px solid var(--color-border);background:var(--color-surface);color:var(--color-text-primary);cursor:pointer;font-weight:700;font-size:14px;transition:all 0.15s}
.ct-choice-btn:hover{border-color:#f59e0b;transform:translateY(-1px)}
.ct-choice-on{border-color:#f59e0b!important;background:rgba(245,158,11,0.15)!important;color:#fbbf24!important;box-shadow:0 0 0 3px rgba(245,158,11,0.12)!important}
.ct-strom-table{border:1px solid var(--color-border);border-radius:10px;overflow:hidden;margin-top:8px}
.ct-strom-header{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;padding:8px 14px;background:rgba(99,102,241,0.1);font-weight:800;color:var(--color-text-secondary);font-size:11px}
.ct-strom-row{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;padding:8px 14px;border-top:1px solid var(--color-border);color:var(--color-text-primary)}
.ct-strom-row:nth-child(even){background:rgba(255,255,255,0.02)}
.ct-strom-label{font-size:13px;font-weight:700;color:#7dd3fc;margin:12px 0 4px}
.ct-total-row{border-top:2px solid rgba(245,158,11,0.35)!important;font-weight:700}
.ct-casio-box{margin-top:6px}
.ct-casio-toggle{width:100%;padding:11px 18px;border-radius:12px;cursor:pointer;background:linear-gradient(135deg,rgba(14,165,233,0.1),rgba(6,182,212,0.06));border:1.5px solid rgba(14,165,233,0.35);color:#38bdf8;font-weight:800;font-size:14px;text-align:left;transition:all 0.18s;display:flex;align-items:center;gap:8px}
.ct-casio-toggle:hover{background:rgba(14,165,233,0.18);border-color:rgba(14,165,233,0.6);transform:translateY(-1px)}
.ct-casio-panel{margin-top:12px;padding:18px;background:linear-gradient(160deg,rgba(2,8,23,0.9),rgba(5,15,30,0.85));border:1px solid rgba(14,165,233,0.3);border-radius:14px;display:flex;flex-direction:column;gap:16px}
.ct-casio-intro{font-size:13px;color:#7dd3fc;font-style:italic}
.ct-casio-step{display:flex;gap:14px;align-items:flex-start;padding:10px 12px;border-radius:10px;background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06)}
.ct-cs-num{font-size:20px;flex-shrink:0;line-height:1.3}
.ct-cs-body{display:flex;flex-direction:column;gap:7px;flex:1}
.ct-cs-label{font-size:13px;font-weight:800;color:#e0f2fe}
.ct-cs-keys{display:flex;flex-wrap:wrap;align-items:center;gap:4px}
.ct-cs-save{display:inline-flex;align-items:center;gap:3px;margin-left:8px}
.ct-cs-result{font-size:13px;color:#a5f3fc;display:flex;align-items:center;flex-wrap:wrap;gap:4px}
kbd{display:inline-flex;align-items:center;justify-content:center;padding:4px 9px;border-radius:6px;font-size:13px;font-family:monospace;font-weight:800;background:#1e3a5f;color:#93c5fd;border:1px solid #2563eb;border-bottom:3px solid #1d4ed8;min-width:30px}
kbd.op{background:#1a2a1a;color:#86efac;border-color:#16a34a;border-bottom-color:#15803d;min-width:24px}
kbd.ans{background:#4c1d95;color:#c4b5fd;border-color:#7c3aed}
kbd.shift{background:#78350f;color:#fde68a;border-color:#d97706}
.ct-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-top:4px}
.ct-done{padding:9px 18px;border-radius:10px;font-size:14px;font-weight:800;background:rgba(34,197,94,0.12);color:#4ade80;border:1px solid rgba(34,197,94,0.35)}
.ct-done-err{background:rgba(239,68,68,0.1)!important;color:#f87171!important}
.ct-btn-next{padding:10px 24px;background:rgba(14,165,233,0.15);color:#38bdf8;border:1.5px solid rgba(14,165,233,0.45);border-radius:10px;font-weight:800;font-size:14px;cursor:pointer;transition:all 0.18s}
.ct-btn-next:hover{background:rgba(14,165,233,0.25);transform:translateY(-1px)}
/* ---- FORMEL-QUIZ ---- */
.fq-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem; }
.fq-progress { font-size:.85rem; color:var(--c-muted); background:rgba(99,102,241,.12); padding:.25rem .7rem; border-radius:1rem; }
.fq-card { background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.08); border-radius:1rem; padding:1.5rem; }
.fq-cat { font-size:.75rem; font-weight:700; letter-spacing:.08em; color:var(--c-accent); text-transform:uppercase; margin-bottom:.4rem; }
.fq-step { font-size:1.15rem; font-weight:600; margin-bottom:.8rem; }
.fq-prompt { font-size:1rem; color:var(--c-muted); margin-bottom:1rem; }
.fq-blank { background:rgba(99,102,241,.2); color:#a5b4fc; border-radius:.3rem; padding:.1em .4em; font-weight:700; }
.fq-input-row { display:flex; gap:.5rem; align-items:center; }
.fq-input { flex:1; }
.fq-result-box { margin-top:1rem; padding:1rem; border-radius:.75rem; font-size:.95rem; display:flex; flex-direction:column; gap:.4rem; }
.fq-ok { background:rgba(34,197,94,.12); border:1px solid rgba(34,197,94,.3); color:#86efac; }
.fq-err { background:rgba(239,68,68,.1); border:1px solid rgba(239,68,68,.25); color:#fca5a5; }
.fq-formula { display:flex; flex-wrap:wrap; align-items:center; gap:.25rem; margin-top:.3rem; }
.fq-label { font-size:.8rem; color:var(--c-muted); margin-right:.25rem; }
.fq-op { color:var(--c-muted); font-size:.9rem; padding:0 .1rem; }
.fq-warn { font-size:.85rem; color:#fbbf24; margin-top:.3rem; }
.fq-btns { display:flex; gap:.75rem; margin-top:1rem; justify-content:flex-end; }

.fq-modes { display:flex; gap:.5rem; flex-wrap:wrap; align-items:center; margin-top:.75rem; }
.fq-mode-btn { font-size:.8rem; padding:.3rem .75rem; border-radius:1rem; border:1px solid rgba(255,255,255,.15); background:transparent; color:var(--c-muted); cursor:pointer; transition:all .2s; }
.fq-mode-btn:hover { border-color:rgba(99,102,241,.5); color:#fff; }
.fq-mode-on { background:rgba(99,102,241,.25); border-color:rgba(99,102,241,.6); color:#a5b4fc; font-weight:600; }
.fq-streak { font-size:.85rem; color:#fbbf24; font-weight:700; margin-left:.5rem; }
.fq-hint { margin-top:.75rem; padding:.75rem 1rem; background:rgba(251,191,36,.08); border:1px solid rgba(251,191,36,.25); border-radius:.6rem; font-size:.9rem; color:#fde68a; }
.fq-hint-btn { margin-top:.5rem; font-size:.85rem; padding:.35rem .8rem; border-radius:.5rem; border:1px dashed rgba(251,191,36,.4); background:transparent; color:#fbbf24; cursor:pointer; }
.fq-hint-btn:hover { background:rgba(251,191,36,.1); }
/* ---- GALGEN ---- */
.hg-layout { display:flex; gap:1.5rem; align-items:flex-start; flex-wrap:wrap; margin-top:.75rem; }
.hg-figure { flex:0 0 120px; display:flex; flex-direction:column; align-items:center; }
.hg-svg { width:120px; height:150px; stroke:#818cf8; stroke-width:3.5; fill:none; stroke-linecap:round; }
.hg-lives { font-size:.9rem; margin-top:.4rem; font-weight:600; }
.hg-danger { color:#f87171; }
.hg-game { flex:1; min-width:180px; }
.hg-formula { display:flex; flex-wrap:wrap; gap:.35rem; align-items:center; margin:1rem 0 1.25rem; }
.hg-fixed { font-size:1.05rem; color:#cbd5e1; }
.hg-blank { font-size:1.2rem; font-weight:700; min-width:1.8rem; text-align:center; padding:.2rem .5rem; border-radius:.4rem; border-bottom:2px solid rgba(99,102,241,.4); transition:all .3s; }
.hg-ok { background:rgba(34,197,94,.15); color:#86efac !important; border-color:#86efac; }
.hg-active { background:rgba(99,102,241,.2); color:#a5b4fc !important; border-color:#818cf8; animation:hg-pulse 1.2s infinite; }
.hg-future { color:#475569 !important; border-color:rgba(255,255,255,.08); }
@keyframes hg-pulse { 0%,100%{box-shadow:0 0 0 0 rgba(99,102,241,.5)} 50%{box-shadow:0 0 0 8px rgba(99,102,241,0)} }
.hg-palette { display:flex; gap:.6rem; flex-wrap:wrap; margin-top:.5rem; }
.hg-sym-btn { font-size:1.4rem; width:3.8rem; height:3.8rem; border-radius:.6rem; border:2px solid rgba(255,255,255,.2); background:rgba(255,255,255,.05); cursor:pointer; color:#e2e8f0; transition:all .2s; font-weight:700; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.05rem; padding:0; }
.hg-btn-sym { font-size:1.3rem; font-weight:700; line-height:1; }
.hg-btn-key { font-size:.6rem; color:#94a3b8; font-weight:400; line-height:1; }
.hg-kb-hint { font-size:.72rem; color:#94a3b8; margin-top:.4rem; letter-spacing:.03em; }
.hg-desc { font-size:.8rem; color:#94a3b8; margin:.1rem 0 .5rem; font-style:italic; line-height:1.4; }
.hg-vars { display:flex; flex-wrap:wrap; gap:.3rem .7rem; margin:.4rem 0 .2rem; padding:.35rem .6rem; background:rgba(99,102,241,.08); border-radius:.4rem; border:1px solid rgba(99,102,241,.2); }
.hg-var-item { font-size:.75rem; color:#cbd5e1; } .hg-var-item b { color:#a5b4fc; font-weight:600; }
.hg-sym-btn:hover:not(:disabled) { border-color:#818cf8; background:rgba(99,102,241,.2); transform:translateY(-2px); }
.hg-sym-btn:disabled { opacity:.4; cursor:not-allowed; }
.hg-sym-err { border-color:#f87171 !important; background:rgba(239,68,68,.15) !important; color:#fca5a5 !important; animation:hg-shake .4s; }
@keyframes hg-shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-5px)} 75%{transform:translateX(5px)} }

/* ---- AV-TABLE STUFEN ---- */
.av-stufe-row { display:flex; gap:.5rem; flex-wrap:wrap; margin-bottom:1rem; }
.av-stufe-btn { font-size:.8rem; padding:.35rem .85rem; border-radius:1rem; border:1px solid rgba(255,255,255,.15); background:transparent; color:var(--c-muted); cursor:pointer; transition:all .2s; }
.av-stufe-btn:hover { border-color:rgba(99,102,241,.5); color:#fff; }
.av-stufe-on { background:rgba(99,102,241,.25); border-color:rgba(99,102,241,.6); color:#a5b4fc; font-weight:600; }
.av-stufe3-hint { font-size:.85rem; color:#fde68a; background:rgba(251,191,36,.08); border:1px solid rgba(251,191,36,.2); border-radius:.6rem; padding:.6rem 1rem; margin-bottom:1rem; line-height:1.6; }
.av-table { border:1px solid rgba(255,255,255,.08); border-radius:.75rem; overflow:hidden; margin-bottom:1rem; }
.av-head { display:grid; grid-template-columns:1fr 1fr 1fr; background:rgba(99,102,241,.12); padding:.6rem 1rem; font-weight:600; font-size:.85rem; gap:.5rem; }
.av-row { display:grid; grid-template-columns:1fr 1fr 1fr; padding:.55rem 1rem; gap:.5rem; border-top:1px solid rgba(255,255,255,.06); align-items:center; }
.av-row-final { background:rgba(99,102,241,.08); font-weight:600; }
.av-col-lbl { font-size:.9rem; color:#cbd5e1; display:flex; align-items:center; gap:.3rem; }
.av-col-a, .av-col-b { display:flex; flex-direction:column; gap:.25rem; }
.av-val-row { display:flex; align-items:center; gap:.3rem; }
.av-given { font-weight:600; color:#a5b4fc; font-size:.95rem; }
.av-lbl-inp { background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.15); border-radius:.4rem; padding:.3rem .5rem; color:#e2e8f0; font-size:.85rem; width:100%; max-width:140px; }
.av-lbl-ok { border-color:#86efac !important; background:rgba(34,197,94,.1); color:#86efac; }

</style>

