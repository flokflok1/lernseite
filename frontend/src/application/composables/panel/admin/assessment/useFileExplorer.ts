/**
 * Core state manager for the Exam Archive File Explorer.
 *
 * Manages program selection, folder navigation, sidebar tree,
 * and CRUD operations on folders/files.
 */

import { ref, computed, onMounted } from 'vue'
import type {
  ArchiveFolder,
  ArchiveFile,
  FolderContents,
  ExamProgram,
} from '@/infrastructure/api/clients/panel/admin/exams/folders.api'
import {
  fetchPrograms,
  fetchSidebarTree,
  fetchFolderContents,
  fetchProgramRoot,
  createFolder,
  updateFolder as apiFolderUpdate,
  moveFolder as apiFolderMove,
  deleteFolder as apiFolderDelete,
  moveFileToFolder,
} from '@/infrastructure/api/clients/panel/admin/exams/folders.api'

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const VIEW_MODE_KEY = 'lsx:exam-archive:view-mode'

// ---------------------------------------------------------------------------
// Composable
// ---------------------------------------------------------------------------

export function useFileExplorer() {
  // ── State ──────────────────────────────────────────────────────────────
  const programs = ref<ExamProgram[]>([])
  const currentProgramId = ref<string | null>(null)
  const currentFolderId = ref<string | null>(null)
  const sidebarTree = ref<ArchiveFolder[]>([])
  const contents = ref<FolderContents | null>(null)
  const viewMode = ref<'grid' | 'list'>('grid')
  const loading = ref(false)
  const error = ref<string | null>(null)
  const searchQuery = ref('')

  // ── Computed ───────────────────────────────────────────────────────────

  const currentProgram = computed(() =>
    programs.value.find((p) => p.program_id === currentProgramId.value) ?? null,
  )

  const breadcrumb = computed(() => contents.value?.breadcrumb ?? [])

  const folders = computed<ArchiveFolder[]>(() => contents.value?.children ?? [])

  const files = computed<ArchiveFile[]>(() => contents.value?.files ?? [])

  const isEmpty = computed(
    () => folders.value.length === 0 && files.value.length === 0,
  )

  const stats = computed(() => {
    const folderCount = folders.value.length
    const fileCount = files.value.length
    const questionCount = files.value.reduce(
      (sum, f) => sum + (f.question_count || 0),
      0,
    )
    return { folderCount, fileCount, questionCount }
  })

  // ── Actions ────────────────────────────────────────────────────────────

  async function loadPrograms() {
    loading.value = true
    error.value = null
    try {
      const res = await fetchPrograms()
      programs.value = res.data
      if (programs.value.length > 0 && !currentProgramId.value) {
        await selectProgram(String(programs.value[0].program_id))
      }
    } catch (e) {
      error.value = 'Failed to load programs'
      console.warn('[FileExplorer] loadPrograms failed:', e)
    } finally {
      loading.value = false
    }
  }

  async function selectProgram(programId: string) {
    loading.value = true
    error.value = null
    currentProgramId.value = programId
    currentFolderId.value = null
    try {
      const [treeRes, contentsRes] = await Promise.all([
        fetchSidebarTree(programId),
        fetchProgramRoot(programId),
      ])
      sidebarTree.value = treeRes.data
      contents.value = contentsRes.data
    } catch (e) {
      error.value = 'Failed to load program'
      console.warn('[FileExplorer] selectProgram failed:', e)
    } finally {
      loading.value = false
    }
  }

  async function navigateToFolder(folderId: string) {
    loading.value = true
    error.value = null
    currentFolderId.value = folderId
    try {
      const res = await fetchFolderContents(folderId)
      contents.value = res.data
    } catch (e) {
      error.value = 'Failed to load folder'
      console.warn('[FileExplorer] navigateToFolder failed:', e)
    } finally {
      loading.value = false
    }
  }

  async function navigateUp() {
    const parentId = contents.value?.folder?.parent_folder_id ?? null
    if (parentId) {
      await navigateToFolder(parentId)
    } else if (currentProgramId.value) {
      currentFolderId.value = null
      await selectProgram(currentProgramId.value)
    }
  }

  async function navigateToBreadcrumb(folderId: string | null) {
    if (folderId === null && currentProgramId.value) {
      currentFolderId.value = null
      await selectProgram(currentProgramId.value)
    } else if (folderId) {
      await navigateToFolder(folderId)
    }
  }

  async function refresh() {
    if (currentFolderId.value) {
      await navigateToFolder(currentFolderId.value)
    } else if (currentProgramId.value) {
      await selectProgram(currentProgramId.value)
    }
    // Also refresh sidebar tree
    if (currentProgramId.value) {
      try {
        const treeRes = await fetchSidebarTree(currentProgramId.value)
        sidebarTree.value = treeRes.data
      } catch (e) {
        console.warn('[FileExplorer] sidebar refresh failed:', e)
      }
    }
  }

  async function handleCreateFolder(name: string, parentId?: string) {
    if (!currentProgramId.value) return
    error.value = null
    try {
      await createFolder({
        parent_folder_id: parentId ?? currentFolderId.value ?? null,
        program_id: currentProgramId.value,
        name,
      })
      await refresh()
    } catch (e) {
      error.value = 'Failed to create folder'
      console.warn('[FileExplorer] handleCreateFolder failed:', e)
    }
  }

  async function handleRenameFolder(folderId: string, newName: string) {
    error.value = null
    try {
      await apiFolderUpdate(folderId, { name: newName })
      await refresh()
    } catch (e) {
      error.value = 'Failed to rename folder'
      console.warn('[FileExplorer] handleRenameFolder failed:', e)
    }
  }

  async function handleDeleteFolder(folderId: string) {
    error.value = null
    try {
      await apiFolderDelete(folderId)
      // If we deleted the current folder, navigate up
      if (currentFolderId.value === folderId) {
        await navigateUp()
      } else {
        await refresh()
      }
    } catch (e) {
      error.value = 'Failed to delete folder'
      console.warn('[FileExplorer] handleDeleteFolder failed:', e)
    }
  }

  async function handleMoveItem(
    type: 'folder' | 'file',
    id: string,
    targetFolderId: string,
  ) {
    error.value = null
    try {
      if (type === 'folder') {
        await apiFolderMove(id, targetFolderId)
      } else {
        await moveFileToFolder(id, targetFolderId)
      }
      await refresh()
    } catch (e) {
      error.value = `Failed to move ${type}`
      console.warn('[FileExplorer] handleMoveItem failed:', e)
    }
  }

  function toggleViewMode() {
    viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid'
    persistViewMode()
  }

  // ── Persistence helpers ────────────────────────────────────────────────

  function restoreViewMode() {
    try {
      const stored = localStorage.getItem(VIEW_MODE_KEY)
      if (stored === 'grid' || stored === 'list') {
        viewMode.value = stored
      }
    } catch {
      /* ignore corrupt storage */
    }
  }

  function persistViewMode() {
    try {
      localStorage.setItem(VIEW_MODE_KEY, viewMode.value)
    } catch {
      /* quota exceeded etc. */
    }
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────

  onMounted(() => {
    restoreViewMode()
    loadPrograms()
  })

  // ── Return ─────────────────────────────────────────────────────────────

  return {
    // State
    programs,
    currentProgramId,
    currentFolderId,
    sidebarTree,
    contents,
    viewMode,
    loading,
    error,
    searchQuery,
    // Computed
    currentProgram,
    breadcrumb,
    folders,
    files,
    isEmpty,
    stats,
    // Actions
    loadPrograms,
    selectProgram,
    navigateToFolder,
    navigateUp,
    navigateToBreadcrumb,
    refresh,
    handleCreateFolder,
    handleRenameFolder,
    handleDeleteFolder,
    handleMoveItem,
    toggleViewMode,
  }
}
