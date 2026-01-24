// eslint.config.cjs (Flat Config for ESLint v9+)
// CommonJS on purpose (project is ESM via package.json "type":"module")

const globals = require("globals");

const req = (m) => {
  const p = require(m);
  return p && p.default ? p.default : p;
};

const tseslint = req("typescript-eslint");
const pluginVue = req("eslint-plugin-vue");
const jsonPlugin = req("@eslint/json");
const importPlugin = req("eslint-plugin-import");

const toArray = (x) => (Array.isArray(x) ? x : [x]).filter(Boolean);

// Vue flat config (your plugin lists these keys)
const vueFlat =
  pluginVue.configs["flat/recommended"] ||
  pluginVue.configs["flat/essential"] ||
  pluginVue.configs["flat/base"];

// IMPORTANT: Vue rules MUST only apply to .vue, otherwise vue rules can crash on JSON
const vueConfigs = toArray(vueFlat).map((cfg) => {
  if (!cfg || typeof cfg !== "object" || Array.isArray(cfg)) return cfg;
  return cfg.files ? cfg : { ...cfg, files: ["**/*.vue"] };
});

// TS recommended flat configs
const tsConfigs = toArray(tseslint.configs?.recommended);

module.exports = [
  // -----------------------------
  // Ignore (replaces .eslintignore)
  // -----------------------------
  {
    ignores: ["node_modules/**", "dist/**", "build/**", "coverage/**", ".claude/**"],
  },

  // -----------------------------
  // Base globals
  // -----------------------------
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts,vue}"],
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
    },
  },

  // -----------------------------
  // TypeScript
  // -----------------------------
  ...tsConfigs,

  // -----------------------------
  // Vue
  // -----------------------------
  ...vueConfigs,

  // Enable TS parser inside <script lang="ts"> in .vue
  {
    files: ["**/*.vue"],
    languageOptions: {
      parserOptions: { parser: tseslint.parser },
    },
  },

  // -----------------------------
  // JSON (i18n etc.)
  // -----------------------------
  {
    files: ["**/*.json"],
    plugins: { json: jsonPlugin },
    language: "json/json",
    rules: {
      "json/no-duplicate-keys": "error",
    },
  },

  // =====================================================================
  // DDD / Clean Architecture boundaries (global)
  // =====================================================================
  {
    files: ["src/**/*.{js,ts,vue}"],
    plugins: { import: importPlugin },
    rules: {
      "import/no-restricted-paths": [
        "error",
        {
          zones: [
            // presentation must not touch infra/domain directly
            {
              target: "./src/presentation",
              from: "./src/infrastructure",
              message:
                "❌ presentation darf nicht aus infrastructure importieren. Nutze application als Gateway.",
            },
            {
              target: "./src/presentation",
              from: "./src/domain",
              message:
                "❌ presentation darf domain nicht direkt importieren. Nutze application layer.",
            },

            // domain must be framework + infra free
            {
              target: "./src/domain",
              from: "./src/infrastructure",
              message: "❌ domain muss infra-frei bleiben.",
            },
            {
              target: "./src/domain",
              from: "./src/presentation",
              message: "❌ domain darf nicht aus presentation importieren.",
            },
          ],
        },
      ],
    },
  },

  // =====================================================================
  // Hard bans (imports) - applies across src (incl. i18n json imports)
  // =====================================================================
  {
    files: ["src/**/*.{js,ts,vue,json}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/windows/**"],
              message: '❌ Ordnername "windows" ist überall verboten. Verwende "panels".',
            },
            {
              group: ["**/presentation/views/**", "@/presentation/views/**"],
              message:
                "❌ views ist deprecated. Migriere nach pages/** oder components/** (panels).",
            },
          ],
        },
      ],
    },
  },

  // =====================================================================
  // Legacy API root imports - only block in application + presentation
  // (infrastructure is allowed to use its internal http/client modules)
  // =====================================================================
  {
    files: ["src/{application,presentation}/**/*.{js,ts,vue}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: [
                "**/infrastructure/api/*.api*",
                "@/infrastructure/api/*.api*",
                "**/infrastructure/api/http*",
                "@/infrastructure/api/http*",
              ],
              message:
                "❌ Legacy API root imports. Nutze api/clients/** (ideal: via application/services/api/*).",
            },
          ],
        },
      ],
    },
  },

  // =====================================================================
  // Root-file policy (layer roots must contain ONLY folders, except index.ts)
  // =====================================================================
  {
    files: ["src/application/*.{ts,vue}"],
    ignores: ["src/application/index.ts"],
    rules: {
      "no-restricted-syntax": [
        "error",
        {
          selector: "Program",
          message:
            "❌ Keine Dateien direkt in src/application/ (außer index.ts). Lege sie in Subfoldern ab.",
        },
      ],
    },
  },
  {
    files: ["src/domain/*.{ts,vue}"],
    ignores: ["src/domain/index.ts"],
    rules: {
      "no-restricted-syntax": [
        "error",
        {
          selector: "Program",
          message:
            "❌ Keine Dateien direkt in src/domain/ (außer index.ts). Lege sie in Subfoldern ab.",
        },
      ],
    },
  },
  {
    files: ["src/infrastructure/*.{ts,vue}"],
    ignores: ["src/infrastructure/index.ts"],
    rules: {
      "no-restricted-syntax": [
        "error",
        {
          selector: "Program",
          message:
            "❌ Keine Dateien direkt in src/infrastructure/ (nur Subfolder).",
        },
      ],
    },
  },
  {
    files: ["src/presentation/components/*.{ts,vue}"],
    rules: {
      "no-restricted-syntax": [
        "error",
        {
          selector: "Program",
          message:
            "❌ Keine Dateien direkt in src/presentation/components/ (nur Subfolder).",
        },
      ],
    },
  },
  {
    files: ["src/presentation/pages/*.{ts,vue}"],
    rules: {
      "no-restricted-syntax": [
        "error",
        {
          selector: "Program",
          message:
            "❌ Keine Dateien direkt in src/presentation/pages/ (nur Subfolder).",
        },
      ],
    },
  },

  // =====================================================================
  // Refactor-friendly TS strictness (doesn't block you during migration)
  // =====================================================================
  {
    files: ["src/{application,presentation,infrastructure}/**/*.{ts,vue}"],
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
    },
  },
  {
    files: ["src/domain/**/*.ts"],
    rules: {
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
    },
  },

  // =====================================================================
  // Reduce Vue formatting noise (keep signal high while refactoring)
  // =====================================================================
  {
    files: ["**/*.vue"],
    rules: {
      "vue/attributes-order": "off",
      "vue/first-attribute-linebreak": "off",
      "vue/html-indent": "off",
      "vue/max-attributes-per-line": "off",
      "vue/singleline-html-element-content-newline": "off",
      "vue/html-self-closing": "off",
      "vue/html-closing-bracket-spacing": "off",
      "vue/require-default-prop": "off",
      "vue/multi-word-component-names": "off",
    },
  },
];
