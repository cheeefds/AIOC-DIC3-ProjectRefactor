"""Exposure, Health, and Causal Attribution Guardrails module.
Intercepts inappropriate queries asking for personal medical diagnosis or unsupported industrial causal attribution.
"""
import re
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class GuardrailCheckResult:
    is_blocked: bool
    guardrail_type: Optional[str]  # "MEDICAL_DIAGNOSIS", "CAUSAL_ATTRIBUTION", or None
    policy_response: Optional[str]

# Patterns for personal clinical / medical diagnosis queries
MEDICAL_PATTERNS = [
    r"(我|小孩|長輩|家人|患者).*(過敏|氣喘|咳嗽|肺癌|就醫|看醫生|吃藥|開藥|診斷|生病|身體不適)",
    r"(該不該|要不要|能不(能|可以)).*(吃藥|看診|掛號|治療)",
    r"(會不會|是不是).*(得肺癌|得慢性阻塞|得COPD|引發心臟病)",
    r"(醫師|醫生|醫療建議|用藥建議)",
]

# Patterns for causal source attribution queries
CAUSAL_PATTERNS = [
    r"(工廠|廠|電廠|台塑|台化|中鋼|中油|焚化爐|工業區|車流|交通|煙囪).*(偷排|排放|排毒|造成|導致|元兇|罪魁禍首|是誰害的|害的|污染源)",
    r"(偷排|排放|放毒|排毒).*(造成|導致|是不是|使|讓|害)",
    r"(是不是|是否為|是不是因為|歸因於|造成|導致).*(工廠|廠|電廠|工業區|鋼鐵廠|火力|排氣管|柴油車|車流|交通|偷排|排放|排毒)",
    r"(是誰造成|誰是元兇|是哪家工廠|是哪家企業|責任歸屬|元兇|罪魁禍首|害的)",
]

def check_guardrails(query_text: str) -> GuardrailCheckResult:
    """Evaluate query text against domain guardrails.
    
    Returns GuardrailCheckResult indicating if the query must be intercepted.
    """
    cleaned = query_text.strip().lower()

    # 1. Check medical diagnosis queries
    for pat in MEDICAL_PATTERNS:
        if re.search(pat, cleaned):
            return GuardrailCheckResult(
                is_blocked=True,
                guardrail_type="MEDICAL_DIAGNOSIS",
                policy_response=(
                    "【醫療與健康守門聲明】\n"
                    "本系統僅提供環境部官方空氣品質監測站之客觀大氣濃度與 AQI 分級資訊，"
                    "測站數據代表監測站周遭大氣環境，絕不等於個人吸入暴露量，"
                    "且系統非醫療專業人員，無法提供個人化醫療診斷、臨床處方或用藥建議。\n\n"
                    "若您或家人有身體不適、氣喘、胸悶或過敏症狀，請儘速諮詢專業合格醫師。\n"
                    "日常防護請參考環境部/WHO 之各等級活動指引（如 AQI 橘色警戒以上時，敏感族群減少戶外劇烈活動）。"
                )
            )

    # 2. Check causal attribution queries
    for pat in CAUSAL_PATTERNS:
        if re.search(pat, cleaned):
            return GuardrailCheckResult(
                is_blocked=True,
                guardrail_type="CAUSAL_ATTRIBUTION",
                policy_response=(
                    "【污染源因果推論限制聲明】\n"
                    "本系統基於環境部 AQX_P_488 測站逐時監測資料，僅能呈現特定測站與時間之濃度、變化趨勢及測站間數值比較。\n\n"
                    "科學與法規界定：單一或少數地面測站之濃度變化與當下風向、風速之時空相關性，"
                    "在缺乏完整排放清冊、網格化氣象場及大氣化學傳輸擴散模式（Dispersion Modeling）嚴格模擬前，"
                    "不能單獨作為特定工廠、電廠或車流排放因果責任之法律或科學歸因證明。\n\n"
                    "系統依領域守門政策，拒絕對特定排放源進行未驗證之因果指控。"
                )
            )

    return GuardrailCheckResult(
        is_blocked=False,
        guardrail_type=None,
        policy_response=None
    )
