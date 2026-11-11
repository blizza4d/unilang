/**
 * record_demo.ts - Automated Playwright demo rehearsal and screen-capture driver.
 * Drives the exact 2.5-minute demo journey with deliberate pauses, simulated smooth cursor
 * movements, and sample file interactions.
 * 
 * Usage:
 *   npx ts-node scripts/record_demo.ts
 *   or:
 *   npx playwright test scripts/record_demo.ts --headed
 */

import { chromium, Page } from "@playwright/test";
import path from "path";

const TARGET_URL = process.env.DEMO_URL || "http://localhost:3000";
const DELIBERATE_PAUSE = 2500; // ms to pause for presentation clarity

async function smoothMove(page: Page, x: number, y: number, steps = 25) {
  await page.mouse.move(x, y, { steps });
}

async function runDemoJourney() {
  console.log(`[*] Launching automated demo journey at ${TARGET_URL}...`);
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100,
    args: ["--window-size=1920,1080", "--start-maximized"],
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: path.join(__dirname, "../docs/screenshots/recordings"),
      size: { width: 1920, height: 1080 },
    },
  });

  const page = await context.newPage();

  try {
    // 1. Landing View
    console.log("  [+] Step 1: Navigating to landing page...");
    await page.goto(TARGET_URL, { waitUntil: "networkidle" });
    await page.waitForTimeout(3000);

    // 2. Click Quick Sample (German Invoice with Math Error)
    console.log("  [+] Step 2: Selecting German sample invoice...");
    const sampleBtn = page.locator("button:has-text('German (Math Error)')").first();
    if (await sampleBtn.isVisible()) {
      const box = await sampleBtn.boundingBox();
      if (box) {
        await smoothMove(page, box.x + box.width / 2, box.y + box.height / 2);
        await page.waitForTimeout(800);
        await sampleBtn.click();
      }
    } else {
      // Fallback: upload sample file
      const samplePath = path.join(__dirname, "../samples/sample_de_math_error.pdf");
      const fileInput = page.locator('input[type="file"]');
      await fileInput.setInputFiles(samplePath);
    }

    // 3. Observe Pipeline Stages & Droid Animation
    console.log("  [+] Step 3: Observing pipeline stages and kinematic droid walk...");
    await page.waitForTimeout(4000);

    // 4. Verification of Math Error Alert
    console.log("  [+] Step 4: Inspecting flagged total discrepancy...");
    await page.waitForSelector("text=Needs Review", { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(DELIBERATE_PAUSE);

    // 5. Enter Review Mode
    console.log("  [+] Step 5: Toggling interactive Review Mode (Key: R)...");
    await page.keyboard.press("r");
    await page.waitForTimeout(1500);

    // 6. Demonstrate Grounding Hover
    console.log("  [+] Step 6: Demonstrating visual bounding-box grounding...");
    const totalField = page.locator("text=Total Amount").first();
    if (await totalField.isVisible()) {
      const box = await totalField.boundingBox();
      if (box) {
        await smoothMove(page, box.x + box.width / 2, box.y + box.height / 2);
        await page.waitForTimeout(2000);
      }
    }

    // 7. Open Batch Queue
    console.log("  [+] Step 7: Opening Batch Queue...");
    const batchBtn = page.locator("button:has-text('Batch')").first();
    if (await batchBtn.isVisible()) {
      await batchBtn.click();
      await page.waitForTimeout(2000);
      await page.keyboard.press("Escape");
    }

    // 8. Open Scoreboard Benchmark
    console.log("  [+] Step 8: Opening Benchmark Scoreboard...");
    const scoreBtn = page.locator("button:has-text('Scoreboard')").first();
    if (await scoreBtn.isVisible()) {
      await scoreBtn.click();
      await page.waitForTimeout(DELIBERATE_PAUSE);
      await page.keyboard.press("Escape");
    }

    // 9. Command Palette Demo
    console.log("  [+] Step 9: Opening Command Palette (Cmd/Ctrl+K)...");
    await page.keyboard.press("Control+k");
    await page.waitForTimeout(2000);
    await page.keyboard.press("Escape");

    console.log("[+] Demo journey executed successfully!");
    await page.waitForTimeout(3000);
  } catch (error) {
    console.error("[-] Demo rehearsal failed:", error);
  } finally {
    await context.close();
    await browser.close();
  }
}

if (require.main === module) {
  runDemoJourney().catch(console.error);
}

export { runDemoJourney };
