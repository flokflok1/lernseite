/**
 * Editor Routes - Course Authoring
 *
 * Feature-first routing for course editor.
 * Uses EditorLayout with DesktopLayer for windowed editing interface.
 */

import type { RouteRecordRaw } from 'vue-router'

export const editorRoutes: RouteRecordRaw = {
  path: '/editor',
  component: () => import('@/presentation/layouts/EditorLayout.vue'),
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
