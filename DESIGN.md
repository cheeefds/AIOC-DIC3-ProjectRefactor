# Taiwan Air Quality Evidence Agent

Living design document for the Proposal and implementation phases. Decisions marked **planned** describe the proposed implementation and should be validated during development. The project is scoped to a Taiwan AQI question-answering evaluation; it does not claim a new general-purpose agent architecture.

## 1. Problem and research question

### 1.0 Proposal Abstract (A-F Structure)

#### Attention Getter（Motivation）
世界衛生組織（WHO）指出，空氣污染是全球首要的環境健康風險因子，每年造成約 660 萬人死亡；其中近 84% 的空污相關死亡來自心血管疾病、中風、慢性阻塞性肺病（COPD）及肺癌等非傳染病。 WHO 亦估計，全球約 99% 人口暴露於超過其 PM2.5 年均 guideline（5 μg/m³）的空氣品質，顯示空污風險具有高度普遍性。

此外，State of Global Air 2025 估計，印度與中國合計占全球空污相關死亡負擔的 56%，凸顯高污染地區的公共衛生負擔高度集中。 空氣污染同時被 WHO 視為僅次於菸草的全球非傳染病風險因子，因此建立即時、可信、可追溯的空氣品質資訊系統，具有明確的公共衛生與政策價值。

#### But（Challenge）
環境部已開放 AQX_P_488「空氣品質指標（AQI）歷史資料」，提供各測站逐時 AQI、PM2.5、PM10、O3、SO2、CO、NO2、風速、風向、經緯度及資料建立時間等欄位。 然而，使用者仍須自行處理測站對齊、時間戳記、污染物單位、移動平均值、AQI 等級判定及資料缺漏等問題；若直接將原始資料交由生成式 LLM 回答，容易產生站點、時間或數值錯配。

純生成式 LLM 也存在明顯的數值與事實幻覺風險。2025 年 ACL 研究指出，即使是表現較佳的 LLM，在不同領域仍可能對 3%–86% 的事實陳述產生幻覺，顯示語言流暢並不等於數值正確。 雖然 Retrieval-Augmented Generation（RAG）可降低幻覺，但研究顯示其並無法完全消除錯誤：一項公共衛生領域的 MEGA-RAG 研究透過多源檢索、重排序與證據不一致檢查，將幻覺率降低逾 40%；另一項 RAG 忠實性研究則發現，即使提供正確上下文，最先進方法仍未必能達到 80% 以上的事實正確率。

既有空品 Agent 亦尚未完全解決台灣在地需求。Neuro-Air 是 2026 年發表於 npj Clean Air 的多代理 LLM 框架，結合即時空污資料檢索與持久化程式執行沙箱，並透過協調代理調度多個領域代理處理都市空污管理任務。 不過，其資料範圍、任務設計與評估情境並非針對台灣環境部站級逐時資料、台灣 AQI 規則、資料衝突偵測及可拒答機制而設計。

#### Cure（Proposed Solution）
本研究提出一個 Tool-augmented Evidence Agent，結合環境部逐時觀測資料檢索、確定性數值分析工具（Deterministic Analytics）、台灣 AQI 領域規則與受限 LLM。系統將語言理解、資料檢索、數值計算與規則判定明確分工：LLM 負責理解使用者意圖、組織證據與生成說明；確定性工具負責查詢、對齊、計算、比較與規則判定。

具體而言，系統以 (SiteId, DataCreationDate) 作為唯一觀測鍵值，避免同名測站、行政區混淆或跨小時、跨更新批次的數值錯配。 當使用者詢問某測站於特定時間的 AQI、主要污染物、濃度變化或空品等級時，Agent 必須先檢索對應原始觀測，再由確定性工具完成計算與規則判斷，最後才由 LLM 產生附帶來源、時間、測站與計算依據的回答。

