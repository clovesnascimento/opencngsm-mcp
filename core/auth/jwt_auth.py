"""
JWT Authentication System
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional

class JWTAuth:
    def __init__(self, secret_key: str = "opencngsm_jwt_secret_2024"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        
    def create_token(self, user_id: str, expires_hours: int = 24) -> str:
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
