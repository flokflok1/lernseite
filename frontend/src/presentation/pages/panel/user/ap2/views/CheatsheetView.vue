<template>
  <div class="ap2-cs">
    <aside class="ap2-cs-side">
      <h3>{{ t('ap2Trainer.cheatsheet.selectTopic') }}</h3>
      <ul class="ap2-cs-topic-list">
        <li v-for="tp in topics" :key="tp.slug">
          <RouterLink
            :to="`/ap2-training/cheatsheet/${tp.slug}`"
            class="ap2-cs-topic"
            :class="{ 'ap2-cs-topic-active': tp.slug === topicSlug }"
          >
            <span class="ap2-cs-bereich">{{ tp.bereich }}</span>
            <span>{{ tp.name_de }}</span>
            <span v-if="cheatsheetWordCounts[tp.slug]" class="ap2-cs-wc">
              {{ t('ap2Trainer.cheatsheet.wordCount', { n: cheatsheetWordCounts[tp.slug] }) }}
            </span>
          </RouterLink>
        </li>
      </ul>
    </aside>

    <main class="ap2-cs-main">
      <div v-if="!topicSlug" class="ap2-cs-empty">
        <p>{{ t('ap2Trainer.cheatsheet.noTopic') }}</p>
        <p class="ap2-cs-tip">💡 {{ t('ap2Trainer.cheatsheet.tip') }}</p>
      </div>

      <template v-else>
        <header class="ap2-cs-header">
          <div>
            <h2>{{ currentTopic?.name_de }}</h2>
            <p class="ap2-cs-meta">
              <span v-if="data?.word_count">{{ t('ap2Trainer.cheatsheet.wordCount', { n: data.word_count }) }}</span>
              <span v-if="lastSavedDisplay" class="ap2-cs-saved">{{ lastSavedDisplay }}</span>
            </p>
          </div>
          <div class="ap2-cs-toolbar">
            <button
              v-for="m in modes"
              :key="m.key"
              class="ap2-cs-mode-btn"
              :class="{ 'ap2-cs-mode-active': mode === m.key }"
              @click="mode = m.key"
            >{{ t(m.labelKey) }}</button>
            <button class="ap2-btn ap2-btn-primary" :disabled="saving" @click="save">
              {{ saving ? t('ap2Trainer.cheatsheet.savingBtn') : t('ap2Trainer.cheatsheet.saveBtn') }}
            </button>
          </div>
        </header>

        <div v-if="loading" class="ap2-cs-loading">{{ t('ap2Trainer.cheatsheet.loading') }}</div>

        <div v-else class="ap2-cs-editor" :class="`ap2-mode-${mode}`">
          <textarea
            v-if="mode !== 'preview'"
            v-model="content"
            class="ap2-cs-textarea"
            :placeholder="t('ap2Trainer.cheatsheet.placeholder')"
          />
          <div
            v-if="mode !== 'edit'"
            class="ap2-cs-preview"
            v-html="renderedHtml"
          />
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import {
  listAp2Topics, listAp2Cheatsheets,
  getAp2Cheatsheet, saveAp2Cheatsheet,
  type Ap2Topic,
} from '@/infrastructure/api/clients/panel/user/exams'

const { t } = useI18n()

interface Props { topicSlug?: string }
const props = defineProps<Props>()

const topics = ref<Ap2Topic[]>([])
const cheatsheetWordCounts = ref<Record<string, number>>({})
const data = ref<{ markdown_content: string; word_count: number; updated_at: string | null } | null>(null)
const content = ref('')
const loading = ref(false)
const saving = ref(false)
const lastSavedAt = ref<Date | null>(null)
const mode = ref<'edit' | 'split' | 'preview'>('split')

const modes = [
  { key: 'edit' as const,    labelKey: 'ap2Trainer.cheatsheet.editToggle' },
  { key: 'split' as const,   labelKey: 'ap2Trainer.cheatsheet.splitToggle' },
  { key: 'preview' as const, labelKey: 'ap2Trainer.cheatsheet.previewToggle' },
]

const currentTopic = computed(() => topics.value.find((tp) => tp.slug === props.topicSlug))

const lastSavedDisplay = computed(() => {
  if (lastSavedAt.value) {
    return t('ap2Trainer.cheatsheet.savedAt', { time: lastSavedAt.value.toLocaleTimeString() })
  }
  if (data.value?.updated_at) {
    return t('ap2Trainer.cheatsheet.lastUpdated', {
      date: new Date(data.value.updated_at).toLocaleDateString()
    })
  }
  return ''
})

const renderedHtml = computed(() => {
  const md = content.value || ''
  let html = md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^([^<].+)$/gm, '<p>$1</p>')
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['h1', 'h2', 'h3', 'p', 'strong', 'em', 'code', 'ul', 'ol', 'li', 'br'],
    ALLOWED_ATTR: [],
  })
})

async function loadTopics() {
  const [tRes, cRes] = await Promise.all([listAp2Topics(), listAp2Cheatsheets()])
  topics.value = tRes.topics
  cheatsheetWordCounts.value = Object.fromEntries(
    cRes.cheatsheets.map((c) => [c.topic_slug, c.word_count])
  )
}

