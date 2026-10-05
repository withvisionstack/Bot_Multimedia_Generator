import os
import base64

import httpx
from dotenv import load_dotenv


load_dotenv()


class NvidiaKontextProvider:

    def __init__(self):
        self.api_key = os.getenv("NVIDIA_KONTEXT")

        if not self.api_key:
            raise ValueError(
                "NVIDIA_KONTEXT não configurada."
            )

        self.url = (
            "https://ai.api.nvidia.com/v1/genai/"
            "black-forest-labs/flux.1-kontext-dev"
        )

    async def edit_image(
        self,
        prompt: str,
        example_id: int = 0,
        cfg_scale: float = 3.5,
    ) -> bytes:

        payload = {
            "prompt": prompt,
            "image": f"data:image/png;example_id,{example_id}",
            "cfg_scale": cfg_scale,
            "steps": 30,
            "seed": 0,
            "samples": 1,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                self.url,
                headers=headers,
                json=payload,
            )

        print("NVIDIA STATUS:", response.status_code)
        print("NVIDIA BODY:", response.text)

        if response.is_error:
            raise RuntimeError(
                f"NVIDIA {response.status_code}: {response.text}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"NVIDIA retornou uma resposta que não é JSON: "
                f"{response.text}"
            ) from exc

        try:
            image_base64 = data["artifacts"][0]["base64"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"Resposta inesperada da NVIDIA: {data}"
            ) from exc

        try:
            return base64.b64decode(image_base64)
        except Exception as exc:
            raise RuntimeError(
                "Não foi possível decodificar a imagem retornada "
                "pela NVIDIA."
            ) from exc
