import DOMPurify from 'dompurify'
import { marked } from 'marked'

const ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'p', 'br', 'ul', 'ol', 'li', 'code', 'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'a', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
const ALLOWED_ATTR = ['href', 'title']

/** Check if text contains markdown syntax */
function isMarkdown(text: string): boolean {
  return text.includes('# ') || text.includes('**') || text.includes('- ')
}

/** Parse markdown to HTML if needed, sanitize the result */
export function renderMarkdown(text: string): string {
  if (!text) return ''
  if (isMarkdown(text)) {
    return DOMPurify.sanitize(marked.parse(text) as string, { ALLOWED_TAGS, ALLOWED_ATTR })
  }
  return DOMPurify.sanitize(text, { ALLOWED_TAGS, ALLOWED_ATTR })
}

/** Sanitize HTML without markdown parsing */
export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, { ALLOWED_TAGS, ALLOWED_ATTR })
}
