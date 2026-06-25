from typing import AsyncGenerator
import jwt
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db.engine import AsyncSessionLocal
from src.models.user import User

security = HTTPBearer()

JWKS_URL = "https://genuine-albacore-22.clerk.accounts.dev/.well-known/jwks.json"
jwk_client = PyJWKClient(JWKS_URL)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia inyectable que provee una sesión de base de datos asíncrona por request.
    Se asegura de cerrar la conexión cuando la request termina.
    """
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False}
        )
        clerk_id = payload.get("sub")
        if not clerk_id:
            raise HTTPException(status_code=401, detail="Token inválido")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Error en token: {str(e)}")

    result = await db.execute(select(User).where(User.clerk_id == clerk_id))
    user = result.scalars().first()
    
    if not user:
        user = User(clerk_id=clerk_id, email=f"{clerk_id}@user.local")
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user
