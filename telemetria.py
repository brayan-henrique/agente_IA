import os
import time
from datetime import datetime

ARQUIVO_LOG = "debug_execucao.log"

def registrar_evento(orgao, acao, detalhe="", status="INFO"):
    """
    Registra um evento passo a passo no terminal e no arquivo debug_execucao.log.
    Exibe timestamps precisos para você saber exatamente onde e quando ocorreu cada ação ou erro.
    """
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefixo_icone = {
        "OUVIDOS": "🎙️",
        "CÉREBRO": "🧠",
        "MÃOS": "⚙️",
        "OLHOS": "👁️",
        "BOCA": "🔊",
        "SISTEMA": "🖥️"
    }.get(orgao, "📌")

    status_tag = f"[{status}]" if status != "INFO" else ""
    mensagem_formatada = f"[{timestamp}] {prefixo_icone} [{orgao}] {status_tag} {acao}"
    if detalhe:
        mensagem_formatada += f" -> {detalhe}"

    # Exibe no terminal
    print(mensagem_formatada)

    # Grava no arquivo de log do disco
    try:
        with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
            f.write(mensagem_formatada + "\n")
    except Exception:
        pass