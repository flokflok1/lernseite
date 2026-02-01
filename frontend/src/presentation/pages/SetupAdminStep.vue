<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">{{ $t('setup.admin.title') }}</h2>
    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ $t('setup.admin.description') }}</p>

    <form v-if="!success" @submit.prevent="submit" class="space-y-4 mb-6">
      <div class="grid grid-cols-2 gap-4">
        <Input v-model="form.first_name" :label="$t('setup.admin.firstName')" required />
        <Input v-model="form.last_name" :label="$t('setup.admin.lastName')" required />
      </div>
      <Input v-model="form.email" type="email" :label="$t('setup.admin.email')" required />
      <Input v-model="form.password" type="password" :label="$t('setup.admin.password')" required :hint="$t('setup.admin.passwordHint')" />
      <Input v-model="confirmPassword" type="password" :label="$t('setup.admin.confirmPassword')" required />
    </form>

    <div v-else class="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 rounded-lg">
      <p class="font-medium text-green-900 dark:text-green-100">{{ $t('setup.admin.success') }}</p>
      <p class="text-sm text-green-700 dark:text-green-300 mt-2">{{ $t('setup.admin.email') }}: {{ form.email }}</p>
    </div>

    <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-300 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button variant="outline" @click="$emit('back')">{{ $t('setup.common.back') }}</Button>
      <Button v-if="!success" type="submit" variant="primary" :loading="loading" @click="submit">{{ $t('setup.common.create') }}</Button>
      <Button v-else variant="primary" @click="$emit('next')">{{ $t('setup.common.next') }}</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import * as setupApi from '@/application/services/api/system'
import Input from '@/presentation/components/shared/ui/Input.vue'
import Button from '@/presentation/components/shared/ui/Button.vue'

const { t } = useI18n()

defineEmits<{ next: []; back: [] }>()

const loading = ref(false)
const success = ref(false)
const error = ref('')
const confirmPassword = ref('')

const form = reactive({
  email: '',
  password: '',
  first_name: '',
  last_name: '',
})

const submit = async () => {
  if (form.password !== confirmPassword.value) {
    error.value = t('setup.admin.passwordMismatch')
    return
  }
  loading.value = true
  error.value = ''
  try {
    await setupApi.createAdmin(form)
    success.value = true
  } catch (err: any) {
    error.value = err.response?.data?.message || t('setup.admin.createFailed')
  } finally {
    loading.value = false
  }
}
</script>
