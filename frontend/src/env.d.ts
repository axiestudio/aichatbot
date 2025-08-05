/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_DEBUG: string
  readonly VITE_DEFAULT_CONFIG_ID: string
  readonly VITE_ANALYTICS_ENABLED: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
