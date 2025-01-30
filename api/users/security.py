# /api/users/security.py
# 사용자 패스워드 검증

from datetime import datetime, timedelta
import bcrypt

def get_password_hash(password: str) -> str:
    """비밀번호를 해시화합니다."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호가 해시와 일치하는지 확인합니다."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
