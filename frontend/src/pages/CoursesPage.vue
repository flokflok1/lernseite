<template>
  <div class="courses-page">
    <h1 class="text-3xl font-bold text-[var(--color-text-primary)] mb-6">{{ t('courses.title') }}</h1>

    <!-- Main Tab Navigation -->
    <div class="flex border-b border-[var(--color-border)] mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id; selectedCategory = ''"
        class="px-6 py-3 text-sm font-medium transition-colors relative"
        :class="[
          activeTab === tab.id
            ? 'text-primary-600 border-b-2 border-primary-600 -mb-px'
            : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
        ]"
      >
        <span class="flex items-center gap-2">
          <span>{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
          <span
            v-if="tab.count !== undefined"
            class="px-2 py-0.5 text-xs rounded-full"
            :class="activeTab === tab.id ? 'bg-primary-100 text-primary-700' : 'bg-[var(--color-surface-secondary)] text-[var(--color-text-secondary)]'"
          >
            {{ tab.count }}
          </span>
        </span>
      </button>
    </div>

    <!-- LSX Academy Tab -->
    <div v-if="activeTab === 'academy'">
      <!-- Category Navigation - Top Level -->
      <div v-if="topLevelCategories.length > 0" class="flex flex-wrap gap-2 mb-4">
        <button
          @click="selectedCategory = ''; selectedSubCategory = ''"
          class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
          :class="selectedCategory === ''
            ? 'bg-primary-600 text-white'
            : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] border border-[var(--color-border)]'"
        >
          {{ t('courses.all_courses') }}
        </button>
        <button
          v-for="category in topLevelCategories"
          :key="category.category_id"
          @click="selectTopCategory(category.category_id)"
          class="px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
          :class="selectedCategory === category.category_id || isChildOfSelected(category.category_id)
            ? 'bg-primary-600 text-white'
            : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] border border-[var(--color-border)]'"
        >
          <span v-if="category.icon">{{ category.icon }}</span>
          <span>{{ category.name }}</span>
          <span
            v-if="category.course_count"
            class="px-1.5 py-0.5 text-xs rounded-full"
            :class="selectedCategory === category.category_id ? 'bg-white/20' : 'bg-[var(--color-surface-secondary)]'"
          >
            {{ category.course_count }}
          </span>
        </button>
      </div>

      <!-- Subcategory Navigation - Children of selected top-level -->
      <div v-if="selectedCategoryChildren.length > 0" class="flex flex-wrap gap-2 mb-6 pl-4 border-l-2 border-primary-200">
        <button
          @click="selectedSubCategory = ''"
          class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors"
          :class="selectedSubCategory === ''
            ? 'bg-primary-500 text-white'
            : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] border border-[var(--color-border)]'"
        >
          {{ t('courses.all_in_category', { category: getSelectedCategoryName() }) }}
        </button>
        <button
          v-for="subcat in selectedCategoryChildren"
          :key="subcat.category_id"
          @click="selectedSubCategory = subcat.category_id"
          class="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5"
          :class="selectedSubCategory === subcat.category_id
            ? 'bg-primary-500 text-white'
            : 'bg-[var(--color-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-secondary)] border border-[var(--color-border)]'"
        >
          <span v-if="subcat.icon">{{ subcat.icon }}</span>
          <span>{{ subcat.name }}</span>
        </button>
      </div>

      <!-- Search & Level Filter -->
      <div class="flex gap-4 mb-6">
        <div class="flex-1 relative">
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="t('courses.search_placeholder')"
            class="w-full px-4 py-2 pl-10 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-secondary)]">🔍</span>
        </div>
        <select
          v-model="selectedLevel"
          class="px-4 py-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="">{{ t('courses.level_all') }}</option>
          <option value="beginner">{{ t('courses.level_beginner') }}</option>
          <option value="intermediate">{{ t('courses.level_intermediate') }}</option>
          <option value="advanced">{{ t('courses.level_advanced') }}</option>
        </select>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>

      <!-- Course Grid -->
      <div v-else-if="filteredAcademyCourses.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <CourseCard
          v-for="course in filteredAcademyCourses"
          :key="course.course_id"
          :course="course"
          @click="openCourse(course)"
        />
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <div class="text-6xl mb-4">📚</div>
        <h3 class="text-xl font-semibold text-[var(--color-text-primary)] mb-2">{{ t('courses.no_courses') }}</h3>
        <p class="text-[var(--color-text-secondary)]">
          {{ searchQuery ? t('courses.no_courses_hint_search') : t('courses.no_courses_hint_academy') }}
        </p>
      </div>
    </div>

    <!-- Community Kurse Tab -->
    <div v-else-if="activeTab === 'community'">
      <div class="text-center py-12 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
        <div class="text-6xl mb-4">🌍</div>
        <h3 class="text-xl font-semibold text-[var(--color-text-primary)] mb-2">{{ t('courses.community_title') }}</h3>
        <p class="text-[var(--color-text-secondary)] mb-4">
          {{ t('courses.community_desc') }}
        </p>
        <span class="inline-block px-4 py-2 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
          🚧 {{ t('courses.coming_soon') }}
        </span>
      </div>
    </div>

    <!-- Eigene Kurse Tab -->
    <div v-else-if="activeTab === 'own'">
      <!-- Enrolled Courses -->
      <div v-if="enrolledCourses.length > 0" class="mb-8">
        <h2 class="text-xl font-semibold text-[var(--color-text-primary)] mb-4">{{ t('courses.enrolled_courses') }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <EnrolledCourseCard
            v-for="enrollment in enrolledCourses"
            :key="enrollment.enrollment_id"
            :enrollment="enrollment"
            @click="continueCourse(enrollment)"
          />
        </div>
      </div>

      <!-- Created Courses (for Creators) -->
      <div v-if="myCourses.length > 0">
        <h2 class="text-xl font-semibold text-[var(--color-text-primary)] mb-4">{{ t('courses.created_courses') }}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <CourseCard
            v-for="course in myCourses"
            :key="course.course_id"
            :course="course"
            :show-edit="true"
            @click="openCourse(course)"
            @edit="editCourse(course)"
          />
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="enrolledCourses.length === 0 && myCourses.length === 0" class="text-center py-12 bg-[var(--color-surface)] rounded-lg border border-[var(--color-border)]">
        <div class="text-6xl mb-4">📖</div>
        <h3 class="text-xl font-semibold text-[var(--color-text-primary)] mb-2">{{ t('courses.no_courses_yet') }}</h3>
        <p class="text-[var(--color-text-secondary)] mb-4">
          {{ t('courses.no_courses_hint_own') }}
        </p>
        <Button variant="primary" @click="activeTab = 'academy'">
          {{ t('courses.discover_courses') }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  searchCourses,
  getMyEnrolledCourses,
  getMyCourses,
  type CourseListItem,
  type EnrolledCourse
} from '@/api/courses.api'
import { getCategoryTree, type Category, type CategoryTreeNode } from '@/api/categories.api'
import { useAuthStore } from '@/store/auth.store'
import Button from '@/components/base/Button.vue'
import CourseCard from '@/components/user/courses/CourseCard.vue'
import EnrolledCourseCard from '@/components/user/courses/EnrolledCourseCard.vue'

// ============================================================================
// State
// ============================================================================

const router = useRouter()
const authStore = useAuthStore()
const { t, locale } = useI18n()
const loading = ref(true)
const activeTab = ref<'academy' | 'community' | 'own'>('academy')
const searchQuery = ref('')
const selectedCategory = ref<number | ''>('')
const selectedSubCategory = ref<number | ''>('')
const selectedLevel = ref('')

const academyCourses = ref<CourseListItem[]>([])
const enrolledCourses = ref<EnrolledCourse[]>([])
const myCourses = ref<CourseListItem[]>([])
const categories = ref<Category[]>([])
const categoryTree = ref<CategoryTreeNode[]>([])

// Check if user is admin
const isAdmin = computed(() => {
  const role = authStore.user?.role
  return role === 'admin' || role === 'superadmin' || role === 'moderator'
})

// ============================================================================
// Computed
// ============================================================================

const tabs = computed(() => {
  void locale.value // Trigger reactivity on language change
  return [
    { id: 'academy' as const, label: t('courses.tab_academy'), icon: '🎓', count: academyCourses.value.length },
    { id: 'community' as const, label: t('courses.tab_community'), icon: '🌍', count: undefined },
    { id: 'own' as const, label: t('courses.tab_own'), icon: '📖', count: enrolledCourses.value.length }
  ]
})

// Top-level categories (no parent)
const topLevelCategories = computed(() => {
  return categoryTree.value.filter(cat => !cat.parent_id)
})

// Children of the currently selected top-level category
const selectedCategoryChildren = computed((): CategoryTreeNode[] => {
  if (!selectedCategory.value) return []
  const findCategory = (cats: CategoryTreeNode[]): CategoryTreeNode | null => {
    for (const cat of cats) {
      if (cat.category_id === selectedCategory.value) return cat
      if (cat.children && cat.children.length > 0) {
        const found = findCategory(cat.children)
        if (found) return found
      }
    }
    return null
  }
  const selected = findCategory(categoryTree.value)
  return selected?.children || []
})

// Get the name of the currently selected category
const getSelectedCategoryName = (): string => {
  if (!selectedCategory.value) return ''
  const findCategory = (cats: CategoryTreeNode[]): string => {
    for (const cat of cats) {
      if (cat.category_id === selectedCategory.value) return cat.name
      if (cat.children && cat.children.length > 0) {
        const found = findCategory(cat.children)
        if (found) return found
      }
    }
    return ''
  }
  return findCategory(categoryTree.value)
}

// Check if a category is a child of the currently selected category
const isChildOfSelected = (categoryId: number): boolean => {
  if (!selectedCategory.value) return false
  return selectedCategory.value === categoryId
}

// Select a top-level category
const selectTopCategory = (categoryId: number) => {
  selectedCategory.value = categoryId
  selectedSubCategory.value = ''
}

// Get all child category IDs for a parent category (for hierarchical filtering)
const getChildCategoryIds = (parentId: number): number[] => {
  const ids: number[] = [parentId]

  // Recursively find the category and all its descendants
  const findCategoryAndChildren = (cats: CategoryTreeNode[]): void => {
    for (const cat of cats) {
      // If this category's parent is already in our list, add this category
      if (cat.category_id === parentId) {
        // Found the parent, now add all children recursively
        const addAllChildren = (children: CategoryTreeNode[]): void => {
          for (const child of children) {
            ids.push(child.category_id)
            if (child.children && child.children.length > 0) {
              addAllChildren(child.children)
            }
          }
        }
        if (cat.children && cat.children.length > 0) {
          addAllChildren(cat.children)
        }
      }
      // Continue searching in children
      if (cat.children && cat.children.length > 0) {
        findCategoryAndChildren(cat.children)
      }
    }
  }

  findCategoryAndChildren(categoryTree.value)
  return ids
}

const filteredAcademyCourses = computed(() => {
  let courses = academyCourses.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    courses = courses.filter(c =>
      c.title.toLowerCase().includes(query) ||
      c.description?.toLowerCase().includes(query)
    )
  }

  // If subcategory is selected, filter by that specific subcategory
  if (selectedSubCategory.value) {
    courses = courses.filter(c => c.category_id === selectedSubCategory.value)
  } else if (selectedCategory.value) {
    // Include courses in this category AND all child categories
    const categoryIds = getChildCategoryIds(selectedCategory.value as number)
    courses = courses.filter(c => c.category_id && categoryIds.includes(c.category_id))
  }

  if (selectedLevel.value) {
    courses = courses.filter(c => c.level === selectedLevel.value)
  }

  return courses
})

