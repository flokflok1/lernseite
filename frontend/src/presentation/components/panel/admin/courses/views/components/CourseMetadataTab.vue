<!--
  Course Metadata Tab

  Form for editing course metadata: title, description, category, level,
  language, price, tags, and visibility.
-->

<template>
  <div class="p-6">
    <form @submit.prevent="$emit('save')" class="space-y-6">
      <!-- Title -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Titel *
        </label>
        <input
          :value="form.title"
          @input="$emit('update:form', { ...form, title: ($event.target as HTMLInputElement).value })"
          type="text"
          required
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          :placeholder="titlePlaceholder"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
          Beschreibung
        </label>
        <textarea
          :value="form.description"
          @input="$emit('update:form', { ...form, description: ($event.target as HTMLTextAreaElement).value })"
          rows="4"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          :placeholder="descriptionPlaceholder"
        ></textarea>
      </div>

      <!-- Category & Level -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Kategorie
          </label>
          <select
            :value="form.category_id"
            @change="$emit('update:form', { ...form, category_id: ($event.target as HTMLSelectElement).value || null })"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option :value="null">Keine Kategorie</option>
            <option
              v-for="cat in flatCategories"
              :key="cat.category_id"
              :value="cat.category_id"
            >
              {{ cat.indent }}{{ cat.name }}
            </option>
          </select>
          <p v-if="loadingCategories" class="mt-1 text-xs text-[var(--color-text-secondary)]">Kategorien werden geladen...</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Level
          </label>
          <select
            :value="form.level"
            @change="$emit('update:form', { ...form, level: ($event.target as HTMLSelectElement).value })"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="beginner">Anfaenger</option>
            <option value="intermediate">Fortgeschritten</option>
            <option value="advanced">Experte</option>
            <option value="expert">Meister</option>
          </select>
        </div>
      </div>

      <!-- Language & Price -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Sprache
          </label>
          <select
            :value="form.language"
            @change="$emit('update:form', { ...form, language: ($event.target as HTMLSelectElement).value })"
            class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          >
            <option value="de">Deutsch</option>
            <option value="en">English</option>
            <option value="fr">Francais</option>
            <option value="es">Espanol</option>
            <option value="it">Italiano</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
            Preis (EUR)
          </label>
          <input
            :value="form.price"
            @input="$emit('update:form', { ...form, price: Number(($event.target as HTMLInputElement).value) })"
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
          Tags (kommagetrennt)
        </label>
        <input
          :value="tagsInput"
          @input="$emit('update:tagsInput', ($event.target as HTMLInputElement).value)"
          type="text"
          class="w-full px-3 py-2 border border-[var(--color-border)] rounded-lg bg-[var(--color-surface)] text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
          placeholder="python, programmieren, anfaenger"
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
          @change="$emit('update:form', { ...form, is_public: ($event.target as HTMLInputElement).checked })"
          type="checkbox"
          id="is_public"
          class="w-4 h-4 text-[var(--color-primary)] border-[var(--color-border)] rounded focus:ring-[var(--color-primary)]"
        />
        <label for="is_public" class="text-sm font-medium text-[var(--color-text-primary)]">
          Kurs oeffentlich sichtbar
        </label>
      </div>

      <!-- Save Button -->
      <div class="flex gap-3 pt-4">
        <button
          type="submit"
          :disabled="saving"
          class="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Speichert...' : 'Aenderungen speichern' }}
        </button>
        <button
          type="button"
          @click="$emit('reset')"
          class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
        >
          Zuruecksetzen
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
interface CategoryOption {
  category_id: number | string
  name: string
  indent: string
}

interface CourseForm {
  title: string
  description: string
  category_id: number | null
  level: string
  language: string
  price: number
  is_public: boolean
  tags: string[]
}

interface Props {
  form: CourseForm
  tagsInput: string
  flatCategories: CategoryOption[]
  loadingCategories: boolean
  saving: boolean
  titlePlaceholder?: string
  descriptionPlaceholder?: string
}

withDefaults(defineProps<Props>(), {
  titlePlaceholder: 'Kurstititel eingeben...',
  descriptionPlaceholder: 'Kursbeschreibung eingeben...'
})

defineEmits<{
  (e: 'save'): void
  (e: 'reset'): void
  (e: 'update:form', form: CourseForm): void
  (e: 'update:tagsInput', value: string): void
}>()
</script>
