-- ============================================================================
-- Migration: 139_ap2_module_organigramm.sql
-- Description: Modul "Organigramm lesen + analysieren". Lehrblock + ~25
--              Aufgaben im Pool.
--              Schwerpunkte: Strukturen aus konkretem Organigramm zuordnen,
--              Stellenarten benennen, Vor-/Nachteile, Sonderformen.
-- Version: 1.0.0
-- Author: LernsystemX Migration System
-- Date: 2026-04-19
-- ============================================================================

INSERT INTO assessments.ap2_modules
    (slug, name_de, description, theory_markdown,
     estimated_min, difficulty, sort_order, prerequisite_slugs, is_active)
VALUES (
    'organigramm-lesen',
    'Organigramm lesen + Strukturen erkennen',
    'Vier klassische Organisationsstrukturen, drei Stellenarten, Vor-/Nachteile. BW-AP1-2026 hatte hier 16P — Pflicht-Modul für AP2.',
$theory$
## Vier klassische Organisationsstrukturen

### 1. Linienorganisation
Streng hierarchisch von oben nach unten. Jeder Mitarbeiter hat **genau einen** Vorgesetzten. Klare Zuständigkeit, einfacher Dienstweg.

```
        Geschäftsführung
        /     |      \
   Einkauf  Vertrieb  Produktion
     /\       /\        /\
   ...      ...        ...
```

**Vorteil:** klare Verantwortung, eindeutige Weisungen.
**Nachteil:** lange Dienstwege, Spitze überlastet, langsam.

### 2. Stab-Linien-Organisation (BW-Klassiker im Mittelstand)
Linienorganisation ergänzt durch **beratende Stäbe** ohne Weisungsbefugnis. Stäbe hängen NEBEN der Linie, nicht in ihr.

```
   Stab          Geschäfts-          Stab
 Recht  ←————    führung    ————→   Öffentlichkeitsarbeit
                  /    \
              Einkauf  Vertrieb
                ...    ...
```

**Erkennungsmerkmal im Diagramm:** Kästchen ohne Verbindung „nach unten", die seitlich an einer Leitungsstelle hängen — das sind Stäbe.

### 3. Spartenorganisation (Divisionalorganisation)
Untergliederung nach **Produkten, Kundengruppen oder Regionen** statt nach Funktionen. Jede Sparte arbeitet wie ein eigenes kleines Unternehmen mit eigenen Funktionsbereichen.

```
    Vertrieb
    /    |     \
Privat- Gewerbe- Behörden-
kunden  kunden   kunden
```

**Erkennungsmerkmal:** Untergliederung verläuft nach KUNDEN/PRODUKT, nicht nach FUNKTION (Einkauf/Verkauf/Produktion).

### 4. Matrixorganisation
**Zwei Vorgesetzte** pro Mitarbeiter — funktional (Fachabteilung) UND objektbezogen (Projekt/Produkt). Häufig in Beratungen, IT-Dienstleistern.

**Vorteil:** Flexibilität, Spezialisierung in beide Richtungen.
**Nachteil:** Kompetenzkonflikte, wer entscheidet wenn Streit.

---

## Drei Stellenarten

| Stellenart | Merkmal | Beispiel im Diagramm |
|---|---|---|
| **Leitungsstelle** (Instanz) | hat Weisungsbefugnis nach unten | Geschäftsführung, Bereichsleiter Einkauf |
| **Stabsstelle** | berät Leitung, KEINE Weisungsbefugnis | Rechtsabteilung, Öffentlichkeitsarbeit, Controlling |
| **Ausführungsstelle** | führt aus, KEINE Weisungsbefugnis nach unten | Buchhaltung, Steuern, KLR |

---

## Wichtig: ein Diagramm zeigt oft MEHRERE Strukturen gleichzeitig

Ein typisches Mittelstands-Organigramm hat:
- **Linien**organisation als Grundstruktur (Geschäftsführung → Funktionalbereiche)
- **Stäbe** (Recht, PR) seitlich an der Geschäftsführung
- innerhalb des Vertriebs **Sparten** (z.B. Privat- vs. Geschäftskunden)

Das ist die typische Falle in BW-AP-Aufgaben: du musst **alle** sichtbaren Strukturen nennen, nicht nur eine.

---

## Vor-/Nachteil-Schema (für Begründungs-Aufgaben)

| Struktur | Hauptvorteil | Hauptnachteil |
|---|---|---|
| Linie | klare Verantwortung | langsame Wege |
| Stab-Linie | Entlastung der Leitung durch Expertise | Konflikte Stab vs. Linie |
| Sparte | kunden-/produktnah, schneller am Markt | Doppelfunktionen, höhere Kosten |
| Matrix | Flexibilität, Multi-Projekt-Fähigkeit | Kompetenz-/Loyalitätskonflikte |
$theory$,
    12, 4, 2,
    '[]'::jsonb, TRUE
)
ON CONFLICT (slug) DO UPDATE SET
    name_de = EXCLUDED.name_de,
    description = EXCLUDED.description,
    theory_markdown = EXCLUDED.theory_markdown,
    sort_order = EXCLUDED.sort_order;

