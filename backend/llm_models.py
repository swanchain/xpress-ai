
import re

def clean_think_context(text: str) -> str:
    """
    Remove the think context from the text (for deepseek R1 models)
    """
    cleaned_text = re.sub(r'^.*?</think>\s*', '', text, flags=re.DOTALL)
    return cleaned_text


LLM_MODELS_AND_POSTPROCESSORS = {
    "meta-llama/Llama-3.3-70B-Instruct": None,
    "deepseek-ai/DeepSeek-V3-0324": None,
    "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": clean_think_context,
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B": clean_think_context,
    "Qwen/QwQ-32B": clean_think_context,
    "Qwen/Qwen2.5-Coder-32B-Instruct": clean_think_context
}
