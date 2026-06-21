import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  expect: {
    timeout: 8_000
  },
  fullyParallel: false,
  reporter: [["list"]],
  use: {
    baseURL: "http://127.0.0.1:5179",
    trace: "retain-on-failure"
  },
  webServer: [
    {
      command: "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000",
      cwd: "../api",
      url: "http://127.0.0.1:8000/docs",
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        AGENT_BACKEND: "deterministic",
        AGENT_DRAFT_BACKEND: "deterministic",
        DASHSCOPE_API_KEY: "",
        QWEN_MODEL: "",
        RUN_LIVE_QWEN_SMOKE: "0"
      }
    },
    {
      command: "npm.cmd run dev -- --port 5179 --strictPort --force",
      url: "http://127.0.0.1:5179",
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        VITE_API_BASE_URL: "http://127.0.0.1:8000"
      }
    }
  ],
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ]
});
