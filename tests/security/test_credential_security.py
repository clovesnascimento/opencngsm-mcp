"""
Penetration Tests - Credential Security
Testa segurança de credenciais
"""
import time
from typing import List
from pathlib import Path
import tempfile

from core.security.credential_manager import CredentialManager
from core.security.pentest_framework import BaseTestSuite, TestResult, TestStatus


class CredentialSecurityTests(BaseTestSuite):
    """
    Testes de segurança de credenciais
    
    Valida que:
    - Credenciais são criptografadas
    - Não há vazamento de dados
    - Permissões de arquivo estão corretas
    """
    
    def __init__(self):
        super().__init__("Credential Security Tests")
    
    async def run_all(self) -> List[TestResult]:
        """Executa todos os testes"""
        results = []
        
        # Teste 1: Criptografia
        result = await self.test_encryption()
        results.append(result)
        
        # Teste 2: Sem vazamento
        result = await self.test_no_leakage()
        results.append(result)
        
        # Teste 3: Permissões de arquivo
        result = await self.test_file_permissions()
        results.append(result)
        
        return results
    
    async def test_encryption(self) -> TestResult:
        """Testa que credenciais são criptografadas"""
        start_time = time.time()
        
        # Criar diretório temporário
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            cred_manager = CredentialManager(config_dir)
            
            # Salvar credencial
            cred_manager.unlock("test_password")
            cred_manager.save_credential('test_service', {
                'api_key': 'secret123',
                'token': 'very_secret_token'
            })
            cred_manager.lock()
            
            # Verificar que arquivo está criptografado
            encrypted_file = config_dir / 'credentials.enc'
            if not encrypted_file.exists():
                return self._create_result(
                    test_name="Credential Security: Encryption",
                    status=TestStatus.FAILED,
                    message="Credentials file not created",
                    duration=time.time() - start_time
                )
            
            content = encrypted_file.read_text()
            
            # Não deve conter as chaves em texto plano
            if 'secret123' in content or 'very_secret_token' in content:
                status = TestStatus.FAILED
                message = "Credentials NOT encrypted (found in plaintext)"
            else:
                status = TestStatus.PASSED
                message = "Credentials properly encrypted"
        
        duration = time.time() - start_time
        
        return self._create_result(
            test_name="Credential Security: Encryption",
            status=status,
            message=message,
            duration=duration
        )
    
    async def test_no_leakage(self) -> TestResult:
        """Testa que não há vazamento de credenciais"""
        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            cred_manager = CredentialManager(config_dir)
            
            # Salvar credencial
            cred_manager.unlock("test_password")
            cred_manager.save_credential('test', {'api_key': 'secret123'})
            
            # Tentar acessar sem senha (deve falhar)
            cred_manager.lock()
            
            try:
                creds = cred_manager.get_credential('test')
                # Se conseguiu acessar, há vazamento
                status = TestStatus.FAILED
                message = "Credentials accessible without password (LEAK!)"
            except Exception:
                # Esperado: deve falhar
                status = TestStatus.PASSED
                message = "Credentials protected (no leakage)"
        
        duration = time.time() - start_time
        
        return self._create_result(
            test_name="Credential Security: No Leakage",
            status=status,
            message=message,
            duration=duration
        )
    
    async def test_file_permissions(self) -> TestResult:
        """Testa permissões de arquivo"""
        start_time = time.time()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            cred_manager = CredentialManager(config_dir)
            
            cred_manager.unlock("test_password")
            cred_manager.save_credential('test', {'api_key': 'secret'})
            
            # Verificar permissões (deve ser 600 no Unix)
            import os
            import stat
            
            encrypted_file = config_dir / 'credentials.enc'
            
            if os.name == 'posix':  # Unix/Linux/Mac
                file_stat = encrypted_file.stat()
                permissions = stat.filemode(file_stat.st_mode)
                
                # Deve ser -rw------- (600)
                if permissions == '-rw-------':
                    status = TestStatus.PASSED
                    message = f"File permissions correct: {permissions}"
                else:
                    status = TestStatus.FAILED
                    message = f"File permissions incorrect: {permissions} (expected -rw-------)"
            else:
                # Windows: pular teste
                status = TestStatus.SKIPPED
                message = "File permissions test skipped on Windows"
        
        duration = time.time() - start_time
        
        return self._create_result(
            test_name="Credential Security: File Permissions",
            status=status,
            message=message,
            duration=duration
        )


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        tests = CredentialSecurityTests()
        results = await tests.run_all()
        
        print("=" * 60)
        print("🧪 Credential Security Tests")
        print("=" * 60)
        
        for result in results:
            status_icon = {
                TestStatus.PASSED: "✅",
                TestStatus.FAILED: "❌",
                TestStatus.SKIPPED: "⏭️"
            }.get(result.status, "❓")
            
            print(f"\n{status_icon} {result.test_name}")
            print(f"   {result.message}")
            print(f"   Duration: {result.duration:.3f}s")
        
        print()
    
    asyncio.run(main())