若資料不足、時間範圍不支援、測站不存在，或同一觀測鍵值下出現數值衝突，系統將優先採取證據連結的拒答（evidence-linked refusal），而非讓 LLM 自行推測或補完數值。此設計直接回應 LLM 在高風險、數值敏感任務中的幻覺問題。

#### Development（Method）
本研究將系統拆分為四個模組：
- **資料檢索模組**：從環境部 AQX_P_488 逐時資料集中，依 SiteId、County、時間範圍與污染物欄位檢索觀測值。
- **資料清理與對齊模組**：以 (SiteId, DataCreationDate) 建立唯一觀測鍵值，處理重複紀錄、缺值、單位、時間戳記與跨批次更新問題。
- **確定性分析模組**：執行 AQI 等級判定、污染物比較、時序變化、移動平均、極值查詢及異常偵測；所有數值結果均由程式計算，而非由 LLM 直接生成。
- **受限生成模組**：LLM 僅能根據已驗證的證據與工具輸出撰寫回答，並須標註測站、時間、資料來源、計算依據；無法驗證時必須明確拒答。

此架構的創新之處，在於不是僅將 LLM 與 RAG 結合，而是將「語言理解」與「數值可信性」徹底分離，並以台灣 AQI 規則作為領域約束。

#### Experiments（Evaluation）
本研究規劃建立 60 題台灣在地空品測試集，包含：
- **45 題可回答題**：涵蓋單一測站即時或歷史 AQI、主要污染物、濃度變化、跨日比較、區域概況及 AQI 等級判定。
- **15 題資料不足／衝突／拒答題**：涵蓋測站不存在、時間超出資料範圍、欄位缺漏、同一觀測鍵值數值衝突，以及無法由既有規則安全推論的問題。

實驗將比較三種模式：
- **LLM-only**：僅使用 LLM 直接回答（評估重點：數值正確率、幻覺率、來源可追溯性）
- **Deterministic Tools Only**：僅使用確定性工具與規則（評估重點：計算正確性、規則一致性、自然語言可用性）
- **Proposed Agent**：檢索 + 確定性工具 + 台灣 AQI 規則 + 受限 LLM（評估重點：整體正確率、拒答正確性、證據可追溯性、衝突偵測）

評估指標將包括回答正確率、數值正確率、AQI 等級判定正確率、來源引用正確率、拒答正確率，以及資料衝突偵測率。此設計可檢驗系統是否不僅「能回答」，更能判斷「何時不應回答」。

#### Findings（Expected Outcomes）
目前 Proposal 階段尚未進行 Agent 實驗，因此所有成效均標註為待驗證。現階段已完成 2026/1/1 至 2026/10/29 共 970,296 筆原始資料清理，保留 606,137 筆獨立觀測，並隔離 13 組數值衝突。

這些前置成果顯示，台灣逐時空品資料確實存在重複、缺漏、時間對齊與數值不一致等實務問題；若未建立確定性驗證與拒答機制，LLM 可能將不完整或衝突資料轉化為看似合理但錯誤的回答。本研究預期，相較於 LLM-only 與 Deterministic Tools Only，本 Agent 能在維持可用性的同時，提高數值正確性、來源可追溯性與拒答可靠性。

### 1.1 Research Question

Users need to interpret air-quality observations by place and time, understand which measurements support the interpretation, and see when evidence is incomplete. The project asks:

> For location- and time-specific questions about Taiwan's AQI, can an agent that retrieves MOENV records, runs deterministic analyses, and grounds its explanation in the source records answer more accurately and traceably than an LLM-only response?

## 2. Scope

### In scope for the proposal prototype

- Offline analysis of MOENV AQX_P_488 historical hourly CSV files.
- Trend summaries, pollutant/AQI context, and station comparisons.
- A deterministic data and analysis layer with an LLM limited to query interpretation and response wording.
- Explicit handling of missing, duplicated, stale, or conflicting records.
- Comparison against an LLM-only response and deterministic tool output.

