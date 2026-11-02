import os
import time
import ctypes
import pyautogui
from PIL import Image, ImageDraw
from telemetria import registrar_evento

try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

ARQUIVO_DEBUG_IMAGEM = "debug_visao.jpg"

_modelo_visao = None
_processador = None
_torch = None

def inicializar_olhos():
    """
    Carrega o modelo de Visual Grounding nos 36GB de RAM com compatibilidade forçada.
    """
    global _modelo_visao, _processador, _torch
    if _modelo_visao is not None:
        return True

    try:
        registrar_evento("OLHOS", "Carregando modelo de visão local nos 36GB de RAM (Hugging Face)...")
        import torch
        from transformers import AutoProcessor, AutoModelForCausalLM, AutoConfig

        _torch = torch
        nome_modelo = "microsoft/Florence-2-base"

        # Trava de segurança para resolver o erro 'forced_bos_token_id'
        config = AutoConfig.from_pretrained(nome_modelo, trust_remote_code=True)
        if hasattr(config, "text_config"):
            config.text_config.forced_bos_token_id = None
        config.forced_bos_token_id = None

        _processador = AutoProcessor.from_pretrained(nome_modelo, trust_remote_code=True)
        _modelo_visao = AutoModelForCausalLM.from_pretrained(
            nome_modelo, 
            config=config,
            torch_dtype=torch.float32, 
            trust_remote_code=True
        ).to("cpu")

        _modelo_visao.eval()
        registrar_evento("OLHOS", "Modelo de visão local carregado e pronto para uso!", status="SUCESSO")
        return True

    except Exception as e:
        registrar_evento("OLHOS", "Falha ao carregar modelo de visão local", str(e), status="ERRO")
        return False

def gerar_imagem_debug(screenshot, centro_x, centro_y, largura_tela, altura_tela, rotulo="", bbox=None):
    """
    Desenha o retângulo detectado pela IA e a mira amarela no ponto de clique.
    """
    try:
        imagem_debug = screenshot.copy()
        draw = ImageDraw.Draw(imagem_debug)

        if bbox:
            x1, y1, x2, y2 = bbox
            draw.rectangle([x1, y1, x2, y2], outline="red", width=4)
        else:
            raio = 35
            draw.rectangle([centro_x - raio, centro_y - raio, centro_x + raio, centro_y + raio], outline="red", width=4)

        draw.line([centro_x - 15, centro_y, centro_x + 15, centro_y], fill="yellow", width=2)
        draw.line([centro_x, centro_y - 15, centro_x, centro_y + 15], fill="yellow", width=2)
        draw.ellipse([centro_x - 4, centro_y - 4, centro_x + 4, centro_y + 4], fill="red")

        texto_info = f"ALVO: {rotulo} ({centro_x}x{centro_y})"
        draw.text((max(0, centro_x - 40), max(0, centro_y - 30)), texto_info, fill="yellow")

        imagem_debug.save(ARQUIVO_DEBUG_IMAGEM, "JPEG", quality=90)
        registrar_evento("OLHOS", f"Imagem de debug salva em: '{ARQUIVO_DEBUG_IMAGEM}'")
    except Exception as e:
        registrar_evento("OLHOS", "Erro ao desenhar imagem de debug", str(e), status="AVISO")

def clicar_no_elemento(descricao_alvo):
    inicio = time.time()
    registrar_evento("OLHOS", f"Localizando visualmente na tela: '{descricao_alvo}'")

    if _modelo_visao is None:
        sucesso = inicializar_olhos()
        if not sucesso:
            return "Falha ao inicializar motor de visão local."

    screenshot = pyautogui.screenshot()
    largura_real, altura_real = pyautogui.size()
    imagem_rgb = screenshot.convert("RGB")

    tarefa = "<CAPTION_TO_PHRASE_GROUNDING>"
    prompt_completo = tarefa + descricao_alvo

    try:
        with _torch.no_grad():
            inputs = _processador(text=prompt_completo, images=imagem_rgb, return_tensors="pt")
            generated_ids = _modelo_visao.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=256,
                num_beams=3
            )
            generated_text = _processador.batch_decode(generated_ids, skip_special_tokens=False)[0]
            resultado = _processador.post_process_generation(
                generated_text, 
                task=tarefa, 
                image_size=(largura_real, altura_real)
            )

        dados_grounding = resultado.get(tarefa, {})
        bboxes = dados_grounding.get("bboxes", [])

        if not bboxes:
            tempo = round(time.time() - inicio, 2)
            registrar_evento("OLHOS", f"Elemento '{descricao_alvo}' não encontrado na tela", f"Tempo: {tempo}s", status="AVISO")
            return f"Não encontrei '{descricao_alvo}' na tela."

        caixa = bboxes[0]
        x1, y1, x2, y2 = [int(v) for v in caixa]

        ponto_x = int((x1 + x2) / 2)
        ponto_y = int((y1 + y2) / 2)

        gerar_imagem_debug(screenshot, ponto_x, ponto_y, largura_real, altura_real, descricao_alvo, bbox=(x1, y1, x2, y2))

        pyautogui.moveTo(ponto_x, ponto_y, duration=0.25)
        pyautogui.click()

        tempo = round(time.time() - inicio, 2)
        registrar_evento("OLHOS", f"Clique realizado em ({ponto_x}x{ponto_y})", f"Tempo: {tempo}s", status="SUCESSO")
        return f"Sucesso! Cliquei em '{descricao_alvo}' nas coordenadas {ponto_x}x{ponto_y}"

    except Exception as e:
        tempo = round(time.time() - inicio, 2)
        registrar_evento("OLHOS", "Erro na inferência visual local", f"{e} (Tempo: {tempo}s)", status="ERRO")
        return f"Falha na visão local: {e}"