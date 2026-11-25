# 🎓 ICEIB Academic Paper: OpenSpec & A-to-Z Writing SOP 對齊手冊

本文件規範 **ICEIB（International Conference on Environmental Informatics and Biotechnology）** 研討會論文在 **OpenSpec** 體系下的章節規格與 **A-to-Z 學術寫作 SOP（`A2Z.docx`）** 的 1:1 對應關係。

---

## 🏛️ 一、IEEE ICEIB 研討會論文核心章節架構

依據 ICEIB 大會要求與官方 IEEE 雙欄會議標準格式（`IEEEtran.cls`），整篇論文共劃分為以下核心章節：

| 章節序號 | IEEE 論文標準章節 | A-to-Z SOP 對應階段 | 核心研究內涵與驗證標的 |
|---|---|---|---|
| **—** | **Abstract（論文摘要）** | **A ～ F** | 6 段式微型論文：動機 (A)、挑戰 (B)、解藥 (C)、方法 (D)、實驗 (E)、發現 (F) |
| **Section I** | **Introduction（緒論）** | **G ～ L** | 現況 (G)、挑戰 (H)、文獻分類 (I)、SWOT 評論 (J)、四大貢獻 (K)、章節架構 (L) |
| **Section II** | **Related Work（相關研究）** | **M ～ O** | 三大方法分類 (M)、研究空缺 Research Gap (N)、六欄文獻比較表 Table I (O) |
| **Section III**| **Proposed Design（提議設計）** | **PA ～ PM** | 13 項設計模組：目標、資料基底、語言計算分離、九大階段、14 行 Algorithm 1 虛擬碼 |
| **Section IV** | **Experiment & Evaluation（實驗與評估）**| **Q ～ U** | 四大評估指標 (Q)、三模式對照 (R)、60 題台灣基準集 (S)、錯誤分析 (T)、Table II 成果 (U) |
| **Section V**  | **Conclusion（結論）** | **W ～ Z** | 研究總結 (W)、專精優勢 (X)、實體產出 (Y)、邊界與未來展望 (Z) |
| **—** | **References（參考文獻）** | **[1] ～ [14]** | 完整收錄 14 篇 IEEE/SCI 期刊與環境部法定規範之 BibTeX |

---

## 📑 二、A-to-Z 26 節點深度對應規範

### 1. Abstract (A ～ F)
- **[A] Attention Getter (Motivation)**：WHO 空污致死數據（660 萬人/年、84% 慢性病）、99% 人口處於超標環境。
- **[B] But (Challenge)**：ACL 2025 揭露純 LLM 高達 3%–86% 數值幻覺；傳統 RAG 與既有 Agent 缺乏台灣環境部 AQI 副指標法規約束。
- **[C] Cure (Proposed Solution)**：提出 Tool-augmented Evidence Agent，語言理解與數值運算徹底分離。
- **[D] Development (Methodology)**：唯一觀測鍵值 `(SiteId, DataCreationDate)`、確定性分析模組與 Evidence Guard 證據連結拒答。
- **[E] Experiments (Evaluation)**：60 題台灣在地空品測試集（45 題趨勢/比較/解讀 + 15 題邊界/衝突拒答）。
- **[F] Findings (Outcomes)**：970,296 筆原始資料清理、隔離 13 組數值衝突；驗證達 100% 數值精確度與零幻覺。

### 2. Section I: Introduction (G ～ L)
- **[G] General (現況)**：環境部 AQX_P_488 逐時資料開放；近期多代理系統（如 Neuro-Air）展示多步驟分析可行性。
- **[H] However (挑戰與問題定義)**：大眾缺乏即時計算與查驗工具，直接詢問 LLM 面臨嚴重的數值捏造與時空錯配。
- **[I] In literature (文獻分類)**：機器學習預測（GB, RF+ARIMA）、微型感測器校正（AirBox SVC）、時序異常偵測（DTW/Z-score）。
- **[J] Judgement (評論與限制)**：預測與校正模型著重黑盒指標，無法提供自然語言可解釋性；自主 LLM 自由推理容易過度推論。
- **[K] Keypoint (四大貢獻)**：① 可重跑之清洗稽核管線、② 確定性分析工具與 Evidence Guard、③ 60 題台灣在地評測集、④ 量化實證零幻覺。
- **[L] List of organization (結構交代)**：明列各章節內容配置。

### 3. Section II: Related Work (M ～ O)
- **[M] Methods (方法分類)**：深入分析 8 篇重點文獻（Neuro-Air、DTW/Z-score 異常偵測、RF+ARIMA 預測、AirBox SVC、STOTEN 2025 濕度漂移校正）。
- **[N] New proposed (Research Gap)**：鎖定文獻空缺——尚未有以環境部 AQX_P_488 逐時資料為基礎，專門評估台灣 AQI 問答並同步執行行級來源查核之系統。
- **[O] Organized (Summary Table)**：呈現標準六欄 Table I（Study, Scope, Method, Domain, Findings, Limitations）。

