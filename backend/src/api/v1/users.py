from fastapi import APIRouter, Depends
from src.api.deps import get_current_user
from src.models.user import User

router = APIRouter()

@router.get("/me/coins")
async def get_my_coins(user: User = Depends(get_current_user)):
    return {"credits_remaining": user.credits_remaining}
