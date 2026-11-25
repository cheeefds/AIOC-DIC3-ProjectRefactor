# 🎯 DIC4 交付總覽：Overleaf IEEE Conference Draft & OpenSpec on GitHub

本文件為 **DIC4** 階段的完整交付與技術整合總覽，全面落實以下兩大核心需求：
1. **Overleaf draft for IEEE conference using MCP**
2. **OpenSpec on GitHub**

---

## 📌 需求一：Overleaf draft for IEEE conference (含 MCP 整合)

### 1. 交付物目錄架構
所有 IEEE 會議論文原始碼與圖表均已存放於專屬目錄 [myplane/overleaf_draft/](file:///c:/Users/user/Downloads/fjdsflds/AIOC-DIC3-ProjectRefactor/myplane/overleaf_draft/)：
- **`main.tex`**：完整標準的 IEEE Conference 雙欄 LaTeX 論文主檔。
  - **題目**：*Taiwan Air Quality Evidence Agent for Traceable Local Air-Quality Analysis*
  - **摘要 (Abstract)**：融合 A~F 架構（Attention Getter, But, Cure, Development, Experiments, Findings），無縫整合 60 萬筆清洗觀測、13 組衝突隔離與 60 題在地評測集。
  - **Index Terms**：Air quality monitoring, evidence-grounded question answering, large language models, tool-augmented agents, deterministic analytics, numerical hallucination, trustworthy artificial intelligence.
  - **正文九大章節**：
    - `I. Introduction`（公衛背景、WHO 660 萬人死亡數據、ACL 2025 LLM 幻覺、四項專題貢獻）
    - `II. Related Work & Research Gap`（8 篇關鍵文獻比較表 Table I、文獻缺口分析）
    - `III. Core Design Principles & Trade-offs`（**五大核心設計思維**、**三大權衡架構決策**）
    - `IV. System Architecture & Methodology`（**九大處理階段文字詳解**、`(SiteId, DataCreationDate)` 唯一主鍵、**Algorithm 1 帶行號演算法虛擬碼**）
    - `V. Implementation & Deterministic Engine`（資料清洗、13 組衝突隔離、4 筆 SiteId 空間修復、Gemini LLM + 雙機制降級、Evidence Guard 閉環查核）
    - `VI. Experimental Benchmark & Evaluation`（60 題台灣在地評測集：45 可回答 + 15 拒答、三種對照模式）
    - `VII. Results & Discussion`（效能比較 Table II、零數值幻覺與 100% 來源可追溯性）
    - `VIII. Limitations & Future Work`（資料時間涵蓋限制、未來即時 API 與微型感測器擴充）
    - `IX. Conclusion`（總結）
- **`references.bib`**：標準 BibTeX 文獻庫，收錄 14 篇重點論文與法規標準（涵蓋 *npj Clean Air*, *IEEE Access*, *STOTEN*, *Biometrics*, WHO, U.S. EPA 等）。
- **`OVERLEAF_MCP_GUIDE.md`**：詳細解說如何使用 Model Context Protocol (MCP) 與 GitHub 雙向同步工作流，支援 AI 代理人直接自動讀取編譯日誌、自動修復 LaTeX 與更新文獻。本草稿專案為**純文字無額外圖檔依賴（Zero Image Dependencies）**，開箱即編譯。

---

## 📌 需求二：OpenSpec on GitHub

### 1. 建立並同步主規格庫 (Main Specs on GitHub)
已將系統 6 大核心能力正式同步至 [myplane/openspec/specs/](file:///c:/Users/user/Downloads/fjdsflds/AIOC-DIC3-ProjectRefactor/myplane/openspec/specs/)，成為 GitHub 上的永久權威依據：
1. `agent-workflow/spec.md`：Agent 互動週期、結構化解析與 Evidence Guard 驗證規範。
2. `data-preparation/spec.md`：MD5 校驗、哨兵值標準化、主鍵去重與空間 SiteId 修復規範。
3. `deterministic-analytics/spec.md`：趨勢計算、多站排序與持續性基準規範。
4. `domain-rules/spec.md`：環境部 AQI 副指標最大值、法定平均視窗與拒答守門規範。
5. `evaluation-benchmark/spec.md`：60 題固定評測集、三模式對照與評估指標規範。
6. `evidence-retrieval/spec.md`：測站代碼反查與時區切片檢索規範。

### 2. 建立 DIC4 專屬變更提案 (Active Change)
已在 [myplane/openspec/changes/dic4-overleaf-ieee-conference/](file:///c:/Users/user/Downloads/fjdsflds/AIOC-DIC3-ProjectRefactor/myplane/openspec/changes/dic4-overleaf-ieee-conference/) 建立標準變更產物：
- `.openspec.yaml`：變更定義與 schema 宣告。
- `proposal.md`：DIC4 需求動機與預期影響。
- `design.md`：IEEE 論文架構、Overleaf MCP 伺服器設計與 CI/CD 機制。
- `tasks.md`：完整可追蹤之任務清單。
- `specs/overleaf-draft/spec.md`：Overleaf 論文草稿規格。
- `specs/github-openspec-integration/spec.md`：GitHub Actions 與規格同步規格。

### 3. GitHub Actions CI 自動化工作流
已於根目錄建立 [`.github/workflows/openspec-verify.yml`](file:///c:/Users/user/Downloads/fjdsflds/AIOC-DIC3-ProjectRefactor/.github/workflows/openspec-verify.yml)：
- 自動監控 GitHub 上的 Pull Requests 與 Push 事件。
- 自動安裝 `@openspec/cli` 並執行 `openspec validate --all`。
- 保證任何違反 OpenSpec 規範的提交無法直接合併至 GitHub 主分支。

### 4. OpenSpec on GitHub 開發指南
已建立 [myplane/OPEN_SPEC_GITHUB_GUIDE.md](file:///c:/Users/user/Downloads/fjdsflds/AIOC-DIC3-ProjectRefactor/myplane/OPEN_SPEC_GITHUB_GUIDE.md)，完整提供團隊在 GitHub 上使用 Spec-Driven Development 的標準 SOP、分支命名原則與 PR 審查準則。

---

## 🔍 三、驗證總覽

在 `myplane` 目錄下執行全規格與變更驗證：
```powershell
cmd /c "cd AIOC-DIC3-ProjectRefactor\myplane && openspec validate --all"
```
**驗證結果**：
```
✓ spec/agent-workflow
✓ spec/data-preparation
✓ spec/deterministic-analytics
✓ change/dic4-overleaf-ieee-conference
✓ spec/domain-rules
✓ spec/evaluation-benchmark
✓ spec/evidence-retrieval
✓ change/taiwan-aqi-evidence-agent
Totals: 8 passed, 0 failed (8 items)
```
全部 8 項規格與變更 100% 通過檢驗！
