import speech_recognition as sr

reconhecedor = sr.Recognizer()

# Desativa a loucura de ficar mudando a sensibilidade do microfone toda hora
reconhecedor.dynamic_energy_threshold = False
# Define uma sensibilidade padrão (se o seu quarto for barulhento, você pode aumentar esse número para 500 ou 600)
reconhecedor.energy_threshold = 400

def ouvir():
    with sr.Microphone() as fonte:
        print("\n[🎙️] Ouvindo... (Pode falar)")
        
        # 1. Calibra o ruído do ambiente por 1 segundo inteiro (antes era 0.5)
        reconhecedor.adjust_for_ambient_noise(fonte, duration=1.0)
        
        # 2. Quanto tempo de silêncio EXATO ele espera antes de achar que você terminou a frase
        reconhecedor.pause_threshold = 2.0 
        
        try:
            # phrase_time_limit: O Jairo agora te escuta falar sem parar por até 20 segundos
            audio_dados = reconhecedor.listen(fonte, timeout=None, phrase_time_limit=20)
            
            print("[☁️] Processando voz...")
            frase = reconhecedor.recognize_google(audio_dados, language='pt-BR')
            return frase
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return "" # Ignora quando ele não entende o que você murmurou
        except Exception as e:
            print(f"[ERRO NO MICROFONE]: {e}")
            return ""