-- ============================================================
-- Aufgaben-Pool
-- ============================================================

WITH topic_lookup AS (
    SELECT topic_id FROM assessments.ap2_topics WHERE slug = 'organigramm' LIMIT 1
)
INSERT INTO assessments.ap2_learning_items
    (topic_id, item_type, prompt, model_answer, expected_answer_structure,
     grading_criteria, points, source_exam, difficulty, estimated_time_sec)
SELECT (SELECT topic_id FROM topic_lookup), v.item_type, v.prompt, v.model_answer,
       v.expected_answer_structure::jsonb,
       v.grading_criteria::jsonb,
       v.points, v.source_exam, v.difficulty, v.estimated_time_sec
FROM (VALUES

-- ============================================================
-- Mastery Pool — Definitionen + Erkennen (Tier 1-2)
-- ============================================================

('cued',
 'Was unterscheidet eine Linienorganisation von einer Mehrlinienorganisation?',
 'Linienorganisation: jeder Mitarbeiter hat GENAU EINEN Vorgesetzten — klare Hierarchie, einfache Weisungswege, aber langsam.\n\nMehrlinienorganisation (Taylor-Funktionsmeister): jeder Mitarbeiter hat MEHRERE fachliche Vorgesetzte (z.B. einer für Qualität, einer für Termine). Vorteil: Spezialisierung. Nachteil: widersprüchliche Weisungen, Kompetenzkonflikte.\n\nIn der Praxis ist die reine Mehrlinie selten — meist als Matrixorganisation modernisiert.',
 '{"required_concepts": ["Linie 1 Vorgesetzter", "Mehrlinie mehrere fachliche", "Taylor", "Konflikte"]}',
 NULL, 4, 'module-organigramm', 2, 180),

('cued',
 'Woran erkennst du im Organigramm eine Stabsstelle? Nenne mindestens zwei Merkmale.',
 'Erkennungsmerkmale einer Stabsstelle:\n1. Sie hängt SEITLICH an einer Leitungsstelle (oft Geschäftsführung), nicht in der vertikalen Linie.\n2. Sie hat KEINE Verbindungslinien NACH UNTEN — also keine Mitarbeiter, denen sie Weisungen erteilen kann.\n3. Typische Funktionen: Recht, Controlling, Personalreferat, Öffentlichkeitsarbeit, Qualitätsmanagement.\n4. Aufgabe: Beratung der Leitung, Vorbereitung von Entscheidungen — keine eigene Weisungsbefugnis.\n\nMerksatz: "Stab steht NEBEN der Linie, nicht in ihr."',
 '{"required_concepts": ["seitlich", "keine Weisungsbefugnis", "Beratung", "ohne Mitarbeiter unter sich"]}',
 NULL, 4, 'module-organigramm', 3, 180),

('cued',
 'Was ist eine Spartenorganisation und wie unterscheidet sie sich von einer Funktionalorganisation?',
 'Spartenorganisation (Divisionalorganisation): Untergliederung nach PRODUKTEN, KUNDENGRUPPEN oder REGIONEN. Jede Sparte arbeitet wie ein eigenes Mini-Unternehmen mit eigenen Funktionsbereichen.\n\nFunktionalorganisation: Untergliederung nach FUNKTIONEN (Einkauf, Produktion, Verkauf, Verwaltung, Rechnungswesen).\n\nBeispiel Spartenorganisation: Vertrieb → Privatkunden / Gewerbekunden / Behörden\nBeispiel Funktional: Einkauf → Materialeinkauf, Investitionseinkauf, Bürobedarf\n\nVorteil Sparten: nähe zum Kunden/Produkt, schneller marktreaktion, Verantwortung klar zugeordnet.\nNachteil: Mehrfachstrukturen (jede Sparte hat eigenen Einkauf), höhere Kosten, Doppelfunktionen.',
 '{"required_concepts": ["Sparten Produkte/Kunden/Regionen", "Funktional Einkauf/Verkauf/Produktion", "Mini-Unternehmen", "Doppelstrukturen"]}',
 NULL, 4, 'module-organigramm', 3, 180),

('cued',
 'Was ist eine Matrixorganisation und für welche Branchen ist sie typisch?',
 'Matrixorganisation: jeder Mitarbeiter hat ZWEI Vorgesetzte gleichzeitig:\n- funktional (Fachabteilung wie Entwicklung, QA, Vertrieb)\n- objektbezogen (Projektleiter, Produktmanager, Kundenmanager)\n\nKonkret: ein Entwickler arbeitet z.B. fachlich für seinen Entwicklungsleiter, gleichzeitig disziplinarisch für den Projektleiter "Kunde X".\n\nTypisch für:\n- IT-Beratungen\n- Multi-Projekt-Engineering (Maschinenbau, Bauwesen)\n- Pharmaforschung\n- Großkonzerne mit vielen parallelen Produkten\n\nVorteil: Flexibilität, Ressourcen können je nach Projekt umverteilt werden.\nNachteil: Kompetenz-/Loyalitätskonflikte, hoher Kommunikationsaufwand, Mitarbeiter muss zwei Hierarchien gerecht werden.',
 '{"required_concepts": ["zwei Vorgesetzte", "funktional + objektbezogen", "Projekt", "IT-Beratung", "Kompetenzkonflikt"]}',
 NULL, 4, 'module-organigramm', 3, 180),

('cued',
 'Nenne die drei Stellenarten in einem Organigramm und je ein konkretes Beispiel.',
 '1. **Leitungsstelle** (Instanz) — hat Weisungsbefugnis nach unten. Beispiele: Geschäftsführung, Bereichsleiter Einkauf, Abteilungsleiter Produktion.\n2. **Stabsstelle** — berät die Leitung, KEINE Weisungsbefugnis. Beispiele: Rechtsabteilung, Controlling, Personalreferat, Qualitätsmanagement.\n3. **Ausführungsstelle** — führt operativ aus, KEINE Weisungsbefugnis nach unten. Beispiele: Buchhalter, Sachbearbeiter, Lagerist, KLR-Mitarbeiter.\n\nMerkmal-Schnellcheck:\n- Hat Weisung nach unten? → Leitung\n- Berät Leitung ohne Weisung? → Stab\n- Macht ausführende Arbeit ohne Weisung nach unten? → Ausführung',
 '{"required_concepts": ["Leitungsstelle Weisungsbefugnis", "Stabsstelle beratend ohne Weisung", "Ausführungsstelle operativ", "Beispiele"]}',
 NULL, 5, 'module-organigramm', 2, 240),

-- ============================================================
-- Application — Erkennen aus konkretem Organigramm (Tier 3)
-- ============================================================

('application',
 'Du analysierst folgendes Organigramm der "TechSol GmbH":

```
              Öffentlichkeits-      Geschäfts-       Rechts-
                  arbeit            führung         abteilung
                                       |
   ┌─────────┬──────────┬─────────────┴──────┬────────────┐
 Einkauf  Entwicklung  Fertigung         Vertrieb     Verwaltung
                                              |              |
                                       ┌──────┼─────┐    Buchhaltung
                                    Privat- Firmen- Öffentl.    Steuern
                                    kunden  kunden  Hand
```

(a) Welche drei Organisationsstrukturen sind in diesem Diagramm gleichzeitig sichtbar? Begründe jede an einer konkreten Stelle.
(b) Welche drei Stellenarten findest du? Nenne je ein Beispiel aus dem Diagramm.',
 '(a) Drei sichtbare Strukturen:

1. **Linienorganisation** — sichtbar an der vertikalen Hierarchie Geschäftsführung → Einkauf/Entwicklung/Fertigung/Vertrieb/Verwaltung. Klare Top-Down-Weisungslinien.

2. **Stab-Linien-Organisation** — sichtbar an den seitlich neben der Geschäftsführung hängenden Kästchen "Öffentlichkeitsarbeit" und "Rechtsabteilung". Diese Stäbe haben keine Weisungsbefugnis (keine Linien nach unten), beraten nur die Geschäftsführung.

3. **Spartenorganisation** — sichtbar im Vertrieb: Untergliederung nach Privatkunden / Firmenkunden / Öffentliche Hand. Das ist eine Aufteilung nach KUNDENGRUPPEN, nicht nach Funktion = Sparten.

(b) Drei Stellenarten:

1. **Leitungsstelle** (Instanz) — Beispiel: Geschäftsführung. Hat Weisungsbefugnis über alle darunterliegenden Bereiche. Bereichsleiter Einkauf wäre auch eine Leitungsstelle.

2. **Stabsstelle** — Beispiele: Öffentlichkeitsarbeit, Rechtsabteilung. Hängen seitlich an der Geschäftsführung, ohne eigene Weisungsbefugnis.

3. **Ausführungsstelle** — Beispiele: Buchhaltung, Steuern (innerhalb der Verwaltung). Sie führen operative Aufgaben aus, haben aber keine Weisungsbefugnis nach unten.',
 '{"required_concepts": ["Linie Geschäftsführung Bereiche", "Stab Öffentlichkeitsarbeit Rechtsabteilung", "Sparten Privat Firmen Öffentlich", "Leitung GF", "Stab seitlich", "Ausführung Buchhaltung Steuern"]}',
 '[{"criterion": "3 Strukturen identifiziert", "weight": 5, "description": "Linie + Stab-Linie + Sparten", "required": true},
   {"criterion": "Jede an konkreter Stelle belegt", "weight": 4, "description": "mit Bezug auf Diagramm", "required": true},
   {"criterion": "3 Stellenarten + Beispiele", "weight": 4, "description": "Leitung/Stab/Ausführung", "required": true}]',
 13, 'module-organigramm', 4, 720),

