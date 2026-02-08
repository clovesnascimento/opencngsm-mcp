"""
OpenCngsm v3.2 - Rate Limiter
Previne abuso de requisições por usuário/IP
"""
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiting por usuário/IP/fingerprint
    
    Features:
    - Limite configurável de requisições
    - Janela de tempo deslizante
    - Múltiplos identificadores (user_id, IP, fingerprint)
    - Estatísticas de bloqueios
    - Auto-limpeza de requisições antigas
    
    Example:
        limiter = RateLimiter(max_requests=10, window_minutes=1)
        
        if not limiter.check_limit(user_id):
            raise RateLimitException("Too many requests")
    """
    
    def __init__(
        self,
        max_requests: int = 10,
        window_minutes: int = 1,
        cleanup_interval: int = 100
    ):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Número máximo de requisições
            window_minutes: Janela de tempo em minutos
            cleanup_interval: Intervalo de limpeza (a cada N verificações)
        """
        self.max_requests = max_requests
        self.window = timedelta(minutes=window_minutes)
        self.cleanup_interval = cleanup_interval
        
        # Armazenar requisições por identificador
        self.requests: Dict[str, list] = defaultdict(list)
        
        # Estatísticas
        self.blocked_count = 0
        self.total_checks = 0
        self.blocked_identifiers = set()
        
        logger.info(f"✅ Rate limiter inicializado: {max_requests} req/{window_minutes}min")
    
    def check_limit(self, identifier: str) -> bool:
        """
        Verifica se usuário excedeu limite
        
        Args:
            identifier: user_id, IP, ou fingerprint
        
        Returns:
            True se permitido, False se bloqueado
        """
        self.total_checks += 1
        now = datetime.now()
        
        # Limpar requisições antigas
        self._cleanup_old_requests(identifier, now)
        
        # Auto-limpeza periódica
        if self.total_checks % self.cleanup_interval == 0:
            self._cleanup_all()
        
        # Verificar limite
        current_count = len(self.requests[identifier])
        
        if current_count >= self.max_requests:
            self.blocked_count += 1
            self.blocked_identifiers.add(identifier)
            
            logger.warning(
                f"🚨 Rate limit exceeded for '{identifier}': "
                f"{current_count}/{self.max_requests} requests"
            )
            return False
        
        # Registrar requisição
        self.requests[identifier].append(now)
        
        logger.debug(
            f"✅ Request allowed for '{identifier}': "
            f"{current_count + 1}/{self.max_requests}"
        )
        
        return True
    
    def _cleanup_old_requests(self, identifier: str, now: datetime):
        """
        Remove requisições antigas para um identificador
        
        Args:
            identifier: Identificador do usuário
            now: Timestamp atual
        """
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window
        ]
    
    def _cleanup_all(self):
        """Remove requisições antigas de todos os identificadores"""
        now = datetime.now()
        
        # Limpar cada identificador
        for identifier in list(self.requests.keys()):
            self._cleanup_old_requests(identifier, now)
            
            # Remover identificador se não tiver mais requisições
            if not self.requests[identifier]:
                del self.requests[identifier]
        
        logger.debug(f"🧹 Cleanup: {len(self.requests)} identificadores ativos")
    
    def get_remaining(self, identifier: str) -> int:
        """
        Retorna número de requisições restantes
        
        Args:
            identifier: Identificador do usuário
        
        Returns:
            Número de requisições restantes
        """
        now = datetime.now()
        self._cleanup_old_requests(identifier, now)
        
        current_count = len(self.requests[identifier])
        remaining = max(0, self.max_requests - current_count)
        
        return remaining
    
    def get_reset_time(self, identifier: str) -> Optional[datetime]:
        """
        Retorna quando o limite será resetado
        
        Args:
            identifier: Identificador do usuário
        
        Returns:
            Timestamp do reset ou None
        """
        if not self.requests[identifier]:
            return None
        
        # Primeira requisição na janela
        oldest_request = min(self.requests[identifier])
        reset_time = oldest_request + self.window
        
        return reset_time
    
    def reset(self, identifier: str):
        """
        Reseta limite para um identificador
        
        Args:
            identifier: Identificador do usuário
        """
        if identifier in self.requests:
            del self.requests[identifier]
            logger.info(f"🔄 Rate limit resetado para '{identifier}'")
    
    def reset_all(self):
        """Reseta todos os limites"""
        self.requests.clear()
        self.blocked_count = 0
        self.blocked_identifiers.clear()
        logger.info("🔄 Todos os rate limits resetados")
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas de rate limiting
        
        Returns:
            Dict com estatísticas
        """
        return {
            'total_checks': self.total_checks,
            'blocked_count': self.blocked_count,
            'blocked_percentage': (
                (self.blocked_count / self.total_checks * 100)
                if self.total_checks > 0 else 0
            ),
            'active_identifiers': len(self.requests),
            'blocked_identifiers': list(self.blocked_identifiers),
            'max_requests': self.max_requests,
            'window_minutes': self.window.total_seconds() / 60
        }
    
    def is_blocked(self, identifier: str) -> bool:
        """
        Verifica se identificador está bloqueado
        
        Args:
            identifier: Identificador do usuário
        
        Returns:
            True se bloqueado
        """
        now = datetime.now()
        self._cleanup_old_requests(identifier, now)
        
        current_count = len(self.requests[identifier])
        return current_count >= self.max_requests


# Singleton global
_global_limiter = None


def get_limiter(
    max_requests: int = 10,
    window_minutes: int = 1
) -> RateLimiter:
    """
    Retorna instância global do rate limiter
    
    Args:
        max_requests: Número máximo de requisições
        window_minutes: Janela de tempo em minutos
    
    Returns:
        RateLimiter instance
    """
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = RateLimiter(
            max_requests=max_requests,
            window_minutes=window_minutes
        )
    return _global_limiter


# Example usage
if __name__ == "__main__":
    import time
    
    # Criar limiter (10 req/min)
    limiter = RateLimiter(max_requests=5, window_minutes=1)
    
    print("=" * 60)
    print("🚦 Rate Limiter - Teste")
    print("=" * 60)
    
    user_id = "user_123"
    
    # Fazer 7 requisições (5 permitidas, 2 bloqueadas)
    for i in range(1, 8):
        allowed = limiter.check_limit(user_id)
        remaining = limiter.get_remaining(user_id)
        
        if allowed:
            print(f"✅ Request {i}: ALLOWED (remaining: {remaining})")
        else:
            print(f"❌ Request {i}: BLOCKED (remaining: {remaining})")
            reset_time = limiter.get_reset_time(user_id)
            print(f"   Reset em: {reset_time}")
    
    # Estatísticas
    print(f"\n📊 Estatísticas:")
    stats = limiter.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Teste completo!")
