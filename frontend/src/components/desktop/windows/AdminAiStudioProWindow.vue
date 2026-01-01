<!--
  Admin AI Studio Pro - Vollständiges KI-Authoring-System

  9 Tabs:
  - 📚 Kurs-Builder: KI-gestützte Kurserstellung
  - 🤖 Tutor: Kapitel/Lektions-Theorie & Erklärungen
  - 🧩 Lernmethoden: 19 Content-LMs (LM00-LM25) Verwaltung
  - 📝 Prüfungen: KI-Prüfungsgenerierung
  - 🎛️ Features: System-Features aktivieren (Tutor, IT-Sandbox, Kollaboration)
  - 📄 Prompts: System-Prompts verwalten
  - 📊 Analytics: Kurs-Statistiken & KI-Nutzung
  - ⚙️ Einstellungen: Kurs-spezifische KI-Modelle & Profile
  - 🌐 Global: Provider, Profile, API-Keys

  Features:
  - Neuer Kurs erstellen (mit KI-Unterstützung)
  - Datei-Upload für Kursmaterialien
  - Vollständiger KI-Workflow

  Phase: KI-Studio Pro Rebuild
  Updated: 2025-12-30
-->

<template>
  <div class="ai-studio-pro h-full flex flex-col bg-[var(--color-bg)]">
    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] bg-gradient-to-r from-violet-600 to-purple-600">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <div>
          <h2 class="text-lg font-bold text-white">KI-Authoring-Studio Pro</h2>
          <p class="text-xs text-white/70">{{ selectedCourse?.title || 'Kurs auswählen' }}</p>
        </div>
      </div>

      <!-- Course Selector & Actions -->
      <div class="flex items-center gap-3">
        <!-- Custom Course Dropdown -->
        <div class="relative" ref="courseDropdownRef">
          <button
            @click="courseDropdownOpen = !courseDropdownOpen"
            class="flex items-center gap-2 px-3 py-2 text-sm bg-white/10 border border-white/20 rounded-lg text-white hover:bg-white/20 transition-colors min-w-[280px]"
          >
            <span class="flex-1 text-left truncate">
              {{ selectedCourse?.title || 'Kurs auswählen...' }}
            </span>
            <svg
              class="w-4 h-4 transition-transform"
              :class="{ 'rotate-180': courseDropdownOpen }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          <!-- Dropdown Menu (right-aligned to prevent overflow) -->
          <div
            v-if="courseDropdownOpen"
            class="absolute top-full right-0 mt-1 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg shadow-xl z-50 overflow-hidden min-w-[320px]"
          >
            <!-- Search Input -->
            <div class="p-2 border-b border-[var(--color-border)]">
              <div class="relative">
                <svg class="absolute left-2.5 top-2.5 w-4 h-4 text-[var(--color-text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  v-model="courseSearchQuery"
                  type="text"
                  placeholder="Kurs suchen..."
                  class="w-full pl-8 pr-3 py-2 text-sm bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)]"
                  @click.stop
                />
              </div>
            </div>

            <!-- Category Filter (collapsible) -->
            <div v-if="allCategories.length > 0" class="border-b border-[var(--color-border)]">
              <button
                @click.stop="categoryPopupOpen = !categoryPopupOpen"
                class="w-full px-3 py-2 text-xs font-medium text-left flex items-center justify-between hover:bg-[var(--color-surface-secondary)] transition-colors"
                :class="selectedCategoryFilter ? 'text-[var(--color-primary)] bg-[var(--color-primary-subtle)]' : 'text-[var(--color-text-secondary)]'"
              >
                <span class="flex items-center gap-2">
                  <span>📁</span>
                  <span>{{ selectedCategoryFilter === '__uncategorized__' ? 'Ohne Kategorie' : (selectedCategoryFilter || 'Alle Kategorien') }}</span>
                  <span class="text-[var(--color-text-tertiary)]">({{ filteredCourses.length }})</span>
                </span>
                <svg
                  class="w-4 h-4 transition-transform"
                  :class="{ 'rotate-180': categoryPopupOpen }"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Expanded Category List -->
              <div v-if="categoryPopupOpen" class="bg-[var(--color-bg)] border-t border-[var(--color-border)]">
                <div class="max-h-[150px] overflow-y-auto">
                  <!-- Alle -->
                  <button
                    @click.stop="selectedCategoryFilter = null"
                    class="w-full px-4 py-1.5 text-xs text-left flex items-center justify-between hover:bg-[var(--color-surface-secondary)] transition-colors"
                    :class="selectedCategoryFilter === null ? 'text-[var(--color-primary)] font-medium' : 'text-[var(--color-text-secondary)]'"
                  >
                    <span>Alle Kategorien</span>
                    <span>{{ courses.length }}</span>
                  </button>
                  <!-- Categories -->
                  <button
                    v-for="cat in allCategories"
                    :key="cat"
                    @click.stop="selectedCategoryFilter = cat"
                    class="w-full px-4 py-1.5 text-xs text-left flex items-center justify-between hover:bg-[var(--color-surface-secondary)] transition-colors"
                    :class="selectedCategoryFilter === cat ? 'text-[var(--color-primary)] font-medium' : 'text-[var(--color-text-secondary)]'"
                  >
                    <span>{{ cat }}</span>
                    <span>{{ getCategoryCount(cat) }}</span>
                  </button>
                  <!-- Ohne -->
                  <button
                    @click.stop="selectedCategoryFilter = '__uncategorized__'"
                    class="w-full px-4 py-1.5 text-xs text-left flex items-center justify-between hover:bg-[var(--color-surface-secondary)] transition-colors"
                    :class="selectedCategoryFilter === '__uncategorized__' ? 'text-[var(--color-primary)] font-medium' : 'text-[var(--color-text-tertiary)]'"
                  >
                    <span>Ohne Kategorie</span>
                    <span>{{ getUncategorizedCount() }}</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- Action: New Course -->
            <button
              @click="showNewCourseModal = true; courseDropdownOpen = false"
              class="w-full px-3 py-2.5 text-sm text-left flex items-center gap-2 bg-gradient-to-r from-violet-500/10 to-purple-500/10 hover:from-violet-500/20 hover:to-purple-500/20 text-[var(--color-primary)] font-medium transition-colors border-b border-[var(--color-border)]"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Neuer Kurs erstellen
            </button>

            <!-- Recently Edited (only if no search and has recent) -->
            <div v-if="!courseSearchQuery && recentCourses.length > 0" class="border-b border-[var(--color-border)]">
              <div class="px-3 py-1 text-[9px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider bg-[var(--color-surface-secondary)]">
                Zuletzt bearbeitet
              </div>
              <button
                v-for="course in recentCourses"
                :key="'recent-' + course.course_id"
                @click="selectCourse(course.course_id)"
                class="w-full px-3 py-2 text-sm text-left flex items-center gap-2 hover:bg-[var(--color-surface-secondary)] transition-colors"
                :class="selectedCourseId === course.course_id ? 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]' : 'text-[var(--color-text-primary)]'"
              >
                <span class="text-xs">🕐</span>
                <span class="flex-1 truncate">{{ course.title }}</span>
              </button>
            </div>

            <!-- Courses Header with Count -->
            <div class="px-3 py-1 text-[9px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider bg-[var(--color-surface-secondary)] flex justify-between">
              <span>{{ courseSearchQuery ? 'Suchergebnisse' : 'Alle Kurse' }}</span>
              <span>{{ filteredCourses.length }} / {{ courses.length }}</span>
            </div>

            <!-- Course List (Grouped by Category) -->
            <div class="max-h-[280px] overflow-y-auto">
              <div v-if="filteredCourses.length === 0" class="px-3 py-4 text-sm text-[var(--color-text-tertiary)] text-center">
                {{ courseSearchQuery ? 'Keine Kurse gefunden' : 'Keine Kurse vorhanden' }}
              </div>

              <!-- Categorized Courses -->
              <template v-for="categoryName in coursesByCategory.sortedCategories" :key="categoryName">
                <div class="px-3 py-2 text-xs font-semibold text-[var(--color-primary)] uppercase tracking-wide bg-[var(--color-primary-subtle)]/40 flex items-center gap-2 sticky top-0">
                  <span>📁</span>
                  <span>{{ categoryName }}</span>
                  <span class="text-[var(--color-text-tertiary)] font-normal text-[10px]">({{ coursesByCategory.groups[categoryName].length }})</span>
                </div>
                <button
                  v-for="course in coursesByCategory.groups[categoryName]"
                  :key="course.course_id"
                  @click="selectCourse(course.course_id)"
                  class="w-full px-3 py-2 text-sm text-left flex items-center gap-2 hover:bg-[var(--color-surface-secondary)] transition-colors"
                  :class="selectedCourseId === course.course_id ? 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]' : 'text-[var(--color-text-primary)]'"
                >
                  <span class="w-5 h-5 rounded bg-[var(--color-surface-secondary)] flex items-center justify-center text-xs">📚</span>
                  <span class="flex-1 truncate">{{ course.title }}</span>
                  <svg v-if="selectedCourseId === course.course_id" class="w-4 h-4 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
              </template>

              <!-- Uncategorized Courses -->
              <template v-if="coursesByCategory.uncategorized.length > 0">
                <div v-if="coursesByCategory.sortedCategories.length > 0" class="px-3 py-2 text-xs font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wide bg-[var(--color-surface-secondary)] sticky top-0 flex items-center gap-2">
                  <span>📦</span>
                  <span>Ohne Kategorie</span>
                  <span class="font-normal text-[10px]">({{ coursesByCategory.uncategorized.length }})</span>
                </div>
                <button
                  v-for="course in coursesByCategory.uncategorized"
                  :key="course.course_id"
                  @click="selectCourse(course.course_id)"
                  class="w-full px-3 py-2 text-sm text-left flex items-center gap-2 hover:bg-[var(--color-surface-secondary)] transition-colors"
                  :class="selectedCourseId === course.course_id ? 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]' : 'text-[var(--color-text-primary)]'"
                >
                  <span class="w-5 h-5 rounded bg-[var(--color-surface-secondary)] flex items-center justify-center text-xs">📚</span>
                  <span class="flex-1 truncate">{{ course.title }}</span>
                  <svg v-if="selectedCourseId === course.course_id" class="w-4 h-4 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
              </template>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-lg">
          <span class="text-xs text-white/70">Lektionen:</span>
          <span class="text-sm font-bold text-white">{{ stats.totalLessons }}</span>
        </div>
      </div>
    </div>

    <!-- Hidden file input for course-specific uploads -->
    <input
      ref="fileUploadInput"
      type="file"
      class="hidden"
      accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md"
      @change="handleFileUpload"
      multiple
    />

    <!-- New Course Modal -->
    <div v-if="showNewCourseModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="showNewCourseModal = false">
      <div class="bg-[var(--color-surface)] rounded-xl shadow-2xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
        <h3 class="text-lg font-bold text-[var(--color-text-primary)] mb-4">Neuen Kurs erstellen</h3>

        <div class="space-y-4">
          <!-- Step 1: File Upload (prominent) -->
          <div class="bg-[var(--color-bg)] rounded-lg p-4 border border-[var(--color-border)]">
            <label class="block text-sm font-medium text-[var(--color-text-primary)] mb-2">
              📄 Schritt 1: Material hochladen
            </label>
            <div
              class="border-2 border-dashed border-[var(--color-border)] rounded-lg p-6 text-center hover:border-[var(--color-primary)] transition-colors cursor-pointer"
              :class="{ 'border-[var(--color-primary)] bg-[var(--color-primary-subtle)]': newCourse.files.length > 0 }"
              @click="($refs.newCourseFileInput as HTMLInputElement)?.click()"
              @dragover.prevent
              @drop.prevent="handleNewCourseFileDrop"
            >
              <input
                ref="newCourseFileInput"
                type="file"
                class="hidden"
                accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md"
                @change="handleNewCourseFileSelect"
                multiple
              />
              <div v-if="newCourse.files.length === 0" class="text-[var(--color-text-tertiary)]">
                <svg class="w-10 h-10 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p class="text-sm font-medium">PDF, Word, PowerPoint oder Textdateien</p>
                <p class="text-xs mt-1">Mehrere Dateien möglich - Klicken oder hierher ziehen</p>
              </div>
              <div v-else class="space-y-2 text-left">
                <div
                  v-for="(file, index) in newCourse.files"
                  :key="index"
                  class="flex items-center gap-2 text-sm text-[var(--color-text-primary)] bg-[var(--color-surface)] rounded px-3 py-2"
                >
                  <span>📄</span>
                  <span class="flex-1 truncate">{{ file.name }}</span>
                  <span class="text-xs text-[var(--color-text-tertiary)]">{{ formatFileSize(file.size) }}</span>
                  <button
                    @click.stop="newCourse.files.splice(index, 1)"
                    class="text-red-500 hover:text-red-600 p-1"
                  >
                    ✕
                  </button>
                </div>
                <p class="text-xs text-[var(--color-primary)] text-center pt-2">+ Weitere Dateien hinzufügen</p>
              </div>
            </div>

            <!-- AI Analyze Button -->
            <button
              v-if="newCourse.files.length > 0 && !newCourse.aiAnalyzed"
              @click="analyzeFilesWithAI"
              :disabled="isAnalyzingFiles"
              class="mt-3 w-full px-4 py-2.5 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-lg hover:from-violet-700 hover:to-purple-700 disabled:opacity-50 flex items-center justify-center gap-2 font-medium"
            >
              <span v-if="isAnalyzingFiles" class="animate-spin">⏳</span>
              <span v-else>🤖</span>
              {{ isAnalyzingFiles ? 'KI analysiert...' : 'Mit KI analysieren' }}
            </button>
            <p v-if="newCourse.files.length > 0 && !newCourse.aiAnalyzed" class="text-xs text-[var(--color-text-tertiary)] mt-2 text-center">
              KI schlägt Titel, Beschreibung & Kategorie vor
            </p>
          </div>

          <!-- Step 2: Course Details (filled by AI or manual) -->
          <div class="space-y-4" :class="{ 'opacity-50': newCourse.files.length > 0 && !newCourse.aiAnalyzed && !newCourse.title }">
            <div class="flex items-center gap-2 text-sm font-medium text-[var(--color-text-primary)]">
              <span>📝</span>
              <span>Schritt 2: Kursdetails</span>
              <span v-if="newCourse.aiAnalyzed" class="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded">✓ KI-Vorschlag</span>
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Kurstitel *</label>
              <input
                v-model="newCourse.title"
                type="text"
                placeholder="z.B. IT-Grundlagen für Fachinformatiker"
                class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)]"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Beschreibung</label>
              <textarea
                v-model="newCourse.description"
                rows="3"
                placeholder="Kurze Beschreibung des Kursinhalts..."
                class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-primary)] resize-none"
              ></textarea>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Kategorie</label>
                <select
                  v-model="newCourse.categoryId"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                >
                  <option :value="null">Keine Kategorie</option>
                  <option v-for="cat in availableCategories" :key="cat.category_id" :value="cat.category_id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">🤖 KI-Profil</label>
                <select
                  v-model="newCourse.profileKey"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                >
                  <option v-for="profile in availableProfiles" :key="profile.key" :value="profile.key">
                    {{ profile.name }}{{ profile.is_default ? ' (Standard)' : '' }}
                  </option>
                </select>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Sprache</label>
                <select
                  v-model="newCourse.language"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                >
                  <option value="de">Deutsch</option>
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="fr">Français</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-[var(--color-text-secondary)] mb-1">Level</label>
                <select
                  v-model="newCourse.level"
                  class="w-full px-3 py-2 bg-[var(--color-bg)] border border-[var(--color-border)] rounded-lg text-[var(--color-text-primary)]"
                >
                  <option value="beginner">Anfänger</option>
                  <option value="intermediate">Fortgeschritten</option>
                  <option value="advanced">Experte</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-between items-center gap-3 mt-6 pt-4 border-t border-[var(--color-border)]">
          <p class="text-xs text-[var(--color-text-tertiary)]">
            Nach Erstellung → Im Kurs-Builder mit KI weiterarbeiten
          </p>
          <div class="flex gap-3">
            <button
              @click="showNewCourseModal = false; resetNewCourseForm()"
              class="px-4 py-2 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            >
              Abbrechen
            </button>
            <button
              @click="createCourse"
              :disabled="!newCourse.title.trim() || isCreatingCourse"
              class="px-4 py-2 text-sm bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <span v-if="isCreatingCourse" class="animate-spin">⏳</span>
              Kurs erstellen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Tabs -->
    <div class="flex border-b border-[var(--color-border)] bg-[var(--color-surface-secondary)]">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all relative"
        :class="activeTab === tab.id
          ? 'text-[var(--color-primary)] bg-[var(--color-bg)]'
          : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'"
      >
        <span class="text-lg">{{ tab.icon }}</span>
        <span>{{ tab.label }}</span>
        <span
          v-if="tab.badge"
          class="px-1.5 py-0.5 text-[10px] font-bold rounded-full"
          :class="tab.badgeColor || 'bg-[var(--color-primary)] text-white'"
        >
          {{ tab.badge }}
        </span>
        <div
          v-if="activeTab === tab.id"
          class="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--color-primary)]"
        ></div>
      </button>

      <!-- Spacer -->
      <div class="flex-1"></div>

      <!-- Chat Toggle -->
      <button
        @click="chatExpanded = !chatExpanded"
        class="flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all"
        :class="chatExpanded ? 'text-[var(--color-primary)]' : 'text-[var(--color-text-secondary)]'"
      >
        <span class="text-lg">💬</span>
        <span>Chat</span>
        <svg
          class="w-4 h-4 transition-transform"
          :class="chatExpanded ? 'rotate-180' : ''"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>

    <!-- Main Content Area -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Left Sidebar: Course Structure OR Builder Session (not for Global tab) -->
      <div
        v-if="activeTab !== 'global'"
        class="w-64 flex-shrink-0 border-r border-[var(--color-border)] bg-[var(--color-surface-secondary)] flex flex-col"
      >
        <!-- Builder Tab: Session & Verlauf Sidebar -->
        <CourseAuthoringSidebar
          v-if="activeTab === 'builder'"
          :session-meta="kursBuilderRef?.sessionMeta"
          :activity-log="kursBuilderRef?.activityLog || []"
          :stats="kursBuilderRef?.draftStats"
        />

        <!-- Other Tabs: Chapter Tree Sidebar -->
        <template v-else>
          <!-- Sidebar Header -->
          <div class="p-3 border-b border-[var(--color-border)]">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Suchen..."
                class="w-full pl-8 pr-3 py-2 text-sm bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg"
              />
              <svg class="absolute left-2.5 top-2.5 w-4 h-4 text-[var(--color-text-tertiary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>

          <!-- Chapter Tree -->
          <div class="flex-1 overflow-y-auto p-2">
            <div v-if="!selectedCourseId" class="p-4 text-center text-sm text-[var(--color-text-tertiary)]">
              Wähle einen Kurs aus
            </div>
            <div v-else-if="loading" class="p-4 text-center">
              <div class="animate-spin w-6 h-6 border-2 border-[var(--color-primary)] border-t-transparent rounded-full mx-auto"></div>
            </div>
            <template v-else>
              <div v-for="chapter in filteredChapters" :key="chapter.chapter_id" class="mb-1">
                <!-- Chapter Header -->
                <button
                  @click="toggleChapter(chapter)"
                  class="w-full p-2 rounded-lg text-left flex items-center gap-2 transition-colors"
                  :class="selectedChapterId === chapter.chapter_id
                    ? 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'
                    : 'hover:bg-[var(--color-surface)]'"
                >
                  <svg
                    class="w-4 h-4 transition-transform flex-shrink-0"
                    :class="expandedChapters.has(chapter.chapter_id) ? 'rotate-90' : ''"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                  <span class="text-xs font-mono text-[var(--color-text-tertiary)]">{{ chapter.order_index + 1 }}.</span>
                  <span class="text-sm font-medium truncate flex-1">{{ chapter.title }}</span>
                  <span class="text-xs text-[var(--color-text-tertiary)]">{{ chapter.lessons?.length || 0 }}</span>
                </button>

                <!-- Lessons -->
                <div v-if="expandedChapters.has(chapter.chapter_id)" class="ml-4 mt-1 space-y-0.5">
                  <button
                    v-for="lesson in chapter.lessons"
                    :key="lesson.lesson_id"
                    @click="selectLesson(lesson, chapter)"
                    class="w-full p-2 rounded-lg text-left flex items-center gap-2 transition-colors text-sm"
                    :class="selectedLessonId === lesson.lesson_id
                      ? 'bg-[var(--color-primary)] text-white'
                      : 'hover:bg-[var(--color-surface)] text-[var(--color-text-secondary)]'"
                  >
                    <span class="text-xs font-mono opacity-60">{{ lesson.order_index + 1 }}.</span>
                    <span class="truncate flex-1">{{ lesson.title }}</span>
                    <!-- LM Badge -->
                    <span
                      v-if="lesson.lm_type"
                      class="px-1.5 py-0.5 text-[10px] font-medium rounded"
                      :class="selectedLessonId === lesson.lesson_id ? 'bg-white/20' : 'bg-[var(--color-primary-subtle)] text-[var(--color-primary)]'"
                    >
                      {{ lesson.lm_type }}
                    </span>
                  </button>
                </div>
              </div>
            </template>
          </div>

          <!-- Quick Actions -->
          <div class="p-3 border-t border-[var(--color-border)] space-y-2">
            <button
              @click="createNewChapter"
              class="w-full p-2 rounded-lg text-sm font-medium bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] transition-colors flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              Neues Kapitel
            </button>
          </div>
        </template>
      </div>

      <!-- Main Content -->
      <div class="flex-1 flex flex-col overflow-hidden">
        <!-- Tab Content -->
        <div class="flex-1 overflow-y-auto">
          <!-- 📚 Kurs-Builder Tab (KI-gestützte Kurserstellung) -->
          <KursBuilderTab
            v-if="activeTab === 'builder'"
            ref="kursBuilderRef"
            :course="selectedCourse"
          />

          <!-- 🤖 Tutor Tab (Kapitel/Lektions-Theorie & Erklärungen) -->
          <TutorTab
            v-if="activeTab === 'tutor'"
            :lesson="selectedLesson"
            :chapter="selectedChapter"
            :course="selectedCourse"
            @back-to-chapter="clearLessonSelection"
          />

          <!-- 🧩 Lernmethoden Tab (19 Content-LMs) -->
          <LernmethodenTab
            v-if="activeTab === 'methods'"
            :course="selectedCourse"
            :chapter="selectedChapter"
            :lesson="selectedLesson"
            :chapters="chapters"
          />

          <!-- 📝 Prüfungen Tab (KI-Prüfungsgenerierung) -->
          <ExamsTab
            v-if="activeTab === 'exams'"
            :course="selectedCourse"
            :chapter="selectedChapter"
            :chapters="chapters"
          />

          <!-- 🎛️ Features Tab (System-Features aktivieren) -->
          <SystemFeaturesTab
            v-if="activeTab === 'features'"
            :course="selectedCourse"
            :chapter="selectedChapter"
            :lesson="selectedLesson"
          />

          <!-- 📄 Prompts Tab (System-Prompts verwalten) -->
          <PromptsTab
            v-if="activeTab === 'prompts'"
            :course="selectedCourse"
          />

          <!-- 📊 Analytics Tab (Kurs-Statistiken & KI-Nutzung) -->
          <AnalyticsTab
            v-if="activeTab === 'analytics'"
            :course="selectedCourse"
            :stats="stats"
          />

          <!-- ⚙️ Einstellungen Tab (Kurs-spezifische KI-Modelle & Profile) -->
          <SettingsTab
            v-if="activeTab === 'settings'"
            :course="selectedCourse"
          />

          <!-- 🌐 Globale Einstellungen Tab (Provider, Profile, API-Keys) -->
          <GlobalSettingsTab
            v-if="activeTab === 'global'"
          />
        </div>

        <!-- Chat Panel (collapsible) -->
        <div
          v-if="chatExpanded"
          class="h-64 border-t border-[var(--color-border)] flex flex-col bg-[var(--color-surface-secondary)]"
        >
          <ChatPanel
            :lessonTitle="selectedLesson?.title"
            :courseTitle="selectedCourse?.title"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import type { LsxWindow } from '@/store/window.store'
