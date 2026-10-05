from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image

from providers.cloudflare import CloudflareProvider
from providers.nvidia import NvidiaProvider


class ImageService:

    def __init__(
        self,
        cloudflare: CloudflareProvider,
        nvidia: NvidiaProvider,
    ):
        self.cloudflare = cloudflare
        self.nvidia = nvidia

    async def edit_image(
        self,
        image_bytes: bytes,
        filename: str,
        prompt: str,
    ) -> bytes:

        generated_image = await self.cloudflare.edit_image(
            image_bytes=image_bytes,
            filename=filename,
            prompt=prompt,
        )

        compressed_image = self._compress_image(
            generated_image
        )

        self._save_image(compressed_image)

        return compressed_image

    async def generate_image(
        self,
        prompt: str,
    ) -> bytes:

        generated_image = await self.cloudflare.generate_image(
            prompt=prompt,
        )

        compressed_image = self._compress_image(
            generated_image
        )

        self._save_image(compressed_image)

        return compressed_image

    async def generate_image_nvidia(
        self,
        prompt: str,
    ) -> bytes:

        generated_image = await self.nvidia.generate_image(
            prompt=prompt,
        )

        compressed_image = self._compress_image(
            generated_image
        )

        self._save_image(compressed_image)

        return compressed_image

    def _compress_image(
        self,
        image_bytes: bytes,
        quality: int = 85,
    ) -> bytes:

        image = Image.open(
            BytesIO(image_bytes)
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        output = BytesIO()

        image.save(
            output,
            format="JPEG",
            quality=quality,
            optimize=True,
        )

        return output.getvalue()

    def _save_image(
        self,
        image_bytes: bytes,
    ) -> None:

        storage_path = Path("storage/images")

        storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = f"{uuid4()}.jpg"

        file_path = storage_path / filename

        with open(file_path, "wb") as file:
            file.write(image_bytes)
