from web3 import Web3
from config import settings
from redis.asyncio import Redis

RPC = settings.RPC
CONTRACT_ADDRESS = settings.CONTRACT_ADDRESS

contract_address = Web3.to_checksum_address(CONTRACT_ADDRESS)
web3 = Web3(Web3.HTTPProvider(RPC))

# Load ABI
abi = [
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "uuid",
        "type": "string"
      }
    ],
    "name": "getTotalCredits",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]

# Contract instance
contract = web3.eth.contract(address=contract_address, abi=abi)

async def get_total_credits(uuid: str, redis: Redis):
    if redis:
      total_credits = await redis.get(uuid)
      if total_credits:
          return total_credits
    total_credits = contract.functions.getTotalCredits(uuid).call()
    if redis:
       await redis.setex(uuid, 30, total_credits)
    return total_credits

