<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  getAdminPrograms, createProgram, updateProgram, deleteProgram,
  getProgramTypes, createProgramType, deleteProgramType,
  type AdminProgram, type ProgramType,
} from '@/infrastructure/api/clients/panel/admin/programs.api'

const { t, locale } = useI18n()

// State
const programs = ref<AdminProgram[]>([])
const types = ref<ProgramType[]>([])
const isLoading = ref(false)
const showCreateForm = ref(false)
const editingId = ref<number | null>(null)
const error = ref<string | null>(null)
const showTypeForm = ref(false)

// Form state
const emptyForm = () => ({
  program_key: '', display_name: { de: '', en: '', pl: '' },
  program_type: '', provider: '', icon: '',
})
const form = ref(emptyForm())
const newTypeForm = ref({ type_key: '', display_name: { de: '', en: '', pl: '' } })

// CSS helpers (reduce template repetition)
const inputCls = 'w-full px-3 py-2 rounded border border-[var(--color-border)] bg-[var(--color-background)] text-[var(--color-text)] text-sm'
const inputClsCompact = 'w-full px-2 py-1.5 rounded border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] text-sm'
const labelCls = 'block text-xs text-[var(--color-text-secondary)] mb-1'
const btnPrimary = 'px-4 py-2 bg-primary-600 text-white rounded text-sm hover:bg-primary-700 transition-colors'
const btnSecondary = 'px-4 py-2 border border-[var(--color-border)] rounded text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)] transition-colors'

// Helpers
const dn = (obj: Record<string, string>) => obj[locale.value] || obj.de || Object.values(obj)[0] || ''

const resetForm = () => {
  form.value = emptyForm()
  showCreateForm.value = false
  editingId.value = null
}

const resetTypeForm = () => {
  newTypeForm.value = { type_key: '', display_name: { de: '', en: '', pl: '' } }
  showTypeForm.value = false
}

