<template>
  <div>
    <h2 class="text-xl font-bold text-white mb-3">
      {{ $t('setup.systemCheck.title') }}
    </h2>
    <p class="text-sm text-gray-400 mb-5">
      {{ $t('setup.systemCheck.description') }}
    </p>

    <!-- Database Configuration -->
    <div class="mb-6 p-5 bg-[#0f1419] border border-[#2a3350] rounded-lg">
      <h3 class="text-base font-semibold text-white mb-3">
        {{ $t('setup.systemCheck.database') }}
      </h3>
      <form @submit.prevent="testDatabase" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <Input
            v-model="dbConfig.host"
            :label="$t('setup.systemCheck.host')"
            placeholder="10.0.10.10"
            required
          />
          <Input
            v-model="dbConfig.port"
            :label="$t('setup.systemCheck.port')"
            placeholder="5432"
            required
          />
        </div>
        <Input
          v-model="dbConfig.dbname"
          :label="$t('setup.systemCheck.dbName')"
          placeholder="lernsystemx_dev"
          required
        />
        <div class="grid grid-cols-2 gap-4">
          <Input
            v-model="dbConfig.user"
            :label="$t('setup.systemCheck.user')"
            placeholder="lernsystem"
            required
          />
          <Input
            v-model="dbConfig.password"
            type="password"
            :label="$t('setup.systemCheck.password')"
            placeholder="********"
            required
          />
        </div>

        <div v-if="dbStatus.message"
          class="p-3 rounded-lg text-sm"
          :class="dbStatus.success ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'"
        >
          {{ dbStatus.message }}
        </div>

        <Button
          type="submit"
          :variant="dbConfigured ? 'outline' : 'primary'"
          :loading="testingDb"
          class="w-full"
        >
          {{ dbConfigured ? '✓ ' + $t('setup.systemCheck.connectionTested') : $t('setup.systemCheck.testConnection') }}
        </Button>
      </form>
    </div>

    <!-- Redis Configuration -->
    <div class="mb-6 p-5 bg-[#0f1419] border border-[#2a3350] rounded-lg">
      <h3 class="text-base font-semibold text-white mb-3">
        {{ $t('setup.systemCheck.redis') }}
      </h3>
      <form @submit.prevent="testRedis" class="space-y-4">
        <div class="grid grid-cols-3 gap-4">
          <Input
            v-model="redisConfig.host"
            :label="$t('setup.systemCheck.host')"
            placeholder="10.0.10.10"
            required
          />
          <Input
            v-model="redisConfig.port"
            :label="$t('setup.systemCheck.port')"
            placeholder="6379"
            required
          />
          <Input
            v-model="redisConfig.db"
            :label="$t('setup.systemCheck.db')"
            placeholder="0"
            required
          />
        </div>

        <div v-if="redisStatus.message"
          class="p-3 rounded-lg text-sm"
          :class="redisStatus.success ? 'bg-green-900/30 text-green-300' : 'bg-red-900/30 text-red-300'"
        >
          {{ redisStatus.message }}
        </div>

        <Button
          type="submit"
          :variant="redisConfigured ? 'outline' : 'primary'"
          :loading="testingRedis"
          class="w-full"
        >
          {{ redisConfigured ? '✓ ' + $t('setup.systemCheck.connectionTested') : $t('setup.systemCheck.testConnection') }}
        </Button>
      </form>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-900/20 border border-red-800 text-red-300 px-4 py-3 rounded mb-6">
      {{ error }}
    </div>

    <!-- Navigation -->
    <div class="flex justify-between">
      <Button variant="outline" disabled>{{ $t('setup.common.back') }}</Button>
      <Button
        variant="primary"
        :disabled="!canProceed"
        @click="$emit('next')"
      >
        {{ $t('setup.common.next') }}
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import Input from '@/components/shared/ui/Input.vue'
import Button from '@/components/shared/ui/Button.vue'

const { t } = useI18n()

defineEmits<{
  next: []
  back: []
}>()

// Use environment variable for setup URL, fallback to window.location.origin
const SETUP_URL = import.meta.env.VITE_SETUP_URL || window.location.origin.replace(':5173', ':5000')

// Database configuration
const dbConfig = reactive({
  host: 'localhost',
  port: '5432',
  dbname: 'lernsystemx_dev',
  user: 'postgres',
  password: ''
})

const dbStatus = reactive({
  success: false,
  message: ''
})

const testingDb = ref(false)
const dbConfigured = ref(false)

// Redis configuration
const redisConfig = reactive({
  host: 'localhost',
  port: '6379',
  db: '0'
})

const redisStatus = reactive({
  success: false,
  message: ''
})

const testingRedis = ref(false)
const redisConfigured = ref(false)

const error = ref('')

const canProceed = computed(() => dbConfigured.value && redisConfigured.value)

const testDatabase = async () => {
  testingDb.value = true
  dbStatus.message = ''
  error.value = ''

  try {
    const response = await axios.post(`${SETUP_URL}/setup/config/database`, dbConfig)
    dbStatus.success = true
    dbStatus.message = response.data.message
    dbConfigured.value = true
  } catch (err: any) {
    dbStatus.success = false
    dbStatus.message = err.response?.data?.message || err.response?.data?.error || t('setup.systemCheck.connectionFailed')
    dbConfigured.value = false
  } finally {
    testingDb.value = false
  }
}

const testRedis = async () => {
  testingRedis.value = true
  redisStatus.message = ''
  error.value = ''

  try {
    const response = await axios.post(`${SETUP_URL}/setup/config/redis`, redisConfig)
    redisStatus.success = true
    redisStatus.message = response.data.message
    redisConfigured.value = true
  } catch (err: any) {
    redisStatus.success = false
    redisStatus.message = err.response?.data?.message || err.response?.data?.error || t('setup.systemCheck.connectionFailed')
    redisConfigured.value = false
  } finally {
    testingRedis.value = false
  }
}
</script>
