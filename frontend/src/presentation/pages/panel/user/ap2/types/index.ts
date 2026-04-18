/**
 * AP2 Training System — Type Definitions
 * ========================================
 * Zentrale Typen für Anlagen, ausfüllbare Tabellen, Diagramm-Builder
 * und Szenario-Kontext. Alle Features bauen auf diesen Interfaces auf.
 *
 * Architektur-Prinzip: Jedes Interface ist eigenständig testbar und
 * kann unabhängig von den anderen Features verwendet werden.
 */

// ============================================================
//  ANLAGEN (Attachments)
// ============================================================

/** Typ einer Anlage — bestimmt die Rendering-Strategie */
export type AnlageType =
  | 'network-topology'   // Netzwerkplan als SVG
  | 'datasheet'          // Datenblatt (z.B. WLAN-AP Vergleich)
  | 'table'              // Referenz-Tabelle (read-only)
  | 'er-diagram'         // ER-Modell als SVG
  | 'rack-layout'        // Server-Rack-Diagramm
  | 'process-diagram'    // Prozessdiagramm (EPK-Vorlage etc.)
  | 'image'              // Allgemeines Bild / Screenshot

/** Tabellen-Daten für Anlagen vom Typ 'table' oder 'datasheet' */
export interface AnlageTableData {
  headers: string[]
  rows: string[][]
  caption?: string
  highlightRows?: number[]      // Indizes hervorgehobener Zeilen
}

/** SVG-basierte Diagramm-Daten für Anlagen */
export interface AnlageDiagramData {
  svg: string                   // Inline-SVG-Markup
  width?: number                // Breite in px (für responsive Skalierung)
  height?: number
  description?: string          // Alt-Text / Beschreibung
}

/** Eine einzelne Anlage zu einer Aufgabe */
export interface Anlage {
  id: string                    // z.B. 'w2324-pb2-anlage1'
  title: string                 // z.B. 'Netzwerkplan Standort Ravensburg'
  type: AnlageType
  /** Inhalt — abhängig vom Typ */
  table?: AnlageTableData       // Für type 'table' | 'datasheet'
  diagram?: AnlageDiagramData   // Für type 'network-topology' | 'er-diagram' etc.
  imageUrl?: string             // Für type 'image' (Base64 data-URL oder relativer Pfad)
  footnote?: string             // Zusatzinfo unter der Anlage
}


// ============================================================
//  AUSFÜLLBARE TABELLEN (Fillable Tables)
// ============================================================

/** Toleranz-Modus für Zellenvergleich */
export type CellTolerance =
  | 'exact'                     // Exakter String-Match
  | 'case-insensitive'          // Groß/Klein egal
  | 'numeric'                   // Numerischer Vergleich (z.B. 2260 ≈ 2260.08)
  | 'ip-address'                // IP-Adress-Format (führende Nullen ignorieren)
  | 'subnet-mask'               // Subnetzmaske (/24 = 255.255.255.0)
  | 'contains'                  // Antwort enthält den erwarteten Wert

/** Eine einzelne Zelle in einer ausfüllbaren Tabelle */
export interface FillableCell {
  /** Vorbelegter Wert (read-only wenn editable=false) */
  value: string
  /** Kann der Prüfling diese Zelle ausfüllen? */
  editable: boolean
  /** Korrekte Antworten (mehrere erlaubt, z.B. '255.255.255.0' und '/24') */
  correctAnswers?: string[]
  /** Vergleichs-Modus für die Bewertung */
  tolerance?: CellTolerance
  /** Tooltip-Hinweis (z.B. 'CIDR-Notation') */
  hint?: string
  /** Spaltenbreite in Prozent (optional, für ungleichmäßige Spalten) */
  widthPct?: number
}

/** Komplette ausfüllbare Tabelle für eine Teilaufgabe */
export interface FillableTableData {
  /** Spaltenüberschriften */
  headers: string[]
  /** Zeilen × Spalten Matrix */
  rows: FillableCell[][]
  /** Anweisungstext über der Tabelle */
  instructions?: string
  /** Spaltenbreiten in Prozent (muss sich zu 100 addieren) */
  columnWidths?: number[]
}

/** Ergebnis der Tabellen-Bewertung */
export interface TableGradingResult {
  /** Score 0–100 */
  pct: number
  /** Pro Zelle: korrekt oder nicht */
  cellResults: { row: number; col: number; correct: boolean; expected?: string }[]
  /** Anzahl korrekter / editierbarer Zellen */
  correctCount: number
  editableCount: number
}


// ============================================================
//  DIAGRAMM-BUILDER
// ============================================================

// ---- ER-Modell ----

export interface ERAttribute {
  name: string
  isPK?: boolean                // Primärschlüssel
  isFK?: boolean                // Fremdschlüssel
  dataType?: string             // z.B. 'VARCHAR(50)', 'INT'
}

export interface EREntity {
  id: string
  name: string
  attributes: ERAttribute[]
}

export interface ERRelationship {
  id: string
  from: string                  // Entity-ID
  to: string                    // Entity-ID
  label?: string                // z.B. 'bestellt', 'gehört zu'
  cardinality: '1:1' | '1:n' | 'n:1' | 'n:m'
}

