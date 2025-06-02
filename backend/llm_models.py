
import re
import os

def clean_think_context(text: str) -> str:
    """
    Remove the think context from the text (for deepseek R1 models)
    """
    cleaned_text = re.sub(r'^.*?</think>\s*', '', text, flags=re.DOTALL)
    return cleaned_text


LLM_MODELS_INFO = {
    # "anthropic/claude-3.7-sonnet": {
    #     "postprocessor": None,
    #     "model_api_url": os.environ['OPENROUTER_API'],
    #     "model_access_key": os.environ['OPENROUTER_API_KEY']
    # },
    # "openai/gpt-4.5-preview": {
    #     "postprocessor": None,
    #     "model_api_url": os.environ['OPENROUTER_API'],
    #     "model_access_key": os.environ['OPENROUTER_API_KEY']
    # },
    "google/gemini-2.5-pro-preview": {
        "postprocessor": None,
        "model_api_url": os.environ['OPENROUTER_API'],
        "model_access_key": os.environ['OPENROUTER_API_KEY']
    },
    # "google/gemini-2.5-flash-preview": {
    #     "postprocessor": None,
    #     "model_api_url": os.environ['OPENROUTER_API'],
    #     "model_access_key": os.environ['OPENROUTER_API_KEY']
    # },
    "meta-llama/Llama-3.3-70B-Instruct": {
        "postprocessor": None,
        "model_api_url": os.environ['NEBULA_GENERATE_REPLY_API'],
        "model_access_key": os.environ['NEBULA_API_KEY']
    },
    "deepseek-ai/DeepSeek-V3-0324": {
        "postprocessor": None,
        "model_api_url": os.environ['NEBULA_GENERATE_REPLY_API'],
        "model_access_key": os.environ['NEBULA_API_KEY']
    },
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": {
        "postprocessor": clean_think_context,
        "model_api_url": os.environ['NEBULA_GENERATE_REPLY_API'],
        "model_access_key": os.environ['NEBULA_API_KEY']
    },
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B": {
        "postprocessor": clean_think_context,
        "model_api_url": os.environ['NEBULA_GENERATE_REPLY_API'],
        "model_access_key": os.environ['NEBULA_API_KEY']
    },
    "Qwen/QwQ-32B": {
        "postprocessor": clean_think_context,
        "model_api_url": os.environ['NEBULA_GENERATE_REPLY_API'],
        "model_access_key": os.environ['NEBULA_API_KEY']
    },
    "Qwen/Qwen2.5-Coder-32B-Instruct": {
        "postprocessor": clean_think_context,
        "model_api_url": os.environ['NEBULA_GENERATE_REPLY_API'],
        "model_access_key": os.environ['NEBULA_API_KEY']
    }
}
