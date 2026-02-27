/**
 * Editor Routes - Redirects to Panel Admin Editor
 *
 * The course editor lives within PanelLayout at /panel/admin/editor.
 * These routes provide backward-compatible redirects from the old /editor path.
 */

import type { RouteRecordRaw } from 'vue-router'

export const editorRoutes: RouteRecordRaw = {
  path: '/editor',
  redirect: '/panel/admin/editor',
  children: [
    {
      path: ':id',
      redirect: (to) => `/panel/admin/editor/${to.params.id}`,
    },
  ],
}

export default editorRoutes