### Outside the required MVP

- Individual exposure estimation, clinical advice, or causal pollution-source attribution.
- Low-cost IoT sensor calibration or fusion. AQX_P_432 live data can be a later demo extension if access is confirmed.
- Learned forecasting or an open-ended multi-agent topology. Add these only if the team can justify and evaluate them with the available data.

## 3. Data inventory and current audit

### Primary source

- Taiwan Ministry of Environment historical AQI dataset **AQX_P_488**: <https://data.moenv.gov.tw/dataset/detail/aqx_p_488>
- Data fields include station/county, AQI/status, pollutant concentrations, wind, `DataCreationDate`, coordinates, and `SiteId`.
- Current download window: **2026-01-01 00:00 to 2026-10-29 16:00**. This does not constitute a complete year.
- Current local files: 10 monthly/current CSV archives, 970,296 raw rows and 88 distinct station IDs across the period.
- Cleanup produced **606,137 unique station-time observations**. It merged localized duplicate rows, normalized missing sentinels to empty cells, recovered four absent `SiteId` values only where county plus exact coordinates uniquely mapped to one known ID, and excluded 13 conflicting station-time keys (26 source variants).
- Detailed file-level counts and MD5 checksums: `data/processed/cleaning_report.md`. The excluded variants and disagreement fields: `data/processed/aqi_2026_conflicts.csv`.
- Cleaning implementation: `scripts/clean_aqi_data.py`. Raw and generated CSVs are local artifacts excluded from Git because of their size; the source archives can be downloaded again from MOENV and processed with the checked-in script.

The source field `DataCreationDate` is retained as the source-provided timestamp. Whether it should be described as observation time or publication time requires confirmation from the MOENV documentation before making temporal semantics more specific. The raw archives contain both Chinese and English labels, so joins use station ID and timestamp rather than names.

### Optional source

- MOENV current AQI dataset **AQX_P_432**: <https://data.moenv.gov.tw/dataset/detail/aqx_p_432>
- MOENV/Civil IoT sensing overview: <https://env.moenv.gov.tw/en/Issue/Index/53b6ae55-bb69-449e-953e-01c2330ca3b8>
- Any integration depends on confirming API access, time semantics, station mapping, historical retention, sensor class, units, and quality metadata. It is not required for the evaluation to run.

## 4. Requirements

### Functional

- Accept a supported station/location, time window, pollutant, and analysis request.
- Retrieve records from the local AQX_P_488 extract and keep source-file and row-level provenance.
- Validate timestamps, units, missingness, duplicate keys, conflicts, and time coverage.
- Produce reproducible trend, pollutant-context, and station-comparison results.
- Show the station ID/name, source time window, values, source, and known limitations.
- Ask for clarification or return a data-gap/unsupported response when needed.
- Avoid causal source claims and individualized medical advice.

### Non-functional

- Reproducible data preparation and evaluation using versioned code and documented source checksums.
- Numeric values in the response must come from deterministic tools.
- Source data remain immutable; cleanup outputs and conflicts are separate artifacts.
- Missing and conflicting records must remain visible in logs or quality summaries.

## 5. Architecture

```mermaid
flowchart LR
  U[① User question] --> P[② Planner]
  P --> R[③ Data retrieval]
  R --> D[(④ MOENV AQX_P_488)]
  D --> Q[⑤ Quality checks and time alignment]
  Q --> A[⑥ Deterministic analytics]
  A --> K[⑦ AQI domain rules]
  K --> G[⑧ Evidence and uncertainty guard]
  G --> O[⑨ Answer with provenance]
  L[(Optional AQX_P_432 live data)] -. conditional .-> R
```

## 6. Components

