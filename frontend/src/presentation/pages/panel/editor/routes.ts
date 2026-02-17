/**
 * Editor Routes - Course Authoring
 *
 * Feature-first routing for course editor
 * Separate from Panel (administration) - Editor is for authoring
 */

import type { RouteRecordRaw } from 'vue-router'
import { h } from 'vue'
import { RouterView } from 'vue-router'

export const editorRoutes: RouteRecordRaw = {
  path: '/editor',
  component: { render: () => h(RouterView) },
  meta: { requiresAuth: true, requiresCreatorOrTeacher: true },
  children: [
    {
      path: '',
      name: 'CourseEditor',
      component: () => import('@/presentation/pages/panel/editor/CourseEditorMain.vue'),
    },
    {
      path: ':id',
      name: 'CourseEditorDetail',
      component: () => import('@/presentation/pages/panel/admin/PanelCourseDetailPage.vue'),
      props: true,
    },
  ],
}

export default editorRoutes
