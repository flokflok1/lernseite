/**
 * useUserManagement Composable
 *
 * Manages user administration actions: ban, unban, grant tokens,
 * verify creator. Encapsulates modal state, form data, and validations.
 */

import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usePanelStore } from '@/application/stores/modules/admin/panel.store'
import type { AdminUser, BanUserRequest } from '@/application/services/api/panel-admin'

export function useUserManagement() {
  const panelStore = usePanelStore()
  const router = useRouter()

  // ============================================================================
  // Search & Filters
  // ============================================================================

  const searchQuery = ref('')
  const roleFilter = ref('')
  const statusFilter = ref('')

  let searchTimeout: ReturnType<typeof setTimeout> | null = null

  function debouncedSearch(): void {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      loadUsers()
    }, 500)
  }

  async function loadUsers(): Promise<void> {
    await panelStore.loadUsers({
      search: searchQuery.value || undefined,
      role: roleFilter.value || undefined,
      status: statusFilter.value as any,
      page: panelStore.usersPage
    })
  }

  function resetFilters(): void {
    searchQuery.value = ''
    roleFilter.value = ''
    statusFilter.value = ''
    loadUsers()
  }

  function changePage(page: number): void {
    panelStore.usersPage = page
    loadUsers()
  }

  // ============================================================================
  // Navigation
  // ============================================================================

  function viewUserDetail(userId: string): void {
    router.push({ name: 'PanelUserDetail', params: { userId } })
  }

  // ============================================================================
  // Modal State
  // ============================================================================

  const showBanModal = ref(false)
  const showUnbanModal = ref(false)
  const showGrantTokensModal = ref(false)
  const showVerifyCreatorModal = ref(false)
  const selectedUser = ref<AdminUser | null>(null)

  // ============================================================================
  // Form Data
  // ============================================================================

  const banForm = ref<BanUserRequest>({
    reason: '',
    duration_days: 30,
    permanent: false,
    notify_user: true
  })

  const unbanForm = ref({ reason: '' })

  const grantTokensForm = ref({ amount: 0, reason: '' })

  const verifyCreatorForm = ref({ verified: true, reason: '' })

  // ============================================================================
  // Validations
  // ============================================================================

  const canSubmitBan = computed((): boolean => banForm.value.reason.length >= 10)
  const canSubmitUnban = computed((): boolean => unbanForm.value.reason.length >= 10)
  const canSubmitGrantTokens = computed((): boolean =>
    grantTokensForm.value.amount > 0 && grantTokensForm.value.reason.length >= 10
  )
  const canSubmitVerifyCreator = computed((): boolean => verifyCreatorForm.value.reason.length >= 10)

  // ============================================================================
  // Ban User
  // ============================================================================

  function openBanModal(user: AdminUser): void {
    selectedUser.value = user
    banForm.value = { reason: '', duration_days: 30, permanent: false, notify_user: true }
    showBanModal.value = true
  }

  function closeBanModal(): void {
    showBanModal.value = false
    selectedUser.value = null
  }

  async function confirmBan(): Promise<void> {
    if (!selectedUser.value || !canSubmitBan.value) return

    try {
      await panelStore.banUser(selectedUser.value.user_id, banForm.value)
      closeBanModal()
      await loadUsers()
    } catch (err) {
      console.error('Failed to ban user:', err)
    }
  }

  // ============================================================================
  // Unban User
  // ============================================================================

  function openUnbanModal(user: AdminUser): void {
    selectedUser.value = user
    unbanForm.value = { reason: '' }
    showUnbanModal.value = true
  }

  function closeUnbanModal(): void {
    showUnbanModal.value = false
    selectedUser.value = null
  }

  async function confirmUnban(): Promise<void> {
    if (!selectedUser.value || !canSubmitUnban.value) return

    try {
      await panelStore.unbanUser(selectedUser.value.user_id, unbanForm.value.reason)
      closeUnbanModal()
      await loadUsers()
    } catch (err) {
      console.error('Failed to unban user:', err)
    }
  }

  // ============================================================================
  // Grant Tokens
  // ============================================================================

  function openGrantTokensModal(user: AdminUser): void {
    selectedUser.value = user
    grantTokensForm.value = { amount: 0, reason: '' }
    showGrantTokensModal.value = true
  }

  function closeGrantTokensModal(): void {
    showGrantTokensModal.value = false
    selectedUser.value = null
  }

  async function confirmGrantTokens(): Promise<void> {
    if (!selectedUser.value || !canSubmitGrantTokens.value) return

    try {
      await panelStore.grantTokens(
        selectedUser.value.user_id,
        grantTokensForm.value.amount,
        grantTokensForm.value.reason
      )
      closeGrantTokensModal()
      await loadUsers()
    } catch (err) {
      console.error('Failed to grant tokens:', err)
    }
  }

  // ============================================================================
  // Verify Creator
  // ============================================================================

  function openVerifyCreatorModal(user: AdminUser): void {
    selectedUser.value = user
    verifyCreatorForm.value = { verified: true, reason: '' }
    showVerifyCreatorModal.value = true
  }

  function closeVerifyCreatorModal(): void {
    showVerifyCreatorModal.value = false
    selectedUser.value = null
  }

  async function confirmVerifyCreator(): Promise<void> {
    if (!selectedUser.value || !canSubmitVerifyCreator.value) return

    try {
      await panelStore.verifyCreator(
        selectedUser.value.user_id,
        verifyCreatorForm.value.verified,
        verifyCreatorForm.value.reason
      )
      closeVerifyCreatorModal()
      await loadUsers()
    } catch (err) {
      console.error('Failed to verify creator:', err)
    }
  }

  // ============================================================================
  // Utility
  // ============================================================================

  function getRoleBadgeClass(role: string): string {
    const classes: Record<string, string> = {
      user: 'bg-gray-100 text-gray-800',
      premium: 'bg-yellow-100 text-yellow-800',
      creator: 'bg-blue-100 text-blue-800',
      teacher: 'bg-green-100 text-green-800',
      admin: 'bg-red-100 text-red-800'
    }
    return classes[role] || 'bg-gray-100 text-gray-800'
  }

  return {
    // Search & Filters
    searchQuery,
    roleFilter,
    statusFilter,
    debouncedSearch,
    loadUsers,
    resetFilters,
    changePage,

    // Navigation
    viewUserDetail,

    // Modal State
    showBanModal,
    showUnbanModal,
    showGrantTokensModal,
    showVerifyCreatorModal,
    selectedUser,

    // Form Data
    banForm,
    unbanForm,
    grantTokensForm,
    verifyCreatorForm,

    // Validations
    canSubmitBan,
    canSubmitUnban,
    canSubmitGrantTokens,
    canSubmitVerifyCreator,

    // Actions
    openBanModal,
    closeBanModal,
    confirmBan,
    openUnbanModal,
    closeUnbanModal,
    confirmUnban,
    openGrantTokensModal,
    closeGrantTokensModal,
    confirmGrantTokens,
    openVerifyCreatorModal,
    closeVerifyCreatorModal,
    confirmVerifyCreator,

    // Utility
    getRoleBadgeClass
  }
}
