import { computed, type Ref } from 'vue'
import type { Anlage } from '@/infrastructure/api/clients/panel/user/exams'

/**
 * Shared parsing logic for Anlage content rendering.
 * Used by AnlagePanel (floating window), AnlagePopoutPage (standalone), and AnlageWindow (legacy modal).
 */
export function useAnlageRenderer(anlageRef: Ref<Anlage | null> | { value: Anlage | null }) {
  const isOffer = computed(() => anlageRef.value?.type === 'offer')
  const isApiRef = computed(() => anlageRef.value?.type === 'api_reference')
  const offerData = computed(() => (anlageRef.value?.data || {}) as Record<string, unknown>)
  const functions = computed(() =>
    ((anlageRef.value?.data as Record<string, unknown>)?.functions || []) as Array<{ name: string; description: string }>
  )

  const rawLines = computed(() => (anlageRef.value?.raw_text || '').split('\n').map(l => l.trim()))

  const recipientLines = computed(() => {
    const lines = rawLines.value
    const start = lines.findIndex(l => l.startsWith('Systemhaus') || l.startsWith('An '))
    if (start < 0) return []
    const result: string[] = []
    for (let i = start; i < Math.min(start + 4, lines.length); i++) {
      if (lines[i] && !lines[i].includes('Angebots') && !lines[i].includes('Kunden')) result.push(lines[i])
      else break
    }
    return result
  })

  const priceHeaders = computed(() => {
    const line = rawLines.value.find(l => l.includes('|') && (l.includes('Pos') || l.includes('Beschreibung')))
    if (!line) return []
    return line.split('|').map(c => c.trim()).filter(Boolean)
  })

  const priceRows = computed(() => {
    const lines = rawLines.value
    const rows: string[][] = []
    let inTable = false
    for (const line of lines) {
      if (line.includes('|') && (line.includes('Pos') || line.includes('Beschreibung'))) {
        inTable = true
        continue
      }
      if (line.includes('---')) continue
      if (inTable && line.includes('|')) {
        const cells = line.split('|').map(c => c.trim()).filter(Boolean)
        if (cells.length >= 2) rows.push(cells)
      } else if (inTable && !line.includes('|')) {
        inTable = false
      }
    }
    return rows
  })

  const totalLines = computed(() => {
    return rawLines.value.filter(l =>
      (l.includes('zzgl.') || l.includes('Gesamtsumme') || l.includes('Gesamtbetrag') ||
       l.includes('Zwischensumme'))
      && !l.includes('|') && !l.includes('USt. ID')
    )
  })

  const bodyParagraphs = computed(() => {
    const lines = rawLines.value
    const result: string[] = []
    const skipPatterns = [
      /^TOPSICHERHEIT|^Heikvision|^ANGEBOT|^Topsicherheit|^Systemhaus|^Hans-Thoma/i,
      /^\d{5}\s/,
      /^Angebots|^Kunden|^Angebot-Nr/i,
      /\|/,
      /^zzgl|^Gesamtsumme|^Gesamtbetrag|^Zwischensumme|^\d+%\s*USt/i,
      /^Mit freundlichen|^Schubert|^Thomas|^Petra|^Karlstraße|^Gartenstraße/i,
      /^[\d+\s]*7121|^www\.|^Reutlinger|^Volksbank|^DE\s\d|^BIC|^USt\.|^Steuer/i,
      /^Geschäftsführer/i,
    ]
    const greetIdx = lines.findIndex(l => l.startsWith('Sehr geehrte'))
    if (greetIdx < 0) return []
    const tableIdx = lines.findIndex(l => l.includes('|') && l.includes('Pos'))
    const stopIdx = tableIdx > 0 ? tableIdx : lines.findIndex(l => l.includes('freundlichen Grüßen'))

    let current = ''
    for (let i = greetIdx; i < (stopIdx > 0 ? stopIdx : lines.length); i++) {
      const line = lines[i]
      if (skipPatterns.some(p => p.test(line))) continue
      if (!line) {
        if (current) { result.push(current); current = '' }
      } else {
        current = current ? current + ' ' + line : line
      }
    }
    if (current) result.push(current)
    return result
  })

  const conditionLines = computed(() => {
    const lines = rawLines.value
    const result: string[] = []
    const totalIdx = lines.findIndex(l => l.includes('Gesamtsumme') || l.includes('Gesamtbetrag'))
    const closingIdx = lines.findIndex(l => l.includes('freundlichen Grüßen'))
    if (totalIdx < 0 || closingIdx < 0) return []

    let current = ''
    for (let i = totalIdx + 1; i < closingIdx; i++) {
      const line = lines[i]
      if (!line || line.includes('zzgl') || line.includes('USt') || line.includes('|')) continue
      if (line.length < 10) continue
      current = current ? current + ' ' + line : line
      if (lines[i + 1] === '' || i === closingIdx - 1) {
        if (current) { result.push(current); current = '' }
      }
    }
    if (current) result.push(current)
    return result
  })

  return {
    isOffer,
    isApiRef,
    offerData,
    functions,
    recipientLines,
    priceHeaders,
    priceRows,
    totalLines,
    bodyParagraphs,
    conditionLines,
  }
}
