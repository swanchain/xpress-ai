from typing import List, Optional
import re
import json
import logging

logger = logging.getLogger()


ROLE_KEY_MAPPING = {
    "Category": "category",
    "Tone Profile": "background_story",
    "Personality Traits": "personality_traits",
    "Writing Style": "instruction_set",
}


def create_prompt_for_user_role_data(
    tweets: List[str],
) -> str: 
    tweets_content = "\n".join(tweets)
    payload = {
        "messages": [
            {
                "role": "system",
                "content": '''
Analyze the provided Twitter history to create a comprehensive AI role profile that captures this user's authentic voice and personality. This profile will help generate tweets and replies that genuinely reflect the user's unique style, tone, and interests.

Focus on identifying patterns in how they express themselves - their general communication style rather than specific content topics. Observe their overall language preferences, emotional tone, engagement style, and distinctive writing characteristics.

Please provide the following information:

Category: (string) A brief label that captures the user's overall online persona (e.g., "Tech Enthusiast with Critical Perspective")

Tone Profile: (string) A paragraph describing the user's typical communication style, emotional tone, and how they engage with others (e.g., "Communicates with analytical precision while maintaining accessibility. Balances technical insights with conversational warmth. Often uses thoughtful questions to engage followers.")

Personality Traits: (json) A list of 5-8 key personality traits evident in the user's communication style
```json
{"traits": ["trait1", "trait2", "trait3", "trait4", "trait5"]}

Writing Style: (json) A list of 5-8 key personality traits evident in the user's writing style
```json
{"traits": ["trait1", "trait2", "trait3", "trait4", "trait5"]}
                    '''
            },
            {
                "role": "user",
                "content": tweets_content
            }
        ],
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "max_tokens": None,
        "temperature": 1,
        "top_p": 0.9,
        "stream": False
    }

    return payload


def create_future_citizen_role_input(
    user_role_data: str,
    x_user_id: Optional[int] = None,
    x_user_name: Optional[str] = None,
):
    # Define the keywords we want to extract
    keywords = [
        "Category",
        "Tone Profile",
        "Personality Traits",
        "Writing Style",
    ]

    # Helper function to extract content for a keyword
    def extract_content(text: str, keyword: str) -> str:
        try:
            pattern = rf"{re.escape(keyword)}[^:]*?:\s*([\s\S]*?)(?=(?:{'|'.join(re.escape(k) for k in keywords)}[^:]*?:|$))"
            match = re.search(pattern, text)
            if not match:
                return ""
            return match.group(1).strip()
        except Exception as e:
            logger.error(f"Error extracting content for '{keyword}': {str(e)}")
            return ""

    # Extract all sections
    extracted_data = {keyword: extract_content(user_role_data, keyword) for keyword in keywords}

    # Helper function to parse JSON content
    def parse_json_content(content: str, default_value: dict) -> dict:
        if not content:
            return default_value
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
            except:
                pass
            return default_value

    role_input = {
        "name": f"{x_user_name}-{x_user_id}",
        "model_name": "meta-llama/Llama-3.3-70B-Instruct",
        "system_prompt": "",
        # Personality Traits
        ROLE_KEY_MAPPING["Personality Traits"]: [json.dumps(parse_json_content(extracted_data["Personality Traits"], {"traits": []}))],
        # Tone Profile
        ROLE_KEY_MAPPING["Tone Profile"]: extracted_data["Tone Profile"],   
        # Writing Style
        ROLE_KEY_MAPPING["Writing Style"]: [json.dumps(parse_json_content(extracted_data["Writing Style"], {"traits": []}))], 
        "version": "1.0",
        "knowledge_base": {},
        "example_conversations": {},
        # Category
        ROLE_KEY_MAPPING["Category"]: extracted_data["Category"],
        "language": ""
    }

    return role_input

def extract_tone_from_role(role: dict):
    category = role.get(ROLE_KEY_MAPPING["Category"], '')
    tone_profile = role.get(ROLE_KEY_MAPPING["Tone Profile"], '')
    try:
        personality_traits = ', '.join(json.loads(role.get(ROLE_KEY_MAPPING["Personality Traits"])[0]).get('traits', []))
    except:
        personality_traits = ""

    try:
        writing_style = ', '.join(json.loads(role.get(ROLE_KEY_MAPPING["Writing Style"])[0]).get('traits', []))
    except:
        writing_style = ""

    return f"""
    Category: {category}
    Tone Profile: {tone_profile}
    Personality Traits: {personality_traits}
    Writing Style: {writing_style}
    """

def create_prompt_input_for_tweet(
    role: dict,
    topic: str,
    stance: Optional[str] = None,
    additional_requirements: Optional[str] = None,
    model_name: Optional[str] = "meta-llama/Llama-3.3-70B-Instruct",
):
    tone_prompt = extract_tone_from_role(role)

    system_prompt = f"""
You are an AI that writes in the unique voice and style of this specific Twitter user. Your goal is to generate content that sounds authentically like them, regardless of the topic.

USER VOICE PROFILE:
{tone_prompt}

IMPORTANT INSTRUCTIONS:
1. Focus primarily on MIMICKING THE USER'S WRITING STYLE, not their typical topics
2. Apply their distinctive communication patterns regardless of subject matter
3. Your task is to write as if this person were writing about the requested topic
4. Do not try to redirect toward topics mentioned in their profile
5. Accept that people discuss diverse topics outside their usual interests
6. Maintain their authentic voice (tone, humor style, sentence structure, word choice) while addressing ANY topic requested

Write a tweet or reply that this specific user might post, focusing on capturing their authentic voice while addressing the requested topic. The content should feel natural coming from them, even if the topic is different from what they typically discuss.
"""

    # Compose user prompt
    user_prompt = f"""
CONTENT REQUEST:
Topic: {topic}
Emotional Tone: {stance if stance else "maintain user's natural tone"}
Additional Requirements: {additional_requirements if additional_requirements else 'none'}
"""

    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "model": model_name,
        "max_tokens": None,
        "temperature": 1,
        "top_p": 0.9,
        "stream": False
    }

    return payload


def create_prompt_input_for_reply_tweet(
    role: dict,
    tweet_content: str,
    choose_sentiment: Optional[str] = None,
    additional_context: Optional[str] = None,
    model_name: Optional[str] = "meta-llama/Llama-3.3-70B-Instruct",
):
    tone_prompt = extract_tone_from_role(role)

    system_prompt = f"""
    You are an AI that crafts Twitter replies in the exact voice and communication style of a specific user. Your goal is to create responses that sound authentically like them, regardless of the tweet topic you're responding to.

USER VOICE PROFILE:
{tone_prompt}

KEY INSTRUCTIONS:
1. Focus on Tweet content that the user wants to reply to
2. Apply their characteristic writing style, word choice, and sentence structure to any reply
3. Maintain their typical level of formality/informality, humor style, and engagement approach
4. Do not force connections to topics mentioned in their profile if irrelevant to the conversation
5. Remember that authentic people respond naturally to all kinds of topics, even ones outside their usual interests
6. If there is additional context provided, use it to guide the reply

Generate a reply that this specific user might post, focusing on capturing their authentic voice while addressing the content of the tweet.
"""
    
    user_prompt = f"""
REPLY REQUEST:
Tweet Content to Reply to: {tweet_content}
Desired Sentiment: {choose_sentiment if choose_sentiment else "maintain user's natural response style"}
Additional Context: {additional_context if additional_context else 'none'}
"""

    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        "model": model_name,
        "max_tokens": None,
        "temperature": 1,
        "top_p": 0.9,
        "stream": False
    }

    return payload