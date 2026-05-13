import os

# Esconde a mensagem de boas-vindas do Pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Silencia avisos de bibliotecas depreciadas no terminal
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import keyboard
from ouvidos import ouvir
from cerebro import processar_com_ia
from maos import mapear_programas_windows, executar_acao
from olhos import clicar_no_elemento 

def iniciar_sistema():
    print("========================================")
    print("      SISTEMA JAIRO INICIALIZADO        ")
    print("      (Ctrl+Alt+K para encerrar)        ")
    print("      (Ctrl+Alt+D para dormir)          ")
    print("========================================")
    
    mapa_programas = mapear_programas_windows()
    print("\n🤖 Jairo: Sistemas online. Estou te ouvindo, chefe.")
    
    modo_espera = False 
    
    while True:
        # Atalho de Emergência
        if keyboard.is_pressed('ctrl+alt+k'):
            print("\n🤖 Jairo: Encerrando sistemas por comando de teclado. Até a próxima.")
            break

        # Atalho de Dormir
        if keyboard.is_pressed('ctrl+alt+d'):
            if not modo_espera: 
                modo_espera = True
                print("\n🤖 Jairo: [Teclado] Entrando em modo de espera zZz... (Fale 'Jairo' para acordar)")

        frase = ouvir()
        
        if frase:
            frase = frase.lower()
            
            correcoes = {
                "flechar": "fechar",
                "bloco de nó": "bloco de notas",
                "jarvis": "jairo",
                "jair": "jairo"
            }
            for errado, certo in correcoes.items():
                frase = frase.replace(errado, certo)
                
            # Verifica se o Jairo está dormindo
            if modo_espera:
                if "jairo" in frase:
                    modo_espera = False
                    print(f"\n🗣️ Você: '{frase}'")
                    print("🤖 Jairo: Estou de volta! O que você precisa?")
                continue 

            print(f"\n🗣️ Você: '{frase}'")
            
            # Comandos manuais para dormir/desligar
            if "parar de escutar" in frase or "vai dormir" in frase or "modo de espera" in frase:
                modo_espera = True
                print("🤖 Jairo: Entrando em modo de espera. É só chamar meu nome quando precisar.")
                continue

            if "desligar assistente" in frase or "encerrar sistema" in frase:
                print("🤖 Jairo: Entendido. Desligando completamente.")
                break
                
            # ========================================================
            # 🧠 O CÉREBRO TOMA TODAS AS DECISÕES (Roteamento Semântico)
            # ========================================================
            comando_ia = processar_com_ia(frase)
            
            if comando_ia:
                fala_jairo = comando_ia.get("resposta", "")
                acao = comando_ia.get("acao", "nenhuma")
                alvo = comando_ia.get("alvo", "")

                # 1º O Jairo sempre responde primeiro (conversacional/didático)
                if fala_jairo:
                    from boca import falar # Importa a função nova
                    print(f"🤖 Jairo: {fala_jairo}")
                    falar(fala_jairo) # O Jairo agora fala com voz neural!
                
                # 2º Ele distribui as tarefas com base na intenção
                if acao == "usar_visao":
                    print(f"   [👁️ JAIRO ESTÁ PROCURANDO '{alvo.upper()}' NA TELA...]")
                    resultado_visao = clicar_no_elemento(alvo) 
                    print(f"   [RESULTADO VISUAL]: {resultado_visao}")
                
                elif acao != "nenhuma":
                    resultado = executar_acao(comando_ia, mapa_programas)
                    print(f"   [⚙️ AÇÃO EXECUTADA]: {resultado}")

if __name__ == "__main__":
    iniciar_sistema()