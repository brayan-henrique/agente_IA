import os
import warnings
import keyboard
import time
import threading

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings("ignore", category=UserWarning)

from telemetria import registrar_evento
from ouvidos import ouvir, inicializar_ouvidos
from boca import falar
from cerebro import processar_com_ia
from maos import mapear_programas_windows, executar_acao
from olhos import clicar_no_elemento

trava_voz = threading.Lock()
pipeline_ativa = False

def falar_seguro(texto):
    with trava_voz:
        falar(texto)

def executar_pipeline_background(comando_ia, mapa_programas):
    global pipeline_ativa
    pipeline_ativa = True

    fala_jairo = comando_ia.get("resposta", "")
    pipeline = comando_ia.get("pipeline", [])

    if fala_jairo:
        print(f"\n🤖 Jairo: {fala_jairo}")
        registrar_evento("BOCA", f"Jairo respondendo: '{fala_jairo}'")
        falar_seguro(fala_jairo)

    for indice, passo in enumerate(pipeline):
        acao = passo.get("acao", "nenhuma")
        alvo = passo.get("alvo", "")
        tempo_espera = passo.get("esperar", 0)

        registrar_evento("SISTEMA", f"Executando Passo {indice+1}/{len(pipeline)}: '{acao}'", f"Alvo: '{alvo}'")

        if acao == "usar_visao":
            resultado = clicar_no_elemento(alvo)
            print(f"   [RESULTADO VISUAL]: {resultado}")
            if "Não encontrei" in resultado or "Falha" in resultado:
                registrar_evento("SISTEMA", "Missão abortada por falha na localização visual", status="AVISO")
                falar_seguro("Não consegui achar o que você pediu na tela, chefe.")
                break

        elif acao != "nenhuma":
            resultado = executar_acao(passo, mapa_programas)
            print(f"   [⚙️ AÇÃO EXECUTADA]: {resultado}")

        if tempo_espera > 0:
            registrar_evento("SISTEMA", f"Aguardando {tempo_espera}s para estabilização da interface...")
            time.sleep(tempo_espera)

    pipeline_ativa = False
    registrar_evento("SISTEMA", "Pipeline concluída com sucesso. Sistema em prontidão.")

def iniciar_sistema():
    registrar_evento("SISTEMA", "========================================")
    registrar_evento("SISTEMA", "      SISTEMA JAIRO INICIALIZADO        ")
    registrar_evento("SISTEMA", "========================================")

    inicializar_ouvidos()
    mapa_programas = mapear_programas_windows()

    print("\n🤖 Jairo: Sistemas online. Cérebro Multitarefa ativado.\n")
    modo_espera = False

    while True:
        try:
            if keyboard.is_pressed('ctrl+alt+k'):
                registrar_evento("SISTEMA", "Encerrando sistema pelo atalho de emergência (Ctrl+Alt+K)")
                break

            if keyboard.is_pressed('ctrl+alt+d'):
                if not modo_espera:
                    modo_espera = True
                    registrar_evento("SISTEMA", "Entrando em modo de espera (Ctrl+Alt+D)")

            frase = ouvir(timeout=1.5, em_espera=modo_espera)

            if frase:
                frase = frase.lower()
                correcoes = {
                    "flechar": "fechar",
                    "bloco de nó": "bloco de notas",
                    "jarvis": "jairo",
                    "jair": "jairo",
                    "diário": "jairo",
                    "zairo": "jairo"
                }
                for errado, certo in correcoes.items():
                    frase = frase.replace(errado, certo)

                registrar_evento("OUVIDOS", f"Fala reconhecida: '{frase}'")

                if modo_espera:
                    if "jairo" in frase:
                        modo_espera = False
                        registrar_evento("OUVIDOS", "Jairo despertou do modo de espera")
                        print(f"\n🗣️ Você: '{frase}'")
                        threading.Thread(target=falar_seguro, args=("Tô na área! Manda a boa.",), daemon=True).start()
                    continue

                print(f"\n🗣️ Você: '{frase}'")

                if "parar de escutar" in frase or "vai dormir" in frase:
                    modo_espera = True
                    registrar_evento("SISTEMA", "Entrando em modo de espera por comando de voz")
                    threading.Thread(target=falar_seguro, args=("Fui. Me chama se precisar.",), daemon=True).start()
                    continue

                if "desligar assistente" in frase or "encerrar sistema" in frase:
                    registrar_evento("SISTEMA", "Desligando assistente por comando de voz")
                    falar_seguro("Desligando. Falou, dev!")
                    break

                comando_ia = processar_com_ia(frase)

                if comando_ia:
                    pipeline_nova = comando_ia.get("pipeline", [])
                    tem_acao_pesada = any(p.get("acao") not in ["nenhuma", "parar_autoclick", "parar_autokey"] for p in pipeline_nova)

                    if pipeline_ativa and tem_acao_pesada:
                        registrar_evento("SISTEMA", "Aviso de ocupado emitido (pipeline em andamento)")
                        threading.Thread(target=falar_seguro, args=("Pera aí chefe, tô terminando uma parada aqui. Dá um segundo.",), daemon=True).start()
                        continue

                    threading.Thread(target=executar_pipeline_background, args=(comando_ia, mapa_programas), daemon=True).start()

        except KeyboardInterrupt:
            registrar_evento("SISTEMA", "Encerrado pelo usuário via terminal (Ctrl+C)")
            break
        except Exception as e:
            registrar_evento("SISTEMA", "Exceção não tratada no loop principal", str(e), status="ERRO")
            time.sleep(0.5)

if __name__ == "__main__":
    iniciar_sistema() 
