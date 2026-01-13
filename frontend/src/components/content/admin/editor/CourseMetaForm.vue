<template>
  <div class="px-6 py-6 space-y-6">
    <h2 class="text-lg font-medium text-gray-900">Kurs-Einstellungen</h2>

    <!-- Title -->
    <div>
      <label for="title" class="block text-sm font-medium text-gray-700">Titel</label>
      <input
        id="title"
        v-model="localCourse.title"
        type="text"
        @blur="updateMeta"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
      />
    </div>

    <!-- Description -->
    <div>
      <label for="description" class="block text-sm font-medium text-gray-700">Beschreibung</label>
      <textarea
        id="description"
        v-model="localCourse.description"
        rows="4"
        @blur="updateMeta"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
      ></textarea>
    </div>

    <!-- Category -->
    <div>
      <label for="category" class="block text-sm font-medium text-gray-700">Kategorie</label>
      <select
        id="category"
        v-model="localCourse.category_id"
        @change="updateMeta"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
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
      <p v-if="loadingCategories" class="mt-1 text-xs text-gray-500">Kategorien werden geladen...</p>
    </div>

    <!-- Level -->
    <div>
      <label for="level" class="block text-sm font-medium text-gray-700">Schwierigkeitsgrad</label>
      <select
        id="level"
        v-model="localCourse.level"
        @change="updateMeta"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
      >
        <option value="beginner">Anfänger</option>
        <option value="intermediate">Fortgeschritten</option>
        <option value="advanced">Erweitert</option>
        <option value="expert">Experte</option>
      </select>
    </div>

    <!-- Language -->
    <div>
      <label for="language" class="block text-sm font-medium text-gray-700">Sprache</label>
      <select
        id="language"
        v-model="localCourse.language"
        @change="updateMeta"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
      >
        <option value="de">Deutsch</option>
        <option value="en">English</option>
        <option value="pl">Polski</option>
      </select>
    </div>

    <!-- Visibility -->
    <div>
      <label for="visibility" class="block text-sm font-medium text-gray-700">Sichtbarkeit</label>
      <select
        id="visibility"
        v-model="localCourse.visibility"
        @change="updateMeta"
        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
      >
        <option value="private">Privat</option>
        <option value="community_public">Community (öffentlich)</option>
        <option value="marketplace">Marketplace</option>
      </select>
    </div>

    <!-- Publish Status -->
    <div class="flex items-center justify-between pt-4 border-t">
      <div>
        <p class="text-sm font-medium text-gray-900">Veröffentlichungsstatus</p>
        <p class="text-sm text-gray-500">
          {{ localCourse.is_published ? 'Veröffentlicht' : 'Entwurf' }}
        </p>
      </div>
      <button
        @click="togglePublish"
        :class="[
          'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
          localCourse.is_published ? 'bg-blue-600' : 'bg-gray-200',
        ]"
      >
        <span
          :class="[
            'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
            localCourse.is_published ? 'translate-x-5' : 'translate-x-0',
          ]"
        />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useCourseEditorStore } from '@/store/modules/content'
import { getCategoryTree, type Category, type CategoryTreeNode } from '@/api/categories.api'

const editorStore = useCourseEditorStore()

const localCourse = ref({ ...editorStore.currentCourse })
const categories = ref<CategoryTreeNode[]>([])
const loadingCategories = ref(false)

// Flatten categories with indentation for hierarchical display
const flatCategories = computed(() => {
  const result: Array<Category & { indent: string }> = []

  const flatten = (cats: CategoryTreeNode[], level: number) => {
    for (const cat of cats) {
      result.push({
        ...cat,
        indent: '—'.repeat(level) + (level > 0 ? ' ' : '')
      })
      if (cat.children && cat.children.length > 0) {
        flatten(cat.children, level + 1)
      }
    }
  }

  flatten(categories.value, 0)
  return result
})

const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const tree = await getCategoryTree(false)
    categories.value = tree.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
    categories.value = []
  } finally {
    loadingCategories.value = false
  }
}

watch(
  () => editorStore.currentCourse,
  (newCourse) => {
    if (newCourse) {
      localCourse.value = { ...newCourse }
    }
  },
  { deep: true }
)

const updateMeta = async () => {
  if (!localCourse.value) return

  await editorStore.updateCourseMeta({
    title: localCourse.value.title,
    subtitle: localCourse.value.subtitle,
    description: localCourse.value.description,
    category_id: localCourse.value.category_id,
    level: localCourse.value.level,
    language: localCourse.value.language,
    visibility: localCourse.value.visibility,
  })
}

const togglePublish = async () => {
  if (localCourse.value.is_published) {
    await editorStore.unpublishCourse()
  } else {
    await editorStore.publishCourse()
  }
  localCourse.value = { ...editorStore.currentCourse! }
}

onMounted(() => {
  loadCategories()
})
</script>
