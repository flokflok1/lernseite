/**
 * LSX Cross-Window Sync SharedWorker
 *
 * Pure message relay — broadcasts messages to all connected ports
 * except the sender. No state stored in the worker.
 *
 * Used by pop-out windows feature for cross-window communication.
 */

const ports: MessagePort[] = []

declare const self: SharedWorkerGlobalScope

function removePort(port: MessagePort): void {
  const idx = ports.indexOf(port)
  if (idx !== -1) ports.splice(idx, 1)
}

self.onconnect = (event: MessageEvent) => {
  const port = event.ports[0]
  ports.push(port)

  port.onmessage = (msg: MessageEvent) => {
    // Allow clients to explicitly disconnect (cleanup dead ports)
    if (msg.data?.type === 'worker:disconnect') {
      removePort(port)
      return
    }

    // Broadcast to all OTHER connected ports
    for (const p of ports) {
      if (p !== port) {
        p.postMessage(msg.data)
      }
    }
  }

  // Remove port when it errors (tab crash / unexpected close)
  port.onmessageerror = () => {
    removePort(port)
  }

  port.start()
}
