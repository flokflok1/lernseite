/**
 * Teacher head drawing functions for 2D canvas character.
 *
 * Extracted from useTeacherDrawing.ts for G01 compliance.
 * Contains: head shape, hair, eyes, glasses, nose, beard, mouth.
 */

export const TEACHER_COLORS = {
  skin: '#F5D0C5',
  skinShadow: '#E8B5A4',
  hair: '#4A3728',
  hairHighlight: '#5D4A3A',
  shirt: '#5B8DBE',
  shirtShadow: '#4A7AAD',
  vest: '#8B5A3C',
  vestShadow: '#7A4A2C',
  tie: '#C44536',
  glasses: '#2D3748',
  eyeWhite: '#FFFFFF',
  iris: '#5D4E37',
  pupil: '#1A1A1A',
  mouth: '#A04030',
  teeth: '#FFFFFF',
  beard: '#3D2E22'
} as const

export function drawHead(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  isBlinking: boolean,
  mouthOpenAmount: number
): void {
  drawNeck(ctx, cx, cy)
  drawHeadShape(ctx, cx, cy)
  drawEars(ctx, cx, cy)
  drawHair(ctx, cx, cy)
  drawEyebrows(ctx, cx, cy)
  drawEyes(ctx, cx, cy, isBlinking)
  drawGlasses(ctx, cx, cy)
  drawNose(ctx, cx, cy)
  drawFacialHair(ctx, cx, cy)
  drawMouth(ctx, cx, cy, mouthOpenAmount)
}

function drawNeck(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
  ctx.fillStyle = TEACHER_COLORS.skin
  ctx.beginPath()
  ctx.ellipse(cx, cy + 70, 25, 30, 0, 0, Math.PI * 2)
  ctx.fill()
}

function drawHeadShape(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
  ctx.fillStyle = TEACHER_COLORS.skin
  ctx.beginPath()
  ctx.ellipse(cx, cy, 65, 80, 0, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = TEACHER_COLORS.skinShadow
  ctx.beginPath()
  ctx.ellipse(cx - 30, cy + 10, 30, 60, 0.2, Math.PI * 0.5, Math.PI * 1.5)
  ctx.fill()
}

function drawEars(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
  ctx.fillStyle = TEACHER_COLORS.skin
  ctx.beginPath()
  ctx.ellipse(cx - 62, cy, 12, 20, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + 62, cy, 12, 20, 0, 0, Math.PI * 2)
  ctx.fill()

  ctx.fillStyle = TEACHER_COLORS.skinShadow
  ctx.beginPath()
  ctx.ellipse(cx - 60, cy, 6, 12, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + 60, cy, 6, 12, 0, 0, Math.PI * 2)
  ctx.fill()
}

function drawHair(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
  ctx.fillStyle = TEACHER_COLORS.hair
  ctx.beginPath()
  ctx.moveTo(cx - 60, cy - 20)
  ctx.quadraticCurveTo(cx - 65, cy - 70, cx, cy - 85)
  ctx.quadraticCurveTo(cx + 65, cy - 70, cx + 60, cy - 20)
  ctx.quadraticCurveTo(cx + 50, cy - 50, cx, cy - 55)
  ctx.quadraticCurveTo(cx - 50, cy - 50, cx - 60, cy - 20)
  ctx.fill()

  ctx.fillStyle = TEACHER_COLORS.hairHighlight
  ctx.beginPath()
  ctx.ellipse(cx + 15, cy - 65, 20, 12, -0.3, 0, Math.PI * 2)
  ctx.fill()

  // Sideburns
  ctx.fillStyle = TEACHER_COLORS.hair
  ctx.beginPath()
  ctx.moveTo(cx - 55, cy - 30)
  ctx.quadraticCurveTo(cx - 65, cy - 10, cx - 58, cy + 10)
  ctx.lineTo(cx - 50, cy + 5)
  ctx.quadraticCurveTo(cx - 55, cy - 15, cx - 50, cy - 30)
  ctx.fill()

  ctx.beginPath()
  ctx.moveTo(cx + 55, cy - 30)
  ctx.quadraticCurveTo(cx + 65, cy - 10, cx + 58, cy + 10)
  ctx.lineTo(cx + 50, cy + 5)
  ctx.quadraticCurveTo(cx + 55, cy - 15, cx + 50, cy - 30)
  ctx.fill()
}

function drawEyebrows(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
  ctx.fillStyle = TEACHER_COLORS.hair
  ctx.lineWidth = 4
  ctx.lineCap = 'round'

  ctx.beginPath()
  ctx.moveTo(cx - 40, cy - 25)
  ctx.quadraticCurveTo(cx - 25, cy - 32, cx - 12, cy - 27)
  ctx.stroke()

  ctx.beginPath()
  ctx.moveTo(cx + 12, cy - 27)
  ctx.quadraticCurveTo(cx + 25, cy - 32, cx + 40, cy - 25)
  ctx.stroke()
}

function drawEyes(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  isBlinking: boolean
): void {
  const eyeY = cy - 10
  const eyeSpacing = 28

  ctx.fillStyle = TEACHER_COLORS.eyeWhite
  ctx.beginPath()
  ctx.ellipse(cx - eyeSpacing, eyeY, 18, isBlinking ? 2 : 14, 0, 0, Math.PI * 2)
  ctx.fill()
  ctx.beginPath()
  ctx.ellipse(cx + eyeSpacing, eyeY, 18, isBlinking ? 2 : 14, 0, 0, Math.PI * 2)
  ctx.fill()

  if (!isBlinking) {
    ctx.fillStyle = TEACHER_COLORS.iris
    ctx.beginPath()
    ctx.ellipse(cx - eyeSpacing + 2, eyeY + 2, 10, 11, 0, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.ellipse(cx + eyeSpacing + 2, eyeY + 2, 10, 11, 0, 0, Math.PI * 2)
    ctx.fill()

    ctx.fillStyle = TEACHER_COLORS.pupil
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing + 3, eyeY + 2, 5, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing + 3, eyeY + 2, 5, 0, Math.PI * 2)
    ctx.fill()

    ctx.fillStyle = '#FFFFFF'
    ctx.beginPath()
    ctx.arc(cx - eyeSpacing - 1, eyeY - 2, 4, 0, Math.PI * 2)
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cx + eyeSpacing - 1, eyeY - 2, 4, 0, Math.PI * 2)
    ctx.fill()
  }
}

