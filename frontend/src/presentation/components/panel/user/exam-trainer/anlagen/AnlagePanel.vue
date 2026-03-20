<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import type { LsxPanel } from '@/application/stores/modules/workspace/panel.types'
import type { Anlage } from '@/infrastructure/api/clients/panel/user/exams'

interface Props {
  window: LsxPanel
}

const props = defineProps<Props>()

const anlage = computed(() => (props.window.payload?.anlage as Anlage) || null)
const examId = computed(() => (props.window.payload?.examId as string) || '')

const sanitizedContent = computed(() => {
  if (!anlage.value) return ''
  const raw = anlage.value.raw_text || ''
  return DOMPurify.sanitize(raw, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'b', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption', 'colgroup', 'col',
      'ul', 'ol', 'li', 'dl', 'dt', 'dd',
      'div', 'span', 'section', 'article', 'header', 'footer',
      'blockquote', 'pre', 'code', 'hr', 'sup', 'sub', 'a', 'img'],
    ALLOWED_ATTR: ['class', 'style', 'colspan', 'rowspan', 'href', 'title', 'alt', 'src', 'width', 'height'],
  })
})

const popout = () => {
  if (!examId.value || !anlage.value) return
  const url = `/exam-trainer/anlage/${examId.value}/${anlage.value.number}`
  window.open(url, `anlage-${anlage.value.number}`, 'width=860,height=700,menubar=no,toolbar=no')
}
</script>

<template>
  <div v-if="anlage" class="anlage-content">
    <div v-if="examId" class="flex justify-end mb-2">
      <button
        class="text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text)] transition-colors flex items-center gap-1"
        @click="popout"
      >
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M7 1h4v4M11 1L6 6M5 1H2a1 1 0 00-1 1v8a1 1 0 001 1h8a1 1 0 001-1V7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ $t('panel.examTrainer.anlagen.popout') }}
      </button>
    </div>
    <div class="anlage-html-content" v-html="sanitizedContent" />
  </div>
</template>

<style scoped>
.anlage-content { padding: 16px; }

/* Style HTML content from Vision AI */
.anlage-html-content { font-size: 14px; line-height: 1.6; color: var(--color-text); }
.anlage-html-content :deep(table) { width: 100%; border-collapse: collapse; margin: 12px 0; }
.anlage-html-content :deep(th) { background: var(--color-surface-elevated, #252840); color: var(--color-text); padding: 8px 12px; text-align: left; font-size: 13px; font-weight: 600; border-bottom: 2px solid var(--color-border); }
.anlage-html-content :deep(td) { padding: 8px 12px; border-bottom: 1px solid var(--color-border); font-size: 13px; color: var(--color-text); }
.anlage-html-content :deep(p) { margin-bottom: 8px; }
.anlage-html-content :deep(h1), .anlage-html-content :deep(h2), .anlage-html-content :deep(h3) { margin: 16px 0 8px; font-weight: 600; color: var(--color-text); }
.anlage-html-content :deep(ul), .anlage-html-content :deep(ol) { padding-left: 20px; margin: 8px 0; }
.anlage-html-content :deep(li) { margin-bottom: 4px; }
.anlage-html-content :deep(hr) { border: none; border-top: 1px solid var(--color-border); margin: 16px 0; }
.anlage-html-content :deep(code) { font-family: 'Fira Code', monospace; font-size: 13px; background: rgba(96,165,250,0.1); padding: 2px 6px; border-radius: 4px; }
.anlage-html-content :deep(blockquote) { border-left: 3px solid var(--color-border); padding-left: 12px; margin: 8px 0; color: var(--color-text-secondary); }

/* Offer-specific styles (CSS classes from Vision AI) */
.anlage-html-content :deep(.anlage-offer) { background: #fafaf8; color: #1a1a1a; border-radius: 4px; padding: 24px 28px; font-family: 'Georgia', serif; box-shadow: 0 1px 3px rgba(0,0,0,0.12); border: 1px solid #c8c8c4; }
.anlage-html-content :deep(.anlage-offer table th) { background: #333; color: #fff; }
.anlage-html-content :deep(.anlage-offer table td) { border-bottom-color: #ddd; color: #1a1a1a; }

/* Diagram styles (CSS classes from Vision AI for network topologies, UML, etc.) */
.anlage-html-content :deep(.diagram-node) { border: 2px solid var(--color-border); padding: 8px 12px; border-radius: 6px; text-align: center; background: var(--color-surface-elevated, #252840); display: inline-block; margin: 4px; font-size: 13px; color: var(--color-text); }
.anlage-html-content :deep(.diagram-line) { border-top: 2px solid var(--color-border); width: 40px; display: inline-block; vertical-align: middle; margin: 0 4px; }
.anlage-html-content :deep(.diagram-group) { border: 1px dashed var(--color-border); padding: 12px; margin: 8px 0; border-radius: 4px; }
.anlage-html-content :deep(.diagram-label) { font-size: 0.85em; color: var(--color-text-secondary); }
.anlage-html-content :deep(.diagram-row) { display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap; margin: 8px 0; }
</style>
