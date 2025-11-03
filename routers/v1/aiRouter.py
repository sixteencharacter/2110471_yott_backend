from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import requests
from config import Ollama_API_URL
from typing import Annotated
from utils import validate_access_token

router = APIRouter(prefix="/paraphrase", tags=["paraphrase"])

# Request model for JSON body
class ParaphraseRequest(BaseModel):
    text: str

@router.post("/royal")
async def paraphrase_to_royal(
    request: ParaphraseRequest, 
    userData: Annotated[dict, Depends(validate_access_token)]
):
    print("[LOG] Starting paraphrase request for:", request.text)

    try:
        # First try non-streaming to test basic connectivity
        ollama_payload = {
            "model": "yott-agent", 
            "prompt": f"Paraphrase this text in royal, fancy English language: '{request.text}'", 
            "stream": False
        }
        
        print(f"[LOG] Sending request to: {Ollama_API_URL}/api/generate")
        print(f"[LOG] Payload: {ollama_payload}")
        
        response = requests.post(
            f"{Ollama_API_URL}/api/generate", 
            json=ollama_payload, 
            timeout=60.0  # Increased timeout
        )
        
        print(f"[LOG] Response status: {response.status_code}")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=500, 
                detail=f"Ollama API error: {response.status_code} - {response.text}"
            )
        
        ollama_response = response.json()
        print(f"[LOG] Ollama response: {ollama_response}")
        
        royal_text = ollama_response.get("response", "")
        
        return JSONResponse({
            "original": request.text,
            "paraphrased": royal_text,
            "model": "yott-agent"
        })
    
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Ollama API timeout - model may be loading")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama service")
    except Exception as e:
        print(f"[LOG] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")