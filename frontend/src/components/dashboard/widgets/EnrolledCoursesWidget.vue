<template>
  <Card title="Meine Kurse" class="xl:col-span-2">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-6 text-gray-500">
      Kurse werden geladen...
    </div>

    <!-- Empty State -->
    <div v-else-if="courses.length === 0" class="text-center py-8 text-gray-500">
      <p class="text-lg">Du bist noch in keinen Kursen eingeschrieben</p>
      <router-link to="/courses" class="text-primary-600 hover:text-primary-700 text-sm font-medium mt-2 inline-block">
        Kurse durchsuchen →
      </router-link>
    </div>

    <!-- Courses List -->
    <div v-else class="space-y-4">
      <div
        v-for="course in displayedCourses"
        :key="course.enrollment_id"
        class="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900 mb-1">{{ course.title }}</h3>
            <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ course.description }}</p>

            <!-- Progress Bar -->
            <div class="mb-2">
              <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                <span>Fortschritt</span>
                <span>{{ Math.round(course.progress) }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-primary-600 h-2 rounded-full transition-all"
                  :style="{ width: `${course.progress}%` }"
                ></div>
              </div>
            </div>

            <div class="flex items-center gap-4 text-xs text-gray-500">
              <span v-if="course.lessons_completed && course.total_lessons">
                {{ course.lessons_completed }} / {{ course.total_lessons }} Lektionen
              </span>
              <span v-if="course.is_completed" class="text-green-600 font-medium">
                ✓ Abgeschlossen
              </span>
            </div>
          </div>

          <div class="ml-4">
            <Button
              variant="primary"
              size="sm"
              @click="continueCourse(course.course_id)"
            >
              Weiterlernen
            </Button>
          </div>
        </div>
      </div>

      <!-- View All Link -->
      <div v-if="courses.length > maxDisplayed" class="text-center pt-2">
        <router-link to="/courses" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
          Alle Kurse anzeigen ({{ courses.length }}) →
        </router-link>
      </div>
    </div>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import type { BaseWidgetProps } from '@/types/widgets'

// ============================================================================
// Props
// ============================================================================

interface Props extends BaseWidgetProps {
  dataContext: any
}

const props = defineProps<Props>()

// ============================================================================
// Router
// ============================================================================

const router = useRouter()

// ============================================================================
// Computed
// ============================================================================

const courses = computed(() => props.dataContext.enrolledCourses || [])
const loading = computed(() => props.dataContext.loading || false)
const maxDisplayed = 5

const displayedCourses = computed(() => {
  return courses.value.slice(0, maxDisplayed)
})

// ============================================================================
// Methods
// ============================================================================

const continueCourse = (courseId: string) => {
  router.push(`/courses/${courseId}`)
}
</script>
