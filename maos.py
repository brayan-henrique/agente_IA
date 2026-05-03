import os
import webbrowser
from thefuzz import fuzz

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

def executar_acao(comando_json, mapa_programas):
    # Pega os dados com segurança. Se for um dicionário complexo, transforma em string.
    acao = str(comando_json.get("acao", "")).lower()
    alvo = str(comando_json.get("alvo", "")).lower()
    
    # 1. ABRIR PROGRAMAS
    if "abrir" in acao and "site" not in acao:
        if not alvo or alvo == "none" or alvo == "{}":
            return "O cérebro falhou e não me enviou o nome do programa."

        if "roblox" in alvo:
            try:
                os.system("start roblox:") 
                return "Iniciando o Roblox nativamente..."
            except:
                pass
                
        nativos = {"calculadora": "calc", "bloco de notas": "notepad", "paint": "mspaint"}
        
        for nativo, comando_cmd in nativos.items():
            if fuzz.partial_ratio(alvo, nativo) > 80:
                os.system(comando_cmd)
                return f"Abri o aplicativo nativo: {nativo}."
                
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
            try:
                os.startfile(melhor_caminho)
                return f"Abri o aplicativo {nome_escolhido} (Certeza: {melhor_pontuacao}%)."
            except FileNotFoundError:
                return f"Erro: O atalho do {nome_escolhido} quebrou."
                
        return f"Não encontrei '{alvo}'. O mais próximo foi '{nome_escolhido}' ({melhor_pontuacao}%)."

    # 2. FECHAR PROGRAMAS
    elif "fechar" in acao:
        if not alvo: return "O cérebro não me enviou o que fechar."
        alvo_formatado = alvo.replace(" ", "")
        os.system(f"taskkill /f /im {alvo_formatado}.exe /t")
        return f"Enviei o comando para fechar o processo do {alvo}."
        
    # 3. ABRIR SITES
    elif "site" in acao or "navegador" in acao:
        if not alvo or alvo == "none": return "O cérebro não informou o site."
        
        # Limpa palavras extras que a IA possa mandar (ex: "youtube.com" vira só "youtube")
        alvo_limpo = alvo.replace(".com", "").replace(".br", "").replace("www.", "").strip()
        webbrowser.open(f"https://www.{alvo_limpo}.com")
        return f"Abri o site {alvo_limpo}."
        
    # 4. PESQUISAR
    elif "pesquisar" in acao:
        if not alvo: return "O cérebro não informou o que pesquisar."
        termo = alvo.replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={termo}")
        return f"Fiz a pesquisa sobre {alvo}."

    return f"Ação ignorada ou desconhecida. (Ação={acao}, Alvo={alvo})"