('application',
 'Die "Nordlicht KG" hat folgendes Organigramm:

```
          Controlling      Geschäfts-     Personalrat
                           führung
                              |
       ┌───────────┬──────────┴────┬───────────────┐
   Produktion   Marketing       Vertrieb        Service
                                   |
                            ┌──────┴───────┐
                          Region          Region
                          Nord            Süd
```

(a) Identifiziere alle Organisationsstrukturen die du erkennst.
(b) Nenne einen Vorteil und einen Nachteil dieser Struktur-Kombination.',
 '(a) Sichtbare Strukturen:

1. **Linienorganisation** als Grundstruktur (Geschäftsführung → Produktion/Marketing/Vertrieb/Service).

2. **Stab-Linien-Organisation** — Controlling und Personalrat hängen als Stäbe seitlich an der Geschäftsführung. Beratende Funktion, keine Weisungsbefugnis nach unten.

3. **Spartenorganisation** — innerhalb des Vertriebs Aufteilung nach REGIONEN (Nord/Süd). Regionale Sparten sind eine klassische Form der Divisionalorganisation.

(b) Vorteil: Controlling als Stab entlastet die Geschäftsführung von operativem Controlling und liefert übergeordnete Auswertungen. Die regionale Spartenstruktur im Vertrieb ermöglicht marktnahe Entscheidungen — Region Nord kann auf lokale Besonderheiten reagieren ohne erst die Geschäftsführung zu fragen.

Nachteil: Stäbe und Linie können in Konflikt geraten ("der Controller hat gesagt..., aber der Bereichsleiter sieht das anders"). Bei der Sparten-Region-Lösung entstehen Doppelstrukturen (Region Nord und Süd haben jeweils eigene Vertriebsmitarbeiter, was teurer ist als ein zentraler Vertrieb).',
 '{"required_concepts": ["Linie", "Stab-Linie Controlling Personalrat", "Sparten Regionen", "Vorteil entlastung marktnah", "Nachteil Konflikt Doppelstruktur"]}',
 '[{"criterion": "Strukturen erkannt", "weight": 4, "description": "Linie + Stab + Sparten", "required": true},
   {"criterion": "Vorteil konkret", "weight": 3, "description": "auf Diagramm bezogen", "required": true},
   {"criterion": "Nachteil konkret", "weight": 3, "description": "auf Diagramm bezogen", "required": true}]',
 10, 'module-organigramm', 4, 600),

