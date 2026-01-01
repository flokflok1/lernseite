<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-4">Installation abschließen</h2>
    <p class="text-gray-600 mb-6">Überprüfe die Installation und schließe den Setup-Prozess ab.</p>

    <div v-if="verifyResult" class="mb-6 space-y-3">
      <div class="p-4 rounded-lg border" :class="verifyResult.success ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'">
        <p class="font-medium mb-3">{{ verifyResult.success ? 'Alle Checks erfolgreich!' : 'Verifizierung läuft...' }}</p>

        <div class="space-y-2">
          <div v-for="(check, index) in verifyResult.checks" :key="index" class="flex items-center text-sm">
            <span v-if="check.status === 'passed'" class="text-green-600 mr-2">✓</span>
            <span v-else class="text-red-600 mr-2">✗</span>
            <span>{{ check.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="completed" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
      <p class="font-medium text-green-900 mb-2">Installation erfolgreich abgeschlossen!</p>
      <p class="text-sm text-green-700">Das System ist jetzt einsatzbereit.</p>
    </div>

    <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button v-if="!completed" variant="outline" @click="$emit('back')">Zurück</Button>
      <div v-else></div>
      <div class="flex gap-3">
        <Button v-if="!verifyResult" variant="outline" :loading="verifying" @click="verify">Verifizieren</Button>
        <Button v-if="verifyResult && !completed" variant="primary" :loading="loading" @click="complete">
          Installation abschließen
        </Button>
        <Button v-if="completed" variant="primary" @click="goToLogin">Zum Login</Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as setupApi from '@/api/setup.api'
import Button from '@/components/ui/Button.vue'
import { useAppStore } from '@/store/app.store'
import http from '@/api/http'

// Import locale files for auto-sync
import deMessages from '@/locales/de.json'
import enMessages from '@/locales/en.json'
import plMessages from '@/locales/pl.json'

defineEmits<{ back: [] }>();

interface VerifyCheck {
  name: string
  status: 'passed' | 'failed' | 'error'
  message: string
  details?: any
}

interface VerifyResponse {
  success: boolean
  checks: VerifyCheck[]
  errors?: string[]
  warnings?: string[]
  timestamp?: string
}

// Flatten nested object to dot-notation keys
function flattenMessages(obj: Record<string, any>, prefix = ''): Record<string, string> {
  const result: Record<string, string> = {}
  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      Object.assign(result, flattenMessages(value, fullKey))
    } else if (typeof value === 'string') {
      result[fullKey] = value
    }
  }
  return result
}

const router = useRouter()
const appStore = useAppStore()

const verifying = ref(false)
const loading = ref(false)
const completed = ref(false)
const error = ref('')
const verifyResult = ref<VerifyResponse | null>(null)
const syncingLocales = ref(false)
const localesSynced = ref(false)

// Auto-run verification on mount
onMounted(() => {
  verify()
})

const formatCheckName = (name: string): string => {
  // Use the name from backend as-is
  return name
}

const verify = async () => {
  verifying.value = true
  error.value = ''
  try {
    const response = await setupApi.verifyInstallation()
    verifyResult.value = response as VerifyResponse
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Verifizierung fehlgeschlagen'
  } finally {
    verifying.value = false
  }
}

const complete = async () => {
  loading.value = true
  error.value = ''
  try {
    await setupApi.completeInstallation()
    completed.value = true
    // Update app store to reflect installation complete
    await appStore.checkInstallationStatus()

    // Auto-sync locale files to database
    await syncLocales()
  } catch (err: any) {
    error.value = err.response?.data?.message || 'Installation-Abschluss fehlgeschlagen'
  } finally {
    loading.value = false
  }
}

const syncLocales = async () => {
  syncingLocales.value = true
  try {
    const allLocaleMessages = {
      de: flattenMessages(deMessages),
      en: flattenMessages(enMessages),
      pl: flattenMessages(plMessages)
    }

    await http.post('/i18n/admin/seed-all-locales', {
      locales: allLocaleMessages,
      primary_language: 'de'
    })

    localesSynced.value = true
    console.log('[Setup] Locale files synced to database')
  } catch (err) {
    // Non-critical error, don't block completion
    console.warn('[Setup] Failed to sync locales:', err)
  } finally {
    syncingLocales.value = false
  }
}

const goToLogin = () => {
  router.push({ name: 'Login' })
}
</script>
