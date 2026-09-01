## UML 圖形建模

### PlantUML

> 參考: 
> 
> 1. [Cheetsheet -- PlantUML 的快速學習小抄](http://ogom.github.io/draw_uml/plantuml/)
> 2. http://plantuml.com/

### 使用個案

```puml
@startuml
left to right direction
actor 客戶接待
actor 客戶
rectangle 訂單建立 {
  客戶 -- (創建訂單)
  客戶 -- (檢查訂單)
  客戶 -- (修改訂單)
  客戶 -- (確認訂單)
  客戶接待 -up- (創建訂單)
  客戶接待 -up- (檢查訂單)
  客戶接待 -up- (修改訂單)
  客戶接待 -up- (確認訂單)
}

actor 倉庫管理員
actor 運送公司
actor 會計系統
actor 庫存系統
rectangle 訂單處理 {
  倉庫管理員 -- (寄送 email)
  倉庫管理員 -- (填寫產品)
  運送公司 -- (出貨運送)
  會計系統 -- (信用查核)
  會計系統 -- (收費)
  庫存系統 -- (檢查存貨)
}

@enduml
```

顯示結果

![](./img/UmlUseCase.png)

### 活動圖

有泳道 (Swimlane) 的活動圖：

```puml
@startuml
|Swimlane1|
start
:foo1;
|#AntiqueWhite|Swimlane2|
:foo2;
:foo3;
|Swimlane1|
:foo4;
|Swimlane2|
:foo5;
stop
@enduml
```

![](./img/UmlUseCaseSwimlane1.png)

更詳細的案例：

```puml
@startuml
|顧客|
  start
  :創建訂單;
|顧客接待|
  :檢查訂單;
fork
  |會計系統|
  :信用查核;
  if (信用良好?) then (是)
  else (否)
    |顧客接待|
    :拒絕訂單;
    stop
  endif
fork again
  |庫存系統|
  :檢查庫存;
  if (庫存足夠?) then (是)
  else (否)
    |倉庫管理員|
    :取消訂單;
    stop
  endif
end fork
|顧客|
  if (是否改單?) then (是)
    :修改訂單;
  else (否)
  endif
|顧客接待|
  :確認訂單;
|倉庫管理員|
  :貨品裝箱;
fork
  |倉庫管理員|
  :寄送郵件;
fork again
  |會計系統|
  :收費;
fork again
  |運送公司|
  :出貨運送;
  stop
end fork
|倉庫管理員|
  stop
@enduml
```

![](./img/UmlUseCaseSwimlane2.png)

### Markdown Preview Enhanced

此 VsCode 的插件支援 PlantUML 的立即檢視與匯出。

可以用 Ctrl-K-V 檢視某 .md 檔案，會顯示成排版後的網頁結果。

在該結果視窗按下滑鼠右鍵，會顯示功能表，按下 Save as Markdown 會將 xxx.md 另存為 xxx_.md，該檔案內的 puml 程式框就會被轉換為圖片存在 /assets/ 資料夾下。

我們可以用 vscode/Edit/Replace in Files 作全部檔案的字串取代，例如：

> ../assets/ 改為https://cccbook.github.io/sejs/docs/assets/

這樣就可以將檔案存回 github/wiki 並且能成功地顯示圖片。

### 問題

Save to Markdown 時會出現下列訊息:


Error: ImageMagick is required to be installed to convert svg to png.
Error: Command failed: convert C:\Users\user\AppData\Local\Temp\mume-svg118101-892-1lp46he.gyxnf.svg D:\course\sejs\docs\assets\d6faad89f84acb96eff9da79e3cb1e620.png
�ѼƵL�� - D:\course\sejs\docs\assets\d6faad89f84acb96eff9da79e3cb1e620.png

結果發現 convert 指令後來被取代掉了，而且 windows 裏的 convert 是 FAT => NTFS 的用途。

參考:

1. https://www.imagemagick.org/discourse-server/viewtopic.php?t=29582
2. http://www.imagemagick.org/Usage/windows/#convert_issue

這樣就沒辦法在 windows 裏正確使用 save markdown 的功能了。

以上問題是因為灌錯 markdown preview enhanced 了，要用 json roger 的這個版本 https://github.com/shd101wyy/vscode-markdown-preview-enhanced/releases

不能用 yiyi Wang 的版本。