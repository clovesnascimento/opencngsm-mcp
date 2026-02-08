"""
Embeddings - Geração de embeddings semânticos
"""

from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Gera embeddings para busca semântica"""
    
    def __init__(self, model: str = "mock"):
        self.model = model
        logger.info(f"[Embeddings] Initialized with model: {model}")
    
    def generate(self, text: str) -> List[float]:
        """
        Gera embedding para um texto
        
        Returns:
            Vetor de embedding (mock: 384 dimensões)
        """
        # Mock - retorna vetor aleatório
        import random
        return [random.random() for _ in range(384)]
    
    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para múltiplos textos"""
        return [self.generate(text) for text in texts]
