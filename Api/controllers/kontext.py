from fastapi import UploadFile


class KontextController:

    def __init__(self, kontext_service):
        self.kontext_service = kontext_service

    async def edit(
        self,
        image: UploadFile,
        prompt: str,
    ) -> bytes:

        return await self.kontext_service.edit_image(
            image=image,
            prompt=prompt,
        )
