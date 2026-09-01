# 安全性議題

## deno

* https://deno.land/x/snelm
    * https://github.com/denjucks/snelm

## 書

* https://nodesecroadmap.fyi/

## 文章
* https://medium.com/@nodepractices/were-under-attack-23-node-js-security-best-practices-e33c146cb87d
    1. Embrace linter security rules
    2. Limit concurrent requests using a middleware
    3. Extract secrets from config files or use packages to encrypt them
    4. Prevent query injection vulnerabilities with ORM/ODM libraries
    5. Avoid DOS attacks by explicitly setting when a process should crash
    6. Adjust the HTTP response headers for enhanced security
    7. Constantly and automatically inspect for vulnerable dependencies
    8. Avoid using the Node.js crypto library for handling passwords, use Bcrypt
    9. Escape HTML, JS and CSS output
    10. Validate incoming JSON schemas
    11. Support blacklisting JWT tokens
    12. Prevent brute-force attacks against authorization
    13. Run Node.js as non-root user
    14. Limit payload size using a reverse-proxy or a middleware
    15. Avoid JavaScript eval statements
    16. Prevent evil RegEx from overloading your single thread execution
    17. Avoid module loading using a variable
    18. Run unsafe code in a sandbox
    19. Take extra care when working with child processes
    20. Hide error details from clients
    21. Configure 2FA for npm or Yarn
    22. Modify session middleware settings
    23. Avoid DOS attacks by explicitly setting when a process should crash
    24. Prevent unsafe redirects
    25. Avoid publishing secrets to the npm registry
    26. A list of 40 generic security advice (not specifically Node.js-related)

* https://github.com/shieldfy/API-Security-Checklist
    * 中文版 -- https://github.com/shieldfy/API-Security-Checklist/blob/master/README-tw.md

## 套件

* https://github.com/lirantal/awesome-nodejs-security (讚!)

* https://nemethgergely.com/nodejs-security-overview/
    * https://github.com/venables/koa-helmet
    * https://www.npmjs.com/package/joi

* https://expressjs.com/en/advanced/best-practice-security.html
    * Don’t use deprecated or vulnerable versions of Express
    * Use TLS
    * Use Helmet
    * Use cookies securely : express-session (Don’t use the default session cookie name, Set cookie security options)
    * Prevent brute-force attacks against authorization
    * Ensure your dependencies are secure
    * Avoid other known vulnerabilities
    * Use csurf middleware to protect against cross-site request forgery (CSRF).
    * Always filter and sanitize user input to protect against cross-site scripting (XSS) and command injection attacks.
    * Defend against SQL injection attacks by using parameterized queries or prepared statements.
    * Use the open-source sqlmap tool to detect SQL injection vulnerabilities in your app.
    * Use the nmap and sslyze tools to test the configuration of your SSL ciphers, keys, and renegotiation as well as the validity of your certificate.
    * Use safe-regex to ensure your regular expressions are not susceptible to regular expression denial of service attacks.

* https://blog.usejournal.com/nodejs-application-security-80d5150a0366
    * npm install --save helmet 
    * npm install --save express-session
    * npm install cors --save
    * npm install csurf


* https://www.toptal.com/nodejs/secure-rest-api-in-nodejs
    * 對 password 加鹽加密

* https://goldbergyoni.com/checklist-best-practice-of-node-js-in-production/

* https://github.com/panva/jose
    * https://jwt.io/#debugger-io
* https://github.com/AdamPflug/express-brute
* https://github.com/llambda/koa-brute
* https://www.npmjs.com/package/koa2-ratelimit


