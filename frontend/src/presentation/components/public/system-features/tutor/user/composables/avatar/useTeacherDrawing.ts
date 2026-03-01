/**
 * useTeacherDrawing - Canvas drawing functions for 2D teacher character
 *
 * Professional illustrated teacher with body, head, glasses, beard,
 * and arm poses (relaxed / pointing). All drawing is canvas-based.
 *
 * Head drawing functions extracted to teacherDrawingHead.ts (G01 split).
 */

import { TEACHER_COLORS, drawHead } from './teacherDrawingHead'

const COLORS = TEACHER_COLORS

interface DrawCharacterParams {
  ctx: CanvasRenderingContext2D
  time: number
  isPointing: boolean
  isBlinking: boolean
  mouthOpenAmount: number
}

interface UseTeacherDrawingReturn {
  drawCharacter: (params: DrawCharacterParams) => void
}

export function useTeacherDrawing(): UseTeacherDrawingReturn {

  function drawCharacter(params: DrawCharacterParams): void {
    const { ctx, time, isPointing } = params
    const cx = isPointing ? 180 : 220
    const cy = 300

    ctx.save()

    const idleBob = Math.sin(time * 2) * 2
    ctx.translate(0, idleBob)

    drawBody(ctx, cx, cy)
    drawLeftArm(ctx, cx, cy)
    drawRightArm(ctx, cx, cy, isPointing)
    drawHead(ctx, cx, cy - 120, params.isBlinking, params.mouthOpenAmount)

    ctx.restore()
  }

  function drawBody(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
    // Torso
    ctx.fillStyle = COLORS.shirt
    ctx.beginPath()
    ctx.moveTo(cx - 70, cy - 60)
    ctx.quadraticCurveTo(cx - 80, cy + 80, cx - 60, cy + 120)
    ctx.lineTo(cx + 60, cy + 120)
    ctx.quadraticCurveTo(cx + 80, cy + 80, cx + 70, cy - 60)
    ctx.quadraticCurveTo(cx, cy - 80, cx - 70, cy - 60)
    ctx.fill()

    // Shirt shadow
    ctx.fillStyle = COLORS.shirtShadow
    ctx.beginPath()
    ctx.moveTo(cx - 30, cy - 40)
    ctx.quadraticCurveTo(cx - 40, cy + 40, cx - 35, cy + 120)
    ctx.lineTo(cx - 60, cy + 120)
    ctx.quadraticCurveTo(cx - 80, cy + 80, cx - 70, cy - 60)
    ctx.quadraticCurveTo(cx - 50, cy - 70, cx - 30, cy - 40)
    ctx.fill()

    // Vest (left side)
    ctx.fillStyle = COLORS.vest
    ctx.beginPath()
    ctx.moveTo(cx - 55, cy - 50)
    ctx.lineTo(cx - 45, cy + 100)
    ctx.lineTo(cx - 15, cy + 100)
    ctx.lineTo(cx - 5, cy - 30)
    ctx.quadraticCurveTo(cx - 30, cy - 40, cx - 55, cy - 50)
    ctx.fill()

    // Vest (right side)
    ctx.beginPath()
    ctx.moveTo(cx + 55, cy - 50)
    ctx.lineTo(cx + 45, cy + 100)
    ctx.lineTo(cx + 15, cy + 100)
    ctx.lineTo(cx + 5, cy - 30)
    ctx.quadraticCurveTo(cx + 30, cy - 40, cx + 55, cy - 50)
    ctx.fill()

    // Vest buttons
    ctx.fillStyle = COLORS.vestShadow
    for (let i = 0; i < 3; i++) {
      ctx.beginPath()
      ctx.arc(cx - 10, cy + 10 + i * 30, 5, 0, Math.PI * 2)
      ctx.fill()
    }

    // Collar
    ctx.fillStyle = COLORS.shirt
    ctx.beginPath()
    ctx.moveTo(cx - 30, cy - 60)
    ctx.lineTo(cx, cy - 30)
    ctx.lineTo(cx + 30, cy - 60)
    ctx.lineTo(cx + 20, cy - 70)
    ctx.lineTo(cx, cy - 50)
    ctx.lineTo(cx - 20, cy - 70)
    ctx.closePath()
    ctx.fill()

    // Tie
    ctx.fillStyle = COLORS.tie
    ctx.beginPath()
    ctx.moveTo(cx - 8, cy - 55)
    ctx.lineTo(cx + 8, cy - 55)
    ctx.lineTo(cx + 12, cy + 50)
    ctx.lineTo(cx, cy + 70)
    ctx.lineTo(cx - 12, cy + 50)
    ctx.closePath()
    ctx.fill()

    // Tie knot
    ctx.beginPath()
    ctx.moveTo(cx - 12, cy - 55)
    ctx.lineTo(cx + 12, cy - 55)
    ctx.lineTo(cx + 8, cy - 40)
    ctx.lineTo(cx - 8, cy - 40)
    ctx.closePath()
    ctx.fill()
  }

  function drawLeftArm(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
    ctx.save()

    // Upper arm
    ctx.fillStyle = COLORS.shirt
    ctx.beginPath()
    ctx.moveTo(cx - 65, cy - 40)
    ctx.quadraticCurveTo(cx - 90, cy, cx - 85, cy + 50)
    ctx.quadraticCurveTo(cx - 80, cy + 60, cx - 70, cy + 55)
    ctx.quadraticCurveTo(cx - 55, cy + 10, cx - 50, cy - 35)
    ctx.closePath()
    ctx.fill()

    // Forearm
    ctx.beginPath()
    ctx.moveTo(cx - 85, cy + 45)
    ctx.quadraticCurveTo(cx - 95, cy + 80, cx - 90, cy + 110)
    ctx.quadraticCurveTo(cx - 85, cy + 120, cx - 75, cy + 115)
    ctx.quadraticCurveTo(cx - 65, cy + 85, cx - 70, cy + 50)
    ctx.closePath()
    ctx.fill()

    // Hand
    ctx.fillStyle = COLORS.skin
    ctx.beginPath()
    ctx.ellipse(cx - 82, cy + 125, 16, 20, 0.1, 0, Math.PI * 2)
    ctx.fill()

    // Fingers
    ctx.beginPath()
    ctx.ellipse(cx - 90, cy + 140, 5, 10, 0.2, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx - 82, cy + 145, 5, 12, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx - 74, cy + 143, 5, 11, -0.1, 0, Math.PI * 2)
    ctx.fill()

    ctx.restore()
  }

  function drawRightArm(
    ctx: CanvasRenderingContext2D,
    cx: number,
    cy: number,
    isPointing: boolean
  ): void {
    ctx.save()

    if (isPointing) {
      drawPointingRightArm(ctx, cx, cy)
    } else {
      drawRelaxedRightArm(ctx, cx, cy)
    }

    ctx.restore()
  }

  function drawPointingRightArm(
    ctx: CanvasRenderingContext2D,
    cx: number,
    cy: number
  ): void {
    // Upper arm
    ctx.fillStyle = COLORS.shirt
    ctx.beginPath()
    ctx.moveTo(cx + 65, cy - 40)
    ctx.quadraticCurveTo(cx + 100, cy - 50, cx + 130, cy - 40)
    ctx.quadraticCurveTo(cx + 140, cy - 35, cx + 135, cy - 25)
    ctx.quadraticCurveTo(cx + 100, cy - 30, cx + 55, cy - 25)
    ctx.closePath()
    ctx.fill()

    // Forearm
    ctx.beginPath()
    ctx.moveTo(cx + 130, cy - 40)
    ctx.quadraticCurveTo(cx + 170, cy - 50, cx + 200, cy - 45)
    ctx.quadraticCurveTo(cx + 210, cy - 40, cx + 205, cy - 30)
    ctx.quadraticCurveTo(cx + 170, cy - 35, cx + 135, cy - 25)
    ctx.closePath()
    ctx.fill()

    // Hand
    ctx.fillStyle = COLORS.skin
    ctx.beginPath()
    ctx.ellipse(cx + 215, cy - 38, 18, 15, 0.2, 0, Math.PI * 2)
    ctx.fill()

    // Pointing finger
    ctx.beginPath()
    ctx.moveTo(cx + 228, cy - 42)
    ctx.lineTo(cx + 260, cy - 50)
    ctx.quadraticCurveTo(cx + 265, cy - 48, cx + 263, cy - 43)
    ctx.lineTo(cx + 232, cy - 35)
    ctx.closePath()
    ctx.fill()

    // Curled fingers
    ctx.beginPath()
    ctx.ellipse(cx + 222, cy - 28, 8, 6, 0.3, 0, Math.PI * 2)
    ctx.fill()
  }

  function drawRelaxedRightArm(
    ctx: CanvasRenderingContext2D,
    cx: number,
    cy: number
  ): void {
    // Upper arm
    ctx.fillStyle = COLORS.shirt
    ctx.beginPath()
    ctx.moveTo(cx + 65, cy - 40)
    ctx.quadraticCurveTo(cx + 90, cy, cx + 85, cy + 50)
    ctx.quadraticCurveTo(cx + 80, cy + 60, cx + 70, cy + 55)
    ctx.quadraticCurveTo(cx + 55, cy + 10, cx + 50, cy - 35)
    ctx.closePath()
    ctx.fill()

    // Forearm
    ctx.beginPath()
    ctx.moveTo(cx + 85, cy + 45)
    ctx.quadraticCurveTo(cx + 95, cy + 80, cx + 90, cy + 110)
    ctx.quadraticCurveTo(cx + 85, cy + 120, cx + 75, cy + 115)
    ctx.quadraticCurveTo(cx + 65, cy + 85, cx + 70, cy + 50)
    ctx.closePath()
    ctx.fill()

    // Hand
    ctx.fillStyle = COLORS.skin
    ctx.beginPath()
    ctx.ellipse(cx + 82, cy + 125, 16, 20, -0.1, 0, Math.PI * 2)
    ctx.fill()

    // Fingers
    ctx.beginPath()
    ctx.ellipse(cx + 90, cy + 140, 5, 10, -0.2, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx + 82, cy + 145, 5, 12, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx + 74, cy + 143, 5, 11, 0.1, 0, Math.PI * 2)
    ctx.fill()
  }

  return {
    drawCharacter
  }
}
