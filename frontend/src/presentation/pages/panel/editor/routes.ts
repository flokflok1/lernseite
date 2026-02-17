/**
 * Editor Routes - Redirects to Panel Editor
 *
 * The course editor lives within PanelLayout at /panel/editor.
 * These routes provide backward-compatible redirects from the old /editor path.
 */

import type { RouteRecordRaw } from 'vue-router'

export const editorRoutes: RouteRecordRaw = {
  path: '/editor',
  redirect: '/panel/editor',
  children: [
    {
      path: ':id',
      redirect: (to) => `/panel/editor/${to.params.id}`,
    },
  ],
}

export default editorRoutes
