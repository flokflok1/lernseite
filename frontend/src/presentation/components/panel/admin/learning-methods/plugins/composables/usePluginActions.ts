/**
 * Composable for LM Plugin action handlers (approve, reject, activate, deactivate)
 *
 * Extracted from LMPluginDetailModal to keep the component under 500 LOC.
 */

import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LMPluginMetadata } from '@/domain/models/learning/plugins.types'

interface PluginActionEmits {
  (event: 'approve', pluginId: string): void
  (event: 'reject', pluginId: string, reason: string): void
  (event: 'activate', pluginId: string): void
  (event: 'deactivate', pluginId: string): void
}

export function usePluginActions(
  plugin: () => LMPluginMetadata,
  emit: PluginActionEmits
) {
  const { t } = useI18n()
  const isProcessing = ref(false)

  async function handleApprove(): Promise<void> {
    if (isProcessing.value) return

    if (!confirm(t('panel.plugins.confirmApprove', { name: plugin().name }))) {
      return
    }

    isProcessing.value = true
    try {
      emit('approve', plugin().plugin_id)
    } finally {
      isProcessing.value = false
    }
  }

  async function handleReject(): Promise<void> {
    if (isProcessing.value) return

    const reason = prompt(t('panel.plugins.rejectReason'))
    if (!reason || reason.trim().length < 10) {
      if (reason !== null) {
        alert(t('panel.plugins.rejectReasonRequired'))
      }
      return
    }

    isProcessing.value = true
    try {
      emit('reject', plugin().plugin_id, reason.trim())
    } finally {
      isProcessing.value = false
    }
  }

  async function handleActivate(): Promise<void> {
    if (isProcessing.value) return

    if (!confirm(t('panel.plugins.confirmActivate', { name: plugin().name }))) {
      return
    }

    isProcessing.value = true
    try {
      emit('activate', plugin().plugin_id)
    } finally {
      isProcessing.value = false
    }
  }

  async function handleDeactivate(): Promise<void> {
    if (isProcessing.value) return

    if (!confirm(t('panel.plugins.confirmDeactivate', { name: plugin().name }))) {
      return
    }

    isProcessing.value = true
    try {
      emit('deactivate', plugin().plugin_id)
    } finally {
      isProcessing.value = false
    }
  }

  function formatDate(dateString: string): string {
    try {
      const date = new Date(dateString)
      return date.toLocaleString('de-DE', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return dateString
    }
  }

  return {
    isProcessing,
    handleApprove,
    handleReject,
    handleActivate,
    handleDeactivate,
    formatDate,
  }
}
