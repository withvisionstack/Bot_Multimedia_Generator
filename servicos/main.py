import httpx
import os


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


async def generate_image(prompt: str) -> bytes:

    async with httpx.AsyncClient(timeout=180.0) as client:

        response = await client.post(
            f"{API_URL}/v1/images/generate",
            data={
                "prompt": prompt,
            },
        )

        response.raise_for_status()

        return response.content

async def generate_image_nvidia(prompt: str) -> bytes:

    url = f"{API_URL}/v1/images/generate-nvidia"

    async with httpx.AsyncClient() as client:

        response = await client.post(
            url,
            data={
                "prompt": prompt,
            },
        )

        response.raise_for_status()

        return response.content



async def edit_image(
    image_bytes: bytes,
    filename: str,
    prompt: str,
) -> bytes:

    files = {
        "image": (
            filename,
            image_bytes,
            "image/jpeg",
        )
    }

    data = {
        "prompt": prompt,
    }

    async with httpx.AsyncClient(timeout=180.0) as client:

        response = await client.post(
            f"{API_URL}/v1/images/edit",
            files=files,
            data=data,
        )

        response.raise_for_status()

        return response.content