function drawGlasses(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
  const eyeY = cy - 10

  ctx.strokeStyle = TEACHER_COLORS.glasses
  ctx.lineWidth = 3
  ctx.fillStyle = 'rgba(200, 220, 255, 0.1)'

  ctx.beginPath()
  ctx.roundRect(cx - 50, eyeY - 18, 42, 35, 5)
  ctx.fill()
  ctx.stroke()

  ctx.beginPath()
  ctx.roundRect(cx + 8, eyeY - 18, 42, 35, 5)
  ctx.fill()
  ctx.stroke()

  // Bridge
  ctx.beginPath()
  ctx.moveTo(cx - 8, eyeY)
  ctx.lineTo(cx + 8, eyeY)
  ctx.stroke()

  // Temple arms
  ctx.beginPath()
  ctx.moveTo(cx - 50, eyeY - 5)
  ctx.lineTo(cx - 65, eyeY - 8)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(cx + 50, eyeY - 5)
  ctx.lineTo(cx + 65, eyeY - 8)
  ctx.stroke()
}

function drawNose(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
  ctx.strokeStyle = TEACHER_COLORS.skinShadow
  ctx.lineWidth = 3
  ctx.beginPath()
  ctx.moveTo(cx, cy + 5)
  ctx.quadraticCurveTo(cx - 5, cy + 25, cx + 5, cy + 30)
  ctx.stroke()
}

function drawFacialHair(ctx: CanvasRenderingContext2D, cx: number, cy: number): void {
  // Beard / stubble
  ctx.fillStyle = TEACHER_COLORS.beard
  ctx.globalAlpha = 0.3
  ctx.beginPath()
  ctx.moveTo(cx - 45, cy + 20)
  ctx.quadraticCurveTo(cx - 55, cy + 50, cx, cy + 75)
  ctx.quadraticCurveTo(cx + 55, cy + 50, cx + 45, cy + 20)
  ctx.quadraticCurveTo(cx + 30, cy + 35, cx, cy + 40)
  ctx.quadraticCurveTo(cx - 30, cy + 35, cx - 45, cy + 20)
  ctx.fill()
  ctx.globalAlpha = 1

  // Mustache
  ctx.fillStyle = TEACHER_COLORS.beard
  ctx.beginPath()
  ctx.moveTo(cx - 25, cy + 38)
  ctx.quadraticCurveTo(cx - 15, cy + 32, cx, cy + 35)
  ctx.quadraticCurveTo(cx + 15, cy + 32, cx + 25, cy + 38)
  ctx.quadraticCurveTo(cx + 15, cy + 45, cx, cy + 42)
  ctx.quadraticCurveTo(cx - 15, cy + 45, cx - 25, cy + 38)
  ctx.fill()
}

function drawMouth(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  mouthOpenAmount: number
): void {
  const mouthY = cy + 50
  const mouthWidth = 25
  const mouthHeight = 8 + mouthOpenAmount * 20

  ctx.fillStyle = TEACHER_COLORS.mouth
  ctx.beginPath()

  if (mouthOpenAmount > 0.1) {
    ctx.ellipse(cx, mouthY + mouthHeight / 2, mouthWidth, mouthHeight, 0, 0, Math.PI * 2)
    ctx.fill()

    // Teeth
    ctx.fillStyle = TEACHER_COLORS.teeth
    ctx.beginPath()
    ctx.rect(cx - 18, mouthY - 2, 36, 8)
    ctx.fill()

    // Tongue hint
    ctx.fillStyle = '#C44536'
    ctx.beginPath()
    ctx.ellipse(cx, mouthY + mouthHeight - 5, 12, 8, 0, 0, Math.PI)
    ctx.fill()
  } else {
    ctx.strokeStyle = TEACHER_COLORS.mouth
    ctx.lineWidth = 4
    ctx.lineCap = 'round'
    ctx.beginPath()
    ctx.moveTo(cx - 20, mouthY)
    ctx.quadraticCurveTo(cx, mouthY + 12, cx + 20, mouthY)
    ctx.stroke()
  }
}
