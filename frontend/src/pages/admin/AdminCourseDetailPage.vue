<!--
  ╔══════════════════════════════════════════════════════════════════════════════╗
  ║  Admin Course Detail Page - Zentrale Kurs-Detailansicht im Admin-Bereich     ║
  ╠══════════════════════════════════════════════════════════════════════════════╣
  ║  WICHTIG: Dies ist die EINZIGE Admin-Kurs-Detailseite!                       ║
  ║  Route: /admin/courses/:id                                                    ║
  ║  Keine alternativen Versionen erstellen!                                     ║
  ╚══════════════════════════════════════════════════════════════════════════════╝

  Refactoring-Historie:
  - 2025-11-27: modules → chapters Umbenennung
  - 2025-12-01: Visuelles Redesign (Hero-Gradient, moderne Stats-Cards,
                Content-Sections, Quick-Actions mit SVG-Icons)

  Features:
  - Hero-Sektion mit animiertem Gradient-Hintergrund
  - 8 Stats-Cards mit farbigen Icons (Blau, Grün, Lila, Orange, Pink, Gelb, Amber, Teal)
  - Glassmorphism-Badges für Status/Sprache/Level
  - Chapter-Preview mit Gradient-Nummern-Badges
  - Course Files Section mit modernem Emerald-Design
  - Quick-Actions mit individuellen Farbschemata
  - Vollständiger Dark Mode Support
  - Responsive Design (Mobile/Tablet/Desktop)
-->

