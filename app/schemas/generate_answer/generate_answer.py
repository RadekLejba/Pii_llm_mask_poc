from pydantic import BaseModel


class Question(BaseModel):
    prompt: str
    context: str


class Answer(BaseModel):
    response: str
