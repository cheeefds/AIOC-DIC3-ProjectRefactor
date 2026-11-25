# Design: 003-Proposed Design Section

## 1. PA~PM Module Mapping
- **PA (Aim)**: Verifiable Taiwan AQI question answering.
- **PB (Background)**: Cleaned MOENV AQX_P_488 dataset covering 88 stations.
- **PC (Cure)**: Separation of language generation from deterministic arithmetic.
- **PD (Design)**: Shift from conversational chatbots to tool-augmented deterministic agents.
- **PE (Elements)**: 9 processing stages (User Query to Provenanced Answer).
- **PF (Formulation)**: Planner, Quality Guard, Analytics, AQI Rules, Evidence Guard.
- **PG (Graph)**: Data flow and verification checkpoints.
- **PH (How)**: Primary observation key $(SiteId, DataCreationDate)$.
- **PI (Implementation)**: Algorithm 1 formal pseudocode (14 numbered lines).
- **PJ (Jump to example)**: Trend, comparison, and interpretation use cases.
- **PK (Key points & limits)**: Guardrails prohibiting clinical diagnosis and speculative causation.
- **PL (Later simulation)**: Real-time AQX_P_432 and IoT network expansion.
- **PM (Math proof)**: Statutory max-subindex calculation $\text{AQI} = \max_i (\text{SubIndex}_i)$.
