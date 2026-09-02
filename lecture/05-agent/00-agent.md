* agent: prompt=>context=>harness=>loop
    * https://gemini.google.com/app/1c7bb09d1cbdd4e6

## ccc: 請說明 agent, prompt, context, harness, loop engineering

在大型語言模型（LLM）開發與 AI 系統架構中，這五個概念各自扮演不同的核心角色，共同構成一個完整且能自主執防任務的 AI 系統：

* **Prompt（提示詞）：** 指導 AI 模型的**指令與基調**。它是輸入給 LLM 的核心文本，定義了 AI 的角色、任務目標、限制條件與輸出格式。
* **Context（上下文/語境）：** AI 在思考與回答時能存取的**資訊總和**。包含 Prompt、對話紀錄、外部檢索出的資料（如 RAG 載入的文本）以及工具執行的返回結果。LLM 的「上下文視窗（Context Window）」決定了它單次能處理的資訊總量。
* **Agent（代理人）：** 具備**目標導向與自主決策能力**的 AI 系統。它不僅能回答問題，還能拆解複雜任務、調用外部工具（如搜尋 API、執行程式碼）、感知環境並根據結果調整行為，以達成指定目標。
* **Harness（測試與運行框架/鞍具）：** 負責**封裝、控管與測試 AI** 的外部系統架構。就像馬鞍與轡頭（Harness）用來控制馬匹一樣，Harness 為 LLM/Agent 提供運行環境，負責輸入輸出攔截、安全過濾、日誌記錄、狀態追蹤以及自動化基準測試（Benchmarking）。
* **Loop Engineering（迴圈工程/迭代設計）：** 讓 AI 實現**自主思考與修正的運作機制**。透過架構設計（如 ReAct、Reflexion 等模式），讓 Agent 在「感知環境 $\rightarrow$ 思考決策 $\rightarrow$ 執行動作 $\rightarrow$ 觀察結果 $\rightarrow$ 再次思考」的閉環中反覆運作，直到達成目標或觸發終止條件。

---

### 各元件關係與運作架構

| 元件 | 主要職責 | 比喻 |
| --- | --- | --- |
| **Agent** | 全局大腦與決策者 | 執行任務的大廚 |
| **Prompt** | 工作指引與角色定義 | 食譜與顧客要求 |
| **Context** | 當前可用的所有資料 | 備料台上的食材與當前烹飪進度 |
| **Harness** | 安全控管與運行環境 | 廚房設施、安全開關與品管員 |
| **Loop Engineering** | 推進任務的循環流程 | 「試吃 $\rightarrow$ 調整火候 $\rightarrow$ 再試吃」的烹飪過程 |

## ccc: 更詳細的用 coding agent 來說明

以目前主流的 AI 寫程式工具（例如 **Cursor**、**Devin** 或 **GitHub Copilot Workspace**）為例，這五個核心概念如何協同完成一個「自動修復 Bug」的任務：

---

### 1. Agent（代理人）：寫程式的 AI 工程師

Agent 是具備**自主規劃與工具調用能力**的主體。在 Coding Agent 中，它不只會產生程式碼，還能：

* **拆解任務：** 將「修復 500 Error」拆解為：搜尋 Log $\rightarrow$ 定位 Bug $\rightarrow$ 修改程式碼 $\rightarrow$ 執行測試。
* **調用工具（Tool Use）：** 主動調用 Bash 執行檔、Git 指令、AST 分析器或 Terminal。

---

### 2. Prompt（提示詞）：任務指引與系統設定

Prompt 是引導模型思考方向的指令，在 Coding Agent 中通常分為兩層：

* **System Prompt（系統提示）：** 預先寫死在 Agent 內部的規則，例如：「你是一個資深的 Python 工程師。修改程式碼時必須遵循 PEP 8，且每次變更後都必須執行 `pytest` 驗證。」
* **User Prompt（使用者提示）：** 使用者輸入的具體需求，例如：「登入頁面傳回 500 error，請幫我修正 `auth.py` 中的 Bug。」

---

### 3. Context（上下文）：大腦當前的工作記憶

