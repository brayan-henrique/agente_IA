import os
import webbrowser
import pyautogui
import threading
import time
import ctypes
from thefuzz import fuzz
from telemetria import registrar_evento

try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

user32 = ctypes.windll.user32
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

def forcar_janela_maximizada(titulos_alvo):
    """
    Localiza a janela do navegador pelo título, restaura, maximiza (tela cheia)
    e força para o primeiro plano total da tela.
    """
    registrar_evento("MÃOS", f"Buscando janelas ativas correspondentes a {titulos_alvo}")
    janela_encontrada = [False]

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))

    def callback(hwnd, extra):
        if user32.IsWindowVisible(hwnd):
            tam = user32.GetWindowTextLengthW(hwnd)
            if tam > 0:
                buf = ctypes.create_unicode_buffer(tam + 1)
                user32.GetWindowTextW(hwnd, buf, tam + 1)
                titulo = buf.value.lower()

                for t in titulos_alvo:
                    if t.lower() in titulo:
                        registrar_evento("MÃOS", f"Janela encontrada: '{buf.value}'", f"HWND: {hwnd}")
                        # 3 = SW_MAXIMIZE (Força Tela Cheia)
                        user32.ShowWindow(hwnd, 3)
                        # Simula toque de ALT para desbloquear foco do Windows
                        pyautogui.press('alt')
                        user32.SetForegroundWindow(hwnd)
                        janela_encontrada[0] = True
                        return False
        return True

    user32.EnumWindows(WNDENUMPROC(callback), 0)
    
    if not janela_encontrada[0]:
        registrar_evento("MÃOS", "Nenhuma janela visível correspondente foi encontrada para focar", status="AVISO")

# =========================================================
# CONTROLES GLOBAIS DE REPETIÇÃO
# =========================================================
loop_clique_ativo = False
loop_tecla_ativo = False
tecla_alvo_atual = ""
loop_texto_ativo = False
texto_alvo_atual = ""

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
        time.sleep(0.5)

def mapear_programas_windows():
    registrar_evento("MÃOS", "Mapeando programas instalados no Menu Iniciar do Windows...")
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

    registrar_evento("MÃOS", f"Total de programas mapeados com sucesso: {len(programas)}")
    return programas

def executar_acao(comando_json, mapa_programas):
    global loop_clique_ativo, loop_tecla_ativo, tecla_alvo_atual
    global loop_texto_ativo, texto_alvo_atual

    acao = str(comando_json.get("acao", "")).lower()
    alvo = str(comando_json.get("alvo", "")).lower()

    registrar_evento("MÃOS", f"Executando ação física '{acao}'", f"Alvo: '{alvo}'")

    # --- 1. ABRIR PROGRAMAS ---
    if acao == "abrir_programa":
        if not alvo:
            registrar_evento("MÃOS", "Falha: Nome do programa não fornecido", status="ERRO")
            return "Faltou o nome do app!"

        if "opera" in alvo:
            for nome_p, cam in mapa_programas.items():
                if "opera" in nome_p:
                    os.startfile(cam)
                    time.sleep(1.0)
                    forcar_janela_maximizada(["opera", "opera gx"])
                    return "Abri o Opera e maximizei na tela."

        if "chrome" in alvo:
            for nome_p, cam in mapa_programas.items():
                if "chrome" in nome_p:
                    os.startfile(cam)
                    time.sleep(1.0)
                    forcar_janela_maximizada(["chrome", "google chrome"])
                    return "Abri o Chrome e maximizei na tela."

        nativos = {"calculadora": "calc", "bloco de notas": "notepad", "paint": "mspaint"}
        for nativo, comando_cmd in nativos.items():
            if fuzz.partial_ratio(alvo, nativo) > 80:
                os.system(f"start {comando_cmd}")
                time.sleep(0.5)
                forcar_janela_maximizada([nativo, comando_cmd])
                return f"Abri o {nativo}."

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
            time.sleep(1.0)
            forcar_janela_maximizada([nome_escolhido, alvo])
            return f"Abri o {nome_escolhido} em tela cheia."

        registrar_evento("MÃOS", f"Nenhum programa compatível encontrado para '{alvo}'", status="AVISO")
        return f"Não achei nada parecido com '{alvo}'."

    # --- 2. FECHAR PROGRAMAS ---
    elif acao == "fechar_programa":
        nativos = {"calculadora": "calc", "bloco de notas": "notepad", "paint": "mspaint"}
        executavel = alvo.replace(" ", "")
        for nativo, cmd in nativos.items():
            if fuzz.partial_ratio(alvo, nativo) > 80:
                executavel = cmd
                break
        os.system(f"taskkill /f /im {executavel}.exe /t")
        return f"Fechei o {alvo}."

    # --- 3. ABRIR SITES COM MAXIMIZAÇÃO ---
    elif acao == "abrir_site":
        alvo_limpo = alvo.replace(".com", "").replace(".br", "").replace("www.", "").strip()
        url = f"https://www.{alvo_limpo}.com"
        registrar_evento("MÃOS", f"Navegando para URL: {url}")
        webbrowser.open(url)

        # Espera carregar e força janela maximizada
        time.sleep(1.2)
        forcar_janela_maximizada(["opera", "chrome", "edge", "brave", "firefox", alvo_limpo])
        return f"Abri o site {alvo_limpo} em tela cheia!"

    # --- 4. PRESSIONAR TECLA (MÍDIA, PAUSE, ATALHOS) ---
    elif acao == "pressionar_tecla":
        tecla = alvo.strip()
        if tecla in ["espaço", "espaco"]:
            tecla = "space"
        pyautogui.press(tecla)
        registrar_evento("MÃOS", f"Tecla '{tecla}' disparada no teclado", status="SUCESSO")
        return f"Pressionei a tecla '{tecla}'."

    # --- 5. DIGITAR TEXTO ---
    elif acao == "digitar_texto":
        pyautogui.write(alvo, interval=0.02)
        registrar_evento("MÃOS", f"Texto digitado: '{alvo}'", status="SUCESSO")
        return f"Digitei a frase: '{alvo}'"

    # --- 6. AUTO-CLICKER ---
    elif acao == "iniciar_autoclick":
        if not loop_clique_ativo:
            loop_clique_ativo = True
            threading.Thread(target=rotina_de_clique, daemon=True).start()
            return "Auto-clicker ligado!"
        return "Já tá ligado!"

    elif acao == "parar_autoclick":
        loop_clique_ativo = False
        return "Parei de clicar."

    # --- 7. AUTO-KEYBOARD ---
    elif acao == "iniciar_autokey":
        tecla_alvo_atual = alvo.replace("tecla ", "").strip()
        if not loop_tecla_ativo:
            loop_tecla_ativo = True
            threading.Thread(target=rotina_de_tecla, daemon=True).start()
            return f"Spammando a tecla '{tecla_alvo_atual}'."
        return f"Já estou apertando '{tecla_alvo_atual}'."

    elif acao == "parar_autokey":
        loop_tecla_ativo = False
        return "Parei o spam do teclado."

    # --- 8. AUTO-TEXTO ---
    elif acao == "iniciar_autotexto":
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