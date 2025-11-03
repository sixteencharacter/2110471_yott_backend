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
async def paraphrase_to_royal_stream(
    request: ParaphraseRequest, 
    userData: Annotated[dict, Depends(validate_access_token)]
):
    print("[LOG] Starting STREAMING paraphrase request for:", request.text)

    try:
        import json
        
        async def generate_stream():
            ollama_payload = {
                "model": "yott-agent", 
                "prompt": f"paraphrase {request.text} in the first-person-manner", 
                "stream": True
            }
            
            print(f"[LOG] Sending streaming request to: {Ollama_API_URL}/api/generate")
            
            # Use requests with stream=True for real-time streaming
            with requests.post(
                f"{Ollama_API_URL}/api/generate", 
                json=ollama_payload, 
                stream=True,
                timeout=(10, 120)  # (connect_timeout, read_timeout)
            ) as response:
                
                if response.status_code != 200:
                    yield f"data: {json.dumps({'error': f'Ollama API error: {response.status_code}'})}\n\n"
                    return
                
                print("[LOG] Starting to stream response...")
                accumulated_text = ""
                
                # Process streaming JSON responses line by line
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            # Parse each JSON chunk
                            chunk_data = json.loads(line)
                            
                            if "response" in chunk_data:
                                # Get the text fragment
                                text_fragment = chunk_data["response"]
                                accumulated_text += text_fragment
                                
                                # Send Server-Sent Events format
                                yield f"data: {json.dumps({'text': text_fragment, 'accumulated': accumulated_text})}\n\n"
                            
                            # Check if streaming is complete
                            if chunk_data.get("done", False):
                                # Send final completion message
                                yield f"data: {json.dumps({'completed': True, 'final_text': accumulated_text})}\n\n"
                                print(f"[LOG] Streaming completed. Final text: {accumulated_text}")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"[LOG] JSON decode error: {e}, line: {line}")
                            continue
        
        return StreamingResponse(
            generate_stream(), 
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Ollama streaming timeout")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama service")
    except Exception as e:
        print(f"[LOG] Streaming error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

