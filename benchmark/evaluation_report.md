# Taiwan AQI Evidence Agent — Benchmark Evaluation Report

## 1. 實驗設計與評估矩陣 (Evaluation Matrix)
本評估採用 60 題固定基準集（包含 45 題可回答時空問答題，以及 15 題邊界拒答/守門題），比較以下三種模式：
1. **LLM-only**：純大型語言模型自由推理（無檢索工具與領域規則）。
2. **Deterministic Tools Only**：純確定性數值分析工具（僅輸出數值表格，無生成式文字）。
3. **Proposed Agent**：工具增強型證據代理人（檢索 + 確定性工具 + 領域守門 + 受限生成 + Evidence Guard）。

## 2. 評估指標量化對比 (Quantitative Comparison)

| 評估指標 (Metrics) | ① LLM-only | ② Deterministic Tools | ③ Proposed Evidence Agent | 理想指標方向 |
| :--- | :---: | :---: | :---: | :---: |
| **回答正確率 (Answer Accuracy)** | `33.3%` | `100.0%` | `100.0%` | 越高越好 (↑) |
| **證據忠實度 (Provenance Fidelity)** | `0.0%` | `100.0%` | `100.0%` | 越高越好 (↑) |
| **無依據主張率 (Unsupported-claim Rate)** | `85.0%` | `0.0%` | `0.0%` | 越低越好 (↓) |
| **限制處理與拒答率 (Limitation Accuracy)** | `13.3%` | `100.0%` | `100.0%` | 越高越好 (↑) |

## 3. 核心發現與分析 (Key Findings)
- **數值防幻覺成效**：LLM-only 條件下數值幻覺頻發，無法給出精確的時序百分比與極值；本專題 Agent 藉由確定性分析模組，確保所有數值 100% 來自真實計算。
- **列級證據追溯**：本專題 Agent 具備 Evidence Guard 機制，每一項數值均附帶來源檔案與 `(SiteId, DataCreationDate)` 觀測主鍵，證據忠實度達標。
- **守門與邊界拒答**：在 15 題資料缺失、因果歸因指控與個人醫療諮詢情境中，本專題 Agent 能 100% 確定性觸發守門與限制宣告，展現「何時不該回答」之可靠性。

## 4. 錯誤分類統計 (Error Taxonomy)
### LLM-only 錯誤類型：
- `NUMERICAL_HALLUCINATION_OR_NO_PROVENANCE`: 30 件
- `FAILED_TO_ABSTAIN_ON_GUARDRAIL`: 13 件

### Proposed Agent 錯誤類型：
- 無錯誤紀錄（全部案例符合預期行為）

---
*Report generated automatically by Taiwan AQI Evidence Agent evaluation suite.*