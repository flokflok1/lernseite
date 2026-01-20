/**
 * Copy Protection Utilities
 *
 * Provides functions to protect content from unauthorized copying.
 * Note: These are client-side protections and can be bypassed by determined users.
 * They serve as a deterrent and legal notice mechanism.
 */

/**
 * Event handler storage for cleanup
 */
const eventHandlers = new WeakMap<HTMLElement, {
  contextmenu: (e: Event) => void
  selectstart: (e: Event) => void
  dragstart: (e: Event) => void
}>()

/**
 * Enables copy protection on a specific element
 * @param element - The HTML element to protect
 */
export function enableCopyProtection(element: HTMLElement): void {
  const handlers = {
    contextmenu: (e: Event) => e.preventDefault(),
    selectstart: (e: Event) => e.preventDefault(),
    dragstart: (e: Event) => e.preventDefault(),
  }

  element.addEventListener('contextmenu', handlers.contextmenu)
  element.addEventListener('selectstart', handlers.selectstart)
  element.addEventListener('dragstart', handlers.dragstart)

  eventHandlers.set(element, handlers)
}

/**
 * Disables copy protection on a specific element
 * @param element - The HTML element to unprotect
 */
export function disableCopyProtection(element: HTMLElement): void {
  const handlers = eventHandlers.get(element)

  if (handlers) {
    element.removeEventListener('contextmenu', handlers.contextmenu)
    element.removeEventListener('selectstart', handlers.selectstart)
    element.removeEventListener('dragstart', handlers.dragstart)
    eventHandlers.delete(element)
  }
}

/**
 * Blocks keyboard shortcuts that could be used for copying
 * @param event - The keyboard event
 * @param callback - Optional callback when a blocked key is pressed
 * @returns true if the shortcut was blocked
 */
export function blockCopyShortcuts(
  event: KeyboardEvent,
  callback?: () => void
): boolean {
  const blockedCombinations = [
    { ctrl: true, key: 'c' },    // Copy
    { ctrl: true, key: 'a' },    // Select All
    { ctrl: true, key: 's' },    // Save
    { ctrl: true, key: 'p' },    // Print
    { ctrl: true, key: 'u' },    // View Source
    { ctrl: true, shift: true, key: 'i' },  // Dev Tools
    { ctrl: true, shift: true, key: 'j' },  // Console
    { key: 'F12' },              // Dev Tools
    { key: 'PrintScreen' },      // Screenshot
  ]

  for (const combo of blockedCombinations) {
    const ctrlMatch = combo.ctrl ? event.ctrlKey || event.metaKey : true
    const shiftMatch = combo.shift ? event.shiftKey : !combo.shift
    const keyMatch = event.key.toLowerCase() === combo.key?.toLowerCase() ||
                     event.code === combo.key

    if (ctrlMatch && shiftMatch && keyMatch) {
      event.preventDefault()
      callback?.()
      return true
    }
  }

  return false
}

/**
 * Adds a copyright notice to copied text
 * This doesn't block copying but adds attribution
 * @param element - The element to monitor for copy events
 * @param copyrightText - The copyright notice to append
 */
export function addCopyrightToClipboard(
  element: HTMLElement,
  copyrightText: string = '\n\n© LernsystemX - https://lernsystemx.de'
): void {
  element.addEventListener('copy', (e: ClipboardEvent) => {
    if (e.clipboardData) {
      const selection = window.getSelection()
      const originalText = selection?.toString() || ''
      e.clipboardData.setData('text/plain', originalText + copyrightText)
      e.preventDefault()
    }
  })
}

/**
 * Disables text selection via CSS class
 * @param element - The element to protect
 */
export function disableTextSelection(element: HTMLElement): void {
  element.style.userSelect = 'none'
  element.style.webkitUserSelect = 'none'
  // @ts-expect-error - msUserSelect is for IE
  element.style.msUserSelect = 'none'
}

/**
 * Enables text selection
 * @param element - The element to unprotect
 */
export function enableTextSelection(element: HTMLElement): void {
  element.style.userSelect = ''
  element.style.webkitUserSelect = ''
  // @ts-expect-error - msUserSelect is for IE
  element.style.msUserSelect = ''
}

/**
 * Detects if DevTools is open (basic detection)
 * Note: This is not foolproof and can be bypassed
 * @param callback - Called when DevTools appears to be open
 */
export function detectDevTools(callback: () => void): () => void {
  const threshold = 160
  let devtoolsOpen = false

  const check = () => {
    const widthThreshold = window.outerWidth - window.innerWidth > threshold
    const heightThreshold = window.outerHeight - window.innerHeight > threshold

    if (widthThreshold || heightThreshold) {
      if (!devtoolsOpen) {
        devtoolsOpen = true
        callback()
      }
    } else {
      devtoolsOpen = false
    }
  }

  const interval = setInterval(check, 1000)

  // Return cleanup function
  return () => clearInterval(interval)
}

/**
 * Creates a transparent overlay to prevent direct image downloading
 * @param imageElement - The image element to protect
 */
export function protectImage(imageElement: HTMLImageElement): HTMLDivElement {
  const wrapper = document.createElement('div')
  wrapper.style.position = 'relative'
  wrapper.style.display = 'inline-block'

  const overlay = document.createElement('div')
  overlay.style.position = 'absolute'
  overlay.style.top = '0'
  overlay.style.left = '0'
  overlay.style.width = '100%'
  overlay.style.height = '100%'
  overlay.style.background = 'transparent'

  imageElement.parentNode?.insertBefore(wrapper, imageElement)
  wrapper.appendChild(imageElement)
  wrapper.appendChild(overlay)

  return wrapper
}
