import {ok} from 'https://deno.land/x/tdd/mod.ts'
import puppeteer from "https://deno.land/x/puppeteer/mod.ts";
var browser, page

const opts = {
  headless: false,
  slowMo: 100,
  timeout: 100000
};

Deno.test('Puppteer', async function() {
  browser = await puppeteer.launch(opts);
  page = await browser.newPage();

  var html;

  await page.goto('http://127.0.0.1:8000', {waitUntil: 'domcontentloaded'})
  html = await page.content()
  console.log('html=', html)
  let idx = html.indexOf('<p>You have <strong>0</strong> posts!</p>')
  console.log('idx=', idx)
  ok(idx >= 0)

  // console.log('test create post...')
  await page.click('#createPost')
  html = await page.content()
  ok(html.indexOf('<h1>New Post</h1>') >= 0)

  // console.log('test add post...')
  await page.focus('#title')
  await page.keyboard.type('aaa')
  await page.focus('#body')
  await page.keyboard.type('aaa')
  await page.click('#savePost')

  // console.log('we should have 1 post now...')
  html = await page.content()
  ok(html.indexOf('<p>You have <strong>1</strong> posts!</p>') >= 0)

  await page.click('#show0')
  html = await page.content()
  ok(html.indexOf('<h1>aaa</h1>') >= 0)

  await browser.close();
})

/*
Deno.test('start puppeteer', async function() {
  browser = await puppeteer.launch(opts);
  page = await browser.newPage();

})

Deno.test('GET / should see <p>You have <strong>0</strong> posts!</p>', async function() {
  await page.goto('http://127.0.0.1:8000', {waitUntil: 'domcontentloaded'})
  let html = await page.content()
  ok(html.indexOf('<p>You have <strong>0</strong> posts!</p>') >= 0)
})

Deno.test('close()', async function() {
  await browser.close();
})
*/
/*
  describe('puppeteer', function() {
    it('GET / should see <p>You have <strong>0</strong> posts!</p>', async function() {
    })
    it('click createPost link', async function() {
      await page.click('#createPost')
      let html = await page.content()
      ok(html.indexOf('<h1>New Post</h1>') >= 0)
    })
    it('fill {title:"aaa", body:"aaa"}', async function() {
      await page.focus('#title')
      await page.keyboard.type('aaa')
      await page.focus('#body')
      await page.keyboard.type('aaa')
      await page.click('#savePost')
    })
    it('should see <p>You have <strong>1</strong> posts!</p>', async function() {
      let html = await page.content()
      ok(html.indexOf('<p>You have <strong>1</strong> posts!</p>') >= 0)
    })
    it('should see <p>You have <strong>1</strong> posts!</p>', async function() {
      await page.click('#show0')
      let html = await page.content()
      ok(html.indexOf('<h1>aaa</h1>') >= 0)
    })
  })
})
*/