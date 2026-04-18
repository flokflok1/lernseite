/**
 * IPv6 Subnetting Generator — Dynamische Übungsaufgaben
 * =====================================================
 * Generiert bei jedem Aufruf eine NEUE IPv6-Subnetting-Aufgabe
 * mit zufälligem Präfix, zufälliger TN-Anzahl und berechneter Lösung.
 *
 * Methode: Marcels 6-Schritte (Dozent Marcel Lindner)
 *   1) Was ist fest im Block 4? (CIDR - 48 = feste Bits)
 *   2) Wie viele Bits? (2^x = Anzahl TN)
 *   3) Freie Bits binär aufschreiben
 *   4) Subnet-Bits abtrennen → alle Kombinationen
 *   5) Nibble-weise zurück in Hex
 *   6) Fester Teil + Hex-Wert = Netzadresse
 *
 * Verwendung:
 *   import { generateSubnettingExercise, generateQuickDrill } from './utils/ipv6SubnettingGenerator'
 *   const exercise = generateSubnettingExercise()       // Vollständige Aufgabe
 *   const drill = generateQuickDrill()                   // Schnelle Rechen-Übung
 *   const exercise2 = generateSubnettingExercise('hard') // Schwere Aufgabe
 */

import type { FillableTableData } from '../types'

// ════════════════════════════════════════════════════════════
// Hilfs-Funktionen
// ════════════════════════════════════════════════════════════

/** Zufällige ganze Zahl von min bis max (inklusiv) */
function randInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

/** Zufälliges Element aus Array */
function randChoice<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

/** Zahl zu Hex-String (4 Zeichen, lowercase) */
function toHex4(n: number): string {
  return n.toString(16).padStart(4, '0')
}

/** Zahl zu Binär-String mit Leerzeichen alle 4 Bit */
function toBin8(n: number): string {
  const bin = n.toString(2).padStart(8, '0')
  return bin.slice(0, 4) + ' ' + bin.slice(4)
}

/** Binärstring (8 Bit) zu Hex (2 Zeichen) */
function binToHex2(bin: string): string {
  const clean = bin.replace(/\s/g, '')
  return parseInt(clean, 2).toString(16).padStart(2, '0')
}

// ════════════════════════════════════════════════════════════
// Pool von realistischen IPv6-Präfixen (Block 1-3)
// ════════════════════════════════════════════════════════════

const PREFIX_POOL = [
  '2001:db8:cafe',
  '2001:db8:affe',
  '2001:db8:abcd',
  '2001:db8:1234',
  '2001:db8:beef',
  '2001:db8:face',
  '2001:db8:dead',
  '2001:db8:c0de',
  '2001:db8:babe',
  '2001:0db8:00ea',
]

// Block-4-Startwerte die realistisch aussehen
const BLOCK4_STARTS: Record<number, string[]> = {
  // /48: Block 4 komplett frei → Startwert 0000
  48: ['0000'],
  // /50: erste 2 Bit fest → verschiedene Startwerte
  50: ['0000', '4000', '8000', 'c000'],
  // /52: erste 4 Bit fest (1 Hex-Zeichen)
  52: ['0000', '1000', '2000', '3000', 'a000', 'b000', 'c000', 'f000'],
  // /54: erste 6 Bit fest
  54: ['0000', '0400', '0800', '1000', '2000', '4000', 'a000', 'e000'],
  // /56: erste 8 Bit fest (2 Hex-Zeichen)
  56: ['ab00', 'cd00', 'ef00', '1200', '2300', '4500', '7800', 'ff00'],
  // /58: erste 10 Bit fest
  58: ['ab00', 'cd00', '2300', '4500', 'ef00', '1200'],
  // /60: erste 12 Bit fest (3 Hex-Zeichen)
  60: ['abc0', 'cde0', '1230', '4560', 'fab0', 'def0'],
}

// ════════════════════════════════════════════════════════════
// Schwierigkeitsstufen
// ════════════════════════════════════════════════════════════

