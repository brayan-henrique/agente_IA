import keyboard
from ouvidos import ouvir
from cerebro import processar_com_ia
from maos import mapear_programas_windows, executar_acao

# IMPORTANDO OS NOVOS OLHOS DO JAIRO
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
        if keyboard.is_pressed('ctrl+alt+k'):
            print("\n🤖 Jairo: Encerrando sistemas por comando de teclado. Até a próxima.")
            break

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
                
            if modo_espera:
                if "jairo" in frase:
                    modo_espera = False
                    print(f"\n🗣️ Você: '{frase}'")
                    print("🤖 Jairo: Estou de volta! O que você precisa?")
                continue 

            print(f"\n🗣️ Você: '{frase}'")
            
            if "parar de escutar" in frase or "vai dormir" in frase or "modo de espera" in frase:
                modo_espera = True
                print("🤖 Jairo: Entrando em modo de espera. É só chamar meu nome quando precisar.")
                continue

            if "desligar assistente" in frase or "encerrar sistema" in frase:
                print("🤖 Jairo: Entendido. Desligando completamente.")
                break
                
            # ========================================================
            # 👁️ O NOVO GATILHO DE VISÃO (Altamente Flexível)
            # ========================================================
            gatilhos_visao = ["clique", "clica", "selecione", "coloque aquele", "coloque o", "toca no"]
            
            if any(gatilho in frase for gatilho in gatilhos_visao):
                print("🤖 Jairo: Entendido. Analisando a tela com meus olhos...")
                # Repassa a sua frase inteira para o modelo de visão entender o contexto
                resultado_visao = clicar_no_elemento(frase) 
                print(f"   [👁️ AÇÃO VISUAL]: {resultado_visao}")
                
                # O 'continue' faz ele voltar a te ouvir sem precisar passar pelo cérebro de texto, 
                # economizando tempo de processamento.
                continue 

            # ========================================================
            # 🧠 O CÉREBRO DE TEXTO TRADICIONAL (Ações e Conversa)
            # ========================================================
            comando_ia = processar_com_ia(frase)
            
            if comando_ia:
                fala_jairo = comando_ia.get("resposta", "")
                if fala_jairo:
                    print(f"🤖 Jairo: {fala_jairo}")
                
                acao = comando_ia.get("acao", "nenhuma")
                if acao != "nenhuma":
                    resultado = executar_acao(comando_ia, mapa_programas)
                    print(f"   [⚙️ AÇÃO EXECUTADA]: {resultado}")

if __name__ == "__main__":
    iniciar_sistema()