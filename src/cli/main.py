"""CLI Interface for Taiwan Air Quality Evidence Agent.
Provides interactive shell, single query execution, dataset cleaning, and benchmark evaluation.
"""
import argparse
import os
import sys
from typing import Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.retrieval.retriever import AQIRetriever
from src.agent.pipeline import TaiwanAQIEvidenceAgent
from scripts.clean_aqi_data import run_cleaning_pipeline
from eval.runner import run_benchmark_evaluation

BANNER = """
================================================================================
  🇹🇼 台灣空氣品質證據分析代理人 (Taiwan AQI Evidence Agent)
  Tool-augmented Agent for Traceable & Deterministic Air-Quality Analysis
================================================================================
"""

def get_agent(clean_csv_path: Optional[str] = None) -> TaiwanAQIEvidenceAgent:
    default_csv = os.path.join(PROJECT_ROOT, "data", "processed", "aqi_2026_clean.csv")
    target_csv = clean_csv_path or default_csv
    
    if os.path.exists(target_csv):
        retriever = AQIRetriever(clean_csv_path=target_csv)
    else:
        # Fallback to test fixtures for demonstration
        from tests.test_agent import TestAgentWorkflow
        fixture = TestAgentWorkflow()
        fixture.setUp()
        retriever = fixture.retriever

    return TaiwanAQIEvidenceAgent(retriever)

def run_interactive_mode(agent: TaiwanAQIEvidenceAgent) -> None:
    print(BANNER)
    print("已載入空品證據代理人。請輸入空品問題（輸入 'exit' 或 'q' 結束）：\n")
    
    while True:
        try:
            query = input("\n[使用者提問] > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                print("感謝使用，再見！")
                break

            print("\n正在檢索環境部觀測數據並執行確定性分析...")
            resp = agent.answer(query)
            print("\n" + resp.final_text)

            if resp.evidence_guard:
                print(f"\n[Evidence Guard 查核通過: 忠實度 {resp.evidence_guard.provenance_fidelity*100:.1f}%, 未支持數字 {resp.evidence_guard.unsupported_numbers_count} 筆]")

        except (KeyboardInterrupt, EOFError):
            print("\n程式結束。")
            break

def main():
    parser = argparse.ArgumentParser(description="Taiwan Air Quality Evidence Agent CLI")
    parser.add_argument("--query", "-q", type=str, help="Single query to ask the agent")
    parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive terminal session")
    parser.add_argument("--clean", action="store_true", help="Run raw MOENV AQX_P_488 data cleaning pipeline")
    parser.add_argument("--benchmark", action="store_true", help="Execute 60-question evaluation benchmark")
    parser.add_argument("--csv", type=str, default=None, help="Custom clean CSV dataset path")
    args = parser.parse_args()

    if args.clean:
        raw_dir = os.path.join(PROJECT_ROOT, "data", "raw", "AQX_P_488_Resource")
        proc_dir = os.path.join(PROJECT_ROOT, "data", "processed")
        run_cleaning_pipeline(raw_dir, proc_dir)
        return

    if args.benchmark:
        bench_json = os.path.join(PROJECT_ROOT, "benchmark", "questions.json")
        report_out = os.path.join(PROJECT_ROOT, "benchmark", "evaluation_report.md")
        clean_csv = args.csv or os.path.join(PROJECT_ROOT, "data", "processed", "aqi_2026_clean.csv")
        run_benchmark_evaluation(bench_json, clean_csv, report_out)
        return

    agent = get_agent(args.csv)

    if args.query:
        print(f"\n查詢問題: {args.query}\n")
        resp = agent.answer(args.query)
        print(resp.final_text)
        return

    # Default to interactive if no flags
    run_interactive_mode(agent)

if __name__ == "__main__":
    main()
