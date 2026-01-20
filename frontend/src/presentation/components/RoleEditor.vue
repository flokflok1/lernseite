<template>
  <div class="role-editor">
    <!-- Header -->
    <div class="editor-header">
      <h2>{{ isNew ? $t('admin.roleStudio.createRole') : $t('admin.roleStudio.editRole') }}</h2>
      <button class="btn-close" @click="$emit('cancel')" :title="$t('common.close')">×</button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner"></div>
      <p>{{ $t('common.saving') }}</p>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleSubmit" class="editor-form">
      <!-- Error Display -->
      <div v-if="formError" class="error-alert">
        <p>{{ formError }}</p>
      </div>

      <!-- Role Code Field -->
      <div class="form-group">
        <label for="role-code">{{ $t('admin.roleStudio.roleCode') }}</label>
        <input
          id="role-code"
          v-model="formData.role_code"
          type="text"
          :disabled="!isNew"
          :placeholder="$t('admin.roleStudio.roleCodePlaceholder')"
          class="form-control"
          @blur="validateRoleCode"
        />
        <span v-if="fieldErrors.role_code" class="field-error">
          {{ fieldErrors.role_code }}
        </span>
      </div>

      <!-- Display Name Field -->
      <div class="form-group">
        <label for="display-name">{{ $t('admin.roleStudio.displayName') }}</label>
        <input
          id="display-name"
          v-model="formData.display_name"
          type="text"
          :placeholder="$t('admin.roleStudio.displayNamePlaceholder')"
          class="form-control"
          @blur="validateDisplayName"
        />
        <span v-if="fieldErrors.display_name" class="field-error">
          {{ fieldErrors.display_name }}
        </span>
      </div>

      <!-- Studio Mode Field -->
      <div class="form-group">
        <label for="studio-mode">{{ $t('admin.roleStudio.studioMode') }}</label>
        <select
          id="studio-mode"
          v-model="formData.studio_mode"
          class="form-control"
          @blur="validateStudioMode"
        >
          <option value="">{{ $t('common.select') }}</option>
          <option v-for="mode in studioModes" :key="mode" :value="mode">
            {{ mode }}
          </option>
        </select>
        <span v-if="fieldErrors.studio_mode" class="field-error">
          {{ fieldErrors.studio_mode }}
        </span>
      </div>

      <!-- Description Field -->
      <div class="form-group">
        <label for="description">{{ $t('admin.roleStudio.description') }}</label>
        <textarea
          id="description"
          v-model="formData.description"
          :placeholder="$t('admin.roleStudio.descriptionPlaceholder')"
          class="form-control"
          rows="3"
        ></textarea>
      </div>

      <!-- Requires Organization Checkbox -->
      <div class="form-group checkbox-group">
        <input
          id="requires-organization"
          v-model="formData.requires_organization"
          type="checkbox"
          class="checkbox-control"
        />
        <label for="requires-organization" class="checkbox-label">
          {{ $t('admin.roleStudio.requiresOrganization') }}
        </label>
      </div>

      <!-- Permissions Section -->
      <div class="permissions-section">
        <h3>{{ $t('admin.roleStudio.permissions') }}</h3>
        <div class="permissions-grid">
          <div
            v-for="permission in availablePermissions"
            :key="permission"
            class="permission-item"
          >
            <input
              :id="`permission-${permission}`"
              v-model="formData.permissions[permission]"
              type="checkbox"
              class="checkbox-control"
            />
            <label :for="`permission-${permission}`" class="permission-label">
              {{ permission }}
            </label>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button type="submit" class="btn-primary" :disabled="isLoading">
          {{ isNew ? $t('common.create') : $t('common.save') }}
        </button>
        <button type="button" class="btn-secondary" @click="$emit('cancel')" :disabled="isLoading">
          {{ $t('common.cancel') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { RoleStudioMode, CreateRoleStudioRequest } from './types'

interface Props {
  role: RoleStudioMode | null
  isNew: boolean
}

interface Emits {
  (e: 'save', data: CreateRoleStudioRequest | Partial<RoleStudioMode>): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { t } = useI18n()

// Form state
const formData = ref({
  role_code: '',
  display_name: '',
  studio_mode: '' as any,
  description: '',
  requires_organization: false,
  permissions: {} as Record<string, boolean>
})

const isLoading = ref(false)
const formError = ref('')
const fieldErrors = ref<Record<string, string>>({})

// Constants
const studioModes = ['admin', 'moderator', 'org_admin', 'org_member', 'teacher', 'user', 'guest']
const availablePermissions = [
  'can_view_content',
  'can_edit_content',
  'can_delete_content',
  'can_manage_users',
  'can_manage_roles',
  'can_view_analytics',
  'can_export_data',
  'can_manage_permissions'
]

// Initialize form with role data
watch(
  () => props.role,
  (newRole) => {
    if (newRole) {
      formData.value = {
        role_code: newRole.role_code,
        display_name: newRole.display_name,
        studio_mode: newRole.studio_mode,
        description: newRole.description || '',
        requires_organization: newRole.requires_organization,
        permissions: { ...newRole.permissions }
      }
    } else {
      // Reset form for new role
      formData.value = {
        role_code: '',
        display_name: '',
        studio_mode: '',
        description: '',
        requires_organization: false,
        permissions: {}
      }
    }
    fieldErrors.value = {}
    formError.value = ''
  },
  { immediate: true }
)

// Validation functions
const validateRoleCode = () => {
  delete fieldErrors.value.role_code

  if (!formData.value.role_code.trim()) {
    fieldErrors.value.role_code = t('admin.roleStudio.roleCodeRequired')
    return false
  }

  if (formData.value.role_code.length < 1 || formData.value.role_code.length > 50) {
    fieldErrors.value.role_code = t('admin.roleStudio.roleCodeLength')
    return false
  }

  if (!/^[a-zA-Z0-9_]+$/.test(formData.value.role_code)) {
    fieldErrors.value.role_code = t('admin.roleStudio.roleCodeFormat')
    return false
  }

  return true
}

const validateDisplayName = () => {
  delete fieldErrors.value.display_name

  if (!formData.value.display_name.trim()) {
    fieldErrors.value.display_name = t('admin.roleStudio.displayNameRequired')
    return false
  }

  if (formData.value.display_name.length > 100) {
    fieldErrors.value.display_name = t('admin.roleStudio.displayNameLength')
    return false
  }

  return true
}

const validateStudioMode = () => {
  delete fieldErrors.value.studio_mode

  if (!formData.value.studio_mode) {
    fieldErrors.value.studio_mode = t('admin.roleStudio.studioModeRequired')
    return false
  }

  if (!studioModes.includes(formData.value.studio_mode)) {
    fieldErrors.value.studio_mode = t('admin.roleStudio.studioModeInvalid')
    return false
  }

  return true
}

const validateForm = () => {
  const isRoleCodeValid = validateRoleCode()
  const isDisplayNameValid = validateDisplayName()
  const isStudioModeValid = validateStudioMode()

  return isRoleCodeValid && isDisplayNameValid && isStudioModeValid
}

const handleSubmit = async () => {
  formError.value = ''

  if (!validateForm()) {
    formError.value = t('admin.roleStudio.formInvalid')
    return
  }

  isLoading.value = true

  try {
    // Prepare data
    const submitData = {
      role_code: formData.value.role_code.toLowerCase(),
      display_name: formData.value.display_name.trim(),
      studio_mode: formData.value.studio_mode,
      description: formData.value.description.trim() || null,
      requires_organization: formData.value.requires_organization,
      permissions: formData.value.permissions
    }

    emit('save', submitData)
  } catch (error) {
    formError.value = error instanceof Error ? error.message : t('common.unknownError')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.role-editor {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 1rem;
}

.editor-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #111827;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  border-radius: 0.75rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: relative;
}

.error-alert {
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  padding: 1rem;
  color: #991b1b;
}

.error-alert p {
  margin: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-control {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-family: inherit;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control:disabled {
  background-color: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.field-error {
  color: #dc2626;
  font-size: 0.875rem;
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-control {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-label {
  margin: 0;
  cursor: pointer;
  font-weight: normal;
}

.permissions-section {
  border-top: 1px solid #e5e7eb;
  padding-top: 1.5rem;
}

.permissions-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.permission-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.permission-label {
  margin: 0;
  cursor: pointer;
  font-size: 0.875rem;
  color: #374151;
}

.form-actions {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background-color: #f3f4f6;
  color: #111827;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e5e7eb;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
