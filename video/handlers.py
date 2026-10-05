import asyncio, os, tempfile, time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes, MessageHandler, filters,
    Application, ApplicationHandlerStop,
)
from . import provider
from .config import *

STATUS_DONE = {"complete"}
STATUS_FAIL = {"error", "canceled"}

_active_users: set[int] = set()   # 1 geração por vez por usuário
MENU_PREFIXES = ("🎨", "🤖", "📝", "🎬")


def cleanup_old_videos():
    limit = time.time() - KEEP_DAYS * 86400
    for f in OUTPUT_DIR.glob("*.mp4"):
        if f.stat().st_mtime < limit:
            f.unlink(missing_ok=True)


def _reset(context):
    context.user_data.pop("video_img", None)
    if context.user_data.get("acao") in ("video", "video_prompt"):
        context.user_data.pop("acao", None)


# 1) clique no botão
async def botao_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("video_img", None)
    context.user_data["acao"] = "video"
    await update.message.reply_text("🎬 Envie a foto que deseja transformar em vídeo.")
    raise ApplicationHandlerStop


# 2) recebe a foto (só no fluxo de vídeo)
async def foto_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("acao") != "video":
        return  # deixa o receber_foto das imagens cuidar

    arquivo = await update.message.photo[-1].get_file()
    context.user_data["video_img"] = bytes(await arquivo.download_as_bytearray())
    context.user_data["acao"] = "video_prompt"

    await update.message.reply_text(
        "📷 Foto recebida!\n\nAgora descreva o movimento do vídeo.\n"
        "Ex: giro lento da câmera com neblina."
    )
    raise ApplicationHandlerStop


# 3) recebe o prompt e gera
async def prompt_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("acao") != "video_prompt":
        return  # deixa o processar_prompt das imagens cuidar

    texto = update.message.text.strip()

    # clicou em outro botão do menu: abandona o fluxo de vídeo
    if texto.startswith(MENU_PREFIXES):
        _reset(context)
        return

    user_id = update.effective_user.id
    if user_id in _active_users:
        await update.message.reply_text("⏳ Você já tem um vídeo em geração. Aguarde.")
        raise ApplicationHandlerStop

    img = context.user_data.get("video_img")
    if not img:
        _reset(context)
        await update.message.reply_text(
            "❌ Não encontrei a foto. Toque em 🎬 Gerar vídeo e envie de novo.")
        raise ApplicationHandlerStop

    _active_users.add(user_id)
    status_msg = await update.message.reply_text(
        "🎬 Gerando seu vídeo, isso pode levar alguns minutos...")

    tmp = os.path.join(tempfile.gettempdir(), f"vid_{user_id}_{int(time.time())}.jpg")
    try:
        with open(tmp, "wb") as f:
            f.write(img)
        job_id = await provider.create_job(tmp, texto)
    except Exception as exc:
        _active_users.discard(user_id)
        _reset(context)
        await status_msg.edit_text(f"❌ Erro ao iniciar a geração.\n\nErro: {exc}")
        raise ApplicationHandlerStop
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

    _reset(context)
    asyncio.create_task(_track(context.bot, update.effective_chat.id, user_id, job_id))
    raise ApplicationHandlerStop


async def _track(bot, chat_id, user_id, job_id):
    start = time.time()
    try:
        while time.time() - start < JOB_TIMEOUT:
            st = await provider.get_status(job_id)

            if st["status"] in STATUS_DONE and st["urls"]:
                dest = OUTPUT_DIR / f"{user_id}_{job_id}.mp4"
                await provider.download_to_file(st["urls"][0], dest)

                size_mb = dest.stat().st_size / 1024 / 1024
                if size_mb <= MAX_TELEGRAM_MB:
                    with open(dest, "rb") as f:
                        await bot.send_video(chat_id, f, caption="Vídeo gerado 🎬",
                                             supports_streaming=True)
                else:
                    await bot.send_message(
                        chat_id,
                        f"Vídeo gerado ({size_mb:.0f} MB), grande demais para o Telegram.")
                cleanup_old_videos()
                return

            if st["status"] in STATUS_FAIL:
                break
            await asyncio.sleep(POLL_INTERVAL)

        await bot.send_message(chat_id, "❌ Falha ou tempo esgotado na geração.")
    except Exception as exc:
        await bot.send_message(chat_id, f"❌ Erro ao gerar o vídeo.\n\nErro: {exc}")
    finally:
        _active_users.discard(user_id)


def _add_menu_button():
    """Adiciona o botão sem editar interface.py nem o start."""
    from handler import interface
    import handler.handlers as start_module

    rows = [list(r) for r in interface.botoes]
    if ["🎬 Gerar vídeo"] not in rows:
        rows.append(["🎬 Gerar vídeo"])

    novo = ReplyKeyboardMarkup(rows, resize_keyboard=True)
    interface.comandos_rapidos = novo        # usado por mostrar_menu()
    start_module.comandos_rapidos = novo     # usado pelo /start


def register(app: Application):
    print(f">>> [video] register chamado. VIDEO_ENABLED={VIDEO_ENABLED}")
    if not VIDEO_ENABLED:
        print(">>> [video] DESLIGADO (VIDEO_ENABLED não é 'true')")
        return
    cleanup_old_videos()
    _add_menu_button()
    print(">>> [video] botão adicionado ao menu")

    app.add_handler(MessageHandler(filters.Regex("^🎬 Gerar vídeo$"), botao_video), group=-1)
    app.add_handler(MessageHandler(filters.PHOTO, foto_video), group=-1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, prompt_video), group=-1)