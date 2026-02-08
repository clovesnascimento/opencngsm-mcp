"""
OpenCngsm v3.2 - Input Validator
Validação e sanitização de inputs do usuário
"""
import re
import logging
from html import escape
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validação e sanitização de inputs
    
    Features:
    - Sanitização de HTML/JavaScript
    - Validação de URLs
    - Validação de API keys
    - Validação de e-mails
    - Validação de números de telefone
    - Remoção de caracteres perigosos
    - Limitação de tamanho
    
    Example:
        validator = InputValidator()
        
        # Sanitizar texto
        safe_text = validator.sanitize_text(user_input)
        
        # Validar API key
        is_valid = validator.validate_api_key(key, 'telegram')
    """
    
    # Padrões de validação
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PHONE_PATTERN = r'^\+?[1-9]\d{1,14}$'  # E.164 format
    
    # Padrões de API keys
    API_KEY_PATTERNS = {
        'telegram': r'^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$',
        'openai': r'^sk-[a-zA-Z0-9]{48}$',
        'anthropic': r'^sk-ant-[a-zA-Z0-9-]{95}$',
        'google': r'^AIza[a-zA-Z0-9_-]{35}$',
        'openrouter': r'^sk-or-[a-zA-Z0-9-]{48}$',
    }
    
    def __init__(
        self,
        max_text_length: int = 10000,
        max_url_length: int = 2000,
        strict_mode: bool = True
    ):
        """
        Initialize input validator
        
        Args:
            max_text_length: Tamanho máximo de texto
            max_url_length: Tamanho máximo de URL
            strict_mode: Modo estrito (mais restritivo)
        """
        self.max_text_length = max_text_length
        self.max_url_length = max_url_length
        self.strict_mode = strict_mode
        
        logger.info(f"✅ Input validator inicializado (strict={strict_mode})")
    
    def sanitize_text(self, text: str) -> str:
        """
        Remove HTML, scripts e caracteres perigosos
        
        Args:
            text: Texto a ser sanitizado
        
        Returns:
            Texto sanitizado
        """
        if not text:
            return ""
        
        # Limitar tamanho
        if len(text) > self.max_text_length:
            logger.warning(f"⚠️ Texto truncado: {len(text)} -> {self.max_text_length}")
            text = text[:self.max_text_length]
        
        # Escapar HTML
        sanitized = escape(text)
        
        # Remover javascript:
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remover data:
        sanitized = re.sub(r'data:', '', sanitized, flags=re.IGNORECASE)
        
        # Remover event handlers
        sanitized = re.sub(r'on\w+=', '', sanitized, flags=re.IGNORECASE)
        
        # Remover tags de script (caso escapem)
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remover null bytes
        sanitized = sanitized.replace('\x00', '')
        
        return sanitized
    
    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Valida URL
        
        Args:
            url: URL a ser validada
        
        Returns:
            (is_valid, error_message)
        """
        if not url:
            return False, "URL vazia"
        
        # Limitar tamanho
        if len(url) > self.max_url_length:
            return False, f"URL muito longa (max: {self.max_url_length})"
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"URL inválida: {e}"
        
        # Verificar scheme
        if parsed.scheme not in ['http', 'https']:
            return False, f"Scheme inválido: {parsed.scheme} (use http/https)"
        
        # Verificar hostname
        if not parsed.netloc:
            return False, "Hostname ausente"
        
        # Modo estrito: bloquear IPs locais
        if self.strict_mode:
            local_patterns = [
                r'^localhost',
                r'^127\.',
                r'^192\.168\.',
                r'^10\.',
                r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
            ]
            
            for pattern in local_patterns:
                if re.match(pattern, parsed.netloc):
                    return False, f"IP local bloqueado: {parsed.netloc}"
        
        return True, None
    
    def validate_email(self, email: str) -> bool:
        """
        Valida e-mail
        
        Args:
            email: E-mail a ser validado
        
        Returns:
            True se válido
        """
        if not email:
            return False
        
        return bool(re.match(self.EMAIL_PATTERN, email))
    
    def validate_phone(self, phone: str) -> bool:
        """
        Valida número de telefone (formato E.164)
        
        Args:
            phone: Número de telefone
        
        Returns:
            True se válido
        """
        if not phone:
            return False
        
        return bool(re.match(self.PHONE_PATTERN, phone))
    
    def validate_api_key(self, key: str, provider: str) -> Tuple[bool, Optional[str]]:
        """
        Valida formato de chave de API
        
        Args:
            key: Chave de API
            provider: Provedor (telegram, openai, etc.)
        
        Returns:
            (is_valid, error_message)
        """
        if not key:
            return False, "Chave vazia"
        
        # Verificar se provedor é conhecido
        if provider not in self.API_KEY_PATTERNS:
            # Sem validação específica, apenas verificar tamanho
            if len(key) < 10:
                return False, "Chave muito curta (min: 10 caracteres)"
            return True, None
        
        # Validar padrão
        pattern = self.API_KEY_PATTERNS[provider]
        if not re.match(pattern, key):
            return False, f"Formato inválido para {provider}"
        
        return True, None
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza nome de arquivo
        
        Args:
            filename: Nome do arquivo
        
        Returns:
            Nome sanitizado
        """
        if not filename:
            return "unnamed"
        
        # Remover caracteres perigosos
        sanitized = re.sub(r'[^\w\s.-]', '', filename)
        
        # Remover .. (path traversal)
        sanitized = sanitized.replace('..', '')
        
        # Limitar tamanho
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        # Remover espaços extras
        sanitized = re.sub(r'\s+', '_', sanitized)
        
        return sanitized or "unnamed"
    
    def validate_json(self, data: str) -> Tuple[bool, Optional[str]]:
        """
        Valida JSON
        
        Args:
            data: String JSON
        
        Returns:
            (is_valid, error_message)
        """
        import json
        
        if not data:
            return False, "JSON vazio"
        
        try:
            json.loads(data)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON inválido: {e}"
    
    def remove_control_characters(self, text: str) -> str:
        """
        Remove caracteres de controle
        
        Args:
            text: Texto
        
        Returns:
            Texto sem caracteres de controle
        """
        if not text:
            return ""
        
        # Remover caracteres de controle (exceto \n, \r, \t)
        cleaned = ''.join(
            char for char in text
            if char in ['\n', '\r', '\t'] or ord(char) >= 32
        )
        
        return cleaned
    
    def validate_integer(
        self,
        value: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Valida inteiro
        
        Args:
            value: Valor a ser validado
            min_value: Valor mínimo
            max_value: Valor máximo
        
        Returns:
            (is_valid, parsed_value, error_message)
        """
        try:
            parsed = int(value)
        except (ValueError, TypeError):
            return False, None, "Não é um inteiro válido"
        
        if min_value is not None and parsed < min_value:
            return False, None, f"Valor muito baixo (min: {min_value})"
        
        if max_value is not None and parsed > max_value:
            return False, None, f"Valor muito alto (max: {max_value})"
        
        return True, parsed, None