| Module | Responsibility | Input | Output |
|---|---|---|---|
| ① User interaction | Receive question and display answer | Natural-language question | Query text and answer view |
| ② Planner | Extract intent, station/location, period, pollutant; request clarification if needed | Query | Structured query plan |
| ③ Retrieval | Select station IDs and read relevant CSV records | Query plan | Raw records and source metadata |
| ④ MOENV dataset | Provide hourly AQI/pollutant observations | Downloaded archives | Source observations |
| ⑤ Quality/time alignment | Parse Taiwan time, apply missing-value rules, check coverage/duplicates/conflicts | Raw records | Valid records and quality flags |
| ⑥ Analytics | Calculate trend, differences, and station comparisons | Valid observations | Numeric findings and baseline results |
| ⑦ Domain rules | Interpret AQI maximum sub-index and pollutant-specific time windows | Findings and source fields | Qualified domain interpretation |
| ⑧ Evidence guard | Match claims to station/time/value records and assess whether evidence is adequate | Interpretation and records | Supported or qualified claims |
| ⑨ Response layer | Explain results in concise language with provenance and limits | Verified claims | Final response |

## 7. Data handling policy

- Preserve original monthly files unchanged and retain original filenames/checksums.
- Normalize source sentinels (`-`, `--`, `NA`) to empty values in the derived CSV.
- Use `(SiteId, DataCreationDate)` as the observation key. Never join on station name alone.
- Collapse localized duplicate rows only if all non-missing numeric fields agree; fill empty fields from another copy when safe.
- Exclude every variant of a key if two non-missing numeric values conflict. Log the differing fields and source rows.
- Recover a missing `SiteId` only when the county and exact coordinates match exactly one known station ID. Otherwise retain the source row in the conflict log.
- Preserve source time and units. Confirm the meaning of `DataCreationDate` before changing the `observed_at` label.
- Do not infer personal exposure from a fixed station or interpret a spatial/temporal association as causal proof.

## 8. AI and analytics policy

The MVP is an analytics-driven, tool-using agent rather than a free-form chatbot. Deterministic code performs retrieval, numeric operations, thresholds, and comparisons. An LLM may parse the question and phrase tool outputs, but it may not create measurement values, interpolate unobserved records, or invent citations. If data quality fails the query's requirements, the response returns the quality limitation.

Initial analysis methods are descriptive summaries, direction/magnitude of change, and a threshold/persistence baseline where an event rule is applicable. Forecasting and learned anomaly models are optional future work; the proposal does not promise them before a labeled evaluation set exists.

## 9. Domain knowledge

- MOENV AQI definition, pollutant sub-indices, categories, units, and averaging windows.
- Source timestamp and time-zone semantics.
- Station location and spatial representativeness.
- Difference between observations, associations, forecasts, source attribution, and personal exposure.
- Low-cost sensor siting, calibration, humidity effects, and transferability if optional IoT data are added.
- Uncertainty communication and clear limits on health-related statements.

Operational rules must cite an authoritative source or peer-reviewed study in `Proposal.md`.

## 10. Algorithm

1. Parse user intent, location/station, time window, and pollutant.
2. Clarify unresolved inputs or state any default.
3. Retrieve source records using station ID and time.
4. Normalize fields and timestamps; assess missingness, conflicts, and coverage.
5. Return a limitation response if evidence cannot answer the request.
6. Execute the requested deterministic trend, comparison, or AQI-context calculation.
7. Compare with a threshold/persistence baseline when the task uses an event rule.
8. Attach source records to numeric claims and apply AQI domain rules.
9. Remove or qualify unsupported claims; return values, time, source, uncertainty, and limitations.

## 11. Evaluation plan

Use a fixed 60-question benchmark: 45 answerable questions (15 trend, 15 station comparison, 15 AQI/pollutant interpretation) and 15 cases with insufficient/conflicting data or unsupported causal/medical premises. Generate expected values with deterministic queries and manually inspect a sample.

Compare three conditions:

1. LLM-only response with no source retrieval.
2. Deterministic analysis output without generated prose.
3. The proposed tool-using Agent.

Metrics:

