import os
import httpx
import logging
from dotenv import load_dotenv
from cachetools import TTLCache
from asyncache import cached
from cachetools.keys import hashkey
import hashlib
import json
from constants import CACHE_TTL

load_dotenv()

logger = logging.getLogger()


cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)


def payload_hash_key(payload):
    payload_str = json.dumps(payload, sort_keys=True)
    return hashkey(hashlib.sha256(payload_str.encode()).hexdigest())


# @cached(cache, key=payload_hash_key)
async def request_llm(
    payload: dict,
    refresh: bool = False
) -> str:
    if not refresh:
        cached_response = cache.get(payload_hash_key(payload))
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

            cache[payload_hash_key(payload)] = content

            return content
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from LLM response: {str(e)}")
            raise ValueError("Unexpected API response format") from e

