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

# =========================================================
# ROTINAS DE BACKGROUND (THREADS)
# =========================================================

def rotina_de_clique():
    """Roda em paralelo clicando o mouse sem travar o Jairo"""
    global loop_clique_ativo
    while loop_clique_ativo:
        pyautogui.click()
        time.sleep(0.1)  # Velocidade do clique (100ms)

def rotina_de_tecla():
    """Roda em paralelo apertando uma tecla sem travar o Jairo"""
    global loop_tecla_ativo, tecla_alvo_atual
    while loop_tecla_ativo:
        pyautogui.press(tecla_alvo_atual)
        time.sleep(0.1)

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
    
    acao = str(comando_json.get("acao", "")).lower()
    alvo = str(comando_json.get("alvo", "")).lower()
    
    # --- 1. ABRIR PROGRAMAS ---
    if acao == "abrir_programa":
        if not alvo: return "Tu quer que eu abra o quê? O além? Fala o nome do app, mestre!"

        # Caso especial para o Roblox (abre o app nativo da Windows Store)
        if "roblox" in alvo:
            try:
                os.system("start roblox:") 
                return "Iniciando o Roblox! Partiu farmar?"
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
            return f"Abri o {nome_escolhido}. Certeza de {melhor_pontuacao}% de que era isso que você queria."
                
        return f"Não achei nada parecido com '{alvo}' no PC. Tenta falar o nome mais direitinho."

    # --- 2. FECHAR PROGRAMAS ---
    elif acao == "fechar_programa":
        alvo_formatado = alvo.replace(" ", "")
        os.system(f"taskkill /f /im {alvo_formatado}.exe /t")
        return 