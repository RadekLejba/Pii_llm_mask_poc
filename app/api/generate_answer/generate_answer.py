import os

from api.generate_answer.mask import PII_Mask
from fastapi import APIRouter
from huggingface_hub import AsyncInferenceClient
from schemas.generate_answer.generate_answer import Answer, Question


router = APIRouter()

client = AsyncInferenceClient(
    os.environ["HUGGINGFACE_MODEL"],
    token=os.environ["HUGGINGFACE_TOKEN"],
)


@router.post(
    "/generate_answer/",
    response_model=Answer,
)
async def generate_answer(question: Question) -> Answer:
    """
    Endpoint for generating an answer to a question. It will mask any PII data
    and send the masked text to the Hugging Face model for completion. The
    response will be unmasked before returning it to the
    user.
    Hugging face model does not support additional context, so it is merged
    with the question prompt.
    """
    message = f"question: {question.prompt} context: {question.context}"
    mask = PII_Mask(message)
    stream = await client.chat.completions.create(
        messages=[{"role": "user", "content": mask.masked_text}],
        stream=True,
    )
    full_text = ""
    async for chunk in stream:
        full_text += chunk.choices[0].delta.content or ""

    unmasked_text = mask.unmask(full_text)
    return Answer(response=unmasked_text)
