<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  getTelegramStatus,
  generateTelegramLinkCode,
  unlinkTelegram,
  type TelegramLinkCode,
  type TelegramStatus,
} from '@/infrastructure/api/clients/panel/user/exams/ap2-telegram.api'

const status = ref<TelegramStatus | null>(null)
const linkCode = ref<TelegramLinkCode | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const copied = ref(false)

async function refresh() {
  try {
    status.value = await getTelegramStatus()
  } catch (e) {
    error.value = 'Status konnte nicht geladen werden.'
  }
}

async function generateCode() {
  loading.value = true
  error.value = null
  try {
    linkCode.value = await generateTelegramLinkCode()
  } catch (e) {
    error.value = 'Code konnte nicht erzeugt werden.'
  } finally {
    loading.value = false
  }
}

async function unlink() {
  if (!window.confirm('Telegram-Verknüpfung wirklich aufheben?')) return
  loading.value = true
  try {
    await unlinkTelegram()
    linkCode.value = null
    await refresh()
  } catch (e) {
    error.value = 'Aufheben fehlgeschlagen.'
  } finally {
    loading.value = false
  }
}

async function copyCommand() {
  if (!linkCode.value) return
  try {
    await navigator.clipboard.writeText(`/start ${linkCode.value.code}`)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    /* clipboard nicht verfügbar */
  }
}

const botLink = (username: string) => `https://t.me/${username}`

onMounted(refresh)
</script>

<template>
  <section class="tg-card">
    <header class="tg-head">
      <span class="tg-icon">📱</span>
      <h3 class="tg-title">Telegram-Bot — tägliche Spot-Checks</h3>
    </header>

    <div v-if="!status" class="tg-loading">
      Lade Status…
    </div>

    <div v-else-if="status.linked" class="tg-state tg-linked">
      <p>
        ✅ <strong>Verbunden mit @{{ status.bot_username }}</strong><br />
        Du bekommst tägliche Pings für fällige Spot-Checks und Same-Day-Recalls.
      </p>
      <button type="button" class="tg-btn tg-btn-danger" :disabled="loading" @click="unlink">
        Verknüpfung aufheben
      </button>
    </div>

    <div v-else class="tg-state">
      <p class="tg-intro">
        Verbinde deinen Account mit dem Telegram-Bot. Du bekommst dann automatisch
        Erinnerungen für fällige Spot-Checks und kannst kurze Recalls direkt aus
        dem Chat beantworten — perfekt für unterwegs.
      </p>

      <button
        v-if="!linkCode"
        type="button"
        class="tg-btn tg-btn-primary"
        :disabled="loading"
        @click="generateCode"
      >
        🔗 Code erzeugen
      </button>

      <div v-else class="tg-code-block">
        <p class="tg-instruction">
          So verbindest du:
        </p>
        <ol class="tg-steps">
          <li>
            Öffne Telegram und such
            <a :href="botLink(linkCode.bot_username)" target="_blank" rel="noopener">
              @{{ linkCode.bot_username }}
            </a>
            (oder klick den Link).
          </li>
          <li>
            Schicke dem Bot diesen Befehl:
            <div class="tg-code-row">
              <code class="tg-code">/start {{ linkCode.code }}</code>
              <button type="button" class="tg-btn-copy" @click="copyCommand">
                {{ copied ? '✓ kopiert' : '📋 kopieren' }}
              </button>
            </div>
          </li>
          <li>Der Bot bestätigt — fertig.</li>
        </ol>
        <p class="tg-expiry">
          Code ist gültig bis {{ new Date(linkCode.expires_at).toLocaleString('de-DE') }}.
        </p>
        <button type="button" class="tg-btn-secondary" @click="generateCode" :disabled="loading">
          Neuen Code erzeugen
        </button>
      </div>
    </div>

    <p v-if="error" class="tg-error">{{ error }}</p>
  </section>
</template>

<style scoped>
.tg-card {
  background: var(--color-surface, #1e293b);
  border: 1px solid var(--color-border, #334155);
  border-radius: 10px;
  padding: 18px;
}

.tg-head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.8rem;
}

.tg-icon { font-size: 1.4rem; }
.tg-title { margin: 0; font-size: 1.05rem; color: #e2e8f0; }

.tg-loading,
.tg-state {
  color: #cbd5e1;
  font-size: 0.92rem;
  line-height: 1.5;
}

.tg-state.tg-linked {
  border-left: 3px solid #16a34a;
  padding-left: 0.8rem;
}

.tg-intro {
  margin: 0 0 0.8rem 0;
}

.tg-btn {
  padding: 0.5rem 0.9rem;
  border: 0;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}

.tg-btn-primary {
  background: #2563eb;
  color: #fff;
}
.tg-btn-primary:hover:not(:disabled) {
  background: #1e40af;
}

.tg-btn-danger {
  background: #b91c1c;
  color: #fff;
}
.tg-btn-danger:hover:not(:disabled) {
  background: #7f1d1d;
}

.tg-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tg-code-block {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 0.9rem 1rem;
  margin-top: 0.5rem;
}

.tg-instruction {
  font-weight: 600;
  margin: 0 0 0.4rem 0;
  color: #f1f5f9;
}

.tg-steps {
  margin: 0;
  padding-left: 1.2rem;
}

.tg-steps li {
  margin-bottom: 0.5rem;
}

.tg-steps a {
  color: #60a5fa;
  text-decoration: none;
}
.tg-steps a:hover { text-decoration: underline; }

.tg-code-row {
  display: flex;
  gap: 0.4rem;
  align-items: center;
  margin-top: 0.3rem;
}

.tg-code {
  flex: 1;
  background: #0f172a;
  border: 1px solid #334155;
  padding: 0.4rem 0.7rem;
  border-radius: 4px;
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  color: #fbbf24;
  font-size: 0.95rem;
  letter-spacing: 0.5px;
}

.tg-btn-copy {
  padding: 0.4rem 0.7rem;
  background: #334155;
  color: #f1f5f9;
  border: 0;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}
.tg-btn-copy:hover { background: #475569; }

.tg-expiry {
  margin: 0.6rem 0;
  font-size: 0.78rem;
  color: #94a3b8;
}

.tg-btn-secondary {
  padding: 0.35rem 0.7rem;
  background: transparent;
  color: #94a3b8;
  border: 1px solid #475569;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}
.tg-btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.04);
  color: #cbd5e1;
}

.tg-error {
  margin-top: 0.6rem;
  padding: 0.5rem 0.7rem;
  background: #7f1d1d33;
  border-left: 3px solid #dc2626;
  color: #fecaca;
  font-size: 0.85rem;
  border-radius: 3px;
}
</style>
