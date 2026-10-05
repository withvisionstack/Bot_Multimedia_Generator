import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TOKEN

from handler.handlers import start


from handler.images import (
    gerar_imagem,
    gerar_imagem_nvidia,
    editar_imagem,
    receber_foto,
    processar_prompt,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


app = Application.builder().token(TOKEN).build()


app.add_handler(
    CommandHandler("start", start)
)


app.add_handler(
    MessageHandler(
        filters.Regex("^🎨 Gerar imagem$"),
        gerar_imagem,
    )
)


app.add_handler(
    MessageHandler(
        filters.Regex("^🤖 Gerar com NVIDIA$"),
        gerar_imagem_nvidia,
    )
)


app.add_handler(
    MessageHandler(
        filters.Regex("^📝 Descrever imagem"),
        editar_imagem,
    )
)


app.add_handler(
    MessageHandler(
        filters.PHOTO,
        receber_foto,
    )
)


app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        processar_prompt,
    )
)


# Módulo de vídeo: se der erro, só o vídeo é desativado
try:
    from video.handlers import register as register_video
    register_video(app)
except Exception:
    logging.exception("Módulo de vídeo desativado por erro")


app.run_polling()