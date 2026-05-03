import pyautogui
import base64
import os
import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
CHAVE_GROQ = os.getenv("GROQ_API_KEY")
cliente = Groq(api_key=CHAVE_GROQ)

def clicar_no_elemento(descricao_alvo):
    # 1. Captura a tela e pega a resolução real do seu monitor
    largura_real, altura_real = pyautogui.size()
    screenshot = pyautogui.screenshot()
    screenshot.save("view.png")

    with open("view.png", "rb") as img:
        img_b64 = base64.b64encode(img.read()).decode('utf-8')

    # 2. O Prompt "Mestre" que ensina a IA a medir a tela
    prompt = f"""Analise este print. O usuário quer clicar em: "{descricao_alvo}".
    Imagine que a tela é uma grade que vai de 0 a 1000 (X e Y).
    Identifique o centro do objeto solicitado.
    
    Responda EXATAMENTE neste formato JSON:
    {{"x": valor_entre_0_e_1000, "y": valor_entre_0_e_1000, "motivo": "curta explicação"}}
    """

    try:
        res = cliente.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
            ]}],
            response_format={"type": "json_object"}
        )

        dados = json.loads(res.choices[0].message.content)
        
        # 3. A REGRA DE TRÊS (Tradução para pixels reais)
        # Se a IA diz 500 num monitor de 1920px, o cálculo é (500 / 1000) * 1920 = 960px
        ponto_x = int((dados['x'] / 1000) * largura_real)
        ponto_y = int((dados['y'] / 1000) * altura_real)

        print(f"🤖 Jairo: Vi o alvo em ({dados['x']},{dados['y']}). Clicando em {ponto_x}x{ponto_y}...")
        
        # Move o mouse e clica
        pyautogui.moveTo(ponto_x, ponto_y, duration=0.5)
        pyautogui.click()
        
        return f"Cliquei no elemento: {dados['motivo']}"

    except Exception as e:
        return f"Erro na visão: {e}"
    finally:
        if os.path.exists("view.png"): os.remove("view.png")