<!--
  CourseMetadataForm - Metadata editing form for course editor

  Handles title, description, category, level, language, price,
  tags, and visibility settings.
-->

<template>
  <div class="p-6">
    <form @submit.prevent="$emit('save')" class="space-y-6">
      <!-- Title -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('courseEditor.metadata.title') }}
        </label>
        <input
          :value="form.title"
          @input="updateField('title', ($event.target as HTMLInputElement).value)"
          type="text"
          required
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          :placeholder="$t('courseEditor.metadata.titlePlaceholder')"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('courseEditor.metadata.description') }}
        </label>
        <textarea
          :value="form.description"
          @input="updateField('description', ($event.target as HTMLTextAreaElement).value)"
          rows="4"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          :placeholder="$t('courseEditor.metadata.descriptionPlaceholder')"
        ></textarea>
      </div>

      <!-- Category & Level -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('courseEditor.metadata.category') }}
          </label>
          <select
            :value="form.category_id"
            @change="updateField('category_id', Number(($event.target as HTMLSelectElement).value) || null)"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option :value="null">{{ $t('courseEditor.metadata.noCategory') }}</option>
            <option
              v-for="cat in flatCategories"
              :key="cat.category_id"
              :value="cat.category_id"
            >
              {{ cat.indent }}{{ cat.name }}
            </option>
          </select>
          <p v-if="loadingCategories" class="mt-1 text-xs text-[var(--color-text-secondary)]">
            {{ $t('courseEditor.metadata.loadingCategories') }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('courseEditor.metadata.level') }}
          </label>
          <select
            :value="form.level"
            @change="updateField('level', ($event.target as HTMLSelectElement).value)"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="beginner">{{ $t('courseEditor.metadata.levelBeginner') }}</option>
            <option value="intermediate">{{ $t('courseEditor.metadata.levelIntermediate') }}</option>
            <option value="advanced">{{ $t('courseEditor.metadata.levelAdvanced') }}</option>
            <option value="expert">{{ $t('courseEditor.metadata.levelExpert') }}</option>
          </select>
        </div>
      </div>

      <!-- Language & Price -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('courseEditor.metadata.language') }}
          </label>
          <select
            :value="form.language"
            @change="updateField('language', ($event.target as HTMLSelectElement).value)"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="de">Deutsch</option>
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="es">Español</option>
            <option value="it">Italiano</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            {{ $t('courseEditor.metadata.price') }}
          </label>
          <input
            :value="form.price"
            @input="updateField('price', Number(($event.target as HTMLInputElement).value))"
            type="number"
            min="0"
            step="0.01"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            placeholder="0.00"
          />
        </div>
      </div>

      <!-- Tags -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          {{ $t('courseEditor.metadata.tags') }}
        </label>
        <input
          :value="tagsInput"
          @input="$emit('update:tags-input', ($event.target as HTMLInputElement).value)"
          type="text"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          :placeholder="$t('courseEditor.metadata.tagsPlaceholder')"
        />
        <div v-if="form.tags && form.tags.length > 0" class="flex flex-wrap gap-2 mt-2">
          <span
            v-for="tag in form.tags"
            :key="tag"
            class="px-2 py-1 bg-[var(--color-primary)]/10 text-[var(--color-primary)] rounded text-xs"
          >
            {{ tag }}
          </span>
        </div>
      </div>

      <!-- Visibility -->
      <div class="flex items-center gap-3">
        <input
          :checked="form.is_public"
          @change="updateField('is_public', ($event.target as HTMLInputElement).checked)"
          type="checkbox"
          id="is_public"
          class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded focus:ring-[var(--color-primary)]"
        />
        <label for="is_public" class="text-sm font-medium text-[var(--color-text-primary)]">
          {{ $t('courseEditor.metadata.isPublic') }}
        </label>
      </div>

      <!-- Save Button -->
      <div class="flex gap-3 pt-4">
        <button
          type="submit"
          :disabled="saving"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? $t('courseEditor.metadata.saving') : $t('courseEditor.metadata.saveChanges') }}
        </button>
        <button
          type="button"
          @click="$emit('reset')"
          class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          {{ $t('courseEditor.metadata.reset') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import type { CourseForm, Category } from './composables/useCourseEditor'

interface Props {
  form: CourseForm
  tagsInput: string
  flatCategories: Array<Category & { indent: string }>
  loadingCategories: boolean
  saving: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:form', form: CourseForm): void
  (e: 'update:tags-input', value: string): void
  (e: 'save'): void
  (e: 'reset'): void
}>()

function updateField(field: keyof CourseForm, value: unknown): void {
  emit('update:form', { ...props.form, [field]: value })
}
</script>
