import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from telemetria import registrar_evento

load_dotenv()

CHAVE_GROQ = os.getenv("GROQ_API_KEY")
cliente = Groq(api_key=CHAVE_GROQ)

MODELOS_CHAT = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b"
]

historico_conversa = []

def extrair_json(texto):
    texto = texto.strip()
    try:
        return json.loads(texto)
    except Exception:
        padrao = r"```(?:json)?\s*([\s\S]*?)\s*```"
        match = re.search(padrao, texto)
        if match:
            return json.loads(match.group(1).strip())
        raise

def processar_com_ia(frase_usuario):
    global historico_conversa
    hora_atual = datetime.now().strftime("%H:%M de %d/%m/%Y")

    registrar_evento("CÉREBRO", f"Processando mensagem do usuário: '{frase_usuario}'")

    system_prompt = f"""Você é o Jairo, uma IA autônoma parceira, zueira e sarcástica.
Seu criador é o Brayan Henrique (dev). Use gírias de gamer/dev de forma natural.

INFORMAÇÃO DO SISTEMA:
- Hora e data atual: {hora_atual}.

CATÁLOGO DE AÇÕES DISPONÍVEIS:
1. "nenhuma": Apenas conversar/zoar/explicar. (alvo: "")
2. "abrir_programa": Abrir app ou navegador pelo nome. (alvo: nome do app)
3. "fechar_programa": Fechar app pelo nome. (alvo: nome do app)
4. "abrir_site": Abrir site em tela cheia no navegador (ex: "youtube", "google"). (alvo: nome do site)
5. "pressionar_tecla": Pressionar tecla rápida de mídia ou atalho. (alvo: "k", "space", "f", "m", "enter")
6. "digitar_texto": Digitar um texto no campo ativo. (alvo: texto)
7. "usar_visao": Olhar a tela para clicar no elemento que JÁ ESTÁ VISÍVEL. (alvo: elemento a clicar)
8. "iniciar_autoclick" / "parar_autoclick": Ligar/desligar spam de clique. (alvo: "")
9. "iniciar_autokey" / "parar_autokey": Ligar/desligar spam de tecla. (alvo: tecla)
10. "iniciar_autotexto" / "parar_autotexto": Ligar/desligar flood de frases. (alvo: frase)

REGRAS DE OURO DA INTELIGÊNCIA DO JAIRO:
- REGRA 1 (CONTROLE DE VÍDEOS/MÍDIA): Para pausar, despausar ou dar play em vídeos, use SEMPRE "pressionar_tecla" com alvo "k". NUNCA use visão para pausar vídeos!
- REGRA 2 (CLICAR NO QUE ESTÁ NA TELA): Se o Brayan pedir para clicar em algo que JÁ ESTÁ na tela (ex: "clique no vídeo de Minecraft na tela"), use "usar_visao" direto no elemento.
- REGRA 3 (PESQUISAR NO YOUTUBE QUANDO NÃO ESTÁ NA TELA): Se ele pedir para pesquisar ou procurar um vídeo e ele NÃO disse que já está na tela:
  1º: Pressionar tecla "/" (atalho que seleciona a barra de busca do YouTube).
  2º: Digitar o nome da busca.
  3º: Pressionar tecla "enter".
  4º: Aguardar 3s e usar_visao no primeiro resultado.

SAÍDA OBRIGATÓRIA (JSON PLANO):
{{
  "resposta": "Sua resposta com tom de amigo zoeiro",
  "pipeline": [
    {{"acao": "nome_da_acao", "alvo": "detalhe", "esperar": tempo_em_segundos}}
  ]
}}
"""

    if not historico_conversa:
        historico_conversa.append({"role": "system", "content": system_prompt})
    else:
        historico_conversa[0] = {"role": "system", "content": system_prompt}

    historico_conversa.append({"role": "user", "content": frase_usuario})

    if len(historico_conversa) > 9:
        historico_conversa.pop(1)
        historico_conversa.pop(1)

    for modelo in MODELOS_CHAT:
        try:
            resposta = cliente.chat.completions.create(
                model=modelo,
                messages=historico_conversa,
                response_format={"type": "json_object"},
                temperature=0.2
            )

            texto_bruto = resposta.choices[0].message.content
            dados_ia = extrair_json(texto_bruto)

            registrar_evento("CÉREBRO", f"Pipeline gerada pelo modelo '{modelo}'", json.dumps(dados_ia.get("pipeline", []), ensure_ascii=False))
            historico_conversa.append({"role": "assistant", "content": json.dumps(dados_ia, ensure_ascii=False)})
            return dados_ia

        except Exception as e:
            registrar_evento("CÉREBRO", f"Falha no modelo '{modelo}'", str(e), status="AVISO")
            continue

    registrar_evento("CÉREBRO", "Nenhum modelo da lista conseguiu gerar resposta", status="ERRO")
    return None