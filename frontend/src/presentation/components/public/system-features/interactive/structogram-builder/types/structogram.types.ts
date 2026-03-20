export type BlockType = 'sequence' | 'if' | 'while' | 'switch'

export interface SequenceBlock {
  id: string
  type: 'sequence'
  text: string
}

export interface IfBlock {
  id: string
  type: 'if'
  condition: string
  yes: StructogramBlock[]
  no: StructogramBlock[]
}

export interface WhileBlock {
  id: string
  type: 'while'
  condition: string
  body: StructogramBlock[]
}

export interface SwitchCase {
  label: string
  blocks: StructogramBlock[]
}

export interface SwitchBlock {
  id: string
  type: 'switch'
  expression: string
  cases: SwitchCase[]
}

export type StructogramBlock = SequenceBlock | IfBlock | WhileBlock | SwitchBlock

export interface StructogramData {
  blocks: StructogramBlock[]
}
