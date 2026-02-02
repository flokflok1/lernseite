/**
 * Watermark Utilities
 *
 * Provides functions to add watermarks to images and content.
 * Supports canvas-based watermarks for images and CSS-based watermarks for content areas.
 */

export interface WatermarkOptions {
  text: string
  username?: string
  date?: Date
  opacity?: number
  fontSize?: number
  fontFamily?: string
  color?: string
  rotation?: number
  position?: 'diagonal' | 'corners' | 'center' | 'tiled'
}

const defaultOptions: Required<WatermarkOptions> = {
  text: '© LernsystemX',
  username: '',
  date: new Date(),
  opacity: 0.25,
  fontSize: 16,
  fontFamily: 'Arial, sans-serif',
  color: '#000000',
  rotation: -30,
  position: 'diagonal',
}

/**
 * Generates a watermark text with username and date
 * @param options - Watermark configuration options
 * @returns Formatted watermark text
 */
export function generateWatermarkText(options: Partial<WatermarkOptions> = {}): string {
  const opts = { ...defaultOptions, ...options }
  const datePart = opts.date ? ` | ${opts.date.toLocaleDateString('de-DE')}` : ''
  const userPart = opts.username ? ` | ${opts.username}` : ''

  return `${opts.text}${userPart}${datePart}`
}

/**
 * Adds a diagonal watermark to an image using Canvas
 * @param imageElement - The image element to watermark
 * @param options - Watermark configuration options
 * @returns Promise resolving to the watermarked image data URL
 */
export async function addImageWatermark(
  imageElement: HTMLImageElement,
  options: Partial<WatermarkOptions> = {}
): Promise<string> {
  const opts = { ...defaultOptions, ...options }

  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')

    if (!ctx) {
      reject(new Error('Could not get canvas context'))
      return
    }

    // Wait for image to load if necessary
    const processImage = () => {
      canvas.width = imageElement.naturalWidth || imageElement.width
      canvas.height = imageElement.naturalHeight || imageElement.height

      // Draw original image
      ctx.drawImage(imageElement, 0, 0)

      // Configure watermark style
      ctx.globalAlpha = opts.opacity
      ctx.font = `${opts.fontSize}px ${opts.fontFamily}`
      ctx.fillStyle = opts.color

      const watermarkText = generateWatermarkText(opts)

      switch (opts.position) {
        case 'diagonal':
          drawDiagonalWatermark(ctx, canvas, watermarkText, opts)
          break
        case 'corners':
          drawCornerWatermarks(ctx, canvas, watermarkText, opts)
          break
        case 'center':
          drawCenterWatermark(ctx, canvas, watermarkText, opts)
          break
        case 'tiled':
          drawTiledWatermark(ctx, canvas, watermarkText, opts)
          break
      }

      resolve(canvas.toDataURL('image/png'))
    }

    if (imageElement.complete) {
      processImage()
    } else {
      imageElement.onload = processImage
      imageElement.onerror = () => reject(new Error('Image failed to load'))
    }
  })
}

/**
 * Draws a single diagonal watermark across the center
 */
function drawDiagonalWatermark(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  text: string,
  opts: Required<WatermarkOptions>
): void {
  ctx.save()
  ctx.translate(canvas.width / 2, canvas.height / 2)
  ctx.rotate((opts.rotation * Math.PI) / 180)
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, 0, 0)
  ctx.restore()
}

/**
 * Draws watermarks in all four corners
 */
function drawCornerWatermarks(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  text: string,
  opts: Required<WatermarkOptions>
): void {
  const padding = 20
  const positions = [
    { x: padding, y: padding, align: 'left' as const, baseline: 'top' as const },
    { x: canvas.width - padding, y: padding, align: 'right' as const, baseline: 'top' as const },
    { x: padding, y: canvas.height - padding, align: 'left' as const, baseline: 'bottom' as const },
    { x: canvas.width - padding, y: canvas.height - padding, align: 'right' as const, baseline: 'bottom' as const },
  ]

  ctx.font = `${opts.fontSize * 0.75}px ${opts.fontFamily}`

  positions.forEach((pos) => {
    ctx.textAlign = pos.align
    ctx.textBaseline = pos.baseline
    ctx.fillText(text, pos.x, pos.y)
  })
}