# Singleton global
_global_validator = None


def get_validator(strict_mode: bool = True) -> InputValidator:
    """
    Retorna instância global do validator
    
    Args:
        strict_mode: Modo estrito
    
    Returns:
        InputValidator instance
    """
    global _global_validator
    if _global_validator is None:
        _global_validator = InputValidator(strict_mode=strict_mode)
    return _global_validator


# Example usage
if __name__ == "__main__":
    validator = InputValidator()
    
    print("=" * 60)
    print("🔍 Input Validator - Teste")
    print("=" * 60)
    
    # Teste 1: Sanitizar texto
    print("\n✅ Teste 1: Sanitizar texto")
    dirty = "<script>alert('XSS')</script>Hello"
    clean = validator.sanitize_text(dirty)
    print(f"   Input: {dirty}")
    print(f"   Output: {clean}")
    
    # Teste 2: Validar URL
    print("\n✅ Teste 2: Validar URL")
    urls = [
        "https://google.com",
        "http://localhost:8000",
        "ftp://example.com",
    ]
    for url in urls:
        is_valid, error = validator.validate_url(url)
        print(f"   {url}: {'✅ VALID' if is_valid else f'❌ INVALID - {error}'}")
    
    # Teste 3: Validar API key
    print("\n✅ Teste 3: Validar API key")
    keys = [
        ("123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11", "telegram"),
        ("sk-invalid", "openai"),
    ]
    for key, provider in keys:
        is_valid, error = validator.validate_api_key(key, provider)
        print(f"   {provider}: {'✅ VALID' if is_valid else f'❌ INVALID - {error}'}")
    
    # Teste 4: Validar e-mail
    print("\n✅ Teste 4: Validar e-mail")
    emails = ["user@example.com", "invalid-email"]
    for email in emails:
        is_valid = validator.validate_email(email)
        print(f"   {email}: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    print("\n✅ Teste completo!")
