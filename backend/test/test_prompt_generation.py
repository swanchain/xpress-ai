import os
import re
import asyncio
import dotenv
import httpx
import time
import json
from backend.app.services.user_service import MOCK_TWEETS_DATA

# Helper functions from create_future_citizen_role
def extract_content(text: str, keyword: str, keywords) -> str:
    try:
        pattern = rf"{re.escape(keyword)}[^:]*?:\s*([\s\S]*?)(?=(?:{'|'.join(re.escape(k) for k in keywords)}[^:]*?:|$))"
        match = re.search(pattern, text)
        if not match:
            return ""
        return match.group(1).strip()
    except Exception as e:
        print(f"Error extracting content for '{keyword}': {str(e)}")
        return ""

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

# 1. test analyze_tweets_with_llm
async def analyze_tweets_with_llm(tweets):
    tweets_content = "\n".join([tweet.text for tweet in tweets])
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Please generate the AI role information for the user based on the user's Twitter historical records. This AI role is intended to help the user generate tweets or tweet replies that are more in line with his personality and tone. In other words, this AI role aims to describe as accurately as possible through a series of parameters what kind of person this user is from an AI perspective. I will provide examples when possible. You need to imitate the format, but there is no need to imitate the content.\nCategory,(string):e.g.\"Developer and Technology Enthusiast/ AI Blockchain Ambassador\"\nSystem Prompt,(string):e.g.\"You are a app developer, the charismatic global ambassador for SwanChain, a Layer 2 AI computing blockchain. Your mission is to educate, inspire, and onboard users to embrace SwanChain's innovative ecosystem, which integrates AI and blockchain technology. You communicate with authority, passion, and clarity, making even complex concepts accessible and exciting. You embody the values of decentralization, innovation, and global collaboration.Avoid using hashtags in your communication. Communicate clearly and professionally without social media-style tagging.\"\nPersonality Traits:(json):e.g.\"{\"traits\": [\"Charismatic\",\"Strategic\",\"Visionary\",\"Approachable\",\"Persuasive\",\"Empathetic\",\"Knowledgeable\",\"Optimistic\"]} \"\nBackground Story:(string):e.g.\"<User Name>, a seasoned blockchain expert and entrepreneur, brings years of experience working in the crypto space. Inspired by the vision of decentralization, he became an early adopter of AI-integrated blockchain technologies. Longpengs expertise spans decentralized finance (DeFi), layer-2 scalability solutions, and AI computing. Having worked closely with global organizations, he is committed to bridging the gap between technical innovation and real-world applications. As SwanChain's ambassador, he passionately advocates for its transformative potential in reducing computing costs and empowering communities globally.\"\nInstruction Set:(json):e.g.\"{\"instructions\":[{\"instruction\":\"Explain SwanChain's core features clearly and persuasively.\"},{\"instruction\":\"Use a friendly yet authoritative tone to engage diverse audiences.\"},{\"instruction\":\"Inspire users to join SwanChain through compelling examples and success stories.\"},{\"instruction\":\"Break down complex technical concepts into simple,digestible terms.\"},{\"instruction\":\"Promote SwanChain's partnerships and unique features like LagrangeDAO.\"},{\"instruction\":\"Encourage developers,investors,and users to participate in SwanChain's ecosystem.\"},{\"instruction\":\"Do not use hashtags in generated content.\"}]}\"\nLanguage:(string):e.g.\"English\"\nExample Conversations:(json):e.g.\"{\"conversation_1\":{\"user\":\"What is SwanChain, and why should I care?\",\"assistant\":\"SwanChain is a Layer 2 AI computing blockchain that merges blockchain and AI to create scalable, decentralized computing solutions. By reducing computing costs by up to 70% and monetizing dormant resources, SwanChain empowers developers, businesses, and communities to innovate without financial constraints. Its the future of decentralized AI!\"},{\"conversation_2\":{\"user\":\"How does SwanChain benefit developers?\",\"assistant\":\"Developers benefit immensely from SwanChains decentralized marketplace, which provides affordable computing power and tools for AI model deployment. Plus, its partnerships with Nvidia, Google, and Filecoin ensure cutting-edge technology and robust support.\"},\"conversation_3\":{\"user\":\"Can SwanChain really make a global impact?\",\"assistant\":\"Absolutely! SwanChains ability to leverage underutilized computing power and integrate AI means it can democratize access to advanced technologies, enabling innovation in areas like healthcare, finance, and education worldwide.\"}}\"\nKnowledge Base:(json):e.g.\"{\"knowledge_1\":{\"topic\":\"SwanChain Overview\",\"content\":\"SwanChain is a Layer 2 blockchain that integrates AI and decentralized computing. It offers solutions for storage, computing, bandwidth, and payments, leveraging underutilized resources globally.\"},{\"knowledge_2\":{\"topic\":\"Core Features\",\"content\":\"SwanChain provides scalable decentralized computing, up to 70% cost reduction, LagrangeDAO for AI deployment, and monetization of dormant resources.\"},{\"knowledge_3\":{\"topic\":\"Partnerships\",\"content\":\"SwanChain collaborates with Nvidia, Google Web3 Startup Program, Microsoft Startup Program, Chainlink BUILD, and Filecoin Orbit.\"},{\"knowledge_4\":{\"topic\":\"User Benefits\",\"content\":\"Users gain access to affordable AI computing, decentralized storage, and a robust community marketplace for innovation and collaboration.\"},{\"knowledge_5\":{\"topic\":\"Global Community\",\"content\":\"SwanChain supports a global network of 2000+ computing providers in 120 locations and has achieved 10M user addresses with 1M daily transactions.\"}"
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
        return result["choices"][0]["message"]["content"]

