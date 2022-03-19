from fastapi import Request, APIRouter

router = APIRouter(prefix="/services")


@router.get("")
async def get_all_service(request: Request):
    return dict(your_email=request.state.user.email)
