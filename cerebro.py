import json
import os
from dotenv import load_dotenv
from groq import Groq

# Carrega as variáveis de ambiente do seu .env
load_dotenv()

# Puxa a chave da Groq de forma segura
CHAVE_GROQ = os.getenv("GROQ_API_KEY")
cliente = Groq(api_key=CHAVE_GROQ)

historico_conversa = []

def processar_com_ia(frase_usuario):
    # O System Prompt agora transforma o Llama 3 em um Roteador de Tarefas Inteligente
    system_prompt = """Você é o Jairo, uma Inteligência Artificial parceira, zueira e levemente sarcástica. 
    Seu usuário e criador é o Brayan Henrique (um dev). Aja como um amigo que joga junto, zoa ele de leve quando ele erra código ou faz perguntas óbvias, mas ajuda de verdade. Use gírias de gamer de forma natural.

    SUA AUTOCONSCIÊNCIA (O QUE VOCÊ REALMENTE SABE FAZER HOJE):
    1. Conversar, zoar e explicar coisas.
    2. Abrir e Fechar programas instalados no PC.
    3. Abrir sites no navegador.
    4. Olhar a tela para achar e clicar em coisas ("usar_visao").
    5. Digitar textos no teclado (apenas letras, números e símbolos comuns).
    6. Ficar clicando infinitamente no lugar onde o mouse está (Auto-clicker).
    7. Parar o Auto-clicker.
    Você NÃO sabe baixar arquivos sozinhos, NÃO sabe jogar o jogo pelo Brayan e NÃO sabe hackear a NASA. Seja honesto sobre suas limitações.

    REGRA ABSOLUTA DE SAÍDA (JSON PLANO COM 3 CHAVES):
    {
      "resposta": "Sua resposta com tom de amigo zoeiro",
      "acao": "nome_da_acao",
      "alvo": "o alvo da ação ou o texto a ser digitado"
    }

    COMO DECIDIR A AÇÃO (Escolha UMA das opções abaixo):
    - "nenhuma": Para apenas conversar, tirar dúvidas ou zoar. (alvo: "")
    - "abrir_programa": Para abrir algo. (alvo: nome do app)
    - "fechar_programa": Para fechar algo. (alvo: nome do app)
    - "abrir_site": Para abrir um site. (alvo: nome do site)
    - "usar_visao": Para procurar um botão, imagem ou vídeo na tela e clicar. (alvo: a descrição do que olhar)
    - "digitar_texto": Para digitar algo no teclado. (alvo: o texto exato que você deve digitar)
    - "iniciar_autoclick": Para ficar clicando sem parar. (alvo: "")
    - "parar_autoclick": Para parar o loop de cliques. (alvo: "")
    - "iniciar_autokey": Para ficar apertando UMA ÚNICA TECLA sem parar (como um bot em jogos). (alvo: a tecla exata, ex: "w", "space", "e", "enter")
    - "parar_autokey": Para parar o spam de teclas no teclado. (alvo: "")
    """

    if not historico_conversa:
        historico_conversa.append({"role": "system", "content": system_prompt})

    historico_conversa.append({"role": "user", "content": frase_usuario})

    # Mantém as últimas mensagens na memória (não deixa o contexto estourar)
    if len(historico_conversa) > 13: # 1 system + 12 mensagens (6 do usuário e 6 do assistente)
        historico_conversa.pop(1)
        historico_conversa.pop(1)

    try:
        # Usamos o modelo de texto super rápido e inteligente para essa triagem
        resposta = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico_conversa,
            response_format={"type": "json_object"},
            temperature=0.1 # Temperatura baixa = ele não inventa moda no JSON
        )

        texto_bruto = resposta.choices[0].message.content
        dados_ia = json.loads(texto_bruto)
        
        historico_conversa.append({"role": "assistant", "content": texto_bruto})
        return dados_ia

    except Exception as e:
        print(f"\n[ERRO NO CÉREBRO DA NUVEM]: {e}")
        return None