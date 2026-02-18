/**
 * Whiteboard Types
 *
 * Shared type definitions for the InteractiveWhiteboard component
 * and its composable useWhiteboardCanvas.
 */

export interface SchemaRow {
  name: string
  operator: string
  value: string
  highlight?: boolean
}

export interface WhiteboardAction {
  type: 'write' | 'draw' | 'highlight' | 'arrow' | 'underline' | 'box' | 'clear' | 'schema'
  content?: string
  position: { x: number; y: number }
  endPosition?: { x: number; y: number }
  duration: number
  color?: string
  fontSize?: number
  fontWeight?: 'normal' | 'bold'
  lineWidth?: number
  schema?: SchemaRow[]
}

export interface ActionHistoryEntry {
  action: WhiteboardAction
  imageData: ImageData
}
