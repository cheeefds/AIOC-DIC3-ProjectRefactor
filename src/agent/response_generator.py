"""Response Generator module.
Formats deterministic findings into structured, readable responses with mandatory provenance and data limits.
"""
from typing import Any, Dict, List, Optional, Set
from src.retrieval.retriever import RetrievedRow, RetrievalResult
from src.analytics.trend import TrendResult
from src.analytics.comparison import ComparisonResult
from src.analytics.baseline import PersistenceBaselineResult
from src.domain.aqi_rules import AQIVerificationResult
from src.domain.time_windows import get_pollutant_spec, format_taiwan_time, get_regulatory_caveat
from src.agent.gemini_client import GeminiClient

def generate_constrained_gemini_summary(
    client: GeminiClient,
    query: str,
    draft_facts: str,
    provenance_block: str
) -> Optional[str]:
    """Generate fluent natural language summary using Google AI Studio Gemini API under strict factual constraints."""
    if not client or not client.is_available():
        return None

    system_instruction = (
        "你是一個受限的台灣空氣品質證據分析代理人（Taiwan AQI Evidence Agent）。"
        "你的任務是根據下方【已驗證之確定性數值事實】撰寫專業、簡明、易讀的繁體中文分析回答。\n\n"
        "【嚴格準則 - 違者無效】：\n"
        "1. 嚴禁幻覺：文本中出現的所有數值（濃度、AQI、變化量、百分比、時間戳記、測站）必須 100% 取自下方提供的事實，絕對禁止自行推算、插補或捏造任何未提及的數字。\n"
        "2. 嚴格守門：不提供個人醫療處方/診斷；不以單點風向或時空相關性推論特定工廠之污染因果責任。\n"
        "3. 出處完整：回答文末必須完整保留下方提供的【資料來源與出處追溯】與【資料限制】區塊。\n"
        "4. 語氣客觀：以科學中立口吻闡述觀測事實與移動平均時窗含意。"
    )

    prompt = (
        f"使用者問題：{query}\n\n"
        f"【已驗證之確定性數值事實】：\n{draft_facts}\n\n"
        f"請整合上述事實撰寫自然流暢之回答，並在文末附上下方完整出處區塊：\n{provenance_block}"
    )

    return client.generate(prompt=prompt, system_instruction=system_instruction)

def build_provenance_block(
    retrieval_result: RetrievalResult,
    pollutant: str,
    extra_limits: Optional[List[str]] = None
) -> str:
    """Construct mandatory provenance metadata section."""
    spec = get_pollutant_spec(pollutant)
    pol_name = spec.display_name if spec else pollutant
    pol_unit = spec.unit if spec else "未知單位"
    pol_window = spec.averaging_window if spec else "依觀測發布時窗"

    # Collect unique stations
    stations_info = []
    seen_sites = set()
    for r in retrieval_result.records:
        if r.site_id not in seen_sites:
            stations_info.append(f"{r.county}{r.site_name} (SiteId: {r.site_id})")
            seen_sites.add(r.site_id)

    time_range_str = f"{retrieval_result.t_start or '未知'} 至 {retrieval_result.t_end or '未知'}"
    if retrieval_result.records:
        earliest = retrieval_result.records[0].timestamp
        latest = retrieval_result.records[-1].timestamp
        actual_window = f"{earliest} 至 {latest} (台灣時間, UTC+8)"
    else:
        actual_window = "無有效觀測時段"

    # Sample observation keys (up to 5 keys)
    keys_sample = [r.record_key for r in retrieval_result.records[:5]]
    if len(retrieval_result.records) > 5:
        keys_sample.append(f"... 等共 {len(retrieval_result.records)} 筆主鍵")
    keys_str = ", ".join(keys_sample) if keys_sample else "無"

    lines = [
        "",
        "---",
        "### 📋 資料來源與出處追溯 (Data Provenance)",
        f"- **監測測站**：{', '.join(stations_info) if stations_info else '無'}",
        f"- **觀測時段**：{actual_window}",
        f"- **指標與單位**：{pol_name}，單位：`{pol_unit}`",
        f"- **法定平均時窗**：{pol_window}",
        f"- **觀測主鍵清單**：`{keys_str}`",
        f"- **來源檔案庫**：{', '.join(retrieval_result.source_files) if retrieval_result.source_files else 'AQX_P_488 Clean Repository'}",
        "",
        "### ⚠️ 資料限制與品質聲明",
        "- **確定性計算原則**：所有數值均由本機確定性程式碼計算，絕無生成式語言模型之虛構或數值插補。",
        "- **暴露量限制**：測站數值僅代表固定測站周邊大氣監測值，不代表個人實際吸入暴露量。",
    ]

    if extra_limits:
        for el in extra_limits:
            lines.append(f"- **專屬限制**：{el}")

    return "\n".join(lines)