<template>
  <div class="admin-course-detail-page">
    <!-- Back Navigation -->
    <div class="px-3 pt-1">
      <router-link to="/admin/courses" class="text-xs text-[var(--color-primary)] hover:underline inline-flex items-center gap-1">
        <span>←</span>
        <span>Zurück</span>
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-10">
      <div class="text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--color-primary)] mx-auto mb-3"></div>
        <p class="text-xs text-[var(--color-text-secondary)]">Lade Kursdetails...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="m-4 rounded-md p-4 border" style="background-color: var(--color-error-bg, #fee); border-color: var(--color-error-border, #fcc);">
      <h3 class="text-sm font-semibold mb-1" style="color: var(--color-error-text, #c00);">Fehler beim Laden</h3>
      <p class="text-xs" style="color: var(--color-error-text-secondary, #e00);">{{ error }}</p>
      <button
        @click="loadCourse"
        class="mt-3 px-3 py-1.5 rounded text-xs transition-colors text-white"
        style="background-color: var(--color-error, #dc2626);"
      >
        Erneut versuchen
      </button>
    </div>

    <!-- Course Details -->
    <div v-else-if="course">

      <!-- ============================================ -->
      <!-- HERO SECTION                                -->
      <!-- ============================================ -->
      <div class="hero-section relative overflow-hidden mx-3 mt-1 rounded-lg shadow-sm">
        <!-- Background: Thumbnail or Animated Gradient -->
        <div class="hero-background absolute inset-0">
          <img
            v-if="course.thumbnail_url"
            :src="course.thumbnail_url"
            :alt="course.title"
            class="w-full h-full object-cover"
          />
          <div
            v-else
            class="w-full h-full animated-gradient"
          ></div>
          <!-- Overlay -->
          <div class="absolute inset-0 bg-gradient-to-t from-[var(--color-background)] via-[var(--color-background)]/70 to-transparent"></div>
        </div>

        <!-- Hero Content -->
        <div class="hero-content relative z-10 px-3 pt-3 pb-2">
          <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <!-- Left: Title & Info -->
            <div class="flex-1">
              <!-- Status Badges -->
              <div class="flex items-center gap-1 mb-1.5 flex-wrap">
                <span
                  class="px-2 py-0.5 rounded-full text-xs font-semibold backdrop-blur-sm"
                  :class="statusBadgeClass"
                  :style="statusBadgeStyle"
                >
                  {{ statusText }}
                </span>
                <span
                  v-if="showAdBadge"
                  class="px-2 py-0.5 rounded-full text-xs font-semibold backdrop-blur-sm bg-amber-500/20 text-amber-700 dark:text-amber-300"
                >
                  Mit Werbung
                </span>
                <span
                  v-if="showPremiumBadge"
                  class="px-2 py-0.5 rounded-full text-xs font-semibold backdrop-blur-sm bg-purple-500/20 text-purple-700 dark:text-purple-300"
                >
                  Premium
                </span>
                <span class="px-2 py-0.5 rounded-full text-xs font-medium backdrop-blur-sm bg-white/10 dark:bg-black/20 text-[var(--color-text-secondary)]">
                  {{ languageLabel }}
                </span>
                <span class="px-2 py-0.5 rounded-full text-xs font-medium backdrop-blur-sm bg-white/10 dark:bg-black/20 text-[var(--color-text-secondary)]">
                  {{ levelLabel }}
                </span>
              </div>

              <!-- Title -->
              <h1 class="text-xl lg:text-2xl font-bold text-[var(--color-text-primary)] mb-1.5">
                {{ course.title }}
              </h1>

              <!-- Description - vollständig lesbar -->
              <p v-if="course.description" class="text-sm text-[var(--color-text-secondary)] leading-relaxed max-w-4xl">
                {{ course.description }}
              </p>
            </div>
          </div>
        </div>

        <!-- Quick Stats Grid - Im Hero integriert -->
        <div class="relative z-10 px-4 md:px-8 pb-2 flex justify-center">
          <div class="grid grid-cols-4 md:grid-cols-8 gap-1.5 w-full max-w-4xl">
          <!-- Chapter Count -->
          <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all cursor-pointer group flex flex-col items-center border border-gray-100 dark:border-gray-700" @click="openChaptersWindow">
            <div class="w-7 h-7 mb-1 bg-blue-100 dark:bg-blue-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
            </div>
            <p class="text-base font-bold text-gray-900 dark:text-white">{{ course.chapter_count || 0 }}</p>
            <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">Kapitel</p>
          </div>

          <!-- Lesson Count -->
          <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
            <div class="w-7 h-7 mb-1 bg-green-100 dark:bg-green-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <p class="text-base font-bold text-gray-900 dark:text-white">{{ lessonCount }}</p>
            <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">Lektionen</p>
          </div>

          <!-- Enrollment Count -->
          <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
            <div class="w-7 h-7 mb-1 bg-purple-100 dark:bg-purple-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
              </svg>
            </div>
            <p class="text-base font-bold text-gray-900 dark:text-white">{{ course.enrollment_count || 0 }}</p>
            <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">Teilnehmer</p>
          </div>

          <!-- Exam Count -->
          <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all cursor-pointer group flex flex-col items-center border border-gray-100 dark:border-gray-700" @click="openExamsWindow">
            <div class="w-7 h-7 mb-1 bg-orange-100 dark:bg-orange-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
              </svg>
            </div>
            <p class="text-base font-bold text-gray-900 dark:text-white">{{ examCount }}</p>
            <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">Prüfungen</p>
          </div>

          <!-- Prompt Count -->
          <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all cursor-pointer group flex flex-col items-center border border-gray-100 dark:border-gray-700" @click="openPromptBrowser">
            <div class="w-7 h-7 mb-1 bg-pink-100 dark:bg-pink-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-pink-600 dark:text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
              </svg>
            </div>
            <p class="text-base font-bold text-gray-900 dark:text-white">{{ promptCount }}</p>
            <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">Prompts</p>
          </div>

          <!-- Files Count -->
          <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all cursor-pointer group flex flex-col items-center border border-gray-100 dark:border-gray-700" @click="triggerFileUpload">
            <div class="w-7 h-7 mb-1 bg-yellow-100 dark:bg-yellow-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
              </svg>
            </div>
            <p class="text-base font-bold text-gray-900 dark:text-white">{{ fileCount }}</p>
            <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">Dateien</p>
          </div>

          <!-- Rating -->
          <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
            <div class="w-7 h-7 mb-1 bg-amber-100 dark:bg-amber-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
              </svg>
            </div>
            <p class="text-base font-bold text-gray-900 dark:text-white">{{ ratingDisplay }}</p>
            <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">Bewertung</p>
          </div>

          <!-- Completion Rate -->
          <div class="stat-card bg-white dark:bg-gray-800 rounded-lg p-2.5 shadow-md hover:shadow-lg transition-all group flex flex-col items-center border border-gray-100 dark:border-gray-700">
            <div class="w-7 h-7 mb-1 bg-teal-100 dark:bg-teal-900/50 rounded-md flex items-center justify-center group-hover:scale-110 transition-transform">
              <svg class="w-4 h-4 text-teal-600 dark:text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"/>
              </svg>
            </div>
            <p class="text-base font-bold text-gray-900 dark:text-white">{{ completionRateDisplay }}</p>
            <p class="text-[10px] font-medium text-gray-600 dark:text-gray-300">Abschluss</p>
          </div>
          </div>
        </div>
      </div>

      <!-- ============================================ -->
      <!-- ACTIONS SECTION                             -->
      <!-- ============================================ -->
      <div class="px-4 py-2">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
          <div class="px-4 py-2 border-b border-gray-200 dark:border-gray-700 animated-header-gradient flex items-center gap-2">
            <div class="w-5 h-5 bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 rounded flex items-center justify-center">
              <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <span class="text-xs font-bold text-gray-900 dark:text-white">Aktionen</span>
          </div>
          <div class="p-2 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-1.5">
          <!-- Kapitel - Blue -->
          <button
            @click="openChaptersWindow"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-blue-500 via-indigo-500 to-blue-600 hover:from-blue-600 hover:via-indigo-600 hover:to-blue-700 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">Kapitel</span>
          </button>

          <!-- Dateien - Orange -->
          <button
            @click="openFilesWindow"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-orange-500 via-amber-500 to-orange-600 hover:from-orange-600 hover:via-amber-600 hover:to-orange-700 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">Dateien</span>
          </button>

          <!-- Prüfungen - Pink/Rose -->
          <button
            @click="openExamsWindow"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-pink-500 via-rose-500 to-pink-600 hover:from-pink-600 hover:via-rose-600 hover:to-pink-700 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">Prüfungen</span>
          </button>

          <!-- KI-Prüfung - Purple/Violet -->
          <button
            @click="generateExam"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-purple-500 via-violet-500 to-fuchsia-500 hover:from-purple-600 hover:via-violet-600 hover:to-fuchsia-600 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">KI-Prüfung</span>
          </button>

          <!-- KI-Studio - Indigo/Blue -->
          <button
            @click="openAiStudioWindow"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-indigo-500 via-blue-500 to-cyan-500 hover:from-indigo-600 hover:via-blue-600 hover:to-cyan-600 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">KI-Studio</span>
          </button>

          <!-- Veröffentlichen - Emerald/Teal -->
          <button
            v-if="course.status === 'draft'"
            @click="publishCourse"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-600 hover:from-emerald-600 hover:via-teal-600 hover:to-cyan-700 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">Veröffentlichen</span>
          </button>

          <!-- Zurückziehen - Amber/Orange (wenn published) -->
          <button
            v-if="course.status === 'published'"
            @click="unpublishCourse"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-amber-500 via-orange-500 to-rose-500 hover:from-amber-600 hover:via-orange-600 hover:to-rose-600 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">Zurückziehen</span>
          </button>

          <!-- Archivieren - Slate/Gray -->
          <button
            v-if="course.status !== 'archived'"
            @click="archiveCourse"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-slate-500 via-gray-500 to-slate-600 hover:from-slate-600 hover:via-gray-600 hover:to-slate-700 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">Archivieren</span>
          </button>

          <!-- Bearbeiten - Grün -->
          <button
            @click="openEditorWindow"
            class="action-btn group py-2.5 px-2 rounded-lg bg-gradient-to-br from-green-500 via-emerald-500 to-green-600 hover:from-green-600 hover:via-emerald-600 hover:to-green-700 shadow-sm hover:shadow-md transition-all text-center"
          >
            <div class="w-8 h-8 mx-auto mb-1 bg-white/20 rounded-md flex items-center justify-center group-hover:scale-110 group-hover:bg-white/30 transition-all">
              <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </div>
            <span class="text-[11px] font-semibold text-white">Bearbeiten</span>
          </button>
          </div>
        </div>
      </div>

      <!-- ============================================ -->
      <!-- INFO GRID - Kursinfo & Ersteller            -->
      <!-- ============================================ -->
      <div class="px-4 py-2 grid grid-cols-1 lg:grid-cols-2 gap-2">
        <!-- Kursinfo -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
          <div class="px-3 py-2 border-b border-gray-200 dark:border-gray-700 animated-header-gradient flex items-center gap-2">
            <div class="w-5 h-5 bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 rounded flex items-center justify-center">
              <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <span class="text-xs font-bold text-gray-900 dark:text-white">Kursinfo</span>
          </div>
          <div class="p-3 space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Kurs-ID:</span>
              <span class="font-mono text-xs text-gray-900 dark:text-white">{{ course.course_id?.slice(0, 8) }}...</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Kategorie:</span>
              <span class="text-gray-900 dark:text-white">{{ course.category || 'Keine' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Preis:</span>
              <span class="text-gray-900 dark:text-white font-semibold">{{ priceLabel }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Sichtbarkeit:</span>
              <span :class="course.is_public ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'">
                {{ course.is_public ? 'Öffentlich' : 'Privat' }}
              </span>
            </div>
            <div class="pt-2 border-t border-gray-200 dark:border-gray-700">
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">Erstellt:</span>
                <span class="text-gray-900 dark:text-white">{{ formatDate(course.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Ersteller -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
          <div class="px-3 py-2 border-b border-gray-200 dark:border-gray-700 animated-header-gradient flex items-center gap-2">
            <div class="w-5 h-5 bg-gradient-to-br from-pink-500 via-purple-500 to-indigo-500 rounded flex items-center justify-center">
              <svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <span class="text-xs font-bold text-gray-900 dark:text-white">Ersteller</span>
          </div>
          <div class="p-3 space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Name:</span>
              <span class="text-gray-900 dark:text-white font-medium">{{ course.creator_name || 'Unbekannt' }}</span>
            </div>
            <div v-if="course.creator_email" class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">E-Mail:</span>
              <a :href="`mailto:${course.creator_email}`" class="text-purple-600 dark:text-purple-400 hover:underline">
                {{ course.creator_email }}
              </a>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Organisation:</span>
              <span class="text-gray-900 dark:text-white">{{ course.organisation_name || 'Keine' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useWindowStore } from '@/store/window.store'
import {
  adminGetCourseDetail,
  adminGetCourseChapters,
  adminDeleteChapter,
  adminPublishCourse,
  adminUnpublishCourse,
  adminArchiveCourse,
  adminListCourseFiles,
  adminUploadCourseFile,
  adminDeleteCourseFile,
  type AdminCourseDetail,
  type AdminChapter,
  type CourseFile,
  type CourseFileCategory,
  type CourseFileCategorySummary
} from '@/api/admin.api'

// Types for chapters/lessons (Refactored: modules → chapters 2025-11-27)
interface Lesson {
  lesson_id?: string
  title: string
  type?: string
  order_index?: number
}

interface Chapter {
  chapter_id?: string
  title: string
  description?: string
  duration_minutes?: number
  order_index?: number
  lessons?: Lesson[]
}

interface Props {
  id: string | number
}

const props = defineProps<Props>()
const windowStore = useWindowStore()

// ============================================================================
// State
// ============================================================================

const course = ref<AdminCourseDetail | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Chapter accordion state
const expandedChapters = ref<number[]>([])
const chapters = ref<Chapter[]>([])
const chaptersLoading = ref(false)

// Stats placeholders (will be loaded from API in future)
const examCount = ref(0)
const promptCount = ref(0)

// Course Files state
const courseFiles = ref<CourseFile[]>([])
const filesLoading = ref(false)
const filesError = ref<string | null>(null)
const filesCategorySummary = ref<CourseFileCategorySummary[]>([])
const fileUploadInput = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)

// ============================================================================
// Computed
// ============================================================================

// Lesson count across all chapters
const lessonCount = computed(() => {
  return chapters.value.reduce((sum, chap) => sum + (chap.lessons?.length || 0), 0)
})

// Files count
const fileCount = computed(() => courseFiles.value.length)

// Revenue display
const revenueDisplay = computed(() => {
  const revenue = (course.value as any)?.revenue || 0
  if (revenue === 0) return '–'
  return `${revenue.toFixed(0)}€`
})

// Rating display
const ratingDisplay = computed(() => {
  const rating = (course.value as any)?.average_rating || 0
  if (rating === 0) return '–'
  return rating.toFixed(1)
})

// Completion rate display
const completionRateDisplay = computed(() => {
  const rate = (course.value as any)?.completion_rate || 0
  if (rate === 0) return '–'
  return `${Math.round(rate)}%`
})

const statusBadgeClass = computed(() => {
  if (!course.value) return ''
  return ''
})

const statusBadgeStyle = computed(() => {
  if (!course.value) return ''

  const statusStyles = {
    draft: 'background-color: var(--color-status-draft-bg, #f3f4f6); color: var(--color-status-draft-text, #374151);',
    published: 'background-color: var(--color-status-published-bg, #dcfce7); color: var(--color-status-published-text, #15803d);',
    archived: 'background-color: var(--color-status-archived-bg, #ffedd5); color: var(--color-status-archived-text, #c2410c);'
  }

  return statusStyles[course.value.status] || statusStyles.draft
})

const statusText = computed(() => {
  if (!course.value) return ''

  const statusLabels = {
    draft: 'Entwurf',
    published: 'Veröffentlicht',
    archived: 'Archiviert'
  }

  return statusLabels[course.value.status] || 'Unbekannt'
})

const languageLabel = computed(() => {
  const languages: Record<string, string> = {
    de: 'Deutsch',
    en: 'English',
    fr: 'Français',
    es: 'Español',
    it: 'Italiano'
  }
  return course.value ? languages[course.value.language] || course.value.language.toUpperCase() : ''
})

const levelLabel = computed(() => {
  if (!course.value?.level) return 'Unbekannt'

  const levels: Record<string, string> = {
    beginner: 'Anfänger',
    intermediate: 'Fortgeschritten',
    advanced: 'Experte',
    expert: 'Meister'
  }

  return levels[course.value.level] || course.value.level
})

// C1.1: Price label with ad logic
const priceLabel = computed(() => {
  if (!course.value) return 'Kostenlos'

  const price = Number(course.value.price || 0)

  if (price === 0 && course.value.ad_enabled) {
    return 'Kostenlos (mit Werbung)'
  }
  if (price === 0 && !course.value.ad_enabled) {
    return 'Kostenlos (Premium - ohne Werbung)'
  }
  if (price > 0) {
    return `${price.toFixed(2)} € (Premium - ohne Werbung)`
  }
  return 'Kostenlos'
})

// C1.1: Ad badge visibility
const showAdBadge = computed(() => {
  if (!course.value) return false
  return Number(course.value.price || 0) === 0 && course.value.ad_enabled
})

// C1.1: Premium badge visibility
const showPremiumBadge = computed(() => {
  if (!course.value) return false
  return Number(course.value.price || 0) === 0 && !course.value.ad_enabled
})

// Methods
const loadCourse = async () => {
  loading.value = true
  error.value = null

  try {
    const courseId = String(props.id)

    // Validate course ID (UUID format)
    if (!courseId || courseId === 'undefined' || courseId === 'null') {
      throw new Error(`Ungültige Kurs-ID: ${props.id}`)
    }

    course.value = await adminGetCourseDetail(courseId)
  } catch (err: any) {
    console.error('Error loading course:', err)
    error.value = err.response?.data?.message || err.message || 'Fehler beim Laden der Kursdetails'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatDateShort = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

/**
 * Load course chapters with lessons
 */
const loadCourseChapters = async (): Promise<void> => {
  if (!course.value) return

  chaptersLoading.value = true

  try {
    const apiChapters = await adminGetCourseChapters(course.value.course_id)
    // Map API chapters to local Chapter type
    chapters.value = apiChapters.map(c => ({
      chapter_id: String(c.chapter_id),
      title: c.title,
      description: c.description || undefined,
      duration_minutes: c.duration_minutes,
      order_index: c.order_index,
      lessons: [] // Lessons would need separate API call if needed
    }))
  } catch (err: any) {
    console.error('Error loading chapters:', err)
    // Don't set error - chapters are non-critical for page display
  } finally {
    chaptersLoading.value = false
  }
}

/**
 * Toggle chapter accordion
 */
const toggleChapter = (index: number): void => {
  const idx = expandedChapters.value.indexOf(index)
  if (idx === -1) {
    expandedChapters.value.push(index)
  } else {
    expandedChapters.value.splice(idx, 1)
  }
}

/**
 * Open Prompt Browser Window (Phase C2.3)
 */
const openPromptBrowser = (): void => {
  if (!course.value) return

  windowStore.openWindow({
    type: 'admin-prompt-browser',
    title: `Prompts: ${course.value.title}`,
    icon: '🤖',
    size: { width: 700, height: 600 },
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

const openEditorWindow = () => {
  if (!course.value) return

  windowStore.openWindow({
    type: 'admin-course-editor',
    title: `Kurs bearbeiten: ${course.value.title}`,
    icon: '✏️',
    payload: {
      courseId: course.value.course_id,
      course: course.value
    }
  })
}

const openChaptersWindow = () => {
  if (!course.value) return

  windowStore.openWindow({
    type: 'admin-kapitel-manager',
    title: `Kapitel: ${course.value.title}`,
    icon: '📚',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

/**
 * Open Files Manager Window
 */
const openFilesWindow = () => {
  if (!course.value) return

  windowStore.openWindow({
    type: 'admin-course-files',
    title: `Dateien: ${course.value.title}`,
    icon: '📁',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

/**
 * Create new chapter - opens editor window without chapterId
 */
const createNewChapter = () => {
  if (!course.value) return

  windowStore.openWindow({
    type: 'admin-kapitel-editor',
    title: 'Neues Kapitel erstellen',
    icon: '📚',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
      // KEIN chapterId = Neu erstellen
    }
  })
}

/**
 * Open AI Studio window for KI-powered content generation
 */
const openAiStudioWindow = () => {
  if (!course.value) return

  windowStore.openWindow({
    type: 'admin-ai-studio',
    title: `KI-Studio: ${course.value.title}`,
    icon: '🤖',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

/**
 * Edit existing chapter - opens editor with chapterId and data
 */
const editChapter = (chapterToEdit: Chapter) => {
  if (!course.value) return

  windowStore.openWindow({
    type: 'admin-kapitel-editor',
    title: `Kapitel: ${chapterToEdit.title}`,
    icon: '📚',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title,
      chapterId: chapterToEdit.chapter_id,
      chapter: {
        chapter_id: chapterToEdit.chapter_id,
        title: chapterToEdit.title,
        description: chapterToEdit.description || ''
      }
    }
  })
}

/**
 * Delete chapter with confirmation
 */
const deleteChapter = async (chapter: Chapter) => {
  if (!course.value || !chapter.chapter_id) return

  if (!confirm(`Möchten Sie das Kapitel "${chapter.title}" wirklich löschen?\n\nAlle Lektionen in diesem Kapitel werden ebenfalls gelöscht.`)) {
    return
  }

  try {
    await adminDeleteChapter(chapter.chapter_id)

    // Kapitel-Liste neu laden
    await loadCourseChapters()

    console.log('Kapitel gelöscht:', chapter.title)
  } catch (error: any) {
    console.error('Fehler beim Löschen:', error)
    alert('Fehler beim Löschen des Kapitels: ' + (error.response?.data?.error || error.message))
  }
}

// C1.3: Open exams window
const openExamsWindow = () => {
  if (!course.value) return

  windowStore.openWindow({
    type: 'admin-exam-manager',
    title: `Prüfungen: ${course.value.title}`,
    icon: '📝',
    payload: {
      courseId: course.value.course_id,
      courseTitle: course.value.title
    }
  })
}

const publishCourse = async () => {
  if (!course.value || !confirm('Möchten Sie diesen Kurs wirklich veröffentlichen?')) return

  try {
    await adminPublishCourse(course.value.course_id)
    await loadCourse() // Reload to get updated status
  } catch (err: any) {
    console.error('Error publishing course:', err)
    alert('Fehler beim Veröffentlichen: ' + (err.response?.data?.message || err.message))
  }
}

const unpublishCourse = async () => {
  if (!course.value || !confirm('Möchten Sie die Veröffentlichung dieses Kurses wirklich zurückziehen?')) return

  try {
    await adminUnpublishCourse(course.value.course_id)
    await loadCourse()
  } catch (err: any) {
    console.error('Error unpublishing course:', err)
    alert('Fehler beim Zurückziehen: ' + (err.response?.data?.message || err.message))
  }
}

const archiveCourse = async () => {
  if (!course.value || !confirm('Möchten Sie diesen Kurs wirklich archivieren?')) return

  try {
    await adminArchiveCourse(course.value.course_id)
    await loadCourse()
  } catch (err: any) {
    console.error('Error archiving course:', err)
    alert('Fehler beim Archivieren: ' + (err.response?.data?.message || err.message))
  }
}

// Selected prompt for exam generation
const selectedExamPrompt = ref<{ id: string; name: string; scope: string } | null>(null)

// C1.3: AI Exam Generator - Opens Prompt Browser for selection
const generateExam = (): void => {
  if (!course.value) return

  // Open prompt browser in selection mode for exam generation
  const callbackId = `exam-generator-${course.value.course_id}`

  windowStore.openWindow({
    type: 'admin-prompt-browser',
    title: 'Prompt für KI-Prüfung auswählen',
    icon: '✨',
    size: { width: 700, height: 600 },
    payload: {
      mode: 'select',
      scope: 'exam_generation',
      courseId: course.value.course_id,
      callbackWindowId: `exam-${course.value.course_id}`,
      callbackId
    }
  })

  // Listen for prompt selection
  const handleExamPromptSelected = (event: CustomEvent<{ callbackId: string; prompt: any }>) => {
    if (event.detail.callbackId === callbackId) {
      selectedExamPrompt.value = event.detail.prompt
      // Remove listener after use
      window.removeEventListener('prompt-selected', handleExamPromptSelected as EventListener)
      // Proceed with exam generation
      startExamGeneration()
    }
  }

  window.addEventListener('prompt-selected', handleExamPromptSelected as EventListener)
}

// Start the actual exam generation after prompt selection
const startExamGeneration = async (): Promise<void> => {
  if (!course.value) return

  const confirmed = confirm(
    `Möchten Sie eine KI-Prüfung für den Kurs "${course.value.title}" generieren?\n\n` +
    (selectedExamPrompt.value
      ? `Ausgewählter Prompt: ${selectedExamPrompt.value.name}\n\n`
      : 'Es wird der Standard-Prompt verwendet.\n\n') +
    'Die KI wird basierend auf den Kursinhalten automatisch Prüfungsfragen erstellen.\n' +
    'Dieser Vorgang kann einige Minuten dauern.'
  )

  if (!confirmed) {
    selectedExamPrompt.value = null
    return
  }

  try {
    // Import the exam generation function
    const { adminGenerateExam } = await import('@/api/admin.api')

    const result = await adminGenerateExam(course.value.course_id, {
      title: `KI-Prüfung: ${course.value.title}`,
      description: `Automatisch generierte Prüfung für den Kurs "${course.value.title}"`,
      exam_standard: 'Custom',
      difficulty: 'intermediate',
      duration_minutes: 60,
      passing_score: 60,
      total_points: 100,
      question_distribution: {
        mcq: 15,
        fill_blanks: 5,
        short_answer: 3
      }
    })

    alert(
      '✅ KI-Prüfung wird generiert!\n\n' +
      `Job-ID: ${result.job_id}\n` +
      `Prüfungs-ID: ${result.exam_id}\n\n` +
      'Die Prüfung wird im Hintergrund generiert. ' +
      'Sie können den Fortschritt im Prüfungs-Manager verfolgen.'
    )

    // Open exam manager to show progress
    openExamsWindow()

  } catch (err: any) {
    console.error('Error generating exam:', err)
    alert('Fehler bei der Prüfungserstellung: ' + (err.response?.data?.error || err.message))
  } finally {
    selectedExamPrompt.value = null
  }
}

// ============================================================================
// Course Files Functions
// ============================================================================

/**
 * Load course files
 */
const loadCourseFiles = async (): Promise<void> => {
  if (!course.value) return

  filesLoading.value = true
  filesError.value = null

  try {
    const response = await adminListCourseFiles(course.value.course_id)
    courseFiles.value = response.files
    filesCategorySummary.value = response.categories_summary
  } catch (err: any) {
    console.error('Error loading course files:', err)
    filesError.value = err.response?.data?.message || err.message || 'Fehler beim Laden der Dateien'
  } finally {
    filesLoading.value = false
  }
}

/**
 * Trigger file upload dialog
 */
const triggerFileUpload = (): void => {
  fileUploadInput.value?.click()
}

/**
 * Handle file selection
 */
const handleFileSelect = async (event: Event): Promise<void> => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file || !course.value) return

  isUploading.value = true

  try {
    const response = await adminUploadCourseFile(course.value.course_id, file, {
      file_category: 'material'
    })

    // Check for duplicate
    if (response.already_exists) {
      alert(response.message || `Datei "${file.name}" ist bereits für diesen Kurs vorhanden.`)
    }

    await loadCourseFiles()
  } catch (err: any) {
    console.error('Error uploading file:', err)
    alert('Fehler beim Hochladen: ' + (err.response?.data?.error || err.message))
  } finally {
    isUploading.value = false
    // Reset input
    if (target) target.value = ''
  }
}

/**
 * Delete a course file
 */
const deleteCourseFile = async (file: CourseFile): Promise<void> => {
  if (!course.value) return

  const confirmed = confirm(`Möchten Sie die Datei "${file.display_name || file.file_name}" wirklich löschen?`)
  if (!confirmed) return

  try {
    await adminDeleteCourseFile(course.value.course_id, file.course_file_id)
    await loadCourseFiles()
  } catch (err: any) {
    console.error('Error deleting file:', err)
    alert('Fehler beim Löschen: ' + (err.response?.data?.error || err.message))
  }
}

/**
 * Format file size for display
 */
const formatFileSize = (bytes: number | null): string => {
  if (!bytes) return '–'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/**
 * Get category label in German
 */
const getCategoryLabel = (category: CourseFileCategory): string => {
  const labels: Record<CourseFileCategory, string> = {
    script: 'Skript',
    material: 'Material',
    exercise: 'Übung',
    solution: 'Lösung',
    reference: 'Referenz',
    template: 'Vorlage',
    other: 'Sonstiges'
  }
  return labels[category] || category
}

/**
 * Get file type icon
 */
const getFileIcon = (fileType: string): string => {
  const icons: Record<string, string> = {
    pdf: '📄',
    docx: '📝',
    pptx: '📊',
    xlsx: '📈',
    txt: '📃',
    image: '🖼️',
    video: '🎬',
    audio: '🎵',
    archive: '📦',
    other: '📎'
  }
  return icons[fileType] || '📎'
}

/**
 * Handle chapter-updated event from AdminKapitelEditorWindow
 */
const handleChapterUpdated = () => {
  console.log('chapter-updated event received, reloading chapters...')
  loadCourseChapters()
}

// Lifecycle
onMounted(async () => {
  await loadCourse()
  if (course.value) {
    // Load files and chapters in parallel
    await Promise.all([
      loadCourseFiles(),
      loadCourseChapters()
    ])
  }

  // Event-Listener für Kapitel-Updates (aus dem Editor-Window)
  window.addEventListener('chapter-updated', handleChapterUpdated)
})

onUnmounted(() => {
  // Event-Listener entfernen
  window.removeEventListener('chapter-updated', handleChapterUpdated)
})
</script>

<style scoped>
/* ============================================ */
/* HERO SECTION - Ultra-Kompakt                */
/* ============================================ */
.hero-section {
  min-height: 100px;
}

.hero-background {
  height: 100%;
}

/* ============================================ */
/* SYNCHRONIZED ANIMATED GRADIENTS             */
/* Alle Gradients laufen perfekt synchron      */
/* ============================================ */

/* Shared animation keyframes */
@keyframes gradient-shift-sync {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

/* Hero Gradient - kräftige Farben */
.animated-gradient {
  background: linear-gradient(
    135deg,
    #7c3aed 0%,
    #ec4899 25%,
    #8b5cf6 50%,
    #06b6d4 75%,
    #7c3aed 100%
  );
  background-size: 400% 400%;
  animation: gradient-shift-sync 12s ease infinite;
}

/* Section Header Gradient - Light Mode */
.animated-header-gradient {
  background: linear-gradient(
    90deg,
    rgba(236, 72, 153, 0.25) 0%,
    rgba(139, 92, 246, 0.25) 25%,
    rgba(99, 102, 241, 0.25) 50%,
    rgba(6, 182, 212, 0.2) 75%,
    rgba(236, 72, 153, 0.25) 100%
  );
  background-size: 400% 400%;
  animation: gradient-shift-sync 12s ease infinite;
}

/* Section Header Gradient - Dark Mode (kräftig wie Hero!) */
.dark .animated-header-gradient {
  background: linear-gradient(
    90deg,
    rgba(124, 58, 237, 0.6) 0%,
    rgba(236, 72, 153, 0.6) 25%,
    rgba(139, 92, 246, 0.6) 50%,
    rgba(6, 182, 212, 0.5) 75%,
    rgba(124, 58, 237, 0.6) 100%
  );
  background-size: 400% 400%;
  animation: gradient-shift-sync 12s ease infinite;
}

/* Hero Buttons */
.hero-btn-primary {
  transition: all 0.3s ease;
}

.hero-btn-primary:hover {
  transform: translateY(-2px);
}

.hero-btn-secondary {
  transition: all 0.3s ease;
}

.hero-btn-secondary:hover {
  transform: translateY(-2px);
  background-color: rgba(255, 255, 255, 0.25);
}

/* ============================================ */
/* STAT CARDS - Modern Style                   */
/* ============================================ */
.stat-card {
  text-align: left;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  border-color: rgba(124, 58, 237, 0.2);
}

/* Dark mode stat card hover */
:deep(.dark) .stat-card:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  border-color: rgba(139, 92, 246, 0.3);
}

/* ============================================ */
/* ACTION BUTTONS                              */
/* ============================================ */
.action-btn {
  transition: all 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

/* Subtle gradient animation for KI buttons */
.animate-gradient-subtle {
  background-size: 200% 200%;
  animation: gradient-shift-subtle 4s ease infinite;
}

@keyframes gradient-shift-subtle {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* ============================================ */
/* CHAPTER LIST                                */
/* ============================================ */
.chapter-item .rotate-180 {
  transform: rotate(180deg);
}

/* ============================================ */
/* UTILITY CLASSES                             */
/* ============================================ */

/* Line clamp for description */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Animate spin for loader */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* ============================================ */
/* RESPONSIVE ADJUSTMENTS                      */
/* ============================================ */
@media (max-width: 768px) {
  .hero-section {
    min-height: 220px;
  }

  .stat-card:hover {
    transform: none;
  }
}

/* ============================================ */
/* DARK MODE ENHANCEMENTS                      */
/* ============================================ */
@media (prefers-color-scheme: dark) {
  .animated-gradient {
    opacity: 0.9;
  }
}
</style>
