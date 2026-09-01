PS C:\ccc\course\sa\se\08-verify\02-ajax\01-puppeteer> deno run -A --unstable PdfTest.js
error: Uncaught (in promise) Error: Protocol error (Page.printToPDF): PrintToPDF is not implemented
      this._callbacks.set(id, { resolve, reject, error: new Error(), method });
                                                        ^
    at https://deno.land/x/puppeteer@9.0.1/vendor/puppeteer-core/puppeteer/common/Connection.js:226:57
    at new Promise (<anonymous>)
    at CDPSession.send (https://deno.land/x/puppeteer@9.0.1/vendor/puppeteer-core/puppeteer/common/Connection.js:225:12)
    at Page.pdf (https://deno.land/x/puppeteer@9.0.1/vendor/puppeteer-core/puppeteer/common/Page.js:1406:39)
    at file:///C:/ccc/course/sa/se/08-verify/02-ajax/01-puppeteer/PdfTest.js:12:14