export type Difficulty = 'easy' | 'medium' | 'hard'

interface DifficultyConfig {
  prefixes: number[]       // Mögliche Start-CIDRs
  subnetCounts: number[]   // Mögliche Anzahl Teilnetze
  showBinary: boolean      // Binär-Spalte anzeigen?
  showHints: boolean       // Hints in den Zellen?
  maxSubnetsToFill: number // Max. Teilnetze die man eintragen muss
}

const DIFFICULTY: Record<Difficulty, DifficultyConfig> = {
  easy: {
    prefixes: [48, 56],
    subnetCounts: [2, 4],
    showBinary: true,
    showHints: true,
    maxSubnetsToFill: 4,
  },
  medium: {
    prefixes: [48, 52, 56, 58],
    subnetCounts: [4, 8],
    showBinary: true,
    showHints: false,
    maxSubnetsToFill: 8,
  },
  hard: {
    prefixes: [50, 52, 54, 56, 58, 60],
    subnetCounts: [8, 16],
    showBinary: false,
    showHints: false,
    maxSubnetsToFill: 16,
  },
}

// ════════════════════════════════════════════════════════════
// Subnet-Berechnung (Marcels Methode)
// ════════════════════════════════════════════════════════════

interface SubnetResult {
  prefix3: string          // Block 1-3 (z.B. "2001:db8:cafe")
  block4Start: string      // Block 4 Startwert hex (z.B. "ab00")
  startCidr: number        // Start-CIDR (z.B. 56)
  subnetCount: number      // Anzahl Teilnetze (z.B. 8)
  bitsNeeded: number       // Benötigte Bits (z.B. 3)
  newCidr: number          // Neue CIDR (z.B. 59)
  fixedHexChars: number    // Feste Hex-Zeichen im Block 4
  freeHexPart: string      // Freier Teil als Hex
  stepSize: number         // Schrittweite dezimal
  stepSizeHex: string      // Schrittweite hex
  subnets: SubnetEntry[]   // Die berechneten Subnetze
}

interface SubnetEntry {
  index: number            // 0-basiert
  subnetBits: string       // z.B. "010"
  binaryFull: string       // z.B. "0100 0000"
  hexValue: string         // z.B. "40" (der freie Teil)
  block4Full: string       // z.B. "ab40"
  fullAddress: string      // z.B. "2001:db8:cafe:ab40::"
}

function calculateSubnets(
  prefix3: string,
  block4Start: string,
  startCidr: number,
  subnetCount: number
): SubnetResult {
  const bitsNeeded = Math.log2(subnetCount)
  const newCidr = startCidr + bitsNeeded

  // Wie viele Bits von Block 4 sind durch CIDR fest?
  const fixedBitsInBlock4 = startCidr - 48
  const fixedHexChars = Math.floor(fixedBitsInBlock4 / 4)

  // Fester und freier Teil von Block 4
  const fixedPart = block4Start.slice(0, fixedHexChars)
  const freePart = block4Start.slice(fixedHexChars)

  // Freie Bits berechnen (die Bits nach dem festen Teil)
  const freeBitsTotal = 16 - fixedBitsInBlock4
  const block4Num = parseInt(block4Start, 16)

  // Schrittweite: 2^(64 - newCidr) aber im Block-4-Kontext
  // = 2^(16 - (newCidr - 48)) = 2^(64 - newCidr)
  const stepBits = 16 - (newCidr - 48)
  const stepSize = Math.pow(2, stepBits)
  const stepSizeHex = stepSize.toString(16)

  // Maske für den festen Teil
  const fixedMask = 0xFFFF << (16 - fixedBitsInBlock4) & 0xFFFF
  const fixedValue = block4Num & fixedMask

  const subnets: SubnetEntry[] = []
  for (let i = 0; i < subnetCount; i++) {
    // Subnet-Bits als Binärstring
    const subnetBits = i.toString(2).padStart(bitsNeeded, '0')

    // Block 4 Wert berechnen: fester Teil + (i * stepSize)
    const block4Value = fixedValue + (i * stepSize)
    const block4Hex = toHex4(block4Value)

    // Freier Teil extrahieren für Anzeige
    const freePartValue = block4Value & ~fixedMask
    const freePartHex = freePartValue.toString(16).padStart(4 - fixedHexChars, '0')

    // Binär-Darstellung des freien Teils (8 Bit für 2 Hex-Zeichen)
    const freeBitsCount = Math.min(8, freeBitsTotal)
    const binaryShifted = (freePartValue >> (16 - fixedBitsInBlock4 - 8)) & 0xFF
    const binaryFull = toBin8(binaryShifted)

    subnets.push({
      index: i,
      subnetBits,
      binaryFull,
      hexValue: freePartHex,
      block4Full: block4Hex,
      fullAddress: `${prefix3}:${block4Hex}::`,
    })
  }

  return {
    prefix3,
    block4Start,
    startCidr,
    subnetCount,
    bitsNeeded,
    newCidr,
    fixedHexChars,
    freeHexPart: freePart,
    stepSize,
    stepSizeHex,
    subnets,
  }
}

