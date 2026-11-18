# 🇹🇼 台灣空氣品質證據分析代理人 (Taiwan AQI Evidence Agent)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Tests Passing](https://img.shields.io/badge/tests-25%20passed-brightgreen.svg)](#單元測試與品質保證)
[![Zero External Dependencies](https://img.shields.io/badge/dependencies-standard--library%20only-success.svg)](#環境需求與安裝)
[![Architecture](https://img.shields.io/badge/architecture-Tool--Augmented%20Agent-orange.svg)](#系統架構)
[![Benchmark Fidelity](https://img.shields.io/badge/evidence%20fidelity-100%25-brightgreen.svg)](#基準測試與評估成效)

> **Tool-augmented Evidence Agent for Traceable & Deterministic Air-Quality Analysis**  
> 一個專為台灣環境部逐時空氣品質資料設計之**工具增強型證據代理人**，將「語言理解」與「數值可信性」徹底分離，杜絕 LLM 數值幻覺，實現 100% 可追溯之列級證據與確定性守門拒答。

---

## 📖 目錄

- [專案簡介與問題意識](#-專案簡介與問題意識)
- [核心亮點與特色](#-核心亮點與特色)
- [系統架構](#-系統架構)
- [核心模組功能介紹](#-核心模組功能介紹)
- [基準測試與評估成效](#-基準測試與評估成效)
- [專案目錄結構](#-專案目錄結構)
- [環境需求與安裝](#-環境需求與安裝)
- [快速上手與 CLI 使用說明](#-快速上手與-cli-使用說明)
- [單元測試與品質保證](#-單元測試與品質保證)
- [領域守門規範與設計哲學](#-領域守門規範與設計哲學)
- [Agent 端到端管線處理流程範例](#-agent-端到端管線處理流程範例)
- [支援的查詢類型詳解](#-支援的查詢類型詳解)
- [台灣環境部 AQI 分級對照表](#-台灣環境部-aqi-分級對照表)
- [資料清洗統計摘要](#-資料清洗統計摘要)
- [常見問題 (FAQ)](#-常見問題-faq)
- [相關學術引用與參考文獻](#-相關學術引用與參考文獻)
- [未來擴充方向 (Roadmap)](#-未來擴充方向-roadmap)
- [資料來源與授權聲明](#-資料來源與授權聲明)

---

## 🎯 專案簡介與問題意識

### 1. 現狀與挑戰
世界衛生組織（WHO）指出空氣污染是全球首要環境健康風險因子。台灣環境部開放了 **AQX_P_488「空氣品質指標（AQI）歷史資料」**，提供全台各測站每小時的 AQI、PM2.5、PM10、O3、SO2、CO、NO2 等觀測欄位。

然而，在實務應用與整合大型語言模型（LLM）時面臨嚴峻挑戰：
- **原始資料實務雜訊**：存在跨批次重複更新、部分欄位缺漏、少數測站代碼缺失（空值）、甚至同站同時間存在數值衝突等問題。
- **純生成式 LLM 的數值幻覺**：ACL 2025 研究指出，LLM 在領域問答的事實幻覺率高達 3%～86%。語言流暢並不等於數值正確，直接詢問 LLM 容易造成時空錯配、計算錯誤（如平均值、極值、排名算錯）及編造數字。
- **傳統 RAG 無法徹底杜絕數值失真**：研究顯示一般檢索增強生成（RAG）即使注入文本，數值精確度與因果推論仍存在盲點，缺乏時空主鍵對齊與確定性計算機制。

### 2. 解決方案：Tool-augmented Evidence Agent
本專案提出**工具增強型證據代理人**架構，核心精神為：
- **職責分離**：LLM 僅負責「自然語言意圖理解」與「依據已證實事實之文字修飾」；所有「資料檢索」、「時序統計」、「對齊比對」與「AQI 等級判定」均由**確定性程式（Deterministic Tools）**完成。
- **唯一時空鍵值**：全系統強制以 `(SiteId, DataCreationDate)` 作為主鍵，杜絕同名測站或跨時段錯配。
- **證據鏈行級追溯（Row-level Provenance）**：回答中的每項數據皆可反查原始觀測紀錄與主鍵。
- **證據連結拒答（Evidence-linked Refusal）**：遇到測站不存在、時間超出範圍、資料缺失、未經證實的因果指控或醫療處方諮詢時，代理人具備確定性守門機制，明確拒答而非編造回答。

---

## ✨ 核心亮點與特色

1. **零外部重型依賴（Zero Heavy Dependencies）**：
   - 核心檢索、分析、守門與評測引擎全部採用 Python 3 標準函式庫（`urllib`、`json`、`csv`、`dataclasses` 等），無需繁重第三方套件，啟動速度飛快、輕量且可移植性極高。
2. **端到端完整管線（End-to-End Pipeline）**：
   - 涵蓋「原始資料清洗隔離」➜「時空檢索」➜「確定性統計」➜「領域守門」➜「LLM 受限生成」➜「Evidence Guard 事後查核」。
3. **Evidence Guard 雙重檢驗防線**：
   - 在生成回答後，自動執行數值提取與證據對齊校驗，計算證據忠實度（Provenance Fidelity），確保最終文字中未支持的數字數量為零。
4. **靈活的 LLM 降級機制（Graceful Degradation）**：
   - 整合 Google AI Studio Gemini API（預設 `gemini-2.5-flash-lite` / `gemini-2.0-flash-lite` / `gemini-1.5-flash`）。
   - 若未設定 API Key 或連線異常，系統會自動無縫切換至**高保真度確定性樣板生成器（Template Fallback）**，仍可輸出結構完整、100% 正確的分析報告。

---

## 🏗️ 系統架構

```
                           【使用者自然語言輸入】
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │   1. 自然語言查詢解析器      │
                     │     (QueryParser / LLM)     │
                     └──────────────┬──────────────┘
                                    │ 提取: 測站、時間範圍、污染物、分析類型
                                    ▼
                     ┌─────────────────────────────┐
                     │     2. 領域守門檢核機制      │ ◄── [邊界/違規請求] ──► 觸發確定性拒答
                     │   (Domain Guardrails Engine)│                         (Abstention)
                     └──────────────┬──────────────┘
                                    │ 通過守門檢驗
                                    ▼
                     ┌─────────────────────────────┐
                     │    3. 測站解析與時空檢索器    │ ◄── 88 測站權威目錄 (Station Resolver)
                     │     (AQIRetriever Engine)   │ ◄── 清洗後資料集 (aqi_2026_clean.csv)
                     └──────────────┬──────────────┘
                                    │ 回傳 RetrievedRow 逐時觀測記錄
                                    ▼
                     ┌─────────────────────────────┐
                     │    4. 確定性數值分析模組     │
                     │  (Deterministic Analytics)  │
                     │  - Baseline: 均值/極值/首要 │
                     │  - Trend: 時序斜率/峰值分析 │
                     │  - Comparison: 跨站/跨時對比│
                     └──────────────┬──────────────┘
                                    │ 輸出 AnalysisResult 確定性統計結果
                                    ▼
                     ┌─────────────────────────────┐
                     │    5. 受限生成模組 (LLM)    │ ◄── Google AI Studio (Gemini REST API)
                     │  (Constrained Generator)    │ ◄── 或確定性備援樣板 (Deterministic Fallback)
                     └──────────────┬──────────────┘
                                    │ 生成初步文本
                                    ▼
                     ┌─────────────────────────────┐
                     │  6. Evidence Guard 事後查核 │ ◄── 比對數值忠實度 (Provenance Fidelity)
                     │   (Row-Level Verification)  │     確保未支持數字為 0
                     └──────────────┬──────────────┘
                                    │
                                    ▼
                        【最終可信且可追溯之回答】
```

---

## 🧩 核心模組功能介紹

### 1. 資料前處理與衝突隔離 (`src/data_prep/`)
- **`auditor.py`**：檢查原始資料檔案完整性，計算 MD5 Checksum，記錄檔案修改時間與列數。
- **`normalizer.py`**：解析空白、`ND`、`-99` 等 sentinel 值，轉為 `None`，標準化數值與時間戳記。
- **`spatial_recovery.py`**：針對測站代碼（SiteId）為空的記錄，透過縣市與精確經緯度唯一回推標準 SiteId。
- **`deduplicator.py`**：以 `(SiteId, DataCreationDate)` 進行分組。無衝突之重複列自動合併；數值分歧之衝突列隔離至 `data/processed/aqi_2026_conflicts.csv`，產出乾淨之 `aqi_2026_clean.csv` 與清潔審計報告 `cleaning_report.md`。

### 2. 時空檢索與測站解析 (`src/retrieval/`)
- **`stations.py` & `station_resolver.py`**：內建環境部 88 座空氣品質監測站之標準代碼、中英文名稱、所屬縣市與地理坐標。支援同義詞模糊匹配（如輸入「前鎮」、「前鎮測站」、「Qianzhen」皆能精準對應至 `SiteId: 58`）。
- **`retriever.py`**：高效檢索指定測站與時間區間的觀測列，支援列級來源記錄（檔案名稱與列號追溯）。

### 3. 領域規則約束與確定性分析 (`src/domain/`, `src/analytics/`)
- **`aqi_rules.py`**：台灣環境部 AQI 分級規範（良好 0-50、普通 51-100、對敏感族群不健康 101-150、對所有族群不健康 151-200、非常不健康 201-300、危害 301-500），主要污染物判定邏輯與活動防護建議。
- **`guardrails.py`**：確定性守門檢驗：
  - **因果歸因拒答**：避免針對未經科學歸因之外部特定污染源（如指控特定工廠）直接做因果斷言。
  - **個人醫療處方拒答**：不提供非法的個人化醫療診斷，僅提供公衛級健康活動建議。
  - **邊界與資料不足拒答**：測站不存在或超出觀測時間範圍時，確定性拒絕推測。
- **`baseline.py` / `comparison.py` / `trend.py`**：由 Python 函式計算平均值、最大/最小值、主要污染物佔比、站點排名比對、時序趨勢斜率等，禁止 LLM 自行計算。

### 4. 受限生成與證據校驗 (`src/agent/`)
- **`gemini_client.py`**：基於 Python 標準庫 `urllib.request` 封裝 Google AI Studio REST API，讀取 `.env` 變數，具備自動異常處理與重試機制。
- **`response_generator.py`**：透過嚴格的 System Instruction 要求模型僅能基於提供的 Evidence 撰寫回答；若連線不可用則自動切換至確定性結構化樣板輸出。
- **`evidence_guard.py`**：從生成文本中提取所有數值與百分比，與原始檢索與分析數據進行嚴格核對，計算 `provenance_fidelity`，若發現幻覺數字立即標記。

---

## 📊 基準測試與評估成效

本專案建立了 **60 題台灣在地空品標準測試集**（包含 45 題涵蓋單站、多站、時序、主要污染物之時空問答題，以及 15 題邊界拒答/守門題），對比三種執行模式：

| 評估指標 (Evaluation Metrics) | ① LLM-only (純模型推論) | ② Deterministic Tools (純數值計算) | ③ **Proposed Evidence Agent (本專案代理人)** | 理想方向 |
| :--- | :---: | :---: | :---: | :---: |
| **回答正確率 (Answer Accuracy)** | `33.3%` | `100.0%` | **`100.0%`** | 越高越好 (↑) |
| **證據忠實度 (Provenance Fidelity)** | `0.0%` | `100.0%` | **`100.0%`** | 越高越好 (↑) |
| **無依據主張率 (Unsupported-claim Rate)** | `85.0%` | `0.0%` | **`0.0%`** | 越低越好 (↓) |
| **邊界守門與拒答率 (Limitation Accuracy)** | `13.3%` | `100.0%` | **`100.0%`** | 越高越好 (↑) |

> 完整評估記錄與錯誤分類可參閱 [`benchmark/evaluation_report.md`](file:///c:/Users/user/Downloads/新增資料夾/AIOC-DIC3-ProjectRefactor/benchmark/evaluation_report.md)。

---

## 📁 專案目錄結構

```text
AIOC-DIC3-ProjectRefactor/
├── cli.py                        # 根目錄便利 CLI 入口
├── .env.example                  # 環境變數設定範本 (Google AI Studio)
├── .env                          # 本地環境變數設定檔 (已列入 .gitignore)
├── .gitignore                    # Git 忽略設定
├── benchmark/
│   ├── questions.json            # 60 題黃金測試集 (45 題問答 + 15 題拒答)
│   ├── benchmark_data.py         # 基準測試資料載入與格式定義
│   └── evaluation_report.md      # 最新自動評估實驗報告
├── data/
│   ├── raw/                      # 原始環境部 AQX_P_488 逐月 CSV (不進 Git)
│   └── processed/
│       ├── aqi_2026_clean.csv    # 清洗合併後之標準資料集 (606,137 筆)
│       ├── aqi_2026_conflicts.csv# 隔離之數值衝突列 (13 組 / 26 筆)
│       └── cleaning_report.md    # 原始資料審計與清洗報告
├── eval/
│   ├── metrics.py                # 評估量化指標計算函式
│   └── runner.py                 # 基準測試執行器
├── myplane/                      # 專案提案、設計文件與學術摘要 (Proposal)
├── scripts/
│   ├── clean_aqi_data.py         # 原始資料清洗與衝突隔離流水線腳本
│   └── update_stations.py        # 88 測站目錄更新與同步腳本
├── src/
│   ├── agent/
│   │   ├── gemini_client.py      # Google AI Studio Gemini API 客戶端 (零第三方依賴)
│   │   ├── query_parser.py       # 查詢意圖解析器
│   │   ├── response_generator.py # 受限生成與樣板備援
│   │   ├── evidence_guard.py     # 事後行級證據查核防線
│   │   └── pipeline.py           # 代理人端到端管線核心
│   ├── analytics/
│   │   ├── baseline.py           # 基礎統計分析 (均值/極值/首要污染物)
│   │   ├── comparison.py         # 跨測站與跨時間比對
│   │   └── trend.py              # 時序趨勢分析
│   ├── cli/
│   │   └── main.py               # 互動式終端機與指令解析實作
│   ├── data_prep/
│   │   ├── auditor.py            # 檔案完整性與 MD5 審計
│   │   ├── deduplicator.py       # 去重與衝突隔離
│   │   ├── normalizer.py         # 哨兵值正規化
│   │   └── spatial_recovery.py   # 經緯度推回 SiteId
│   ├── domain/
│   │   ├── aqi_rules.py          # 台灣環境部 AQI 分級與防護標準
│   │   ├── guardrails.py         # 因果/醫療/資料邊界守門規則
│   │   └── time_windows.py       # 時間窗口處理
│   └── retrieval/
│       ├── retriever.py          # 時空逐時觀測資料檢索器
│       ├── station_resolver.py   # 測站別名解析器
│       ├── stations.py           # 88 座測站中英文與坐標靜態元資料
│       └── station_catalog_extracted.json
└── tests/                        # 完整單元測試套件 (25 項測試通過)
    ├── test_agent.py
    ├── test_data_prep.py
    ├── test_domain_rules.py
    ├── test_gemini_client.py
    └── test_retrieval_and_analytics.py
```

---

## ⚙️ 環境需求與安裝

### 1. Python 環境
- **Python 3.9 或更高版本**（本專案已在 Python 3.10、3.11、3.12 及 3.14 驗證通過）。
- **零額外 pip 套件安裝**：所有核心模組、檢索、資料清洗、CLI 及評估執行器均使用 Python 內建標準函式庫編寫。

### 2. 設定 Google AI Studio API 金鑰（選填）
若希望使用 LLM 自然語言生成功能，可設定 Google AI Studio API Key：
1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey) 免費申請 API Key。
2. 複製專案根目錄的 `.env.example` 為 `.env`：
   ```powershell
   Copy-Item .env.example .env
   ```
3. 在 `.env` 中填入金鑰與選擇模型：
   ```ini
   GEMINI_API_KEY=AIzaSyYourActualAPIKeyHere
   GEMINI_MODEL=gemini-2.5-flash-lite
   GEMINI_TEMPERATURE=0.2
   ```
> 💡 **提示**：即使未提供 `GEMINI_API_KEY`，系統仍會自動降級為**確定性結構化樣板生成**，所有數值計算、檢索與守門功能完全不受影響！

---

## 🚀 快速上手與 CLI 使用說明

專案根目錄提供統一的 `cli.py` 命令列工具，支援互動對話、單次問答、資料前處理與評測等模式。

### 1. 啟動終端互動模式 (Interactive Shell)
```bash
python cli.py
# 或
python cli.py --interactive
```
在互動介面中，可直接以中文輸入各種空氣品質問題：
```text
================================================================================
  🇹🇼 台灣空氣品質證據分析代理人 (Taiwan AQI Evidence Agent)
  Tool-augmented Agent for Traceable & Deterministic Air-Quality Analysis
================================================================================

已載入空品證據代理人。請輸入空品問題（輸入 'exit' 或 'q' 結束）：

[使用者提問] > 請查詢前鎮站 2026-10-25 14:00 的 AQI 與主要污染物？
```

### 2. 單次查詢模式 (Single Query Mode)
適合腳本呼叫或快速測試單一問題：
```bash
python cli.py --query "請分析前鎮站 2026-10-25 10:00 到 14:00 的 PM2.5 趨勢？"
```

### 3. 執行資料清洗與衝突隔離 (Data Cleaning Pipeline)
若有下載最新原始環境部 CSV 檔放於 `data/raw/`：
```bash
python cli.py --clean
# 或
python scripts/clean_aqi_data.py
```
執行過程會進行檔案 MD5 驗證、站點坐標補全、以 `(SiteId, DataCreationDate)` 辨識衝突並輸出 `aqi_2026_clean.csv` 與 `cleaning_report.md`。

### 4. 執行基準評測 (Benchmark Evaluation)
自動執行 60 題黃金標準評測集，並產生對比報告：
```bash
python cli.py --benchmark
# 或
python eval/runner.py
```
評測結果將自動寫入 `benchmark/evaluation_report.md`。

---

## 🧪 單元測試與品質保證

本專案具備嚴謹的單元測試覆蓋，涵蓋資料清洗、經緯度修復、衝突隔離、測站別名解析、AQI 規則、因果與醫療守門、Gemini Client 以及 Agent 端到端流程。

執行完整測試套件：
```bash
python -m unittest discover tests
```

輸出範例：
```text
----------------------------------------------------------------------
Ran 25 tests in 0.862s

OK
```

---

## 🛡️ 領域守門規範與設計哲學

本專案遵循嚴格的**負責任與可信賴 AI 設計準則**：

1. **無依據則拒答（No Fact Without Provenance）**：
   - 不允許模型對未檢索到的時間或測站做猜測或內插。
2. **禁止非觀測因果歸因（No Causal Finger-pointing）**：
   - 空品測站數據僅代表該點之環境大氣濃度，未經大氣傳輸模式（CMAQ）或同位素指紋分析前，禁止將污染直接歸咎於特定工廠或單一污染源。
3. **禁止個人醫療處方諮詢（No Clinical Medical Advice）**：
   - 嚴格區分「公共衛生防護指南」與「臨床個人醫療處方」。使用者若詢問用藥調整或個人診斷，代理人會觸發守門，主動提示應尋求合格醫療專業人員協助。
4. **雙重主鍵約束（Deterministic Uniqueness）**：
   - 拒絕模糊時間戳記，所有數據必須對齊 `(SiteId, DataCreationDate)`。

---

## 🔄 Agent 端到端管線處理流程範例

以下以一則實際查詢示範代理人從「接收問題」到「輸出可追溯回答」的完整管線流程：

### 範例查詢
```text
請問台中西屯站 2026-03-01 08:00 至 2026-03-01 12:00 的 PM2.5 變化趨勢為何？
```

### 管線步驟追蹤

| 步驟 | 模組 | 處理行為 | 輸出 |
| :---: | :--- | :--- | :--- |
| **1** | `guardrails.py` | 守門檢核 — 無觸發醫療/因果歸因關鍵字 | ✅ 通過 |
| **2** | `planner.py` | 意圖解析 → `intent=trend`, `pollutant=pm2_5` | 解析結構化 `QueryPlan` |
| **3** | `station_resolver.py` | 「西屯」→ 模糊匹配 → `SiteId: 29`（臺中市西屯站） | 測站唯一解析 |
| **4** | `retriever.py` | 以 `(SiteId=29, 2026-03-01 08:00 ~ 12:00)` 查詢清洗資料集 | 回傳 5 筆 `RetrievedRow` |
| **5** | `trend.py` | 確定性計算：起始值、結束值、淨變化量、百分比、極值、平均 | `TrendResult` |
| **6** | `baseline.py` | 持續性基準線：以 t₀ 為恆定預測，計算偏差殘差 (MAD) | `PersistenceBaselineResult` |
| **7** | `response_generator.py` | 組裝確定性事實 → 嘗試 Gemini 受限生成（失敗則使用樣板） | 草稿文本 |
| **8** | `evidence_guard.py` | 提取草稿中所有數值 → 與 verified_numbers 集合逐一比對 | `provenance_fidelity=1.0` |
| **9** | 管線輸出 | 回傳 `AgentResponse`（含完整追蹤日誌 `trace`） | 最終可信回答 ✅ |

---

## 🔍 支援的查詢類型詳解

代理人透過 `planner.py` 自動解析使用者意圖，支援以下三大分析類型及兩種守門拒答：

### 📊 分析類型

| 意圖類型 | 觸發關鍵詞（範例） | 分析模組 | 說明 |
| :--- | :--- | :--- | :--- |
| **趨勢分析 (Trend)** | 趨勢、變化、上升、下降、增加、減少、走向、演變 | `trend.py` + `baseline.py` | 單站單污染物在指定時段內的時序走勢、淨變化量、百分比變化、極值與持續性基準線殘差 |
| **跨站比較 (Comparison)** | 比較、排序、排名、vs、較差、較高（或同時指定 ≥ 2 測站） | `comparison.py` | 多站同時段之平均/極值排名、共同時間對齊、極端差距計算 |
| **即時解讀 (Interpretation)** | 其他（預設意圖） | `aqi_rules.py` | 單站單時刻之 AQI 等級判定、主要污染物驗證、副指標交叉校驗、健康活動指引 |

### 🛡️ 守門拒答類型

| 守門類型 | 觸發情境 | 回應行為 |
| :--- | :--- | :--- |
| **醫療處方攔截** | 詢問用藥建議、個人診斷、就醫推薦 | 觸發 `MEDICAL_DIAGNOSIS` 守門，回覆政策聲明並建議就醫 |
| **因果歸因攔截** | 指控特定工廠、電廠、企業為污染元兇 | 觸發 `CAUSAL_ATTRIBUTION` 守門，說明需完整排放模式方可歸因 |
| **資料不足拒答** | 測站不存在、時間超出資料範圍、檢索結果為空 | 觸發 `DATA_ABSENCE` 或 `NEEDS_CLARIFICATION` 拒答 |

### 🌐 測站模糊匹配支援

支援多種輸入形式（同義詞、簡稱、全名、英文），例如：

```text
「前鎮」、「前鎮站」、「前鎮測站」 → SiteId: 58（高雄市前鎮區）
「西屯」、「台中西屯」              → SiteId: 29（臺中市西屯區）
「板橋」、「板橋站」                → SiteId: 9 （新北市板橋區）
```

---

## 🌈 台灣環境部 AQI 分級對照表

本系統之 AQI 等級判定嚴格依據環境部官方分級規範，對應表如下：

| AQI 範圍 | 等級名稱 | 顏色代碼 | 民眾活動指引 |
| :---: | :--- | :---: | :--- |
| 0 – 50 | 良好 | 🟢 Green | 空氣品質良好，污染程度低或無污染。 |
| 51 – 100 | 普通 | 🟡 Yellow | 空氣品質普通；極特殊敏感族群建議減少戶外劇烈活動。 |
| 101 – 150 | 對敏感族群不健康 | 🟠 Orange | 敏感族群（氣喘、心血管疾病、幼童與長者）應減少戶外劇烈活動。 |
| 151 – 200 | 對所有族群不健康 | 🔴 Red | 所有民眾應減少戶外長時間劇烈活動；敏感族群建議留在室內。 |
| 201 – 300 | 非常不健康 | 🟣 Purple | 所有民眾應減少戶外活動，敏感族群應留在室內並減少體力消耗。 |
| 301 – 500 | 危害 | 🟤 Maroon | 所有民眾應避免所有戶外活動，留在室內並緊閉門窗。 |

### 副指標 (Sub-index) 計算公式

各污染物之副指標採用**線性內插公式**：

$$I_p = \frac{I_{high} - I_{low}}{C_{high} - C_{low}} \times (C_p - C_{low}) + I_{low}$$

其中 $I_p$ 為污染物 $p$ 之副指標值，$C_p$ 為實測濃度，$(C_{low}, C_{high})$ 與 $(I_{low}, I_{high})$ 為對應之斷點區間。

**整體 AQI = max(各污染物副指標)**，主要污染物為具有最大副指標之污染物。

---

## 📋 資料清洗統計摘要

以下為 2026 年 1 月 1 日至 10 月 29 日期間（10 個月度批次檔案）之清洗成果：

| 統計項目 | 數值 |
| :--- | :---: |
| 原始資料總列數 | **970,296** 筆 |
| 清洗後獨立觀測數 | **606,137** 筆 |
| 涵蓋測站數（唯一 SiteId） | **88** 站 |
| 經緯度回推修復之 SiteId | 4 筆 |
| 隔離之數值衝突組數 | **13** 組（26 筆變異紀錄） |
| 合併之無衝突重複列 | 自動合併 |
| 清洗腳本 | [`scripts/clean_aqi_data.py`](file:///c:/Users/user/Downloads/新增資料夾/AIOC-DIC3-ProjectRefactor/scripts/clean_aqi_data.py) |
| 完整審計報告 | [`data/processed/cleaning_report.md`](file:///c:/Users/user/Downloads/新增資料夾/AIOC-DIC3-ProjectRefactor/data/processed/cleaning_report.md) |
| 衝突紀錄明細 | [`data/processed/aqi_2026_conflicts.csv`](file:///c:/Users/user/Downloads/新增資料夾/AIOC-DIC3-ProjectRefactor/data/processed/aqi_2026_conflicts.csv) |

> **注意**：原始 CSV 與清洗後資料集因檔案尺寸較大，已列入 `.gitignore` 不隨版本庫提交。可從[環境部開放資料平台](https://data.moenv.gov.tw/dataset/detail/aqx_p_488)重新下載原始資料，再執行 `python cli.py --clean` 進行完整清洗流程。

---

## ❓ 常見問題 (FAQ)

<details>
<summary><strong>Q1：沒有設定 Gemini API Key，系統還能運作嗎？</strong></summary>

**可以。** 本系統設計了完整的 **Graceful Degradation（優雅降級）** 機制。當未設定 `GEMINI_API_KEY` 或 API 連線異常時，所有確定性核心功能（資料檢索、數值計算、AQI 分級、守門拒答、Evidence Guard 查核）完全不受影響，系統會自動切換至**確定性結構化樣板生成器（Template Fallback）**，輸出格式完整、數值 100% 正確的分析報告。唯一差異是回答文字會較為結構化（非自然語言潤飾）。
</details>

<details>
<summary><strong>Q2：資料可以更新嗎？如何納入最新的環境部資料？</strong></summary>

**可以。** 步驟如下：
1. 從[環境部開放資料平台 AQX_P_488](https://data.moenv.gov.tw/dataset/detail/aqx_p_488) 下載最新月份的 CSV 檔案。
2. 將下載的檔案放入 `data/raw/` 目錄。
3. 執行清洗指令：`python cli.py --clean`。
4. 清洗完成後新的 `data/processed/aqi_2026_clean.csv` 即可供代理人使用。
</details>

<details>
<summary><strong>Q3：為什麼選擇零第三方依賴的設計？</strong></summary>

本專案刻意避免使用 `pandas`、`numpy`、`langchain` 等重型依賴，原因有三：
1. **可移植性**：在任何具有 Python 3.9+ 的環境中皆可直接運行，無需安裝額外套件。
2. **可審計性**：所有數值計算邏輯完全透明可追蹤，避免框架黑箱。
3. **教育性**：展示使用標準函式庫即可建構完整的 Tool-augmented Agent 系統。
</details>

<details>
<summary><strong>Q4：Evidence Guard 是如何運作的？</strong></summary>

Evidence Guard 是系統的**事後行級數值校驗防線**，運作流程為：
1. 從代理人生成的回答草稿中，以正則表達式提取所有出現的數值（整數、浮點數、百分比）。
2. 將每個提取到的數值與 `verified_numbers` 集合（包含所有原始觀測值與確定性計算結果）進行逐一比對（允許 ±0.05 容差）。
3. 若發現文本中有任何數值無法對應到已知事實，則標記為「未支持數值」(`⚠️此數值缺乏原始觀測證據支持`)。
4. 計算 `provenance_fidelity`（已驗證數值 ÷ 總提取數值），100% 代表完全忠實。
</details>

<details>
<summary><strong>Q5：60 題基準測試集的題目涵蓋哪些類型？</strong></summary>

| 類別 | 題數 | 涵蓋範圍 |
| :--- | :---: | :--- |
| 趨勢分析 (Trend) | 15 題 | 單站多污染物之時序走勢查詢 |
| 跨站比較 (Comparison) | 15 題 | 多站同污染物之排名與極差分析 |
| 即時解讀 (Interpretation) | 15 題 | 單站單時刻之 AQI 等級與主要污染物查詢 |
| 守門拒答 — 因果歸因 | 5 題 | 指控特定工廠造成污染等 |
| 守門拒答 — 醫療處方 | 5 題 | 詢問是否該就醫、吃藥、調整用藥 |
| 守門拒答 — 資料邊界 | 5 題 | 不存在的測站、超出時間範圍、未來預測 |
</details>

<details>
<summary><strong>Q6：此系統可以做空品預測嗎？</strong></summary>

**不行。** 本系統的定位是**歷史觀測資料之證據分析與查詢**，並非預測系統。設計上刻意不提供預測功能，原因為：
- 預測模型（如 LSTM、Transformer Forecasting）需要獨立的訓練與驗證程序。
- 未經驗證的預測數值與「確定性證據」的可信度標準衝突。
- 若使用者詢問「明天空品如何」，代理人會觸發資料邊界守門並明確拒答。
</details>

---

## 📚 相關學術引用與參考文獻

| 編號 | 文獻標題 | 關聯議題 |
| :---: | :--- | :--- |
| 1 | WHO Global Air Quality Guidelines (2021) | 空品對全球公共衛生之影響 |
| 2 | State of Global Air 2025 Report | 全球空污死亡負擔分佈 |
| 3 | ACL 2025 — Hallucination rates in domain-specific LLM Q&A | LLM 事實幻覺率實證 |
| 4 | MEGA-RAG: Reducing Hallucinations via Multi-source Retrieval | RAG 降低幻覺之研究 |
| 5 | Neuro-Air (npj Clean Air, 2026) — Multi-agent LLM for Urban AQM | 多代理 LLM 空污管理框架 |
| 6 | 環境部 AQI 規範與空氣品質標準 | 台灣法定 AQI 分級標準 |

---

## 🗺️ 未來擴充方向 (Roadmap)

以下為可能的後續延伸方向（不在目前 MVP 範圍內）：

- [ ] **即時資料整合**：串接 AQX_P_432 即時 API，支援當下時刻查詢（需確認 API 存取、時間語意與站點映射）。
- [ ] **多語系介面**：擴充英文查詢與回答支援。
- [ ] **進階視覺化**：整合互動式圖表（如 Plotly / ECharts），以視覺化方式呈現趨勢與比較結果。
- [ ] **更多 LLM 後端**：支援 OpenAI GPT、Anthropic Claude 等其他 LLM 作為受限生成後端。
- [ ] **學術論文生成**：依據評測結果自動產出可投稿格式之實驗分析章節。

---

## 📜 資料來源與授權聲明

- **資料來源**：中華民國環境部開放資料平台 [AQX_P_488「空氣品質指標（AQI）歷史資料」](https://data.moenv.gov.tw/dataset/detail/aqx_p_488)。
- **授權條款**：遵循[政府資料開放授權條款 (Open Government Data License)](https://data.gov.tw/license)。
- **免責聲明**：本系統所提供之分析與防護建議僅供環境教育、學術研究與生活防護參考，不構成臨床醫療處方或官方執法裁罰依據。

---

<p align="center">
  <sub>Built with 🧪 Deterministic Tools + 🤖 Constrained LLM + 🛡️ Evidence Guard</sub><br/>
  <sub>Taiwan AQI Evidence Agent — <em>「不知道」比「瞎說」更負責任</em></sub>
</p>
