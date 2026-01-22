<template>
  <div class="language-selector" :class="{ 'is-open': isOpen }">
    <!-- Current Language Button -->
    <button
      type="button"
      class="language-btn"
      @click="toggleDropdown"
      :title="t('i18n.select_language')"
    >
      <span class="flag">{{ currentFlag }}</span>
      <span v-if="showLabel" class="label">{{ currentLabel }}</span>
      <svg class="chevron" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>

    <!-- Dropdown -->
    <Transition name="dropdown">
      <div v-if="isOpen" class="dropdown" @click.stop>
        <!-- Primary Languages -->
        <div class="dropdown-section">
          <div class="section-label">{{ t('i18n.language') }}</div>
          <button
            v-for="lang in primaryLanguages"
            :key="lang.language_code"
            class="dropdown-item"
            :class="{ 'is-active': lang.language_code === currentLanguage }"
            @click="selectLanguage(lang.language_code)"
          >
            <span class="flag">{{ lang.flag_emoji }}</span>
            <span class="name">{{ lang.native_name }}</span>
            <span v-if="lang.completion_percent < 100" class="completion">
              {{ Math.round(lang.completion_percent) }}%
            </span>
            <svg v-if="lang.language_code === currentLanguage" class="check" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </button>
        </div>

        <!-- Other Languages (if any) -->
        <div v-if="otherLanguages.length > 0" class="dropdown-section">
          <div class="section-label">{{ t('i18n.other_languages') }}</div>
          <button
            v-for="lang in otherLanguages"
            :key="lang.language_code"
            class="dropdown-item"
            :class="{ 'is-active': lang.language_code === currentLanguage }"
            @click="selectLanguage(lang.language_code)"
          >
            <span class="flag">{{ lang.flag_emoji }}</span>
            <span class="name">{{ lang.native_name }}</span>
            <span class="completion">{{ Math.round(lang.completion_percent) }}%</span>
          </button>
        </div>

        <!-- Request Translation -->
        <div v-if="showRequestOption" class="dropdown-footer">
          <button class="request-btn" @click="openRequestModal">
            <svg viewBox="0 0 20 20" fill="currentColor" class="icon">
              <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
            </svg>
            {{ t('i18n.request_language') }}
          </button>
        </div>
      </div>
    </Transition>

    <!-- Click outside to close -->
    <div v-if="isOpen" class="backdrop" @click="isOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useTranslation } from '@/application/composables/useTranslation'
import type { LanguageProgress } from '@/infrastructure/api/i18n.api'

// Props
interface Props {
  showLabel?: boolean
  showRequestOption?: boolean
  variant?: 'default' | 'compact' | 'inline'
}

const props = withDefaults(defineProps<Props>(), {
  showLabel: false,
  showRequestOption: true,
  variant: 'default'
})

// Emits
const emit = defineEmits<{
  (e: 'change', lang: string): void
  (e: 'request'): void
}>()

// i18n
const { t } = useI18n()
const { currentLanguage, setLanguage, fetchLanguages, isLoading } = useTranslation()

// State
const isOpen = ref(false)
const languages = ref<LanguageProgress[]>([])

// Computed
const primaryLanguages = computed(() =>
  languages.value.filter(l => l.is_primary && l.active)
)

const otherLanguages = computed(() =>
  languages.value.filter(l => !l.is_primary && l.active && l.completion_percent > 50)
)

const currentLang = computed(() =>
  languages.value.find(l => l.language_code === currentLanguage.value)
)

const currentFlag = computed(() => currentLang.value?.flag_emoji || '🌐')
const currentLabel = computed(() => currentLang.value?.native_name || currentLanguage.value.toUpperCase())

// Methods
function toggleDropdown() {
  isOpen.value = !isOpen.value
}

async function selectLanguage(lang: string) {
  if (lang === currentLanguage.value) {
    isOpen.value = false
    return
  }

  await setLanguage(lang)
  emit('change', lang)
  isOpen.value = false
}

function openRequestModal() {
  emit('request')
  isOpen.value = false
}

// Keyboard navigation
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    isOpen.value = false
  }
}

// Lifecycle
onMounted(async () => {
  languages.value = await fetchLanguages()
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.language-selector {
  position: relative;
  display: inline-block;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-bg-secondary, #f3f4f6);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.15s ease;
  font-size: 0.875rem;
}

.language-btn:hover {
  background: var(--color-bg-tertiary, #e5e7eb);
  border-color: var(--color-border-hover, #d1d5db);
}

.is-open .language-btn {
  border-color: var(--color-primary, #3b82f6);
  box-shadow: 0 0 0 2px var(--color-primary-light, rgba(59, 130, 246, 0.2));
}

.flag {
  font-size: 1.25rem;
  line-height: 1;
}

.label {
  font-weight: 500;
  color: var(--color-text, #1f2937);
}

.chevron {
  width: 1rem;
  height: 1rem;
  color: var(--color-text-secondary, #6b7280);
  transition: transform 0.15s ease;
}

.is-open .chevron {
  transform: rotate(180deg);
}

/* Dropdown */
.dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  min-width: 200px;
  background: var(--color-bg, white);
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  z-index: 100;
}

.dropdown-section {
  padding: 0.5rem;
}

.dropdown-section + .dropdown-section {
  border-top: 1px solid var(--color-border, #e5e7eb);
}

.section-label {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-tertiary, #9ca3af);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.625rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  text-align: left;
  transition: background 0.1s ease;
}

.dropdown-item:hover {
  background: var(--color-bg-secondary, #f3f4f6);
}

.dropdown-item.is-active {
  background: var(--color-primary-light, #eff6ff);
}

.dropdown-item .flag {
  font-size: 1.25rem;
}

.dropdown-item .name {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text, #1f2937);
}

.dropdown-item .completion {
  font-size: 0.75rem;
  color: var(--color-text-secondary, #6b7280);
  background: var(--color-bg-tertiary, #e5e7eb);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.dropdown-item .check {
  width: 1rem;
  height: 1rem;
  color: var(--color-primary, #3b82f6);
}

/* Footer */
.dropdown-footer {
  padding: 0.5rem;
  border-top: 1px solid var(--color-border, #e5e7eb);
  background: var(--color-bg-secondary, #f9fafb);
}

.request-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: 1px dashed var(--color-border, #d1d5db);
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.15s ease;
}

.request-btn:hover {
  background: var(--color-bg, white);
  border-color: var(--color-primary, #3b82f6);
  color: var(--color-primary, #3b82f6);
}

.request-btn .icon {
  width: 1rem;
  height: 1rem;
}

/* Backdrop */
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 99;
}

/* Transitions */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-0.5rem);
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
  .language-btn {
    background: #374151;
    border-color: #4b5563;
  }

  .language-btn:hover {
    background: #4b5563;
  }

  .dropdown {
    background: #1f2937;
    border-color: #374151;
  }

  .dropdown-item:hover {
    background: #374151;
  }

  .dropdown-item.is-active {
    background: rgba(59, 130, 246, 0.2);
  }
}
</style>