// Load data
const loadData = async () => {
  isLoading.value = true
  error.value = null
  try {
    const [p, tp] = await Promise.all([getAdminPrograms(), getProgramTypes()])
    programs.value = p
    types.value = tp
  } catch (e) {
    error.value = String(e)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadData)

// Program CRUD
const startEdit = (program: AdminProgram) => {
  editingId.value = program.program_id
  showCreateForm.value = false
  form.value = {
    program_key: program.program_key,
    display_name: { ...program.display_name },
    program_type: program.program_type,
    provider: program.provider || '',
    icon: program.icon || '',
  }
}

const handleCreate = async () => {
  try {
    await createProgram({
      program_key: form.value.program_key,
      display_name: form.value.display_name,
      program_type: form.value.program_type,
      provider: form.value.provider || null,
      icon: form.value.icon || null,
    })
    resetForm()
    await loadData()
  } catch (e) { error.value = String(e) }
}

const handleUpdate = async (id: number) => {
  try {
    await updateProgram(id, {
      display_name: form.value.display_name,
      program_type: form.value.program_type,
      provider: form.value.provider || null,
      icon: form.value.icon || null,
    })
    resetForm()
    await loadData()
  } catch (e) { error.value = String(e) }
}

const handleDelete = async (id: number) => {
  if (!confirm(t('panel.programs.admin.confirmDelete'))) return
  try {
    await deleteProgram(id)
    await loadData()
  } catch (e) { error.value = String(e) }
}

// Type CRUD
const handleCreateType = async () => {
  try {
    await createProgramType({
      type_key: newTypeForm.value.type_key,
      display_name: newTypeForm.value.display_name,
    })
    resetTypeForm()
    await loadData()
  } catch (e) { error.value = String(e) }
}

const handleDeleteType = async (key: string) => {
  if (!confirm(t('panel.programs.admin.deleteType') + '?')) return
  try {
    await deleteProgramType(key)
    await loadData()
  } catch (e) { error.value = String(e) }
}
</script>

<template>
  <div class="p-6 max-w-6xl mx-auto space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-[var(--color-text)]">{{ t('panel.programs.admin.title') }}</h1>
      <button
        v-if="!showCreateForm"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
        @click="showCreateForm = true; editingId = null; form = emptyForm()"
      >+ {{ t('panel.programs.admin.create') }}</button>
    </div>

    <!-- Error -->
    <div v-if="error" class="p-3 bg-red-100 text-red-800 rounded-lg text-sm">
      {{ error }}
      <button class="ml-2 underline" @click="error = null">{{ t('common.close') }}</button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="text-center py-12 text-[var(--color-text-secondary)]">
      {{ t('common.loading') }}
    </div>

    <!-- Create form -->
    <div v-if="showCreateForm && !isLoading" class="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg space-y-3">
      <h3 class="text-lg font-semibold text-[var(--color-text)]">{{ t('panel.programs.admin.create') }}</h3>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.fields.programKey') }}</label>
          <input v-model="form.program_key" :class="inputCls" placeholder="e.g. fisi_ap1" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.fields.programType') }}</label>
          <select v-model="form.program_type" :class="inputCls">
            <option value="" disabled>--</option>
            <option v-for="tp in types" :key="tp.type_key" :value="tp.type_key">{{ dn(tp.display_name) }}</option>
          </select>
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (DE)</label>
          <input v-model="form.display_name.de" :class="inputCls" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (EN)</label>
          <input v-model="form.display_name.en" :class="inputCls" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (PL)</label>
          <input v-model="form.display_name.pl" :class="inputCls" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.fields.provider') }}</label>
          <input v-model="form.provider" :class="inputCls" placeholder="e.g. IHK" />
        </div>
        <div>
          <label :class="labelCls">{{ t('panel.programs.admin.fields.icon') }}</label>
          <input v-model="form.icon" :class="inputCls" placeholder="e.g. graduation-cap" />
        </div>
      </div>
      <div class="flex gap-2 pt-2">
        <button :class="btnPrimary" @click="handleCreate">{{ t('actions.save') }}</button>
        <button :class="btnSecondary" @click="resetForm">{{ t('actions.cancel') }}</button>
      </div>
    </div>

    <!-- Programs table -->
    <div v-if="!isLoading" class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-[var(--color-border)] bg-[var(--color-background)]">
            <th class="text-left px-4 py-3 text-[var(--color-text-secondary)] font-medium">{{ t('panel.programs.admin.fields.icon') }}</th>
            <th class="text-left px-4 py-3 text-[var(--color-text-secondary)] font-medium">{{ t('panel.programs.admin.fields.displayName') }}</th>
            <th class="text-left px-4 py-3 text-[var(--color-text-secondary)] font-medium">{{ t('panel.programs.admin.fields.programType') }}</th>
            <th class="text-left px-4 py-3 text-[var(--color-text-secondary)] font-medium">{{ t('panel.programs.admin.fields.provider') }}</th>
            <th class="text-right px-4 py-3 text-[var(--color-text-secondary)] font-medium">{{ t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="programs.length === 0">
            <td colspan="5" class="px-4 py-8 text-center text-[var(--color-text-secondary)]">{{ t('panel.programs.catalog.noPrograms') }}</td>
          </tr>
          <template v-for="prog in programs" :key="prog.program_id">
            <!-- Display row -->
            <tr v-if="editingId !== prog.program_id" class="border-b border-[var(--color-border)] hover:bg-[var(--color-background)] transition-colors">
              <td class="px-4 py-3 text-lg">{{ prog.icon || '--' }}</td>
              <td class="px-4 py-3 text-[var(--color-text)] font-medium">
                {{ dn(prog.display_name) }}
                <span class="text-xs text-[var(--color-text-secondary)] ml-1">({{ prog.program_key }})</span>
              </td>
              <td class="px-4 py-3 text-[var(--color-text-secondary)]">{{ prog.program_type }}</td>
              <td class="px-4 py-3 text-[var(--color-text-secondary)]">{{ prog.provider || '--' }}</td>
              <td class="px-4 py-3 text-right space-x-2">
                <button class="text-primary-600 hover:text-primary-800 text-sm" @click="startEdit(prog)">{{ t('panel.programs.admin.edit') }}</button>
                <button class="text-red-600 hover:text-red-800 text-sm" @click="handleDelete(prog.program_id)">{{ t('panel.programs.admin.delete') }}</button>
              </td>
            </tr>
            <!-- Inline edit row -->
            <tr v-else class="border-b border-[var(--color-border)] bg-[var(--color-background)]">
              <td colspan="5" class="px-4 py-3">
                <div class="grid grid-cols-3 gap-3">
                  <div>
                    <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (DE)</label>
                    <input v-model="form.display_name.de" :class="inputClsCompact" />
                  </div>
                  <div>
                    <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (EN)</label>
                    <input v-model="form.display_name.en" :class="inputClsCompact" />
                  </div>
                  <div>
                    <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (PL)</label>
                    <input v-model="form.display_name.pl" :class="inputClsCompact" />
                  </div>
                  <div>
                    <label :class="labelCls">{{ t('panel.programs.admin.fields.programType') }}</label>
                    <select v-model="form.program_type" :class="inputClsCompact">
                      <option v-for="tp in types" :key="tp.type_key" :value="tp.type_key">{{ dn(tp.display_name) }}</option>
                    </select>
                  </div>
                  <div>
                    <label :class="labelCls">{{ t('panel.programs.admin.fields.provider') }}</label>
                    <input v-model="form.provider" :class="inputClsCompact" />
                  </div>
                  <div>
                    <label :class="labelCls">{{ t('panel.programs.admin.fields.icon') }}</label>
                    <input v-model="form.icon" :class="inputClsCompact" />
                  </div>
                </div>
                <div class="flex gap-2 mt-3">
                  <button :class="btnPrimary" @click="handleUpdate(prog.program_id)">{{ t('actions.save') }}</button>
                  <button :class="btnSecondary" @click="resetForm">{{ t('actions.cancel') }}</button>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Types section -->
    <div v-if="!isLoading" class="space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-lg font-semibold text-[var(--color-text)]">{{ t('panel.programs.admin.types') }}</h2>
        <button
          v-if="!showTypeForm"
          class="px-3 py-1.5 border border-[var(--color-border)] rounded text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)] transition-colors"
          @click="showTypeForm = true"
        >+ {{ t('panel.programs.admin.createType') }}</button>
      </div>

      <!-- Create type form -->
      <div v-if="showTypeForm" class="p-4 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label :class="labelCls">{{ t('panel.programs.admin.fields.programKey') }}</label>
            <input v-model="newTypeForm.type_key" :class="inputCls" placeholder="e.g. ihk_exam" />
          </div>
          <div>
            <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (DE)</label>
            <input v-model="newTypeForm.display_name.de" :class="inputCls" />
          </div>
          <div>
            <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (EN)</label>
            <input v-model="newTypeForm.display_name.en" :class="inputCls" />
          </div>
          <div>
            <label :class="labelCls">{{ t('panel.programs.admin.fields.displayName') }} (PL)</label>
            <input v-model="newTypeForm.display_name.pl" :class="inputCls" />
          </div>
        </div>
        <div class="flex gap-2">
          <button :class="btnPrimary" @click="handleCreateType">{{ t('actions.save') }}</button>
          <button :class="btnSecondary" @click="resetTypeForm">{{ t('actions.cancel') }}</button>
        </div>
      </div>

      <!-- Types list -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg divide-y divide-[var(--color-border)]">
        <div v-if="types.length === 0" class="px-4 py-6 text-center text-[var(--color-text-secondary)] text-sm">
          {{ t('panel.programs.catalog.noPrograms') }}
        </div>
        <div v-for="tp in types" :key="tp.type_key" class="flex items-center justify-between px-4 py-3">
          <div>
            <span class="text-[var(--color-text)] font-medium">{{ dn(tp.display_name) }}</span>
            <span class="text-xs text-[var(--color-text-secondary)] ml-2">({{ tp.type_key }})</span>
          </div>
          <button class="text-red-600 hover:text-red-800 text-sm" @click="handleDeleteType(tp.type_key)">
            {{ t('panel.programs.admin.deleteType') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
