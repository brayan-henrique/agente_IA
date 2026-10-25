import edge_tts
import asyncio
import pygame
import os
import time
import subprocess

VOZ = "pt-BR-AntonioNeural"

def falar_voz_nativa_windows(texto):
    """
    Fallback 100% offline usando o sintetizador nativo do Windows.
    Garante que o Jairo fale mesmo se os servidores da Microsoft caírem.
    """
    try:
        texto_limpo = texto.replace('"', '').replace("'", "")
        cmd = f'Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{texto_limpo}")'
        subprocess.run(
            ["powershell", "-Command", cmd], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            creationflags=0x08000000 # Roda invisível sem abrir janela preta
        )
    except Exception as e:
        print(f"[⚠️ Falha total no som]: {e}")

async def comunicar_edge(texto, arquivo_audio):
    comunicador = edge_tts.Communicate(texto, VOZ)
    await comunicador.save(arquivo_audio)

    pygame.mixer.init()
    pygame.mixer.music.load(arquivo_audio)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.05)

    pygame.mixer.quit()

def falar(texto):
    """
    Tenta falar com a voz neural da Microsoft. Se der erro 403 ou timeout,
    fala com a voz nativa sem travar o Jairo.
    """
    arquivo_temp = f"fala_{int(time.time()*1000)}.mp3"
    
    try:
        asyncio.run(comunicar_edge(texto, arquivo_temp))
    except Exception as e:
        print(f"\n[⚠️ Edge-TTS indisponível ({e}). Usando voz nativa...]")
        falar_voz_nativa_windows(texto)
    finally:
        if os.path.exists(arquivo_temp):
            try:
                os.remove(arquivo_temp)
            except Exception:
                pass