from fastapi import FastAPI
from routes.images import router as images_router
from routes.kontext import router as kontext_router


app = FastAPI(
    title="Image Generator API",
    version="1.0.0",
)


app.include_router(images_router)
app.include_router(kontext_router)

