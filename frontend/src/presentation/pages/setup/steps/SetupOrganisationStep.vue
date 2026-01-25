<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-4">{{ $t('setup.organisation.title') }}</h2>
    <p class="text-gray-600 dark:text-gray-300 mb-6">{{ $t('setup.organisation.description') }}</p>

    <form v-if="!success" @submit.prevent="submit" class="space-y-4 mb-6">
      <Input v-model="form.name" :label="$t('setup.organisation.name')" required :placeholder="$t('setup.organisation.namePlaceholder')" />
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ $t('setup.organisation.type') }}</label>
        <select v-model="form.org_type" class="input-field">
          <option value="academy">{{ $t('setup.organisation.typeAcademy') }}</option>
          <option value="school">{{ $t('setup.organisation.typeSchool') }}</option>
          <option value="company">{{ $t('setup.organisation.typeCompany') }}</option>
          <option value="creator_org">{{ $t('setup.organisation.typeCreator') }}</option>
          <option value="community">{{ $t('setup.organisation.typeCommunity') }}</option>
          <option value="system">{{ $t('setup.organisation.typeSystem') }}</option>
        </select>
      </div>
    </form>

    <div v-else class="mb-6 p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700 rounded-lg">
      <p class="font-medium text-green-900 dark:text-green-100">{{ $t('setup.organisation.success') }}</p>
    </div>

    <div v-if="error" class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-300 px-4 py-3 rounded mb-6">{{ error }}</div>

    <div class="flex justify-between">
      <Button variant="outline" @click="$emit('back')">{{ $t('setup.common.back') }}</Button>
      <Button v-if="!success" variant="primary" :loading="loading" @click="submit">{{ $t('setup.common.create') }}</Button>
      <Button v-else variant="primary" @click="$emit('next')">{{ $t('setup.common.next') }}</Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import * as setupApi from '@/application/services/api/system'
import Input from '@/presentation/components/base/Input.vue'
import Button from '@/presentation/components/base/Button.vue'

const { t } = useI18n()

defineEmits<{ next: []; back: [] }>()

const loading = ref(false)
const success = ref(false)
const error = ref('')

const form = reactive({
  name: '',
  org_type: 'academy' as 'system' | 'school' | 'company' | 'academy' | 'creator_org' | 'community',
})

const submit = async () => {
  loading.value = true
  error.value = ''
  try {
    await setupApi.createOrganisation(form)
    success.value = true
  } catch (err: any) {
    error.value = err.response?.data?.message || t('setup.organisation.createFailed')
  } finally {
    loading.value = false
  }
}
</script>
