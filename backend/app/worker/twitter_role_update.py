import os
import sys
from pathlib import Path
import re

# Add the backend directory to Python path
backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import tweepy
import dotenv
import logging
from typing import Optional, List
from app.models.user import User
from app.services.user_service import UserService
from app.services.api_service import get_futurecitizen_bearer_token_async
from app.database.session import AsyncSessionLocal
from tweepy.errors import TooManyRequests
import httpx
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def get_user_tweets(client: tweepy.Client, user_id: int, use_mock: bool = False) -> Optional[List[tweepy.Tweet]]:
    """
    Get user's tweets
    Args:
        client: Tweepy client instance
        user_id: Twitter user ID
        use_mock: Whether to use mock data (for testing)
    Returns:
        Optional[List[tweepy.Tweet]]: List of tweets or None if no tweets found
    """
    if use_mock:
        return MOCK_TWEETS_DATA

    tweets = client.get_users_tweets(
        id=user_id,
        max_results=10,
        tweet_fields=["created_at", "public_metrics", "text", "entities", "id", "referenced_tweets"],
        expansions=["referenced_tweets.id", "referenced_tweets.id.author_id"]
    )
    
    if not tweets.data:
        return None
        
    return tweets.data

async def analyze_tweets_with_llm(tweets: List[tweepy.Tweet]) -> str:
    """
    Call LLM to analyze user's tweets
    Args:
        tweets: List of Tweet objects to analyze
    Returns:
        str: LLM analysis result
    """
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
            os.environ['NEBULA_GENERATE_ROLE_API'],
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
            return content
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract content from LLM response: {str(e)}")
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
        # Define the keywords we want to extract
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
        extracted_data = {keyword: extract_content(user_data, keyword) for keyword in keywords}

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

        # Get bearer token through login
        bearer_token = await get_futurecitizen_bearer_token_async()

        # Prepare the payload
        payload = {
            "name": f"{user.x_screen_name}-{user.x_user_id}",
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

        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.environ['FUTURECITIZEN_CREATE_ROLE_API'],
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {bearer_token}",
                    "accept": "application/json, text/plain, */*"
                }
            )
            response.raise_for_status()
            result = response.json()
            
            try:
                return str(result['id'])
            except KeyError as e:
                raise ValueError("Role ID not found in API response") from e

    except Exception as e:
        logger.error(f"Error in create_future_citizen_role: {str(e)}")
        raise

async def update_user_role(user: User, role_id: str, user_service: UserService) -> None:
    """
    Update user's role_id
    """
    await user_service.update_user_role_by_user_id(user.id, role_id)

async def process_single_user(client: tweepy.Client, user: User, use_mock: bool = False) -> None:
    """
    Process the complete process for a single user
    """
    # 1. Get user's tweets
    tweets = await get_user_tweets(client, user.x_user_id, use_mock)
    if not tweets:
        return
        
    # 2. LLM analyze tweets
    analysis_result = await analyze_tweets_with_llm(tweets)
    
    # 3. Create FutureCitizen role
    role_id = await create_future_citizen_role(user, analysis_result)
    
    # 4. Update user's role_id
    await update_user_role(user, role_id)

async def update_user_role_task() -> None:
    """
    Main task to update user roles
    """
    try:
        async with AsyncSessionLocal() as session:
            user_service = UserService(session)
            users_to_update = await user_service.get_empty_ai_role_id_user_list()
            
            if not users_to_update:
                logger.info("No users need role updates")
                return

            client = tweepy.Client(
                bearer_token=os.environ.get("X_BEARER_TOKEN_FOR_API"),
                wait_on_rate_limit=True
            )

            for user in users_to_update:
                try:
                    tweets = await get_user_tweets(client, user.x_user_id)
                    if not tweets:
                        logger.warning(f"No tweets found for user {user.x_screen_name}")
                        continue

                    user_data = await analyze_tweets_with_llm(tweets)
                    role_id = await create_future_citizen_role(user, user_data)
                    await update_user_role(user, role_id, user_service)
                    
                    logger.info(f"Successfully updated role for user {user.x_screen_name}")
                
                except TooManyRequests:
                    logger.error("Twitter API rate limit exceeded")
                    break
                except Exception as e:
                    logger.error(f"Error processing user {user.x_screen_name}: {str(e)}")
                    continue

    except Exception as e:
        logger.error(f"Error in update_user_role_task: {str(e)}")
        raise

# Mock User class for testing purposes
class MockUser:
    """Mock User class for testing"""
    def __init__(self, id=1, x_user_id="44196397", x_screen_name="elonmusk"):
        self.id = id
        self.x_user_id = x_user_id
        self.x_screen_name = x_screen_name

    def update_user_role_by_user_id(self, user_id, role_id):
        print(f"Mock: Updated user {user_id} with role_id {role_id}")

    @staticmethod
    def get_empty_ai_role_id_user_list():
        return [MockUser()]

# Add mock tweets for testing
class MockTweet:
    """Mock Tweet class for testing"""
    def __init__(self, text, created_at=None):
        self.text = text
        self.created_at = created_at

MOCK_TWEETS_DATA = [
    MockTweet("@MarioNawfal $1.5B spent every year!? Wow, that makes my political contributions last year small by comparison."),
    MockTweet("RT @_jaybaxter_: The reason posts with links sometimes get lower reach is not because they are explicitly downranked by any evil rule or lo…"),
    MockTweet("@SERobinsonJr @_jaybaxter_ That does need some love"),
    MockTweet("@SawyerMerritt Uh oh 😬 Inverse Cramer is tough karma to overcome!"),
    MockTweet("I'm calling weekend reviews with Autopilot to accelerate progress."),
    MockTweet("@nataliegwinters 💯"),
    MockTweet("RT @SawyerMerritt: NEWS: Tesla reportedly has 300 test operators driving around Austin, Texas to prepare for their big June robotaxi launch…"),
    MockTweet("@SawyerMerritt Waymo needs \"way mo\" money to succeed 😂"),
    MockTweet("@MarioNawfal Cool"),
    MockTweet("Good move. There are thousands of committees that take up a lot of time without clear accomplishments. A reset was needed."),
    MockTweet("To be clear, there is no explicit rule limiting the reach of links in posts. The algorithm tries (not always successfully) to maximize user-seconds on 𝕏, so a link that causes people to cut short their time here will naturally get less exposure.")
]

async def run_test():
    """Test function to verify the twitter role update functionality"""
    try:
        # Load environment variables
        dotenv.load_dotenv()
        
        # Verify required environment variables
        required_env_vars = ['NEBULA_API_KEY', 'FUTURECITIZEN_API_KEY']  # Removed X_BEARER_TOKEN as it's not needed for mock
        missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return

        # Initialize Tweepy client with a dummy token (won't be used with mock data)
        client = tweepy.Client(bearer_token="dummy_token")
        
        # Create a mock user
        test_user = MockUser()
        
        # Test the complete process with mock data
        try:
            await process_single_user(client, test_user, use_mock=True)
        except Exception as e:
            logger.error(f"Error during test: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_test()) 