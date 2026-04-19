<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  getPreferences,
  updatePreferences,
  type UserPreferences,
  type PreferencesResponse,
} from '@/infrastructure/api/clients/panel/user/exams/ap2-modules.api'

const { t } = useI18n()

const loading = ref(true)
const saving = ref(false)
const error = ref<string | null>(null)
const saveOk = ref(false)

const prefs = ref<UserPreferences | null>(null)
const meta = ref<PreferencesResponse['meta'] | null>(null)

const targetHint = computed(() => {
  if (!prefs.value) return ''
  return t('ap2Trainer.prefs.targets.rangeHint', {
    base: prefs.value.base_target,
    max: prefs.value.max_target,
  })
})

const targetsSectionHint = computed(() => {
  if (!prefs.value) return ''
  return t('ap2Trainer.prefs.targets.hint', { max: prefs.value.max_target })
})

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await getPreferences()
    prefs.value = res.preferences
    meta.value = res.meta
  } catch (e: any) {
    error.value = e?.response?.data?.error || t('ap2Trainer.prefs.loadError')
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!prefs.value) return
  saving.value = true
  saveOk.value = false
  error.value = null
  try {
    const res = await updatePreferences({
      base_target: prefs.value.base_target,
      max_target: prefs.value.max_target,
      recovery_mode: prefs.value.recovery_mode,
      stuetzrad_default: prefs.value.stuetzrad_default,
      mastery_strictness: prefs.value.mastery_strictness,
    })
    prefs.value = res.preferences
    meta.value = res.meta
    saveOk.value = true
    setTimeout(() => { saveOk.value = false }, 2500)
  } catch (e: any) {
    error.value = e?.response?.data?.error || t('ap2Trainer.prefs.saveError')
  } finally {
    saving.value = false
  }
}

function onBaseChange(v: number) {
  if (!prefs.value) return
  prefs.value.base_target = v
  if (prefs.value.max_target < v) prefs.value.max_target = v
}

function onMaxChange(v: number) {
  if (!prefs.value) return
  prefs.value.max_target = Math.max(v, prefs.value.base_target)
}

onMounted(load)
</script>

<template>
  <div class="prefs">
    <header class="prefs-head">
      <h2>{{ $t('ap2Trainer.prefs.title') }}</h2>
      <p class="prefs-sub">{{ $t('ap2Trainer.prefs.subtitle') }}</p>
    </header>

    <div v-if="loading" class="prefs-loading">
      {{ $t('ap2Trainer.prefs.loading') }}
    </div>
    <div v-else-if="error" class="prefs-error">⚠️ {{ error }}</div>

    <form v-else-if="prefs && meta" class="prefs-form" @submit.prevent="save">
      <!-- TARGETS -->
      <section class="prefs-section">
        <h3>{{ $t('ap2Trainer.prefs.targets.title') }}</h3>
        <p class="section-hint">{{ targetsSectionHint }}</p>

        <div class="form-row">
          <label class="form-label">
            {{ $t('ap2Trainer.prefs.targets.base') }}
            <span class="form-value">{{ prefs.base_target }}×</span>
          </label>
          <input
            type="range"
            :min="meta.abs_min_target"
            :max="Math.min(10, meta.abs_max_target)"
            :value="prefs.base_target"
            @input="onBaseChange(Number(($event.target as HTMLInputElement).value))"
            class="form-range"
          />
          <div class="range-ticks">
            <span>1</span><span>3</span><span>5</span><span>7</span><span>10</span>
          </div>
        </div>

        <div class="form-row">
          <label class="form-label">
            {{ $t('ap2Trainer.prefs.targets.max') }}
            <span class="form-value">{{ prefs.max_target }}×</span>
          </label>
          <input
            type="range"
            :min="prefs.base_target"
            :max="meta.abs_max_target"
            :value="prefs.max_target"
            @input="onMaxChange(Number(($event.target as HTMLInputElement).value))"
            class="form-range"
          />
          <div class="range-ticks">
            <span>{{ prefs.base_target }}</span>
            <span>10</span>
            <span>15</span>
            <span>{{ meta.abs_max_target }}</span>
          </div>
        </div>

        <p class="form-hint-small">{{ targetHint }}</p>
      </section>

      <!-- RECOVERY MODE -->
      <section class="prefs-section">
        <h3>{{ $t('ap2Trainer.prefs.recovery.title') }}</h3>
        <p class="section-hint">{{ $t('ap2Trainer.prefs.recovery.hint') }}</p>
        <div class="radio-group">
          <label
            v-for="m in meta.recovery_modes"
            :key="m"
            class="radio-option"
            :class="{ 'radio-option--selected': prefs.recovery_mode === m }"
          >
            <input type="radio" :value="m" v-model="prefs.recovery_mode" />
            <span>{{ $t(`ap2Trainer.prefs.recovery.${m}`) }}</span>
          </label>
        </div>
      </section>

      <!-- STUETZRAD DEFAULT -->
      <section class="prefs-section">
        <h3>{{ $t('ap2Trainer.prefs.stuetzrad.title') }}</h3>
        <p class="section-hint">{{ $t('ap2Trainer.prefs.stuetzrad.hint') }}</p>
        <div class="radio-group">
          <label
            v-for="s in meta.stuetzrad_defaults"
            :key="s"
            class="radio-option"
            :class="{ 'radio-option--selected': prefs.stuetzrad_default === s }"
          >
            <input type="radio" :value="s" v-model="prefs.stuetzrad_default" />
            <span>{{ $t(`ap2Trainer.prefs.stuetzrad.${s}`) }}</span>
          </label>
        </div>
      </section>

      <!-- MASTERY STRICTNESS -->
      <section class="prefs-section">
        <h3>{{ $t('ap2Trainer.prefs.mastery.title') }}</h3>
        <p class="section-hint">{{ $t('ap2Trainer.prefs.mastery.hint') }}</p>
        <div class="radio-group">
          <label
            v-for="m in meta.mastery_strictness_levels"
            :key="m"
            class="radio-option"
            :class="{ 'radio-option--selected': prefs.mastery_strictness === m }"
          >
            <input type="radio" :value="m" v-model="prefs.mastery_strictness" />
            <span>{{ $t(`ap2Trainer.prefs.mastery.${m}`) }}</span>
          </label>
        </div>
      </section>

      <div class="prefs-actions">
        <button class="btn btn-primary" type="submit" :disabled="saving">
          {{ saving
            ? $t('ap2Trainer.prefs.savingBtn')
            : $t('ap2Trainer.prefs.saveBtn') }}
        </button>
        <span v-if="saveOk" class="save-ok">
          {{ $t('ap2Trainer.prefs.savedOk') }}
        </span>
      </div>
    </form>
  </div>
