import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePanelStore } from '@/application/stores/modules/desktop/panel.store'

describe('usePanelStore - Multi-Window Support', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('openPanel', () => {
    it('should generate unique IDs for multiple panels', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'AI Editor: Course 1',
        icon: '🤖'
      })

      const panel2Id = store.openPanel({
        type: 'admin-course-editor',
        title: 'Manual Editor: Course 2',
        icon: '📝'
      })

      const panel3Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'AI Editor: Course 3',
        icon: '🤖'
      })

      expect(panel1Id).toBeTruthy()
      expect(panel2Id).toBeTruthy()
      expect(panel3Id).toBeTruthy()
      expect(panel1Id).not.toBe(panel2Id)
      expect(panel2Id).not.toBe(panel3Id)
      expect(panel1Id).not.toBe(panel3Id)
    })

    it('should cascade position for multiple panels', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 1',
        icon: '🤖'
      })

      const panel2Id = store.openPanel({
        type: 'admin-course-editor',
        title: 'Panel 2',
        icon: '📝'
      })

      const panel3Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 3',
        icon: '🤖'
      })

      const panel1 = store.getPanelById(panel1Id)
      const panel2 = store.getPanelById(panel2Id)
      const panel3 = store.getPanelById(panel3Id)

      expect(panel1).toBeTruthy()
      expect(panel2).toBeTruthy()
      expect(panel3).toBeTruthy()

      // Verify cascade positions (30px offset)
      if (panel1 && panel2 && panel3) {
        // First panel should have default/base position
        expect(panel1.position.x).toBeGreaterThanOrEqual(0)
        expect(panel1.position.y).toBeGreaterThanOrEqual(0)

        // Second panel should be offset from first
        expect(panel2.position.x).toBeGreaterThanOrEqual(panel1.position.x + 30 - 10) // Allow small tolerance
        expect(panel2.position.y).toBeGreaterThanOrEqual(panel1.position.y + 30 - 10)

        // Third panel should be offset from second
        expect(panel3.position.x).toBeGreaterThanOrEqual(panel2.position.x + 30 - 10)
        expect(panel3.position.y).toBeGreaterThanOrEqual(panel2.position.y + 30 - 10)
      }
    })

    it('should set new panel as active with highest z-index', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 1',
        icon: '🤖'
      })

      const panel2Id = store.openPanel({
        type: 'admin-course-editor',
        title: 'Panel 2',
        icon: '📝'
      })

      const panel3Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 3',
        icon: '🤖'
      })

      const panel1 = store.getPanelById(panel1Id)
      const panel2 = store.getPanelById(panel2Id)
      const panel3 = store.getPanelById(panel3Id)

      expect(store.activePanelId).toBe(panel3Id)

      if (panel1 && panel2 && panel3) {
        expect(panel3.zIndex).toBeGreaterThan(panel2.zIndex)
        expect(panel2.zIndex).toBeGreaterThan(panel1.zIndex)
      }
    })

    it('should store panel metadata correctly', () => {
      const store = usePanelStore()

      const payload = { courseId: '123', courseTitle: 'Test Course' }
      const panelId = store.openPanel({
        type: 'admin-ai-editor',
        title: 'AI Editor: Test Course',
        icon: '🤖',
        payload
      })

      const panel = store.getPanelById(panelId)

      expect(panel).toBeTruthy()
      if (panel) {
        expect(panel.type).toBe('admin-ai-editor')
        expect(panel.title).toBe('AI Editor: Test Course')
        expect(panel.icon).toBe('🤖')
        expect(panel.payload).toEqual(payload)
        expect(panel.minimized).toBe(false)
        expect(panel.maximized).toBe(false)
      }
    })

    it('should support custom panel sizes', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'AI Editor',
        size: { width: 1400, height: 900 }
      })

      const panel2Id = store.openPanel({
        type: 'admin-course-editor',
        title: 'Manual Editor',
        size: { width: 1200, height: 800 }
      })

      const panel1 = store.getPanelById(panel1Id)
      const panel2 = store.getPanelById(panel2Id)

      expect(panel1?.size).toEqual({ width: 1400, height: 900 })
      expect(panel2?.size).toEqual({ width: 1200, height: 800 })
    })
  })

  describe('closePanel', () => {
    it('should remove panel from store', () => {
      const store = usePanelStore()

      const panelId = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 1',
        icon: '🤖'
      })

      expect(store.getPanelById(panelId)).toBeTruthy()

      store.closePanel(panelId)

      expect(store.getPanelById(panelId)).toBeUndefined()
    })

    it('should transfer focus when closing active panel', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 1',
        icon: '🤖'
      })

      const panel2Id = store.openPanel({
        type: 'admin-course-editor',
        title: 'Panel 2',
        icon: '📝'
      })

      const panel3Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 3',
        icon: '🤖'
      })

      expect(store.activePanelId).toBe(panel3Id)

      // Close active panel (panel 3)
      store.closePanel(panel3Id)

      // Focus should transfer to next available panel
      expect(store.getPanelById(panel3Id)).toBeUndefined()
      expect(store.activePanelId).toBeTruthy()
      expect(store.activePanelId).not.toBe(panel3Id)
    })

    it('should handle closing multiple panels', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 1',
        icon: '🤖'
      })

      const panel2Id = store.openPanel({
        type: 'admin-course-editor',
        title: 'Panel 2',
        icon: '📝'
      })

      const panel3Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 3',
        icon: '🤖'
      })

      // Close panels
      store.closePanel(panel2Id)
      store.closePanel(panel1Id)

      // Verify
      expect(store.getPanelById(panel1Id)).toBeUndefined()
      expect(store.getPanelById(panel2Id)).toBeUndefined()
      expect(store.getPanelById(panel3Id)).toBeTruthy()
      expect(store.activePanelId).toBe(panel3Id)
    })
  })

  describe('focusPanel', () => {
    it('should update active panel and z-index', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 1',
        icon: '🤖'
      })

      const panel2Id = store.openPanel({
        type: 'admin-course-editor',
        title: 'Panel 2',
        icon: '📝'
      })

      const panel3Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 3',
        icon: '🤖'
      })

      const panel2Before = store.getPanelById(panel2Id)
      const panel3Before = store.getPanelById(panel3Id)

      expect(store.activePanelId).toBe(panel3Id)
      expect(panel3Before?.zIndex).toBeGreaterThan(panel2Before!.zIndex)

      // Focus panel 2
      store.focusPanel(panel2Id)

      const panel2After = store.getPanelById(panel2Id)
      const panel3After = store.getPanelById(panel3Id)

      expect(store.activePanelId).toBe(panel2Id)
      expect(panel2After?.zIndex).toBeGreaterThan(panel3After!.zIndex)
    })
  })

  describe('minimizePanel', () => {
    it('should set minimized flag', () => {
      const store = usePanelStore()

      const panelId = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 1',
        icon: '🤖'
      })

      const panelBefore = store.getPanelById(panelId)
      expect(panelBefore?.minimized).toBe(false)

      store.minimizePanel(panelId)

      const panelAfter = store.getPanelById(panelId)
      expect(panelAfter?.minimized).toBe(true)
    })
  })

  describe('restorePanel', () => {
    it('should restore minimized panel and update z-index', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'Panel 1',
        icon: '🤖'
      })

      const panel2Id = store.openPanel({
        type: 'admin-course-editor',
        title: 'Panel 2',
        icon: '📝'
      })

      store.minimizePanel(panel1Id)

      const panelMinimized = store.getPanelById(panel1Id)
      expect(panelMinimized?.minimized).toBe(true)

      store.restorePanel(panel1Id)

      const panelRestored = store.getPanelById(panel1Id)
      expect(panelRestored?.minimized).toBe(false)
      expect(panelRestored?.zIndex).toBeGreaterThan(store.getPanelById(panel2Id)!.zIndex)
    })
  })

  describe('Multi-Window Scenario', () => {
    it('should handle 3+ simultaneous editors with independent state', () => {
      const store = usePanelStore()

      // Open 3 editors
      const aiEditorId = store.openPanel({
        type: 'admin-ai-editor',
        title: 'AI Editor: Python Course',
        icon: '🤖',
        payload: { courseId: '1', courseTitle: 'Python Course' },
        size: { width: 1400, height: 900 }
      })

      const manualEditorId = store.openPanel({
        type: 'admin-course-editor',
        title: 'Manual Editor: JavaScript Course',
        icon: '📝',
        payload: { courseId: '2', courseTitle: 'JavaScript Course' },
        size: { width: 1200, height: 800 }
      })

      const aiEditor2Id = store.openPanel({
        type: 'admin-ai-editor',
        title: 'AI Editor: Web Development',
        icon: '🤖',
        payload: { courseId: '3', courseTitle: 'Web Development' },
        size: { width: 1400, height: 900 }
      })

      // Verify all panels exist
      expect(store.panels).toHaveLength(3)
      expect(store.getPanelById(aiEditorId)).toBeTruthy()
      expect(store.getPanelById(manualEditorId)).toBeTruthy()
      expect(store.getPanelById(aiEditor2Id)).toBeTruthy()

      // Verify independent state
      const aiEditor = store.getPanelById(aiEditorId)!
      const manualEditor = store.getPanelById(manualEditorId)!
      const aiEditor2 = store.getPanelById(aiEditor2Id)!

      expect(aiEditor.type).toBe('admin-ai-editor')
      expect(manualEditor.type).toBe('admin-course-editor')
      expect(aiEditor2.type).toBe('admin-ai-editor')

      expect(aiEditor.payload?.courseId).toBe('1')
      expect(manualEditor.payload?.courseId).toBe('2')
      expect(aiEditor2.payload?.courseId).toBe('3')

      // Verify z-index hierarchy
      expect(aiEditor2.zIndex).toBeGreaterThan(manualEditor.zIndex)
      expect(manualEditor.zIndex).toBeGreaterThan(aiEditor.zIndex)

      // Verify positions are cascaded
      expect(manualEditor.position.x).toBeGreaterThan(aiEditor.position.x)
      expect(manualEditor.position.y).toBeGreaterThan(aiEditor.position.y)
      expect(aiEditor2.position.x).toBeGreaterThan(manualEditor.position.x)
      expect(aiEditor2.position.y).toBeGreaterThan(manualEditor.position.y)
    })

    it('should allow independent minimize/restore of multiple panels', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({ type: 'admin-ai-editor', title: 'Panel 1' })
      const panel2Id = store.openPanel({ type: 'admin-course-editor', title: 'Panel 2' })
      const panel3Id = store.openPanel({ type: 'admin-ai-editor', title: 'Panel 3' })

      // Minimize panel 1
      store.minimizePanel(panel1Id)

      // Verify only panel 1 is minimized
      expect(store.getPanelById(panel1Id)?.minimized).toBe(true)
      expect(store.getPanelById(panel2Id)?.minimized).toBe(false)
      expect(store.getPanelById(panel3Id)?.minimized).toBe(false)

      // Minimize panel 3
      store.minimizePanel(panel3Id)

      expect(store.getPanelById(panel1Id)?.minimized).toBe(true)
      expect(store.getPanelById(panel2Id)?.minimized).toBe(false)
      expect(store.getPanelById(panel3Id)?.minimized).toBe(true)

      // Restore panel 1
      store.restorePanel(panel1Id)

      expect(store.getPanelById(panel1Id)?.minimized).toBe(false)
      expect(store.getPanelById(panel3Id)?.minimized).toBe(true)
    })

    it('should manage focus correctly with multiple panels', () => {
      const store = usePanelStore()

      const panel1Id = store.openPanel({ type: 'admin-ai-editor', title: 'Panel 1' })
      const panel2Id = store.openPanel({ type: 'admin-course-editor', title: 'Panel 2' })
      const panel3Id = store.openPanel({ type: 'admin-ai-editor', title: 'Panel 3' })

      // Panel 3 should be active initially (last opened)
      expect(store.activePanelId).toBe(panel3Id)

      // Focus panel 1
      store.focusPanel(panel1Id)
      expect(store.activePanelId).toBe(panel1Id)

      // Focus panel 2
      store.focusPanel(panel2Id)
      expect(store.activePanelId).toBe(panel2Id)

      // Focus panel 3
      store.focusPanel(panel3Id)
      expect(store.activePanelId).toBe(panel3Id)
    })
  })
})
