// frontend/eslint.config.cjs
// ESLint Flat Config (v9+)
// CommonJS bewusst (package.json ist ESM via "type":"module")

const globals = require("globals");

const req = (m) => {
  const mod = require(m);
  return mod && mod.default ? mod.default : mod;
};

const tseslint = req("typescript-eslint");
const vuePlugin = req("eslint-plugin-vue");
const vueParser = require("vue-eslint-parser");

const toArray = (x) => (Array.isArray(x) ? x : x ? [x] : []);

module.exports = [
  // -----------------------------------------------------
  // Global ignores
  // -----------------------------------------------------
  {
    ignores: [
      "**/node_modules/**",
      "**/dist/**",
      "**/.vite/**",
      "**/.vite/deps/**",
      "**/coverage/**",
      "**/*.min.*",

      // tooling/config
      "**/eslint.config.*",
      "**/vite.config.*",
      "**/vitest.config.*",
      "**/postcss.config.*",
      "**/tailwind.config.*",

      // TS configs können Comments haben -> nicht linten
      "**/tsconfig*.json",

      // scripts
      "scripts/**"
    ],
  },

  // -----------------------------------------------------
  // Base globals for JS/TS/Vue
  // -----------------------------------------------------
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts,vue}"],
    languageOptions: {
      globals: { ...globals.browser, ...globals.node },
    },
  },

  // -----------------------------------------------------
  // TypeScript recommended (non-blocking) - nur für TS/JS
  // -----------------------------------------------------
  ...toArray(tseslint.configs?.recommended).map((cfg) => ({
    ...cfg,
    files: ["**/*.{js,mjs,cjs,ts,mts,cts}"],
    rules: {
      ...(cfg.rules || {}),
      "@typescript-eslint/no-explicit-any": "off",  // TODO: Enable later, 527 violations to fix
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-empty-object-type": "warn",
      "@typescript-eslint/no-unsafe-function-type": "warn",
    },
  })),

  // -----------------------------------------------------
  // Vue files - mit vue-eslint-parser
  // -----------------------------------------------------
  {
    files: ["**/*.vue"],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
        ecmaVersion: "latest",
        sourceType: "module",
        extraFileExtensions: [".vue"],
      },
    },
    plugins: {
      vue: vuePlugin,
      "@typescript-eslint": tseslint.plugin,
    },
    rules: {
      // TypeScript rules for Vue files
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],

      // Vue recommended rules (subset)
      "vue/no-ref-as-operand": "warn",
      "vue/no-unused-vars": ["warn", { ignorePattern: "^_" }],
      "vue/no-mutating-props": "warn",  // TODO: Fix prop mutations then set to error
      "vue/require-v-for-key": "error",
      "vue/no-use-v-if-with-v-for": "error",

      // Format/Style Noise runterdrehen
      "vue/html-self-closing": "off",
      "vue/multiline-html-element-content-newline": "off",
      "vue/attributes-order": "off",
      "vue/first-attribute-linebreak": "off",
      "vue/html-indent": "off",
      "vue/max-attributes-per-line": "off",
      "vue/singleline-html-element-content-newline": "off",
      "vue/multi-word-component-names": "off",
    },
  },

  // -----------------------------------------------------
  // Override unused-vars for ALL files to ensure _ prefix works
  // Also allow common Vue patterns (t from useI18n, props, emit)
  // -----------------------------------------------------
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts,vue}"],
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "warn",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^(_|t$|props$|emit$)",
          caughtErrorsIgnorePattern: "^_"
        },
      ],
    },
  },
];
