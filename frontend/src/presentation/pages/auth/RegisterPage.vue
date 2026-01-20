<template>
  <div>
    <h2 class="text-2xl font-bold text-[var(--color-text-primary)] mb-6">{{ t('auth.register') }}</h2>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <Input
          id="first_name"
          v-model="form.first_name"
          type="text"
          :label="t('auth.first_name')"
          placeholder="Max"
          :required="true"
          :error="errors.first_name"
        />

        <Input
          id="last_name"
          v-model="form.last_name"
          type="text"
          :label="t('auth.last_name')"
          placeholder="Mustermann"
          :required="true"
          :error="errors.last_name"
        />
      </div>

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
        :hint="t('auth.password_hint')"
      />

      <Input
        id="confirm_password"
        v-model="form.confirm_password"
        type="password"
        :label="t('auth.confirm_password')"
        placeholder="••••••••"
        :required="true"
        :error="errors.confirm_password"
      />

      <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {{ errorMessage }}
      </div>

      <div v-if="successMessage" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
        {{ successMessage }}
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        class="w-full"
        :loading="isLoading"
        :disabled="isLoading"
      >
        {{ t('auth.register') }}
      </Button>
    </form>

    <div class="mt-6 text-center">
      <p class="text-sm text-[var(--color-text-secondary)]">
        {{ t('auth.have_account') }}
        <router-link to="/login" class="text-primary-600 hover:text-primary-700 font-medium">
          {{ t('auth.login_now') }}
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/application/stores/auth.store'
import Input from '@/presentation/components/base/Input.vue'
import Button from '@/presentation/components/base/Button.vue'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const form = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirm_password: '',
})

const errors = reactive({
  first_name: '',
  last_name: '',
  email: '',
  password: '',
  confirm_password: '',
})

const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)

const validateForm = (): boolean => {
  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })
  errorMessage.value = ''

  // Validate first name
  if (!form.first_name) {
    errors.first_name = t('errors.required')
    return false
  }

  // Validate last name
  if (!form.last_name) {
    errors.last_name = t('errors.required')
    return false
  }

  // Validate email
  if (!form.email) {
    errors.email = t('errors.required')
    return false
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    errors.email = t('errors.invalid_email')
    return false
  }

  // Validate password
  if (!form.password) {
    errors.password = t('errors.required')
    return false
  }

  if (form.password.length < 8) {
    errors.password = t('errors.password_min_length')
    return false
  }

  if (!/[A-Z]/.test(form.password)) {
    errors.password = t('errors.password_uppercase')
    return false
  }

  if (!/[0-9]/.test(form.password)) {
    errors.password = t('errors.password_number')
    return false
  }

  // Validate password confirmation
  if (form.password !== form.confirm_password) {
    errors.confirm_password = t('errors.password_mismatch')
    return false
  }

  return true
}

const handleRegister = async () => {
  // Validate form
  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    await authStore.register({
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      password: form.password,
    })

    successMessage.value = t('auth.register_success')

    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push('/login')
    }, 2000)

  } catch (error: any) {
    errorMessage.value = error.response?.data?.message || error.message || t('auth.register_failed')

  } finally {
    isLoading.value = false
  }
}
</script>
