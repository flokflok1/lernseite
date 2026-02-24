/**
 * Cross-window synchronization via SharedWorker.
 *
 * Connects to the SharedWorker, provides send/listen helpers,
 * and handles graceful degradation (SharedWorker not supported).
 *
 * Usage:
 *   const { sendSync, onSync, isConnected } = useWindowSync()
 *   onSync('action:popin', (msg) => { ... })
 *   sendSync('action:popout', { windowType: 'admin-ai-editor' })
 */

import { ref, onUnmounted, getCurrentInstance } from 'vue'

export interface SyncMessage {
  type: string
  payload?: Record<string, unknown>
  senderId?: string
}

// Singleton: one worker connection per browser tab
let workerPort: MessagePort | null = null
const listeners = new Map<string, Set<(msg: SyncMessage) => void>>()
const tabId = `tab-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`

function ensureWorker(): MessagePort | null {
  if (workerPort) return workerPort

  if (typeof SharedWorker === 'undefined') {
    console.warn('[WindowSync] SharedWorker not supported — cross-window sync disabled')
    return null
  }

  try {
    const worker = new SharedWorker(
      new URL('@/infrastructure/workers/sync.shared-worker.ts', import.meta.url),
      { type: 'module', name: 'lsx-sync' }
    )
    workerPort = worker.port

    workerPort.onmessage = (event: MessageEvent<SyncMessage>) => {
      const msg = event.data
      const handlers = listeners.get(msg.type)
      if (handlers) {
        for (const handler of handlers) {
          handler(msg)
        }
      }
    }

    workerPort.start()
    return workerPort
  } catch (e) {
    console.error('[WindowSync] Failed to create SharedWorker:', e)
    return null
  }
}

/**
 * Send a message to all other windows.
 */
export function sendSync(type: string, payload?: Record<string, unknown>): void {
  const port = ensureWorker()
  if (!port) return

  const msg: SyncMessage = { type, payload, senderId: tabId }
  port.postMessage(msg)
}

/**
 * Composable: subscribe to sync messages (auto-unsubscribes on unmount).
 */
export function useWindowSync() {
  ensureWorker()

  const isConnected = ref(workerPort !== null)

  function onSync(type: string, handler: (msg: SyncMessage) => void): void {
    if (!listeners.has(type)) {
      listeners.set(type, new Set())
    }
    listeners.get(type)!.add(handler)

    onUnmounted(() => {
      listeners.get(type)?.delete(handler)
    })
  }

  // Send disconnect when tab unloads (best-effort cleanup)
  if (typeof window !== 'undefined') {
    const handleUnload = () => sendSync('worker:disconnect')
    window.addEventListener('beforeunload', handleUnload)

    if (getCurrentInstance()) {
      onUnmounted(() => {
        window.removeEventListener('beforeunload', handleUnload)
      })
    }
  }

  return { sendSync, onSync, isConnected, tabId }
}
