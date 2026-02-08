#!/usr/bin/env python3
"""
G-SEC Metrics Exporter for Prometheus
Reads Garak and PromptFuzz reports and exposes metrics
"""
import json
import time
from pathlib import Path
from prometheus_client import start_http_server, Gauge, Counter
from flask import Flask

# Prometheus metrics
gsec_adversarial_score = Gauge('gsec_adversarial_success_rate', 'Overall adversarial success rate')
gsec_judge_bypass_score = Gauge('gsec_judge_bypass_success_rate', 'Judge bypass protection rate')
gsec_config_mod_score = Gauge('gsec_config_modification_success_rate', 'Config modification protection rate')
gsec_reflection_score = Gauge('gsec_reflection_leak_success_rate', 'Reflection leak protection rate')
gsec_jailbreak_score = Gauge('gsec_jailbreak_success_rate', 'Jailbreak/DAN protection rate')
gsec_prompt_leak_score = Gauge('gsec_prompt_leaking_success_rate', 'Prompt leaking protection rate')
gsec_rce_score = Gauge('gsec_rce_success_rate', 'RCE protection rate')
gsec_supply_chain_score = Gauge('gsec_supply_chain_success_rate', 'Supply chain protection rate')

gsec_total_tests = Counter('gsec_total_tests', 'Total number of adversarial tests run')
gsec_last_test_timestamp = Gauge('gsec_last_test_timestamp', 'Timestamp of last test execution')

# Configuration
REPORT_DIR = Path("/app/reports")
PROMPTFUZZ_DIR = Path("/app/promptfuzz_reports")
UPDATE_INTERVAL = 60  # seconds

def parse_garak_reports():
    """Parse Garak JSON reports and extract metrics"""
    latest_dir = max(REPORT_DIR.glob("*/garak"), default=None, key=lambda p: p.stat().st_mtime)
    
    if not latest_dir or not latest_dir.exists():
        print("No Garak reports found")
        return
    
    scores = {
        'judge_bypass': 0,
        'config_modification': 0,
        'reflection_leak': 0,
        'jailbreak': 0,
        'prompt_leaking': 0,
        'rce': 0,
        'supply_chain': 0,
    }
    
    total_prompts = 0
    blocked_prompts = 0
    
    for report_file in latest_dir.glob("gsec_adversarial_*.json"):
        try:
            data = json.loads(report_file.read_text())
            probe_name = data.get("probe", "unknown")
            total = data.get("total_prompts", 0)
            blocked = data.get("blocked_prompts", 0)
            
            total_prompts += total
            blocked_prompts += blocked
            
            if total > 0:
                score = (blocked / total) * 100
                
                # Map probe names to metrics
                if 'judge_bypass' in probe_name:
                    scores['judge_bypass'] = score
                elif 'config_modification' in probe_name:
                    scores['config_modification'] = score
                elif 'reflection' in probe_name:
                    scores['reflection_leak'] = score
                elif 'jailbreak' in probe_name:
                    scores['jailbreak'] = score
                elif 'prompt_leaking' in probe_name:
                    scores['prompt_leaking'] = score
                elif 'rce' in probe_name:
                    scores['rce'] = score
                elif 'supply_chain' in probe_name:
                    scores['supply_chain'] = score
        
        except Exception as e:
            print(f"Error parsing {report_file}: {e}")
    
    # Update Prometheus metrics
    if total_prompts > 0:
        overall_score = (blocked_prompts / total_prompts) * 100
        gsec_adversarial_score.set(overall_score)
    
    gsec_judge_bypass_score.set(scores['judge_bypass'])
    gsec_config_mod_score.set(scores['config_modification'])
    gsec_reflection_score.set(scores['reflection_leak'])
    gsec_jailbreak_score.set(scores['jailbreak'])
    gsec_prompt_leak_score.set(scores['prompt_leaking'])
    gsec_rce_score.set(scores['rce'])
    gsec_supply_chain_score.set(scores['supply_chain'])
    
    gsec_total_tests.inc(total_prompts)
    gsec_last_test_timestamp.set(time.time())
    
    print(f"✅ Metrics updated: Overall={overall_score:.1f}%, Judge={scores['judge_bypass']:.1f}%, Config={scores['config_modification']:.1f}%")

def main():
    """Main metrics exporter loop"""
    print("🛡️ G-SEC Metrics Exporter starting...")
    print(f"Report directory: {REPORT_DIR}")
    print(f"Update interval: {UPDATE_INTERVAL}s")
    
    # Start Prometheus HTTP server
    start_http_server(8080)
    print("✅ Metrics server started on :8080/metrics")
    
    # Continuous update loop
    while True:
        try:
            parse_garak_reports()
        except Exception as e:
            print(f"❌ Error updating metrics: {e}")
        
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
