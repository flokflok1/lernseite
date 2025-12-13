# KI-Studio Briefing: AP1 FISI Content-Generierung

## Projekt-Uebersicht

**Kurs:** AP1 Pruefungsvorbereitung - FISI Baden-Wuerttemberg
**Kurs-ID:** `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
**Zielgruppe:** Fachinformatiker Systemintegration (FISI) in Pruefungsvorbereitung
**Pruefung:** Abschlusspruefung Teil 1 (AP1), 90 Minuten, 90 Punkte

---

## Struktur des Kurses (bereits in DB)

| Modul | Titel | Lektionen | Punkte |
|-------|-------|-----------|--------|
| 1 | Unternehmen & Beschaffung | 10 | ~30 |
| 2 | IT-Sicherheit | 7 | ~15 |
| 3 | Netzwerktechnik (KERN!) | 15 | ~30 |
| 4 | Datenbanken & SQL | 10 | ~15 |
| 5 | Programmierung | 6 | ~15 |
| 6 | Pruefungsvorbereitung | 5 | - |

**Gesamt:** 53 Lektionen

---

## Lernmethoden pro Lektion

Jede Lektion hat im `content` JSONB-Feld folgende Felder:
- `lm_primary`: Primaere Lernmethode (z.B. "LM12")
- `lm_secondary`: Optionale sekundaere Lernmethode
- `topic`: Konkretes Thema
- `pruefungs_relevanz`: SEHR HOCH / HOCH / mittel / niedrig

### Primaere Lernmethoden

| LM | Name | Wann verwenden |
|----|------|----------------|
| **LM00** | Tiefe Erklaerung | Theorievermittlung komplexer Konzepte |
| **LM09** | Code Sandbox | SQL-Abfragen, Programmierung |
| **LM10** | Netzwerk-Simulation | Subnetting visuell, Netzwerkplaene |
| **LM11** | IT-Szenario | Schutzbedarfsanalyse, Troubleshooting |
| **LM12** | Mathe-Interaktiv | Handelskalkulation, Subnetting-Berechnungen |
| **LM13** | Flashcards | Begriffe (ITIL, OSI, IPv6-Typen) |
| **LM14** | Drag & Drop | Zuordnungsaufgaben (OSI, DHCP-Schritte) |
| **LM16** | Fehleranalyse | SQL-Fehler, Code-Bugs finden |
| **LM19** | IHK-Stil | Original-Pruefungsaufgaben nachbauen |
| **LM21** | Zeitlimit-Training | 90-Min-Simulation |
| **LM22** | Quiz | Multiple-Choice Theoriefragen |
| **LM25** | Kapitel-Endpruefung | Modul-Abschlusspruefungen |

---

## Content-Anforderungen pro Modul

### MODUL 1: Unternehmen & Beschaffung

#### Lektion 1.5-1.8: HANDELSKALKULATION (KRITISCH!)

**Bezugskalkulation (LM12):**
```
Listeneinkaufspreis (LEP)
- Lieferantenrabatt (z.B. 10%)
= Zieleinkaufspreis (ZEP)
- Lieferantenskonto (z.B. 2%)
= Bareinkaufspreis (BEP)
+ Bezugskosten (Transport, Verpackung)
= Bezugspreis (Einstandspreis)
```

**Verkaufskalkulation (LM12):**
```
Bezugspreis
+ Handlungskosten (z.B. 25%)
= Selbstkosten
+ Gewinnzuschlag (z.B. 15%)
= Barverkaufspreis
+ Kundenskonto (z.B. 3%)
= Zielverkaufspreis
+ Kundenrabatt (z.B. 10%)
= Listenverkaufspreis (netto)
+ Umsatzsteuer (19%)
= Listenverkaufspreis (brutto)
```

**Beispielaufgabe fuer LM19:**
> Die Muster-IT GmbH kauft 50 Server zu je 2.400 EUR (LEP).
> - Rabatt: 15%
> - Skonto: 3%
> - Bezugskosten: 1.200 EUR gesamt
> - Handlungskostenzuschlag: 20%
> - Gewinnzuschlag: 12%
> - Kundenskonto: 2%
> - Kundenrabatt: 5%
>
> Berechnen Sie den Listenverkaufspreis (brutto) pro Server.

---

### MODUL 2: IT-Sicherheit

#### Lektion 2.3-2.4: SCHUTZBEDARFSANALYSE (WICHTIG!)

**Schutzziele (CIA-Triade):**
- **Vertraulichkeit** (Confidentiality): Nur Berechtigte haben Zugriff
- **Integritaet** (Integrity): Daten sind korrekt und unveraendert
- **Verfuegbarkeit** (Availability): Systeme sind erreichbar

**Schutzbedarfskategorien:**
| Kategorie | Auswirkung bei Verletzung |
|-----------|---------------------------|
| normal | begrenzte/ueberschaubare Schaeden |
| hoch | betraechtliche Schaeden |
| sehr hoch | existenzbedrohende/katastrophale Schaeden |

**Maximumprinzip:** Der hoechste Schutzbedarf eines Teilaspekts bestimmt den Gesamtschutzbedarf.

**Beispielaufgabe fuer LM11:**
> Fuellen Sie die Schutzbedarfsanalyse fuer eine Arztpraxis aus:
>
> | Schutzobjekt | Vertraulichkeit | Integritaet | Verfuegbarkeit |
> |--------------|-----------------|-------------|----------------|
> | Patientendaten | ? | ? | ? |
> | Terminkalender | ? | ? | ? |
> | Abrechnungsdaten | ? | ? | ? |
> | Website | ? | ? | ? |
>
> Begruenden Sie jede Einstufung!

---

### MODUL 3: Netzwerktechnik (HAUPTMODUL!)

#### Lektion 3.4-3.8: SUBNETTING (KRITISCH!)

**IPv4-Subnetting Schritte (LM12):**

1. **Subnetzmaske in CIDR:** /24 = 255.255.255.0
2. **Netzwerkadresse:** IP AND Subnetzmaske (binaer)
3. **Broadcastadresse:** Alle Hostbits auf 1 setzen
4. **Hostbereich:** Netzwerkadresse+1 bis Broadcast-1
5. **Anzahl Hosts:** 2^n - 2 (n = Hostbits)

**CIDR-Tabelle:**
| CIDR | Subnetzmaske | Hosts |
|------|--------------|-------|
| /24 | 255.255.255.0 | 254 |
| /25 | 255.255.255.128 | 126 |
| /26 | 255.255.255.192 | 62 |
| /27 | 255.255.255.224 | 30 |
| /28 | 255.255.255.240 | 14 |
| /29 | 255.255.255.248 | 6 |
| /30 | 255.255.255.252 | 2 |

**Beispielaufgabe fuer LM19:**
> Gegeben: IP 192.168.50.137/26
>
> Ermitteln Sie:
> a) Subnetzmaske in dezimaler Schreibweise
> b) Netzwerkadresse
> c) Broadcastadresse
> d) Erster nutzbarer Host
> e) Letzter nutzbarer Host
> f) Anzahl maximal moeglicher Hosts

**Loesung:**
- a) 255.255.255.192
- b) 192.168.50.128
- c) 192.168.50.191
- d) 192.168.50.129
- e) 192.168.50.190
- f) 62

#### Lektion 3.9-3.10: IPv6

**IPv6-Adresstypen (LM13 Flashcards):**
| Typ | Praefix | Beispiel |
|-----|---------|----------|
| Global Unicast | 2000::/3 | 2001:db8::1 |
| Link-Local | fe80::/10 | fe80::1 |
| Unique Local | fc00::/7 | fd00::1 |
| Multicast | ff00::/8 | ff02::1 |

**Kuerzungsregeln:**
1. Fuehrende Nullen weglassen: 2001:0db8 → 2001:db8
2. Laengste Nullfolge durch :: ersetzen (nur einmal!)

#### Lektion 3.11: DHCP (LM14 Drag&Drop)

**DORA-Prozess in korrekter Reihenfolge:**
1. **D**iscover (Client → Broadcast): "Gibt es einen DHCP-Server?"
2. **O**ffer (Server → Client): "Ich biete dir diese IP an"
3. **R**equest (Client → Broadcast): "Ich nehme die IP von Server X"
4. **A**cknowledge (Server → Client): "Bestaetigt, du hast die IP"

---

### MODUL 4: Datenbanken & SQL

#### Lektion 4.2-4.5: ERM & Relationenmodell

**Kardinalitaeten (LM14):**
- **1:1** - Ein Mitarbeiter hat genau einen Dienstwagen
- **1:n** - Ein Kunde hat mehrere Bestellungen
- **m:n** - Schueler besuchen mehrere Kurse, Kurse haben mehrere Schueler

**ERM → Relationenmodell:**
- 1:1 → Fremdschluessel in einer der Tabellen
- 1:n → Fremdschluessel auf der n-Seite
- m:n → Zwischentabelle mit beiden Fremdschluesseln

#### Lektion 4.6-4.9: SQL (LM09 Code Sandbox)

**SELECT-Beispiele:**
```sql
-- Einfache Abfrage
SELECT vorname, nachname FROM mitarbeiter WHERE abteilung = 'IT';

