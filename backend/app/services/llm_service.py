import os
import httpx
import logging
from dotenv import load_dotenv
from cachetools.keys import hashkey
import hashlib
from redis.asyncio import Redis
import json
from constants import CACHE_TTL
from llm_models import LLM_MODELS_INFO

load_dotenv()

logger = logging.getLogger()



def payload_hash_key(payload: dict) -> str:
    payload_str = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(payload_str.encode()).hexdigest()


async def request_llm(
    payload: dict,
    model_name: str = "meta-llama/Llama-3.3-70B-Instruct",
    redis_client: Redis = None,
) -> str:
    key = payload_hash_key(payload)
    if redis_client:
        cached_response = await redis_client.get(key)
        if cached_response is not None:
            return cached_response

    logger.info("Requesting LLM...")
    model_api_url = LLM_MODELS_INFO.get(model_name, {}).get("model_api_url")
    model_access_key = LLM_MODELS_INFO.get(model_name, {}).get("model_access_key")
    if not model_api_url:
        raise ValueError("Model API URL not found")
    
    payload.update({"model": model_name})
    
    if not model_access_key:
        raise ValueError("Model access key not found")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            model_api_url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {model_access_key}"
            }
        )
        response.raise_for_status()
        result = response.json()
        
        try:
            content = result["choices"][0]["message"]["content"]
            if postprocessor := LLM_MODELS_INFO.get(model_name, {}).get("postprocessor"):
                content = postprocessor(content)
            
            if redis_client:
                await redis_client.setex(key, CACHE_TTL, content)

            return content
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from LLM response: {str(e)}")
            raise ValueError("Generate content failed") from e


async def request_gemini_llm(
    payload: dict,
    model_name: str = "google/gemini-2.5-pro-preview",
) -> str:
    logger.info("Requesting Gemini LLM via OpenRouter...")
    payload.update({"model": model_name})

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            },
        )
        response.raise_for_status()
        result = response.json()

        try:
            content = result["choices"][0]["message"]["content"]

            return content
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from Gemini response: {str(e)}")
            raise ValueError("Gemini generate content failed") from e
