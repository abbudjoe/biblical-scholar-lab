import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  use: { baseURL: "http://127.0.0.1:4173", trace: "retain-on-failure" },
  webServer: {
    command: "cd .. && uv run python tests/support/vs01_web_server.py --port 4173",
    url: "http://127.0.0.1:4173/",
    reuseExistingServer: false,
    timeout: 30_000,
  },
  reporter: "list",
});
