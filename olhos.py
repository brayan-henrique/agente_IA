import pyautogui
import base64
import os
import json
import time
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

# Carrega as credenciais e inicializa a IA
load_dotenv()
cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

def tirar_print_otimizado(modo="alta"):
    """Tira print e comprime para economizar dados e tempo de API"""
    screenshot = pyautogui.screenshot()
    caminho = "view_temp.jpg"
    
    if modo == "rapido":
        # 480p / Qualidade baixa: Ideal para checar se uma janela abriu rápido
        screenshot = screenshot.resize((854, 480), Image.LANCZOS)
        screenshot.save(caminho, "JPEG", quality=30, optimize=True)
    else:
        # 720p / Qualidade alta: Ideal para precisão de clique do mouse
        screenshot = screenshot.resize((1280, 720), Image.LANCZOS)
        screenshot.save(caminho, "JPEG", quality=80, optimize=True)
    
    # Converte para base64 para mandar pra nuvem
    with open(caminho, "rb") as img:
        b64_string = base64.b64encode(img.read()).decode('utf-8')
        
    return b64_string, caminho

def clicar_no_elemento(descricao_alvo, modo="alta"):
    """Olha a tela, acha a coordenada e clica (ou retorna erro)"""
    img_b64, caminho_img = tirar_print_otimizado(modo)
    largura_real, altura_real = pyautogui.size()

    # O Prompt de Visão com a grade de coordenadas e check de status
    prompt = f"""Analise este print da tela. Imagine que a imagem possui uma grade que vai de X=0 a 1000 (esquerda para direita) e Y=0 a 1000 (cima para baixo).
    Encontre: '{descricao_alvo}'.
    Se o alvo estiver na tela, retorne o centro dele em X e Y, e status 'ok'.
    Se o alvo NÃO estiver na tela (ou houver tela de erro/carregamento), retorne status 'erro'.
    Responda EXATAMENTE neste formato JSON: {{"x": valor_x, "y": valor_y, "status": "ok/erro"}}"""

    try:
        res = cliente.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", # Modelo mais rápido e atual de visão
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]}],
            response_format={"type": "json_object"}
        )
        
        dados = json.loads(res.choices[0].message.content)
        status = dados.get('status', 'erro')
        
        # O Check de Sanidade: Se não achou, avisa e cancela o clique
        if status == 'erro':
            return "Não encontrei o alvo na tela ou ainda está carregando."

        # Regra de Três: Converte a escala 1000x1000 para os pixels reais do seu monitor
        ponto_x = int((dados['x'] / 1000) * largura_real)
        ponto_y = int((dados['y'] / 1000) * altura_real)

        # Move o mouse suavenente (0.3s) para você ver o que ele está fazendo
        pyautogui.moveTo(ponto_x, ponto_y, duration=0.3)
        pyautogui.click()
        return f"Sucesso! Cliquei nas coordenadas {ponto_x}x{ponto_y}"
        
    except Exception as e:
        return f"Falha ao processar visão: {e}"
    finally:
        # Limpa o rastro da imagem pra não lotar seu HD
        if os.path.exists(caminho_img): 
            os.remove(caminho_img)