/**
 * Tabellen-Bewertung — Vergleicht Nutzer-Eingaben mit korrekten Antworten.
 *
 * Unterstützt verschiedene Toleranz-Modi für unterschiedliche Aufgabentypen:
 * - exact: Exakter String-Match
 * - case-insensitive: Groß/Klein wird ignoriert
 * - numeric: Numerischer Vergleich mit Toleranz
 * - ip-address: IP-Format-Normalisierung (010.0.0.1 → 10.0.0.1)
 * - subnet-mask: /24 ↔ 255.255.255.0 Konvertierung
 * - contains: Antwort enthält den erwarteten Wert
 */

import type { FillableCell, FillableTableData, TableGradingResult, CellTolerance } from '../types'

/**
 * Normalisiert eine IP-Adresse (entfernt führende Nullen)
 */
function normalizeIP(ip: string): string {
  return ip.trim().split('.').map(octet => String(parseInt(octet, 10))).join('.')
}

/**
 * Konvertiert CIDR-Notation zu Subnetzmaske und umgekehrt.
 * Gibt beide Formen als Array zurück für flexiblen Vergleich.
 */
function subnetVariants(value: string): string[] {
  const v = value.trim()
  const variants: string[] = [v]

  // CIDR → Dezimal
  const cidrMatch = v.match(/^\/(\d+)$/)
  if (cidrMatch) {
    const prefix = parseInt(cidrMatch[1], 10)
    const mask = (0xFFFFFFFF << (32 - prefix)) >>> 0
    const decimal = [
      (mask >>> 24) & 0xFF,
      (mask >>> 16) & 0xFF,
      (mask >>> 8) & 0xFF,
      mask & 0xFF,
    ].join('.')
    variants.push(decimal)
    variants.push(v.replace('/', ''))  // Ohne Slash
    return variants
  }

  // Dezimal → CIDR
  const parts = v.split('.')
  if (parts.length === 4) {
    const binary = parts
      .map(p => parseInt(p, 10).toString(2).padStart(8, '0'))
      .join('')
    const prefix = binary.indexOf('0') === -1 ? 32 : binary.indexOf('0')
    variants.push(`/${prefix}`)
    variants.push(String(prefix))
  }

  return variants
}

/**
 * Vergleicht eine Nutzer-Antwort mit einer erwarteten Antwort.
 */
function compareCell(
  userAnswer: string,
  expectedAnswer: string,
  tolerance: CellTolerance = 'case-insensitive'
): boolean {
  const a = userAnswer.trim()
  const e = expectedAnswer.trim()

  if (!a) return false

  switch (tolerance) {
    case 'exact':
      return a === e

    case 'case-insensitive':
      return a.toLowerCase() === e.toLowerCase()

    case 'numeric': {
      const numA = parseFloat(a.replace(',', '.'))
      const numE = parseFloat(e.replace(',', '.'))
      if (isNaN(numA) || isNaN(numE)) return false
      // 1% Toleranz oder max 0.5 Differenz
      return Math.abs(numA - numE) <= Math.max(Math.abs(numE) * 0.01, 0.5)
    }

    case 'ip-address':
      return normalizeIP(a) === normalizeIP(e)

    case 'subnet-mask': {
      const variantsA = subnetVariants(a)
      const variantsE = subnetVariants(e)
      return variantsA.some(va => variantsE.some(ve =>
        va.toLowerCase() === ve.toLowerCase()
      ))
    }

    case 'contains':
      return a.toLowerCase().includes(e.toLowerCase())

    default:
      return a.toLowerCase() === e.toLowerCase()
  }
}

/**
 * Bewertet eine komplette ausfüllbare Tabelle.
 *
 * @param tableData - Die Tabellen-Definition mit korrekten Antworten
 * @param userAnswers - Map von "row-col" → Nutzer-Eingabe
 * @returns Bewertungsergebnis mit Score und Zell-Details
 */
export function gradeTable(
  tableData: FillableTableData,
  userAnswers: Record<string, string>
): TableGradingResult {
  const cellResults: TableGradingResult['cellResults'] = []
  let correctCount = 0
  let editableCount = 0

  for (let row = 0; row < tableData.rows.length; row++) {
    for (let col = 0; col < tableData.rows[row].length; col++) {
      const cell = tableData.rows[row][col]
      if (!cell.editable || !cell.correctAnswers?.length) continue

      editableCount++
      const key = `${row}-${col}`
      const userAnswer = userAnswers[key] || ''

      const isCorrect = cell.correctAnswers.some(expected =>
        compareCell(userAnswer, expected, cell.tolerance || 'case-insensitive')
      )

      if (isCorrect) correctCount++

      cellResults.push({
        row,
        col,
        correct: isCorrect,
        expected: isCorrect ? undefined : cell.correctAnswers[0],
      })
    }
  }

  return {
    pct: editableCount > 0 ? Math.round((correctCount / editableCount) * 100) : 0,
    cellResults,
    correctCount,
    editableCount,
  }
}

/**
 * Erstellt den Antwort-String für die KI-Bewertung aus Tabellen-Daten.
 * Formatiert die Tabelle als lesbaren Text.
 */
export function tableToAnswerString(
  tableData: FillableTableData,
  userAnswers: Record<string, string>
): string {
  const lines: string[] = []

  if (tableData.instructions) {
    lines.push(`Aufgabe: ${tableData.instructions}`)
    lines.push('')
  }

  // Header
  lines.push(tableData.headers.join(' | '))
  lines.push(tableData.headers.map(() => '---').join(' | '))

  // Rows
  for (let row = 0; row < tableData.rows.length; row++) {
    const cells = tableData.rows[row].map((cell, col) => {
      if (cell.editable) {
        return userAnswers[`${row}-${col}`] || '(leer)'
      }
      return cell.value
    })
    lines.push(cells.join(' | '))
  }

  return lines.join('\n')
}