def format_trend_response(
    trend: TrendResult,
    retrieval: RetrievalResult,
    baseline: Optional[PersistenceBaselineResult] = None,
    gemini_client: Optional[GeminiClient] = None,
    query: str = ""
) -> str:
    """Format a comprehensive trend answer, optionally enhanced by Gemini constrained generation."""
    spec = get_pollutant_spec(trend.pollutant)
    pol_display = spec.display_name if spec else trend.pollutant
    unit = spec.unit if spec else ""

    if not trend.is_valid:
        lines = [
            f"## ❌ 無法計算趨勢：{trend.site_name}（{trend.pollutant}）",
            f"**原因**：{trend.limitation_warning}",
            f"目前在指定時段內僅檢索到 {trend.data_points_count} 筆有效觀測，無法形成時序變化分析。"
        ]
        return "\n".join(lines) + "\n" + build_provenance_block(retrieval, trend.pollutant, [trend.limitation_warning])

    pct_str = f"（變化幅度 {trend.pct_change:+.1f}%）" if trend.pct_change is not None else ""
    delta_sign = "+" if (trend.net_delta or 0) > 0 else ""

    lines = [
        f"## 📈 {trend.site_name}站 {pol_display} 趨勢分析結果",
        f"在指定分析期間內，**{trend.site_name}站**的 {pol_display} 呈現 **「{trend.direction}」** 走勢{pct_str}。",
        "",
        "### 📊 核心指標摘要",
        f"- **起始數值**：`{trend.start_val}` {unit}（時間：{format_taiwan_time(trend.start_time or '')}）",
        f"- **結束數值**：`{trend.end_val}` {unit}（時間：{format_taiwan_time(trend.end_time or '')}）",
        f"- **淨變化量**：`{delta_sign}{trend.net_delta}` {unit}",
        f"- **期間最高值**：`{trend.max_val}` {unit}（發生於 {format_taiwan_time(trend.max_time or '')}）",
        f"- **期間最低值**：`{trend.min_val}` {unit}（發生於 {format_taiwan_time(trend.min_time or '')}）",
        f"- **期間平均值**：`{trend.mean_val}` {unit}",
    ]

    if baseline:
        lines.extend([
            "",
            "### 🎯 持續性基準線（Persistence Baseline）比較",
            f"- **初始基準值 (t0)**：`{baseline.t0_value}` {unit}（{baseline.t0_timestamp}）",
            f"- **平均絕對殘差 (MAD)**：`{baseline.mean_absolute_deviation}` {unit}",
            f"- **最大正向偏離**：`+{baseline.max_positive_deviation}` {unit}",
            f"- **最大負向偏離**：`{baseline.max_negative_deviation}` {unit}（發生於 {baseline.max_deviation_time}）",
            f"說明：此基準線以 t0 讀值恆定不變為對照，殘差反映真實大氣擾動幅度。"
        ])

    caveats = []
    reg_caveat = get_regulatory_caveat(trend.pollutant)
    caveats.append(reg_caveat)

    prov_block = build_provenance_block(retrieval, trend.pollutant, caveats)
    deterministic_text = "\n".join(lines) + "\n" + prov_block

    if gemini_client and gemini_client.is_available():
        facts_summary = "\n".join(lines)
        gemini_text = generate_constrained_gemini_summary(gemini_client, query, facts_summary, prov_block)
        if gemini_text and len(gemini_text.strip()) > 30:
            return gemini_text

    return deterministic_text

