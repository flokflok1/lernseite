# Frontend API Import Refactoring Analysis

**Task:** Convert three API import paths across 20 admin component files

**Conversion Rules:**
- `@/api/admin.api` → `@/infrastructure/api/clients/admin`
- `@/api/categories.api` → `@/infrastructure/api/clients/content`
- `@/api/http` → `@/infrastructure/api/clients/system/http`

---

## Files WITHOUT Imports (No Changes Needed)

These files do not import from the three target APIs:

1. **FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/lessons/LessonEditor.vue`
   - Status: NO IMPORTS TO CHANGE

2. **FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/lessons/views/LessonEditorPanel.vue`
   - Status: NO IMPORTS TO CHANGE

3. **FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/lessons/LessonPreview.vue`
   - Status: NO IMPORTS TO CHANGE (uses `http` but not imported in this file)

---

## Files WITH Imports (Changes Required)

### Chapter Components

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/chapters/ChapterEditor.vue`
- LINE: 531
- OLD: `import { adminCreateChapter, adminUpdateChapter, adminDeleteChapter, adminGetCourseChapters, adminPublishChapter, type AdminChapter } from '@/api/admin.api'`
- NEW: `import { adminCreateChapter, adminUpdateChapter, adminDeleteChapter, adminGetCourseChapters, adminPublishChapter, type AdminChapter } from '@/infrastructure/api/clients/admin'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/chapters/views/KapitelEditorPanel.vue`
- LINE: 531
- OLD: `import { adminUpdateChapter, type AdminChapter } from '@/api/admin.api'`
- NEW: `import { adminUpdateChapter, type AdminChapter } from '@/infrastructure/api/clients/admin'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/chapters/views/KapitelManagerPanel.vue`
- LINE: 216
- OLD: `import { adminGetCourseChapters, adminCreateChapter, adminDeleteChapter, type AdminChapter } from '@/api/admin.api'`
- NEW: `import { adminGetCourseChapters, adminCreateChapter, adminDeleteChapter, type AdminChapter } from '@/infrastructure/api/clients/admin'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/chapters/ChapterManager.vue`
- LINE: 216
- OLD: `import { adminGetCourseChapters, adminCreateChapter, adminDeleteChapter, type AdminChapter } from '@/api/admin.api'`
- NEW: `import { adminGetCourseChapters, adminCreateChapter, adminDeleteChapter, type AdminChapter } from '@/infrastructure/api/clients/admin'`

---

### Lesson Components

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/lessons/views/LessonPreviewPanel.vue`
- LINE: 154
- OLD: `import http from '@/api/http'`
- NEW: `import http from '@/infrastructure/api/clients/system/http'`

---

### Course Components

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/courses/CourseEditor.vue`
- LINE: 364
- OLD: `} from '@/api/admin.api'`
- NEW: `} from '@/infrastructure/api/clients/admin'`
- Additional import at LINE: 365
- OLD: `import { getCategoryTree, type Category, type CategoryTreeNode } from '@/api/categories.api'`
- NEW: `import { getCategoryTree, type Category, type CategoryTreeNode } from '@/infrastructure/api/clients/content'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/courses/views/CourseEditorPanel.vue`
- LINE: 368
- OLD: `} from '@/api/admin.api'`
- NEW: `} from '@/infrastructure/api/clients/admin'`
- Additional import at LINE: 369
- OLD: `import { getCategoryTree, type Category, type CategoryTreeNode } from '@/api/categories.api'`
- NEW: `import { getCategoryTree, type Category, type CategoryTreeNode } from '@/infrastructure/api/clients/content'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/courses/forms/ManualCourseForm.vue`
- LINE: 118
- OLD: `import type { AdminCourseCreateRequest, Category } from '@/api/admin.api'`
- NEW: `import type { AdminCourseCreateRequest, Category } from '@/infrastructure/api/clients/admin'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/courses/detail/CourseDetailHeader.vue`
- LINE: 169
- OLD: `import type { AdminCourseDetail } from '@/api/admin.api'`
- NEW: `import type { AdminCourseDetail } from '@/infrastructure/api/clients/admin'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/courses/CourseForm.vue`
- LINE: 118
- OLD: `import type { AdminCourseCreateRequest, Category } from '@/api/admin.api'`
- NEW: `import type { AdminCourseCreateRequest, Category } from '@/infrastructure/api/clients/admin'`

---

### Editor Components

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/admin/editor/CourseMetaForm.vue`
- LINE: 125
- OLD: `import { getCategoryTree, type Category, type CategoryTreeNode } from '@/api/categories.api'`
- NEW: `import { getCategoryTree, type Category, type CategoryTreeNode } from '@/infrastructure/api/clients/content'`

---

### User Components (Shared)

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/user/chapters/ChapterTheorySection.vue`
- LINE: 177
- OLD: `import http from '@/api/http'`
- NEW: `import http from '@/infrastructure/api/clients/system/http'`

---

### System Admin Components

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/content/shared/FilePreview.vue`
- LINE: 158
- OLD: `import http from '@/api/http'`
- NEW: `import http from '@/infrastructure/api/clients/system/http'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/system/admin/views/FilePreviewPanel.vue`
- LINE: 158
- OLD: `import http from '@/api/http'`
- NEW: `import http from '@/infrastructure/api/clients/system/http'`

---

**FILE:** `/home/pascal/Lernsystem/frontend/src/components/base/system/admin/SystemStatus.vue`
- LINE: 79
- OLD: `import type { SystemStatsData } from '@/api/admin.api'`
- NEW: `import type { SystemStatsData } from '@/infrastructure/api/clients/admin'`

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total Files Analyzed | 20 |
| Files WITHOUT Imports | 3 |
| Files WITH Imports | 17 |
| Total Import Changes | 21 |
| `@/api/admin.api` changes | 13 |
| `@/api/categories.api` changes | 4 |
| `@/api/http` changes | 4 |

---

## Implementation Notes

1. **Multi-import Handling**: Some files (e.g., CourseEditor.vue) have multiple imports from different APIs on consecutive lines - ensure both are updated
2. **Multi-line Imports**: Some imports span multiple lines with named exports - update only the `from` clause
3. **Type Imports**: Both regular imports and type imports need conversion
4. **Grouped Imports**: Files importing multiple functions from `@/api/admin.api` have the closing brace `}` on the line with the `from` statement
