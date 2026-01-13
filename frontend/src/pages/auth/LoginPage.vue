<template>
  <div>
    <h2 class="text-2xl font-bold text-[var(--color-text-primary)] mb-6">{{ t('auth.login') }}</h2>

    <form @submit.prevent="handleLogin" class="space-y-4">
      <Input
        id="email"
        v-model="form.email"
        type="email"
        :label="t('auth.email')"
        placeholder="user@example.com"
        :required="true"
        :error="errors.email"
      />

      <Input
        id="password"
        v-model="form.password"
        type="password"
        :label="t('auth.password')"
        placeholder="••••••••"
        :required="true"
        :error="errors.password"
      />

      <Input
        v-if="show2FA"
        id="totp"
        v-model="form.totp_code"
        type="text"
        :label="t('auth.2fa_code')"
        placeholder="123456"
        :required="show2FA"
        :hint="t('auth.2fa_hint')"
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
        {{ t('auth.login') }}
      </Button>
    </form>

    <div class="mt-6 text-center">
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ t('auth.no_account') }}
        <router-link to="/register" class="text-primary-600 hover:text-primary-700 font-medium">
          {{ t('auth.register') }}
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/store/modules/core'
import Input from '@/components/base/Input.vue'
import Button from '@/components/base/Button.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

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
    errors.email = t('errors.required')
    return
  }

  if (!form.password) {
    errors.password = t('errors.required')
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
      errorMessage.value = t('auth.2fa_required')
      return
    }

    // Show error message
    errorMessage.value = error.response?.data?.message || error.message || t('auth.login_failed')

  } finally {
    isLoading.value = false
  }
}
</script>
