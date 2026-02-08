#!/usr/bin/env python3
"""
G-SEC Complete Test Suite - Final Validation
Runs all security tests and generates comprehensive report
"""
import sys
import asyncio
import subprocess
from pathlib import Path

def run_test_suite(test_file: str, test_name: str) -> dict:
    """Run a test suite and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {test_name}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        ["python", test_file],
        cwd=str(Path(__file__).parent),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(Path(__file__).parent)}
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    return {
        "name": test_name,
        "exit_code": result.exit_code,
        "passed": result.exit_code == 0,
        "output": result.stdout
    }

def main():
    """Run all G-SEC tests"""
    print("🛡️ G-SEC COMPLETE TEST SUITE - FINAL VALIDATION")
    print("="*60)
    
    test_suites = [
        ("tests/security/test_base_gsec.py", "Base G-SEC (22 tests)"),
        ("tests/security/test_stage6_rce.py", "Stage 6: RCE Protection (4 tests)"),
        ("tests/security/test_stage7_multiturn.py", "Stage 7: Multi-Turn Jailbreak (5 tests)"),
        ("tests/security/test_stage8_supply_chain.py", "Stage 8: Supply-Chain Poisoning (5 tests)"),
        ("test_judge_bypass.py", "Stage 10.2: LLM Judge Bypass (3 tests)"),
    ]
    
    results = []
    for test_file, test_name in test_suites:
        result = run_test_suite(test_file, test_name)
        results.append(result)
    
    # Generate summary
    print(f"\n{'='*60}")
    print("📊 FINAL RESULTS SUMMARY")
    print(f"{'='*60}\n")
    
    total_passed = sum(1 for r in results if r["passed"])
    total_tests = len(results)
    
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        print(f"{status}: {result['name']}")
    
    print(f"\n{'='*60}")
    print(f"Overall Success Rate: {total_passed}/{total_tests} ({total_passed/total_tests*100:.1f}%)")
    print(f"{'='*60}\n")
    
    if total_passed == total_tests:
        print("🎉 SUCCESS! All G-SEC test suites passed!")
        print("🛡️ Classification: MILITARY-GRADE SECURITY++++")
        return 0
    else:
        print(f"⚠️ WARNING: {total_tests - total_passed} test suite(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
