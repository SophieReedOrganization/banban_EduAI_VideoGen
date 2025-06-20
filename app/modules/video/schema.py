from pydantic import BaseModel
from typing import Optional

class VideoGenerationRequest(BaseModel):
    text: str
    voice: str = "zh-TW-HsiaoChenNeural"
    image_base64: Optional[str] = None
    rate: Optional[float] = 0.0
    volume: Optional[float] = 0.0
    content: Optional[str] = None