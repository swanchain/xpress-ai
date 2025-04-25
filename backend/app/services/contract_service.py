from web3 import Web3
from config import settings

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

from cachetools import TTLCache
from cachetools import cached

credit_cache = TTLCache(maxsize=1000, ttl=30)

@cached(credit_cache)
def get_total_credits(uuid: str):
    print("calling contract")
    total_credits = contract.functions.getTotalCredits(uuid).call()
    return total_credits