Context 是 LLM 在當前步驟思考時**所能看到的所有資訊總和**。由於 Context Window 有長度限制，Coding Agent 的關鍵技術之一就是 **Context Management**：

* **自動抓取的檔案內容：** 透過 RAG 或專案索引抓取與 `auth.py` 相關的函式定義。
* **歷史對話與步驟：** 過去幾次嘗試的記錄。
* **工具執行結果（Tool Output）：** 執行 Terminal 指令後的報錯訊息（StackTrace）。

---

### 4. Harness（測試與運行框架/鞍具）：控制與保護邊界

Harness 是包裹在 LLM 外層的**控制系統與執行環境**，負責提供 Agent 運作所需的「沙盒」與「防護欄」：

* **隔離沙盒（Sandbox）：** 在 Docker 或 VM 內執行 Agent 產生的指令，防止 Agent 意外刪除真實開發環境的檔案（如 `rm -rf /`）。
* **權限與安全過濾：** 限制 API 金鑰權限、攔截危險指令。
* **狀態追蹤與 Snapshot：** 紀錄每一次程式碼變更，支援自動 Rollback（回滾）。
* **自動化評測（Benchmarking Harness）：** 在 SWE-bench 等基準測試中，Harness 負責載入 Task、提供 Agent 執行環境，並在結束後跑單元測試驗證分數。

---

### 5. Loop Engineering（迴圈工程）：自我修正的閉環機制

這是讓 Coding Agent 從「一次性產生程式碼」升級為「能自己修到好」的核心架構。Loop Engineering 設計了 Agent 思考與執行的循環（如 **ReAct 模式** 或 **Reflexion 模式**）：

```
[進入 Loop] 
  │
  ├── 1. Thought (思考): 分析目前 Context，決定下一步要檢查 auth.py 的第 42 行
  ├── 2. Action (行動): 調用 Bash 工具執行 `pytest tests/test_auth.py`
  ├── 3. Observation (觀察): Harness 傳回測試結果：AssertionError: Expected 200 got 500
  ├── 4. Update Context (更新): 將報錯資訊寫入 Context
  │
  └── [判斷條件] 測試通過了嗎？
        ├── 否 ──> 帶著新的 Context 回到步驟 1 (繼續修復)
        └── 是 ──> 結束 Loop，向使用者回報修復完成

```

透過這種架構，Coding Agent 能夠在遭遇語法錯誤或測試失敗時，**自己讀取 Error Log 並進行第 2 次、第 3 次的嘗試與修正**，不需要人類手動複製貼上報錯訊息。

---

### 總結架構關係

| 元件 | 程式開發中的實體 | 運作職責 |
| --- | --- | --- |
| **Agent** | AI 程式碼編輯器的大腦 | 決定下一步要讀檔案、改程式碼還是跑測試 |
| **Prompt** | `.cursorrules` / System Rules | 規定 AI 寫程式的風格、禁用語法與思考規則 |
| **Context** | 系統當前打開的檔案與 Log | 決定 AI 寫程式時能「參考」到的程式碼範圍 |
| **Harness** | Docker 控制器 / 測試運算環境 | 提供安全的執行環境，防止毀損主機環境 |
| **Loop Engineering** | `while (!test_passed)` 運行機制 | 讓 AI 重複「寫 code $\rightarrow$ 跑測試 $\rightarrow$ 看 error $\rightarrow$ 改 code」直到通過 |

## ccc: 改用其他非 coding 的案例來說明

以一個「自動化旅遊規劃與訂房 Agent」（例如一個能幫你規畫日本行程並完成訂房與餐廳預約的 AI 助手）為例，這五個核心概念如何運作：

---

### 1. Agent（代理人）：專屬私人旅遊管家

Agent 是具備**目標導向與工具調用能力**的決策核心。它不只給出旅遊建議，還能：

* **拆解目標：** 將「規劃 5 天東京行程」拆解為：查詢機票時間 $\rightarrow$ 安排每日景點與路線 $\rightarrow$ 檢查飯店空房與預算 $\rightarrow$ 調用 API 進行預約。
* **工具調用（Tool Use）：** 主動連結 Google Maps API 算車程、連線 Booking.com 查房價、使用日曆 API 寫入行程。