async function loadSheet() {
  if (!props.topicSlug) return
  loading.value = true
  try {
    const cs = await getAp2Cheatsheet(props.topicSlug)
    data.value = cs
    content.value = cs.markdown_content
    lastSavedAt.value = null
  } catch (e) {
    console.warn('[AP2] cheatsheet load failed:', e)
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!props.topicSlug) return
  saving.value = true
  try {
    const res = await saveAp2Cheatsheet(props.topicSlug, content.value)
    lastSavedAt.value = new Date()
    cheatsheetWordCounts.value[props.topicSlug] = res.word_count
    if (data.value) data.value.word_count = res.word_count
  } catch (e) {
    console.warn('[AP2] cheatsheet save failed:', e)
  } finally {
    saving.value = false
  }
}

watch(() => props.topicSlug, (s) => { if (s) loadSheet() })
onMounted(async () => {
  await loadTopics()
  if (props.topicSlug) await loadSheet()
})
</script>

<style scoped>
.ap2-cs { display: grid; grid-template-columns: 280px 1fr; gap: 16px; min-height: 600px; }
@media (max-width: 768px) { .ap2-cs { grid-template-columns: 1fr; } }
.ap2-cs-side { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 12px; padding: 12px; height: fit-content; max-height: 80vh; overflow-y: auto; }
.ap2-cs-side h3 { font-size: 12px; color: #94a3b8; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 0.5px; }
.ap2-cs-topic-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 4px; }
.ap2-cs-topic { display: grid; grid-template-columns: auto 1fr auto; gap: 6px; align-items: center; padding: 8px 10px; border-radius: 6px; color: #cbd5e1; text-decoration: none; font-size: 12px; }
.ap2-cs-topic:hover { background: rgba(255,255,255,0.04); color: #fff; }
.ap2-cs-topic-active { background: rgba(99,102,241,0.18); color: #a5b4fc; }
.ap2-cs-bereich { font-size: 9px; padding: 2px 5px; background: rgba(255,255,255,0.06); border-radius: 3px; font-weight: 700; }
.ap2-cs-wc { font-size: 9px; color: #64748b; }
.ap2-cs-main { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.ap2-cs-empty { text-align: center; padding: 64px 24px; background: var(--color-surface, #1e293b); border: 1px dashed var(--color-border, #334155); border-radius: 12px; }
.ap2-cs-empty p { color: #94a3b8; margin: 0 0 16px; }
.ap2-cs-tip { font-size: 12px; color: #818cf8 !important; }
.ap2-cs-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; padding: 12px 16px; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 12px; flex-wrap: wrap; }
.ap2-cs-header h2 { margin: 0 0 4px; color: #fff; font-size: 18px; }
.ap2-cs-meta { display: flex; gap: 12px; font-size: 11px; color: #94a3b8; margin: 0; }
.ap2-cs-saved { color: #4ade80; }
.ap2-cs-toolbar { display: flex; gap: 4px; flex-wrap: wrap; }
.ap2-cs-mode-btn { padding: 6px 10px; background: transparent; border: 1px solid var(--color-border, #334155); border-radius: 6px; color: #cbd5e1; cursor: pointer; font-size: 11px; font-weight: 600; }
.ap2-cs-mode-active { background: #4338ca !important; border-color: #4338ca !important; color: #fff !important; }
.ap2-btn { padding: 6px 14px; border-radius: 6px; border: 1px solid; cursor: pointer; font-size: 12px; font-weight: 600; }
.ap2-btn-primary { background: #4338ca; border-color: #4338ca; color: #fff; }
.ap2-btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.ap2-cs-loading { padding: 48px; text-align: center; color: #94a3b8; }
.ap2-cs-editor { display: grid; gap: 12px; min-height: 500px; }
.ap2-mode-edit { grid-template-columns: 1fr; }
.ap2-mode-preview { grid-template-columns: 1fr; }
.ap2-mode-split { grid-template-columns: 1fr 1fr; }
@media (max-width: 768px) { .ap2-mode-split { grid-template-columns: 1fr; } }
.ap2-cs-textarea { width: 100%; min-height: 500px; padding: 16px; background: rgba(0,0,0,0.2); border: 1px solid var(--color-border, #334155); border-radius: 8px; color: #fff; font-family: ui-monospace, monospace; font-size: 13px; line-height: 1.6; resize: vertical; }
.ap2-cs-textarea:focus { outline: none; border-color: #6366f1; }
.ap2-cs-preview { padding: 16px; background: rgba(255,255,255,0.02); border: 1px solid var(--color-border, #334155); border-radius: 8px; color: #e2e8f0; overflow-y: auto; max-height: 70vh; }
.ap2-cs-preview :deep(h1) { font-size: 20px; margin: 0 0 8px; color: #fff; border-bottom: 1px solid var(--color-border, #334155); padding-bottom: 4px; }
.ap2-cs-preview :deep(h2) { font-size: 16px; margin: 14px 0 6px; color: #a5b4fc; }
.ap2-cs-preview :deep(h3) { font-size: 14px; margin: 12px 0 4px; color: #cbd5e1; }
.ap2-cs-preview :deep(p)  { margin: 4px 0 8px; line-height: 1.5; font-size: 13px; }
.ap2-cs-preview :deep(ul) { margin: 4px 0 8px 20px; }
.ap2-cs-preview :deep(li) { margin-bottom: 2px; font-size: 13px; }
.ap2-cs-preview :deep(strong) { color: #fbbf24; }
.ap2-cs-preview :deep(em) { color: #818cf8; }
.ap2-cs-preview :deep(code) { background: rgba(0,0,0,0.4); padding: 1px 4px; border-radius: 3px; font-family: ui-monospace, monospace; font-size: 12px; color: #fcd34d; }
</style>
