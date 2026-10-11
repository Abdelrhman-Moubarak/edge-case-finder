import os
from typing import Any, List, Optional

import requests
from dotenv import load_dotenv
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM


load_dotenv()

NGROK_URL = os.getenv("NGROK_URL")
API_KEY = os.getenv("API_KEY")

if NGROK_URL is None:
    raise RuntimeError("NGROK_URL environment variable is not set")

if API_KEY is None:
    raise RuntimeError("API_KEY environment variable is not set")


class QwenLLM(LLM):
    max_new_tokens: int = 1500
    timeout: int = 300
    thinking: bool = False

    @property
    def _llm_type(self) -> str:
        return "qwen-ngrok"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        response = requests.post(
            f"{NGROK_URL}/generate",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "prompt": prompt,
                "max_new_tokens": self.max_new_tokens,
                "thinking": self.thinking,
            },
            timeout=self.timeout,
        )

        if not response.ok:
            raise RuntimeError(
                f"Server returned {response.status_code}: {response.text}"
            )

        return response.json()["response"]