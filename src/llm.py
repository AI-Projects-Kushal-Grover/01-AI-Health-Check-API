import os
import logging

from google import genai
from google.genai import types

class LLMService:
    def __init__(self) -> None:
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")).aio

    async def write(self, *, prompt: str, system_prompt: str) -> str | None:
        logging.info(f"Using model: {self.model} for prompting.")
        response = await self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        return response.text