from fastapi import UploadFile, HTTPException

from services.images import ImageService


class ImageController:

    def __init__(self, image_service: ImageService):
        self.image_service = image_service

    async def edit(
        self,
        image: UploadFile,
        prompt: str,
    ):

        if not image.content_type:
            raise HTTPException(
                status_code=400,
                detail="Tipo da imagem não informado.",
            )

        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="O arquivo enviado precisa ser uma imagem.",
            )

        image_bytes = await image.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="A imagem está vazia.",
            )

        try:
            result = await self.image_service.edit_image(
                image_bytes=image_bytes,
                filename=image.filename or "image.jpg",
                prompt=prompt,
            )

            return result

        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Erro ao processar imagem: {exc}",
            )

    async def generate(
        self,
        prompt: str,
    ) -> bytes:

        try:
            return await self.image_service.generate_image(
                prompt=prompt
            )

        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Erro ao gerar imagem: {exc}",
            )

    async def generate_nvidia(
        self,
        prompt: str,
    ) -> bytes:

        try:
            return await self.image_service.generate_image_nvidia(
                prompt=prompt
            )

        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Erro ao gerar imagem com NVIDIA: {exc}",
            )