-- Mit Sortierung
SELECT * FROM produkte ORDER BY preis DESC;

-- Mit Aggregatfunktion
SELECT abteilung, COUNT(*) AS anzahl
FROM mitarbeiter
GROUP BY abteilung;

-- Mit JOIN (WICHTIG!)
SELECT k.name, b.bestelldatum
FROM kunden k
INNER JOIN bestellungen b ON k.kunden_id = b.kunden_id;
```

**Fehlerhafte SQL fuer LM16:**
```sql
-- Fehler 1: Fehlender Alias
SELECT COUNT(*) FROM mitarbeiter GROUP BY abteilung

-- Fehler 2: Falsche Syntax
SELECT * FROM kunden WHERE name = 'Müller;

-- Fehler 3: Falscher Operator
SELECT * FROM produkte WHERE preis => 100;

-- Fehler 4: Nicht existierende Spalte in GROUP BY
SELECT abteilung, gehalt FROM mitarbeiter GROUP BY name;
```

---

### MODUL 5: Programmierung

#### Lektion 5.5: Fehler in Code finden (LM16)

**Beispiel fehlerhafter Code (Java-aehnlich):**
```java
// Aufgabe: Durchschnitt berechnen
public double berechneDurchschnitt(int[] zahlen) {
    int summe;  // FEHLER: Nicht initialisiert
    for (int i = 0; i <= zahlen.length; i++) {  // FEHLER: <= statt <
        summe = summe + zahlen[i];
    }
    return summe / zahlen.length;  // FEHLER: Integer-Division
}
```

**Korrigierter Code:**
```java
public double berechneDurchschnitt(int[] zahlen) {
    int summe = 0;
    for (int i = 0; i < zahlen.length; i++) {
        summe = summe + zahlen[i];
    }
    return (double) summe / zahlen.length;
}
```

---

### MODUL 6: Pruefungsvorbereitung

#### Lektion 6.2-6.4: Original-Pruefungen (LM21 + LM19)

**Konfiguration:**
- Zeitlimit: 90 Minuten
- auto_submit: true
- shuffle_questions: false (Reihenfolge wie in Pruefung)

**Aufgabenstruktur 2024 (4 Aufgaben):**
| Aufgabe | Thema | Punkte | Zeit |
|---------|-------|--------|------|
| IT 1 | Beschaffung | 30 | ~25 Min |
| IT 2 | Programmierung | 15 | ~15 Min |
| IT 3 | Datenbank/SQL | 15 | ~15 Min |
| IT 4 | Netzwerk + Sicherheit | 30 | ~35 Min |

---

## Pruefungs-Tipps (fuer Lektion 6.1)

### Zeitmanagement-Strategie:
1. **Erst lesen:** Alle Aufgaben ueberfliegen (5 Min)
2. **Leichte zuerst:** Mit sicheren Punkten beginnen
3. **Punkte = Minuten:** 30-Punkte-Aufgabe = max. 30 Min
4. **Nicht haengenbleiben:** Bei Unklarheit weitergehen, spaeter zurueck
5. **Kontrolle:** Letzte 5 Min fuer Kontrolle reservieren

### Typische Fehlerquellen:
- Handelskalkulation: Reihenfolge der Zu-/Abschlaege
- Subnetting: AND-Verknuepfung falsch gerechnet
- SQL: Semikolon vergessen, Apostrophe bei Strings
- Schutzbedarfsanalyse: Begruendung vergessen

---

## Content-Generierung mit KI-Studio

### Empfohlener Workflow:

1. **PDF Upload:** AP1-FISI-Analyse.md + Original-Pruefungs-PDFs
2. **Prompt:** "Generiere Lernmethoden-Content fuer Lektion [X.Y] mit Thema [TOPIC] im Format [LM_PRIMARY]"
3. **Review:** Content auf IHK-Konformitaet pruefen
4. **Speichern:** Als learning_method_instance in DB

### Beispiel-Prompt fuer LM12 (Mathe-Interaktiv):

```
Erstelle eine interaktive Mathe-Aufgabe fuer die Bezugskalkulation.

Thema: Listeneinkaufspreis zu Bezugspreis
Format: Schrittweise Eingabe mit sofortigem Feedback

Aufgabe:
Ein IT-Haendler kauft 20 Notebooks zu je 800 EUR Listeneinkaufspreis.
- Lieferantenrabatt: 12%
- Lieferantenskonto: 3%
- Bezugskosten: 180 EUR gesamt

Der Lernende soll jeden Schritt einzeln berechnen:
1. Zieleinkaufspreis pro Stueck
2. Bareinkaufspreis pro Stueck
3. Bezugspreis pro Stueck
4. Bezugspreis gesamt

Gib fuer jeden Schritt:
- Die Formel
- Das erwartete Ergebnis
- Einen Hinweis bei falschem Ergebnis
```

---

## Dateien

- **Kurs-Grundgeruest:** `backend/database/seed_ap1_fisi_course.sql`
- **Analyse-Dokument:** `LernsystemX-Doku/AP1-FISI-Analyse.md`
- **Dieses Briefing:** `LernsystemX-Doku/AP1-KI-Studio-Briefing.md`

---

*Erstellt: Dezember 2024*
*Fuer: LernsystemX KI-Studio Content-Generierung*
