from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response

from controllers.images import ImageController
from services.images import ImageService
from providers.cloudflare import CloudflareProvider
from providers.nvidia import NvidiaProvider


router = APIRouter(
    prefix="/v1/images",
    tags=["images"],
)


cloudflare_provider = CloudflareProvider()
nvidia_provider = NvidiaProvider()

image_service = ImageService(
    cloudflare=cloudflare_provider,
    nvidia=nvidia_provider,
)

image_controller = ImageController(
    image_service=image_service,
)


@router.post("/edit")
async def edit_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
):
    result = await image_controller.edit(
        image=image,
        prompt=prompt,
    )

    return Response(
        content=result,
        media_type="image/jpeg",
    )


@router.post("/generate")
async def generate_image(
    prompt: str = Form(...),
):
    result = await image_controller.generate(
        prompt=prompt,
    )

    return Response(
        content=result,
        media_type="image/jpeg",
    )


@router.post("/generate-nvidia")
async def generate_image_nvidia(
    prompt: str = Form(...),
):
    result = await image_controller.generate_nvidia(
        prompt=prompt,
    )

    return Response(
        content=result,
        media_type="image/jpeg",
    )