('application',
 'Im Organigramm der "Schnellinger GmbH" ist der Vertriebsleiter Herr Müller. Unter ihm arbeiten 4 Sachbearbeiter im Innendienst. Frau Becker ist Justiziarin (Rechtsabteilung) und berichtet direkt der Geschäftsführung.

(a) Welche Stellenart hat Herr Müller? Begründe.
(b) Welche Stellenart hat Frau Becker? Begründe.
(c) Welche Stellenart haben die 4 Sachbearbeiter? Begründe.
(d) Welche Konflikte könnten entstehen, wenn Frau Becker den Sachbearbeitern eine Weisung erteilen wollte?',
 '(a) Herr Müller ist eine **Leitungsstelle (Instanz)**. Er hat Weisungsbefugnis über die 4 Sachbearbeiter im Innendienst — er kann ihnen Anweisungen geben und ist für ihre Arbeitsergebnisse verantwortlich.

(b) Frau Becker ist eine **Stabsstelle**. Sie berichtet direkt der Geschäftsführung (= seitlich an der Geschäftsführung positioniert) und ist als Justiziarin in einer beratenden Funktion. Sie hat keine eigenen Mitarbeiter, denen sie Weisungen erteilen kann.

(c) Die 4 Sachbearbeiter sind **Ausführungsstellen**. Sie erledigen operative Aufgaben (Auftragsbearbeitung, Kundenkorrespondenz), haben aber keine Mitarbeiter unter sich und damit keine Weisungsbefugnis nach unten.

(d) Konflikt: Frau Becker hat als Stab keine Weisungsbefugnis. Wenn sie den Sachbearbeitern direkt eine Anweisung gibt, umgeht sie den Dienstweg und greift in die Kompetenz von Herrn Müller ein. Korrekt wäre: Frau Becker bespricht ihr Anliegen mit Herrn Müller (oder der Geschäftsführung), der dann selbst die Weisung erteilt. Andernfalls drohen:\n- Verwirrung bei den Sachbearbeitern (wem folgen?)\n- Untergrabung der Autorität von Herrn Müller\n- Klassischer "Stab-Linien-Konflikt" — typische Schwäche dieser Struktur.',
 '{"required_concepts": ["Leitungsstelle Müller Weisung", "Stabsstelle Becker beratend", "Ausführungsstelle Sachbearbeiter operativ", "Stab-Linien-Konflikt", "Dienstweg umgangen"]}',
 '[{"criterion": "Müller = Leitung", "weight": 2, "description": "mit Begründung", "required": true},
   {"criterion": "Becker = Stab", "weight": 2, "description": "mit Begründung", "required": true},
   {"criterion": "Sachbearbeiter = Ausführung", "weight": 2, "description": "mit Begründung", "required": true},
   {"criterion": "Konflikt erklärt", "weight": 4, "description": "Stab-Linien-Konflikt", "required": true}]',
 10, 'module-organigramm', 4, 600),

