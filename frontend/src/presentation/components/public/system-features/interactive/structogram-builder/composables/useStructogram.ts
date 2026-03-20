import { ref, computed } from 'vue'
import type {
  StructogramBlock, StructogramData, BlockType,
  SequenceBlock, IfBlock, WhileBlock, SwitchBlock,
} from '../types/structogram.types'

let idCounter = 0
function newId(): string {
  return `b${++idCounter}`
}

export function useStructogram(initial?: StructogramData) {
  const blocks = ref<StructogramBlock[]>(initial?.blocks || [])
  const selectedId = ref<string | null>(null)

  function createBlock(type: BlockType): StructogramBlock {
    switch (type) {
      case 'sequence':
        return { id: newId(), type: 'sequence', text: '' } as SequenceBlock
      case 'if':
        return { id: newId(), type: 'if', condition: '', yes: [], no: [] } as IfBlock
      case 'while':
        return { id: newId(), type: 'while', condition: '', body: [] } as WhileBlock
      case 'switch':
        return {
          id: newId(), type: 'switch', expression: '',
          cases: [
            { label: 'Fall 1', blocks: [] },
            { label: 'Sonst', blocks: [] },
          ],
        } as SwitchBlock
    }
  }

  function addBlock(type: BlockType, targetList?: StructogramBlock[]) {
    const block = createBlock(type)
    const list = targetList || blocks.value
    list.push(block)
    selectedId.value = block.id
  }

  function findAndRemove(id: string, list: StructogramBlock[]): boolean {
    const idx = list.findIndex(b => b.id === id)
    if (idx !== -1) { list.splice(idx, 1); return true }
    for (const b of list) {
      if (b.type === 'if') {
        if (findAndRemove(id, b.yes)) return true
        if (findAndRemove(id, b.no)) return true
      } else if (b.type === 'while') {
        if (findAndRemove(id, b.body)) return true
      } else if (b.type === 'switch') {
        for (const c of b.cases) {
          if (findAndRemove(id, c.blocks)) return true
        }
      }
    }
    return false
  }

  function removeBlock(id: string) {
    findAndRemove(id, blocks.value)
    if (selectedId.value === id) selectedId.value = null
  }

  function findBlock(id: string, list: StructogramBlock[]): StructogramBlock | null {
    for (const b of list) {
      if (b.id === id) return b
      if (b.type === 'if') {
        const found = findBlock(id, b.yes) || findBlock(id, b.no)
        if (found) return found
      } else if (b.type === 'while') {
        const found = findBlock(id, b.body)
        if (found) return found
      } else if (b.type === 'switch') {
        for (const c of b.cases) {
          const found = findBlock(id, c.blocks)
          if (found) return found
        }
      }
    }
    return null
  }

  function updateText(id: string, field: string, value: string) {
    const block = findBlock(id, blocks.value)
    if (block) (block as Record<string, unknown>)[field] = value
  }

  function moveBlock(id: string, direction: 'up' | 'down', list?: StructogramBlock[]) {
    const arr = list || blocks.value
    const idx = arr.findIndex(b => b.id === id)
    if (idx === -1) {
      for (const b of arr) {
        if (b.type === 'if') {
          moveBlock(id, direction, b.yes)
          moveBlock(id, direction, b.no)
        } else if (b.type === 'while') {
          moveBlock(id, direction, b.body)
        } else if (b.type === 'switch') {
          for (const c of b.cases) moveBlock(id, direction, c.blocks)
        }
      }
      return
    }
    const swapIdx = direction === 'up' ? idx - 1 : idx + 1
    if (swapIdx < 0 || swapIdx >= arr.length) return
    ;[arr[idx], arr[swapIdx]] = [arr[swapIdx], arr[idx]]
  }

  function clearAll() {
    blocks.value = []
    selectedId.value = null
  }

  const toJSON = computed<StructogramData>(() => ({ blocks: blocks.value }))

  const isEmpty = computed(() => blocks.value.length === 0)

  function toReadableText(list?: StructogramBlock[], indent = 0): string {
    const arr = list || blocks.value
    const pad = '  '.repeat(indent)
    return arr.map(b => {
      if (b.type === 'sequence') return `${pad}${b.text || '...'}`
      if (b.type === 'if') {
        const yes = toReadableText(b.yes, indent + 1)
        const no = toReadableText(b.no, indent + 1)
        return `${pad}WENN ${b.condition || '?'}:\n${pad}  JA:\n${yes}\n${pad}  NEIN:\n${no}`
      }
      if (b.type === 'while') {
        const body = toReadableText(b.body, indent + 1)
        return `${pad}SOLANGE ${b.condition || '?'}:\n${body}`
      }
      if (b.type === 'switch') {
        const cases = b.cases.map(c =>
          `${pad}  ${c.label}:\n${toReadableText(c.blocks, indent + 2)}`
        ).join('\n')
        return `${pad}FALLAUSWAHL ${b.expression || '?'}:\n${cases}`
      }
      return ''
    }).join('\n')
  }

  return {
    blocks,
    selectedId,
    addBlock,
    removeBlock,
    updateText,
    moveBlock,
    clearAll,
    toJSON,
    isEmpty,
    toReadableText,
  }
}
