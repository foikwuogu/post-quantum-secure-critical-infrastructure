from pydantic import BaseModel, Field

class Message(BaseModel):
    message_id: str
    message_type: str
    sender: str
    receiver: str
    amount: float = Field(ge=0)
    currency: str = "USD"
    timestamp: str

class EncryptRequest(BaseModel):
    mode: str = Field(pattern="^(classical|pqc|hybrid)$")
    message: Message

class EnvelopeRequest(BaseModel):
    envelope: dict

class BenchmarkRequest(BaseModel):
    iterations: int = Field(default=3, ge=1, le=20)