---

### 2. Prompt（提示詞）：服務標準與顧客需求

Prompt 設定了 AI 的服務態度與任務範疇：

* **System Prompt（系統提示）：** 預先設定的管家原則，例如：「你是一位精通日本旅遊的專業管家。規劃行程必須考慮交通流暢度，單日移動時間不得超過 2 小時，且優先推薦評分 4.5 星以上的餐廳。」
* **User Prompt（使用者提示）：** 顧客的具體需求，例如：「幫我規劃 11 月賞楓 5 天 4 夜東京行程，預算 5 萬台幣，帶長輩同行，不要太趕。」

---

### 3. Context（上下文）：當前的行程企劃案與歷史紀錄

Context 是 AI 在決策時**眼前桌上擺放的所有資料**：

* **偏好與限制：** 長輩不能走太久、同行人數、總預算限制。
* **實時資料：** 剛透過 API 查到的「11 月飯店剩餘房價」與「紅葉預測情報」。
* **對話與執行紀錄：** 前幾步已經確定好的 Day 1 飯店與景點。

---

### 4. Harness（測試與運行框架/鞍具）：履約安全與交易防護欄

Harness 是外圍的控制系統，確保 AI 在存取外部 API 或消費時**不會失控**：

* **支付與金鑰安全：** 限制 AI 不能擅自調用超過指定額度的信用卡支付 API。
* **資料過濾與校正：** 當 API 回傳的飯店地址格式異常時，Harness 負責清理資料後才餵給 AI。
* **確認機制（Human-in-the-loop）：** 在最終按下「扣款訂房」按鈕前，強制跳出視窗要求使用者進行生物識別認證。

---

### 5. Loop Engineering（迴圈工程）：動態調整與排錯的運作循環

這是讓旅遊管家能「因應變化、自動修正」的決策機制：

```
[進入 Loop] 
  │
  ├── 1. Thought (思考): 預計預訂新宿某飯店，但先檢查預算與交通時間
  ├── 2. Action (行動): 調用 Booking API 查詢 11/15 的雙人房房價
  ├── 3. Observation (觀察): API 回傳「已滿房」或「房價超出單夜預算 50%」
  ├── 4. Update Context (更新): 將「該飯店不可用」與「最新房價」寫入 Context
  │
  └── [判斷條件] 行程與飯店都安排妥當了嗎？
        ├── 否 ──> 帶著新的 Context 回到步驟 1 (重新尋找上野或品川附近的備選飯店)
        └── 是 ──> 結束 Loop，輸出完整行程並請使用者確認扣款

```

透過這種循環，即使熱門景點突然休館、或是預定的飯店滿房，Agent 也能**自己看懂回傳的失敗訊息，並自動進行第 2 次、第 3 次的替代方案搜尋**，直到排出一份完美的行程。

---

### 總結架構關係

| 元件 | 旅遊管家案例中的實體 | 運作職責 |
| --- | --- | --- |
| **Agent** | 私人旅遊管家 AI | 決定下一步要查地圖、找飯店還是排餐廳 |
| **Prompt** | 「服務條款」與「顧客需求表」 | 定義排行程的原則（如：不能讓長輩走太累） |
| **Context** | 企劃白板（含預算、景點資料、對話紀錄） | 提供 AI 當下決策所需的即時資訊 |
| **Harness** | 刷卡額度限制與訂單確認防護網 | 防止 AI 誤刷卡、保護個人隱私與 API 安全 |
| **Loop Engineering** | 「尋找 $\rightarrow$ 碰撞客滿 $\rightarrow$ 換方案」的排班機制 | 遇到沒房或爆預算時，自動嘗試備案直到排成功 |

您希望針對哪一個非 coding 領域（如：醫療診斷、客服系統、金融投資分析）再做更深入的細節拆解嗎？

## ccc: 醫療診斷

以一個「臨床智慧診斷與治療建議 Agent」（例如輔助醫師進行複雜罕見疾病診斷、或在急診室進行傷患分級的 AI 醫療助手）為例，說明這五個概念如何協同運作：

