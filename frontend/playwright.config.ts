import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  timeout: 45000,
  reporter: [["list"]],
  use: {
    baseURL: process.env.LIVE_FRONTEND_URL || "https://uni-lang.vercel.app",
    trace: "on",
    video: "on",
    screenshot: "on",
    ignoreHTTPSErrors: true,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
