/**
 * Lesson content generator for Bezugskalkulation (procurement cost calculation).
 *
 * Generates a sequence of TeachingSteps that guide the student through
 * a full Bezugskalkulation with interactive calculator challenges.
 */

import type { TeachingStep } from './teachingTimeline.types'

interface BezugskalkulationTask {
  question: string
  values: {
    quantity: number
    unitPrice: number
    supplierDiscount: number
    cashDiscount: number
    shippingCost: number
  }
  result: number
}

export function generateBezugskalkulationLesson(task: BezugskalkulationTask): TeachingStep[] {
  const { quantity, unitPrice, supplierDiscount, cashDiscount, shippingCost } = task.values

  // Calculate intermediate values
  const lep = quantity * unitPrice
  const rabattBetrag = lep * (supplierDiscount / 100)
  const zep = lep - rabattBetrag
  const skontoBetrag = zep * (cashDiscount / 100)
  const bep = zep - skontoBetrag
  const einstandspreis = bep + shippingCost

  const formatCurrency = (n: number): string =>
    n.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' \u20AC'

  return [
    {
      id: 'intro',
      speech: `Okay, lass uns zusammen eine Bezugskalkulation durchrechnen! ${task.question}`,
      whiteboard: [
        { type: 'write', content: 'Bezugskalkulation', position: { x: 280, y: 30 }, fontSize: 28, fontWeight: 'bold', duration: 1200, color: '#1e40af' }
      ],
      animation: { type: 'explaining', expression: 'happy' }
    },
    {
      id: 'step1-lep',
      speech: `Wir starten mit dem Listeneinkaufspreis. Das ist der Preis, den der Lieferant im Katalog angibt. Wir rechnen: ${quantity} St\u00FCck mal ${formatCurrency(unitPrice)}.`,
      whiteboard: [
        { type: 'write', content: '1  Listeneinkaufspreis (LEP)', position: { x: 30, y: 80 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${quantity} \u00D7 ${formatCurrency(unitPrice)}`, position: { x: 400, y: 80 }, fontSize: 18, duration: 800 }
      ],
      animation: { type: 'pointing', pointAt: { x: 0.5, y: 0.2 } }
    },
    {
      id: 'step1-calc',
      speech: `Jetzt bist du dran! Tippe die Rechnung in den Taschenrechner ein.`,
      whiteboard: [
        { type: 'highlight', content: `${quantity} \u00D7 ${unitPrice} = ?`, position: { x: 400, y: 110 }, fontSize: 18, duration: 500, color: '#fbbf24' }
      ],
      animation: { type: 'idle', expression: 'neutral' },
      calculatorChallenge: {
        prompt: `Berechne: ${quantity} \u00D7 ${unitPrice.toFixed(2)}`,
        expectedResult: lep,
        tolerance: 0.01,
        hint: 'St\u00FCckzahl mal St\u00FCckpreis ergibt den Listeneinkaufspreis'
      }
    },
    {
      id: 'step1-result',
      speech: `Perfekt! ${formatCurrency(lep)} ist richtig. Das ist unser Listeneinkaufspreis.`,
      whiteboard: [
        { type: 'write', content: `= ${formatCurrency(lep)}`, position: { x: 550, y: 80 }, fontSize: 20, duration: 600, color: '#10b981' }
      ],
      animation: { type: 'celebrating', expression: 'happy' }
    },
    {
      id: 'step2-rabatt',
      speech: `Jetzt ziehen wir den Lieferantenrabatt von ${supplierDiscount}% ab. Rabatte sind Preisnachl\u00E4sse, die wir vom Lieferanten bekommen.`,
      whiteboard: [
        { type: 'write', content: `2  \u2212 Lieferantenrabatt (${supplierDiscount}%)`, position: { x: 30, y: 130 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${formatCurrency(lep)} \u00D7 ${supplierDiscount}%`, position: { x: 400, y: 130 }, fontSize: 18, duration: 800 }
      ],
      animation: { type: 'pointing', pointAt: { x: 0.5, y: 0.35 } }
    },
    {
      id: 'step2-calc',
      speech: `Berechne den Rabattbetrag: ${formatCurrency(lep)} mal ${supplierDiscount} Prozent.`,
      whiteboard: [
        { type: 'highlight', content: `${lep.toFixed(2)} \u00D7 0,${supplierDiscount.toString().padStart(2, '0')} = ?`, position: { x: 400, y: 160 }, fontSize: 18, duration: 500, color: '#fbbf24' }
      ],
      animation: { type: 'idle', expression: 'neutral' },
      calculatorChallenge: {
        prompt: `Berechne: ${lep.toFixed(2)} \u00D7 ${supplierDiscount / 100}`,
        expectedResult: rabattBetrag,
        tolerance: 0.01,
        hint: `Tipp: ${supplierDiscount}% = ${supplierDiscount / 100}`
      }
    },
    {
      id: 'step2-result',
      speech: `Richtig! ${formatCurrency(rabattBetrag)} Rabatt.`,
      whiteboard: [
        { type: 'write', content: `= ${formatCurrency(rabattBetrag)}`, position: { x: 550, y: 130 }, fontSize: 20, duration: 600, color: '#ef4444' }
      ],
      animation: { type: 'talking', expression: 'happy' }
    },
    {
      id: 'step3-zep',
      speech: `Nach Abzug des Rabatts erhalten wir den Zieleinkaufspreis.`,
      whiteboard: [
        { type: 'write', content: '3  = Zieleinkaufspreis (ZEP)', position: { x: 30, y: 180 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${formatCurrency(lep)} \u2212 ${formatCurrency(rabattBetrag)}`, position: { x: 400, y: 180 }, fontSize: 18, duration: 800 },
        { type: 'write', content: `= ${formatCurrency(zep)}`, position: { x: 550, y: 180 }, fontSize: 20, duration: 600, color: '#3b82f6' }
      ],
      animation: { type: 'explaining' }
    },
    {
      id: 'step4-skonto',
      speech: `Jetzt kommt das Skonto von ${cashDiscount}%. Skonto ist ein Preisnachlass f\u00FCr schnelle Zahlung.`,
      whiteboard: [
        { type: 'write', content: `4  \u2212 Lieferantenskonto (${cashDiscount}%)`, position: { x: 30, y: 230 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${formatCurrency(zep)} \u00D7 ${cashDiscount}%`, position: { x: 400, y: 230 }, fontSize: 18, duration: 800 }
      ],
      animation: { type: 'pointing', pointAt: { x: 0.5, y: 0.5 } }
    },
    {
      id: 'step4-calc',
      speech: `Berechne das Skonto.`,
      whiteboard: [
        { type: 'highlight', content: `${zep.toFixed(2)} \u00D7 0,0${cashDiscount} = ?`, position: { x: 400, y: 260 }, fontSize: 18, duration: 500, color: '#fbbf24' }
      ],
      animation: { type: 'idle', expression: 'neutral' },
      calculatorChallenge: {
        prompt: `Berechne: ${zep.toFixed(2)} \u00D7 ${cashDiscount / 100}`,
        expectedResult: skontoBetrag,
        tolerance: 0.01
      }
    },
    {
      id: 'step4-result',
      speech: `Super! ${formatCurrency(skontoBetrag)} Skonto.`,
      whiteboard: [
        { type: 'write', content: `= ${formatCurrency(skontoBetrag)}`, position: { x: 550, y: 230 }, fontSize: 20, duration: 600, color: '#ef4444' }
      ],
      animation: { type: 'celebrating', expression: 'happy' }
    },
    {
      id: 'step5-bep',
      speech: `Nach Abzug des Skontos haben wir den Bareinkaufspreis.`,
      whiteboard: [
        { type: 'write', content: '5  = Bareinkaufspreis (BEP)', position: { x: 30, y: 280 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `${formatCurrency(zep)} \u2212 ${formatCurrency(skontoBetrag)}`, position: { x: 400, y: 280 }, fontSize: 18, duration: 800 },
        { type: 'write', content: `= ${formatCurrency(bep)}`, position: { x: 550, y: 280 }, fontSize: 20, duration: 600, color: '#3b82f6' }
      ],
      animation: { type: 'explaining' }
    },
    {
      id: 'step6-bezugskosten',
      speech: `Jetzt addieren wir die Bezugskosten von ${formatCurrency(shippingCost)}. Das sind zum Beispiel Versand oder Verpackung.`,
      whiteboard: [
        { type: 'write', content: '6  + Bezugskosten', position: { x: 30, y: 330 }, fontSize: 20, duration: 1000 },
        { type: 'write', content: `+ ${formatCurrency(shippingCost)}`, position: { x: 550, y: 330 }, fontSize: 20, duration: 600, color: '#10b981' }
      ],
      animation: { type: 'pointing', pointAt: { x: 0.7, y: 0.7 } }
    },
    {
      id: 'final',
      speech: `Und jetzt das Ergebnis! Der Einstandspreis betr\u00E4gt ${formatCurrency(einstandspreis)}. Das ist der Preis, den wir wirklich f\u00FCr die Ware bezahlen. Super gemacht!`,
      whiteboard: [
        { type: 'underline', content: '', position: { x: 30, y: 370 }, endPosition: { x: 650, y: 370 }, duration: 500, lineWidth: 2 },
        { type: 'write', content: '= Einstandspreis', position: { x: 30, y: 380 }, fontSize: 22, fontWeight: 'bold', duration: 1000, color: '#1e40af' },
        { type: 'write', content: `${formatCurrency(einstandspreis)}`, position: { x: 520, y: 380 }, fontSize: 24, fontWeight: 'bold', duration: 800, color: '#10b981' },
        { type: 'box', position: { x: 500, y: 368 }, endPosition: { x: 670, y: 415 }, duration: 600, color: '#10b981', lineWidth: 3 }
      ],
      animation: { type: 'celebrating', expression: 'happy' }
    }
  ]
}
