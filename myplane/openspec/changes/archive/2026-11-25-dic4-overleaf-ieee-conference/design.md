# Design: DIC4 Overleaf IEEE Draft, MCP Bridge, and GitHub OpenSpec

## 1. IEEE Conference Paper Architecture
The conference manuscript follows the official IEEE two-column format (`IEEEtran.cls` conference mode).
- **Title**: Taiwan Air Quality Evidence Agent for Traceable Local Air-Quality Analysis
- **Structure**:
  1. **Abstract**: Structured IEEE single-paragraph abstract incorporating Attention Getter, But, Cure, Development, Experiments, Findings, and Index Terms.
  2. **Section I: Introduction**: Global WHO background, MOENV AQX_P_488 challenges, LLM hallucinations, proposed solution, and explicit contribution claims.
  3. **Section II: Related Work & Research Gap**: Comparison matrix of 8 foundational papers and the specific research gap addressed.
  4. **Section III: Domain Foundations & Design Principles**: The 5 core principles (multi-pollutant summary, micro-environment, sensor tiers, temporal alignment, correlation vs. causation) and 3 trade-offs (IoT vs. reference stations, ML vs. deterministic analytics, autonomous vs. constrained agent).
  5. **Section IV: System Methodology**: 9-stage pipeline, observation key `(SiteId, DataCreationDate)`, and 14-line Algorithm 1 pseudocode.
  6. **Section V: Deterministic Suite & Implementation**: Offline cleanup, 13 conflict exclusions, 4 SiteId recoveries, and Evidence Guard closed-loop verification.
  7. **Section VI: Benchmark & Experimental Evaluation**: 60-question Taiwan benchmark (45 answerable, 15 abstention), three evaluation modes, and quantitative metrics.
  8. **Section VII: Empirical Results & Discussion**: Accuracy, fidelity, and limitation performance.
  9. **Section VIII: Limitations & Conclusion**: Future IoT/API roadmap and closing remarks.

## 2. MCP (Model Context Protocol) Overleaf Bridge Design
To allow coding agents to author, review, and debug Overleaf projects seamlessly:
- **Architecture**:
  - `Overleaf MCP Server` connects via Overleaf Git bridge / API or local working directory.
  - Exposes tools: `overleaf_read_file`, `overleaf_write_file`, `overleaf_compile`, `overleaf_get_compiler_logs`.
  - Agents receive compile errors/warnings and automatically patch `main.tex` and `references.bib`.
- **Sync Protocol**:
  - Local repository (`myplane/overleaf_draft`) <---> GitHub Repository <---> Overleaf Project (via Overleaf-GitHub Sync or Git bridge).

## 3. OpenSpec on GitHub CI/CD Design
- **Workflow File**: `.github/workflows/openspec-verify.yml`.
- **Triggers**: `push` to `main`, `pull_request` on all branches touching `openspec/**`.
- **Validation Steps**:
  1. Checkout code.
  2. Set up Node.js.
  3. Install `@openspec/cli` globally.
  4. Run `openspec validate --all` inside `myplane`.
  5. Enforce blocking check on PR merges if specs or changes contain validation syntax errors.
