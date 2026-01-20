<template>
  <div class="language-selector" :class="{ 'is-open': isOpen }">
    <!-- Current Language Button -->
    <button
      type="button"
      class="language-btn"
      @click="toggleDropdown"
      :title="t('i18n.select_language')"
    >
      <span class="flag" :data-lang="currentLanguage">{{ currentFlag }}</span>
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
            <span class="flag" :data-lang="lang.language_code">{{ lang.flag_emoji }}</span>
            <span class="name">{{ t(`languages.${lang.language_code}`) }}</span>
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
            <span class="flag" :data-lang="lang.language_code">{{ lang.flag_emoji }}</span>
            <span class="name">{{ t(`languages.${lang.language_code}`) }}</span>
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
import { useTranslation } from '@/features/useTranslation'
import type { LanguageProgress } from '@/infrastructure/api/clients/system'

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
const currentLabel = computed(() => {
  if (currentLang.value?.language_code) {
    return t(`languages.${currentLang.value.language_code}`)
  }
  return currentLanguage.value.toUpperCase()
})

// Methods
function toggleDropdown() {
  isOpen.value = !isOpen.value
  console.log(`[LanguageSelector] Dropdown ${isOpen.value ? 'opened' : 'closed'}`)

  // If emoji not supported and dropdown just opened, replace emoji in items
  if (isOpen.value && document.documentElement.getAttribute('data-emoji-support') === 'false') {
    setTimeout(() => {
      console.log('[LanguageSelector] Replacing emoji in dropdown items...')
      replaceEmojiWithLanguageCode()
    }, 10)
  }
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

// Check if emoji rendering works properly
function emojiSupported(): boolean {
  try {
    const canvas = document.createElement('canvas')
    canvas.width = 100
    canvas.height = 100
    const ctx = canvas.getContext('2d')
    if (!ctx) return true // Assume it works if we can't test

    // Test 1: Measure rendered width of flag emoji vs text
    // A properly rendered flag emoji should be ~30-35px wide (single glyph)
    // When degraded to text, it's usually wider or much narrower
    ctx.font = 'bold 30px "Apple Color Emoji", "Segoe UI Emoji", sans-serif'
    const emojiWidth = ctx.measureText('🇬🇧').width
    const textWidth = ctx.measureText('GB').width

    // If emoji width is similar to text width (within 5px), it likely degraded
    // A proper emoji should be narrower or have different metrics
    if (Math.abs(emojiWidth - textWidth) < 5) {
      console.log(`[LanguageSelector] Emoji width (${emojiWidth}) too close to text width (${textWidth}) - likely degraded`)
      return false
    }

    // Test 2: Visual pixel rendering check
    // Clear canvas and test visual rendering
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, 100, 100)
    ctx.fillStyle = '#000000'
    ctx.textBaseline = 'middle'
    ctx.fillText('🇩🇪', 10, 50)

    // Get pixel data and check for rendering
    const imageData = ctx.getImageData(0, 0, 100, 100).data
    let nonWhitePixels = 0
    let coloredPixels = 0  // Pixels with color (not just black/gray text)

    for (let i = 0; i < imageData.length; i += 4) {
      const r = imageData[i]
      const g = imageData[i + 1]
      const b = imageData[i + 2]

      // Count non-white pixels
      if (r < 240 || g < 240 || b < 240) {
        nonWhitePixels++

        // Count colored pixels (emoji are usually colorful, text is monochrome)
        // Check if this pixel has significant color variation (not just grayscale)
        const maxComponent = Math.max(r, g, b)
        const minComponent = Math.min(r, g, b)
        if (maxComponent - minComponent > 50) {
          coloredPixels++  // Color variation indicates emoji, not text
        }
      }
    }

    // If we have significant color variation, emoji rendered properly
    if (coloredPixels > 50) {
      console.log(`[LanguageSelector] Detected colored pixels (${coloredPixels}) - emoji likely rendered`)
      return true
    }

    // If we have very few non-white pixels, emoji didn't render at all
    if (nonWhitePixels < 50) {
      console.log(`[LanguageSelector] Very few pixels rendered (${nonWhitePixels}) - emoji not supported`)
      return false
    }

    // If we have non-white pixels but no color variation, it's likely degraded to text
    if (nonWhitePixels > 100 && coloredPixels < 50) {
      console.log(`[LanguageSelector] Pixels detected (${nonWhitePixels}) but no color variation (${coloredPixels}) - likely text degradation`)
      return false
    }

    console.log(`[LanguageSelector] Ambiguous detection: pixels=${nonWhitePixels}, colored=${coloredPixels} - assuming supported`)
    return true
  } catch (e) {
    console.log(`[LanguageSelector] Error during emoji detection: ${e}`)
    return true // Assume it works if detection fails
  }
}

