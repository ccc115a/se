// https://github.com/lucacasonato/deno-puppeteer

import puppeteer from "https://deno.land/x/puppeteer@5.5.1/mod.ts";

const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto("https://example.com");
await page.screenshot({ path: "./example.png" });

await browser.close();