def format_comparison_response(
    comp: ComparisonResult,
    retrieval: RetrievalResult,
    gemini_client: Optional[GeminiClient] = None,
    query: str = ""
) -> str:
    """Format a multi-station comparison answer, optionally enhanced by Gemini."""
    spec = get_pollutant_spec(comp.pollutant)
    pol_display = spec.display_name if spec else comp.pollutant
    unit = spec.unit if spec else ""

    if not comp.stations_ranked:
        return f"無有效測站觀測可供比較。\n" + build_provenance_block(retrieval, comp.pollutant)

    lines = [
        f"## 🏆 多測站 {pol_display} 比較與排名",
        f"依據嚴格對齊之共同時段（共 {comp.shared_timestamps_count} 小時共同資料），各測站依 **{comp.rank_metric.upper()}** 由高至低排序如下：",
        "",
        "| 排名 | 測站名稱 | 縣市 | 平均濃度 | 最高濃度 | 最低濃度 | 最新讀值 |",
        "| :---: | :--- | :--- | :---: | :---: | :---: | :---: |"
    ]

    for idx, s in enumerate(comp.stations_ranked, start=1):
        lines.append(
            f"| **{idx}** | {s.site_name} (ID: {s.site_id}) | {s.county} | `{s.mean_val}` {unit} | `{s.max_val}` | `{s.min_val}` | `{s.latest_val or '無'}` |"
        )

    if len(comp.stations_ranked) >= 2:
        top = comp.stations_ranked[0]
        bottom = comp.stations_ranked[-1]
        lines.extend([
            "",
            f"### 🔍 差異分析",
            f"- **最高污染測站**：{top.county}{top.site_name}（平均值 `{top.mean_val}` {unit}）",
            f"- **最低污染測站**：{bottom.county}{bottom.site_name}（平均值 `{bottom.mean_val}` {unit}）",
            f"- **極端平均差距**：`{comp.max_diff}` {unit}",
        ])

    caveats = []
    if comp.alignment_warning:
        caveats.append(comp.alignment_warning)
    caveats.append(get_regulatory_caveat(comp.pollutant))

    prov_block = build_provenance_block(retrieval, comp.pollutant, caveats)
    deterministic_text = "\n".join(lines) + "\n" + prov_block

    if gemini_client and gemini_client.is_available():
        facts_summary = "\n".join(lines)
        gemini_text = generate_constrained_gemini_summary(gemini_client, query, facts_summary, prov_block)
        if gemini_text and len(gemini_text.strip()) > 30:
            return gemini_text

    return deterministic_text

def format_interpretation_response(
    records: List[RetrievedRow],
    verification: AQIVerificationResult,
    retrieval: RetrievalResult,
    gemini_client: Optional[GeminiClient] = None,
    query: str = ""
) -> str:
    """Format single-station / time AQI interpretation answer, optionally enhanced by Gemini."""
    latest = records[-1] if records else None
    if not latest:
        return "查無該測站於指定時間的觀測數據。"

    lines = [
        f"## 🌿 {latest.county}{latest.site_name}站 空氣品質（AQI）解讀",
        f"在 **{format_taiwan_time(latest.timestamp)}**，測站回報狀態如下：",
        "",
        f"- **AQI 數值**：`{verification.reported_aqi or verification.calculated_aqi}`（等級：**{verification.category_name}**，顏色代碼：`{verification.color_code}`）",
        f"- **主要污染物**：`{latest.pollutant or verification.calculated_dominant_pollutant or '無指定'}`",
        f"- **民眾活動指引**：{verification.health_advice}",
        "",
        "### 🔬 逐項污染物量測與副指標驗證",
        f"- **PM2.5**：`{latest.pm2_5 or '缺測'}` μg/m³（副指標：`{verification.sub_indices.get('pm2_5', '無')}`）",
        f"- **PM10**：`{latest.pm10 or '缺測'}` μg/m³（副指標：`{verification.sub_indices.get('pm10', '無')}`）",
        f"- **O3 (8小時平均)**：`{latest.o3_8hr or '缺測'}` ppm（副指標：`{verification.sub_indices.get('o3_8hr', '無')}`）",
        f"- **SO2**：`{latest.so2 or '缺測'}` ppb（副指標：`{verification.sub_indices.get('so2', '無')}`）",
        f"- **NO2**：`{latest.no2 or '缺測'}` ppb（副指標：`{verification.sub_indices.get('no2', '無')}`）",
        f"- **風向風速**：風速 `{latest.wind_speed or '無'}` m/s，風向角 `{latest.wind_direction or '無'}`°",
    ]

    caveats = []
    if verification.discrepancy_warning:
        lines.extend([
            "",
            f"> ⚠️ **數值一致性警示**：{verification.discrepancy_warning}"
        ])
        caveats.append(verification.discrepancy_warning)

    caveats.append(get_regulatory_caveat("aqi"))
    prov_block = build_provenance_block(retrieval, "aqi", caveats)
    deterministic_text = "\n".join(lines) + "\n" + prov_block

    if gemini_client and gemini_client.is_available():
        facts_summary = "\n".join(lines)
        gemini_text = generate_constrained_gemini_summary(gemini_client, query, facts_summary, prov_block)
        if gemini_text and len(gemini_text.strip()) > 30:
            return gemini_text

    return deterministic_text
