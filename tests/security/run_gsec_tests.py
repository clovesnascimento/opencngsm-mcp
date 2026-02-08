"""
Run G-SEC Advanced Security Tests
Executa testes avançados de segurança incluindo:
- Vetores de ataque G-SEC
- Chaos Engineering
- Testes de resiliência
"""
import asyncio
from pathlib import Path

from core.security.pentest_framework import PenetrationTestFramework, TestSuite
from tests.security.test_advanced_attacks import AdvancedAttackVectorTests
from tests.security.test_chaos_engineering import ChaosEngineeringTests


async def main():
    """
    Executa suite completa de testes avançados
    """
    print("\n" + "=" * 80)
    print("🔥 OpenCngsm v3.3 - G-SEC Advanced Security Tests")
    print("=" * 80)
    print()
    
    # Criar suite
    suite = TestSuite(name="G-SEC Advanced Security Tests")
    
    # 1. Testes de vetores de ataque avançados
    print("🔥 Executando G-SEC Attack Vector Tests...")
    print()
    
    attack_tests = AdvancedAttackVectorTests()
    attack_results = await attack_tests.run_all()
    
    for result in attack_results:
        suite.add_result(result)
        status_icon = "✅" if result.status.value == "passed" else "❌"
        print(f"{status_icon} {result.test_name}")
        print(f"   {result.message}")
        print()
    
    # 2. Testes de Chaos Engineering
    print("\n" + "=" * 80)
    print("💥 Executando Chaos Engineering Tests...")
    print("=" * 80)
    print()
    
    chaos_tests = ChaosEngineeringTests()
    chaos_results = await chaos_tests.run_all()
    
    for result in chaos_results:
        suite.add_result(result)
        status_icon = "✅" if result.status.value == "passed" else "❌"
        print(f"{status_icon} {result.test_name}")
        print(f"   {result.message}")
        print()
    
    # Gerar relatórios
    print("\n" + "=" * 80)
    print("📊 Gerando Relatórios...")
    print("=" * 80)
    print()
    
    framework = PenetrationTestFramework()
    
    # Relatório em texto
    framework.generate_report(suite)
    
    # Relatório em JSON
    framework.generate_json_report(suite)
    
    # Estatísticas finais
    stats = suite.get_stats()
    success_rate = suite.success_rate()
    
    print("\n" + "=" * 80)
    print("📈 ANÁLISE FINAL - G-SEC")
    print("=" * 80)
    print()
    
    print(f"Total de testes: {stats['total']}")
    print(f"✅ Passou: {stats['passed']}")
    print(f"❌ Falhou: {stats['failed']}")
    print(f"⏭️ Pulado: {stats['skipped']}")
    print(f"⚠️ Erro: {stats['error']}")
    print()
    print(f"Taxa de sucesso: {success_rate:.1f}%")
    print()
    
    # Análise de vulnerabilidades
    if stats['failed'] > 0:
        print("🚨 VULNERABILIDADES DETECTADAS:")
        print()
        
        for result in suite.results:
            if result.status.value == "failed":
                print(f"   ❌ {result.test_name}")
                print(f"      {result.message}")
                print()
        
        print("⚠️ AÇÃO NECESSÁRIA:")
        print("   1. Revisar filtros de prompt injection")
        print("   2. Adicionar detecção de Base64 suspeito")
        print("   3. Implementar validação semântica profunda")
        print("   4. Adicionar proteção contra Self-DoS")
        print()
    
    # Conclusão
    print("=" * 80)
    print("🎯 CONCLUSÃO")
    print("=" * 80)
    print()
    
    if success_rate >= 95:
        print("✅ EXCELENTE: Sistema resistiu a ataques avançados!")
        print("   Segurança de nível militar confirmada.")
    elif success_rate >= 80:
        print("⚠️ BOM: Sistema tem defesas sólidas, mas há gaps.")
        print("   Recomenda-se implementar melhorias sugeridas.")
    elif success_rate >= 60:
        print("⚠️ ATENÇÃO: Vulnerabilidades significativas detectadas.")
        print("   Correções URGENTES necessárias.")
    else:
        print("❌ CRÍTICO: Sistema vulnerável a ataques avançados!")
        print("   NÃO USAR EM PRODUÇÃO até correções.")
    
    print()
    print("=" * 80)
    print()
    
    # Sugestões de correção
    if stats['failed'] > 0:
        print("💡 SUGESTÕES DE CORREÇÃO:")
        print()
        print("1. Validação Semântica Profunda:")
        print("   - Implementar LLM secundário para detecção de injeção")
        print("   - Usar delimitadores XML estritos (<user_input> vs <system_command>)")
        print()
        print("2. Deny-list Dinâmica:")
        print("   - Adicionar padrões como 'echo > /tmp/'")
        print("   - Detectar Base64 suspeito em contextos de comando")
        print()
        print("3. Runtime Isolado:")
        print("   - Docker com network=none")
        print("   - AppArmor profiles reforçados")
        print("   - Egress controlado")
        print()
        print("4. Proteção de Admin:")
        print("   - Whitelist de usuários admin")
        print("   - Bypass de bloqueio automático para admin")
        print()
        print("=" * 80)
        print()
    
    return 0 if success_rate >= 95 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
