import puppeteer from "https://deno.land/x/puppeteer@9.0.1/mod.ts";

const opts = {
    headless: false,
    slowMo: 100,
    timeout: 10000
  };
const browser = await puppeteer.launch(opts);
const page = await browser.newPage();
await page.goto("https://example.com");
await page.screenshot({ path: "example.png" });

await browser.close();
