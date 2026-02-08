"""
Penetration Tests - Rate Limiting
Testa sistema de rate limiting
"""
import asyncio
import time
from typing import List

from core.security.rate_limiter import RateLimiter
from core.security.pentest_framework import BaseTestSuite, TestResult, TestStatus


class RateLimitingTests(BaseTestSuite):
    """
    Testes de rate limiting
    
    Valida que:
    - Rate limit é aplicado corretamente
    - Janela de tempo funciona
    - Reset funciona
    """
    
    def __init__(self):
        super().__init__("Rate Limiting Tests")
    
    async def run_all(self) -> List[TestResult]:
        """Executa todos os testes"""
        results = []
        
        # Teste 1: Rate limit básico
        result = await self.test_basic_rate_limit()
        results.append(result)
        
        # Teste 2: Múltiplos usuários
        result = await self.test_multiple_users()
        results.append(result)
        
        # Teste 3: Janela de tempo
        result = await self.test_time_window()
        results.append(result)
        
        return results
    
    async def test_basic_rate_limit(self) -> TestResult:
        """Testa rate limit básico"""
        start_time = time.time()
        
        limiter = RateLimiter(max_requests=5, window_minutes=1)
        user_id = "test_user"
        
        # Fazer 10 requisições
        allowed = 0
        blocked = 0
        
        for i in range(10):
            if limiter.check_limit(user_id):
                allowed += 1
            else:
                blocked += 1
        
        duration = time.time() - start_time
        
        # Deve permitir 5 e bloquear 5
        if allowed == 5 and blocked == 5:
            status = TestStatus.PASSED
            message = f"Rate limit enforced: {allowed} allowed, {blocked} blocked"
        else:
            status = TestStatus.FAILED
            message = f"Rate limit failed: {allowed} allowed, {blocked} blocked (expected 5/5)"
        
        return self._create_result(
            test_name="Rate Limiting: Basic Enforcement",
            status=status,
            message=message,
            details={'allowed': allowed, 'blocked': blocked},
            duration=duration
        )
    
    async def test_multiple_users(self) -> TestResult:
        """Testa isolamento entre usuários"""
        start_time = time.time()
        
        limiter = RateLimiter(max_requests=3, window_minutes=1)
        
        users = ["user1", "user2", "user3"]
        results = {}
        
        for user in users:
            allowed = 0
            for i in range(5):
                if limiter.check_limit(user):
                    allowed += 1
            results[user] = allowed
        
        duration = time.time() - start_time
        
        # Cada usuário deve ter 3 requisições permitidas
        if all(count == 3 for count in results.values()):
            status = TestStatus.PASSED
            message = "User isolation working correctly"
        else:
            status = TestStatus.FAILED
            message = f"User isolation failed: {results}"
        
        return self._create_result(
            test_name="Rate Limiting: User Isolation",
            status=status,
            message=message,
            details=results,
            duration=duration
        )
    
    async def test_time_window(self) -> TestResult:
        """Testa janela de tempo"""
        start_time = time.time()
        
        # Usar janela curta para teste (5 segundos)
        limiter = RateLimiter(max_requests=2, window_minutes=0.083)  # ~5 segundos
        user_id = "test_user_window"
        
        # Fazer 2 requisições (deve permitir)
        allowed_first = sum(1 for _ in range(2) if limiter.check_limit(user_id))
        
        # Tentar mais uma (deve bloquear)
        blocked = not limiter.check_limit(user_id)
        
        # Aguardar janela expirar
        await asyncio.sleep(6)
        
        # Tentar novamente (deve permitir)
        allowed_after = limiter.check_limit(user_id)
        
        duration = time.time() - start_time
        
        if allowed_first == 2 and blocked and allowed_after:
            status = TestStatus.PASSED
            message = "Time window working correctly"
        else:
            status = TestStatus.FAILED
            message = f"Time window failed: first={allowed_first}, blocked={blocked}, after={allowed_after}"
        
        return self._create_result(
            test_name="Rate Limiting: Time Window",
            status=status,
            message=message,
            duration=duration
        )


# Example usage
if __name__ == "__main__":
    async def main():
        tests = RateLimitingTests()
        results = await tests.run_all()
        
        print("=" * 60)
        print("🧪 Rate Limiting Tests")
        print("=" * 60)
        
        for result in results:
            status_icon = "✅" if result.status == TestStatus.PASSED else "❌"
            print(f"\n{status_icon} {result.test_name}")
            print(f"   {result.message}")
            print(f"   Duration: {result.duration:.3f}s")
        
        print()
    
    asyncio.run(main())
