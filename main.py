import os
import warnings

# ========================================================
# FAXINA DO TERMINAL (TEM QUE SER AS PRIMEIRAS LINHAS)
# ========================================================
# Esconde a mensagem chata de boas-vindas do Pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# Silencia avisos de bibliotecas velhas (como o pkg_resources)
warnings.filterwarnings("ignore", category=UserWarning)

# Agora sim, importamos o resto das ferramentas
import keyboard
import time
import threading
from ouvidos import ouvir
from boca import falar
from cerebro import processar_com_ia
from maos import mapear_programas_windows, executar_acao
from olhos import clicar_no_elemento 

# ========================================================
# CONTROLES GLOBAIS DE MULTITAREFA
# ========================================================
trava_voz = threading.Lock()
pipeline_ativa = False

def falar_seguro(texto):
    """Garante que o Jairo não tente falar duas coisas ao mesmo tempo e travar o áudio"""
    with trava_voz:
        falar(texto)

def executar_pipeline_background(comando_ia, mapa_programas):
    """Esta função roda invisível no fundo enquanto o Jairo continua te ouvindo"""
    global pipeline_ativa
    pipeline_ativa = True
    
    fala_jairo = comando_ia.get("resposta", "")
    pipeline = comando_ia.get("pipeline", [])

    # 1. Fala logo a resposta pra não te deixar no vácuo
    if fala_jairo:
        print(f"🤖 Jairo: {fala_jairo}")
        falar_seguro(fala_jairo) 
    
    # 2. Executa o roteiro passo a passo
    for indice, passo in enumerate(pipeline):
        acao = passo.get("acao", "nenhuma")
        alvo = passo.get("alvo", "")
        tempo_espera = passo.get("esperar", 0)

        if acao != "nenhuma":
            print(f"   [⏳ Passo {indice+1}/{len(pipeline)}]: Executando '{acao}' no alvo '{alvo}'")

        # -> Ação Visual (Olhar e Clicar)
        if acao == "usar_visao":
            # Se for a última ação, usa precisão alta. Senão, tira print leve e rápido.
            modo_visao = "alta" if indice == len(pipeline) - 1 else "rapido"
            print(f"   [👁️ Analisando tela em modo '{modo_visao}']")
            
            resultado = clicar_no_elemento(alvo, modo=modo_visao) 
            print(f"   [RESULTADO VISUAL]: {resultado}")
            
            # CHECAGEM DE SANIDADE: Se a visão falhar, ele para tudo.
            if "Não encontrei" in resultado or "Falha" in resultado:
                print("   [⚠️ Abortando o resto da missão devido a falha visual].")
                falar_seguro("Deu ruim aqui, não achei o que eu tava procurando. Missão abortada.")
                break 

        # -> Ações Físicas (Mouse/Teclado/Abrir/Fechar)
        elif acao != "nenhuma":
            resultado = executar_acao(passo, mapa_programas)
            print(f"   [⚙️ AÇÃO EXECUTADA]: {resultado}")
        
        # -> O Delay Inteligente
        if tempo_espera > 0:
            print(f"   [⏱️ Aguardando {tempo_espera}s para o sistema carregar...]")
            time.sleep(tempo_espera)
            
    # Libera o Jairo para tarefas pesadas novamente
    pipeline_ativa = False

# ========================================================
# MOTOR PRINCIPAL
# ========================================================
def iniciar_sistema():
    print("========================================")
    print("      SISTEMA JAIRO INICIALIZADO        ")
    print("      (Ctrl+Alt+K para encerrar)        ")
    print("      (Ctrl+Alt+D para dormir)          ")
    print("========================================")
    
    mapa_programas = mapear_programas_windows()
    print("\n🤖 Jairo: Sistemas online. Cérebro Multitarefa ativado.")
    
    modo_espera = False 
    
    while True:
        # Atalho de Emergência
        if keyboard.is_pressed('ctrl+alt+k'):
            print("\n🤖 Jairo: Encerrando sistemas na marra...")
            break

        # Atalho de Dormir
        if keyboard.is_pressed('ctrl+alt+d'):
            if not modo_espera: 
                modo_espera = True
                print("\n🤖 Jairo: Entrando em modo de espera zZz...")

        frase = ouvir()
        
        if frase:
            frase = frase.lower()
            
            # Ajuste de dicionário
            correcoes = {"flechar": "fechar", "bloco de nó": "bloco de notas", "jarvis": "jairo", "jair": "jairo"}
            for errado, certo in correcoes.items():
                frase = frase.replace(errado, certo)
                
            # Verifica se o Jairo está dormindo
            if modo_espera:
                if "jairo" in frase:
                    modo_espera = False
                    print(f"\n🗣️ Você: '{frase}'")
                    print("🤖 Jairo: Tô na área! Manda a boa.")
                    threading.Thread(target=falar_seguro, args=("Tô na área! Manda a boa.",), daemon=True).start()
                continue 

            print(f"\n🗣️ Você: '{frase}'")
            
            # Comandos manuais para dormir/desligar
            if "parar de escutar" in frase or "vai dormir" in frase:
                modo_espera = True
                print("🤖 Jairo: Fui. Me chama se precisar.")
                threading.Thread(target=falar_seguro, args=("Fui. Me chama se precisar.",), daemon=True).start()
                continue

            if "desligar assistente" in frase or "encerrar sistema" in frase:
                print("🤖 Jairo: Desligando. Falou, dev!")
                falar_seguro("Desligando. Falou, dev!")
                break
                
            # ========================================================
            # ROTEAMENTO MULTITAREFA DO CÉREBRO
            # ========================================================
            comando_ia = processar_com_ia(frase)
            
            if comando_ia:
                pipeline_nova = comando_ia.get("pipeline", [])
                
                # Verifica se o pedido atual exige AÇÃO FÍSICA PESADA (ignorando conversar ou parar loops)
                tem_acao_pesada = any(p.get("acao") not in ["nenhuma", "parar_autoclick", "parar_autokey"] for p in pipeline_nova)

                # Se ele já estiver fazendo algo demorado e você pedir outra coisa demorada:
                if pipeline_ativa and tem_acao_pesada:
                    aviso = "Pera aí chefe, tô terminando uma parada aqui. Dá um segundo."
                    print(f"🤖 Jairo: {aviso}")
                    threading.Thread(target=falar_seguro, args=(aviso,), daemon=True).start()
                    continue
                    
                # Se for só conversa, pedir pra parar um loop, ou ele estiver livre:
                # Dispara a tarefa pro background e deixa o ouvido livre!
                threading.Thread(target=executar_pipeline_background, args=(comando_ia, mapa_programas), daemon=True).start()

# ==========================================
# MOTOR DE PARTIDA
# ==========================================
if __name__ == "__main__":
    iniciar_sistema()