// Replace emoji with language code for systems without emoji support
function replaceEmojiWithLanguageCode() {
  const hasEmojiSupport = document.documentElement.getAttribute('data-emoji-support')
  if (hasEmojiSupport !== 'false') return // Only replace if emoji not supported

  // Find all .flag elements with data-lang
  const flagElements = document.querySelectorAll('.flag[data-lang]')
  let replaced = 0

  flagElements.forEach((el) => {
    const langCode = el.getAttribute('data-lang')
    // Replace with uppercase language code (EN, DE, PL)
    if (langCode && langCode.length <= 3) {
      const upper = langCode.toUpperCase()
      el.textContent = upper
      replaced++
    }
  })

  if (replaced > 0) {
    console.log(`[LanguageSelector] Replaced ${replaced} emoji with language codes`)
  }
}

// Lifecycle
onMounted(async () => {
  // Check emoji support first
  const hasEmojiSupport = emojiSupported()
  console.log(`[LanguageSelector] Emoji support detected: ${hasEmojiSupport}`)

  if (!hasEmojiSupport) {
    document.documentElement.setAttribute('data-emoji-support', 'false')
    console.log('[LanguageSelector] Set data-emoji-support="false" on root')
  }

  // Load languages
  languages.value = await fetchLanguages()
  console.log(`[LanguageSelector] Loaded ${languages.value.length} languages`)

  // Replace emoji immediately if not supported
  if (!hasEmojiSupport) {
    // Wait a tick for DOM to be fully updated
    setTimeout(() => {
      replaceEmojiWithLanguageCode()
    }, 10)
  }

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
  text-align: center;
  /* Support emoji rendering across browsers */
  font-family: "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji", sans-serif;
  /* Optimize emoji rendering */
  font-feature-settings: "liga" 0;
  font-variant: normal;
}

/* Fallback for Windows 11 Chromium when regional indicators don't render */
@supports (font-variant: emoji) {
  .flag {
    font-variant: emoji;
  }
}

/* When emoji support is disabled, display language flag SVG instead of emoji */
:root[data-emoji-support="false"] .flag {
  width: 1.5rem;
  height: 1rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  position: relative;
  color: transparent;
  font-size: 0;
  line-height: 0;
  border: 1px solid var(--color-border, #e5e7eb);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* Germany flag: Black-Red-Gold (Schwarz-Rot-Gold) */
:root[data-emoji-support="false"] .flag[data-lang="de"] {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600"><rect width="900" height="200" fill="%23000000"/><rect y="200" width="900" height="200" fill="%23DD0000"/><rect y="400" width="900" height="200" fill="%23FFCE00"/></svg>');
}

/* USA flag: Stars and Stripes (Red-White-Blue) */
:root[data-emoji-support="false"] .flag[data-lang="en"] {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600"><rect width="900" height="600" fill="%23B22234"/><g fill="%23FFFFFF"><rect y="46" width="900" height="46"/><rect y="138" width="900" height="46"/><rect y="230" width="900" height="46"/><rect y="322" width="900" height="46"/><rect y="414" width="900" height="46"/><rect y="506" width="900" height="46"/></g><rect width="360" height="322" fill="%233C3B6B"/></svg>');
}

/* Poland flag: White-Red (Weiß-Rot) */
:root[data-emoji-support="false"] .flag[data-lang="pl"] {
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 600"><rect width="900" height="300" fill="%23FFFFFF"/><rect y="300" width="900" height="300" fill="%23DC143C"/></svg>');
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
    color: #f3f4f6;
  }

  .language-btn:hover {
    background: #4b5563;
  }

  .dropdown {
    background: #1f2937;
    border-color: #374151;
  }

  .dropdown-item {
    color: #f3f4f6;
  }

  .dropdown-item:hover {
    background: #374151;
  }

  .dropdown-item.is-active {
    background: rgba(59, 130, 246, 0.2);
  }

  .dropdown-item .name {
    color: #f3f4f6;
  }

  .dropdown-item .completion {
    background: #4b5563;
    color: #d1d5db;
  }

  .section-label {
    color: #9ca3af;
  }
}
</style>