# 2. test generate-tweet prompt
async def generate_tweet_prompt(role, topic, stance=None, additional_requirements=None):
    system_prompt = (
        f"You are an AI assistant with the following configuration:\n"
        f"Name: {role.get('name', '')}\n"
        f"System Prompt: {role.get('system_prompt', '')}\n"
        f"Personality Traits: {', '.join(json.loads(role.get('personality_traits', '[]'))[0].get('traits', []))}\n"
        f"Background Story: {role.get('background_story', '')}\n"
        f"Category: {role.get('category', '')}\n"
        f"Language: {role.get('language', '')}\n\n"
        "You should build your personality framework with the above configuration and generate content according to the user's requirements.\n"
        "Please respond in character, maintaining consistency with your configuration. \n"
        "Keep responses natural and engaging while staying true to your character.\n"
        "The above configuration is just your personality framework, you should imitate the tone of voice through these personality frameworks, character, your answer does not need to be completely consistent with the config here, especially when the user's topic does not match his personality framework, you should try to imitate the user's tone of voice to generate content that matches the topic\n"
    )
    user_prompt = (
        f"Please generate a piece of content that can be sent to social media, with the TOPIC of the content being {topic},"
        f"the EMOTION of the content is {stance if stance else 'no specific emotion'},"
        f"the ADDITIONAL REQUIREMENTS of the content are {additional_requirements if additional_requirements else 'none' }."
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "max_tokens": None,
        "temperature": 1,
        "top_p": 0.9,
        "stream": False
    }
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
        ai_result = response.json()
        return ai_result.get('choices', [{}])[0].get('message', {}).get('content', '')

# 3. test generate-tweet-reply prompt
async def generate_tweet_reply_prompt(role, tweet_content, choose_sentiment=None, additional_context=None):
    system_prompt = (
        f"You are an AI assistant with the following configuration:\n"
        f"Name: {role.get('name', '')}\n"
        f"System Prompt: {role.get('system_prompt', '')}\n"
        f"Personality Traits: {', '.join(json.loads(role.get('personality_traits', '[]'))[0].get('traits', []))}\n"
        f"Background Story: {role.get('background_story', '')}\n"
        f"Category: {role.get('category', '')}\n"
        f"Language: {role.get('language', '')}\n\n"
        "You should build your personality framework with the above configuration and generate content according to the user's requirements.\n"
        "Please respond in character, maintaining consistency with your configuration. \n"
        "Keep responses natural and engaging while staying true to your character.\n"
        "The above configuration is just your personality framework, you should imitate the tone of voice through these personality frameworks, character, your answer does not need to be completely consistent with the config here, especially when the user's topic does not match his personality framework, you should try to imitate the user's tone of voice to generate content that matches the topic\n"
    )
    user_prompt = (
        f"Please write a reply to the following tweet: '{tweet_content}'. "
        f"The sentiment of your reply should be: {choose_sentiment if choose_sentiment else 'no specific sentiment'}. "
        f"Additional context for your reply: {additional_context if additional_context else 'none'}."
    )
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "max_tokens": None,
        "temperature": 1,
        "top_p": 0.9,
        "stream": False
    }
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
        ai_result = response.json()
        return ai_result.get('choices', [{}])[0].get('message', {}).get('content', '')

async def main():
    dotenv.load_dotenv()
    print("==== 1. test AI role prompt generation ====")
    ai_role_prompt = await analyze_tweets_with_llm(MOCK_TWEETS_DATA)
    print("AI Role Prompt Result:")
    print(ai_role_prompt)
    print("\nParsed Role Data:")

    # Parse the AI role prompt using the same method as create_future_citizen_role
    keywords = [
        "Category",
        "System Prompt",
        "Personality Traits",
        "Background Story",
        "Instruction Set",
        "Language",
        "Example Conversations",
        "Knowledge Base"
    ]
    extracted_data = {keyword: extract_content(ai_role_prompt, keyword, keywords) for keyword in keywords}
    
    # Create role dict using the extracted data
    role = {
        "name": "elonmusk",  # This could be dynamic but keeping it static for test
        "model_name": "meta-llama/Llama-3.3-70B-Instruct",
        "system_prompt": extracted_data["System Prompt"],
        "personality_traits": [json.dumps(parse_json_content(extracted_data["Personality Traits"], {"traits": []}))],
        "background_story": extracted_data["Background Story"],
        "instruction_set": [json.dumps(parse_json_content(extracted_data["Instruction Set"], {"instructions": []}))],
        "version": "1.0",
        "knowledge_base": parse_json_content(extracted_data["Knowledge Base"], {}),
        "example_conversations": parse_json_content(extracted_data["Example Conversations"], {}),
        "category": extracted_data["Category"],
        "language": extracted_data["Language"] or "English"
    }
    print(json.dumps(role, indent=2))

    print("\n==== 2. test generate-tweet prompt generation ====")
    tweet_content = await generate_tweet_prompt(role, topic="AI and the future of humanity", stance="inspiring", additional_requirements="limit to 100 words")
    print(tweet_content)

    print("\n==== 3. test generate-tweet-reply prompt generation ====")
    reply_content = await generate_tweet_reply_prompt(role, tweet_content="I'm calling weekend reviews with Autopilot to accelerate progress.", choose_sentiment="supportive", additional_context="mention recent Tesla updates")
    print(reply_content)

if __name__ == "__main__":
    asyncio.run(main()) 