---

### 1. Agent（代理人）：主治醫師的 AI 臨床助手

Agent 是具備**自主推理與醫療工具調用能力**的主體。它不只是給出常識性的健康諮詢，而是能主動輔助診斷：

* **拆解診斷任務：** 將「評估胸痛病患」拆解為：分析病歷 $\rightarrow$ 調用 PACS 系統讀取胸部 X 光 $\rightarrow$ 檢查抽血報告（心肌轉氨酶）$\rightarrow$ 交叉比對最新臨床指南 $\rightarrow$ 開立診斷建議。
* **工具調用（Tool Use）：** 主動連結 Hospital Information System (HIS) 電子病歷、調用醫療影像分析模組、查詢 PubMed 文獻庫或 drug-drug interaction（藥物交互作用）資料庫。

---

### 2. Prompt（提示詞）：臨床診療指引與安全界限

Prompt 設定了 AI 的醫德規範、思考邏輯與回應限制：

* **System Prompt（系統提示）：** 預先寫入的醫療準則，例如：「你是一位輔助急診醫師的 AI 臨床專家。診斷時必須優先排除高致死率疾病（如主動脈剝離、急性心肌梗塞）。所有處方建議必須符合 2026 最新 AHA 指南，並標明實證醫學等級。」
* **User Prompt（使用者提示）：** 醫師輸入的主訴與現場狀況，例如：「55 歲男性，突發性撕裂樣胸痛延伸至背部，血壓 180/100 mmHg，請評估可能診斷與下一步檢查建議。」

---

### 3. Context（上下文）：病歷檔案與即時監測數據

Context 是 AI 在進行臨床推理時，**當前病房與病歷系統中的動態資料總和**：

* **患者結構化資料：** 過去病史（高血壓）、過敏史（對 Penicillin 過敏）、生理徵象（心跳、血壓、血氧）。
* **檢驗與影像回傳結果：** 剛完成的 D-Dimer 血液檢查數值、CT 斷層掃描報告文本。
* **對話與推論歷程：** 前幾輪評估中已排除的疾病（如心電圖無 ST 段上升，排除典型 STEMI 心肌梗塞）。

---

### 4. Harness（測試與運行框架/鞍具）：醫療安全防護網與 HIPAA 合規層

在醫療領域，Harness 是**絕對不能少的安全護欄**，負責隔離風險並確保醫療合規（Compliance）：

* **患者隱私脫敏（De-identification）：** 在將病歷 Context 傳送給 LLM 前，Harness 自動過濾掉姓名、身分證字號等 HIPAA 敏感資訊。
* **安全邊界與劑量過濾：** 當 Agent 建議的開藥劑量超過安全極限（例如計算錯體重導向藥量過高），Harness 的硬性規則層（Rule-based Engine）會直接攔截並發出警報。
* **醫師確認機制（Human-in-the-Loop）：** AI 產生的任何診斷或處方建議，Harness 都會強制設定為「待醫師簽核」狀態，嚴禁 AI 直接發送指令給藥局或執行醫療行為。

---

### 5. Loop Engineering（迴圈工程）：鑑別診斷與臨床推理循環

醫療診斷很少能「一步到位」，通常是透過鑑別診斷（Differential Diagnosis）不斷蒐集新證據並修正推論。Loop Engineering 設計了這個臨床邏輯閉環：

```
[進入 Loop] 
  │
  ├── 1. Thought (思考): 病患胸痛且血壓極高，需排除主動脈剝離與心肌梗塞。
  ├── 2. Action (行動): 調用 HIS API 檢查心電圖與 Troponin 報告，並請求主動脈 CT 攝影。
  ├── 3. Observation (觀察): 心電圖無異常，但主動脈 CT 回傳報告顯示「升主動脈內膜撕裂」。
  ├── 4. Update Context (更新): 將「CT 確認 Type A 主動脈剝離」寫入 Context，排除心肌梗塞。
  │
  └── [判斷條件] 診斷是否明確且緊急處置方案已完成？
        ├── 否 ──> 帶著新的 Context 回到步驟 1 (繼續思考手術會診與降血壓藥物組合)
        └── 是 ──> 結束 Loop，輸出「A 型主動脈剝離」緊急警告，提供降血壓藥物建議並提示召集心臟外科團隊

```

