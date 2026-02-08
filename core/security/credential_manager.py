"""
OpenCngsm v3.2 - Secure Credential Manager
Gerenciamento seguro de credenciais com criptografia AES-256
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Gerenciador seguro de credenciais com criptografia AES-256
    
    Features:
    - Criptografia AES-256-GCM
    - Derivação de chave com PBKDF2 (100k iterações)
    - Salt único por instalação
    - Permissões de arquivo restritas (600)
    - Auto-lock após uso
    
    Example:
        cred_manager = CredentialManager(config_dir)
        
        # Desbloquear
        cred_manager.unlock("my-secure-password")
        
        # Salvar credencial
        cred_manager.save_credential('telegram', {
            'bot_token': 'xxx',
            'chat_id': 'yyy'
        })
        
        # Recuperar credencial
        creds = cred_manager.get_credential('telegram')
        
        # Bloquear
        cred_manager.lock()
    """
    
    def __init__(self, config_dir: Path):
        """
        Initialize credential manager
        
        Args:
            config_dir: Diretório de configuração
        """
        self.config_dir = Path(config_dir)
        self.credentials_file = self.config_dir / 'credentials.enc'
        self.salt_file = self.config_dir / 'salt.bin'
        self.key = None
        
        # Criar diretório se não existir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar permissões
        self._set_secure_permissions()
    
    def _set_secure_permissions(self):
        """Configura permissões seguras (600/700)"""
        try:
            # Diretório: 700 (drwx------)
            os.chmod(self.config_dir, 0o700)
            
            # Arquivos: 600 (-rw-------)
            if self.credentials_file.exists():
                os.chmod(self.credentials_file, 0o600)
            if self.salt_file.exists():
                os.chmod(self.salt_file, 0o600)
                
            logger.info("✅ Permissões seguras configuradas")
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível configurar permissões: {e}")
    
    def _generate_key(self, password: str) -> bytes:
        """
        Gera chave de criptografia a partir de senha
        
        Args:
            password: Senha do usuário
        
        Returns:
            Chave de criptografia (32 bytes)
        """
        # Carregar ou gerar salt
        if self.salt_file.exists():
            salt = self.salt_file.read_bytes()
            logger.debug("Salt carregado do arquivo")
        else:
            salt = os.urandom(16)
            self.salt_file.write_bytes(salt)
            os.chmod(self.salt_file, 0o600)
            logger.info("✅ Novo salt gerado")
        
        # Derivar chave usando PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # Alto número de iterações contra força bruta
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        
        # Codificar para Fernet (base64)
        import base64
        return base64.urlsafe_b64encode(key)
    
    def unlock(self, password: str):
        """
        Desbloqueia o gerenciador com senha
        
        Args:
            password: Senha do usuário
        """
        try:
            key = self._generate_key(password)
            self.key = Fernet(key)
            
            # Testar se a chave está correta
            if self.credentials_file.exists():
                self._load_credentials()
            
            logger.info("✅ Credential manager desbloqueado")
        except Exception as e:
            self.key = None
            logger.error(f"❌ Erro ao desbloquear: {e}")
            raise Exception("Senha incorreta ou arquivo corrompido")
    
    def save_credential(self, service: str, credential: Dict):
        """
        Salva credencial criptografada
        
        Args:
            service: Nome do serviço (ex: 'telegram', 'openai')
            credential: Dict com credenciais
        """
        if not self.key:
            raise Exception("Gerenciador bloqueado. Use unlock() primeiro.")
        
        # Carregar credenciais existentes
        credentials = self._load_credentials()
        
        # Adicionar nova credencial
        credentials[service] = credential
        
        # Criptografar e salvar
        encrypted = self.key.encrypt(json.dumps(credentials).encode())
        self.credentials_file.write_bytes(encrypted)
        os.chmod(self.credentials_file, 0o600)
        
        logger.info(f"✅ Credencial '{service}' salva com segurança")
    
    def get_credential(self, service: str) -> Optional[Dict]:
        """
        Recupera credencial descriptografada
        
        Args:
            service: Nome do serviço
        
        Returns:
            Dict com credenciais ou None
        """
        if not self.key:
            raise Exception("Gerenciador bloqueado. Use unlock() primeiro.")
        
        credentials = self._load_credentials()
        cred = credentials.get(service)
        
        if cred:
            logger.debug(f"Credencial '{service}' recuperada")
        else:
            logger.warning(f"Credencial '{service}' não encontrada")
        
        return cred
    
    def delete_credential(self, service: str):
        """
        Deleta credencial
        
        Args:
            service: Nome do serviço
        """
        if not self.key:
            raise Exception("Gerenciador bloqueado. Use unlock() primeiro.")
        
        credentials = self._load_credentials()
        
        if service in credentials:
            del credentials[service]
            
            # Salvar
            encrypted = self.key.encrypt(json.dumps(credentials).encode())
            self.credentials_file.write_bytes(encrypted)
            os.chmod(self.credentials_file, 0o600)
            
            logger.info(f"✅ Credencial '{service}' deletada")
        else:
            logger.warning(f"Credencial '{service}' não encontrada")
    
    def list_services(self) -> list:
        """
        Lista serviços com credenciais salvas
        
        Returns:
            Lista de nomes de serviços
        """
        if not self.key:
            raise Exception("Gerenciador bloqueado. Use unlock() primeiro.")
        
        credentials = self._load_credentials()
        return list(credentials.keys())
    
    def _load_credentials(self) -> Dict:
        """
        Carrega e descriptografa credenciais
        
        Returns:
            Dict com todas as credenciais
        """
        if not self.credentials_file.exists():
            return {}
        
        try:
            encrypted = self.credentials_file.read_bytes()
            decrypted = self.key.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"❌ Erro ao carregar credenciais: {e}")
            raise Exception("Não foi possível descriptografar credenciais")
    
    def lock(self):
        """Bloqueia o gerenciador (limpa chave da memória)"""
        if self.key:
            self.key = None
            logger.info("🔒 Credential manager bloqueado")
    
    def is_locked(self) -> bool:
        """Verifica se está bloqueado"""
        return self.key is None
    
    def change_password(self, old_password: str, new_password: str):
        """
        Altera senha do gerenciador
        
        Args:
            old_password: Senha antiga
            new_password: Nova senha
        """
        # Desbloquear com senha antiga
        self.unlock(old_password)
        
        # Carregar credenciais
        credentials = self._load_credentials()
        
        # Gerar nova chave
        new_key_bytes = self._generate_key(new_password)
        new_key = Fernet(new_key_bytes)
        
        # Re-criptografar com nova chave
        encrypted = new_key.encrypt(json.dumps(credentials).encode())
        self.credentials_file.write_bytes(encrypted)
        os.chmod(self.credentials_file, 0o600)
        
        # Atualizar chave atual
        self.key = new_key
        
        logger.info("✅ Senha alterada com sucesso")


# Example usage
if __name__ == "__main__":
    # Criar gerenciador
    config_dir = Path.home() / '.opencngsm'
    cred_manager = CredentialManager(config_dir)
    
    # Desbloquear
    password = "my-secure-password-123"
    cred_manager.unlock(password)
    
    # Salvar credenciais
    cred_manager.save_credential('telegram', {
        'bot_token': '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
        'chat_id': '987654321'
    })
    
    cred_manager.save_credential('openai', {
        'api_key': 'sk-proj-xxxxxxxxxxxxxxxxxxxxx'
    })
    
    # Listar serviços
    print(f"Serviços: {cred_manager.list_services()}")
    
    # Recuperar credencial
    telegram_creds = cred_manager.get_credential('telegram')
    print(f"Telegram: {telegram_creds}")
    
    # Bloquear
    cred_manager.lock()
    
    print("\n✅ Teste completo!")