('cued',
 'Welcher Vorteil und welcher Nachteil sind typisch für eine Linienorganisation in einem mittelständischen Betrieb (~100 Mitarbeiter)?',
 'Typischer Vorteil: KLARE VERANTWORTLICHKEITEN. Jeder Mitarbeiter weiß genau, wem er berichtet, und Konflikte über Zuständigkeiten sind selten. Bei 100 Mitarbeitern ist die Hierarchie noch überschaubar (3-4 Ebenen).\n\nTypischer Nachteil: LANGE DIENSTWEGE. Wenn ein Sachbearbeiter eine Frage an die Buchhaltung in einer anderen Abteilung hat, muss die Anfrage formal über mehrere Hierarchieebenen laufen. Im Mittelstand wird das oft pragmatisch umgangen ("kurzer Dienstweg"), aber offiziell ist es vorgeschrieben. Bei wachsendem Unternehmen wird die Geschäftsführung schnell zum Flaschenhals.',
 '{"required_concepts": ["klare Verantwortung", "lange Dienstwege", "Geschäftsführung Flaschenhals"]}',
 NULL, 4, 'module-organigramm', 3, 180),

('cued',
 'Erkläre warum die Stab-Linien-Organisation als „Klassiker im deutschen Mittelstand" gilt.',
 'Drei Gründe warum Stab-Linien-Organisation im Mittelstand dominant ist:\n\n1. **Spezialwissen ohne neue Hierarchie-Ebene**: Recht, Controlling, Datenschutz, Compliance werden als Stäbe an die Geschäftsführung gehängt. Die operativen Bereichsleiter müssen sich nicht selbst um diese Spezialthemen kümmern, behalten aber Weisungsbefugnis im operativen Geschäft.\n\n2. **Klare Linien**: Anders als die Matrixorganisation behält jeder Mitarbeiter EINEN operativen Vorgesetzten — keine Loyalitäts-Konflikte. Das passt zur deutschen Mittelstandskultur (klare Verantwortung, klare Zuständigkeit).\n\n3. **Wirtschaftlich**: Stäbe sind oft 1-2 Personen — günstiger als eine eigene Abteilung. Wachstum ohne Strukturveränderung möglich (mehr Stäbe einfach hinzufügen).\n\nNachteil: bei zu vielen Stäben ("Stabsflut") wird die Geschäftsführung wieder zum Engpass — dann ist es Zeit für eine Spartenstruktur.',
 '{"required_concepts": ["Spezialwissen ohne neue Ebene", "klare Linien", "wirtschaftlich", "Stabsflut"]}',
 NULL, 4, 'module-organigramm', 3, 240),

