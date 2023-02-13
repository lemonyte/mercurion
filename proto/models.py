from pydantic import BaseModel


class Message(BaseModel):
    subject: str
    content: str
    sender: str
    recipient: str
    origin: str
    destination: str
    timestamp: int
    read: bool = False
