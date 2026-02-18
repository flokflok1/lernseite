/**
 * useClassroomScene - Classroom environment with whiteboard
 *
 * Creates the classroom scene (floor, wall) and an interactive whiteboard
 * with dynamic canvas texture for displaying content.
 */

import * as THREE from 'three'

interface UseClassroomSceneReturn {
  createClassroomScene: (scene: THREE.Scene, showWhiteboard: boolean) => void
  createWhiteboard: (scene: THREE.Scene, content?: string) => void
  updateWhiteboard: (content: string) => void
  getWhiteboardTexture: () => THREE.CanvasTexture | null
}

export function useClassroomScene(): UseClassroomSceneReturn {
  let whiteboardTexture: THREE.CanvasTexture | null = null

  function createClassroomScene(scene: THREE.Scene, showWhiteboard: boolean): void {
    const floorGeometry = new THREE.PlaneGeometry(10, 10)
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a5568,
      roughness: 0.8
    })
    const floor = new THREE.Mesh(floorGeometry, floorMaterial)
    floor.rotation.x = -Math.PI / 2
    floor.position.y = 0
    floor.receiveShadow = true
    scene.add(floor)

    const wallGeometry = new THREE.PlaneGeometry(10, 5)
    const wallMaterial = new THREE.MeshStandardMaterial({
      color: 0x374151,
      roughness: 0.9
    })
    const wall = new THREE.Mesh(wallGeometry, wallMaterial)
    wall.position.set(0, 2.5, -2)
    scene.add(wall)

    if (showWhiteboard) {
      createWhiteboard(scene)
    }
  }

  function createWhiteboard(scene: THREE.Scene, content?: string): void {
    const frameGeometry = new THREE.BoxGeometry(3, 2, 0.1)
    const frameMaterial = new THREE.MeshStandardMaterial({
      color: 0x1f2937,
      roughness: 0.7
    })
    const frame = new THREE.Mesh(frameGeometry, frameMaterial)
    frame.position.set(0.5, 1.3, -1.9)
    scene.add(frame)

    const canvas = document.createElement('canvas')
    canvas.width = 1024
    canvas.height = 680
    const ctx = canvas.getContext('2d')!

    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    if (content) {
      drawWhiteboardText(ctx, content, canvas.width, canvas.height)
    }

    whiteboardTexture = new THREE.CanvasTexture(canvas)
    whiteboardTexture.needsUpdate = true

    const boardGeometry = new THREE.PlaneGeometry(2.8, 1.8)
    const boardMaterial = new THREE.MeshStandardMaterial({
      map: whiteboardTexture,
      roughness: 0.1
    })
    const whiteboardMesh = new THREE.Mesh(boardGeometry, boardMaterial)
    whiteboardMesh.position.set(0.5, 1.3, -1.84)
    scene.add(whiteboardMesh)
  }

  function updateWhiteboard(content: string): void {
    if (!whiteboardTexture) return

    const canvas = whiteboardTexture.image as HTMLCanvasElement
    const ctx = canvas.getContext('2d')!

    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    drawWhiteboardText(ctx, content, canvas.width, canvas.height)

    whiteboardTexture.needsUpdate = true
  }

  function drawWhiteboardText(
    ctx: CanvasRenderingContext2D,
    content: string,
    canvasWidth: number,
    _canvasHeight: number
  ): void {
    ctx.fillStyle = '#1f2937'
    ctx.font = 'bold 48px Arial'
    ctx.textAlign = 'center'

    const lines = wrapText(ctx, content, 900)
    lines.forEach((line, i) => {
      ctx.fillText(line, canvasWidth / 2, 80 + i * 60)
    })
  }

  function wrapText(
    ctx: CanvasRenderingContext2D,
    text: string,
    maxWidth: number
  ): string[] {
    const words = text.split(' ')
    const lines: string[] = []
    let currentLine = ''

    words.forEach(word => {
      const testLine = currentLine + (currentLine ? ' ' : '') + word
      const metrics = ctx.measureText(testLine)

      if (metrics.width > maxWidth && currentLine) {
        lines.push(currentLine)
        currentLine = word
      } else {
        currentLine = testLine
      }
    })

    if (currentLine) {
      lines.push(currentLine)
    }

    return lines
  }

  function getWhiteboardTexture(): THREE.CanvasTexture | null {
    return whiteboardTexture
  }

  return {
    createClassroomScene,
    createWhiteboard,
    updateWhiteboard,
    getWhiteboardTexture
  }
}
