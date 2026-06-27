import { defineConfig, devices } from "@playwright/test";
import os from "node:os";
import path from "node:path";

const apiPort = Number.parseInt(process.env.PLAYWRIGHT_API_PORT ?? "8000", 10);
const webPort = Number.parseInt(process.env.PLAYWRIGHT_WEB_PORT ?? "5179", 10);
const apiBaseURL = process.env.VITE_API_BASE_URL ?? `http://127.0.0.1:${apiPort}`;
const webBaseURL = process.env.PLAYWRIGHT_BASE_URL ?? `http://127.0.0.1:${webPort}`;
const databaseURL =
  process.env.DATABASE_URL ??
  `sqlite:///${path
    .join(os.tmpdir(), `thousandmodels-v26-browser-release-evidence-${process.pid}.sqlite`)
    .replace(/\\/g, "/")}`;

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 60_000,
  expect: {
    timeout: 10_000
  },
  fullyParallel: false,
  reporter: [["list"]],
  use: {
    baseURL: webBaseURL,
    trace: "retain-on-failure"
  },
  webServer: [
    {
      command: `python -m uvicorn app.main:app --host 127.0.0.1 --port ${apiPort}`,
      cwd: "../api",
      url: `${apiBaseURL}/api/health`,
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        AGENT_BACKEND: "deterministic",
        AGENT_DRAFT_BACKEND: "deterministic",
        DASHSCOPE_API_KEY: "",
        DATABASE_URL: databaseURL,
        QWEN_MODEL: "",
        RUN_LIVE_QWEN_SMOKE: "0"
      }
    },
    {
      command: `npm.cmd run dev -- --port ${webPort} --strictPort --force`,
      cwd: ".",
      url: webBaseURL,
      reuseExistingServer: false,
      timeout: 120_000,
      env: {
        VITE_API_BASE_URL: apiBaseURL
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