### 4. Section III: Proposed Design (PA ～ PM)
- **[PA] Aim**：建立能準確回答台灣 AQI 且每項數值皆可回溯原始列之 Agent。
- **[PB] Background**：基於 88 個官方測站 2026/01–10 逐時資料庫。
- **[PC] Cure / Cause**：語言生成與數值計算解耦，消弭數值幻覺。
- **[PD] Design Transfer**：由 Free-form Chatbot 轉移至 Tool-augmented 確定性工具鏈。
- **[PE] Paper Elements**：九大處理階段（問題 ➜ Planner ➜ 檢索 ➜ MOENV 資料 ➜ 品質對齊 ➜ 確定性分析 ➜ AQI 規則 ➜ Evidence Guard ➜ 附來源回答）。
- **[PF] Formulation**：各模組數學公式與功能邊界。
- **[PG] Graph**：資料流與流程圖。
- **[PH] How**：以 `(SiteId, DataCreationDate)` 為唯一觀測鍵值對齊。
- **[PI] Implementation**：收錄帶行號之 14 步 Algorithm 1 演算法虛擬碼。
- **[PJ] Jump to Example**：三大典型案例（逐時趨勢、多站比較、AQI 判定）。
- **[PK] Key Points & Limits**：五大核心設計思維與三大權衡決策（不給醫療診斷、風向關聯不等於污染因果）。
- **[PL] Later Simulation**：AQX_P_432 即時串流與 IoT 感測網路之條件式擴充。
- **[PM] Math Proof**：環境部法定最大副指標 $\text{AQI} = \max_i (\text{SubIndex}_i)$ 與滑動平均時窗嚴格數學計算。

### 5. Section IV: Experiment and Evaluation (Q ～ U)
- **[Q] Quality & Quantity**：四大指標（數值正確率、證據忠實度、未引用主張率、限制拒答正確率）。
- **[R] Related Methods to Compare**：三模式對照（Mode 1: LLM-only, Mode 2: Deterministic Tools, Mode 3: Proposed Agent）。
- **[S] Simulation Setup**：60 題固定評測集（45 可回答 + 15 邊界拒答）。
- **[T] Tuning Parameters**：錯誤分類學分析（缺值、日期邊界、13 組衝突隔離）。
- **[U] Useful Results**：收錄 Table II 評測績效矩陣，實證 Proposed Agent 在正確性與拒答率均達 100%。

### 6. Section V: Conclusion (W ～ Z)
- **[W] What Proposed**：總結結合環境部資料、確定性工具與受限 LLM 的空品證據 Agent。
- **[X] eXcel**：專精於台灣在地逐時趨勢、測站比較與可稽核來源追溯。
- **[Y] Yields**：60 萬筆清洗觀測、13 組衝突日誌、60 題評測集、OpenSpec 規格庫。
- **[Z] Zen**：恪守證據邊界，為環境資訊系統提供可解釋、可驗證之可信 AI 典範。

---

## 📂 三、OpenSpec 模組化變更架構 (Modular Changes)

為避免單一提案過於龐大（Too large），OpenSpec 已依章節拆分為 7 個獨立的模組化變更（Changes）：

1. **`000-abstract`**：負責摘要結構（A~F：動機、挑戰、解藥、方法、實驗、發現）與 250 字檢驗。
2. **`001-introduction`**：負責緒論邏輯（G~L：現況、挑戰、文獻、評論、四大貢獻、章節架構）。
3. **`002-related-work`**：負責文獻分類（M~O：方法分類、Research Gap、六欄 Table I 摘要表）。
4. **`003-proposed-design`**：負責系統設計（PA~PM：目標、資料基底、文字計算分離、九大階段、14 行 Algorithm 1 虛擬碼）。
5. **`004-experiment`**：負責實驗與評估（Q~U：四大評估指標、三模式對照、60 題基準集、Table II 績效表）。
6. **`005-conclusion`**：負責結論撰寫（W~Z：研究總結、專精優勢、實體產出、證據邊界與未來展望）。
7. **`006-reference`**：負責參考文獻管理（收錄完整 14 篇重點期刊與環境部法規之標準 BibTeX）。

---

## 🛠️ 四、OpenSpec 指令操作與驗證狀態

目前在 `myplane` 目錄下執行全驗證：
```powershell
cmd /c "cd AIOC-DIC3-ProjectRefactor\myplane && openspec validate --all"
```
**驗證結果**：
```
✓ change/000-abstract
✓ change/001-introduction
✓ change/002-related-work
✓ change/003-proposed-design
✓ change/004-experiment
✓ change/005-conclusion
✓ change/006-reference
✓ spec/agent-workflow
✓ spec/data-preparation
✓ spec/deterministic-analytics
✓ spec/domain-rules
✓ spec/evaluation-benchmark
✓ spec/evidence-retrieval
✓ spec/github-openspec-integration
✓ spec/overleaf-draft
Totals: 15 passed, 0 failed (15 items)
```
OpenSpec 7 大模組化章節變更已全面通過檢查。
