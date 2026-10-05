from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response

from controllers.kontext import KontextController
from services.kontext import KontextService
from providers.nvidia_kontext import NvidiaKontextProvider


router = APIRouter(
    prefix="/v1/kontext",
    tags=["kontext"],
)


kontext_provider = NvidiaKontextProvider()

kontext_service = KontextService(
    kontext=kontext_provider,
)

kontext_controller = KontextController(
    kontext_service=kontext_service,
)


@router.post("/edit")
async def edit_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
):
    result = await kontext_controller.edit(
        image=image,
        prompt=prompt,
    )

    return Response(
        content=result,
        media_type="image/png",
    )
