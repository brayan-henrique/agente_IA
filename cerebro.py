import json
from groq import Groq
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Sua chave da Groq
CHAVE_GROQ = os.getenv("GROQ_API_KEY")
cliente = Groq(api_key=CHAVE_GROQ)

historico_conversa = []

def processar_com_ia(frase_usuario):
    # Prompt com regras rigorosas de JSON
    system_prompt = """Você é o Jairo, um assistente de inteligência artificial de altíssimo nível. 
    Seu usuário é o Brayan Henrique, um desenvolvedor. Atue como um mentor.

    REGRA ABSOLUTA DE SAÍDA:
    Você OBRIGATORIAMENTE deve responder em um JSON plano com EXATAMENTE TRÊS chaves na raiz. Não crie sub-dicionários.
    
    ESTRUTURA EXATA DO JSON:
    {
      "resposta": "Sua resposta conversacional para o usuário",
      "acao": "abrir_programa",
      "alvo": "roblox"
    }

    VALORES PERMITIDOS PARA 'acao':
    - "abrir_programa"
    - "fechar_programa"
    - "abrir_site"
    - "pesquisar_web"
    - "nenhuma"

    VALORES PERMITIDOS PARA 'alvo':
    - O nome limpo do programa ou do site (ex: "roblox", "youtube", "vscode"). 
    - Se a ação for "nenhuma", defina o alvo como uma string vazia "".
    """

    if not historico_conversa:
        historico_conversa.append({"role": "system", "content": system_prompt})

    historico_conversa.append({"role": "user", "content": frase_usuario})

    if len(historico_conversa) > 9: 
        historico_conversa.pop(1)
        historico_conversa.pop(1)

    try:
        resposta = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico_conversa,
            response_format={"type": "json_object"},
            temperature=0.1 # Reduzi a criatividade para ele focar em seguir o formato estrito
        )

        texto_bruto = resposta.choices[0].message.content
        dados_ia = json.loads(texto_bruto)
        
        historico_conversa.append({"role": "assistant", "content": texto_bruto})
        return dados_ia

    except Exception as e:
        print(f"\n[ERRO NO CÉREBRO DA NUVEM]: {e}")
        return None