- Numeric answer accuracy for retrieved AQI, pollutant values, trend direction/change, and station ranking, using a task-specific tolerance.
- Provenance accuracy: whether cited station IDs, times, values, and source records match.
- Unsupported-claim rate: numeric claims lacking a matching retrieved record.
- Limitation/abstention accuracy on the 15 insufficient or unsupported cases.
- Error analysis by missing data, timestamp edges, conflicting rows, mixed-language station labels, and ambiguous questions.

No results are available at Proposal stage. Any event classification metric requires a written labeling rubric and a separate test set. A full-year or seasonal generalization claim requires later data beyond the current 2026-01 to 2026-10-29 snapshot.

## 12. Implementation mapping

| Component | Planned implementation |
|---|---|
| Current archive cleanup | `python scripts/clean_aqi_data.py` using Python standard library |
| Retrieval | Local CSV selection by station ID and time; optional MOENV API only after access/rate limits are verified |
| Quality checks | Reusable Python validation and flags; current cleanup writes a clean CSV, conflict CSV, and report |
| Analytics | Python/pandas or standard-library calculations; define deterministic reference query outputs |
| Planner/agent | Lightweight intent router and explicit tool calls; LLM integration only if available and evaluable |
| Interface | CLI or a small web interface; team to choose based on implementation capacity |
| Evaluation | Reproducible scripts and the fixed question/expected-answer set |

### Data cleanup command

After placing unmodified MOENV monthly CSV files in `data/raw/AQX_P_488_Resource/`, run from the project root:

```powershell
python scripts/clean_aqi_data.py
```

The script writes `data/processed/aqi_2026_clean.csv`, `data/processed/aqi_2026_conflicts.csv`, and `data/processed/cleaning_report.md`. The CSV outputs are ignored by Git because they are large; the script and report are tracked.

## 13. Limitations and risks

- The downloaded period is partial-year and cannot support complete 2026 seasonal summaries.
- The raw archives include repeated localized rows and 13 station-time keys with conflicting numeric values; all conflicting variants are excluded from the clean output and preserved in the conflict file.
- Four absent station IDs were recovered from unique county-plus-coordinate matches. This rule should be rechecked if additional source archives change the station metadata.
- `DataCreationDate` semantics remain to be confirmed; do not describe it as an exact physical sampling time without evidence.
- Official station readings do not represent a user's exact exposure.
- AQI and station correlations do not establish pollution sources or clinical outcomes.
- Optional low-cost sensor data would require separate calibration, siting, temporal alignment, and transferability checks.
- A team-sized question benchmark may not represent all real public questions; report the sampling rule and limits.

## 14. Team decisions for implementation

The Proposal is complete enough for review, but the team should confirm the following before implementation:

1. Whether to adopt the national MOENV AQI question-answering scope.
2. Which interface to build (CLI or small web application).
3. Which team member owns retrieval, analytics, domain-rule review, benchmark, and presentation/demo.
4. Whether there is enough time and a verified source to add live or low-cost IoT data.

These choices do not block a review of the current Proposal Document and Proposal PPT.

## 15. References

- MOENV historical AQI dataset AQX_P_488: <https://data.moenv.gov.tw/dataset/detail/aqx_p_488>
- MOENV current AQI dataset AQX_P_432: <https://data.moenv.gov.tw/dataset/detail/aqx_p_432>
- MOENV AQI definition: <https://air.moenv.gov.tw/envtopics/AirQuality_1.aspx>
- WHO global air quality guidelines (2021): <https://www.who.int/publications/i/item/9789240034228>
- WHO 2025 air-pollution science and policy summary: <https://www.who.int/publications/i/item/B09461>
- U.S. EPA, A Guide to Siting and Installing Air Sensors: <https://www.epa.gov/air-sensor-toolbox/guide-siting-and-installing-air-sensors>
- Key research references and DOI links: see `Proposal.md`, References [1]–[8].
