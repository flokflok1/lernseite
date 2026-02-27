/**
 * CourseSelector.vue
 *
 * Course list view shown before the editor when no course is selected.
 * Displays user's courses with tabs (Active / Archive / Trash),
 * search, create, and per-tab context actions.
 * Dark-mode-ready using CSS variables from the start.
 */

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCourseEditorStore } from '@/application/stores/modules/content/courseEditor.store'
import { useCourseActions } from '@/presentation/components/panel/editor/shared/composables'
import ConfirmBanner from '@/presentation/components/panel/editor/shared/ConfirmBanner.vue'

const { t } = useI18n()
const store = useCourseEditorStore()

const emit = defineEmits<{
  select: [courseId: number]
  create: []
}>()

type TabKey = 'active' | 'archived' | 'trash'

const courseActions = useCourseActions()
const activeTab = ref<TabKey>('active')
const searchQuery = ref('')
const confirmingEmptyTrash = ref(false)

onMounted(() => {
  store.listCourses('active')
})

watch(activeTab, (tab) => {
  searchQuery.value = ''
  courseActions.cancelAction()
  confirmingEmptyTrash.value = false
  store.listCourses(tab)
})

const filteredCourses = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return store.courseList
  return store.courseList.filter(
    (c: any) =>
      c.title?.toLowerCase().includes(q) ||
      c.description?.toLowerCase().includes(q)
  )
})

const trashCount = computed(() => {
  if (activeTab.value === 'trash') return store.courseList.length
  return 0
})

const getStatusKey = (course: any): string => {
  if (course.trashed_at) return 'archived'
  if (course.status === 'published' || course.published) return 'published'
  if (course.status === 'archived') return 'archived'
  return 'draft'
}

const getStatusClass = (course: any): string => {
  return `status-${getStatusKey(course)}`
}

const getCourseTypeLabel = (course: any): string => {
  return course.course_type === 'academy' ? 'Academy' : 'Creator'
}

