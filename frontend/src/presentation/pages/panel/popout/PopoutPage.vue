<!--
  LSX Pop-out Page

  Route handler for /panel/popout/:windowType
  Decodes payload from URL, resolves window component, renders full-screen.
  Communicates with main window via SharedWorker for pop-in.
-->

<template>
  <div class="popout-page h-screen flex flex-col overflow-hidden">
    <!-- Pop-out Header (minimal: title + pop-in button) -->
    <header
      class="flex-shrink-0 flex items-center justify-between px-4 py-2 bg-[var(--color-surface)] border-b border-[var(--color-border)]"
    >
      <span class="text-sm font-medium text-[var(--color-text-primary)]">
        {{ virtualWindow.title || windowType }}
      </span>
      <button
        @click="handlePopIn"
        class="px-3 py-1.5 text-xs font-medium rounded-md bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
        :title="$t('common.pop_in')"
      >
        ← {{ $t('common.pop_in') }}
      </button>
    </header>

    <!-- Window Content -->
    <div class="flex-1 overflow-auto">
      <component
        v-if="windowComponent"
        :is="windowComponent"
        :window="virtualWindow"
      />
      <div v-else class="flex items-center justify-center h-full text-[var(--color-text-secondary)]">
        {{ $t('common.unknown_window_type') }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import type { LsxPanel } from '@/application/stores/modules/workspace/panel.types'
import { resolveWindowComponent } from '@/presentation/components/shared/layout/window-manager/windowResolver'
import { sendSync, useWindowSync } from '@/application/composables/useWindowSync'

const route = useRoute()
useWindowSync()

const windowType = computed(() => route.params.windowType as string)

const decodedPayload = computed<Record<string, unknown>>(() => {
  const encoded = route.query.p as string
  if (!encoded) return {}
  try {
    return JSON.parse(atob(encoded))
  } catch {
    console.error('[PopoutPage] Failed to decode payload')
    return {}
  }
})

const virtualWindow = computed<LsxPanel>(() => ({
  id: `popout-${windowType.value}-${Date.now()}`,
  type: windowType.value as LsxPanel['type'],
  title: (decodedPayload.value.title as string) || '',
  minimized: false,
  maximized: false,
  position: { x: 0, y: 0 },
  zIndex: 1,
  payload: decodedPayload.value,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
}))

const windowComponent = computed(() => resolveWindowComponent(windowType.value))

function handlePopIn() {
  sendSync('action:popin', {
    windowType: windowType.value,
    payload: decodedPayload.value,
  })
  window.close()
}

onMounted(() => {
  sendSync('window:register', { windowType: windowType.value })
  document.title = `LSX — ${virtualWindow.value.title || windowType.value}`
})

onBeforeUnmount(() => {
  sendSync('window:unregister', { windowType: windowType.value })
})
</script>