import os
import warnings
import keyboard
import time
import threading

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings("ignore", category=UserWarning)

from telemetria import registrar_evento
from ouvidos import ouvir, inicializar_ouvidos
from boca import falar
from cerebro import processar_com_ia
from maos import mapear_programas_windows, executar_acao
from olhos import clicar_no_elemento

trava_voz = threading.Lock()
pipeline_ativa = False

def falar_seguro(texto):
    with trava_voz:
        falar(texto)

def executar_pipeline_background(comando_ia, mapa_programas):
    global pipeline_ativa
    pipeline_ativa = True

    fala_jairo = comando_ia.get("resposta", "")
    pipeline = comando_ia.get("pipeline", [])

    if fala_jairo:
        print(f"\n🤖 Jairo: {fala_jairo}")
        registrar_evento("BOCA", f"Jairo respondendo: '{fala_jairo}'")
        falar_seguro(fala_jairo)

    for indice, passo in enumerate(pipeline):
        acao = passo.get("acao", "nenhuma")
        alvo = passo.get("alvo", "")
        tempo_espera = passo.get("esperar", 0)

        registrar_evento("SISTEMA", f"Executando Passo {indice+1}/{len(pipeline)}: '{acao}'", f"Alvo: '{alvo}'")

        if acao == "usar_visao":
            resultado = clicar_no_elemento(alvo)
            print(f"   [RESULTADO VISUAL]: {resultado}")
            if "Não encontrei" in resultado or "Falha" in resultado:
                registrar_evento("SISTEMA", "Missão abortada por falha na localização visual", status="AVISO")
                falar_seguro("Não consegui achar o que você pediu na tela, chefe.")
                break

        elif acao != "nenhuma":
            resultado = executar_acao(passo, mapa_programas)
            print(f"   [⚙️ AÇÃO EXECUTADA]: {resultado}")

        if tempo_espera > 0:
            registrar_evento("SISTEMA", f"Aguardando {tempo_espera}s para estabilização da interface...")
            time.sleep(tempo_espera)

    pipeline_ativa = False
    registrar_evento("SISTEMA", "Pipeline concluída com sucesso. Sistema em prontidão.")

def iniciar_sistema():
    registrar_evento("SISTEMA", "========================================")
    registrar_evento("SISTEMA", "      SISTEMA JAIRO INICIALIZADO        ")
    registrar_evento("SISTEMA", "========================================")

    inicializar_ouvidos()
    mapa_programas = mapear_programas_windows()

    print("\n🤖 Jairo: Sistemas online. Cérebro Multitarefa ativado.\n")
    modo_espera = False

    while True:
        try:
            if keyboard.is_pressed('ctrl+alt+k'):
                registrar_evento("SISTEMA", "Encerrando sistema pelo atalho de emergência (Ctrl+Alt+K)")
                break

            if keyboard.is_pressed('ctrl+alt+d'):
                if not modo_espera:
                    modo_espera = True
                    registrar_evento("SISTEMA", "Entrando em modo de espera (Ctrl+Alt+D)")

            frase = ouvir(timeout=1.5, em_espera=modo_espera)

            if frase:
                frase = frase.lower()
                correcoes = {
                    "flechar": "fechar",
                    "bloco de nó": "bloco de notas",
                    "jarvis": "jairo",
                    "jair": "jairo",
                    "diário": "jairo",
                    "zairo": "jairo"
                }
                for errado, certo in correcoes.items():
                    frase = frase.replace(errado, certo)

                registrar_evento("OUVIDOS", f"Fala reconhecida: '{frase}'")

                if modo_espera:
                    if "jairo" in frase:
                        modo_espera = False
                        registrar_evento("OUVIDOS", "Jairo despertou do modo de espera")
                        print(f"\n🗣️ Você: '{frase}'")
                        threading.Thread(target=falar_seguro, args=("Tô na área! Manda a boa.",), daemon=True).start()
                    continue

                print(f"\n🗣️ Você: '{frase}'")

                if "parar de escutar" in frase or "vai dormir" in frase:
                    modo_espera = True
                    registrar_evento("SISTEMA", "Entrando em modo de espera por comando de voz")
                    threading.Thread(target=falar_seguro, args=("Fui. Me chama se precisar.",), daemon=True).start()
                    continue

                if "desligar assistente" in frase or "encerrar sistema" in frase:
                    registrar_evento("SISTEMA", "Desligando assistente por comando de voz")
                    falar_seguro("Desligando. Falou, dev!")
                    break

                comando_ia = processar_com_ia(frase)

                if comando_ia:
                    pipeline_nova = comando_ia.get("pipeline", [])
                    tem_acao_pesada = any(p.get("acao") not in ["nenhuma", "parar_autoclick", "parar_autokey"] for p in pipeline_nova)

                    if pipeline_ativa and tem_acao_pesada:
                        registrar_evento("SISTEMA", "Aviso de ocupado emitido (pipeline em andamento)")
                        threading.Thread(target=falar_seguro, args=("Pera aí chefe, tô terminando uma parada aqui. Dá um segundo.",), daemon=True).start()
                        continue

                    threading.Thread(target=executar_pipeline_background, args=(comando_ia, mapa_programas), daemon=True).start()

        except KeyboardInterrupt:
            registrar_evento("SISTEMA", "Encerrado pelo usuário via terminal (Ctrl+C)")
            break
        except Exception as e:
            registrar_evento("SISTEMA", "Exceção não tratada no loop principal", str(e), status="ERRO")
            time.sleep(0.5)

if __name__ == "__main__":
    iniciar_sistema()