透過這種循環，當初期的檢驗結果不符合預期（例如血液指標正常）時，Agent 能**自動重新評估其他的可能性，建議下一步該補做哪些檢查**，直到鎖定真正病因。

---

### 總結架構關係

| 元件 | 醫療診斷案例中的實體 | 運作職責 |
| --- | --- | --- |
| **Agent** | 臨床智慧診斷助手 | 決定下一步要讀取病歷、建議檢查項目還是比對醫學文獻 |
| **Prompt** | 醫療倫理與臨床指南 (Guidelines) | 規定 AI 的診斷原則（如優先排除高致死率疾病） |
| **Context** | 患者的電子病歷 (EMR) 與當前檢驗報告 | 提供 AI 當下做鑑別診斷所需的全部臨床數據 |
| **Harness** | HIPAA 個資防護網與開藥劑量安全護欄 | 確保個資不外洩、攔截危險處方並強制要求醫師簽核 |
| **Loop Engineering** | 鑑別診斷的迭代推理機制 | 重複「提出假設 $\rightarrow$ 查驗報告 $\rightarrow$ 排除/確認 $\rightarrow$ 調整方案」 |

## ccc: 法律訴訟

以一個「法律訴訟與電子發現（e-Discovery）AI 代理系統」（例如輔助訴訟律師進行開庭準備、案件分析與書狀起草的 AI 助手）為例，說明這五個概念如何協同運作：

---

### 1. Agent（代理人）：訴訟律師的 AI 法務助理

Agent 是具備**自主規劃、法律推理與工具調用能力**的主體。在法律訴訟中，它不只是解答法條，更能處理複雜的訴訟流程：

* **拆解訴訟任務：** 將「準備民事答辯狀」拆解為：研讀原告起訴狀 $\rightarrow$ 搜尋歷史判例庫（如司法院裁判書）$\rightarrow$ 標註關鍵爭點與時效性 $\rightarrow$ 自動起草答辯狀初稿。
* **調用工具（Tool Use）：** 主動調用法規資料庫 API（如 Westlaw、LexisNexis、司法院系統）、開庭日曆 API、或內部卷宗檔的向量檢索系統（RAG）。

---

### 2. Prompt（提示詞）：訴訟策略與律師倫理準則

Prompt 設定了 AI 的角色、論述風格與嚴格的法律原則：

* **System Prompt（系統提示）：** 預先設定的法務規範，例如：「你是一位精通台灣民事訴訟法的 AI 助理。回答必須基於中華民國現行法規與最高法院最新判例。若遇到法條爭議，必須同時列出肯認說與否定說，且**絕對不可編造**不存在的判決字號（避免 AI 幻覺）。」
* **User Prompt（使用者提示）：** 律師輸入的訴訟交辦，例如：「原告主張本件求償權已過消滅時效，請調閱當事人提供的 Line 對話紀錄，分析是否有『承認』或『中斷時效』的抗辯事實。」

---

### 3. Context（上下文）：案件卷宗與證據資料庫

Context 是 AI 在進行法律推理時**當前能存取的所有訴訟卷宗總和**：

* **案件卷宗與證物（Evidence）：** 原告訴狀、合約書 PDF、對話紀錄截圖、證人逐字稿。
* **檢索到的判例（Precedents）：** 剛透過 API 搜尋到的 3 則同類型的最高法院裁判書全文。
* **審理進度與對話歷程：** 當前訴訟進行到第幾次準備程序、法官指示的舉證事項。

---

### 4. Harness（測試與運行框架/鞍具）：保密護欄與保密特權（Attorney-Client Privilege）

在法律領域，Harness 負責防範**律師保密義務外洩、利益衝突**與**虛假判例**等致命風險：

