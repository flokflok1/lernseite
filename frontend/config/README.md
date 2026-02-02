# Frontend Configuration

Centralized build tool and development configuration files for the LernSystemX frontend.

## Configuration Files

### Build & Bundling

- **`vite.config.ts`** - Vite bundler configuration
  - Development server setup (host 0.0.0.0, port 5173)
  - API proxy configuration (proxies `/api/*` to backend at localhost:5000)
  - Path alias for `@` → `src/`

- **`vitest.config.ts`** - Vitest test runner configuration
  - Test environment setup (jsdom)
  - Coverage configuration (minimum 75% for lines, functions, branches, statements)
  - Path alias for `@` → `src/`

### TypeScript

- **`tsconfig.json`** - Main TypeScript configuration
  - Project references to `tsconfig.app.json` and `tsconfig.node.json`

- **`tsconfig.app.json`** - TypeScript config for application code
  - Compilation target: `esnext`
  - Module system: `esnext`

- **`tsconfig.node.json`** - TypeScript config for build tools/Node.js code
  - Used by Vite, Vitest, and other build tooling

### Styling

- **`tailwind.config.js`** - Tailwind CSS configuration
  - Utility class generation
  - Custom theme configuration

- **`postcss.config.js`** - PostCSS transformation pipeline
  - Tailwind CSS plugin
  - Other CSS transformations

## Usage

All configuration files in this directory are referenced from the frontend root via explicit `--config` flags in `package.json` scripts:

```bash
# Development
npm run dev          # Uses config/vite.config.ts

# Build
npm run build        # Uses config/vite.config.ts
npm run build:typecheck  # Uses config/tsconfig.json + config/vite.config.ts

# Testing
npm run test         # Uses config/vitest.config.ts
npm run test:watch   # Uses config/vitest.config.ts
npm run test:coverage # Uses config/vitest.config.ts
npm run test:ui      # Uses config/vitest.config.ts

# Type Checking
npm run typecheck    # Uses config/tsconfig.json
```

## Path Resolution

Configuration files use relative paths to reference each other and source directories:

- `../src/` - Refers to `frontend/src/`
- `../tests/` - Refers to `frontend/tests/`

These relative paths are resolved from the config file location (in the `config/` directory).

## Last Updated

2026-01-18
