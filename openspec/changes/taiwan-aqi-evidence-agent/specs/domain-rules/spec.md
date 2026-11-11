## ADDED Requirements

### Requirement: MOENV AQI Sub-index Validation
The system SHALL validate reported AQI values against MOENV AQI calculation rules, confirming that the overall station AQI equals the maximum of the individual pollutant sub-indices and identifying the primary pollutant (dominant contributor).

#### Scenario: Verify dominant pollutant
- **WHEN** AQI and pollutant concentrations are retrieved for a station-hour
- **THEN** system checks whether the designated primary pollutant corresponds to the maximum sub-index and flags any discrepancy

### Requirement: Averaging Window and Timezone Alignment
The system SHALL explicitly display the time aggregation window (e.g., 1-hour reading, 8-hour moving average for $O_3$, 12-hour/4-hour weighted average for $PM_{2.5}$) and ensure timestamps are unambiguously expressed in Taiwan Time (UTC+8).

#### Scenario: Clarifying time semantics
- **WHEN** presenting pollutant measurements and AQI metrics
- **THEN** system tags each metric with its regulatory averaging window and unit (e.g., $\mu g/m^3$, $ppb$, $ppm$) and notes that hourly AQI reflects moving averages rather than instantaneous exposure

### Requirement: Exposure and Causal Guardrails
The system SHALL reject or strictly qualify any user query requesting personal health diagnosis or claiming direct industrial/traffic source causation from single-station correlations.

#### Scenario: Refusal of medical advice
- **WHEN** user asks for personal clinical advice or health diagnosis based on station AQI
- **THEN** system provides general MOENV/WHO public activity guideline categories while explicitly refusing to offer personal medical advice

#### Scenario: Refusal of causal source attribution
- **WHEN** user asks whether a specific factory or highway caused a local spike based only on wind and station measurements
- **THEN** system explains that correlation and wind direction alone cannot establish source causation without dispersion modeling and emission inventories