import http from '@/api/http'

// Sub-components - 9 Main Tabs (8 Kurs-bezogen + 1 Global)
import KursBuilderTab from './ai-studio/KursBuilderTab.vue'
import TutorTab from './ai-studio/TutorTab.vue'
import LernmethodenTab from './ai-studio/LernmethodenTab.vue'
import ExamsTab from './ai-studio/ExamsTab.vue'
import SystemFeaturesTab from './ai-studio/SystemFeaturesTab.vue'
import PromptsTab from './ai-studio/PromptsTab.vue'
import AnalyticsTab from './ai-studio/AnalyticsTab.vue'
import SettingsTab from './ai-studio/SettingsTab.vue'
import GlobalSettingsTab from './ai-studio/GlobalSettingsTab.vue'
import ChatPanel from './ai-studio/ChatPanel.vue'
import CourseAuthoringSidebar from '@/components/ai-studio/course-authoring/CourseAuthoringSidebar.vue'

// Types
interface Course {
  course_id: string
  title: string
  description?: string
  category_id?: number | null
  category_name?: string | null
}

interface Chapter {
  chapter_id: string
  title: string
  order_index: number
  lessons?: Lesson[]
}

interface Lesson {
  lesson_id: string
  title: string
  order_index: number
  lm_type?: string
  has_video?: boolean
  video_generating?: boolean
  content?: Record<string, unknown>
}

