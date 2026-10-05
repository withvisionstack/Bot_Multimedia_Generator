from fastapi import UploadFile


class KontextService:

    def __init__(self, kontext):
        self.kontext = kontext

    async def edit_image(
        self,
        image: UploadFile,
        prompt: str,
    ) -> bytes:

        # Temporariamente ignoramos a imagem enviada.
        # O endpoint da NVIDIA está sendo testado
        # utilizando um example_id.

        return await self.kontext.edit_image(
            prompt=prompt,
            example_id=0,
        )