('cued',
 'Wann ist eine Matrixorganisation sinnvoller als eine Stab-Linien-Organisation?',
 'Matrix lohnt wenn:\n1. **Viele parallele Projekte/Produkte** mit unterschiedlichen Anforderungen — z.B. IT-Beratung mit 20 Kundenprojekten parallel.\n2. **Hochqualifizierte Mitarbeiter** die zwischen Projekten flexibel verteilt werden müssen (Spezialisten knapp).\n3. **Komplexe Produkte** mit vielen Disziplinen (z.B. Auto: Mechanik + Elektronik + Software → ein Modell-Projektleiter + drei Fachabteilungs-Leiter).\n4. **Internationaler Konzern** mit Länder-/Region-Achse + Produkt-Achse.\n\nStab-Linien reicht wenn:\n- Wenige große Projekte/Produkte\n- Klare funktionale Trennung\n- Stabile Abläufe ohne ständige Umverteilung\n\nFalle Matrix: braucht reife Führungskultur. In rigiden Umgebungen entstehen Dauer-Konflikte.',
 '{"required_concepts": ["viele Projekte parallel", "knappe Spezialisten", "komplexe Produkte", "Konzern mit Land+Produkt", "Führungskultur nötig"]}',
 NULL, 4, 'module-organigramm', 3, 240),

-- ============================================================
-- Spot-Check Pool (kurze Fragen)
-- ============================================================

('cued',
 'Hat eine Stabsstelle Weisungsbefugnis?',
 'Nein. Stäbe beraten die Leitung, haben aber keine Weisungsbefugnis nach unten. Das unterscheidet sie von der Leitungsstelle.',
 '{"required_concepts": ["nein", "berät", "keine Weisungsbefugnis"]}',
 NULL, 1, 'module-organigramm-spot', 1, 30),