// ════════════════════════════════════════════════════════════
// Aufgaben-Generatoren
// ════════════════════════════════════════════════════════════

/**
 * Generiert eine vollständige Subnetting-Aufgabe als FillableTableData.
 * Enthält: Schritte-Tabelle + Teilnetze-Tabelle
 */
export function generateSubnettingExercise(
  difficulty: Difficulty = 'medium'
): { stepsTable: FillableTableData; subnetsTable: FillableTableData; meta: SubnetResult } {
  const config = DIFFICULTY[difficulty]

  const startCidr = randChoice(config.prefixes)
  const subnetCount = randChoice(config.subnetCounts)
  const prefix3 = randChoice(PREFIX_POOL)
  const block4Starts = BLOCK4_STARTS[startCidr] || ['0000']
  const block4Start = randChoice(block4Starts)

  const result = calculateSubnets(prefix3, block4Start, startCidr, subnetCount)

  // ─── Schritte-Tabelle ───
  const fixedBits = startCidr - 48
  const fixedHex = block4Start.slice(0, result.fixedHexChars)
  const freeHex = block4Start.slice(result.fixedHexChars)

  const stepsTable: FillableTableData = {
    instructions:
      `Marcels 6-Schritte-Methode:\n${prefix3}:${block4Start}::/${startCidr} → ${subnetCount} Subnetze\n\nBerechnen Sie die Schritte!`,
    headers: ['Schritt', 'Ihre Antwort'],
    columnWidths: [50, 50],
    rows: [
      [
        { value: `Schritt 1: Wie viele Hex-Zeichen in Block 4 sind fest?\n(/${startCidr} → ${fixedBits} Bit fest = ? Hex-Zeichen)`, editable: false },
        {
          value: '', editable: true,
          correctAnswers: [
            String(result.fixedHexChars),
            `${result.fixedHexChars} Zeichen`,
            ...(fixedHex ? [`"${fixedHex}"`, fixedHex] : []),
          ],
          tolerance: 'contains',
          hint: config.showHints ? `${fixedBits} Bit ÷ 4 = ?` : '',
        },
      ],
      [
        { value: `Schritt 2: Wie viele Bits für ${subnetCount} Subnetze?\n(2^x = ${subnetCount})`, editable: false },
        {
          value: '', editable: true,
          correctAnswers: [String(result.bitsNeeded), `${result.bitsNeeded} Bit`],
          tolerance: 'contains',
          hint: config.showHints ? `2^? = ${subnetCount}` : '',
        },
      ],
      [
        { value: `Schritt 2: Neue CIDR?\n(/${startCidr} + ${result.bitsNeeded})`, editable: false },
        {
          value: '', editable: true,
          correctAnswers: [`/${result.newCidr}`, String(result.newCidr)],
          tolerance: 'contains',
          hint: config.showHints ? `/${startCidr} + ${result.bitsNeeded} = ?` : '',
        },
      ],
      [
        { value: `Schritt 3: Schrittweite in Hex?\n2^(64 - ${result.newCidr}) = ?`, editable: false },
        {
          value: '', editable: true,
          correctAnswers: [result.stepSizeHex, `0x${result.stepSizeHex}`, String(result.stepSize)],
          tolerance: 'case-insensitive',
          hint: config.showHints ? `2^${64 - result.newCidr} = ${result.stepSize} dez → Hex?` : '',
        },
      ],
    ],
  }

  // ─── Teilnetze-Tabelle ───
  const actualCount = Math.min(subnetCount, config.maxSubnetsToFill)

  const headers = config.showBinary
    ? ['TN', 'Subnet-Bits', 'Hex Block 4', 'Netzadresse', 'CIDR']
    : ['TN', 'Hex Block 4', 'Netzadresse', 'CIDR']
  const columnWidths = config.showBinary
    ? [8, 16, 16, 45, 15]
    : [10, 20, 50, 20]

  const rows = result.subnets.slice(0, actualCount).map((sn) => {
    const tnCell = { value: String(sn.index + 1), editable: false }
    const block4Cell = {
      value: '', editable: true,
      correctAnswers: [sn.block4Full, sn.block4Full.toLowerCase()],
      tolerance: 'case-insensitive' as const,
      hint: config.showHints
        ? (sn.index === 0 ? 'Startwert' : `+${result.stepSizeHex} hex`)
        : '',
    }
    const addrCell = {
      value: '', editable: true,
      correctAnswers: [
        sn.fullAddress,
        sn.fullAddress.toLowerCase(),
        `${prefix3}:${sn.block4Full}::/`,
      ],
      tolerance: 'contains' as const,
      hint: '',
    }
    const cidrCell = {
      value: '', editable: true,
      correctAnswers: [`/${result.newCidr}`, String(result.newCidr)],
      tolerance: 'contains' as const,
      hint: config.showHints ? `/${startCidr} + ${result.bitsNeeded}` : '',
    }

    if (config.showBinary) {
      const bitsCell = { value: sn.subnetBits, editable: false }
      return [tnCell, bitsCell, block4Cell, addrCell, cidrCell]
    }
    return [tnCell, block4Cell, addrCell, cidrCell]
  })

  const subnetsTable: FillableTableData = {
    instructions:
      `Tragen Sie die ${actualCount} Subnetze ein.\n` +
      (fixedHex ? `Fester Teil: "${fixedHex}" — ändert sich nie!\n` : '') +
      `Schrittweite: ${result.stepSizeHex} hex`,
    headers,
    columnWidths,
    rows,
  }

  return { stepsTable, subnetsTable, meta: result }
}

