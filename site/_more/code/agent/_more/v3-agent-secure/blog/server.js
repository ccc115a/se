// 引入 Express 框架，用於建立 Web 伺服器
const express = require('express');
// 引入 SQLite3 資料庫驅動（詳細訊息模式）
const sqlite3 = require('sqlite3').verbose();
// 引入 body-parser 中介軟體，用於解析 HTTP 請求主體
const bodyParser = require('body-parser');
// 引入 path 模組，處理檔案路徑
const path = require('path');

// 建立 Express 應用程式實例
const app = express();
// 建立 SQLite 資料庫連線，資料庫檔案為 ./blog.db
const db = new sqlite3.Database('./blog.db');

// 設定 EJS 為範本引擎
app.set('view engine', 'ejs');
// 設定檢視範本目錄為目前檔案所在目錄下的 views 資料夾
app.set('views', path.join(__dirname, 'views'));
// 使用 body-parser 解析 URL 編碼的請求主體（用於表單提交）
app.use(bodyParser.urlencoded({ extended: true }));
// 設定 public 資料夾為靜態檔案目錄
app.use(express.static('public'));

// 初始化資料庫表格（序列化執行，確保表格在連線請求前建立）
db.serialize(() => {
  // 建立 posts 表格（若不存在），包含 id、title、content、created_at 四個欄位
  db.run(`
    CREATE TABLE IF NOT EXISTS posts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
});

// 路由：首頁 — 顯示所有文章（依建立時間遞減排列）
app.get('/', (req, res) => {
  db.all('SELECT * FROM posts ORDER BY created_at DESC', [], (err, posts) => {
    if (err) return res.send('Error: ' + err.message);
    // 使用 index 範本渲染，傳入 posts 資料
    res.render('index', { posts });
  });
});

// 路由：顯示單篇文章 — 根據文章 ID 查詢
app.get('/post/:id', (req, res) => {
  db.get('SELECT * FROM posts WHERE id = ?', [req.params.id], (err, post) => {
    if (err) return res.send('Error: ' + err.message);
    // 使用 post 範本渲染，傳入單筆 post 資料
    res.render('post', { post });
  });
});

// 路由：顯示新增文章頁面
app.get('/new', (req, res) => {
  res.render('new');
});

// 路由：建立新文章 — 從表單取得 title 和 content 後插入資料庫
app.post('/posts', (req, res) => {
  const { title, content } = req.body;
  // 使用參數化查詢防止 SQL 注入
  db.run('INSERT INTO posts (title, content) VALUES (?, ?)', [title, content], (err) => {
    if (err) return res.send('Error: ' + err.message);
    // 新增成功後重新導向回首頁
    res.redirect('/');
  });
});

// 路由：刪除文章 — 根據文章 ID 刪除
app.post('/delete/:id', (req, res) => {
  db.run('DELETE FROM posts WHERE id = ?', [req.params.id], (err) => {
    if (err) return res.send('Error: ' + err.message);
    res.redirect('/');
  });
});

// 設定伺服器監聽埠號為 3000
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Blog server running at http://localhost:${PORT}`);
});
