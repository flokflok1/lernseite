<template>
  <div>
    <h2 class="text-2xl font-bold text-[var(--color-text-primary)] mb-6">Login</h2>

    <form @submit.prevent="handleLogin" class="space-y-4">
      <Input
        id="email"
        v-model="form.email"
        type="email"
        label="E-Mail"
        placeholder="user@example.com"
        :required="true"
        :error="errors.email"
      />

      <Input
        id="password"
        v-model="form.password"
        type="password"
        label="Passwort"
        placeholder="••••••••"
        :required="true"
        :error="errors.password"
      />

      <Input
        v-if="show2FA"
        id="totp"
        v-model="form.totp_code"
        type="text"
        label="2FA Code"
        placeholder="123456"
        :required="show2FA"
        hint="Geben Sie Ihren 6-stelligen 2FA-Code ein"
      />

      <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {{ errorMessage }}
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        class="w-full"
        :loading="isLoading"
        :disabled="isLoading"
      >
        Anmelden
      </Button>
    </form>

    <div class="mt-6 text-center">
      <p class="text-sm text-[var(--color-text-secondary)]">
        Noch kein Account?
        <router-link to="/register" class="text-primary-600 hover:text-primary-700 font-medium">
          Jetzt registrieren
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth.store'
import Input from '@/components/ui/Input.vue'
import Button from '@/components/ui/Button.vue'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: '',
  totp_code: '',
})

const errors = reactive({
  email: '',
  password: '',
})

const errorMessage = ref('')
const isLoading = ref(false)
const show2FA = ref(false)

const handleLogin = async () => {
  // Reset errors
  errors.email = ''
  errors.password = ''
  errorMessage.value = ''

  // Basic validation
  if (!form.email) {
    errors.email = 'E-Mail ist erforderlich'
    return
  }

  if (!form.password) {
    errors.password = 'Passwort ist erforderlich'
    return
  }

  isLoading.value = true

  try {
    await authStore.login({
      email: form.email,
      password: form.password,
      totp_code: form.totp_code || undefined,
    })

    // Redirect to dashboard on success
    router.push('/dashboard')

  } catch (error: any) {
    // Check if 2FA is required
    if (error.response?.data?.two_factor_required) {
      show2FA.value = true
      errorMessage.value = 'Bitte geben Sie Ihren 2FA-Code ein'
      return
    }

    // Show error message
    errorMessage.value = error.response?.data?.message || error.message || 'Login fehlgeschlagen'

  } finally {
    isLoading.value = false
  }
}
</script>
