from fastapi import APIRouter , Depends, Request
from fastapi.responses import JSONResponse
import config

router = APIRouter(prefix="/paraphrase",tags=["paraphrase"])

@router.get("/royal")
async def paraphrase_to_royal(text: str, request: Request):
    response = await request.get(f"{config.Ollama_API_URL}/royal", params={"text": text})
    royal_text = response.text
    return JSONResponse({"original": text, "paraphrased": royal_text})