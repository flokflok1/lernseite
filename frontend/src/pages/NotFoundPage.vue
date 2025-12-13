<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-primary-600 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-900 mb-4">Seite nicht gefunden</h2>
      <p class="text-gray-600 mb-8">
        Die von Ihnen gesuchte Seite existiert nicht.
      </p>
      <router-link to="/dashboard" class="btn btn-primary">
        Zurück zum Dashboard
      </router-link>
    </div>
  </div>
</template>
