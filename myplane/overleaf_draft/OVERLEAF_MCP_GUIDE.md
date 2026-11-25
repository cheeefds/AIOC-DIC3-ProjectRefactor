# 📄 Overleaf Draft for IEEE Conference using MCP (Model Context Protocol)

本指南詳細說明如何使用 **Model Context Protocol (MCP)** 工具鏈以及 **GitHub Git Bridge**，在 **Overleaf** 上高效協同編寫、即時編譯與自動偵錯 IEEE 研討會論文（`main.tex` 與 `references.bib`）。

---

## 🚀 一、Overleaf MCP 核心概念與架構

Model Context Protocol (MCP) 允許 AI 代理人直接與外部軟體、雲端服務與編譯器進行結構化互動。透過 Overleaf MCP 伺服器，AI 代理人可直接具備以下能力：
1. **讀取與檢視 Overleaf 專案檔案**（`main.tex`、`references.bib`、圖表與編譯日誌）。
2. **自動診斷 LaTeX 編譯錯誤**（分析 `output.log`，定位未定義引用、遺失 macro 或套件衝突）。
3. **安全套用修訂與補全文獻**（自動更新 BibTeX、修復行內方程式與調整雙欄排版）。
4. **與 GitHub 進行雙向無縫同步**（本地代碼庫 ⟷ GitHub ⟷ Overleaf）。

```
  ┌─────────────────────────────────────────────────────────┐
  │                 AI Coding Agent (Antigravity)           │
  └────────────────────────────┬────────────────────────────┘
                               │ MCP Protocol (JSON-RPC)
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │               Overleaf / LaTeX MCP Server               │
  │  - overleaf_compile_project                             │
  │  - overleaf_get_compiler_log                            │
  │  - overleaf_read_file / overleaf_write_file             │
  └────────────────────────────┬────────────────────────────┘
                               │ Sync / API
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │         Overleaf Cloud Project (IEEE Conference)        │
  │  - main.tex (IEEEtran 雙欄會議模板，純文本無依賴圖檔)   │
  │  - references.bib (14 篇文獻完整 BibTeX)                 │
  └─────────────────────────────────────────────────────────┘
```

---

## ⚙️ 二、Overleaf MCP 伺服器配置設定

在您的 Antigravity / Claude Code / Cursor MCP 設定檔（例如 `mcp_settings.json` 或 `antigravity.mcp.json`）中加入以下配置：

### 1. 配置範例（Overleaf Local / Git Bridge MCP）
```json
{
  "mcpServers": {
    "overleaf-bridge": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-latex-overleaf",
        "--project-dir",
        "C:\\Users\\user\\Downloads\\fjdsflds\\AIOC-DIC3-ProjectRefactor\\myplane\\overleaf_draft"
      ],
      "env": {
        "OVERLEAF_PROJECT_ID": "<YOUR_OVERLEAF_PROJECT_ID>",
        "OVERLEAF_API_TOKEN": "<YOUR_OVERLEAF_TOKEN_IF_PREMIUM>",
        "LATEX_COMPILER": "pdflatex"
      }
    }
  }
}
```

### 2. 核心 MCP 工具清單 (Tool Definitions)
| 工具名稱 | 參數 | 功能說明 |
|---|---|---|
| `overleaf_read_file` | `path: string` | 讀取指定 LaTeX 檔案或 BibTeX 內容 |
| `overleaf_write_file` | `path: string, content: string` | 更新或局部修訂論文內容 |
| `overleaf_compile` | `timeout: integer` | 觸發 pdfLaTeX 編譯，回傳編譯狀態 |
| `overleaf_get_compiler_log` | `lines: integer` | 獲取編譯失敗之錯誤行號與警告訊息 |
| `overleaf_verify_citations` | `tex_file: string, bib_file: string` | 自動檢查所有 `\cite{}` 是否皆存在於 `references.bib` |

---

## 🔄 三、GitHub ↔ Overleaf 雙向同步工作流

Overleaf 支援直接連結 GitHub 倉庫（Professional/Student 方案或透過 Git Bridge）：

### 步驟 1：建立 Overleaf 專案
1. 登入 [Overleaf](https://www.overleaf.com/)。
2. 點選 **New Project** ➜ **Upload Project**（可直接將 `myplane/overleaf_draft` 壓縮為 `.zip` 上傳）或 **Import from GitHub**。
3. 選擇 `cheeefds/AIOC-DIC3-ProjectRefactor` 倉庫。

### 步驟 2：設定 Overleaf 編譯器
- 在 Overleaf 介面左上角點擊 **Menu**：
  - **Compiler**: `pdfLaTeX` (推薦) 或 `XeLaTeX`
  - **Main document**: `main.tex`
  - **TeX Live version**: `2024` 或最新版

### 步驟 3：使用 Git Bridge 進行本地與雲端同步
若您使用 Overleaf 的 Git 遠端網址：
```bash
# 進入本機 draft 目錄
cd myplane/overleaf_draft

# 初始化獨立 git（或使用子模組/主倉庫同步）
git remote add overleaf https://git.overleaf.com/<YOUR_PROJECT_ID>
git pull overleaf master
# 本地修改後推送
git commit -am "Update IEEE conference draft via MCP"
git push overleaf master
```

---

## 📝 四、論文檔案清單與功能

目錄 `myplane/overleaf_draft/` 包含以下完整交付物：
1. **[main.tex](file:///c:/Users/user/Downloads/fjdsflds/AIOC-DIC3-ProjectRefactor/myplane/overleaf_draft/main.tex)**：
   - 採用 IEEE 官方會議格式 (`\documentclass[conference]{IEEEtran}`)。
   - 包含 Abstract、I. Introduction、II. Related Work、III. Core Design Principles & Trade-offs、IV. System Architecture & Methodology、V. Implementation & Deterministic Engine、VI. Experimental Benchmark & Evaluation、VII. Results & Discussion、VIII. Limitations & Future Work、IX. Conclusion。
   - 內建帶行號之 **Algorithm 1 Pseudocode** 與文獻比較表 **Table I**。
2. **[references.bib](file:///c:/Users/user/Downloads/fjdsflds/AIOC-DIC3-ProjectRefactor/myplane/overleaf_draft/references.bib)**：
   - 收錄 `ma2026multi` (npj Clean Air 2026)、`lee2025anomaly` (IEEE Access 2025)、`tzeng2023spatially` (Biometrics 2023)、`dong2025calibration` (STOTEN 2025)、`moenv2026aqi_historical` 等 14 篇完整 BibTeX 項目。
   - 本草稿專案設計為**純文本無額外圖檔依賴（Zero Image Dependencies）**，直接由結構化文字清單、Table I、Table II 與 Algorithm 1 演算法虛擬碼自包含呈現，上傳 Overleaf 即可直接編譯完成。
