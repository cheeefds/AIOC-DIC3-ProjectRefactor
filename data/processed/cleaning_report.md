# Taiwan MOENV AQI Historical Dataset (AQX_P_488) Cleaning Report

## 1. Executive Summary
- **Audit Period**: 2026-01-01 to 2026-10-29
- **Raw CSV Files Audited**: 10
- **Total Raw Input Rows**: 979,537
- **Valid Clean Observations**: 610,758
- **Isolated Conflict Groups**: 8
- **Total Conflicting / Unresolved Rows**: 20
- **Recovered SiteId Count**: 0

## 2. File-level Integrity & MD5 Checksums

| File Name | File Size (Bytes) | Row Count | MD5 Checksum |
| :--- | :--- | :--- | :--- |
| `空氣品質指標(AQI)(歷史資料) (2026-01).csv` | 9,028,556 | 64,686 | `a8b043c21383d0da508101a677506cdd` |
| `空氣品質指標(AQI)(歷史資料) (2026-02).csv` | 8,000,720 | 57,035 | `abd3bb07474c87ede92ace53ac9ff0eb` |
| `空氣品質指標(AQI)(歷史資料) (2026-03).csv` | 17,217,526 | 125,256 | `a44684145db6c54e49c30d5e7e352e47` |
| `空氣品質指標(AQI)(歷史資料) (2026-04).csv` | 16,593,652 | 120,288 | `d2fc4e4fdbcfb4eff9551996db854e08` |
| `空氣品質指標(AQI)(歷史資料) (2026-05).csv` | 16,657,188 | 124,656 | `5df436f3d7eb6e959d5448fed0910339` |
| `空氣品質指標(AQI)(歷史資料) (2026-06).csv` | 15,554,904 | 120,035 | `8ecfe78d5b6e28ea0eb3b63bde69240a` |
| `空氣品質指標(AQI)(歷史資料) (2026-07).csv` | 7,924,798 | 62,325 | `99b343e1073a2bbaccc8864458dc879c` |
| `空氣品質指標(AQI)(歷史資料) (2026-08).csv` | 9,964,897 | 77,868 | `8cb8c726cfd941fa81fd5a5b31db301b` |
| `空氣品質指標(AQI)(歷史資料) (2026-09).csv` | 13,677,856 | 102,648 | `d962ca7c4ba37c40b77579dbfd006961` |
| `空氣品質指標(AQI)(歷史資料) (2026-10).csv` | 16,923,032 | 124,740 | `9fe58917f032960179b6d4ffa84c5bb7` |

## 3. Data Cleaning & Integrity Policies Applied
- **Sentinel Normalization**: `-`, `--`, `NA`, and blank strings converted to NULL/None.
- **Primary Key Deduplication**: Grouped on `(SiteId, DataCreationDate)`. Identical observations safely merged.
- **Conflict Isolation**: All variants with conflicting measurements excluded from clean dataset and logged.
- **Spatial SiteId Recovery**: Missing `SiteId` filled ONLY when county and coordinates uniquely matched a known station.

---
*Report generated automatically by Taiwan Air Quality Evidence Agent pipeline.*