export interface ERDiagramData {
  entities: EREntity[]
  relationships: ERRelationship[]
}

// ---- EPK (Ereignisgesteuerte Prozesskette) ----

export type EPKNodeType = 'event' | 'function' | 'xor' | 'and' | 'or'

export interface EPKNode {
  id: string
  type: EPKNodeType
  label: string
}

export interface EPKEdge {
  id: string
  from: string                  // Node-ID
  to: string                    // Node-ID
}

export interface EPKDiagramData {
  nodes: EPKNode[]
  edges: EPKEdge[]
}

// ---- Zustandsdiagramm (State Diagram) ----

export interface StateNode {
  id: string
  name: string
  isInitial?: boolean
  isFinal?: boolean
}

export interface StateTransition {
  id: string
  from: string                  // State-ID
  to: string                    // State-ID
  trigger: string               // Auslöser (z.B. 'Paket empfangen')
  guard?: string                // Bedingung (z.B. '[CRC OK]')
  action?: string               // Aktion (z.B. '/ ACK senden')
}

export interface StateDiagramData {
  states: StateNode[]
  transitions: StateTransition[]
}

// ---- Sequenzdiagramm ----

export type SequenceMessageType = 'sync' | 'async' | 'return' | 'create' | 'destroy'

export interface SequenceActor {
  id: string
  name: string
  type: 'actor' | 'object' | 'system'
}

export interface SequenceMessage {
  id: string
  from: string                  // Actor-ID
  to: string                    // Actor-ID
  label: string                 // z.B. 'HTTP GET /api/users'
  type: SequenceMessageType
  sequence: number              // Reihenfolge (1, 2, 3, ...)
}

export interface SequenceDiagramData {
  actors: SequenceActor[]
  messages: SequenceMessage[]
}

// ---- Gemeinsamer Diagramm-Container ----

export type DiagramType = 'er' | 'epk' | 'state' | 'sequence'

export interface DiagramTask {
  type: DiagramType
  /** Vorgabe-Daten (z.B. teilweise ausgefülltes ER-Modell) */
  template?: ERDiagramData | EPKDiagramData | StateDiagramData | SequenceDiagramData
  /** Erwartete Lösung für automatische Bewertung */
  solution?: ERDiagramData | EPKDiagramData | StateDiagramData | SequenceDiagramData
  /** Zusätzliche Anweisungen */
  instructions?: string
}

/** Ergebnis der Diagramm-Bewertung */
export interface DiagramGradingResult {
  pct: number
  feedback: string
  details: {
    entityScore?: number        // ER: Entitäten korrekt?
    attributeScore?: number     // ER: Attribute + PK/FK?
    relationshipScore?: number  // ER: Beziehungen + Kardinalitäten?
    nodeScore?: number          // EPK/State: Knoten korrekt?
    edgeScore?: number          // EPK/State/Sequence: Verbindungen korrekt?
    sequenceScore?: number      // Sequence: Reihenfolge korrekt?
    structureScore?: number     // Allgemein: Struktur logisch?
  }
}


// ============================================================
//  SZENARIO-KONTEXT
// ============================================================

/** Beschreibt den Prüfungskontext einer zusammenhängenden Aufgabengruppe */
export interface ScenarioContext {
  /** Projekt-/Firmenname (z.B. 'Agrarenergie Müller e. K.') */
  title: string
  /** Ausführliche Beschreibung des Szenarios */
  description: string
  /** Welche Aufgaben-Nummern gehören zum Szenario */
  aufgabenNummern: number[]
  /** Optionale Zusatzinfos (z.B. Firmenstruktur, Standorte) */
  contextDetails?: string
}


// ============================================================
//  ERWEITERTE EXAM-INTERFACES (rückwärtskompatibel)
// ============================================================

/**
 * Erweiterte Teilaufgabe mit optionalen Rich-Features.
 * Erweitert das bestehende AP2Teilaufgabe-Interface.
 */
export interface AP2TeilaufgabeExtended {
  // --- Bestehende Felder (aus ap2ExamData.ts) ---
  nummer: string
  kontext?: string
  frage: string
  points: number
  loesung: string
  keywords: string[]
  topics: string[]
  codeBlock?: string
  lernhilfe?: string

  // --- Neue Features ---
  /** Ausfüllbare Tabelle (z.B. Subnetting) */
  fillableTable?: FillableTableData
  /** Diagramm-Aufgabe (ER, EPK, Zustand, Sequenz) */
  diagramTask?: DiagramTask
}

/**
 * Erweiterte Aufgabe mit strukturierten Anlagen.
 * Erweitert das bestehende AP2Aufgabe-Interface.
 */
export interface AP2AufgabeExtended {
  nummer: number
  titel: string
  points: number
  kontext?: string
  teilaufgaben: AP2TeilaufgabeExtended[]

  // --- Neue Features ---
  /** Legacy-Anlagen-String (rückwärtskompatibel) */
  anlagen?: string
  /** Strukturierte Anlagen mit echtem Inhalt */
  anlagenData?: Anlage[]
}
