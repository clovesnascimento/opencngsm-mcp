"""
Run Complete G-SEC Advanced Test Suite
Executa suite completa incluindo:
- Vetores de ataque avançados (7 testes)
- Cadeia de ataque multi-estágio (6 testes)
- Chaos cognitive fuzzing (5 testes)
- Chaos engineering (4 testes)

Total: 22 testes avançados
"""
import sys
import asyncio
from pathlib import Path

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from core.security.pentest_framework import PenetrationTestFramework, TestSuite
from tests.security.test_advanced_attacks import AdvancedAttackVectorTests
from tests.security.test_attack_chain import MultiStageAttackChainTests
from tests.security.test_cognitive_fuzzing import ChaosCognitiveFuzzingTests
from tests.security.test_chaos_engineering import ChaosEngineeringTests


async def main():
    """
    Executa suite COMPLETA de testes G-SEC avançados
    """
    print("\n" + "=" * 80)
    print("🔥 OpenCngsm v3.3 - COMPLETE G-SEC Advanced Security Test Suite")
    print("=" * 80)
    print()
    
    # Criar suite
    suite = TestSuite(name="Complete G-SEC Advanced Security Tests")
    
    # 1. Advanced Attack Vectors (7 testes)
    print("🔥 [1/4] Advanced Attack Vector Tests...")
    print("=" * 80)
    
    attack_tests = AdvancedAttackVectorTests()
    attack_results = await attack_tests.run_all()
    
    for result in attack_results:
        suite.add_result(result)
        status_icon = "✅" if result.status.value == "passed" else "❌"
        print(f"{status_icon} {result.test_name}: {result.message}")
    
    # 2. Multi-Stage Attack Chain (6 testes)
    print("\n" + "=" * 80)
    print("🔥 [2/4] Multi-Stage Attack Chain Tests...")
    print("=" * 80)
    
    chain_tests = MultiStageAttackChainTests()
    chain_results = await chain_tests.run_all()
    
    for result in chain_results:
        suite.add_result(result)
        status_icon = "✅" if result.status.value == "passed" else "❌"
        print(f"{status_icon} {result.test_name}: {result.message}")
    
    # 3. Chaos Cognitive Fuzzing (5 testes)
    print("\n" + "=" * 80)
    print("💥 [3/4] Chaos Cognitive Fuzzing Tests...")
    print("=" * 80)
    
    fuzzing_tests = ChaosCognitiveFuzzingTests()
    fuzzing_results = await fuzzing_tests.run_all()
    
    for result in fuzzing_results:
        suite.add_result(result)
        status_icon = "✅" if result.status.value == "passed" else "❌"
        print(f"{status_icon} {result.test_name}: {result.message}")
    
    # 4. Chaos Engineering (4 testes)
    print("\n" + "=" * 80)
    print("💥 [4/4] Chaos Engineering Tests...")
    print("=" * 80)
    
    chaos_tests = ChaosEngineeringTests()
    chaos_results = await chaos_tests.run_all()
    
    for result in chaos_results:
        suite.add_result(result)
        status_icon = "✅" if result.status.value == "passed" else "❌"
        print(f"{status_icon} {result.test_name}: {result.message}")
    
    # Gerar relatórios
    print("\n" + "=" * 80)
    print("📊 Generating Reports...")
    print("=" * 80)
    
    framework = PenetrationTestFramework()
    framework.generate_report(suite)
    framework.generate_json_report(suite)
    
    # Análise final
    stats = suite.get_stats()
    success_rate = suite.success_rate()
    
    print("\n" + "=" * 80)
    print("📈 FINAL ANALYSIS - COMPLETE G-SEC SUITE")
    print("=" * 80)
    print()
    
    print(f"Total Tests: {stats['total']}")
    print(f"✅ Passed: {stats['passed']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"⏭️ Skipped: {stats['skipped']}")
    print(f"⚠️ Error: {stats['error']}")
    print()
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    # Análise por categoria
    print("=" * 80)
    print("📊 BREAKDOWN BY CATEGORY")
    print("=" * 80)
    print()
    
    categories = {
        'Advanced Attacks': attack_results,
        'Attack Chain': chain_results,
        'Cognitive Fuzzing': fuzzing_results,
        'Chaos Engineering': chaos_results,
    }
    
    for category, results in categories.items():
        passed = sum(1 for r in results if r.status.value == "passed")
        total = len(results)
        rate = (passed / total * 100) if total > 0 else 0
        
        status_icon = "✅" if rate >= 95 else "⚠️" if rate >= 80 else "❌"
        print(f"{status_icon} {category}: {passed}/{total} ({rate:.1f}%)")
    
    print()
    
    # Vulnerabilidades críticas
    if stats['failed'] > 0:
        print("=" * 80)
        print("🚨 CRITICAL VULNERABILITIES DETECTED")
        print("=" * 80)
        print()
        
        for result in suite.results:
            if result.status.value == "failed":
                print(f"❌ {result.test_name}")
                print(f"   {result.message}")
                print()
    
    # Recomendações
    print("=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    if success_rate >= 95:
        print("✅ EXCELLENT: System is highly resilient to advanced attacks")
        print("   - Military-grade security confirmed")
        print("   - Ready for production deployment")
    elif success_rate >= 80:
        print("⚠️ GOOD: System has solid defenses but gaps exist")
        print("   - Implement suggested fixes")
        print("   - Re-run tests before production")
    elif success_rate >= 60:
        print("⚠️ WARNING: Significant vulnerabilities detected")
        print("   - URGENT fixes required")
        print("   - DO NOT deploy to production")
    else:
        print("❌ CRITICAL: System is vulnerable to advanced attacks")
        print("   - IMMEDIATE action required")
        print("   - Complete security overhaul needed")
    
    print()
    
    # Correções prioritárias
    if stats['failed'] > 0:
        print("=" * 80)
        print("🔧 PRIORITY FIXES")
        print("=" * 80)
        print()
        
        print("1. Enhanced Prompt Filter:")
        print("   - Multilingual detection (PT, ES, FR)")
        print("   - Base64 suspicious pattern detection")
        print("   - Unicode normalization")
        print("   - Framing pattern detection")
        print()
        
        print("2. Permission Hardening:")
        print("   - Deny: env, printenv, curl, wget, nslookup")
        print("   - Deny: cat ~/.config/*, echo >> *, mkdir -p")
        print("   - Ask: all file write operations")
        print()
        
        print("3. Runtime Isolation:")
        print("   - Docker with network=none")
        print("   - Read-only filesystem")
        print("   - Ephemeral containers (discard after session)")
        print()
        
        print("4. Semantic Validation:")
        print("   - Secondary LLM judge for tool calls")
        print("   - XML delimiters for user input")
        print("   - Context rotation every 4-6 turns")
        print()
        
        print("5. Admin Protection:")
        print("   - Whitelist admin users")
        print("   - Bypass auto-block for admins")
        print("   - Manual confirmation for critical actions")
        print()
    
    print("=" * 80)
    print()
    
    return 0 if success_rate >= 95 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
