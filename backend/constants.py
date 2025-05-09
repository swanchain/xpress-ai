from llm_models import LLM_MODELS_AND_POSTPROCESSORS

STATUS_SUCCESS = 'success'
STATUS_FAILED = 'failed'

"""X Developers"""
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
OAUTH_CALLBACK = 'https://task-test.filswan.com'
OAUTH_AUTHORIZE = 'https://api.twitter.com/oauth/authorize'
OAUTH_ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
USER_PROFILE = 'https://api.twitter.com/1.1/account/verify_credentials.json'
X_USER_PUBLIC_METRIC_API = "https://api.twitter.com/2/users/by/username/{}?user.fields=public_metrics"
X_TWEET_POST_INFO_API = "https://api.twitter.com/2/tweets/{}?tweet.fields=conversation_id,referenced_tweets"

GENERATE_TYPE_TWEET = 'tweet'
GENERATE_TYPE_REPLY = 'reply'

CACHE_TTL = 600

ALL_AVAILABLE_MODEL_NAMES = list(LLM_MODELS_AND_POSTPROCESSORS.keys())