const getCourseTypeClass = (course: any): string => {
  return course.course_type === 'academy' ? 'type-academy' : 'type-creator'
}

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString(undefined, { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const getDaysRemaining = (trashedAt: string): number => {
  const trashed = new Date(trashedAt)
  const purgeDate = new Date(trashed.getTime() + 30 * 24 * 60 * 60 * 1000)
  const now = new Date()
  const diff = Math.ceil((purgeDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return Math.max(0, diff)
}

// --- Actions (delegated to shared composable) ---

const cancelAllConfirm = () => {
  courseActions.cancelAction()
  confirmingEmptyTrash.value = false
}

const requestEmptyTrash = () => {
  confirmingEmptyTrash.value = true
}

const confirmEmptyTrash = async () => {
  confirmingEmptyTrash.value = false
  try {
    for (const c of [...store.courseList]) {
      await store.permanentDelete(c.course_id)
    }
  } catch { /* error in store */ }
}

function getCardConfirmMessage(course: any): string {
  if (courseActions.pendingAction.value === 'purge') {
    return t('panel.manualEditor.courseSelector.trash.confirmPermanentDelete', { title: course.title })
  }
  return t('panel.manualEditor.courseSelector.confirmDelete', { title: course.title })
}

function getCardConfirmLabel(): string {
  if (courseActions.pendingAction.value === 'purge') {
    return t('panel.manualEditor.courseSelector.trash.permanentDelete')
  }
  return t('panel.manualEditor.courseSelector.moveToTrash')
}
</script>

<template>
  <div class="course-selector">
    <!-- Header -->
    <div class="selector-header">
      <h2 class="selector-title">{{ $t('panel.manualEditor.courseSelector.title') }}</h2>
      <button class="btn-create" @click="emit('create')">
        + {{ $t('panel.manualEditor.courseSelector.createNew') }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="tab-bar">
      <button
        v-for="tab in (['active', 'archived', 'trash'] as TabKey[])"
        :key="tab"
        class="tab-btn"
        :class="{ 'tab-active': activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ $t(`panel.manualEditor.courseSelector.tabs.${tab}`) }}
        <span v-if="tab === 'trash' && activeTab === 'trash' && trashCount > 0" class="tab-count">
          {{ trashCount }}
        </span>
      </button>
    </div>

    <!-- Search -->
    <div class="search-bar">
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        :placeholder="$t('panel.manualEditor.courseSelector.search')"
      />
    </div>

    <!-- Trash hint -->
    <div v-if="activeTab === 'trash' && store.courseList.length > 0" class="trash-hint">
      <span>{{ $t('panel.manualEditor.courseSelector.trash.autoDeleteHint') }}</span>
      <button class="btn-empty-trash" @click="requestEmptyTrash">
        {{ $t('panel.manualEditor.courseSelector.trash.emptyTrash') }}
      </button>
    </div>

    <!-- Confirm empty trash -->
    <ConfirmBanner
      v-if="confirmingEmptyTrash"
      :message="$t('panel.manualEditor.courseSelector.trash.confirmEmptyTrash')"
      :confirm-label="$t('panel.manualEditor.courseSelector.trash.emptyTrash')"
      variant="danger"
      @confirm="confirmEmptyTrash"
      @cancel="cancelAllConfirm"
    />

    <!-- Loading -->
    <div v-if="store.courseListLoading" class="loading-state">
      <p>{{ $t('common.loading') }}...</p>
    </div>

    <!-- Empty states per tab -->
    <div v-else-if="store.courseList.length === 0" class="empty-state">
      <template v-if="activeTab === 'active'">
        <p class="empty-title">{{ $t('panel.manualEditor.courseSelector.noCourses') }}</p>
        <p class="empty-hint">{{ $t('panel.manualEditor.courseSelector.noCoursesHint') }}</p>
      </template>
      <template v-else-if="activeTab === 'archived'">
        <p class="empty-title">{{ $t('panel.manualEditor.courseSelector.archive.empty') }}</p>
      </template>
      <template v-else>
        <p class="empty-title">{{ $t('panel.manualEditor.courseSelector.trash.empty') }}</p>
      </template>
    </div>

    <!-- No search results -->
    <div v-else-if="filteredCourses.length === 0" class="empty-state">
      <p class="empty-title">{{ $t('panel.manualEditor.courseSelector.noResults') }}</p>
    </div>

    <!-- Course list -->
    <div v-else class="course-list">
      <div
        v-for="course in filteredCourses"
        :key="course.course_id"
        class="course-card"
        :class="{
          'card-confirming': courseActions.isConfirmingCourse(course.course_id)
        }"
        @click="activeTab === 'active' && !courseActions.isConfirmingCourse(course.course_id) && emit('select', course.course_id)"
      >
        <!-- Confirm action view (trash or permanent delete) -->
        <template v-if="courseActions.isConfirmingCourse(course.course_id)">
          <ConfirmBanner
            :message="getCardConfirmMessage(course)"
            :confirm-label="getCardConfirmLabel()"
            variant="danger"
            @confirm="courseActions.confirmAction()"
            @cancel="courseActions.cancelAction()"
          />
        </template>

        <!-- Normal view -->
        <template v-else>
          <div class="card-body">
            <div class="card-top">
              <span class="course-title">{{ course.title }}</span>
              <span class="type-badge" :class="getCourseTypeClass(course)">
                {{ getCourseTypeLabel(course) }}
              </span>
              <span v-if="activeTab === 'active'" class="status-badge" :class="getStatusClass(course)">
                {{ $t(`panel.manualEditor.courseSelector.status.${getStatusKey(course)}`) }}
              </span>
              <span v-if="activeTab === 'trash' && course.trashed_at" class="trash-countdown">
                {{ $t('panel.manualEditor.courseSelector.trash.daysRemaining', { days: getDaysRemaining(course.trashed_at) }) }}
              </span>
            </div>
            <p v-if="course.description" class="course-desc">{{ course.description }}</p>
            <div class="card-meta">
              <span v-if="course.chapter_count != null" class="meta-item">
                {{ $t('panel.manualEditor.courseSelector.chapters', { count: course.chapter_count }) }}
              </span>
              <span class="meta-item">
                {{ $t('panel.manualEditor.courseSelector.lastEdited') }}: {{ formatDate(course.updated_at || course.created_at) }}
              </span>
            </div>
          </div>

          <!-- Actions: Active tab -->
          <div v-if="activeTab === 'active'" class="card-actions">
            <button
              class="btn-action btn-archive"
              @click.stop="store.archiveCourse(course.course_id)"
              :title="$t('panel.manualEditor.courseSelector.archive.moveTo')"
            >
              &#128451;
            </button>
            <button
              class="btn-action btn-delete"
              @click.stop="courseActions.requestAction('trash', course.course_id)"
              :title="$t('panel.manualEditor.courseSelector.moveToTrash')"
            >
              &times;
            </button>
          </div>

          <!-- Actions: Archive tab -->
          <div v-if="activeTab === 'archived'" class="card-actions">
            <button
              class="btn-action btn-unarchive"
              @click.stop="store.unarchiveCourse(course.course_id)"
              :title="$t('panel.manualEditor.courseSelector.unarchive')"
            >
              &#8634;
            </button>
            <button
              class="btn-action btn-delete"
              @click.stop="courseActions.requestAction('trash', course.course_id)"
              :title="$t('panel.manualEditor.courseSelector.moveToTrash')"
            >
              &times;
            </button>
          </div>

          <!-- Actions: Trash tab -->
          <div v-if="activeTab === 'trash'" class="card-actions">
            <button
              class="btn-action btn-unarchive"
              @click.stop="store.restoreFromTrash(course.course_id)"
              :title="$t('panel.manualEditor.courseSelector.trash.restore')"
            >
              &#8634;
            </button>
            <button
              class="btn-action btn-delete"
              @click.stop="courseActions.requestAction('purge', course.course_id)"
              :title="$t('panel.manualEditor.courseSelector.trash.permanentDelete')"
            >
              &times;
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.course-selector {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  overflow: hidden;
  background: var(--color-bg);
}

.selector-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.selector-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.btn-create {
  padding: 8px 16px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: filter 0.15s;
}

.btn-create:hover {
  filter: brightness(0.9);
}

/* Tab bar */
.tab-bar {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0;
}

.tab-btn {
  padding: 8px 16px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-btn:hover {
  color: var(--color-text-primary);
}

.tab-btn.tab-active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

.tab-count {
  background: color-mix(in srgb, var(--color-text-tertiary) 20%, transparent);
  color: var(--color-text-secondary);
  padding: 1px 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
}

.tab-active .tab-count {
  background: color-mix(in srgb, var(--color-accent) 15%, transparent);
  color: var(--color-accent);
}

/* Search bar */
.search-bar {
  margin-bottom: 12px;
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  background: var(--color-surface);
  color: var(--color-text-primary);
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

/* Trash hint */
.trash-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin-bottom: 12px;
  background: color-mix(in srgb, var(--color-warning) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-warning) 25%, transparent);
  border-radius: 6px;
  font-size: 12px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.btn-empty-trash {
  padding: 4px 10px;
  background: var(--color-error);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: filter 0.15s;
  flex-shrink: 0;
}

.btn-empty-trash:hover {
  filter: brightness(0.9);
}

/* States */
.loading-state,
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin: 0 0 4px;
}

.empty-hint {
  font-size: 13px;
  margin: 0;
}

/* Course list */
.course-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  cursor: pointer;
  transition: all 0.15s;
}

.course-card:hover {
  border-color: var(--color-accent);
  background: color-mix(in srgb, var(--color-accent) 5%, var(--color-surface));
}

.course-card.card-confirming {
  border-color: var(--color-error);
  background: color-mix(in srgb, var(--color-error) 5%, var(--color-surface));
  cursor: default;
}

.card-body {
  flex: 1;
  min-width: 0;
}

.card-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.course-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.status-draft {
  background: color-mix(in srgb, var(--color-text-tertiary) 15%, transparent);
  color: var(--color-text-secondary);
}

.status-published {
  background: color-mix(in srgb, var(--color-success) 15%, transparent);
  color: var(--color-success);
}

.status-archived {
  background: color-mix(in srgb, var(--color-warning) 15%, transparent);
  color: var(--color-warning);
}

.trash-countdown {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--color-error) 12%, transparent);
  color: var(--color-error);
}

.type-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

.type-academy {
  background: color-mix(in srgb, var(--color-accent) 15%, transparent);
  color: var(--color-accent);
}

.type-creator {
  background: color-mix(in srgb, var(--color-text-tertiary) 10%, transparent);
  color: var(--color-text-secondary);
}

.course-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0 0 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.card-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.btn-action {
  width: 32px;
  height: 32px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
  transition: all 0.15s;
}

.btn-delete:hover {
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
  border-color: var(--color-error);
  color: var(--color-error);
}

.btn-unarchive:hover {
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
  border-color: var(--color-success);
  color: var(--color-success);
}

.btn-archive:hover {
  background: color-mix(in srgb, var(--color-warning) 10%, transparent);
  border-color: var(--color-warning);
  color: var(--color-warning);
}

</style>