/**
 * Generiert eine schnelle Rechen-Übung (nur Bits + CIDR + Schrittweite).
 * Gut für schnelles Drilling — 5 zufällige Szenarien in einer Tabelle.
 */
export function generateQuickDrill(count: number = 5): FillableTableData {
  const rows = []

  for (let i = 0; i < count; i++) {
    const startCidr = randChoice([48, 50, 52, 54, 56, 58, 60])
    const subnetCount = randChoice([2, 4, 8, 16, 32])
    const bitsNeeded = Math.log2(subnetCount)
    const newCidr = startCidr + bitsNeeded
    const stepBits = 64 - newCidr
    const stepSize = Math.pow(2, stepBits)
    const stepHex = stepSize.toString(16)

    // Sicherstellen dass newCidr <= 64
    if (newCidr > 64) continue

    rows.push([
      { value: String.fromCharCode(65 + i), editable: false },  // A, B, C, ...
      { value: `/${startCidr}`, editable: false },
      { value: String(subnetCount), editable: false },
      {
        value: '', editable: true,
        correctAnswers: [String(bitsNeeded)],
        tolerance: 'exact' as const,
        hint: `2^? = ${subnetCount}`,
      },
      {
        value: '', editable: true,
        correctAnswers: [`/${newCidr}`, String(newCidr)],
        tolerance: 'contains' as const,
        hint: `/${startCidr} + ${bitsNeeded}`,
      },
      {
        value: '', editable: true,
        correctAnswers: [stepHex, `0x${stepHex}`, String(stepSize)],
        tolerance: 'case-insensitive' as const,
        hint: `2^${stepBits} → Hex`,
      },
    ])
  }

  return {
    instructions:
      'Schnell-Drill: Berechnen Sie für jedes Szenario Bits, CIDR und Schrittweite.\n' +
      'Formel: 2^x = TN → CIDR = alt + x → Schritt = 2^(64 - CIDR) in HEX\n' +
      'CASIO: Mode 4 (BASE-N) → DEC → 2^x → HEX!',
    headers: ['#', 'Start-CIDR', 'Teilnetze', 'Bits (x)', 'Neue CIDR', 'Schrittweite (hex)'],
    columnWidths: [8, 15, 14, 13, 16, 20],
    rows,
  }
}