interface Stats {
  videosGenerated: number
  totalLessons: number
  tokensUsed: number
  costToday: number
}

// Props
interface Props {
  window: LsxWindow
}

const props = defineProps<Props>()

// State
const loading = ref(false)
const courses = ref<Course[]>([])
const selectedCourseId = ref('')
const selectedCourse = computed(() => courses.value.find(c => c.course_id === selectedCourseId.value) || null)

// KursBuilder Ref for sidebar data
const kursBuilderRef = ref<InstanceType<typeof KursBuilderTab> | null>(null)

const chapters = ref<Chapter[]>([])
const expandedChapters = ref<Set<string>>(new Set())
const selectedChapterId = ref<string | null>(null)
const selectedChapter = computed(() => chapters.value.find(c => c.chapter_id === selectedChapterId.value))

const selectedLessonId = ref<string | null>(null)
const selectedLesson = computed(() => {
  for (const chapter of chapters.value) {
    const lesson = chapter.lessons?.find(l => l.lesson_id === selectedLessonId.value)
    if (lesson) return lesson
  }
  return null
})

const searchQuery = ref('')
const activeTab = ref('builder') // Default to Kurs-Builder tab
const chatExpanded = ref(false)

// New Course Modal
const showNewCourseModal = ref(false)
const isCreatingCourse = ref(false)
const newCourse = ref({
  title: '',
  description: '',
  language: 'de',
  level: 'beginner',
  categoryId: null as number | null,
  profileKey: 'standard' as string,
  files: [] as File[],
  aiAnalyzed: false
})
const isAnalyzingFiles = ref(false)
const availableCategories = ref<Array<{ category_id: number; name: string }>>([])
const availableProfiles = ref<Array<{ key: string; name: string; description?: string; is_default?: boolean }>>([])

