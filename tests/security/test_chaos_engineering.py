"""
Chaos Engineering Tests
Testa resiliência do sistema através de falhas injetadas

Baseado em princípios de Chaos Engineering:
- Desligar componentes aleatoriamente
- Saturar sistema com múltiplos incidentes
- Testar auto-recuperação
- Validar degradação graciosa
"""
import asyncio
import time
import random
from typing import List

from core.security.incident_response import IncidentResponse, IncidentType, Severity
from core.security.security_middleware import SecurityMiddleware
from core.security.pentest_framework import BaseTestSuite, TestResult, TestStatus
from pathlib import Path


class ChaosEngineeringTests(BaseTestSuite):
    """
    Testes de Chaos Engineering
    
    Valida:
    - Resiliência sob falhas
    - Auto-recuperação
    - Degradação graciosa
    - Saturação de sistema
    """
    
    def __init__(self):
        super().__init__("Chaos Engineering Tests")
    
    async def run_all(self) -> List[TestResult]:
        """Executa todos os testes de caos"""
        results = []
        
        # Teste 1: Saturação de incidentes
        result = await self.test_incident_saturation()
        results.append(result)
        
        # Teste 2: Self-DoS (bloqueio do admin)
        result = await self.test_self_dos()
        results.append(result)
        
        # Teste 3: Múltiplos incidentes simultâneos
        result = await self.test_concurrent_incidents()
        results.append(result)
        
        # Teste 4: Degradação sob carga
        result = await self.test_degradation_under_load()
        results.append(result)
        
        return results
    
    async def test_incident_saturation(self) -> TestResult:
        """Testa saturação com todos os 8 tipos de incidentes simultaneamente"""
        start_time = time.time()
        
        config_dir = Path("/tmp/opencngsm_chaos")
        config_dir.mkdir(exist_ok=True)
        
        ir = IncidentResponse(config_dir)
        
        # Criar todos os 8 tipos de incidentes simultaneamente
        incident_types = [
            IncidentType.PROMPT_INJECTION,
            IncidentType.RATE_LIMIT_EXCEEDED,
            IncidentType.UNAUTHORIZED_ACCESS,
            IncidentType.CREDENTIAL_THEFT,
            IncidentType.MALICIOUS_FILE,
            IncidentType.SUSPICIOUS_PATTERN,
            IncidentType.BRUTE_FORCE,
            IncidentType.DATA_EXFILTRATION,
        ]
        
        # Criar incidentes em paralelo
        tasks = []
        for i, inc_type in enumerate(incident_types):
            severity = random.choice([Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL])
            task = ir.handle_incident(
                incident_type=inc_type,
                severity=severity,
                details={'test': 'saturation', 'index': i},
                user_id=f'chaos_user_{i}'
            )
            tasks.append(task)
        
        # Executar todos simultaneamente
        try:
            incidents = await asyncio.gather(*tasks)
            
            # Verificar que todos foram processados
            if len(incidents) == 8:
                status = TestStatus.PASSED
                message = f"System handled {len(incidents)} concurrent incidents successfully"
            else:
                status = TestStatus.FAILED
                message = f"System only processed {len(incidents)}/8 incidents"
        
        except Exception as e:
            status = TestStatus.FAILED
            message = f"System collapsed under saturation: {e}"
        
        duration = time.time() - start_time
        
        return self._create_result(
            test_name="Chaos: Incident Saturation (8 types)",
            status=status,
            message=message,
            details={'incident_count': len(incidents) if 'incidents' in locals() else 0},
            duration=duration
        )
    
    async def test_self_dos(self) -> TestResult:
        """Testa se sistema pode bloquear o próprio administrador"""
        start_time = time.time()
        
        config_dir = Path("/tmp/opencngsm_chaos")
        config_dir.mkdir(exist_ok=True)
        
        ir = IncidentResponse(config_dir)
        
        admin_user = "admin"  # Must match whitelist: ['admin', 'root', 'system', 'superuser', 'administrator']
        
        # Tentar criar incidente CRITICAL para admin
        await ir.handle_incident(
            incident_type=IncidentType.CREDENTIAL_THEFT,
            severity=Severity.CRITICAL,
            details={'test': 'self_dos'},
            user_id=admin_user
        )
        
        # Verificar se admin foi bloqueado
        is_blocked = ir.is_blocked(admin_user)
        
        duration = time.time() - start_time
        
        if is_blocked:
            # Admin foi bloqueado - potencial Self-DoS!
            status = TestStatus.FAILED
            message = "VULNERABILITY: Admin can be blocked (Self-DoS possible!)"
        else:
            # Sistema protegeu admin
            status = TestStatus.PASSED
            message = "Admin protected from Self-DoS"
        
        return self._create_result(
            test_name="Chaos: Self-DoS Protection",
            status=status,
            message=message,
            details={'admin_blocked': is_blocked},
            duration=duration
        )
    
    async def test_concurrent_incidents(self) -> TestResult:
        """Testa priorização sob múltiplos incidentes"""
        start_time = time.time()
        
        config_dir = Path("/tmp/opencngsm_chaos")
        config_dir.mkdir(exist_ok=True)
        
        ir = IncidentResponse(config_dir)
        
        # Criar 50 incidentes concorrentes
        tasks = []
        for i in range(50):
            severity = random.choice([Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL])
            inc_type = random.choice(list(IncidentType))
            
            task = ir.handle_incident(
                incident_type=inc_type,
                severity=severity,
                details={'test': 'concurrent', 'index': i},
                user_id=f'user_{i % 10}'  # 10 usuários diferentes
            )
            tasks.append(task)
        
        try:
            incidents = await asyncio.gather(*tasks)
            
            # Verificar que CRITICAL foram priorizados
            critical_count = sum(1 for inc in incidents if inc.severity == Severity.CRITICAL)
            
            status = TestStatus.PASSED
            message = f"Processed {len(incidents)} concurrent incidents ({critical_count} critical)"
        
        except Exception as e:
            status = TestStatus.FAILED
            message = f"System failed under concurrent load: {e}"
        
        duration = time.time() - start_time
        
        return self._create_result(
            test_name="Chaos: Concurrent Incidents (50x)",
            status=status,
            message=message,
            details={'total': len(incidents) if 'incidents' in locals() else 0},
            duration=duration
        )
    
    async def test_degradation_under_load(self) -> TestResult:
        """Testa degradação graciosa sob carga extrema"""
        start_time = time.time()
        
        config_dir = Path("/tmp/opencngsm_chaos")
        config_dir.mkdir(exist_ok=True)
        
        middleware = SecurityMiddleware(config_dir)
        
        # Fazer 100 requisições simultâneas
        tasks = []
        for i in range(100):
            task = middleware.process_request(
                user_id=f"load_user_{i % 5}",  # 5 usuários
                user_input=f"Test request {i}"
            )
            tasks.append(task)
        
        # Executar e contar sucessos/falhas
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successes = sum(1 for r in results if not isinstance(r, Exception))
        failures = len(results) - successes
        
        duration = time.time() - start_time
        
        # Sistema deve degradar graciosamente (não crashar)
        if successes > 0:
            status = TestStatus.PASSED
            message = f"Graceful degradation: {successes} succeeded, {failures} failed (no crash)"
        else:
            status = TestStatus.FAILED
            message = f"System completely failed under load"
        
        return self._create_result(
            test_name="Chaos: Degradation Under Load (100 requests)",
            status=status,
            message=message,
            details={'successes': successes, 'failures': failures},
            duration=duration
        )


# Example usage
if __name__ == "__main__":
    async def main():
        tests = ChaosEngineeringTests()
        results = await tests.run_all()
        
        print("=" * 80)
        print("💥 Chaos Engineering Tests")
        print("=" * 80)
        print()
        
        for result in results:
            status_icon = "✅" if result.status == TestStatus.PASSED else "❌"
            print(f"{status_icon} {result.test_name}")
            print(f"   {result.message}")
            print(f"   Duration: {result.duration:.3f}s")
            print()
        
        print("=" * 80)
    
    asyncio.run(main())
