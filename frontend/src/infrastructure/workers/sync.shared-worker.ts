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

self.onconnect = (event: MessageEvent) => {
  const port = event.ports[0]
  ports.push(port)

  port.onmessage = (msg: MessageEvent) => {
    // Broadcast to all OTHER connected ports
    for (const p of ports) {
      if (p !== port) {
        p.postMessage(msg.data)
      }
    }
  }

  port.start()
}
