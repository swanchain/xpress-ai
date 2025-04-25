import tweepy
import dotenv
import os
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from ..models.user import User
from ..database.session import get_engine
from tweepy.errors import TooManyRequests
import httpx
import json

logger = logging.getLogger(__name__)

async def get_user_tweets(client: tweepy.Client, user_id: int) -> str:
    """
    Get user's tweets
    """
    tweets = client.get_users_tweets(
        id=user_id,
        max_results=10,
        tweet_fields=["created_at", "public_metrics", "text", "entities", "id", "referenced_tweets"],
        expansions=["referenced_tweets.id", "referenced_tweets.id.author_id"]
    )
    
    if not tweets.data:
        logger.info(f"No tweets found for user ID: {user_id}")
        return None
        
    return tweets.data

async def analyze_tweets_with_llm(tweets: str) -> str:
    """
    Call LLM to analyze user's tweets
    """
    # Convert tweets to string format
    tweets_content = "\n".join([tweet.text for tweet in tweets])
    
    # Prepare the API request payload
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

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://inference.nebulablock.com/v1/chat/completions",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.environ['NEBULA_API_KEY']}"
            }
        )
        response.raise_for_status()
        result = response.json()
        
        try:
            return result["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise ValueError("Unexpected API response format") from e

async def create_future_citizen_role(user: User, user_data: str) -> str:
    """
    Call FutureCitizen API to create role
    Args:
        user: User object containing x_screen_name and x_user_id
        user_data: String containing the role data from LLM analysis
    Returns:
        str: The created role ID
    """
    try:
        # Parse the required fields from user_data
        data_dict = {
            'Category': '',
            'System Prompt': '',
            'Personality Traits': '{"traits": []}',
            'Background Story': '',
            'Instruction Set': '{"instructions": []}',
            'Knowledge Base': '{}',
            'Example Conversations': '{}',
            'Language': 'English'
        }
        
        # Extract values from user_data, using defaults if not found
        for key in data_dict:
            if key in user_data:
                data_dict[key] = user_data[key]

        # Format data for API
        payload = {
            "name": f"{user.x_screen_name}-{user.x_user_id}",
            "model_name": "meta-llama/Llama-3.3-70B-Instruct",
            "system_prompt": data_dict['System Prompt'],
            "personality_traits": [json.dumps({"traits": json.loads(data_dict['Personality Traits'])["traits"]})],
            "background_story": data_dict['Background Story'],
            "instruction_set": [json.dumps({"instructions": json.loads(data_dict['Instruction Set'])["instructions"]})],
            "version": "1.0",
            "knowledge_base": json.loads(data_dict['Knowledge Base']),
            "example_conversations": json.loads(data_dict['Example Conversations']),
            "category": data_dict['Category'],
            "language": data_dict['Language']
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.futurecitizen.ai/api/v1/ai-roles",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.environ['FUTURECITIZEN_API_KEY']}",
                    "accept": "application/json, text/plain, */*"
                }
            )
            response.raise_for_status()
            result = response.json()
            
            try:
                return str(result['id'])
            except KeyError as e:
                raise ValueError("Role ID not found in API response") from e

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in user data: {str(e)}") from e

async def update_user_role(user: User, role_id: str) -> None:
    """
    Update user's role_id
    """
    user.update_user_role_by_user_id(user.id, role_id)
    logger.info(f"Successfully updated role_id for user {user.id}")

async def process_single_user(client: tweepy.Client, user: User) -> None:
    """
    Process the complete process for a single user
    """
    # 1. Get user's tweets
    tweets = await get_user_tweets(client, user.x_user_id)
    if not tweets:
        return
        
    # 2. LLM analyze tweets
    analysis_result = await analyze_tweets_with_llm(tweets)
    
    # 3. Create FutureCitizen role
    role_id = await create_future_citizen_role(user, analysis_result)
    
    # 4. Update user's role_id
    await update_user_role(user, role_id)

async def update_user_role_task():
    """
    Main task: Update user roles
    """
    try:
        dotenv.load_dotenv()
        client = tweepy.Client(bearer_token=os.environ['BEARER_TOKEN'])
        
        users_to_update = User.get_empty_ai_role_id_user_list()
        if not users_to_update:
            logger.info("No users to update")
            return
        
        logger.info(f"Found {len(users_to_update)} users to update")
        
        for user in users_to_update:
            if not user.x_user_id:
                logger.warning(f"User {user.id} has no Twitter ID")
                continue
                
            try:
                await process_single_user(client, user)
            except TooManyRequests:
                logger.warning("Twitter API rate limit reached. Stopping processing until next scheduled run.")
                return
            except Exception as e:
                logger.error(f"Failed to process user {user.id}: {str(e)}")
                continue
            
    except Exception as e:
        logger.error(f"Error in update_user_role_task: {str(e)}")
        raise 