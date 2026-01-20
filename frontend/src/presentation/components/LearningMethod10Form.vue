<template>
  <BaseLearningMethodForm
    :window="window"
    :method-code="METHOD_CODE"
    :additional-data="methodData"
  >
    <template #method-fields="{ form }">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.lm10.title') }}
          </label>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {{ $t('windows.lm10.description') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.lm10.instructionLabel') }}
          </label>
          <textarea
            v-model="methodData.instruction"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            :placeholder="$t('windows.lm10.instructionPlaceholder')"
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.lm10.networkTypeLabel') }}
          </label>
          <select
            v-model="methodData.network_type"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            required
          >
            <option value="">{{ $t('windows.lm10.networkTypeDefault') }}</option>
            <option value="lan">{{ $t('windows.lm10.networkTypeLan') }}</option>
            <option value="wan">{{ $t('windows.lm10.networkTypeWan') }}</option>
            <option value="vlan">{{ $t('windows.lm10.networkTypeVlan') }}</option>
            <option value="routing">{{ $t('windows.lm10.networkTypeRouting') }}</option>
            <option value="firewall">{{ $t('windows.lm10.networkTypeFirewall') }}</option>
            <option value="vpn">{{ $t('windows.lm10.networkTypeVpn') }}</option>
            <option value="wifi">{{ $t('windows.lm10.networkTypeWifi') }}</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.lm10.componentsLabel') }}
          </label>
          <div class="grid grid-cols-2 gap-2">
            <label v-for="comp in availableComponents" :key="comp.id" class="flex items-center space-x-2">
              <input
                v-model="methodData.components"
                :value="comp.id"
                type="checkbox"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ $t(`windows.lm10.component_${comp.id}`) }}</span>
            </label>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.lm10.topologyLabel') }}
          </label>
          <textarea
            v-model="methodData.expected_topology"
            rows="4"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            :placeholder="$t('windows.lm10.topologyPlaceholder')"
            required
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('windows.lm10.ipRangeLabel') }}
          </label>
          <input
            v-model="methodData.ip_range"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            :placeholder="$t('windows.lm10.ipRangePlaceholder')"
          />
        </div>

        <div>
          <label class="flex items-center space-x-2">
            <input
              v-model="methodData.check_connectivity"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              {{ $t('windows.lm10.connectivityLabel') }}
            </span>
          </label>
        </div>
      </div>
    </template>
  </BaseLearningMethodForm>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LsxWindow } from '@/application/stores/modules/desktop'
import BaseLearningMethodForm from './BaseLearningMethodForm.vue'

const METHOD_CODE = 10

interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

const availableComponents = [
  { id: 'router', name: 'Router' },
  { id: 'switch', name: 'Switch' },
  { id: 'firewall', name: 'Firewall' },
  { id: 'server', name: 'Server' },
  { id: 'pc', name: 'PC/Client' },
  { id: 'access_point', name: 'Access Point' }
]

const methodData = ref<{
  instruction: string
  network_type: string
  components: string[]
  expected_topology: string
  ip_range: string
  check_connectivity: boolean
}>({
  instruction: '',
  network_type: '',
  components: [],
  expected_topology: '',
  ip_range: '',
  check_connectivity: true
})

onMounted(() => {
  const existingData = props.window.payload?.instanceData?.data
  if (existingData) {
    methodData.value = {
      instruction: existingData.instruction || '',
      network_type: existingData.network_type || '',
      components: existingData.components || [],
      expected_topology: existingData.expected_topology || '',
      ip_range: existingData.ip_range || '',
      check_connectivity: existingData.check_connectivity !== undefined ? existingData.check_connectivity : true
    }
  }
})
</script>