/**
 * Generiert eine komplett neue Aufgabe als AP2-Teilaufgabe-Objekt.
 * Kann direkt in die Aufgabenliste eingefügt werden.
 */
export function generateDynamicTeilaufgabe(difficulty: Difficulty = 'medium') {
  const { stepsTable, subnetsTable, meta } = generateSubnettingExercise(difficulty)

  return {
    stepsTask: {
      nummer: 'DYN.1',
      frage:
        `🔄 Dynamische Aufgabe (${difficulty === 'easy' ? 'Einfach' : difficulty === 'medium' ? 'Mittel' : 'Schwer'}):\n` +
        `${meta.prefix3}:${meta.block4Start}::/${meta.startCidr} → ${meta.subnetCount} Subnetze\n\n` +
        `Berechnen Sie mit Marcels 6-Schritte-Methode.`,
      points: 4,
      loesung:
        `${meta.subnetCount} TN → 2^${meta.bitsNeeded} = ${meta.subnetCount} → ${meta.bitsNeeded} Bit\n` +
        `Neue CIDR: /${meta.startCidr} + ${meta.bitsNeeded} = /${meta.newCidr}\n` +
        `Schrittweite: 2^(64-${meta.newCidr}) = 2^${64 - meta.newCidr} = ${meta.stepSize} dez = ${meta.stepSizeHex} hex`,
      keywords: [String(meta.bitsNeeded), `/${meta.newCidr}`, meta.stepSizeHex],
      topics: ['IPv6', 'Subnetting'],
      fillableTable: stepsTable,
      lernhilfe: `🧠 Schritt 1: /${meta.startCidr} - 48 = ${meta.startCidr - 48} Bit fest = ${meta.fixedHexChars} Hex-Zeichen fest.`,
    },
    subnetsTask: {
      nummer: 'DYN.2',
      frage:
        `Tragen Sie jetzt die ${Math.min(meta.subnetCount, DIFFICULTY[difficulty].maxSubnetsToFill)} Subnetze ein.\n\n` +
        `Fester Teil Block 4: "${meta.block4Start.slice(0, meta.fixedHexChars)}"\n` +
        `Schrittweite: ${meta.stepSizeHex} hex`,
      points: meta.subnetCount <= 8 ? 8 : 10,
      loesung: meta.subnets.map(sn =>
        `TN ${sn.index + 1}: ${sn.fullAddress}/${meta.newCidr}`
      ).join('\n'),
      keywords: meta.subnets.slice(0, 4).map(sn => sn.block4Full),
      topics: ['IPv6', 'Subnetting'],
      fillableTable: subnetsTable,
      lernhilfe: `🧠 Schrittweite ${meta.stepSizeHex}: ${meta.subnets.slice(0, 3).map(sn => sn.block4Full).join(', ')}...`,
    },
    meta,
  }
}
