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
    system_prompt = """Você é o Jairo, um assistente de inteligência artificial de altíssimo nível. 
    Seu usuário é o Brayan Henrique, um desenvolvedor. Atue como um mentor e roteador de tarefas.

    Sua função principal é interpretar a INTENÇÃO do usuário e decidir qual ferramenta usar.
    
    REGRA ABSOLUTA DE SAÍDA (JSON PLANO COM 3 CHAVES):
    {
      "resposta": "Sua resposta conversacional para o usuário",
      "acao": "nome_da_acao",
      "alvo": "o que deve ser procurado, aberto ou fechado"
    }

    COMO DECIDIR A AÇÃO:
    1. Se o usuário estiver apenas conversando, tirando dúvidas teóricas ou perguntando "como fazer" algo: use "nenhuma".
    2. Se o usuário pedir ou mandar você abrir um programa instalado no PC: use "abrir_programa".
    3. Se o usuário pedir ou mandar você fechar um programa: use "fechar_programa".
    4. Se o usuário pedir para abrir um site específico: use "abrir_site".
    5. Se o usuário pedir ou mandar você clicar, selecionar, procurar, olhar ou interagir com algo que JÁ ESTÁ na tela: use "usar_visao".

    Exemplo 1: "Como eu faria para selecionar o botão azul no Flutter?" -> acao: "nenhuma" (é uma dúvida).
    Exemplo 2: "Jairo, clique no botão azul." -> acao: "usar_visao", alvo: "botão azul" (é uma ordem de execução).
    """

    if not historico_conversa:
        historico_conversa.append({"role": "system", "content": system_prompt})

    historico_conversa.append({"role": "user", "content": frase_usuario})

    # Mantém as últimas mensagens na memória (não deixa o contexto estourar)
    if len(historico_conversa) > 9: 
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