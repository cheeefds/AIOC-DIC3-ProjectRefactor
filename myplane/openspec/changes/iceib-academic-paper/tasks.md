## 1. Abstract & Introduction (A2Z Sections A~L)

- [x] 1.1 撰寫 Abstract 六段結構：Motivation (A)、But (B)、Cure (C)、Development (D)、Experiments (E)、Findings (F)，符合 IEEE 單段與 250 字限制。
- [x] 1.2 撰寫 Introduction 緒論邏輯：General 現況 (G)、However 挑戰 (H)、In literature 文獻分類 (I)、Judgement 評論 (J)、Keypoint 四大貢獻 (K) 與 List of organization 文章結構 (L)。

## 2. Related Work & Research Gap (A2Z Sections M~O)

- [x] 2.1 彙整方法分類 (M)：梳理空品 Agent (Neuro-Air)、時序異常偵測 (DTW/Z-score)、預測模型 (RF+ARIMA, GB) 與感測器校正 (SVC, Bland-Altman) 等 8 篇論文。
- [x] 2.2 明確界定 Research Gap (N)：聚焦以環境部 AQX_P_488 為基底的台灣在地 AQI 問答基準與列級來源驗證空缺。
- [x] 2.3 構建標準六欄 Article Summary Table (O)：涵蓋 Study, Scope, Method, Domain, Findings, Local Limitations。

## 3. Proposed Design (A2Z Sections PA~PM)

- [x] 3.1 規範系統目標與資料基底 (PA/PB)：鎖定台灣 88 個官方測站 2026 年逐時觀測資料。
- [x] 3.2 落實職責分離與架構轉移 (PC/PD)：確立文字生成與數值計算分離原則，由 free-form 轉為 tool-augmented。
- [x] 3.3 定義九大模組與功能規範 (PE/PF)：涵蓋 Planner、Quality Guard、Analytics、AQI Rules 與 Evidence Guard。
- [x] 3.4 呈現資料流與演算法 (PG/PH/PI)：以 `(SiteId, DataCreationDate)` 為主鍵，提供 14 行帶行號之 Algorithm 1 虛擬代碼。
- [x] 3.5 定義三大典型案例與守門邊界 (PJ/PK/PL/PM)：規範趨勢/比較/解讀案例、因果/醫療守門、IoT 擴充與確定性代數基礎。

## 4. Experiment & Evaluation (A2Z Sections Q~U)

- [x] 4.1 定義質化與量化評估指標 (Q)：Answer Accuracy、Provenance Fidelity、Unsupported-claim Rate 與 Limitation Accuracy。
- [x] 4.2 建立三模式對比架構 (R)：LLM-only vs. Deterministic Tools vs. Proposed Agent。
- [x] 4.3 實作 60 題固定基準集 (S)：45 題可回答（趨勢/比較/解讀各 15 題）與 15 題邊界拒答情境。
- [x] 4.4 執行失敗案例與邊界參數分析 (T)：記錄資料缺漏、衝突與中英標籤之錯誤分類。
- [x] 4.5 產出實證成效矩陣 (U)：彙整 Table II 比較結果，驗證零數值幻覺與 100% 來源可追溯性。

## 5. Conclusion & References (A2Z Sections W~Z)

- [x] 5.1 撰寫 Conclusion 四大要素：What proposed 研究總結 (W)、eXcel 專精優勢 (X)、Yields 產出成果 (Y) 與 Zen 結論邊界 (Z)。
- [x] 5.2 驗證 IEEE 參考文獻庫：確保 `references.bib` 收錄完整 14 篇重點期刊與環境部規範文獻，並於正文精準引用。
