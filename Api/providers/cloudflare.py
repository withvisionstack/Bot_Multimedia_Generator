import os

import httpx
from dotenv import load_dotenv


load_dotenv()


class CloudflareProvider:
    def __init__(self):
        self.edit_url = os.getenv("CLOUDFLARE_EDIT_URL")
        self.generate_url = os.getenv("CLOUDFLARE_GENERATE_URL")
        self.api_key = os.getenv("CLOUDFLARE_WORKER_KEY")

        if not self.edit_url:
            raise ValueError(
                "CLOUDFLARE_EDIT_URL não configurada."
            )

        if not self.generate_url:
            raise ValueError(
                "CLOUDFLARE_GENERATE_URL não configurada."
            )

        if not self.api_key:
            raise ValueError(
                "CLOUDFLARE_WORKER_KEY não configurada."
            )

    async def edit_image(
        self,
        image_bytes: bytes,
        filename: str,
        prompt: str,
    ) -> bytes:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        files = {
            "input_image_0": (
                filename,
                image_bytes,
                "image/jpeg",
            )
        }

        data = {
            "prompt": prompt,
        }

        timeout = httpx.Timeout(
            connect=10.0,
            read=180.0,
            write=30.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                self.edit_url,
                headers=headers,
                data=data,
                files=files,
            )

        response.raise_for_status()

        return response.content

    async def generate_image(
            self,
            prompt: str,
    ) -> bytes:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        files = {
            "prompt": (None, prompt),
        }

        timeout = httpx.Timeout(
            connect=10.0,
            read=180.0,
            write=30.0,
            pool=10.0,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                self.generate_url,
                headers=headers,
                files=files,
            )

        print("\n========== CLOUDFLARE DEBUG ==========")
        print("STATUS:", response.status_code)
        print("HEADERS:", dict(response.headers))
        print("BODY:", response.text)
        print("=======================================\n")

        if response.status_code >= 400:
            raise RuntimeError(
                f"Cloudflare retornou {response.status_code}: "
                f"{response.text}"
            )

        return response.content