// ============================================================================
// Methods
// ============================================================================

const loadCategories = async () => {
  try {
    // Load category tree and flatten for display
    const tree = await getCategoryTree(true)
    // Store full tree for hierarchical filtering
    categoryTree.value = tree.categories || []

    const flatList: Category[] = []

    const flatten = (cats: CategoryTreeNode[], level: number = 0) => {
      for (const cat of cats) {
        flatList.push({
          ...cat,
          name: level > 0 ? `${'  '.repeat(level)}${cat.name}` : cat.name
        })
        if (cat.children && cat.children.length > 0) {
          flatten(cat.children, level + 1)
        }
      }
    }

    flatten(tree.categories || [])
    categories.value = flatList
  } catch (error) {
    console.error('Failed to load categories:', error)
    categoryTree.value = []
    categories.value = []
  }
}

const loadCourses = async () => {
  loading.value = true
  try {
    // Load categories first
    await loadCategories()

    // Load academy courses (course_type=academy)
    // Admins can see drafts, regular users only see published
    const academyResult = await searchCourses({
      per_page: 50,
      course_type: 'academy',
      include_drafts: isAdmin.value
    })
    academyCourses.value = academyResult.items

    // Load enrolled courses
    try {
      const enrolledResult = await getMyEnrolledCourses({ status: 'active' })
      enrolledCourses.value = enrolledResult.items
    } catch {
      // User might not have enrollments
      enrolledCourses.value = []
    }

    // Load my created courses (course_type=creator, user's own courses only)
    // This should NOT show admin-created academy courses
    try {
      myCourses.value = await getMyCourses()
    } catch {
      // User might not have created courses
      myCourses.value = []
    }
  } catch (error) {
    console.error('Failed to load courses:', error)
  } finally {
    loading.value = false
  }
}

const openCourse = (course: CourseListItem) => {
  router.push({ name: 'CourseOverview', params: { courseId: course.course_id } })
}

const continueCourse = (enrollment: EnrolledCourse) => {
  router.push({ name: 'CourseOverview', params: { courseId: enrollment.course_id } })
}

const editCourse = (course: CourseListItem) => {
  router.push({ name: 'CreatorCourseEditor', params: { courseId: course.course_id } })
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  loadCourses()
})
</script>
