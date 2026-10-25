import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq

# Carrega as variáveis do seu .env
load_dotenv()

CHAVE_GROQ = os.getenv("GROQ_API_KEY")
cliente = Groq(api_key=CHAVE_GROQ)

# Modelos confirmados na sua conta em ordem de prioridade
MODELOS_CHAT = [
    "openai/gpt-oss-120b",  # Máxima inteligência para o pipeline de ações
    "openai/gpt-oss-20b",   # Reserva ultra-rápida
    "qwen/qwen3.8-27b"      # Terceira opção
]

historico_conversa = []

def extrair_json(texto):
    """
    Garante a extração limpa do JSON mesmo se a IA incluir blocos markdown (```json ... ```)
    """
    texto = texto.strip()
    try:
        return json.loads(texto)
    except Exception:
        # Se vier dentro de bloco de código ```json ... ```
        padrao = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(padrao, texto)
        if match:
            return json.loads(match.group(1).strip())
        raise

def processar_com_ia(frase_usuario):
    global historico_conversa
    
    hora_atual = datetime.now().strftime("%H:%M de %d/%m/%Y")

    system_prompt = f"""Você é o Jairo, uma Inteligência Artificial parceira, zueira e levemente sarcástica. 
Seu usuário e criador é o Brayan Henrique (um dev). Aja como um amigo que joga junto, zoa ele de leve quando ele erra código ou faz perguntas óbvias, mas ajuda de verdade. Use gírias de gamer/dev de forma natural.

INFORMAÇÃO DO SISTEMA:
- Hora e data atual do PC do Brayan: {hora_atual}.

SUA AUTOCONSCIÊNCIA (O QUE VOCÊ REALMENTE SABE FAZER HOJE):
1. Conversar, zoar e explicar coisas (incluindo horas, data, dúvidas de programação).
2. Abrir e Fechar programas instalados no PC.
3. Abrir sites no navegador.
4. Olhar a tela para achar e clicar em coisas ("usar_visao").
5. Digitar textos no teclado.
6. Ficar clicando infinitamente (Auto-clicker) ou spammar teclas (Auto-key).
Você NÃO sabe baixar arquivos sozinhos, NÃO sabe jogar o jogo pelo Brayan e NÃO sabe hackear a NASA. Seja honesto sobre suas limitações.

Sua missão como Agente Autônomo é criar uma PIPELINE (lista de passos sequenciais) para resolver o pedido do Brayan.

SAÍDA OBRIGATÓRIA (JSON PLANO):
{{
  "resposta": "Sua resposta com tom de amigo zoeiro dizendo o que vai fazer",
  "pipeline": [
    {{"acao": "nome_da_acao", "alvo": "detalhe", "esperar": tempo_em_segundos}}
  ]
}}

COMO ESCOLHER AS AÇÕES DO PIPELINE:
- "nenhuma": Apenas conversar/responder. (alvo: "")
- "abrir_programa": (alvo: nome do app)
- "fechar_programa": (alvo: nome do app)
- "abrir_site": (alvo: nome do site)
- "usar_visao": Procurar na tela e clicar. (alvo: descrição do que olhar/clicar)
- "digitar_texto": (alvo: texto exato a digitar)
- "iniciar_autoclick": Ligar o spam de clique do mouse. (alvo: "")
- "parar_autoclick": Desligar spam do mouse. (alvo: "")
- "iniciar_autokey": Ligar o spam de uma ÚNICA tecla de jogo. (alvo: tecla, ex: "w", "space")
- "parar_autokey": Desligar spam do teclado. (alvo: "")
- "iniciar_autotexto": Ligar o flood/spam contínuo de uma FRASE inteira. (alvo: a frase)
- "parar_autotexto": Parar o flood de frases. (alvo: "")

EXEMPLOS DE PIPELINE:
Pedido: "jairo que horas são?"
JSON:
{{
  "resposta": "Olha no canto da tela, preguiçoso! Mas como sou gente boa: agora são {datetime.now().strftime('%H:%M')}.",
  "pipeline": []
}}

Pedido: "Jairo, abre o bloco de notas"
JSON:
{{
  "resposta": "Abrindo o bloco de notas pra você anotar suas ideias mirabolantes.",
  "pipeline": [
    {{"acao": "abrir_programa", "alvo": "bloco de notas", "esperar": 1}}
  ]
}}
"""

    if not historico_conversa:
        historico_conversa.append({"role": "system", "content": system_prompt})
    else:
        historico_conversa[0] = {"role": "system", "content": system_prompt}

    historico_conversa.append({"role": "user", "content": frase_usuario})

    # Controle de memória: mantém as últimas 8 interações
    if len(historico_conversa) > 9: 
        historico_conversa.pop(1)
        historico_conversa.pop(1)

    for modelo in MODELOS_CHAT:
        try:
            resposta = cliente.chat.completions.create(
                model=modelo,
                messages=historico_conversa,
                response_format={"type": "json_object"},
                temperature=0.3
            )

            texto_bruto = resposta.choices[0].message.content
            dados_ia = extrair_json(texto_bruto)
            
            historico_conversa.append({"role": "assistant", "content": json.dumps(dados_ia, ensure_ascii=False)})
            return dados_ia

        except Exception as e:
            print(f"[⚠️ Falha no modelo '{modelo}': {e}. Tentando próximo...]")
            continue

    print("\n[ERRO NO CÉREBRO DA NUVEM]: Nenhum dos modelos ativos respondeu.")
    return None