/**
 * Draws a centered watermark
 */
function drawCenterWatermark(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  text: string,
  opts: Required<WatermarkOptions>
): void {
  ctx.save()
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.font = `${opts.fontSize * 2}px ${opts.fontFamily}`
  ctx.fillText(text, canvas.width / 2, canvas.height / 2)
  ctx.restore()
}

/**
 * Draws tiled watermarks across the entire canvas
 */
function drawTiledWatermark(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  text: string,
  opts: Required<WatermarkOptions>
): void {
  const stepX = 200
  const stepY = 100

  ctx.save()
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'

  for (let y = 0; y < canvas.height + stepY; y += stepY) {
    for (let x = 0; x < canvas.width + stepX; x += stepX) {
      ctx.save()
      ctx.translate(x, y)
      ctx.rotate((opts.rotation * Math.PI) / 180)
      ctx.fillText(text, 0, 0)
      ctx.restore()
    }
  }

  ctx.restore()
}

/**
 * Creates a CSS-based watermark overlay for content areas
 * @param container - The container element to add the watermark to
 * @param options - Watermark configuration options
 * @returns The created watermark element
 */
export function createContentWatermark(
  container: HTMLElement,
  options: Partial<WatermarkOptions> = {}
): HTMLDivElement {
  const opts = { ...defaultOptions, ...options }
  const watermarkText = generateWatermarkText(opts)

  // Create watermark canvas
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')

  if (!ctx) {
    throw new Error('Could not get canvas context')
  }

  canvas.width = 300
  canvas.height = 200

  ctx.font = `${opts.fontSize}px ${opts.fontFamily}`
  ctx.fillStyle = opts.color
  ctx.globalAlpha = opts.opacity * 0.5 // Even more subtle for content overlays

  ctx.save()
  ctx.translate(canvas.width / 2, canvas.height / 2)
  ctx.rotate((opts.rotation * Math.PI) / 180)
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(watermarkText, 0, 0)
  ctx.restore()

  // Create overlay element
  const overlay = document.createElement('div')
  overlay.className = 'watermark-overlay'
  overlay.style.cssText = `
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background-image: url(${canvas.toDataURL()});
    background-repeat: repeat;
    z-index: 1000;
    opacity: ${opts.opacity};
  `

  // Ensure container has relative positioning
  const containerPosition = window.getComputedStyle(container).position
  if (containerPosition === 'static') {
    container.style.position = 'relative'
  }

  container.appendChild(overlay)

  return overlay
}

/**
 * Removes a content watermark
 * @param overlay - The watermark overlay element to remove
 */
export function removeContentWatermark(overlay: HTMLDivElement): void {
  overlay.parentNode?.removeChild(overlay)
}

/**
 * Applies watermark to all images within a container
 * @param container - The container element
 * @param options - Watermark configuration options
 */
export async function watermarkAllImages(
  container: HTMLElement,
  options: Partial<WatermarkOptions> = {}
): Promise<void> {
  const images = container.querySelectorAll('img')

  for (const img of images) {
    if (img.dataset.watermarked === 'true') {
      continue
    }

    try {
      const watermarkedSrc = await addImageWatermark(img as HTMLImageElement, options)
      img.src = watermarkedSrc
      img.dataset.watermarked = 'true'
    } catch (error) {
      console.error('Failed to watermark image:', error)
    }
  }
}

/**
 * Vue composable for easy watermark integration
 */
export function useWatermark(options: Partial<WatermarkOptions> = {}) {
  return {
    addImageWatermark: (img: HTMLImageElement) => addImageWatermark(img, options),
    createContentWatermark: (container: HTMLElement) => createContentWatermark(container, options),
    watermarkAllImages: (container: HTMLElement) => watermarkAllImages(container, options),
    generateWatermarkText: () => generateWatermarkText(options),
  }
}
