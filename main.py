import os
import warnings

# ========================================================
# FAXINA DO TERMINAL
# ========================================================
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings("ignore", category=UserWarning)

import keyboard
import time
import threading
from ouvidos import ouvir, inicializar_ouvidos
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
    """Garante que o Jairo não tente falar duas coisas ao mesmo tempo"""
    with trava_voz:
        falar(texto)

def executar_pipeline_background(comando_ia, mapa_programas):
    """Roda as ações pesadas no fundo enquanto o Jairo continua te ouvindo"""
    global pipeline_ativa
    pipeline_ativa = True
    
    fala_jairo = comando_ia.get("resposta", "")
    pipeline = comando_ia.get("pipeline", [])

    # 1. Fala logo a resposta
    if fala_jairo:
        print(f"\n🤖 Jairo: {fala_jairo}")
        falar_seguro(fala_jairo) 
    
    # 2. Executa cada passo do roteiro
    for indice, passo in enumerate(pipeline):
        acao = passo.get("acao", "nenhuma")
        alvo = passo.get("alvo", "")
        tempo_espera = passo.get("esperar", 0)

        if acao != "nenhuma":
            print(f"   [⏳ Passo {indice+1}/{len(pipeline)}]: Executando '{acao}' no alvo '{alvo}'")

        # -> Visão computacional
        if acao == "usar_visao":
            modo_visao = "alta" if indice == len(pipeline) - 1 else "rapido"
            print(f"   [👁️ Analisando tela em modo '{modo_visao}']")
            
            resultado = clicar_no_elemento(alvo, modo=modo_visao) 
            print(f"   [RESULTADO VISUAL]: {resultado}")
            
            if "Não encontrei" in resultado or "Falha" in resultado:
                print("   [⚠️ Abortando o resto da missão devido a falha visual].")
                falar_seguro("Deu ruim aqui, não achei o que eu tava procurando. Missão abortada.")
                break 

        # -> Ações de mouse/teclado/janelas
        elif acao != "nenhuma":
            resultado = executar_acao(passo, mapa_programas)
            print(f"   [⚙️ AÇÃO EXECUTADA]: {resultado}")
        
        # -> Espera inteligente
        if tempo_espera > 0:
            print(f"   [⏱️ Aguardando {tempo_espera}s para o sistema carregar...]")
            time.sleep(tempo_espera)
            
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
    
    inicializar_ouvidos()
    
    mapa_programas = mapear_programas_windows()
    print("\n🤖 Jairo: Sistemas online. Cérebro Multitarefa ativado.\n")
    
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

        # Escuta o microfone
        frase = ouvir(timeout=1.5, em_espera=modo_espera)
        
        if frase:
            frase = frase.lower()
            
            # Dicionário de correções fonéticas comuns
            correcoes = {
                "flechar": "fechar", 
                "bloco de nó": "bloco de notas", 
                "jarvis": "jairo", 
                "jair": "jairo"
            }
            for errado, certo in correcoes.items():
                frase = frase.replace(errado, certo)
                
            # Se o Jairo estiver dormindo
            if modo_espera:
                if "jairo" in frase:
                    modo_espera = False
                    print(f"\n🗣️ Você: '{frase}'")
                    print("🤖 Jairo: Tô na área! Manda a boa.")
                    threading.Thread(target=falar_seguro, args=("Tô na área! Manda a boa.",), daemon=True).start()
                continue 

            print(f"\n🗣️ Você: '{frase}'")
            
            # Comandos de voz para dormir ou desligar
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
                
                # Se for ação pesada física e ele já estiver ocupado
                tem_acao_pesada = any(
                    p.get("acao") not in ["nenhuma", "parar_autoclick", "parar_autokey"] 
                    for p in pipeline_nova
                )

                if pipeline_ativa and tem_acao_pesada:
                    aviso = "Pera aí chefe, tô terminando uma parada aqui. Dá um segundo."
                    print(f"🤖 Jairo: {aviso}")
                    threading.Thread(target=falar_seguro, args=(aviso,), daemon=True).start()
                    continue
                    
                # Dispara a execução em background e libera o microfone
                threading.Thread(
                    target=executar_pipeline_background, 
                    args=(comando_ia, mapa_programas), 
                    daemon=True
                ).start()

# ==========================================
# MOTOR DE PARTIDA
# ==========================================
if __name__ == "__main__":
    iniciar_sistema()