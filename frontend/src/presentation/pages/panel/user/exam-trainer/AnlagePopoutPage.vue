<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import DOMPurify from 'dompurify'
import { trainerGetAnlagen } from '@/infrastructure/api/clients/panel/user/exams'
import type { Anlage } from '@/infrastructure/api/clients/panel/user/exams'

const props = defineProps<{
  examId: string
  anlageNumber: string
}>()

const { t } = useI18n()
const anlage = ref<Anlage | null>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const anlagen = await trainerGetAnlagen(props.examId)
    anlage.value = anlagen.find(a => a.number === parseInt(props.anlageNumber)) || null
    if (!anlage.value) error.value = `Anlage ${props.anlageNumber} not found`
  } catch (e) {
    error.value = String(e)
  } finally {
    loading.value = false
  }
  if (anlage.value) {
    document.title = `${t('panel.examTrainer.anlagen.anlageNr', { number: anlage.value.number })} — ${anlage.value.title}`
  }
})

const sanitizedContent = computed(() => {
  if (!anlage.value) return ''
  return DOMPurify.sanitize(anlage.value.raw_text || '', {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'b', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption',
      'ul', 'ol', 'li', 'div', 'span', 'section',
      'blockquote', 'pre', 'code', 'hr', 'sup', 'sub', 'a'],
    ALLOWED_ATTR: ['class', 'colspan', 'rowspan', 'href', 'title'],
  })
})
</script>

<template>
  <div class="popout-page">
    <div v-if="loading" class="popout-loading">Loading...</div>
    <div v-else-if="error" class="popout-error">{{ error }}</div>
    <div v-else-if="anlage" class="popout-content" v-html="sanitizedContent" />
  </div>
</template>

<style scoped>
.popout-page { min-height: 100vh; background: #f5f5f3; padding: 32px; }
.popout-loading, .popout-error { text-align: center; padding: 48px; font-size: 16px; color: #666; }
.popout-content { max-width: 800px; margin: 0 auto; font-size: 15px; line-height: 1.65; color: #1a1a1a; }
.popout-content :deep(table) { width: 100%; border-collapse: collapse; margin: 16px 0; }
.popout-content :deep(th) { background: #f0f0f0; padding: 10px 14px; text-align: left; font-size: 14px; border-bottom: 2px solid #ddd; }
.popout-content :deep(td) { padding: 10px 14px; border-bottom: 1px solid #eee; font-size: 14px; }
.popout-content :deep(p) { margin-bottom: 10px; }
.popout-content :deep(.anlage-offer) { background: #fafaf8; border-radius: 4px; padding: 32px 40px; font-family: 'Georgia', serif; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #d0d0d0; }
.popout-content :deep(.anlage-offer table th) { background: #333; color: #fff; }
</style>