</template>

<style scoped>
.prefs { max-width: 720px; margin: 0 auto; padding: 1rem; }

.prefs-head h2 { margin: 0 0 0.3rem 0; color: #f1f5f9; }
.prefs-sub {
  margin: 0 0 1.5rem 0;
  color: #94a3b8;
  font-size: 0.9rem;
  line-height: 1.5;
}

.prefs-loading, .prefs-error {
  padding: 1rem; border-radius: 8px;
  background: var(--color-surface, #1e293b);
}
.prefs-error { background: #7f1d1d33; border-left: 3px solid #dc2626; color: #fecaca; }

.prefs-section {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 1.2rem;
  margin-bottom: 1rem;
}
.prefs-section h3 { margin: 0 0 0.4rem 0; color: #f1f5f9; font-size: 1rem; }

.section-hint {
  margin: 0 0 1rem 0;
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.5;
}

.form-row { margin-bottom: 1rem; }
.form-label {
  display: flex;
  justify-content: space-between;
  color: #cbd5e1;
  font-size: 0.9rem;
  margin-bottom: 0.4rem;
  font-weight: 500;
}
.form-value { color: #fbbf24; font-weight: 700; }

.form-range { width: 100%; accent-color: #3b82f6; }

.range-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 0.2rem;
}

.form-hint-small {
  font-size: 0.8rem;
  color: #94a3b8;
  margin: 0.3rem 0 0 0;
}

.radio-group { display: flex; flex-direction: column; gap: 0.4rem; }

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.8rem;
  background: rgba(0,0,0,0.15);
  border: 1px solid #334155;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #cbd5e1;
  transition: all 0.15s;
}
.radio-option:hover { border-color: #475569; background: rgba(0,0,0,0.25); }
.radio-option--selected {
  border-color: #3b82f6;
  background: rgba(59,130,246,0.15);
  color: #e0e7ff;
}
.radio-option input[type=radio] { accent-color: #3b82f6; }

.prefs-actions {
  display: flex; gap: 0.8rem; align-items: center;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.6rem 1.2rem; border: 0; border-radius: 6px;
  font-weight: 600; font-size: 0.9rem; cursor: pointer;
}
.btn-primary { background: #2563eb; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #1e40af; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.save-ok {
  color: #86efac;
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
