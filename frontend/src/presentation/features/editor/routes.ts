/**
 * Editor Routes - Course Authoring
 *
 * Feature-first routing for course editor
 * Separate from Panel (administration) - Editor is for authoring
 */

import type { RouteRecordRaw } from 'vue-router'

export const editorRoutes: RouteRecordRaw = {
  path: '/editor',
  meta: { requiresAuth: true, requiresCreatorOrTeacher: true },
  children: [
    {
      path: '',
      name: 'CourseEditor',
      component: () => import('@/presentation/features/editor/course-editor/CourseEditorMain.vue'),
    },
    {
      path: ':id',
      name: 'CourseEditorDetail',
      component: () => import('@/presentation/features/panel/pages/PanelCourseDetailPage.vue'),
      props: true,
    },
  ],
}

export default editorRoutes
