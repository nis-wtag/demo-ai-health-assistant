from core.limiter import limiter
from fastapi import APIRouter, Depends, Request
from models.user import User
from schemas.chat_schema import ChatQuery, ChatResponse
from services.dependencies.auth_dependencies import get_current_user
from services.llm_query_service import QueryService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=200,
    summary="Process a user chat query",
)
@limiter.limit("10/minute")
def process_chat_query(
    request: Request,
    chat_in: ChatQuery,
    current_user: User = Depends(get_current_user),
    query_service: QueryService = Depends(),
):
    return query_service.process_user_query(user_query=chat_in.query)