('cued',
 'Nenne 3 typische Beispiele für Stabsstellen in einem Unternehmen.',
 'Rechtsabteilung, Controlling, Personalreferat, Öffentlichkeitsarbeit, Qualitätsmanagement, Compliance — drei genügen.',
 '{"required_concepts": ["Recht", "Controlling", "PR oder Personal"]}',
 NULL, 1, 'module-organigramm-spot', 1, 30),

('cued',
 'Welche Organisationsform hat genau zwei Vorgesetzte pro Mitarbeiter?',
 'Matrixorganisation — funktional (Fachabteilung) + objektbezogen (Projekt/Produkt).',
 '{"required_concepts": ["Matrix"]}',
 NULL, 1, 'module-organigramm-spot', 1, 20),

('cued',
 'Wie unterscheidest du im Diagramm Spartenorganisation von Funktionalorganisation?',
 'Sparten gliedern nach PRODUKTEN/KUNDEN/REGIONEN (z.B. Privatkunden / Firmenkunden), Funktional gliedert nach FUNKTIONEN (Einkauf / Verkauf / Produktion).',
 '{"required_concepts": ["Sparten Produkte/Kunden/Regionen", "Funktional Einkauf/Verkauf"]}',
 NULL, 2, 'module-organigramm-spot', 2, 60),

('cued',
 'Was ist der größte Nachteil einer Matrixorganisation?',
 'Kompetenz- und Loyalitätskonflikte zwischen den zwei Vorgesetzten — wem soll der Mitarbeiter zuerst Folge leisten? Hoher Kommunikationsaufwand.',
 '{"required_concepts": ["Kompetenzkonflikt", "Loyalitätskonflikt", "zwei Vorgesetzte"]}',
 NULL, 1, 'module-organigramm-spot', 1, 30),

('cued',
 'Wie erkennst du im Organigramm einen Stab vs. eine Linienstelle?',
 'Stab: hängt SEITLICH an einer Leitungsstelle, hat KEINE Linien NACH UNTEN.\nLinie: ist Teil der vertikalen Hierarchie, hat Mitarbeiter unter sich.',
 '{"required_concepts": ["Stab seitlich", "keine Linie nach unten", "Linie vertikal"]}',
 NULL, 1, 'module-organigramm-spot', 2, 45)

) AS v(item_type, prompt, model_answer,
       expected_answer_structure, grading_criteria, points, source_exam, difficulty, estimated_time_sec);

-- ============================================================
-- Items dem Modul zuordnen
-- ============================================================

WITH module_lookup AS (
    SELECT module_id FROM assessments.ap2_modules WHERE slug = 'organigramm-lesen' LIMIT 1
),
mastery_items AS (
    SELECT i.item_id, ROW_NUMBER() OVER (ORDER BY i.created_at) AS sort_order
    FROM assessments.ap2_learning_items i
    WHERE i.source_exam = 'module-organigramm'
)
INSERT INTO assessments.ap2_module_items (module_id, item_id, pool_tier, use_in, sort_order)
SELECT (SELECT module_id FROM module_lookup), m.item_id, 2, 'mastery', m.sort_order
FROM mastery_items m
ON CONFLICT (module_id, item_id) DO NOTHING;

WITH module_lookup AS (
    SELECT module_id FROM assessments.ap2_modules WHERE slug = 'organigramm-lesen' LIMIT 1
),
spotcheck_items AS (
    SELECT i.item_id, ROW_NUMBER() OVER (ORDER BY i.created_at) AS sort_order
    FROM assessments.ap2_learning_items i
    WHERE i.source_exam = 'module-organigramm-spot'
)
INSERT INTO assessments.ap2_module_items (module_id, item_id, pool_tier, use_in, sort_order)
SELECT (SELECT module_id FROM module_lookup), s.item_id, 1, 'spotcheck', s.sort_order
FROM spotcheck_items s
ON CONFLICT (module_id, item_id) DO NOTHING;

COMMIT;
