#!/usr/bin/env node

/**
 * LernsystemX Frontend - Setup Check Script
 *
 * Überprüft die vollständige Frontend-Installation und -Konfiguration
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m',
  bold: '\x1b[1m'
};

const log = {
  success: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`),
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  header: (msg) => console.log(`\n${colors.bold}${colors.blue}${msg}${colors.reset}\n`)
};

let errorCount = 0;
let warningCount = 0;

function checkFileExists(filePath, description) {
  const fullPath = path.join(__dirname, filePath);
  if (fs.existsSync(fullPath)) {
    log.success(`${description}: ${filePath}`);
    return true;
  } else {
    log.error(`${description} fehlt: ${filePath}`);
    errorCount++;
    return false;
  }
}

function checkDirExists(dirPath, description) {
  const fullPath = path.join(__dirname, dirPath);
  if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
    log.success(`${description}: ${dirPath}`);
    return true;
  } else {
    log.error(`${description} fehlt: ${dirPath}`);
    errorCount++;
    return false;
  }
}

function checkFileContent(filePath, searchString, description) {
  const fullPath = path.join(__dirname, filePath);
  if (!fs.existsSync(fullPath)) {
    log.error(`Datei nicht gefunden: ${filePath}`);
    errorCount++;
    return false;
  }

  const content = fs.readFileSync(fullPath, 'utf-8');
  if (content.includes(searchString)) {
    log.success(`${description}`);
    return true;
  } else {
    log.warning(`${description} - nicht gefunden: "${searchString}"`);
    warningCount++;
    return false;
  }
}

function checkPackageJson() {
  log.header('📦 Package.json überprüfen');

  const pkgPath = path.join(__dirname, 'package.json');
  if (!fs.existsSync(pkgPath)) {
    log.error('package.json nicht gefunden!');
    errorCount++;
    return;
  }

  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf-8'));

  // Check dependencies
  const requiredDeps = {
    'vue': 'Vue 3',
    'pinia': 'Pinia State Management',
    'vue-router': 'Vue Router',
    'axios': 'Axios HTTP Client'
  };

  const requiredDevDeps = {
    'vite': 'Vite Build Tool',
    'typescript': 'TypeScript',
    'tailwindcss': 'TailwindCSS',
    '@vitejs/plugin-vue': 'Vite Vue Plugin'
  };

  log.info('Dependencies:');
  for (const [dep, name] of Object.entries(requiredDeps)) {
    if (pkg.dependencies && pkg.dependencies[dep]) {
      log.success(`  ${name} (${pkg.dependencies[dep]})`);
    } else {
      log.error(`  ${name} fehlt!`);
      errorCount++;
    }
  }

  log.info('Dev Dependencies:');
  for (const [dep, name] of Object.entries(requiredDevDeps)) {
    if (pkg.devDependencies && pkg.devDependencies[dep]) {
      log.success(`  ${name} (${pkg.devDependencies[dep]})`);
    } else {
      log.error(`  ${name} fehlt!`);
      errorCount++;
    }
  }

  // Check scripts
  log.info('Scripts:');
  const requiredScripts = ['dev', 'build', 'preview'];
  for (const script of requiredScripts) {
    if (pkg.scripts && pkg.scripts[script]) {
      log.success(`  npm run ${script}`);
    } else {
      log.error(`  Script fehlt: ${script}`);
      errorCount++;
    }
  }
}

function checkConfigFiles() {
  log.header('⚙️ Konfigurationsdateien überprüfen');

  checkFileExists('vite.config.ts', 'Vite Config');
  checkFileExists('tailwind.config.js', 'Tailwind Config');
  checkFileExists('postcss.config.js', 'PostCSS Config');
  checkFileExists('tsconfig.json', 'TypeScript Config');
  checkFileExists('tsconfig.app.json', 'TypeScript App Config');
  checkFileExists('.env', 'Environment Variables');

  // Check vite.config.ts for path alias
  checkFileContent('vite.config.ts', '@', 'Vite: Path Alias (@/) konfiguriert');

  // Check .env for API URL
  checkFileContent('.env', 'VITE_API_BASE_URL', 'Environment: API Base URL definiert');
}

function checkSourceStructure() {
  log.header('📁 Quellcode-Struktur überprüfen');

  // Check main directories
  checkDirExists('src', 'Source-Verzeichnis');
  checkDirExists('src/api', 'API-Verzeichnis');
  checkDirExists('src/store', 'Store-Verzeichnis');
  checkDirExists('src/router', 'Router-Verzeichnis');
  checkDirExists('src/layouts', 'Layouts-Verzeichnis');
  checkDirExists('src/pages', 'Pages-Verzeichnis');
  checkDirExists('src/components', 'Components-Verzeichnis');
  checkDirExists('src/components/ui', 'UI-Components-Verzeichnis');

  // Check page directories
  checkDirExists('src/pages/auth', 'Auth-Pages-Verzeichnis');
  checkDirExists('src/pages/dashboard', 'Dashboard-Pages-Verzeichnis');
}

function checkCoreFiles() {
  log.header('📄 Kern-Dateien überprüfen');

  // Main files
  checkFileExists('src/main.ts', 'Main Entry Point');
  checkFileExists('src/App.vue', 'Root Component');
  checkFileExists('src/style.css', 'Global Styles');

  // API
  checkFileExists('src/api/http.ts', 'HTTP Client');
  checkFileExists('src/api/auth.api.ts', 'Auth API Service');

  // Store
  checkFileExists('src/store/auth.store.ts', 'Auth Store');

  // Router
  checkFileExists('src/router/index.ts', 'Router Config');

  // Layouts
  checkFileExists('src/layouts/BaseLayout.vue', 'Base Layout');
  checkFileExists('src/layouts/AuthLayout.vue', 'Auth Layout');

  // UI Components
  checkFileExists('src/components/ui/Button.vue', 'Button Component');
  checkFileExists('src/components/ui/Input.vue', 'Input Component');
  checkFileExists('src/components/ui/Card.vue', 'Card Component');

  // Pages
  checkFileExists('src/pages/auth/LoginPage.vue', 'Login Page');
  checkFileExists('src/pages/auth/RegisterPage.vue', 'Register Page');
  checkFileExists('src/pages/dashboard/DashboardPage.vue', 'Dashboard Page');
  checkFileExists('src/pages/ProfilePage.vue', 'Profile Page');
  checkFileExists('src/pages/CoursesPage.vue', 'Courses Page');
  checkFileExists('src/pages/NotFoundPage.vue', 'NotFound Page');
}

function checkImportantContent() {
  log.header('🔍 Wichtige Code-Features überprüfen');

  // Check HTTP Client features
  checkFileContent('src/api/http.ts', 'Authorization', 'HTTP Client: JWT Auto-Injection');
  checkFileContent('src/api/http.ts', '401', 'HTTP Client: 401 Error Handling');
  checkFileContent('src/api/http.ts', 'interceptors', 'HTTP Client: Interceptors');

  // Check Auth Store features
  checkFileContent('src/store/auth.store.ts', 'defineStore', 'Auth Store: Pinia Store');
  checkFileContent('src/store/auth.store.ts', 'isAuthenticated', 'Auth Store: isAuthenticated Getter');
  checkFileContent('src/store/auth.store.ts', 'localStorage', 'Auth Store: LocalStorage Persistierung');

  // Check Router features
  checkFileContent('src/router/index.ts', 'beforeEach', 'Router: Navigation Guards');
  checkFileContent('src/router/index.ts', 'requiresAuth', 'Router: Auth Meta Field');

  // Check Tailwind setup
  checkFileContent('src/style.css', '@tailwind', 'Styles: Tailwind Directives');
  checkFileContent('tailwind.config.js', 'content', 'Tailwind: Content Paths konfiguriert');
}

function checkNodeModules() {
  log.header('📚 Node Modules überprüfen');

  if (fs.existsSync(path.join(__dirname, 'node_modules'))) {
    log.success('node_modules vorhanden');

    // Check if key packages are installed
    const keyPackages = ['vue', 'pinia', 'vue-router', 'axios', 'tailwindcss'];
    for (const pkg of keyPackages) {
      const pkgPath = path.join(__dirname, 'node_modules', pkg);
      if (fs.existsSync(pkgPath)) {
        log.success(`  ${pkg} installiert`);
      } else {
        log.error(`  ${pkg} nicht installiert!`);
        errorCount++;
      }
    }
  } else {
    log.error('node_modules nicht gefunden!');
    log.info('Führe "npm install" aus, um Dependencies zu installieren.');
    errorCount++;
  }
}

function checkWidgetSystem() {
  log.header('🎨 Widget-System (Phase F4) überprüfen');

  // Widget System Types & Config
  checkFileExists('src/types/widgets.ts', 'Widget Types');
  checkFileExists('src/config/widgetRegistry.ts', 'Widget Registry');

  // Dashboard Store
  checkFileExists('src/store/dashboard.store.ts', 'Dashboard Store');

  // Dashboard Components
  checkFileExists('src/components/dashboard/DashboardWidgetsArea.vue', 'Dashboard Widgets Area');
  checkFileExists('src/components/dashboard/WidgetConfigPanel.vue', 'Widget Config Panel');

  // Widget Components
  checkDirExists('src/components/dashboard/widgets', 'Widgets-Verzeichnis');
  checkFileExists('src/components/dashboard/widgets/WelcomeWidget.vue', 'Welcome Widget');
  checkFileExists('src/components/dashboard/widgets/ProfileSummaryWidget.vue', 'Profile Summary Widget');
  checkFileExists('src/components/dashboard/widgets/PlanTokensWidget.vue', 'Plan & Tokens Widget');
  checkFileExists('src/components/dashboard/widgets/EnrolledCoursesWidget.vue', 'Enrolled Courses Widget');
  checkFileExists('src/components/dashboard/widgets/CoursesProgressWidget.vue', 'Courses Progress Widget');
  checkFileExists('src/components/dashboard/widgets/OrgOverviewWidget.vue', 'Organisation Overview Widget');

  // Dashboard API
  checkFileExists('src/api/dashboard.api.ts', 'Dashboard API (prepared for backend)');

  // Check Widget Registry Content
  checkFileContent('src/config/widgetRegistry.ts', 'WIDGET_DEFINITIONS', 'Widget Registry: Definitions exportiert');
  checkFileContent('src/config/widgetRegistry.ts', 'getWidgetsForRole', 'Widget Registry: Role-Filter Funktion');

  // Check Dashboard Store Content
  checkFileContent('src/store/dashboard.store.ts', 'defineStore', 'Dashboard Store: Pinia Store');
  checkFileContent('src/store/dashboard.store.ts', 'visibleWidgets', 'Dashboard Store: visibleWidgets Getter');
  checkFileContent('src/store/dashboard.store.ts', 'loadLayout', 'Dashboard Store: loadLayout Action');
  checkFileContent('src/store/dashboard.store.ts', 'localStorage', 'Dashboard Store: LocalStorage Persistierung');
}

function checkDocumentation() {
  log.header('📖 Dokumentation überprüfen');

  checkFileExists('README.md', 'README');

  if (checkFileContent('README.md', 'LernsystemX Frontend', 'README: Projekt-Titel')) {
    checkFileContent('README.md', 'Installation', 'README: Installation Anleitung');
    checkFileContent('README.md', 'npm run dev', 'README: Dev-Server Anleitung');
    checkFileContent('README.md', 'Widget-System', 'README: Widget-System Dokumentation');
  }
}

function printSummary() {
  log.header('📊 Zusammenfassung');

  if (errorCount === 0 && warningCount === 0) {
    console.log(`${colors.green}${colors.bold}✓ Alle Checks erfolgreich!${colors.reset}`);
    console.log('\nDas Frontend ist korrekt eingerichtet und bereit für die Entwicklung.');
    console.log('\nNächste Schritte:');
    console.log('  1. Backend starten: cd ../backend && python run.py');
    console.log('  2. Frontend starten: npm run dev');
    console.log('  3. Browser öffnen: http://localhost:5173');
  } else {
    if (errorCount > 0) {
      console.log(`${colors.red}${colors.bold}✗ ${errorCount} Fehler gefunden!${colors.reset}`);
    }
    if (warningCount > 0) {
      console.log(`${colors.yellow}${colors.bold}⚠ ${warningCount} Warnungen${colors.reset}`);
    }

    console.log('\nBitte behebe die Fehler, bevor du fortfährst.');

    if (errorCount > 0) {
      process.exit(1);
    }
  }
}

// Main execution
function main() {
  console.log(`${colors.bold}${colors.blue}`);
  console.log('═══════════════════════════════════════════════════════');
  console.log('   LernsystemX Frontend - Setup Check Script');
  console.log('═══════════════════════════════════════════════════════');
  console.log(colors.reset);

  checkPackageJson();
  checkConfigFiles();
  checkSourceStructure();
  checkCoreFiles();
  checkImportantContent();
  checkWidgetSystem();
  checkNodeModules();
  checkDocumentation();
  printSummary();
}

main();
