from io import BytesIO

from telegram import Update
from telegram.ext import ContextTypes

from servicos.main import (
    generate_image,
    generate_image_nvidia,
    edit_image,
)


async def gerar_imagem(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["acao"] = "gerar"

    await update.message.reply_text(
        "🎨 Digite a descrição da imagem que deseja gerar."
    )


async def gerar_imagem_nvidia(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["acao"] = "gerar_nvidia"

    await update.message.reply_text(
        "🤖 Digite a descrição da imagem que deseja gerar com NVIDIA."
    )


async def editar_imagem(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data["acao"] = "editar"

    await update.message.reply_text(
        "📝 Envie a imagem que deseja editar."
    )


async def receber_foto(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if context.user_data.get("acao") != "editar":
        await update.message.reply_text(
            "Primeiro escolha 📝 Descrever imagem."
        )
        return

    foto = update.message.photo[-1]

    arquivo = await foto.get_file()

    image_bytes = await arquivo.download_as_bytearray()

    context.user_data["imagem"] = bytes(image_bytes)

    await update.message.reply_text(
        "📷 Imagem recebida!\n\n"
        "Agora me diga o que deseja adicionar ou modificar na imagem."
    )


async def processar_prompt(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    prompt = update.message.text

    acao = context.user_data.get("acao")

    if acao == "gerar":
        await processar_geracao(
            update,
            context,
            prompt,
        )

    elif acao == "gerar_nvidia":
        await processar_geracao_nvidia(
            update,
            context,
            prompt,
        )

    elif acao == "editar":
        await processar_edicao(
            update,
            context,
            prompt,
        )

    else:
        await update.message.reply_text(
            "Escolha uma opção no menu primeiro."
        )


async def processar_geracao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    prompt: str,
):
    try:
        await update.message.reply_text(
            "🎨 Gerando sua imagem..."
        )

        image_bytes = await generate_image(prompt)

        await enviar_imagem(
            update,
            image_bytes,
            "Imagem gerada 🎨",
        )

        context.user_data.pop("acao", None)

    except Exception as exc:
        await update.message.reply_text(
            f"❌ Não foi possível gerar a imagem.\n\n"
            f"Erro: {exc}"
        )


async def processar_geracao_nvidia(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    prompt: str,
):
    try:
        await update.message.reply_text(
            "🤖 Gerando sua imagem com NVIDIA...\n"
            "Isso pode demorar um pouco."
        )

        image_bytes = await generate_image_nvidia(prompt)

        await enviar_imagem(
            update,
            image_bytes,
            "Imagem gerada com NVIDIA 🤖",
        )

        context.user_data.pop("acao", None)

    except Exception as exc:
        await update.message.reply_text(
            f"❌ Não foi possível gerar a imagem com NVIDIA.\n\n"
            f"Erro: {exc}"
        )


async def processar_edicao(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    prompt: str,
):
    image_bytes = context.user_data.get("imagem")

    if not image_bytes:
        await update.message.reply_text(
            "❌ Não encontrei a imagem. "
            "Envie a imagem novamente."
        )
        return

    try:
        await update.message.reply_text(
            "📝 Editando sua imagem..."
        )

        image_result = await edit_image(
            image_bytes=image_bytes,
            filename="telegram_image.jpg",
            prompt=prompt,
        )

        await enviar_imagem(
            update,
            image_result,
            "Imagem editada 📝",
        )

        context.user_data.pop("imagem", None)
        context.user_data.pop("acao", None)

    except Exception as exc:
        await update.message.reply_text(
            f"❌ Não foi possível editar a imagem.\n\n"
            f"Erro: {exc}"
        )


async def enviar_imagem(
    update: Update,
    image_bytes: bytes,
    caption: str,
):
    await update.message.reply_photo(
        photo=BytesIO(image_bytes),
        caption=caption,
    )