* **資安與隱私隔離（Privilege-Safe Architecture）：** 保證傳入模型的所有訴訟資料都不會被用於訓練公開模型，並符合 GDPR / 密件防護標準。
* **判例真偽驗證網（Hallucination Guardrail）：** 在 AI 輸出引用的裁判字號（如「112 年台上字第 1234 號」）時，Harness 的外圍程式會自動去官方資料庫查驗，若查無此案則立即攔截並提示修正。
* **律師最終覆核（Human-in-the-Loop）：** 所有產出的答辯狀草稿或訴訟分析，Harness 都會強制標示為「待律師簽署」，未經律師審閱核可前，嚴禁自動發送給法院或對造。

---

### 5. Loop Engineering（迴圈工程）：證據檢視與答辯攻防循環

訴訟充滿攻防變化，Loop Engineering 讓 Agent 能透過「攻防攻防」的反覆推演，產出最完善的訴訟策略：

```
[進入 Loop] 
  │
  ├── 1. Thought (思考): 分析原告攻防，原告主張損害賠償，但我方可主張「與有過失」。
  ├── 2. Action (行動): 調用卷宗檢索工具，搜尋對手提供的診斷證明與現場監視器畫面。
  ├── 3. Observation (觀察): 發現原告在事故發生時有違規闖紅燈之事實（錄影第 02:15 處）。
  ├── 4. Update Context (更新): 將「原告違規闖紅燈」的關鍵證據與《民法》第 217 條寫入 Context。
  │
  └── [判斷條件] 答辯邏輯是否完整且具備法條與證據支撐？
        ├── 否 ──> 帶著新的 Context 回到步驟 1 (繼續尋找是否有其他免責或減輕事由)
        └── 是 ──> 結束 Loop，產出包含「與有過失折抵賠償金額」的答辯狀初稿供律師審閱

```

透過這種循環，Agent 能在面對數千頁的巨量訴訟卷宗時，**自動反覆比對法條、判例與證物，甚至扮演對造律師進行「模擬攻防」**，找出隱藏的法律爭點。

---

### 總結架構關係

| 元件 | 法律訴訟案例中的實體 | 運作職責 |
| --- | --- | --- |
| **Agent** | AI 訴訟法務助理 | 決定下一步要檢索判例、研讀證物還是起草書狀 |
| **Prompt** | 律師倫理規範與辦案指引 | 規定 AI 必須嚴格依據真實判例、遵循訴訟法程序 |
| **Context** | 案件全部卷宗、證物與搜尋到的判例 | 提供 AI 撰寫答辯狀與分析爭點時所需的所有證據 |
| **Harness** | 律師保密特權防護網與判例真實性查驗器 | 確保訴訟機密不外洩、攔截虛構判例，並要求律師親簽 |
| **Loop Engineering** | 訴訟攻防與證據比對的迭代推演 | 重複「提出攻防主張 $\rightarrow$ 尋找證物判例 $\rightarrow$ 檢視漏洞 $\rightarrow$ 完善論述」 |

## ccc: 解析 openclaw agent 設計中的上述元素

OpenClaw（或 AutoClaw/NemoClaw 類型的開放式 Agent 框架）專為**自動化網路爬蟲、數據抓取與 RPA 流程**設計。其系統設計精確將上述五個元素落地為具體的架構模組：

---

### 1. Agent（代理人）：自動化抓取與爬蟲大腦

* **角色定義：** 負責分析目標網頁結構、拆解爬取任務的決策核心。
* **實作機制：** 接收高階任務（如「抓取電商平台的歷史價格變動」），將其拆解為子步驟：繞過驗證碼 $\rightarrow$ 模擬點擊 $\rightarrow$ 滾動載入數據 $\rightarrow$ 解析 DOM $\rightarrow$ 儲存資料庫。

### 2. Prompt（提示詞）：導航指令與解析規則

* **System Prompt：** 定義 Agent 的網頁操作原則，如「優先使用最省流量的 API 存取；若無 API 則切換至視覺（Vision/Computer Use）模式操作；遇到 Cloudflare 驗證時切換策略」。
* **User Prompt：** 具體抓取目標，如「請連至 `example.com` 抓取前 5 頁的商品名稱與價格」。

### 3. Context（上下文）：動態網頁狀態與 DOM 樹

