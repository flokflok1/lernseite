/**
 * useWhiteboardCanvas Composable
 *
 * Encapsulates all canvas drawing and animation logic for the
 * InteractiveWhiteboard component: text writing, line drawing,
 * highlights, arrows, underlines, boxes, schemas, and clearing.
 *
 * @param canvasRef - Ref to the HTMLCanvasElement
 * @param canvasWidth - Computed pixel width of the canvas
 * @param canvasHeight - Computed pixel height of the canvas
 * @param backgroundColor - Reactive prop for the board background
 * @param textColor - Reactive prop for the default text color
 */

import { ref } from 'vue'
import type { Ref, ComputedRef } from 'vue'
import type { WhiteboardAction, ActionHistoryEntry } from '../types/whiteboard.types.ts'

interface UseWhiteboardCanvasOptions {
  canvasRef: Ref<HTMLCanvasElement | null>
  canvasWidth: ComputedRef<number>
  canvasHeight: ComputedRef<number>
  backgroundColor: () => string
  textColor: () => string
  onActionStart: (action: WhiteboardAction) => void
  onActionComplete: (action: WhiteboardAction) => void
  onCleared: () => void
}

export function useWhiteboardCanvas(options: UseWhiteboardCanvasOptions) {
  const {
    canvasRef,
    canvasWidth,
    canvasHeight,
    backgroundColor,
    textColor,
    onActionStart,
    onActionComplete,
    onCleared,
  } = options

  const isDrawing = ref(false)
  const cursorPosition = ref({ x: 0, y: 0 })
  const actionHistory = ref<ActionHistoryEntry[]>([])

  // ---------------------------------------------------------------------------
  // Canvas Context
  // ---------------------------------------------------------------------------
  function getContext(): CanvasRenderingContext2D | null {
    return canvasRef.value?.getContext('2d') ?? null
  }

  // ---------------------------------------------------------------------------
  // Position Helpers - Convert percent (0-100) to pixel coordinates
  // ---------------------------------------------------------------------------
  function toPixelX(percentX: number): number {
    if (percentX > 100) return percentX
    return (percentX / 100) * canvasWidth.value
  }

  function toPixelY(percentY: number): number {
    if (percentY > 100) return percentY
    return (percentY / 100) * canvasHeight.value
  }

  function toPixelPos(pos: { x: number; y: number }): { x: number; y: number } {
    return { x: toPixelX(pos.x), y: toPixelY(pos.y) }
  }

  // ---------------------------------------------------------------------------
  // Utility
  // ---------------------------------------------------------------------------
  function delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  // ---------------------------------------------------------------------------
  // Animation Functions
  // ---------------------------------------------------------------------------
  async function animateText(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
    if (!action.content) return

    const fontSize = action.fontSize || 24
    const fontWeight = action.fontWeight || 'normal'
    const color = action.color || textColor()
    const pos = toPixelPos(action.position)

    ctx.font = `${fontWeight} ${fontSize}px 'Segoe UI', Arial, sans-serif`
    ctx.fillStyle = color
    ctx.textBaseline = 'top'

    const text = action.content
    const charDelay = action.duration / text.length
    let currentText = ''

    for (let i = 0; i < text.length; i++) {
      currentText += text[i]

      const metrics = ctx.measureText(currentText)
      cursorPosition.value = { x: pos.x + metrics.width, y: pos.y }

      const prevMetrics = ctx.measureText(currentText.slice(0, -1))
      ctx.fillText(text[i], pos.x + prevMetrics.width, pos.y)

      await delay(charDelay)
    }
  }

  async function animateLine(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
    if (!action.endPosition) return

    const color = action.color || textColor()
    const lineWidth = action.lineWidth || 2

    ctx.strokeStyle = color
    ctx.lineWidth = lineWidth
    ctx.lineCap = 'round'

    const startPos = toPixelPos(action.position)
    const endPos = toPixelPos(action.endPosition)

    const steps = 30
    const stepDelay = action.duration / steps

    for (let i = 0; i <= steps; i++) {
      const progress = i / steps
      const currentX = startPos.x + (endPos.x - startPos.x) * progress
      const currentY = startPos.y + (endPos.y - startPos.y) * progress

      cursorPosition.value = { x: currentX, y: currentY }

      if (i === 0) {
        ctx.beginPath()
        ctx.moveTo(startPos.x, startPos.y)
      }

      ctx.lineTo(currentX, currentY)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(currentX, currentY)

      await delay(stepDelay)
    }
  }

  async function animateHighlight(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
    if (!action.content) return

    const fontSize = action.fontSize || 24
    const color = action.color || '#fbbf24'
    const pos = toPixelPos(action.position)

    ctx.font = `${fontSize}px 'Segoe UI', Arial, sans-serif`
    const metrics = ctx.measureText(action.content)

    const padding = 6
    const boxWidth = metrics.width + padding * 2
    const boxHeight = fontSize + padding * 2

    ctx.fillStyle = color + '40'
    const steps = 10
    const stepDelay = action.duration / steps

    for (let i = 0; i <= steps; i++) {
      const progress = i / steps
      ctx.fillRect(pos.x - padding, pos.y - padding, boxWidth * progress, boxHeight)
      await delay(stepDelay)
    }

    ctx.fillStyle = action.color || textColor()
    ctx.fillText(action.content, pos.x, pos.y)
  }

  async function animateArrow(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
    if (!action.endPosition) return

    await animateLine(ctx, action)

    const endPos = toPixelPos(action.endPosition)
    const startPos = toPixelPos(action.position)

    const color = action.color || textColor()
    const lineWidth = action.lineWidth || 2
    const angle = Math.atan2(endPos.y - startPos.y, endPos.x - startPos.x)

    const arrowLength = 15
    const arrowAngle = Math.PI / 6

    ctx.strokeStyle = color
    ctx.fillStyle = color
    ctx.lineWidth = lineWidth

    ctx.beginPath()
    ctx.moveTo(endPos.x, endPos.y)
    ctx.lineTo(
      endPos.x - arrowLength * Math.cos(angle - arrowAngle),
      endPos.y - arrowLength * Math.sin(angle - arrowAngle)
    )
    ctx.lineTo(
      endPos.x - arrowLength * Math.cos(angle + arrowAngle),
      endPos.y - arrowLength * Math.sin(angle + arrowAngle)
    )
    ctx.closePath()
    ctx.fill()
  }

  async function animateUnderline(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
    if (!action.content) return

    const pos = toPixelPos(action.position)
    const fontSize = action.fontSize || 24

    ctx.font = `${fontSize}px 'Segoe UI', Arial, sans-serif`
    const metrics = ctx.measureText(action.content)

    const color = action.color || textColor()
    const lineWidth = action.lineWidth || 3
    const startX = pos.x
    const startY = pos.y + fontSize + 4
    const endX = pos.x + metrics.width

    ctx.strokeStyle = color
    ctx.lineWidth = lineWidth
    ctx.lineCap = 'round'

    const steps = 20
    const stepDelay = action.duration / steps

    for (let i = 0; i <= steps; i++) {
      const progress = i / steps
      const currentX = startX + (endX - startX) * progress

      cursorPosition.value = { x: currentX, y: startY }

      if (i === 0) {
        ctx.beginPath()
        ctx.moveTo(startX, startY)
      }

      ctx.lineTo(currentX, startY)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(currentX, startY)

      await delay(stepDelay)
    }
  }

  async function animateSchema(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
    if (!action.schema || action.schema.length === 0) return

    const startX = (action.position?.x || 10) * canvasWidth.value / 100
    const startY = (action.position?.y || 10) * canvasHeight.value / 100
    const fontSize = action.fontSize || 18
    const lineHeight = fontSize * 1.5
    const color = action.color || textColor()
    const highlightColor = '#fbbf24'

    ctx.font = `${fontSize}px 'Segoe UI', Arial, sans-serif`
    ctx.textBaseline = 'top'

    const delayPerRow = action.duration / action.schema.length

    for (let i = 0; i < action.schema.length; i++) {
      const row = action.schema[i]
      const y = startY + i * lineHeight

      if (row.highlight) {
        ctx.fillStyle = highlightColor + '40'
        const nameWidth = ctx.measureText(row.name).width
        const opWidth = ctx.measureText(` ${row.operator} `).width
        const valueWidth = ctx.measureText(row.value).width
        const totalWidth = nameWidth + opWidth + valueWidth + 20
        ctx.fillRect(startX - 5, y - 3, totalWidth, lineHeight)
      }

      ctx.fillStyle = row.highlight ? highlightColor : color
      ctx.fillText(row.name, startX, y)
      const nameWidth = ctx.measureText(row.name).width

      ctx.fillStyle = '#94a3b8'
      ctx.fillText(` ${row.operator} `, startX + nameWidth, y)
      const opWidth = ctx.measureText(` ${row.operator} `).width

      ctx.fillStyle = row.highlight ? highlightColor : color
      ctx.font = `bold ${fontSize}px 'Segoe UI', Arial, sans-serif`
      ctx.fillText(row.value, startX + nameWidth + opWidth, y)
      ctx.font = `${fontSize}px 'Segoe UI', Arial, sans-serif`

      cursorPosition.value = {
        x: startX + nameWidth + opWidth + ctx.measureText(row.value).width,
        y: y
      }

      await delay(delayPerRow)
    }
  }

  async function animateBox(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
    if (!action.endPosition) return

    const color = action.color || textColor()
    const lineWidth = action.lineWidth || 2

    ctx.strokeStyle = color
    ctx.lineWidth = lineWidth

    const startPos = toPixelPos(action.position)
    const endPos = toPixelPos(action.endPosition)

    const x = startPos.x
    const y = startPos.y
    const w = endPos.x - x
    const h = endPos.y - y

    const steps = 40
    const stepDelay = action.duration / steps
    const perimeter = 2 * (w + h)

    ctx.beginPath()

    for (let i = 0; i <= steps; i++) {
      const progress = i / steps
      const distance = perimeter * progress

      let px: number
      let py: number

      if (distance <= w) {
        px = x + distance
        py = y
      } else if (distance <= w + h) {
        px = x + w
        py = y + (distance - w)
      } else if (distance <= 2 * w + h) {
        px = x + w - (distance - w - h)
        py = y + h
      } else {
        px = x
        py = y + h - (distance - 2 * w - h)
      }

      cursorPosition.value = { x: px, y: py }

      if (i === 0) {
        ctx.moveTo(px, py)
      } else {
        ctx.lineTo(px, py)
        ctx.stroke()
        ctx.beginPath()
        ctx.moveTo(px, py)
      }

      await delay(stepDelay)
    }

    ctx.lineTo(x, y)
    ctx.stroke()
  }

  async function animateClear(ctx: CanvasRenderingContext2D, action: WhiteboardAction): Promise<void> {
    const steps = 20
    const stepDelay = action.duration / steps
    const isTransparent = backgroundColor() === 'transparent'

    for (let i = 0; i <= steps; i++) {
      const progress = i / steps
      if (isTransparent) {
        ctx.globalAlpha = 1 - progress
      } else {
        ctx.fillStyle = backgroundColor()
        ctx.globalAlpha = progress
        ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
      }
      await delay(stepDelay)
    }

    ctx.globalAlpha = 1
    ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

    if (!isTransparent) {
      ctx.fillStyle = backgroundColor()
      ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
    }

    actionHistory.value = []
    onCleared()
  }

  // ---------------------------------------------------------------------------
  // Action Execution
  // ---------------------------------------------------------------------------
  async function executeAction(action: WhiteboardAction): Promise<void> {
    const ctx = getContext()
    if (!ctx) return

    onActionStart(action)
    isDrawing.value = true

    const imageData = ctx.getImageData(0, 0, canvasWidth.value, canvasHeight.value)
    actionHistory.value.push({ action, imageData })

    switch (action.type) {
      case 'write':
        await animateText(ctx, action)
        break
      case 'draw':
        await animateLine(ctx, action)
        break
      case 'highlight':
        await animateHighlight(ctx, action)
        break
      case 'arrow':
        await animateArrow(ctx, action)
        break
      case 'underline':
        await animateUnderline(ctx, action)
        break
      case 'box':
        await animateBox(ctx, action)
        break
      case 'schema':
        await animateSchema(ctx, action)
        break
      case 'clear':
        await animateClear(ctx, action)
        break
    }

    isDrawing.value = false
    onActionComplete(action)
  }

  async function executeActions(actions: WhiteboardAction[]): Promise<void> {
    for (const action of actions) {
      await executeAction(action)
    }
  }

  // ---------------------------------------------------------------------------
  // Control Functions
  // ---------------------------------------------------------------------------
  function clearBoard(): void {
    const ctx = getContext()
    if (!ctx) return

    ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)

    if (backgroundColor() !== 'transparent') {
      ctx.fillStyle = backgroundColor()
      ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
    }

    actionHistory.value = []
    onCleared()
  }

  function undoLast(): void {
    if (actionHistory.value.length === 0) return

    const ctx = getContext()
    if (!ctx) return

    actionHistory.value.pop()

    if (actionHistory.value.length === 0) {
      clearBoard()
    } else {
      const lastEntry = actionHistory.value[actionHistory.value.length - 1]
      ctx.putImageData(lastEntry.imageData, 0, 0)
    }
  }

  function initCanvas(): void {
    const ctx = getContext()
    if (!ctx) return

    if (backgroundColor() !== 'transparent') {
      ctx.fillStyle = backgroundColor()
      ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
    }
  }

  return {
    isDrawing,
    cursorPosition,
    actionHistory,
    executeAction,
    executeActions,
    clearBoard,
    undoLast,
    initCanvas,
  }
}
