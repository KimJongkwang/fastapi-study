from tokenize import Token
from fastapi import APIRouter


router = APIRouter()


@router.post("/register/{sns_type}", status_code=200, response_model=Token)
async def register(sns_type:SnsType, reg_info: models.UserRegister, session: Session = Depends(db.session)):
    # FastAPI 내 docs string에서는 ``을 넣으면 swagger에서 코드블럭 잡아줌
    """
    `회원가입 API`

    Args:
        sns_type (SnsType): 
        reg_info (models.UserRegister): 
        session (Session, optional): . Defaults to Depends(db.session).
    """
    pass