* **資料範疇：** 包括當前的網頁 HTML/DOM 樹摘要、螢幕截圖（Vision Context）、已抓取到的 JSON 數據，以及 Cookies/Session 狀態。
* **上下文管理：** 由於完整的 DOM 樹非常巨大，OpenClaw 會透過「DOM 樹剪裁（Tree Pruning）」或語意壓縮，只保留可點擊元件（如 `<button>`, `<a>`）與關鍵文字，以節省 Token 視窗。

### 4. Harness（測試與運行框架/鞍具）：Playwright / Selenium 安全沙盒

* **隔離環境：** 封裝了無頭瀏覽器（Headless Browser，如 Playwright、Puppeteer）、代理伺服器（Proxy Rotation）與抗爬蟲偵測模組。
* **安全與頻率護欄：** 限制請求頻率（Rate Limiting），防止被目標網站封鎖 IP；設有超時（Timeout）與重試限制，避免無限等待。
* **人類干預（Human-in-the-Loop）：** 遇到極複雜的真人驗證（CAPTCHA）時，Harness 會暫停並彈出畫面讓人工手動輸入，通過後再交還權限給 Agent。

### 5. Loop Engineering（迴圈工程）：動態應對網頁變化的執行閉環

OpenClaw 依賴強大的 **Observation $\rightarrow$ Action** 閉環機制來應對動態網頁：

```
[進入 Loop] 
  │
  ├── 1. Thought: 發現「下一頁」按鈕點擊後頁面無反應，判斷資料為動態 AJAX 載入。
  ├── 2. Action: 調用 Playwright 工具執行 `page.evaluate('window.scrollTo(0, document.body.scrollHeight)')`
  ├── 3. Observation: 畫面更新，DOM 樹出現新的 `.product-item` 節點。
  ├── 4. Update Context: 將新出現的 20 筆商品資料追加至 Context 中。
  │
  └── [判斷條件] 已達到指定的 5 頁抓取量？
        ├── 否 ──> 帶著新 Context 回到步驟 1 (繼續向下滾動或尋找翻頁鈕)
        └── 是 ──> 結束 Loop，將結果匯出為 CSV/JSON

```

---

### OpenClaw 各元件職責總覽

| 元件 | OpenClaw 系統中的具體實現 | 解決的核心問題 |
| --- | --- | --- |
| **Agent** | 網頁自動化規劃器 | 將複雜的爬蟲需求自動轉換為操作步驟 |
| **Prompt** | 爬蟲邏輯與邊界設定 | 指導模型如何優先選用高效的 DOM 操作方式 |
| **Context** | 剪裁後的 DOM 樹、截圖與 Session | 讓 AI 能夠「看懂」當前網頁處於什麼狀態 |
| **Harness** | Playwright 沙盒、IP 代理池、驗證碼過濾器 | 防止 IP 被封、隔離瀏覽器環境並確保安全執行 |
| **Loop Engineering** | 「滾動/點擊 $\rightarrow$ 觀察 DOM 變化 $\rightarrow$ 修正選擇器」閉環 | 解決動態網頁、反爬機制與頁面渲染延遲的問題 |

## ccc: openclaw 不只抓網頁，請再次分析

OpenClaw 是一個**全功能自主 AI 助理（Self-Hosted Autonomous Executive Assistant）**。它透過通訊軟體（如 Telegram、Slack、Discord）作為互動介面，具備直接操控本地系統 Terminal、檔案系統、瀏覽器與外部 API 的能力。

---

### 1. Agent（代理人）：全域執行的大腦（Executive Brain）

OpenClaw 的 Agent 不僅僅是「網頁爬蟲」，而是一個**常駐在伺服器/本地設備上的個人執行官**：

* **目標路由：** 分析使用者透過 Telegram、Slack 發送的自然語言指令，將其拆解為「系統操作（Shell）」、「網路操作（Browser）」、「檔案處理（FS）」或「API 呼叫（Skills）」。
* **主動式執行（Proactive Execution）：** 能結合 Cron 機制主動發起任務（例如「每早 8 點檢查伺服器健康狀態並傳送報告至 Slack」），無須人類即時對話觸發。

---

