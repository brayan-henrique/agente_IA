import speech_recognition as sr
import os
from groq import Groq
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Sua chave que você salvou
CHAVE_GROQ = os.getenv("GROQ_API_KEY")

cliente = Groq(api_key=CHAVE_GROQ)

def ouvir():
    reconhecedor = sr.Recognizer()
    
    with sr.Microphone() as fonte:
        reconhecedor.adjust_for_ambient_noise(fonte, duration=1) 
        print("\n[🎙️] Estou ouvindo... (Fale agora)")
        
        try:
            audio_dados = reconhecedor.listen(fonte, timeout=5, phrase_time_limit=10)
            
            # 1. Usamos um nome de arquivo fixo e simples
            nome_temp = "audio_temp.wav"
            
            with open(nome_temp, "wb") as f:
                f.write(audio_dados.get_wav_data())
            
            print("[☁️] Enviando para a nuvem da Groq...")
            
            # 2. O TRUQUE: Abrimos o arquivo e passamos um nome "fake" (audio.wav) 
            # para a Groq, assim ela não vê os acentos da sua pasta no Windows.
            with open(nome_temp, "rb") as arquivo_audio:
                transcricao = cliente.audio.transcriptions.create(
                    file=("audio.wav", arquivo_audio.read()), # Aqui forçamos um nome sem acento
                    model="whisper-large-v3",
                    language="pt"
                )
            
            texto = transcricao.text.strip()
            
            if os.path.exists(nome_temp):
                os.remove(nome_temp)
                
            return texto
            
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            # Se der erro, ele tenta limpar o arquivo para não travar a próxima tentativa
            if 'nome_temp' in locals() and os.path.exists(nome_temp):
                os.remove(nome_temp)
            print(f"[ERRO NOS OUVIDOS DA NUVEM] {e}")
            return None