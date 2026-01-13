<template>
  <Card title="Widgets anpassen" class="bg-primary-50 border-primary-200">
    <div class="space-y-4">
      <!-- Info Notice -->
      <div class="bg-blue-50 border border-blue-200 p-3 rounded">
        <p class="text-sm text-blue-800">
          💎 Als Premium-Nutzer kannst du dein Dashboard personalisieren. Wähle aus, welche Widgets angezeigt werden sollen.
        </p>
      </div>

      <!-- Widget Toggles -->
      <div class="space-y-2">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">Verfügbare Widgets</h3>

        <div
          v-for="widget in availableWidgets"
          :key="widget.id"
          class="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:border-primary-300 transition-colors"
        >
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <span class="text-xl">{{ widget.icon || '📊' }}</span>
              <div>
                <p class="font-medium text-gray-900">{{ widget.title }}</p>
                <p v-if="widget.description" class="text-xs text-gray-500">{{ widget.description }}</p>
              </div>
            </div>
          </div>

          <div class="ml-4">
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                :checked="isWidgetVisible(widget.id)"
                @change="toggleWidget(widget.id)"
                class="sr-only peer"
              >
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between pt-4 border-t border-gray-300">
        <Button
          variant="outline"
          size="sm"
          @click="resetToDefault"
        >
          Auf Standard zurücksetzen
        </Button>

        <Button
          variant="primary"
          size="sm"
          @click="closePanel"
        >
          Fertig
        </Button>
      </div>

      <!-- Success Message -->
      <div v-if="showSuccessMessage" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
        ✓ Einstellungen gespeichert!
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDashboardStore } from '@/store/modules/learning'
import Card from '@/components/base/Card.vue'
import Button from '@/components/base/Button.vue'

// ============================================================================
// Emits
// ============================================================================

const emit = defineEmits<{
  close: []
}>()

// ============================================================================
// Store
// ============================================================================

const dashboardStore = useDashboardStore()

// ============================================================================
// State
// ============================================================================

const showSuccessMessage = ref(false)

// ============================================================================
// Computed
// ============================================================================

const availableWidgets = computed(() => dashboardStore.availableWidgets)

// ============================================================================
// Methods
// ============================================================================

const isWidgetVisible = (widgetId: string): boolean => {
  if (!dashboardStore.layout) return false

  const widget = dashboardStore.layout.widgets.find(w => w.widgetId === widgetId)
  return widget?.visible || false
}

const toggleWidget = async (widgetId: string) => {
  if (!dashboardStore.layout) return

  const widget = dashboardStore.layout.widgets.find(w => w.widgetId === widgetId)
  if (widget) {
    await dashboardStore.toggleWidgetVisibility(widget.instanceId)
    flashSuccessMessage()
  }
}

const resetToDefault = async () => {
  if (confirm('Möchtest du deine Widget-Einstellungen wirklich auf die Standardwerte zurücksetzen?')) {
    await dashboardStore.resetToDefault()
    flashSuccessMessage()
  }
}

const closePanel = () => {
  emit('close')
}

const flashSuccessMessage = () => {
  showSuccessMessage.value = true
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 2000)
}
</script>

<style scoped>
/* Toggle switch styling is handled by Tailwind classes */
</style>