### 2. Prompt（提示詞）：系統邊界與技能定義（SOPS & Skills）

* **System Prompt：** 設定 Agent 的身份、權限邊界（如禁用某些危險指令）、輸出格式約束，以及思考架構（ReAct 模式）。
* **Skill Prompts：** OpenClaw 的核心特色在於模組化的 **Skills** 機制。每個技能（如操作 Jira、執行 Bash、調用 API）都由一段 Prompt 描述其調用條件與輸入/輸出規格，引導模型準確選擇工具。

---

### 3. Context（上下文）：跨領域的長期記憶與狀態流動

OpenClaw 處理的 Context 遠超出單一網頁，它整合了**跨工具與跨時間的狀態資料**：

* **Multi-Modal Context：** 包含視訊/截圖（Computer Use）、Terminal 的 `stdout`/`stderr` 輸出、本地檔案內容，以及與使用者的通訊歷史。
* **Long-Term Memory（長期記憶）：** 透過向量資料庫或本地檔案系統（如 Markdown 筆記、向量檢索）紀錄用戶偏好、過去任務履歷與系統憑證資訊，讓 Agent 在重啟後仍具備上下文記憶。

---

### 4. Harness（測試與運行框架/鞍具）：Gateway 與系統防護欄

Harness 是 OpenClaw 能安全操控實體主機的核心封裝層：

* **Gateway（通訊網關與會話管理）：** 封裝 Telegram、Slack、Discord 等 SDK，將不同通訊管道的訊息統一標準化後輸入給 LLM，並管理多用戶 Session。
* **Execution Sandbox（沙盒與權限控管）：** 執行 Bash 命令時的隔離環境（Docker / Restricted Shell），避免 AI 執行 `rm -rf /` 或毀損主機。
* **Rate-Limiting & Approval Guardrails：** 當 Agent 擬執行敏感操作（如付款、發送對外 Email、刪除資料庫）時，Harness 會阻斷流程並透過通訊軟體發送確認按鈕（Human-in-the-Loop）。

---

### 5. Loop Engineering（迴圈工程）：自我修復與多工具協同閉環

OpenClaw 的核心價值在於跨系統的自適應修復能力（Self-Healing Loop）：

```
[進入 Loop] 
  │
  ├── 1. Thought: 收到指令「部署最新程式碼並確認服務上線」。決定先跑 Git Pull 與 Shell 部署指令。
  ├── 2. Action: 調用 Shell Skill 執行 `git pull && docker-compose up -d`
  ├── 3. Observation: Terminal 回傳錯誤：Port 8080 is already in use
  ├── 4. Update Context: 將「8080 埠位衝突」寫入 Context，調整策略為尋找佔用進程或更改 Port
  ├── 5. Re-Action: 調用 Shell 工具執行 `lsof -i :8080` 並終止衝突進程，再次重試部署
  │
  └── [判斷條件] 部署成功且 HTTP Status 200？
        ├── 否 ──> 帶著新 Context 回到步驟 1 (繼續除錯)
        └── 是 ──> 調用 Telegram API 發送「部署完畢」通知給使用者，結束 Loop

```

---

### 全功能 OpenClaw 元件架構對照

| 元件 | OpenClaw 的真實實作 | 運作職責 |
| --- | --- | --- |
| **Agent** | 自主執行大腦 (LLM Agent Core) | 決策、規劃與跨系統（Shell/Browser/API）工具調用 |
| **Prompt** | System Rules & Skill Definitions | 定義行為準則、指令集與各項技能的觸發規範 |
| **Context** | 視訊截圖 + Terminal Log + 長期向量記憶 | 整合全系統狀態，讓 AI 理解當前整體環境 |
| **Harness** | Local Gateway + Docker/Shell 隔離與權限閘門 | 銜接通訊平台、提供安全的執行沙盒並進行高風險指令攔截 |
| **Loop Engineering** | 「感知 Terminal/網頁/API $\rightarrow$ 決策 $\rightarrow$ 執行 $\rightarrow$ 遇錯自動修復」閉環 | 讓 AI 能自主排除系統異常，完成端到端的複雜工作流程 |
