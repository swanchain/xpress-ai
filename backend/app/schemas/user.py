
from pydantic import BaseModel

class WalletSignatureLogin(BaseModel):
    wallet_address: str
    signature: str

