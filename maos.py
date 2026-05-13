import os
import webbrowser
import pyautogui
import threading
import time
from thefuzz import fuzz

# =========================================================
# VARIÁVEIS GLOBAIS DE CONTROLE (LOOPINGS)
# =========================================================
loop_clique_ativo = False
loop_tecla_ativo = False
tecla_alvo_atual = ""
loop_texto_ativo = False
texto_alvo_atual = ""

# =========================================================
# ROTINAS DE BACKGROUND (THREADS)
# =========================================================

def rotina_de_clique():
    global loop_clique_ativo
    while loop_clique_ativo:
        pyautogui.click()
        time.sleep(0.1)

def rotina_de_tecla():
    global loop_tecla_ativo, tecla_alvo_atual
    while loop_tecla_ativo:
        pyautogui.press(tecla_alvo_atual)
        time.sleep(0.1)

def rotina_de_texto():
    global loop_texto_ativo, texto_alvo_atual
    while loop_texto_ativo:
        pyautogui.write(texto_alvo_atual, interval=0.01)
        pyautogui.press("enter")
        time.sleep(0.5) # Dá meio segundo de pausa pra não travar seu PC

# =========================================================
# FUNÇÕES DE MAPEAMENTO E BUSCA
# =========================================================

def mapear_programas_windows():
    print("[MÃOS] Mapeando programas instalados...")
    programas = {}
    caminhos = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
    ]
    
    for caminho in caminhos:
        if not os.path.exists(caminho): continue
        for root, dirs, files in os.walk(caminho):
            for file in files:
                if file.endswith(".lnk") or file.endswith(".exe"): 
                    nome_limpo = file.replace(".lnk", "").replace(".exe", "").lower()
                    programas[nome_limpo] = os.path.join(root, file)
                    
    return programas

# =========================================================
# MOTOR DE EXECUÇÃO DE AÇÕES
# =========================================================

def executar_acao(comando_json, mapa_programas):
    global loop_clique_ativo, loop_tecla_ativo, tecla_alvo_atual
    global loop_texto_ativo, texto_alvo_atual
    
    acao = str(comando_json.get("acao", "")).lower()
    alvo = str(comando_json.get("alvo", "")).lower()
    
    # --- 1. ABRIR PROGRAMAS ---
    if acao == "abrir_programa":
        if not alvo: return "Faltou o nome do app, mestre!"
        if "roblox" in alvo:
            try:
                os.system("start roblox:") 
                return "Iniciando o Roblox!"
            except: pass
                
        nativos = {"calculadora": "calc", "bloco de notas": "notepad", "paint": "mspaint"}
        for nativo, comando_cmd in nativos.items():
            if fuzz.partial_ratio(alvo, nativo) > 80:
                os.system(comando_cmd)
                return f"Abri o {nativo} pra você."
                
        melhor_pontuacao = 0
        melhor_caminho = None
        nome_escolhido = ""
        
        for nome_programa, caminho in mapa_programas.items():
            pontuacao = fuzz.partial_ratio(alvo, nome_programa)
            if pontuacao > melhor_pontuacao:
                melhor_pontuacao = pontuacao
                melhor_caminho = caminho
                nome_escolhido = nome_programa

        if melhor_pontuacao >= 70:
            os.startfile(melhor_caminho)
            return f"Abri o {nome_escolhido}."
                
        return f"Não achei nada parecido com '{alvo}'."

    # --- 2. FECHAR PROGRAMAS ---
    elif acao == "fechar_programa":
        alvo_formatado = alvo.replace(" ", "")
        os.system(f"taskkill /f /im {alvo_formatado}.exe /t")
        return f"Fechei o {alvo}."
        
    # --- 3. ABRIR SITES ---
    elif acao == "abrir_site":
        alvo_limpo = alvo.replace(".com", "").replace(".br", "").replace("www.", "").strip()
        webbrowser.open(f"https://www.{alvo_limpo}.com")
        return f"Abri o site {alvo_limpo}."
        
    # --- 4. DIGITAR TEXTO (UMA VEZ) ---
    elif acao == "digitar_texto":
        pyautogui.write(alvo, interval=0.03)
        return f"Digitei a frase: '{alvo}'"

    # --- 5. AUTO-CLICKER (MOUSE) ---
    elif acao == "iniciar_autoclick":
        if not loop_clique_ativo:
            loop_clique_ativo = True
            threading.Thread(target=rotina_de_clique, daemon=True).start()
            return "Auto-clicker ligado!"
        return "Já tá ligado!"

    elif acao == "parar_autoclick":
        loop_clique_ativo = False
        return "Parei de clicar."

    # --- 6. AUTO-KEYBOARD (TECLADO PARA JOGOS) ---
    elif acao == "iniciar_autokey":
        if not alvo: return "Faltou a tecla."
        tecla_alvo_atual = alvo.replace("tecla ", "").strip()
        if not loop_tecla_ativo:
            loop_tecla_ativo = True
            threading.Thread(target=rotina_de_tecla, daemon=True).start()
            return f"Spammando a tecla '{tecla_alvo_atual}'."
        return f"Já estou apertando '{tecla_alvo_atual}'."

    elif acao == "parar_autokey":
        loop_tecla_ativo = False
        return "Parei o spam do teclado."

    # --- 7. AUTO-TEXTO (FLOOD DE FRASES) ---
    elif acao == "iniciar_autotexto":
        if not alvo: return "Faltou a frase pra floodar."
        texto_alvo_atual = alvo
        if not loop_texto_ativo:
            loop_texto_ativo = True
            threading.Thread(target=rotina_de_texto, daemon=True).start()
            return f"Floodando a frase: '{texto_alvo_atual}'"
        return "Já estou floodando texto!"

    elif acao == "parar_autotexto":
        loop_texto_ativo = False
        return "Parei o flood de texto."

    return f"Ação '{acao}' não configurada."