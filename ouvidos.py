import speech_recognition as sr
import time

reconhecedor = sr.Recognizer()

# Configurações de sensibilidade
reconhecedor.dynamic_energy_threshold = False
reconhecedor.energy_threshold = 400   # Sensibilidade base segura
reconhecedor.pause_threshold = 0.8    # Silêncio necessário para considerar fim de fala
reconhecedor.non_speaking_duration = 0.4

_microfone_calibrado = False

def inicializar_ouvidos(duracao_calibracao=1.0):
    """
    Calibra o microfone uma única vez e garante que a sensibilidade
    não caia em valores absurdamente baixos que captam ruído de ventoinha.
    """
    global _microfone_calibrado
    try:
        with sr.Microphone() as fonte:
            print("[🎙️ Ouvidos] Calibrando microfone para o ruído do ambiente...")
            reconhecedor.adjust_for_ambient_noise(fonte, duration=duracao_calibracao)
            
            # TRAVA DE SEGURANÇA: Nunca deixa a sensibilidade menor que 300
            # Se ficar menor que 300, qualquer respiração trava o reconhecimento
            if reconhecedor.energy_threshold < 300:
                reconhecedor.energy_threshold = 350
                
            _microfone_calibrado = True
            print(f"[🎙️ Ouvidos] Calibrado com sucesso! Limiar seguro: {reconhecedor.energy_threshold:.0f}")
    except Exception as e:
        print(f"[⚠️ Erro ao calibrar microfone]: {e}")
        reconhecedor.energy_threshold = 400
        _microfone_calibrado = True

def ouvir(timeout=1.5, phrase_time_limit=12, em_espera=False):
    """
    Escuta o microfone de forma ágil e com feedback no terminal.
    """
    global _microfone_calibrado
    if not _microfone_calibrado:
        inicializar_ouvidos()

    limite_tempo = 4 if em_espera else phrase_time_limit

    try:
        with sr.Microphone() as fonte:
            # Feedback visual para você saber que ele está escutando
            status = "zZz (Aguardando 'Jairo')..." if em_espera else "Pode falar..."
            print(f"\r[🎙️ Ouvindo] {status}", end="", flush=True)

            audio_dados = reconhecedor.listen(
                fonte, 
                timeout=timeout, 
                phrase_time_limit=limite_tempo
            )

        print("\r[☁️ Processando voz...]                    ", end="", flush=True)
        frase = reconhecedor.recognize_google(audio_dados, language='pt-BR')
        print("\r" + " " * 45 + "\r", end="", flush=True) # Limpa a linha de status
        return frase.strip()

    except sr.WaitTimeoutError:
        # Silêncio dentro do timeout: normal, libera o loop para checar teclas
        return ""
    except sr.UnknownValueError:
        # Barulho não identificado: limpa a linha e segue
        print("\r" + " " * 45 + "\r", end="", flush=True)
        return ""
    except sr.RequestError as e:
        print(f"\n[☁️ Erro de conexão com a API de voz]: {e}")
        return ""
    except Exception as e:
        print(f"\n[⚠️ Erro inesperado no microfone]: {e}")
        time.sleep(0.3)
        return ""