import puppeteer from "https://deno.land/x/puppeteer@9.0.1/mod.ts";

const opts = {
  headless: false,
  slowMo: 100,
  timeout: 10000
};
(async () => {
  const browser = await puppeteer.launch(opts);
  const page = await browser.newPage();
  await page.goto('https://news.ycombinator.com', {waitUntil: 'networkidle2'});
  await page.pdf({path: 'hn.pdf', format: 'A4'});

  await browser.close();
})();