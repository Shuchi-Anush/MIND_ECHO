from pydantic import BaseModel

class SentimentRequest(BaseModel):
    text: str

class TextRequest(BaseModel):
    text: str
