import os
import base64

import httpx
from dotenv import load_dotenv


load_dotenv()


class NvidiaProvider:

    def __init__(self):

        self.api_key = os.getenv("NVIDIA_API_KEY")

        if not self.api_key:
            raise ValueError(
                "NVIDIA_API_KEY não configurada."
            )

        self.url = (
            "https://ai.api.nvidia.com/v1/genai/"
            "black-forest-labs/flux.2-klein-4b"
        )

    async def generate_image(
            self,
            prompt: str,
    ) -> bytes:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": prompt,
            "height": 1024,
            "width": 1024,
            "cfg_scale": 1,
            "samples": 1,
            "seed": 0,
            "steps": 4,
        }

        timeout = httpx.Timeout(
            connect=10.0,
            read=180.0,
            write=30.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                self.url,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"NVIDIA retornou {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        image_base64 = data["artifacts"][0]["base64"]

        return base64.b64decode(image_base64)
