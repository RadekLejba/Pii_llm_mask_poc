from fastapi import APIRouter

from api.generate_answer import generate_answer

api_router = APIRouter()
api_router.include_router(generate_answer.router, tags=["generate_answer"])
