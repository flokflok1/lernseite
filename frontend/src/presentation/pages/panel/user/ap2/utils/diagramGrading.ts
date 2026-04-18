/**
 * Diagramm-Bewertungsutilities
 *
 * Zentrale Hilfsfunktionen für die Bewertung von Diagramm-Aufgaben.
 * Die eigentliche Bewertungslogik ist in den jeweiligen Builder-Komponenten,
 * hier liegen allgemeine Vergleichsfunktionen.
 */

import type { DiagramGradingResult, DiagramType } from '../types'

/**
 * Erstellt eine textuelle Beschreibung des Diagramm-Ergebnisses
 * für die KI-gestützte Bewertung.
 */
export function diagramResultToText(
  type: DiagramType,
  result: DiagramGradingResult
): string {
  const lines: string[] = []
  lines.push(`Diagramm-Typ: ${getDiagramTypeName(type)}`)
  lines.push(`Gesamtscore: ${result.pct}%`)
  lines.push(`Feedback: ${result.feedback}`)

  if (result.details) {
    lines.push('\nDetailbewertung:')
    if (result.details.entityScore !== undefined)
      lines.push(`  Entitäten: ${result.details.entityScore}%`)
    if (result.details.attributeScore !== undefined)
      lines.push(`  Attribute & Schlüssel: ${result.details.attributeScore}%`)
    if (result.details.relationshipScore !== undefined)
      lines.push(`  Beziehungen: ${result.details.relationshipScore}%`)
    if (result.details.nodeScore !== undefined)
      lines.push(`  Knoten/Zustände: ${result.details.nodeScore}%`)
    if (result.details.edgeScore !== undefined)
      lines.push(`  Kanten/Transitionen: ${result.details.edgeScore}%`)
    if (result.details.sequenceScore !== undefined)
      lines.push(`  Reihenfolge: ${result.details.sequenceScore}%`)
    if (result.details.structureScore !== undefined)
      lines.push(`  Strukturlogik: ${result.details.structureScore}%`)
  }

  return lines.join('\n')
}

/**
 * Gibt den deutschen Anzeigenamen für einen Diagrammtyp zurück.
 */
export function getDiagramTypeName(type: DiagramType): string {
  const names: Record<DiagramType, string> = {
    er: 'ER-Diagramm (Entity-Relationship)',
    epk: 'EPK (Ereignisgesteuerte Prozesskette)',
    state: 'Zustandsdiagramm',
    sequence: 'Sequenzdiagramm',
  }
  return names[type] || type
}

/**
 * Berechnet einen gewichteten Gesamtscore aus Teilscores.
 */
export function weightedScore(
  scores: { value: number; weight: number }[]
): number {
  const totalWeight = scores.reduce((s, e) => s + e.weight, 0)
  if (totalWeight === 0) return 0
  const weighted = scores.reduce((s, e) => s + e.value * e.weight, 0)
  return Math.round(weighted / totalWeight)
}

/**
 * Generiert Feedback-Text basierend auf Score-Bereichen.
 */
export function scoreFeedback(
  pct: number,
  context: {
    excellent?: string
    good?: string
    fair?: string
    poor?: string
  } = {}
): string {
  if (pct >= 90) return context.excellent || 'Ausgezeichnet!'
  if (pct >= 70) return context.good || 'Gut gemacht, einige Details fehlen.'
  if (pct >= 50) return context.fair || 'Grundstruktur erkennbar, aber Lücken.'
  return context.poor || 'Muss noch deutlich verbessert werden.'
}

/**
 * Vergleicht zwei String-Listen (z.B. Entity-Namen) und gibt den
 * Anteil übereinstimmender Einträge zurück (0-100).
 */
export function listMatchScore(
  expected: string[],
  actual: string[],
  caseSensitive = false
): number {
  if (expected.length === 0) return 100
  const normalize = (s: string) => caseSensitive ? s.trim() : s.trim().toLowerCase()
  const normalizedActual = actual.map(normalize)
  const matched = expected.filter(e => normalizedActual.includes(normalize(e)))
  return Math.round((matched.length / expected.length) * 100)
}
