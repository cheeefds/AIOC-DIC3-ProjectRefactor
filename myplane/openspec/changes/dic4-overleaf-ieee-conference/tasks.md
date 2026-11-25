## 1. IEEE Conference Paper Draft (Overleaf Preparation)

- [x] 1.1 撰寫標準 IEEEtran 雙欄 LaTeX 主文檔 `myplane/overleaf_draft/main.tex`，純文字架構無圖檔依賴，完整涵蓋 Abstract、五大核心設計、三大權衡、九大管線階段、14 行演算法虛擬碼與 60 題評測。
- [x] 1.2 建立標準 BibTeX 引用文獻庫 `myplane/overleaf_draft/references.bib`，納入 [1]~[14] 完整期刊、會議與環境部標準文獻。
- [x] 1.3 設計純文字無圖檔相依架構，消除外置圖片編譯風險，上傳 Overleaf 即可直接成功編譯。

## 2. Overleaf MCP (Model Context Protocol) 整合與協作工具鏈

- [x] 2.1 撰寫 Overleaf MCP 伺服器配置指南 `myplane/overleaf_draft/OVERLEAF_MCP_GUIDE.md`，定義 MCP tool schema 與環境變數設定。
- [x] 2.2 規劃 GitHub <-> Overleaf Git Bridge 雙向同步工作流，使 AI Agent 具備遠端編譯檢查與修復能力。

## 3. OpenSpec on GitHub CI/CD 自動化與主規格同步

- [x] 3.1 同步既有能力規格至 `myplane/openspec/specs/`，確立 6 項核心功能之權威規格（Main Specs）。
- [x] 3.2 建立 GitHub Actions 自動化規格驗證工作流程 `.github/workflows/openspec-verify.yml`，於 PR 與 Push 時自動執行 `openspec validate`。
- [x] 3.3 撰寫 OpenSpec on GitHub 協同開發指南 `myplane/OPEN_SPEC_GITHUB_GUIDE.md`，詳解 Spec-Driven Development 流程與分支規範。
- [x] 3.4 產出 DIC4 綜合總覽與交付說明文檔 `myplane/DIC4_README.md`。