function resetNewCourseForm() {
  const defaultProfile = availableProfiles.value.find(p => p.is_default)?.key || 'standard'
  newCourse.value = {
    title: '',
    description: '',
    language: 'de',
    level: 'beginner',
    categoryId: null,
    profileKey: defaultProfile,
    files: [],
    aiAnalyzed: false
  }
}

async function loadCategories() {
  try {
    const response = await http.get('/categories')
    availableCategories.value = response.data.data?.categories || response.data.categories || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

async function loadProfiles() {
  try {
    const response = await http.get('/admin/ai-model-profiles')
    availableProfiles.value = response.data.data?.profiles || []
    // Set default profile in newCourse
    const defaultProfile = availableProfiles.value.find(p => p.is_default)
    if (defaultProfile) {
      newCourse.value.profileKey = defaultProfile.key
    }
  } catch (error) {
    console.error('Failed to load profiles:', error)
  }
}

async function analyzeFilesWithAI() {
  if (!newCourse.value.files.length) return

  isAnalyzingFiles.value = true

  try {
    // Upload files for analysis
    const formData = new FormData()
    for (const file of newCourse.value.files) {
      formData.append('files', file)
    }
    formData.append('action', 'analyze_for_course')

    const response = await http.post('/admin/ai-studio/analyze-material', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    if (response.data.success) {
      const suggestion = response.data.data || response.data

      // Fill in suggestions
      if (suggestion.title) newCourse.value.title = suggestion.title
      if (suggestion.description) newCourse.value.description = suggestion.description
      if (suggestion.category_id) newCourse.value.categoryId = suggestion.category_id
      if (suggestion.level) newCourse.value.level = suggestion.level
      if (suggestion.language) newCourse.value.language = suggestion.language

      newCourse.value.aiAnalyzed = true
    } else {
      // Fallback: Use filename as title
      const fileName = newCourse.value.files[0]?.name.replace(/\.[^/.]+$/, '') || ''
      newCourse.value.title = fileName
      newCourse.value.aiAnalyzed = true
      console.warn('AI analysis failed, using filename as title')
    }
  } catch (error) {
    console.error('Failed to analyze files:', error)
    // Fallback
    const fileName = newCourse.value.files[0]?.name.replace(/\.[^/.]+$/, '') || ''
    newCourse.value.title = fileName
    newCourse.value.aiAnalyzed = true
  } finally {
    isAnalyzingFiles.value = false
  }
}

// File Upload State
const uploadingFiles = ref(false)
const fileUploadInput = ref<HTMLInputElement | null>(null)

// Course Dropdown State
const courseDropdownOpen = ref(false)
const courseDropdownRef = ref<HTMLElement | null>(null)
const courseSearchQuery = ref('')
const selectedCategoryFilter = ref<string | null>(null) // null = alle Kategorien
const categoryPopupOpen = ref(false)
const recentCourseIds = ref<string[]>([]) // Track recently selected courses

const stats = ref<Stats>({
  videosGenerated: 0,
  totalLessons: 0,
  tokensUsed: 0,
  costToday: 0
})

// Tabs configuration - 9 Main Tabs (8 Kurs-bezogen + 1 Global)
const tabs = computed(() => [
  { id: 'builder', icon: '📚', label: 'Kurs-Builder', badge: kursBuilderRef.value?.hasSession ? '●' : undefined, badgeColor: 'bg-green-500 text-white' },
  { id: 'tutor', icon: '🤖', label: 'Tutor', badge: stats.value.totalLessons > 0 ? `${stats.value.totalLessons}` : undefined, badgeColor: 'bg-violet-500 text-white' },
  { id: 'methods', icon: '🧩', label: 'Lernmethoden' },
  { id: 'exams', icon: '📝', label: 'Prüfungen' },
  { id: 'features', icon: '🎛️', label: 'Features' },
  { id: 'prompts', icon: '📄', label: 'Prompts' },
  { id: 'analytics', icon: '📊', label: 'Analytics' },
  { id: 'settings', icon: '⚙️', label: 'Einstellungen' },
  { id: 'global', icon: '🌐', label: 'Global' }
])

// All unique categories from courses
const allCategories = computed(() => {
  const categories = new Set<string>()
  for (const course of courses.value) {
    if (course.category_name) {
      categories.add(course.category_name)
    }
  }
  return Array.from(categories).sort()
})

// Helper: Count courses in a category
function getCategoryCount(categoryName: string): number {
  return courses.value.filter(c => c.category_name === categoryName).length
}

// Helper: Count uncategorized courses
function getUncategorizedCount(): number {
  return courses.value.filter(c => !c.category_name).length
}

// Filtered courses based on search AND category filter
const filteredCourses = computed(() => {
  let result = courses.value

  // Apply category filter
  if (selectedCategoryFilter.value) {
    if (selectedCategoryFilter.value === '__uncategorized__') {
      result = result.filter(c => !c.category_name)
    } else {
      result = result.filter(c => c.category_name === selectedCategoryFilter.value)
    }
  }

  // Apply search filter
  if (courseSearchQuery.value) {
    const query = courseSearchQuery.value.toLowerCase()
    result = result.filter(course =>
      course.title.toLowerCase().includes(query) ||
      course.category_name?.toLowerCase().includes(query)
    )
  }

  return result
})

// Courses grouped by category
const coursesByCategory = computed(() => {
  const groups: Record<string, Course[]> = {}
  const uncategorized: Course[] = []

  for (const course of filteredCourses.value) {
    const categoryName = course.category_name || null
    if (categoryName) {
      if (!groups[categoryName]) {
        groups[categoryName] = []
      }
      groups[categoryName].push(course)
    } else {
      uncategorized.push(course)
    }
  }

  // Sort categories alphabetically
  const sortedCategories = Object.keys(groups).sort()

  return { groups, sortedCategories, uncategorized }
})

// Recent courses (max 5, excluding current selection)
const recentCourses = computed(() => {
  return recentCourseIds.value
    .filter(id => id !== selectedCourseId.value)
    .slice(0, 5)
    .map(id => courses.value.find(c => c.course_id === id))
    .filter((c): c is Course => c !== undefined)
})

// Filtered chapters based on search
const filteredChapters = computed(() => {
  if (!searchQuery.value) return chapters.value
  const query = searchQuery.value.toLowerCase()
  return chapters.value.filter(chapter => {
    if (chapter.title.toLowerCase().includes(query)) return true
    return chapter.lessons?.some(lesson => lesson.title.toLowerCase().includes(query))
  })
})

// Methods
async function loadCourses() {
  try {
    const response = await http.get('/admin/courses')
    courses.value = response.data.data?.courses || response.data.courses || []
  } catch (error) {
    console.error('Failed to load courses:', error)
  }
}

async function loadChaptersWithLessons(courseId: string) {
  loading.value = true
  try {
    // Load chapters
    const chaptersRes = await http.get(`/admin/courses/${courseId}/chapters`)
    const data = chaptersRes.data
    const loadedChapters = data.data?.chapters || data.chapters || []

    // Load lessons for each chapter
    for (const chapter of loadedChapters) {
      try {
        const lessonsRes = await http.get(`/admin/chapters/${chapter.chapter_id}/lessons`)
        const lessonsData = lessonsRes.data
        chapter.lessons = (lessonsData.data?.lessons || lessonsData.lessons || []).map((l: any) => ({
          ...l,
          lm_type: l.content?.lm_primary,
          has_video: l.content?.has_video || false,
          video_generating: false
        }))
      } catch {
        chapter.lessons = []
      }
    }

    chapters.value = loadedChapters
    updateStats()
  } catch (error) {
    console.error('Failed to load chapters:', error)
  } finally {
    loading.value = false
  }
}

function updateStats() {
  let total = 0
  let withVideo = 0
  for (const chapter of chapters.value) {
    for (const lesson of chapter.lessons || []) {
      total++
      if (lesson.has_video) withVideo++
    }
  }
  stats.value.totalLessons = total
  stats.value.videosGenerated = withVideo
}

function onCourseChange(_event?: Event) {
  // Reset state
  chapters.value = []
  selectedChapterId.value = null
  selectedLessonId.value = null
  expandedChapters.value.clear()

  // Load chapters if course is selected
  if (selectedCourseId.value) {
    loadChaptersWithLessons(selectedCourseId.value)
  }
}

function selectCourse(courseId: string) {
  selectedCourseId.value = courseId
  courseDropdownOpen.value = false
  categoryPopupOpen.value = false
  courseSearchQuery.value = '' // Clear search
  selectedCategoryFilter.value = null // Clear filter

  // Track in recent courses (add to front, remove duplicates, max 10)
  recentCourseIds.value = [
    courseId,
    ...recentCourseIds.value.filter(id => id !== courseId)
  ].slice(0, 10)

  // Persist to localStorage
  localStorage.setItem('lsx_recent_courses', JSON.stringify(recentCourseIds.value))

  onCourseChange()
}


function handleClickOutside(event: MouseEvent) {
  if (courseDropdownRef.value && !courseDropdownRef.value.contains(event.target as Node)) {
    courseDropdownOpen.value = false
    categoryPopupOpen.value = false
  }
}

function toggleChapter(chapter: Chapter) {
  // If clicking on already selected chapter AND a lesson is selected → deselect lesson
  // This allows going back to chapter view
  if (selectedChapterId.value === chapter.chapter_id && selectedLessonId.value) {
    selectedLessonId.value = null
    return
  }

  // Normal toggle behavior for expand/collapse
  if (expandedChapters.value.has(chapter.chapter_id)) {
    // If already selected and no lesson, collapse
    if (selectedChapterId.value === chapter.chapter_id) {
      expandedChapters.value.delete(chapter.chapter_id)
    }
  } else {
    expandedChapters.value.add(chapter.chapter_id)
  }
  selectedChapterId.value = chapter.chapter_id
}

function selectLesson(lesson: Lesson, chapter: Chapter) {
  selectedLessonId.value = lesson.lesson_id
  selectedChapterId.value = chapter.chapter_id
  if (!expandedChapters.value.has(chapter.chapter_id)) {
    expandedChapters.value.add(chapter.chapter_id)
  }
}

function clearLessonSelection() {
  // Clear lesson selection to go back to chapter view
  selectedLessonId.value = null
}

function createNewChapter() {
  // Open chat with prompt
  chatExpanded.value = true
  // TODO: Send message to chat
}

async function createCourse() {
  if (!newCourse.value.title.trim()) return

  isCreatingCourse.value = true
  try {
    const response = await http.post('/admin/courses', {
      title: newCourse.value.title,
      description: newCourse.value.description,
      language: newCourse.value.language,
      level: newCourse.value.level,
      status: 'draft'
    })

    const data = response.data
    const createdCourse = data.data?.course || data.course

    // Refresh courses list
    await loadCourses()

    // Select the new course
    if (createdCourse?.course_id) {
      selectedCourseId.value = createdCourse.course_id
      onCourseChange()

      // If AI mode, switch to builder tab
      if (newCourse.value.useAI) {
        activeTab.value = 'builder'
      }
    }

    // Reset and close modal
    showNewCourseModal.value = false
    newCourse.value = {
      title: '',
      description: '',
      language: 'de',
      level: 'beginner',
      useAI: true
    }
  } catch (error: any) {
    console.error('Failed to create course:', error)
    const message = error.response?.data?.error?.message || 'Kurs konnte nicht erstellt werden'
    alert(`Fehler: ${message}`)
  } finally {
    isCreatingCourse.value = false
  }
}

// New Course File Handling
function handleNewCourseFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  const files = Array.from(input.files)
  newCourse.value.files.push(...files)
  input.value = '' // Reset input for re-selection
}

function handleNewCourseFileDrop(event: DragEvent) {
  const files = event.dataTransfer?.files
  if (!files?.length) return

  const validFiles = Array.from(files).filter(file => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    return ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md'].includes(ext || '')
  })

  newCourse.value.files.push(...validFiles)
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function handleFileUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files?.length) return

  // Need a course selected for file upload
  if (!selectedCourseId.value) {
    alert('Bitte wähle zuerst einen Kurs aus, um Dateien hochzuladen.')
    input.value = ''
    return
  }

  uploadingFiles.value = true
  const files = Array.from(input.files)

  try {
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_category', 'material')

      await http.post(`/admin/courses/${selectedCourseId.value}/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }

    // Switch to exams tab where files are displayed, or stay on current tab
    if (activeTab.value === 'builder') {
      // Notify the builder about new files if possible
      console.log(`Uploaded ${files.length} file(s) to course`)
    }

    alert(`${files.length} Datei(en) erfolgreich hochgeladen!`)
  } catch (error) {
    console.error('File upload failed:', error)
    alert('Fehler beim Hochladen der Dateien')
  } finally {
    uploadingFiles.value = false
    input.value = ''
  }
}


function onContentUpdate() {
  // Reload lessons after content update
  if (selectedCourseId.value) {
    loadChaptersWithLessons(selectedCourseId.value)
  }
}


// Lifecycle
onMounted(() => {
  loadCourses()
  loadCategories()
  loadProfiles()

  // Load recent courses from localStorage
  try {
    const stored = localStorage.getItem('lsx_recent_courses')
    if (stored) {
      recentCourseIds.value = JSON.parse(stored)
    }
  } catch (e) {
    console.warn('Failed to load recent courses:', e)
  }

  // Check if opened with courseId
  const courseId = props.window.payload?.courseId
  if (courseId && typeof courseId === 'string') {
    selectedCourseId.value = courseId
    onCourseChange()
  }

  // Add click outside listener for dropdown
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Watch for payload changes
watch(() => props.window.payload?.courseId, (newCourseId) => {
  if (newCourseId && typeof newCourseId === 'string' && newCourseId !== selectedCourseId.value) {
    selectedCourseId.value = newCourseId
    onCourseChange()
  }
})
</script>

<style scoped>
.ai-studio-pro {
  min-height: 600px;
  min-width: 900px;
}
</style>
