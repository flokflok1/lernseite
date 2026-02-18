<template>
  <!-- Ban User Modal -->
  <div v-if="showBanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">{{ $t('panel.users.banUser') }}</h3>
        <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
      </div>
      <div class="px-6 py-4">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.banReason') }} *</label>
          <textarea
            :modelValue="banForm.reason"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            :placeholder="$t('panel.users.minChars')"
            @update:modelValue="$emit('update:banForm', { ...banForm, reason: $event })"
            @input="$emit('update:banForm', { ...banForm, reason: ($event.target as HTMLTextAreaElement).value })"
          ></textarea>
        </div>
        <div class="mb-4">
          <label class="flex items-center">
            <input
              :checked="banForm.permanent"
              type="checkbox"
              class="rounded border-gray-300 text-red-600 focus:ring-red-500"
              @change="$emit('update:banForm', { ...banForm, permanent: ($event.target as HTMLInputElement).checked })"
            />
            <span class="ml-2 text-sm text-gray-700">{{ $t('panel.users.permanentBan') }}</span>
          </label>
        </div>
        <div v-if="!banForm.permanent" class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.durationDays') }}</label>
          <input
            :value="banForm.duration_days"
            type="number"
            min="1"
            max="365"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            placeholder="30"
            @input="$emit('update:banForm', { ...banForm, duration_days: Number(($event.target as HTMLInputElement).value) })"
          />
        </div>
        <div class="mb-4">
          <label class="flex items-center">
            <input
              :checked="banForm.notify_user"
              type="checkbox"
              class="rounded border-gray-300 text-red-600 focus:ring-red-500"
              @change="$emit('update:banForm', { ...banForm, notify_user: ($event.target as HTMLInputElement).checked })"
            />
            <span class="ml-2 text-sm text-gray-700">{{ $t('panel.users.notifyByEmail') }}</span>
          </label>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
        <button
          @click="$emit('closeBan')"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          @click="$emit('confirmBan')"
          :disabled="!canSubmitBan"
          class="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ $t('panel.users.banUser') }}
        </button>
      </div>
    </div>
  </div>

  <!-- Unban User Modal -->
  <div v-if="showUnbanModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">{{ $t('panel.users.unbanUser') }}</h3>
        <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
      </div>
      <div class="px-6 py-4">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.unbanReason') }} *</label>
          <textarea
            v-model="internalUnbanReason"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            :placeholder="$t('panel.users.minChars')"
          ></textarea>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
        <button
          @click="$emit('closeUnban')"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          @click="$emit('confirmUnban')"
          :disabled="!canSubmitUnban"
          class="px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ $t('panel.users.unbanUser') }}
        </button>
      </div>
    </div>
  </div>

  <!-- Grant Tokens Modal -->
  <div v-if="showGrantTokensModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">{{ $t('panel.users.grantTokens') }}</h3>
        <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ $t('panel.users.currentBalance') }}: {{ selectedUser?.token_balance || 0 }} Tokens</p>
      </div>
      <div class="px-6 py-4">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.tokenAmount') }} *</label>
          <input
            v-model.number="internalTokenAmount"
            type="number"
            min="1"
            max="1000000"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="5000"
          />
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.reason') }} *</label>
          <textarea
            v-model="internalTokenReason"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            :placeholder="$t('panel.users.minChars')"
          ></textarea>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
        <button
          @click="$emit('closeGrantTokens')"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          @click="$emit('confirmGrantTokens')"
          :disabled="!canSubmitGrantTokens"
          class="px-4 py-2 text-white bg-purple-600 rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ $t('panel.users.grantTokens') }}
        </button>
      </div>
    </div>
  </div>

  <!-- Verify Creator Modal -->
  <div v-if="showVerifyCreatorModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-semibold text-gray-900">{{ $t('panel.users.verifyCreator') }}</h3>
        <p class="text-sm text-gray-600 mt-1">{{ selectedUser?.first_name }} {{ selectedUser?.last_name }}</p>
      </div>
      <div class="px-6 py-4">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.action') }} *</label>
          <select
            v-model="internalVerifyStatus"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
          >
            <option :value="true">{{ $t('panel.users.verify') }}</option>
            <option :value="false">{{ $t('panel.users.revokeVerification') }}</option>
          </select>
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">{{ $t('panel.users.reason') }} *</label>
          <textarea
            v-model="internalVerifyReason"
            rows="3"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
            :placeholder="$t('panel.users.minChars')"
          ></textarea>
        </div>
      </div>
      <div class="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
        <button
          @click="$emit('closeVerifyCreator')"
          class="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
        >
          {{ $t('common.cancel') }}
        </button>
        <button
          @click="$emit('confirmVerifyCreator')"
          :disabled="!canSubmitVerifyCreator"
          class="px-4 py-2 text-white bg-yellow-600 rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ internalVerifyStatus ? $t('panel.users.verify') : $t('panel.users.revoke') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { AdminUser, BanUserRequest } from '@/application/services/api/panel-admin'

interface Props {
  showBanModal: boolean
  showUnbanModal: boolean
  showGrantTokensModal: boolean
  showVerifyCreatorModal: boolean
  selectedUser: AdminUser | null
  banForm: BanUserRequest
  unbanForm: { reason: string }
  grantTokensForm: { amount: number; reason: string }
  verifyCreatorForm: { verified: boolean; reason: string }
  canSubmitBan: boolean
  canSubmitUnban: boolean
  canSubmitGrantTokens: boolean
  canSubmitVerifyCreator: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:banForm': [value: BanUserRequest]
  'update:unbanForm': [value: { reason: string }]
  'update:grantTokensForm': [value: { amount: number; reason: string }]
  'update:verifyCreatorForm': [value: { verified: boolean; reason: string }]
  closeBan: []
  confirmBan: []
  closeUnban: []
  confirmUnban: []
  closeGrantTokens: []
  confirmGrantTokens: []
  closeVerifyCreator: []
  confirmVerifyCreator: []
}>()

const internalUnbanReason = computed({
  get: () => props.unbanForm.reason,
  set: (val: string) => emit('update:unbanForm', { reason: val })
})

const internalTokenAmount = computed({
  get: () => props.grantTokensForm.amount,
  set: (val: number) => emit('update:grantTokensForm', { ...props.grantTokensForm, amount: val })
})

const internalTokenReason = computed({
  get: () => props.grantTokensForm.reason,
  set: (val: string) => emit('update:grantTokensForm', { ...props.grantTokensForm, reason: val })
})

const internalVerifyStatus = computed({
  get: () => props.verifyCreatorForm.verified,
  set: (val: boolean) => emit('update:verifyCreatorForm', { ...props.verifyCreatorForm, verified: val })
})

const internalVerifyReason = computed({
  get: () => props.verifyCreatorForm.reason,
  set: (val: string) => emit('update:verifyCreatorForm', { ...props.verifyCreatorForm, reason: val })
})
</script>
