import os
import httpx
import logging
from dotenv import load_dotenv
from cachetools.keys import hashkey
import hashlib
from redis.asyncio import Redis
import json
from constants import CACHE_TTL
from llm_models import LLM_MODELS_AND_POSTPROCESSORS

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

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            os.environ['NEBULA_GENERATE_REPLY_API'],
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['NEBULA_API_KEY']}"
            }
        )
        response.raise_for_status()
        result = response.json()
        
        try:
            content = result["choices"][0]["message"]["content"]
            if postprocessor := LLM_MODELS_AND_POSTPROCESSORS.get(model_name):
                content = postprocessor(content)
            
            if redis_client:
                await redis_client.setex(key, CACHE_TTL, content)

            return content
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from LLM response: {str(e)}")
            raise ValueError("Generate content failed") from e

